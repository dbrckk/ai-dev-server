"""Resumable trusted Android device-smoke stage for Godot studio checkpoints."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from core import StudioError, canonical, request_check
from godot_android_export import export_debug_apk, install_android_templates
from godot_device_qa import validate_debug_apk
from godot_preview import _publish, _restore
from godot_runtime import install
from run import GitHub


def _valid_sha(value) -> bool:
    return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def execute(req: dict, root: Path, out: Path, github, device_validator=validate_debug_apk,
            runtime_installer=install, template_installer=install_android_templates,
            exporter=export_debug_apk) -> dict:
    req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
    if any(root.iterdir()): raise StudioError('Workspace must be fresh for Godot device stage')
    branch='studio/'+req['id']
    state,parent,checkpoint=_restore(github,branch,root)
    if not checkpoint or not isinstance(state,dict): raise StudioError('Godot device stage requires studio checkpoint')
    if state.get('engine')!='godot' or state.get('status')!='godot_android_export_validated':
        raise StudioError('Godot device stage requires validated Android export checkpoint')
    completion=state.get('completion'); export_state=state.get('android_export')
    if (not isinstance(completion,dict) or completion.get('finished') is not False or
            completion.get('next_stage')!='godot_device_qa' or not isinstance(export_state,dict) or
            not _valid_sha(export_state.get('apk_sha256'))):
        raise StudioError('Godot device checkpoint contract invalid')

    apk=out/'app-debug.apk'; expected=export_state['apk_sha256']; reexported=False
    local_ok=(apk.is_file() and not apk.is_symlink() and apk.stat().st_size>=1000 and
              hashlib.sha256(apk.read_bytes()).hexdigest()==expected)
    if not local_ok:
        reexported=True
        with tempfile.TemporaryDirectory(prefix='studio-godot-device-reexport-') as cache:
            cache_root=Path(cache)
            binary=runtime_installer(cache_root/'runtime')
            templates=template_installer(cache_root/'templates')
            evidence=exporter(root,binary,templates,artifact_path=apk)
        if not evidence.get('passed') or not _valid_sha(evidence.get('apk_sha256')) or not apk.is_file():
            state.update(status='godot_device_qa_failed',blockers=['Godot APK re-export failed before device QA'])
            state['completion']={'finished':False,'next_stage':'godot_device_qa','reason':'Device QA requires a verified local APK.'}
            parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
            (out/'report.json').write_text(canonical(state)); return state
        expected=evidence['apk_sha256']
        if hashlib.sha256(apk.read_bytes()).hexdigest()!=expected:
            raise StudioError('Re-exported Godot APK hash evidence mismatch')
        export_state=dict(export_state); export_state.update(apk_sha256=expected,reexported_for_device_qa=True)
        state['android_export']=export_state

    result=device_validator(root,apk,expected,out)
    (out/'godot-device-qa.json').write_text(canonical(result))
    if not result.get('passed'):
        state.update(status='godot_device_qa_failed',blockers=['Godot Android device smoke failed'])
        state['completion']={'finished':False,'next_stage':'godot_device_qa','reason':'Install/launch/runtime smoke evidence incomplete.'}
    else:
        if result.get('apk_sha256')!=expected or result.get('journeys_executed') is not False or result.get('visual_reviewed') is not False:
            raise StudioError('Godot device QA returned invalid evidence contract')
        state.update(status='godot_device_validated',blockers=[])
        coverage=dict(state.get('coverage') or {}); coverage.update(engine='godot',android_export=True,device_qa=True,journeys_executed=False,visual_qa=False)
        state['coverage']=coverage
        state['device_qa']={'environment':result.get('environment'),'package':result.get('package'),
                            'apk_sha256':expected,'screenshot_sha256':result.get('screenshot_sha256'),
                            'network':result.get('network'),'reexported':reexported}
        state['completion']={'finished':False,'next_stage':'godot_runtime_journey_qa',
                             'reason':'Android install/launch/no-crash smoke passed; scripted journeys and visual acceptance remain required.'}
    state['release_status']='not_store_ready'
    parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
    (out/'report.json').write_text(canonical(state)); return state


def main(argv=None)->int:
    parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
    req=request_check(json.loads(Path(args.request).read_text()))
    state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
    return 0 if state.get('status')=='godot_device_validated' else 1


if __name__=='__main__':
    try: raise SystemExit(main())
    except (StudioError,ValueError,OSError,json.JSONDecodeError) as exc:
        print(str(exc) if isinstance(exc,StudioError) else type(exc).__name__); raise SystemExit(1)

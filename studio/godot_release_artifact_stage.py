"""Resumable signed AAB artifact stage with isolated signing boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

from core import StudioError, canonical, request_check
from godot_preview import _publish, _restore
from godot_release_artifact import build_unsigned_aab, install_source_template, sign_aab
from godot_release_qa import signing_credentials
from godot_runtime import install
from run import GitHub


def _sha(value)->bool:
    return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def execute(req:dict,root:Path,out:Path,github,runtime_installer=install,source_installer=install_source_template,
            builder=build_unsigned_aab,signer=sign_aab,env:dict|None=None)->dict:
    req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
    if any(root.iterdir()): raise StudioError('Workspace must be fresh for Godot release artifact stage')
    branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
    if not checkpoint or not isinstance(state,dict): raise StudioError('Godot release artifact stage requires studio checkpoint')
    if state.get('engine')!='godot' or state.get('status')!='godot_release_preflight_validated':
        raise StudioError('Godot release artifact stage requires validated release preflight')
    completion=state.get('completion'); preflight=state.get('release_preflight')
    if (not isinstance(completion,dict) or completion.get('finished') is not False or completion.get('next_stage')!='godot_release_artifact_qa'
            or not isinstance(preflight,dict) or preflight.get('format')!='aab' or preflight.get('target_api',0)<36):
        raise StudioError('Godot release artifact checkpoint contract invalid')
    current=os.environ if env is None else env
    credentials=signing_credentials(current)
    if not credentials.get('available'):
        state.update(status='godot_release_credentials_required',blockers=[credentials.get('blocker') or 'release_keystore_required'])
        state['release_status']='human_action_required'; state['completion']={'finished':False,'next_stage':'godot_release_qa','reason':'Release signing credentials are no longer available.'}
        parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent; (out/'report.json').write_text(canonical(state)); return state
    keystore=Path(current['GODOT_ANDROID_KEYSTORE_RELEASE_PATH']); alias=current['GODOT_ANDROID_KEYSTORE_RELEASE_USER']; password=current['GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD']
    unsigned=out/'app-unsigned.aab'; signed=out/'app-release.aab'
    with tempfile.TemporaryDirectory(prefix='studio-godot-release-artifact-') as td:
        cache=Path(td); binary=runtime_installer(cache/'runtime'); source_template=source_installer(cache/'templates')
        build=builder(root,binary,source_template,unsigned)
    if not build.get('passed') or not _sha(build.get('unsigned_aab_sha256')) or not unsigned.is_file():
        state.update(status='godot_release_artifact_qa_failed',blockers=['Unsigned AAB build failed'])
        state['completion']={'finished':False,'next_stage':'godot_release_artifact_qa','reason':'Offline unsigned AAB evidence incomplete.'}
        state['release_status']='not_store_ready'
    else:
        if build.get('network')!='none' or build.get('source_project')!='not_mounted' or build.get('signing_material_exposed') is not False:
            raise StudioError('Unsigned AAB build violated signing isolation contract')
        if hashlib.sha256(unsigned.read_bytes()).hexdigest()!=build['unsigned_aab_sha256']:
            raise StudioError('Unsigned AAB artifact hash mismatch')
        signed_evidence=signer(unsigned,signed,keystore,alias,password)
        (out/'godot-release-signing.json').write_text(canonical(signed_evidence))
        if (not signed_evidence.get('passed') or not _sha(signed_evidence.get('signed_aab_sha256'))
                or not _sha(signed_evidence.get('certificate_sha256')) or signed_evidence.get('signing_scope')!='artifact_only'
                or signed_evidence.get('project_code_had_signing_material') is not False or not signed.is_file()):
            raise StudioError('Signed AAB evidence contract invalid')
        if hashlib.sha256(signed.read_bytes()).hexdigest()!=signed_evidence['signed_aab_sha256']:
            raise StudioError('Signed AAB artifact hash mismatch')
        state.update(status='godot_release_artifact_validated',blockers=[])
        coverage=dict(state.get('coverage') or {}); coverage.update(release_artifact=True,release_signed=True)
        state['coverage']=coverage
        state['release_artifact']={'aab_sha256':signed_evidence['signed_aab_sha256'],'unsigned_aab_sha256':build['unsigned_aab_sha256'],
                                   'certificate_sha256':signed_evidence['certificate_sha256'],'format':'aab','target_api':preflight['target_api'],
                                   'package':preflight.get('package'),'version_code':preflight.get('version_code'),'version_name':preflight.get('version_name'),
                                   'signing_scope':'artifact_only','project_code_had_signing_material':False}
        state['completion']={'finished':False,'next_stage':'godot_store_metadata_qa',
                             'reason':'Signed AAB artifact verified; Play listing, privacy, security and publication evidence remain required.'}
        state['release_status']='not_store_ready'
    (out/'godot-release-build.json').write_text(canonical(build))
    parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent; (out/'report.json').write_text(canonical(state)); return state


def main(argv=None)->int:
    parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
    req=request_check(json.loads(Path(args.request).read_text())); state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
    return 0 if state.get('status') in {'godot_release_artifact_validated','godot_release_credentials_required'} else 1

if __name__=='__main__':
    try: raise SystemExit(main())
    except (StudioError,ValueError,OSError,json.JSONDecodeError) as exc:
        print(str(exc) if isinstance(exc,StudioError) else type(exc).__name__); raise SystemExit(1)

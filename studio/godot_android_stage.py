"""Resumable trusted Android-export stage for Godot studio checkpoints."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from core import StudioError, canonical, request_check
from godot_android_export import export_debug_apk, install_android_templates
from godot_preview import _publish, _restore
from godot_runtime import install
from run import GitHub


def execute(req: dict, root: Path, out: Path, github, runtime_installer=install,
            template_installer=install_android_templates, exporter=export_debug_apk) -> dict:
    req = request_check(req)
    root.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()): raise StudioError('Workspace must be fresh for Godot Android stage')
    branch = 'studio/' + req['id']
    state, parent, checkpoint = _restore(github, branch, root)
    if not checkpoint or not isinstance(state, dict): raise StudioError('Godot Android stage requires studio checkpoint')
    if state.get('engine') != 'godot' or state.get('status') != 'godot_preview_validated':
        raise StudioError('Godot Android stage requires validated preview checkpoint')
    completion = state.get('completion')
    if not isinstance(completion, dict) or completion.get('finished') is not False or completion.get('next_stage') != 'godot_android_export_qa':
        raise StudioError('Godot Android checkpoint stage contract invalid')
    artifact = out/'app-debug.apk'
    with tempfile.TemporaryDirectory(prefix='studio-godot-android-cache-') as cache:
        cache_root = Path(cache)
        binary = runtime_installer(cache_root/'runtime')
        templates = template_installer(cache_root/'templates')
        evidence = exporter(root, binary, templates, artifact_path=artifact)
    (out/'godot-android-export.json').write_text(canonical(evidence))
    if not evidence.get('passed') or not evidence.get('apk_sha256') or not artifact.is_file():
        state.update(status='godot_android_export_failed', blockers=['Godot Android debug export failed'])
        state['completion'] = {'finished':False,'next_stage':'godot_android_export_qa','reason':'Android export evidence incomplete.'}
    else:
        state.update(status='godot_android_export_validated', blockers=[])
        coverage = dict(state.get('coverage') or {})
        coverage.update(engine='godot', android_export=True, device_qa=False, visual_qa=False, journeys_executed=False)
        state['coverage'] = coverage
        state['android_export'] = {'apk_sha256':evidence['apk_sha256'],'preset':evidence['preset'],
                                   'engine_version':evidence['engine_version'],'templates_sha256':evidence['templates_sha256'],
                                   'release_signed':False}
        state['completion'] = {'finished':False,'next_stage':'godot_device_qa',
                               'reason':'Debug APK export passed; device/runtime/visual journey evidence still required.'}
    state['release_status'] = 'not_store_ready'
    parent = _publish(github, branch, parent, root, state)
    state['checkpoint_commit'] = parent
    (out/'report.json').write_text(canonical(state))
    return state


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
    req=request_check(json.loads(Path(args.request).read_text()))
    state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
    return 0 if state.get('status') == 'godot_android_export_validated' else 1


if __name__=='__main__':
    try: raise SystemExit(main())
    except (StudioError,ValueError,OSError,json.JSONDecodeError) as exc:
        print(str(exc) if isinstance(exc,StudioError) else type(exc).__name__); raise SystemExit(1)

"""Resumable Play release preflight for validated Godot visual checkpoints."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import StudioError, canonical, request_check
from godot_preview import _publish, _restore
from godot_release_qa import preflight
from run import GitHub


def execute(req:dict,root:Path,out:Path,github,validator=preflight)->dict:
    req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
    if any(root.iterdir()): raise StudioError('Workspace must be fresh for Godot release stage')
    branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
    if not checkpoint or not isinstance(state,dict): raise StudioError('Godot release stage requires studio checkpoint')
    if state.get('engine')!='godot' or state.get('status')!='godot_visual_validated':
        raise StudioError('Godot release stage requires validated visual checkpoint')
    completion=state.get('completion'); coverage=state.get('coverage') or {}
    if (not isinstance(completion,dict) or completion.get('finished') is not False or completion.get('next_stage')!='godot_release_qa'
            or coverage.get('visual_qa') is not True or coverage.get('journeys_executed') is not True):
        raise StudioError('Godot release checkpoint contract invalid')
    evidence=validator(root)
    (out/'godot-release-preflight.json').write_text(canonical(evidence))
    audit=evidence.get('audit') if isinstance(evidence,dict) else None
    if not isinstance(audit,dict) or audit.get('passed') is not True:
        state.update(status='godot_release_qa_failed',blockers=evidence.get('blockers') or ['Godot release preset invalid'])
        state['completion']={'finished':False,'next_stage':'godot_release_qa','reason':'Play release preset requirements are not satisfied.'}
        state['release_status']='not_store_ready'
    elif evidence.get('signing',{}).get('available') is not True:
        state.update(status='godot_release_credentials_required',blockers=evidence.get('blockers') or ['release_keystore_required'])
        state['release_preflight']={'package':audit.get('package'),'version_code':audit.get('version_code'),'version_name':audit.get('version_name'),
                                    'target_api':audit.get('target_api'),'format':audit.get('format'),'gradle':audit.get('gradle'),'arm64':audit.get('arm64'),
                                    'preset_normalized':bool(evidence.get('preset_normalized')),'aab_built':False}
        state['completion']={'finished':False,'next_stage':'godot_release_qa',
                             'reason':'Non-secret Play settings are ready; production upload keystore credentials are required.'}
        state['release_status']='human_action_required'
    else:
        if evidence.get('aab_built') is not False:
            raise StudioError('Godot release preflight cannot claim an AAB artifact')
        state.update(status='godot_release_preflight_validated',blockers=[])
        state['release_preflight']={'package':audit.get('package'),'version_code':audit.get('version_code'),'version_name':audit.get('version_name'),
                                    'target_api':audit.get('target_api'),'format':audit.get('format'),'gradle':audit.get('gradle'),'arm64':audit.get('arm64'),
                                    'preset_normalized':bool(evidence.get('preset_normalized')),'aab_built':False}
        state['completion']={'finished':False,'next_stage':'godot_release_artifact_qa',
                             'reason':'Play release configuration and signing inputs are present; signed AAB artifact evidence remains required.'}
        state['release_status']='not_store_ready'
    parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
    (out/'report.json').write_text(canonical(state)); return state


def main(argv=None)->int:
    parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
    req=request_check(json.loads(Path(args.request).read_text())); state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
    return 0 if state.get('status') in {'godot_release_preflight_validated','godot_release_credentials_required'} else 1

if __name__=='__main__':
    try: raise SystemExit(main())
    except (StudioError,ValueError,OSError,json.JSONDecodeError) as exc:
        print(str(exc) if isinstance(exc,StudioError) else type(exc).__name__); raise SystemExit(1)

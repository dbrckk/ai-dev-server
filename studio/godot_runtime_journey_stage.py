"""Resumable trusted execution stage for immutable Godot acceptance journeys."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from core import StudioError, canonical, request_check
from godot_preview import _publish, _restore
from godot_runtime import install
from godot_runtime_journeys import run_journeys
from journeys import validate_journeys
from run import GitHub


def execute(req:dict,root:Path,out:Path,github,runtime_installer=install,journey_runner=run_journeys)->dict:
    req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
    if any(root.iterdir()): raise StudioError('Workspace must be fresh for Godot runtime journey stage')
    branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
    if not checkpoint or not isinstance(state,dict): raise StudioError('Godot runtime journey stage requires studio checkpoint')
    if state.get('engine')!='godot' or state.get('status')!='godot_device_validated':
        raise StudioError('Godot runtime journey stage requires validated device checkpoint')
    completion=state.get('completion')
    if not isinstance(completion,dict) or completion.get('finished') is not False or completion.get('next_stage')!='godot_runtime_journey_qa':
        raise StudioError('Godot runtime journey checkpoint contract invalid')
    product=state.get('product')
    if not isinstance(product,dict): raise StudioError('Godot runtime journeys require immutable product evidence')
    try: journeys=validate_journeys(product.get('journeys'))
    except ValueError as exc: raise StudioError(str(exc)) from None
    with tempfile.TemporaryDirectory(prefix='studio-godot-journey-runtime-') as cache:
        binary=runtime_installer(Path(cache)); evidence=journey_runner(root,binary,journeys)
    (out/'godot-runtime-journeys.json').write_text(canonical(evidence))
    if not evidence.get('passed') or evidence.get('journeys_executed') is not True or evidence.get('journey_count')!=len(journeys):
        state.update(status='godot_runtime_journey_qa_failed',blockers=['Godot acceptance journeys did not all execute successfully'])
        state['completion']={'finished':False,'next_stage':'godot_runtime_journey_qa','reason':'Runtime journey evidence incomplete.'}
    else:
        expected=[item['id'] for item in journeys]
        if evidence.get('passed_ids')!=expected or evidence.get('network')!='none' or evidence.get('source_project')!='not_mounted':
            raise StudioError('Godot runtime journey evidence contract invalid')
        state.update(status='godot_runtime_journeys_validated',blockers=[])
        coverage=dict(state.get('coverage') or {}); coverage.update(engine='godot',android_export=True,device_qa=True,journeys_executed=True,visual_qa=False)
        state['coverage']=coverage
        state['runtime_journeys']={'journey_count':len(journeys),'passed_ids':expected,'network':'none',
                                   'binary_sha256':evidence.get('binary_sha256'),'harness':evidence.get('harness')}
        state['completion']={'finished':False,'next_stage':'godot_visual_qa',
                             'reason':'Acceptance journeys executed successfully; visual acceptance evidence remains required.'}
    state['release_status']='not_store_ready'; parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
    (out/'report.json').write_text(canonical(state)); return state


def main(argv=None)->int:
    parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
    req=request_check(json.loads(Path(args.request).read_text())); state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
    return 0 if state.get('status')=='godot_runtime_journeys_validated' else 1

if __name__=='__main__':
    try: raise SystemExit(main())
    except (StudioError,ValueError,OSError,json.JSONDecodeError) as exc:
        print(str(exc) if isinstance(exc,StudioError) else type(exc).__name__); raise SystemExit(1)

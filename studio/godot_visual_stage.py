"""Resumable Android-rendered visual acceptance stage for Godot checkpoints."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import StudioError, canonical, request_check
from godot_preview import _publish, _restore
from godot_visual_qa import capture_and_review
from journeys import validate_journeys
from run import GitHub


def execute(req:dict,root:Path,out:Path,github,visual_validator=capture_and_review)->dict:
    req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
    if any(root.iterdir()): raise StudioError('Workspace must be fresh for Godot visual stage')
    branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
    if not checkpoint or not isinstance(state,dict): raise StudioError('Godot visual stage requires studio checkpoint')
    if state.get('engine')!='godot' or state.get('status')!='godot_runtime_journeys_validated':
        raise StudioError('Godot visual stage requires validated runtime journeys')
    completion=state.get('completion'); coverage=state.get('coverage') or {}
    if (not isinstance(completion,dict) or completion.get('finished') is not False or completion.get('next_stage')!='godot_visual_qa'
            or coverage.get('journeys_executed') is not True or coverage.get('device_qa') is not True):
        raise StudioError('Godot visual checkpoint contract invalid')
    product=state.get('product'); design=state.get('design')
    if not isinstance(product,dict) or not isinstance(design,dict): raise StudioError('Godot visual QA requires product and design evidence')
    try: journeys=validate_journeys(product.get('journeys'))
    except ValueError as exc: raise StudioError(str(exc)) from None
    evidence=visual_validator(root,journeys,design,out)
    (out/'godot-visual-qa.json').write_text(canonical(evidence))
    expected=[item['id'] for item in journeys]
    if not evidence.get('passed'):
        state.update(status='godot_visual_qa_failed',blockers=evidence.get('blockers') or ['Godot visual acceptance failed'])
        state['completion']={'finished':False,'next_stage':'godot_visual_qa','reason':'Android-rendered visual evidence was rejected.'}
    else:
        hashes=evidence.get('screenshot_sha256')
        if (evidence.get('visual_reviewed') is not True or evidence.get('journey_ids')!=expected or evidence.get('network')!='airplane_mode'
                or not isinstance(hashes,list) or len(hashes)!=len(expected) or any(not isinstance(v,str) or len(v)!=64 for v in hashes)):
            raise StudioError('Godot visual QA returned invalid evidence contract')
        state.update(status='godot_visual_validated',blockers=[])
        coverage=dict(coverage); coverage.update(engine='godot',android_export=True,device_qa=True,journeys_executed=True,visual_qa=True)
        state['coverage']=coverage
        state['visual_qa']={'journey_ids':expected,'screenshot_sha256':hashes,'environment':evidence.get('environment'),
                            'review_model':evidence.get('review_model'),'network':'airplane_mode'}
        state['completion']={'finished':False,'next_stage':'godot_release_qa',
                             'reason':'Android-rendered journey screens passed visual review; release/store/privacy/security evidence remains required.'}
    state['release_status']='not_store_ready'; parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
    (out/'report.json').write_text(canonical(state)); return state


def main(argv=None)->int:
    parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
    req=request_check(json.loads(Path(args.request).read_text())); state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
    return 0 if state.get('status')=='godot_visual_validated' else 1

if __name__=='__main__':
    try: raise SystemExit(main())
    except (StudioError,ValueError,OSError,json.JSONDecodeError) as exc:
        print(str(exc) if isinstance(exc,StudioError) else type(exc).__name__); raise SystemExit(1)

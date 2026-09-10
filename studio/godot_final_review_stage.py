"""Resumable final Godot technical store-readiness review."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from core import StudioError,canonical,request_check
from godot_preview import _publish,_restore
from godot_final_review_qa import review
from run import GitHub

def execute(req:dict,root:Path,out:Path,github,reviewer=review)->dict:
    req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
    if any(root.iterdir()): raise StudioError('Workspace must be fresh for Godot final review stage')
    branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
    if not checkpoint or not isinstance(state,dict): raise StudioError('Godot final review requires studio checkpoint')
    if state.get('engine')!='godot' or state.get('status')!='godot_privacy_security_validated':
        raise StudioError('Godot final review requires validated privacy/security checkpoint')
    completion=state.get('completion')
    if not isinstance(completion,dict) or completion.get('finished') is not False or completion.get('next_stage')!='godot_final_review_qa':
        raise StudioError('Godot final review checkpoint contract invalid')
    evidence=reviewer(root,out,state); (out/'godot-final-review.json').write_text(canonical(evidence))
    if not evidence.get('passed') or evidence.get('technical_store_ready') is not True or evidence.get('published') is not False:
        state.update(status='godot_final_review_qa_failed',blockers=evidence.get('blockers') or ['Godot final release review failed'])
        state['completion']={'finished':False,'next_stage':'godot_final_review_qa','reason':'Final technical release evidence is incomplete.'}
        state['release_status']='not_store_ready'
    else:
        actions=evidence.get('human_actions_required')
        if not isinstance(actions,list) or 'play_console_submission' not in actions or 'data_safety_legal_attestation' not in actions:
            raise StudioError('Godot final review omitted mandatory human submission actions')
        state.update(status='godot_technical_store_ready',blockers=[])
        coverage=dict(state.get('coverage') or {}); coverage['final_review']=True; state['coverage']=coverage
        state['final_review']={'release_bundle_sha256':evidence.get('release_bundle_sha256'),'release_bundle':evidence.get('release_bundle')}
        state['release_status']='technical_store_ready'
        state['human_actions_required']=actions
        state['completion']={'finished':False,'next_stage':'godot_play_submission',
                             'reason':'All technical release evidence passed. Legal Play declarations and submission remain human actions.'}
    parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
    (out/'report.json').write_text(canonical(state)); return state

def main(argv=None)->int:
    p=argparse.ArgumentParser(); p.add_argument('request'); p.add_argument('--work',required=True); p.add_argument('--out',required=True); a=p.parse_args(argv)
    req=request_check(json.loads(Path(a.request).read_text())); state=execute(req,Path(a.work),Path(a.out),GitHub(req['target_repo']))
    return 0 if state.get('status')=='godot_technical_store_ready' else 1

if __name__=='__main__':
    try: raise SystemExit(main())
    except (StudioError,ValueError,OSError,json.JSONDecodeError) as exc:
        print(str(exc) if isinstance(exc,StudioError) else type(exc).__name__); raise SystemExit(1)

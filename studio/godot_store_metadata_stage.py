"""Resumable Godot Play metadata stage."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import StudioError, canonical, request_check
from godot_preview import _publish, _restore
from godot_store_metadata_qa import build
from run import GitHub

def execute(req:dict,root:Path,out:Path,github,builder=build)->dict:
    req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
    if any(root.iterdir()): raise StudioError('Workspace must be fresh for Godot store metadata stage')
    branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
    if not checkpoint or not isinstance(state,dict): raise StudioError('Godot store metadata stage requires studio checkpoint')
    if state.get('engine')!='godot' or state.get('status')!='godot_release_artifact_validated':
        raise StudioError('Godot store metadata stage requires validated release artifact')
    completion=state.get('completion'); coverage=state.get('coverage') or {}
    if (not isinstance(completion,dict) or completion.get('finished') is not False or
            completion.get('next_stage')!='godot_store_metadata_qa' or
            coverage.get('release_artifact') is not True or coverage.get('release_signed') is not True):
        raise StudioError('Godot store metadata checkpoint contract invalid')
    evidence=builder(req,root,out,state)
    (out/'godot-store-metadata.json').write_text(canonical(evidence))
    if not evidence.get('passed'):
        state.update(status='godot_store_metadata_qa_failed',blockers=evidence.get('blockers') or ['Godot Play metadata QA failed'])
        state['completion']={'finished':False,'next_stage':'godot_store_metadata_qa','reason':'Play listing evidence incomplete.'}
    else:
        if (evidence.get('release_aab_sha256')!=(state.get('release_artifact') or {}).get('aab_sha256') or
                evidence.get('screenshot_count',0)<2 or evidence.get('human_submission_required') is not True):
            raise StudioError('Godot store metadata evidence contract invalid')
        state.update(status='godot_store_metadata_validated',blockers=[])
        coverage=dict(coverage); coverage.update(store_metadata=True)
        state['coverage']=coverage
        state['store_metadata']={
            'manifest_sha256':evidence.get('manifest_sha256'),
            'listing':evidence.get('listing'),
            'assets':evidence.get('assets'),
            'screenshot_count':evidence.get('screenshot_count'),
            'privacy_preclassification':evidence.get('privacy'),
        }
        state['completion']={'finished':False,'next_stage':'godot_privacy_security_qa',
                             'reason':'Play listing package validated; privacy/security and final human Play declarations remain required.'}
    state['release_status']='not_store_ready'
    parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
    (out/'report.json').write_text(canonical(state)); return state

def main(argv=None)->int:
    parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
    req=request_check(json.loads(Path(args.request).read_text()))
    state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
    return 0 if state.get('status')=='godot_store_metadata_validated' else 1

if __name__=='__main__':
    try: raise SystemExit(main())
    except (StudioError,ValueError,OSError,json.JSONDecodeError) as exc:
        print(str(exc) if isinstance(exc,StudioError) else type(exc).__name__); raise SystemExit(1)

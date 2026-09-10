"""Resumable Godot privacy/security stage bound to release/store hashes."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from core import StudioError,canonical,request_check
from godot_preview import _publish,_restore
from godot_privacy_security_qa import audit
from run import GitHub

def execute(req:dict,root:Path,out:Path,github,auditor=audit)->dict:
    req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
    if any(root.iterdir()): raise StudioError('Workspace must be fresh for Godot privacy/security stage')
    branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
    if not checkpoint or not isinstance(state,dict): raise StudioError('Godot privacy/security stage requires studio checkpoint')
    if state.get('engine')!='godot' or state.get('status')!='godot_store_metadata_validated':
        raise StudioError('Godot privacy/security stage requires validated store metadata')
    completion=state.get('completion'); coverage=state.get('coverage') or {}
    if (not isinstance(completion,dict) or completion.get('finished') is not False or completion.get('next_stage')!='godot_privacy_security_qa'
            or coverage.get('store_metadata') is not True):
        raise StudioError('Godot privacy/security checkpoint contract invalid')
    evidence=auditor(root,out,state); (out/'godot-privacy-security.json').write_text(canonical(evidence))
    if not evidence.get('passed'):
        state.update(status='godot_privacy_security_qa_failed',blockers=evidence.get('blockers') or ['Godot privacy/security audit failed'])
        state['completion']={'finished':False,'next_stage':'godot_privacy_security_qa','reason':'Privacy/security evidence incomplete.'}
    else:
        artifact=state.get('release_artifact') or {}; store=state.get('store_metadata') or {}
        if (evidence.get('release_aab_sha256')!=artifact.get('aab_sha256') or evidence.get('store_manifest_sha256')!=store.get('manifest_sha256')
                or evidence.get('human_legal_attestation_required') is not True):
            raise StudioError('Godot privacy/security evidence contract invalid')
        state.update(status='godot_privacy_security_validated',blockers=[])
        coverage=dict(coverage); coverage.update(privacy_qa=True,security_qa=True)
        state['coverage']=coverage
        state['privacy_security']={
            'policy_sha256':evidence.get('policy_sha256'),'data_safety_sha256':evidence.get('data_safety_sha256'),
            'release_aab_sha256':evidence.get('release_aab_sha256'),'store_manifest_sha256':evidence.get('store_manifest_sha256'),
            'data_safety':evidence.get('data_safety'),
        }
        state['completion']={'finished':False,'next_stage':'godot_final_review_qa',
                             'reason':'Release-bound privacy/security checks passed; final independent release review and Play declarations remain required.'}
    state['release_status']='not_store_ready'
    parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
    (out/'report.json').write_text(canonical(state)); return state

def main(argv=None)->int:
    p=argparse.ArgumentParser(); p.add_argument('request'); p.add_argument('--work',required=True); p.add_argument('--out',required=True); a=p.parse_args(argv)
    req=request_check(json.loads(Path(a.request).read_text())); state=execute(req,Path(a.work),Path(a.out),GitHub(req['target_repo']))
    return 0 if state.get('status')=='godot_privacy_security_validated' else 1

if __name__=='__main__':
    try: raise SystemExit(main())
    except (StudioError,ValueError,OSError,json.JSONDecodeError) as exc:
        print(str(exc) if isinstance(exc,StudioError) else type(exc).__name__); raise SystemExit(1)

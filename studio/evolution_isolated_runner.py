"""Materialize, execute and score validated evolution candidates in isolation.

Candidate Python/tests run only in the pinned Flutter container with networking
removed, a read-only workspace, dropped Linux capabilities and no production
credentials. Trusted host-side code creates detached worktrees, runs the protected
factory smoke on baseline and candidate with a scrubbed environment, and feeds the
resulting machine evidence to the deterministic promotion evaluator. This module
never pushes or merges candidate code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from core import IMAGE, canonical
from evolution_benchmark import evaluate as evaluate_promotion
from evolution_candidate import PROTECTED_PATHS
from evolution_differential import evaluate as evaluate_differential

class IsolatedRunError(RuntimeError): pass
SAFE_ENV={'PATH':'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin','HOME':'/tmp/home','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1'}
def _run(args,*,cwd=None,timeout=300,env=None,check=False):
    result=subprocess.run(args,cwd=cwd,env=env,text=True,capture_output=True,timeout=timeout)
    if check and result.returncode: raise IsolatedRunError('Trusted command failed: '+args[0])
    return result
def _sha(value,label):
    if not isinstance(value,str) or not re.fullmatch(r'[0-9a-f]{40}',value): raise IsolatedRunError(label+' SHA invalid')
    return value
def _test_path(validated_candidate):
    paths=[item.get('path') for item in validated_candidate.get('files',[]) if isinstance(item,dict) and isinstance(item.get('path'),str) and item['path'].startswith('tests/test_')]
    if len(paths)!=1: raise IsolatedRunError('Validated candidate must contain exactly one primary test file')
    return paths[0]
def _materialize_candidate(root,validated_candidate):
    for item in validated_candidate.get('files',[]):
        if not isinstance(item,dict) or set(item)!={'path','content'}: raise IsolatedRunError('Validated candidate files malformed')
        target=root/item['path']
        if not target.resolve().is_relative_to(root.resolve()): raise IsolatedRunError('Candidate path escaped worktree')
        target.parent.mkdir(parents=True,exist_ok=True); target.write_text(item['content'])
def _protected_hashes(root):
    result={}
    for path in sorted(PROTECTED_PATHS):
        file=root/path
        if file.is_file(): result[path]=hashlib.sha256(file.read_bytes()).hexdigest()
    if not result: raise IsolatedRunError('Protected factory files missing from worktree')
    return result
def _docker_python(root,python_args,timeout=300):
    if shutil.which('docker') is None: raise IsolatedRunError('Docker unavailable for candidate isolation')
    command=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','128','--memory','1024m','--cpus','2','--tmpfs','/tmp:rw,noexec,nosuid,size=256m','-e','HOME=/tmp/home','-e','LANG=C.UTF-8','-e','LC_ALL=C.UTF-8','-e','PYTHONDONTWRITEBYTECODE=1','-e','PYTHONUNBUFFERED=1','-v',str(root.resolve())+':/workspace:ro','-w','/workspace',IMAGE,'python3',*python_args]
    return _run(command,timeout=timeout,env=SAFE_ENV)
def _trusted_flutter_smoke(root,smoke_root,timeout=900):
    if smoke_root.exists(): raise IsolatedRunError('Smoke root already exists')
    env=dict(SAFE_ENV); env['STUDIO_SMOKE_ROOT']=str(smoke_root)
    return _run(['python3','studio/smoke.py'],cwd=root,timeout=timeout,env=env).returncode==0
def _parse_unittest(output,returncode):
    match=re.search(r'Ran\s+(\d+)\s+tests?',output); count=int(match.group(1)) if match else 0; failures=0; errors=0; failed=re.search(r'FAILED\s*\(([^)]*)\)',output)
    if failed:
        for key,value in re.findall(r'(failures|errors)=(\d+)',failed.group(1)):
            if key=='failures': failures=int(value)
            elif key=='errors': errors=int(value)
    passed=returncode==0 and count>0 and failures==0 and errors==0
    return {'passed':passed,'count':count,'failures':failures,'errors':errors}
def _candidate_test_result(root,commit_sha,test_file):
    result=_docker_python(root,['-m','unittest','discover','-s','tests','-p',Path(test_file).name,'-v']); parsed=_parse_unittest((result.stdout or '')+'\n'+(result.stderr or ''),result.returncode)
    return {'commit_sha':commit_sha,'test_file':test_file,'tests_collected':parsed['count'],'failures':parsed['failures'],'errors':parsed['errors'],'passed':parsed['passed']}
def _copy_test_into_baseline(candidate_root,baseline_root,test_file):
    source=candidate_root/test_file
    if not source.is_file(): raise IsolatedRunError('Candidate differential test missing')
    target=baseline_root/test_file; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(source.read_bytes())
def _commit_candidate(candidate_root,baseline_sha,paths):
    _run(['git','add','--',*paths],cwd=candidate_root,check=True); env=dict(SAFE_ENV); env['GIT_AUTHOR_NAME']=env['GIT_COMMITTER_NAME']='ai-dev-server evolution'; env['GIT_AUTHOR_EMAIL']=env['GIT_COMMITTER_EMAIL']='evolution@localhost'
    _run(['git','commit','--no-gpg-sign','-m','Validated autonomous evolution candidate'],cwd=candidate_root,env=env,check=True); sha=_run(['git','rev-parse','HEAD'],cwd=candidate_root,check=True).stdout.strip()
    if sha==baseline_sha: raise IsolatedRunError('Candidate commit did not advance baseline')
    return _sha(sha,'Candidate')
def _is_reversible(candidate_root,baseline_sha): return _run(['git','rev-parse','HEAD^'],cwd=candidate_root).stdout.strip()==baseline_sha
def _capability_result(gap,assertions,passed):
    if type(assertions) is not int or assertions<1: raise IsolatedRunError('Validated candidate benchmark assertion count missing')
    return {'gap':gap,'passed':passed,'assertions_total':assertions,'assertions_passed':assertions if passed else 0}
def execute(repo_root,work_order,validated_candidate,out):
    baseline_sha=_sha(work_order.get('baseline_sha'),'Baseline')
    if validated_candidate.get('status')!='candidate_validated' or validated_candidate.get('candidate_id')!=work_order.get('candidate_id'): raise IsolatedRunError('Validated candidate identity mismatch')
    gap=validated_candidate.get('gap')
    if not isinstance(gap,str) or gap!=(work_order.get('primary_gap') or {}).get('value'): raise IsolatedRunError('Validated candidate gap mismatch')
    assertions=validated_candidate.get('benchmark_assertions')
    if validated_candidate.get('differential_tests')!=assertions: raise IsolatedRunError('Candidate benchmark/test cardinality mismatch')
    if _run(['git','cat-file','-e',baseline_sha+'^{commit}'],cwd=repo_root).returncode: raise IsolatedRunError('Pinned baseline commit unavailable locally')
    out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='evolution-run-') as tmp:
        temp=Path(tmp); baseline_root=temp/'baseline'; candidate_root=temp/'candidate'; _run(['git','worktree','add','--detach',str(baseline_root),baseline_sha],cwd=repo_root,check=True)
        try:
            _run(['git','worktree','add','--detach',str(candidate_root),baseline_sha],cwd=repo_root,check=True)
            try:
                _materialize_candidate(candidate_root,validated_candidate); paths=[item['path'] for item in validated_candidate['files']]; candidate_sha=_commit_candidate(candidate_root,baseline_sha,paths); reversible=_is_reversible(candidate_root,baseline_sha); test_file=_test_path(validated_candidate); _copy_test_into_baseline(candidate_root,baseline_root,test_file)
                baseline_diff=_candidate_test_result(baseline_root,baseline_sha,test_file); candidate_diff=_candidate_test_result(candidate_root,candidate_sha,test_file); differential=evaluate_differential(work_order,validated_candidate,baseline_diff,candidate_diff); capability_passed=bool(differential.get('improvement_proved'))
                braw=_docker_python(baseline_root,['-m','unittest','discover','-s','tests','-v']); craw=_docker_python(candidate_root,['-m','unittest','discover','-s','tests','-v']); btests=_parse_unittest((braw.stdout or '')+'\n'+(braw.stderr or ''),braw.returncode); ctests=_parse_unittest((craw.stdout or '')+'\n'+(craw.stderr or ''),craw.returncode)
                bcompile=_docker_python(baseline_root,['-m','compileall','-q','studio','tests']).returncode==0; ccompile=_docker_python(candidate_root,['-m','compileall','-q','studio','tests']).returncode==0; bsmoke=_trusted_flutter_smoke(baseline_root,temp/'baseline-smoke'); csmoke=_trusted_flutter_smoke(candidate_root,temp/'candidate-smoke')
                baseline={'version':1,'commit_sha':baseline_sha,'compile_passed':bcompile,'unit_tests':btests,'flutter_smoke_passed':bsmoke,'protected_hashes':_protected_hashes(baseline_root),'capability_benchmark':_capability_result(gap,assertions,False),'reversible':True}
                candidate={'version':1,'commit_sha':candidate_sha,'compile_passed':ccompile,'unit_tests':ctests,'flutter_smoke_passed':csmoke,'protected_hashes':_protected_hashes(candidate_root),'capability_benchmark':_capability_result(gap,assertions,capability_passed),'reversible':reversible}
                promotion=evaluate_promotion(work_order,baseline,candidate,differential); evidence={'version':2,'status':'isolated_benchmark_complete','candidate_id':work_order.get('candidate_id'),'baseline_sha':baseline_sha,'candidate_sha':candidate_sha,'network':'disabled_for_candidate_code','candidate_workspace':'read_only','candidate_capabilities':'dropped','credentials_exposed_to_candidate':False,'baseline':baseline,'candidate':candidate,'differential':differential,'promotion':promotion}
                (out/'evolution-isolated-benchmark.json').write_text(canonical(evidence)+'\n'); (out/'evolution-promotion.json').write_text(canonical(promotion)+'\n'); return evidence
            finally: _run(['git','worktree','remove','--force',str(candidate_root)],cwd=repo_root)
        finally: _run(['git','worktree','remove','--force',str(baseline_root)],cwd=repo_root)
def main(argv=None):
    parser=argparse.ArgumentParser(); parser.add_argument('work_order'); parser.add_argument('candidate'); parser.add_argument('--repo-root',default='.'); parser.add_argument('--out',default='studio-output'); args=parser.parse_args(argv); out=Path(args.out)
    try:
        order=json.loads(Path(args.work_order).read_text()); candidate=json.loads(Path(args.candidate).read_text()); evidence=execute(Path(args.repo_root),order,candidate,out); print(canonical({'status':evidence['status'],'promotion':evidence['promotion']['status']})); return 0
    except (OSError,ValueError,json.JSONDecodeError,subprocess.SubprocessError,IsolatedRunError) as exc:
        out.mkdir(parents=True,exist_ok=True); (out/'evolution-isolated-error.json').write_text(canonical({'status':'isolated_benchmark_blocked','error':type(exc).__name__})+'\n'); return 1
if __name__=='__main__': sys.exit(main())

"""Fail-closed contract for synthesized factory-evolution candidates.

A candidate may add only the missing trusted QA implementation, its trusted stage
adapter, tests and a benchmark fixture. It cannot edit completion/security/privacy
contracts, CI workflows, existing tests, or other trusted factory code. Registry
changes are deliberately reserved for the later trusted promotion layer.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import PurePosixPath
import re

VERSION = 1
MAX_FILES = 6
MAX_FILE_BYTES = 80_000
MAX_TOTAL_BYTES = 220_000

PROTECTED_PATHS = {
    'studio/completion.py','studio/core.py','studio/security_audit.py','studio/privacy_audit.py',
    'studio/stage_registry.py','studio/orchestrator.py','studio/github_runner.py','studio/ci_runner.py',
    'studio/smoke.py','studio/adaptation.py','studio/evolution_executor.py','studio/evolution_evidence.py',
    'studio/evolution_research.py','studio/evolution_synthesis.py','studio/evolution_candidate.py',
    'studio/evolution_benchmark.py','studio/evolution_differential.py','studio/evolution_isolated_runner.py',
    'studio/evolution_promotion.py','studio/evolution_rollback.py','studio/evolution_stage_runner.py',
    'studio/evolution_persist.py','studio/evolution_pending.py','studio/evolution_automerge.py',
    'studio/project_engine.py','studio/existing_project.py','studio/godot_runtime.py','studio/engine_patch.py',
    '.github/workflows/validate.yml','.github/workflows/studio-smoke.yml','.github/workflows/mobile-studio.yml',
    '.circleci/config.yml',
}
FORBIDDEN_CALLS = {'eval','exec','compile','__import__','os.system','os.popen','subprocess.call',
    'subprocess.check_call','subprocess.check_output','unittest.skip','unittest.skipIf','unittest.skipUnless','pytest.skip'}
SECRET_PATTERNS = (re.compile(r'gh[pousr]_[A-Za-z0-9_]{20,}'),re.compile(r'AIza[0-9A-Za-z_-]{20,}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'))

class CandidateRejected(ValueError): pass

def _gap(value):
    if not isinstance(value,str) or not re.fullmatch(r'[a-z][a-z0-9_]{2,48}',value): raise CandidateRejected('Candidate gap name invalid')
    if not value.endswith('_qa'): raise CandidateRejected('Evolution candidates currently require a QA stage gap')
    return value

def expected_paths(gap):
    gap=_gap(gap); base=gap[:-3]
    return {'implementation':f'studio/{gap}.py','stage':f'studio/{base}_stage.py','tests':f'tests/test_{gap}.py','benchmark':f'tests/benchmarks/{gap}.json'}
def _safe_path(path):
    if not isinstance(path,str) or not path or '\\' in path or path.startswith('/'): raise CandidateRejected('Candidate path invalid')
    p=PurePosixPath(path)
    if '..' in p.parts or '.' in p.parts or any(not part for part in p.parts): raise CandidateRejected('Candidate path traversal rejected')
    normalized=p.as_posix()
    if normalized in PROTECTED_PATHS or normalized.startswith('.github/') or normalized.startswith('.circleci/'): raise CandidateRejected('Candidate attempted to modify protected factory policy')
    return normalized
def _call_name(node):
    target=node.func
    if isinstance(target,ast.Name): return target.id
    parts=[]
    while isinstance(target,ast.Attribute): parts.append(target.attr); target=target.value
    if isinstance(target,ast.Name): parts.append(target.id); return '.'.join(reversed(parts))
    return ''
def _decorator_name(node):
    if isinstance(node,ast.Name): return node.id
    if isinstance(node,ast.Attribute):
        parts=[]; target=node
        while isinstance(target,ast.Attribute): parts.append(target.attr); target=target.value
        if isinstance(target,ast.Name): parts.append(target.id); return '.'.join(reversed(parts))
    if isinstance(node,ast.Call): return _decorator_name(node.func)
    return ''
def _python_tree(path,content):
    try: return ast.parse(content,filename=path)
    except SyntaxError: raise CandidateRejected('Candidate Python does not parse') from None
def _validate_python(path,content):
    tree=_python_tree(path,content)
    for node in ast.walk(tree):
        if isinstance(node,(ast.Global,ast.Nonlocal)): raise CandidateRejected('Candidate global/nonlocal mutation rejected')
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                if _decorator_name(decorator) in {'unittest.skip','unittest.skipIf','unittest.skipUnless','pytest.mark.skip','pytest.mark.skipif'}: raise CandidateRejected('Candidate skipped tests rejected')
        if isinstance(node,ast.Call):
            name=_call_name(node)
            if name in FORBIDDEN_CALLS: raise CandidateRejected('Candidate dangerous execution primitive rejected')
            if name.startswith('subprocess.'):
                for keyword in node.keywords:
                    if keyword.arg=='shell' and isinstance(keyword.value,ast.Constant) and keyword.value.value is True: raise CandidateRejected('Candidate shell execution rejected')
        if isinstance(node,ast.Import):
            for alias in node.names:
                if alias.name in {'socket','ctypes'}: raise CandidateRejected('Candidate low-level runtime import rejected')
        if isinstance(node,ast.ImportFrom) and node.module in {'socket','ctypes'}: raise CandidateRejected('Candidate low-level runtime import rejected')
def _validate_benchmark(content,gap):
    try: value=json.loads(content)
    except json.JSONDecodeError: raise CandidateRejected('Candidate benchmark JSON invalid') from None
    if not isinstance(value,dict) or set(value)!={'version','id','gap','purpose','assertions'} or value.get('version')!=1: raise CandidateRejected('Candidate benchmark schema invalid')
    if value.get('gap')!=gap: raise CandidateRejected('Candidate benchmark gap mismatch')
    if not isinstance(value.get('id'),str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{2,64}',value['id']): raise CandidateRejected('Candidate benchmark id invalid')
    if not isinstance(value.get('purpose'),str) or not value['purpose'].strip() or len(value['purpose'])>500: raise CandidateRejected('Candidate benchmark purpose invalid')
    assertions=value.get('assertions')
    if not isinstance(assertions,list) or not 1<=len(assertions)<=20 or any(not isinstance(item,str) or not item.strip() or len(item)>300 for item in assertions): raise CandidateRejected('Candidate benchmark assertions invalid')
    if len(set(assertions))!=len(assertions): raise CandidateRejected('Candidate benchmark assertions must be distinct')
    return value
def _test_method_count(content):
    tree=_python_tree('candidate_test.py',content); names=[node.name for node in ast.walk(tree) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name.startswith('test_')]
    if len(names)!=len(set(names)): raise CandidateRejected('Candidate test method names must be unique')
    return len(names)
def _reject_top_level_candidate_import(test_content,gap):
    tree=_python_tree('candidate_test.py',test_content); targets={gap,'studio.'+gap}
    for node in tree.body:
        if isinstance(node,ast.Import):
            if any(alias.name in targets for alias in node.names): raise CandidateRejected('Candidate capability import must occur inside each test')
        elif isinstance(node,ast.ImportFrom) and node.module in targets: raise CandidateRejected('Candidate capability import must occur inside each test')
def validate_candidate(work_order,research,candidate):
    if not isinstance(work_order,dict) or work_order.get('status')!='candidate_planned': raise CandidateRejected('Candidate requires a planned work order')
    if not isinstance(research,dict) or research.get('status')!='research_complete': raise CandidateRejected('Candidate requires completed trusted research')
    candidate_id=work_order.get('candidate_id')
    if research.get('candidate_id')!=candidate_id: raise CandidateRejected('Research candidate id mismatch')
    primary=work_order.get('primary_gap'); gap=_gap(primary.get('value') if isinstance(primary,dict) else None)
    if not isinstance(candidate,dict) or set(candidate)!={'version','candidate_id','gap','files'}: raise CandidateRejected('Candidate envelope malformed')
    if candidate.get('version')!=VERSION or candidate.get('candidate_id')!=candidate_id or candidate.get('gap')!=gap: raise CandidateRejected('Candidate identity mismatch')
    files=candidate.get('files')
    if not isinstance(files,list) or not 1<=len(files)<=MAX_FILES: raise CandidateRejected('Candidate file count invalid')
    expected=expected_paths(gap); allowed=set(expected.values()); normalized=[]; seen=set(); total=0; benchmark_value=None; test_content=None
    for item in files:
        if not isinstance(item,dict) or set(item)!={'path','content'}: raise CandidateRejected('Candidate file entry malformed')
        path=_safe_path(item.get('path'))
        if path not in allowed: raise CandidateRejected('Candidate path is outside missing-capability scope')
        if path in seen: raise CandidateRejected('Candidate duplicate path')
        seen.add(path); content=item.get('content')
        if not isinstance(content,str): raise CandidateRejected('Candidate file content invalid')
        size=len(content.encode())
        if size==0 or size>MAX_FILE_BYTES: raise CandidateRejected('Candidate file size invalid')
        total+=size
        if total>MAX_TOTAL_BYTES: raise CandidateRejected('Candidate payload too large')
        if any(pattern.search(content) for pattern in SECRET_PATTERNS): raise CandidateRejected('Candidate contains credential-like material')
        if path.endswith('.py'):
            _validate_python(path,content)
            if path==expected['tests']: test_content=content
        else: benchmark_value=_validate_benchmark(content,gap)
        normalized.append({'path':path,'content':content})
    missing=[role for role,path in expected.items() if path not in seen]
    if missing: raise CandidateRejected('Candidate missing required artifacts: '+','.join(missing))
    if not isinstance(test_content,str) or not isinstance(benchmark_value,dict): raise CandidateRejected('Candidate test/benchmark evidence missing')
    _reject_top_level_candidate_import(test_content,gap)
    test_count=_test_method_count(test_content); assertion_count=len(benchmark_value['assertions'])
    if test_count<1 or test_count!=assertion_count: raise CandidateRejected('Candidate requires exactly one concrete test per benchmark assertion')
    digest_payload={'candidate_id':candidate_id,'gap':gap,'files':[{'path':item['path'],'sha256':hashlib.sha256(item['content'].encode()).hexdigest()} for item in sorted(normalized,key=lambda x:x['path'])]}
    digest=hashlib.sha256(json.dumps(digest_payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'version':VERSION,'status':'candidate_validated','candidate_id':candidate_id,'candidate_branch':work_order.get('candidate_branch'),'baseline_sha':work_order.get('baseline_sha'),'gap':gap,'files':normalized,'candidate_sha256':digest,'benchmark_assertions':assertion_count,'differential_tests':test_count,'protected_paths_enforced':True,'registry_change_reserved_for_promotion':True}

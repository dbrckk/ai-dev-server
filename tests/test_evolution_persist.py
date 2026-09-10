import hashlib
import json
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from evolution_persist import PersistenceError,_branch_prefix,persist
from orchestrator import _run_adaptation_persistence

BASELINE='a'*40; CANDIDATE_SHA='b'*40; COMMIT='c'*40; CANDIDATE='candidate-12345678'; GAP='future_capability_qa'

class EvolutionPersistTests(unittest.TestCase):
    def fixture(self,root):
        candidate_files={'studio/future_capability_stage.py':'stage-fixture','studio/future_capability_qa.py':'implementation-fixture','tests/test_future_capability_qa.py':'tests-fixture','tests/benchmarks/future_capability_qa.json':'benchmark-fixture'}
        for rel,content in candidate_files.items():
            path=root/rel; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content)
        registry=root/'control/promoted_stages.json'; registry.parent.mkdir(parents=True,exist_ok=True)
        registry.write_text(json.dumps({'version':1,'stages':{GAP:{'script':'studio/future_capability_stage.py','candidate_id':CANDIDATE,'baseline_sha':BASELINE,'candidate_sha':CANDIDATE_SHA}}}))
        rollback=root/'control/evolution_rollbacks'/(CANDIDATE+'.json'); rollback.parent.mkdir(parents=True,exist_ok=True)
        rollback.write_text(json.dumps({'version':2,'candidate_id':CANDIDATE,'gap':GAP,'baseline_sha':BASELINE,'candidate_sha':CANDIDATE_SHA,'created_paths':sorted(candidate_files),'created_sha256':{rel:hashlib.sha256(content.encode()).hexdigest() for rel,content in candidate_files.items()},'registry_before':{'version':1,'stages':{}},'registry_sha256_before':'0'*64}))
        return {'status':'promoted','candidate_id':CANDIDATE,'gap':GAP,'candidate_sha':CANDIDATE_SHA}

    def api(self,existing=False,moved=False,different_tree=False):
        blobs={'n':0}; branch=_branch_prefix(GAP,CANDIDATE)+COMMIT
        def request(url,token,method='GET',payload=None,allow_404=False):
            if url.endswith('/git/commits/'+BASELINE): return {'tree':{'sha':'base-tree'}}
            if url.endswith('/git/blobs'):
                blobs['n']+=1; return {'sha':'blob-'+str(blobs['n'])}
            if url.endswith('/git/trees'): return {'sha':'candidate-tree'}
            if '/git/matching-refs/heads/' in url:
                return [{'ref':'refs/heads/'+branch,'object':{'sha':'d'*40 if moved else COMMIT}}] if existing else []
            if url.endswith('/git/commits/'+COMMIT): return {'tree':{'sha':'different-tree' if different_tree else 'candidate-tree'},'parents':[{'sha':BASELINE}]}
            if url.endswith('/git/commits') and method=='POST': return {'sha':COMMIT}
            if url.endswith('/git/refs') and method=='POST': return {'ref':'refs/heads/'+branch,'object':{'sha':COMMIT}}
            if '/pulls?' in url: return [{'number':17,'head':{'sha':COMMIT,'ref':branch}}] if existing else []
            if url.endswith('/pulls') and method=='POST': return {'number':17}
            raise AssertionError(url)
        return request,branch

    def test_new_branch_encodes_exact_approved_commit_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); applied=self.fixture(root); request,branch=self.api()
            with patch('evolution_persist._request',side_effect=request): result=persist(root,applied,'token','owner/repo',BASELINE)
            self.assertEqual(result['status'],'promotion_persisted'); self.assertEqual(result['commit_sha'],COMMIT); self.assertEqual(result['branch'],branch)
            self.assertTrue(branch.endswith(COMMIT))

    def test_existing_identical_content_bound_branch_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); applied=self.fixture(root); request,branch=self.api(existing=True)
            with patch('evolution_persist._request',side_effect=request): result=persist(root,applied,'token','owner/repo',BASELINE)
            self.assertEqual(result['status'],'already_persisted'); self.assertEqual(result['pull_request'],17); self.assertEqual(result['branch'],branch)

    def test_force_moved_existing_branch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); applied=self.fixture(root); request,_=self.api(existing=True,moved=True)
            with patch('evolution_persist._request',side_effect=request):
                with self.assertRaisesRegex(PersistenceError,'approved SHA'): persist(root,applied,'token','owner/repo',BASELINE)

    def test_existing_branch_with_different_tree_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); applied=self.fixture(root); request,_=self.api(existing=True,different_tree=True)
            with patch('evolution_persist._request',side_effect=request):
                with self.assertRaisesRegex(PersistenceError,'different content'): persist(root,applied,'token','owner/repo',BASELINE)

    def test_modified_promoted_file_is_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); applied=self.fixture(root); (root/'studio/future_capability_qa.py').write_text('tampered')
            with patch('evolution_persist._request') as request:
                with self.assertRaisesRegex(PersistenceError,'changed after approval'): persist(root,applied,'token','owner/repo',BASELINE)
            request.assert_not_called()

    def test_github_orchestrator_requires_persistence_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp); (out/'evolution-applied.json').write_text(json.dumps({'status':'promoted','candidate_id':CANDIDATE,'gap':GAP,'candidate_sha':CANDIDATE_SHA}))
            calls=[]
            def runner(args,timeout):
                calls.append(args); (out/'evolution-persisted.json').write_text(json.dumps({'status':'promotion_persisted','candidate_id':CANDIDATE,'gap':GAP,'pull_request':17})); return subprocess.CompletedProcess(args,0)
            with patch.dict('os.environ',{'STUDIO_CI_PROVIDER':'github'},clear=True): status=_run_adaptation_persistence(out,100,runner,lambda:0)
            self.assertEqual(status,'persisted'); self.assertTrue(any('studio/evolution_persist.py' in call for call in calls))

    def test_non_github_provider_does_not_attempt_github_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls=[]
            with patch.dict('os.environ',{'STUDIO_CI_PROVIDER':'circleci'},clear=True): status=_run_adaptation_persistence(Path(tmp),100,lambda args,timeout:calls.append(args),lambda:0)
            self.assertEqual(status,'not_applicable'); self.assertEqual(calls,[])

if __name__=='__main__': unittest.main()

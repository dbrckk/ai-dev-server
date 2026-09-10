import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_pending import check
from evolution_persist import _branch_prefix
from orchestrator import _run_adaptation_pending

CANDIDATE='future-capability-qa-123456789abc'; GAP='future_capability_qa'; BASELINE='a'*40; COMMIT='b'*40

def order(): return {'status':'candidate_planned','candidate_id':CANDIDATE,'baseline_sha':BASELINE,'primary_gap':{'value':GAP}}
def branch(): return _branch_prefix(GAP,CANDIDATE)+COMMIT
def pr(state='open',merged_at=None,sha=COMMIT,ref=None,number=9):
    return {'number':number,'state':state,'merged_at':merged_at,'head':{'sha':sha,'ref':ref or branch()}}

class EvolutionPendingTests(unittest.TestCase):
    def test_no_pr_and_no_branch_allows_new_evolution(self):
        def request(url,token,method='GET',payload=None,allow_404=False):
            if '/pulls?' in url: return []
            if '/git/matching-refs/heads/' in url: return []
            raise AssertionError(url)
        with patch('evolution_pending._request',side_effect=request): result=check(order(),'token','owner/repo')
        self.assertEqual(result['status'],'no_pending_promotion')

    def test_open_pr_recovers_branch_name_sha_proof(self):
        def request(url,token,method='GET',payload=None,allow_404=False):
            if '/pulls?' in url: return [pr()]
            if '/git/ref/heads/' in url: return {'object':{'sha':COMMIT}}
            raise AssertionError(url)
        with patch('evolution_pending._request',side_effect=request): result=check(order(),'token','owner/repo')
        self.assertEqual(result['status'],'promotion_pending_merge'); self.assertEqual(result['commit_sha'],COMMIT)
        self.assertEqual(result['branch'],branch()); self.assertEqual(result['proof'],'branch_name_sha_v1')

    def test_force_moved_branch_is_orphaned(self):
        def request(url,token,method='GET',payload=None,allow_404=False):
            if '/pulls?' in url: return [pr()]
            if '/git/ref/heads/' in url: return {'object':{'sha':'c'*40}}
            raise AssertionError(url)
        with patch('evolution_pending._request',side_effect=request): result=check(order(),'token','owner/repo')
        self.assertEqual(result['status'],'promotion_orphaned')

    def test_pr_head_not_equal_encoded_sha_is_orphaned(self):
        with patch('evolution_pending._request',return_value=[pr(sha='c'*40)]):
            result=check(order(),'token','owner/repo')
        self.assertEqual(result['status'],'promotion_orphaned')

    def test_multiple_candidate_prs_fail_closed(self):
        with patch('evolution_pending._request',return_value=[pr(number=9),pr(number=10)]):
            result=check(order(),'token','owner/repo')
        self.assertEqual(result['status'],'promotion_orphaned')

    def test_merged_pr_survives_deleted_branch(self):
        with patch('evolution_pending._request',return_value=[pr(state='closed',merged_at='2026-09-09T19:00:00Z')]):
            result=check(order(),'token','owner/repo')
        self.assertEqual(result['status'],'promotion_merged_restart_required'); self.assertEqual(result['commit_sha'],COMMIT)

    def test_orchestrator_maps_open_pr_to_pending_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp); (out/'evolution-work-order.json').write_text(json.dumps(order()))
            def runner(args,timeout):
                (out/'evolution-pending.json').write_text(json.dumps({'status':'promotion_pending_merge'})); return type('Result',(),{'returncode':0})()
            with patch.dict('os.environ',{'STUDIO_CI_PROVIDER':'github'},clear=True): status=_run_adaptation_pending(out,100,runner,lambda:0)
            self.assertEqual(status,'pending_merge')

if __name__=='__main__': unittest.main()

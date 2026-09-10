from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from evolution_automerge import AutoMergeError, attempt
from evolution_candidate import expected_paths
from evolution_persist import _branch_prefix

CANDIDATE='future-capability-qa-123456789abc'; GAP='future_capability_qa'; HEAD='b'*40
BRANCH=_branch_prefix(GAP,CANDIDATE)+HEAD

def order(): return {'status':'candidate_planned','candidate_id':CANDIDATE,'primary_gap':{'value':GAP},'baseline_sha':'a'*40}
def persisted(): return {'status':'promotion_persisted','candidate_id':CANDIDATE,'gap':GAP,'branch':BRANCH,'commit_sha':HEAD,'pull_request':12}
def pending(): return {'status':'promotion_pending_merge','candidate_id':CANDIDATE,'gap':GAP,'branch':BRANCH,'commit_sha':HEAD,'pull_request':12,'proof':'branch_name_sha_v1'}
def files(extra=None):
    names=set(expected_paths(GAP).values())|{'control/promoted_stages.json','control/evolution_rollbacks/'+CANDIDATE+'.json'}
    if extra: names.add(extra)
    return [{'filename':name,'status':'modified' if name=='control/promoted_stages.json' else 'added'} for name in sorted(names)]
def check(name,status='completed',conclusion='success',slug='github-actions',details='https://github.com/owner/repo/actions/runs/123/job/4'):
    return {'name':name,'status':status,'conclusion':conclusion,'app':{'slug':slug},'details_url':details}

def request_for(checks=None,head=HEAD,extra=None):
    def req(url,token,method='GET',payload=None,allow_404=False):
        if url.endswith('/pulls/12'): return {'state':'open','draft':False,'mergeable':True,'mergeable_state':'clean','base':{'ref':'main'},'head':{'ref':BRANCH,'sha':head}}
        if '/pulls/12/files?' in url: return files(extra)
        if '/check-runs?' in url: return {'check_runs':checks if checks is not None else [check('validate'),check('mobile-smoke')]}
        if url.endswith('/pulls/12/merge') and method=='PUT': return {'merged':True,'sha':'d'*40}
        raise AssertionError(url)
    return req

class EvolutionAutoMergeTests(unittest.TestCase):
    def test_restarted_runner_can_merge_from_durable_proof_without_local_file(self):
        with patch('evolution_automerge.check_pending',return_value=pending()),patch('evolution_automerge._request',side_effect=request_for()):
            result=attempt(order(),None,'token','owner/repo')
        self.assertEqual(result['status'],'promotion_merged')

    def test_local_proof_must_match_durable_proof(self):
        bad=dict(persisted(),commit_sha='c'*40)
        with patch('evolution_automerge.check_pending',return_value=pending()):
            with self.assertRaisesRegex(AutoMergeError,'does not match'): attempt(order(),bad,'token','owner/repo')

    def test_changed_head_is_rejected(self):
        with patch('evolution_automerge.check_pending',return_value=pending()),patch('evolution_automerge._request',side_effect=request_for(head='c'*40)):
            with self.assertRaisesRegex(AutoMergeError,'head changed after approval'): attempt(order(),None,'token','owner/repo')

    def test_spoofed_check_names_are_not_trusted(self):
        spoofed=[check('validate',slug='other-app'),check('mobile-smoke',slug='other-app')]
        with patch('evolution_automerge.check_pending',return_value=pending()),patch('evolution_automerge._request',side_effect=request_for(spoofed)):
            result=attempt(order(),None,'token','owner/repo')
        self.assertEqual(result['status'],'awaiting_required_checks'); self.assertEqual(result['missing_checks'],['mobile-smoke','validate'])

    def test_wrong_actions_repository_is_not_trusted(self):
        wrong=[check('validate',details='https://github.com/attacker/repo/actions/runs/1'),check('mobile-smoke',details='https://github.com/attacker/repo/actions/runs/2')]
        with patch('evolution_automerge.check_pending',return_value=pending()),patch('evolution_automerge._request',side_effect=request_for(wrong)):
            self.assertEqual(attempt(order(),None,'token','owner/repo')['status'],'awaiting_required_checks')

    def test_extra_file_blocks_merge(self):
        with patch('evolution_automerge.check_pending',return_value=pending()),patch('evolution_automerge._request',side_effect=request_for(extra='studio/orchestrator.py')):
            with self.assertRaisesRegex(AutoMergeError,'file scope changed'): attempt(order(),None,'token','owner/repo')

    def test_failed_trusted_check_blocks_merge(self):
        checks=[check('validate'),check('mobile-smoke',conclusion='failure')]
        with patch('evolution_automerge.check_pending',return_value=pending()),patch('evolution_automerge._request',side_effect=request_for(checks)):
            with self.assertRaisesRegex(AutoMergeError,'Required promotion check failed'): attempt(order(),None,'token','owner/repo')

    def test_green_checks_merge_exact_encoded_sha(self):
        calls=[]
        def req(url,token,method='GET',payload=None,allow_404=False):
            calls.append((url,method,payload)); return request_for()(url,token,method,payload,allow_404)
        with patch('evolution_automerge.check_pending',return_value=pending()),patch('evolution_automerge._request',side_effect=req):
            result=attempt(order(),persisted(),'token','owner/repo')
        self.assertEqual(result['status'],'promotion_merged')
        merge=[item for item in calls if item[0].endswith('/pulls/12/merge')][0]
        self.assertEqual(merge[2]['sha'],HEAD)

if __name__=='__main__': unittest.main()

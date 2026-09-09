from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from evolution_automerge import AutoMergeError, attempt
from evolution_candidate import expected_paths

CANDIDATE='future-capability-qa-123456789abc'; GAP='future_capability_qa'; HEAD='b'*40; BRANCH='evolution/promote-future-capability-qa-abcdef123456'

def order(): return {'status':'candidate_planned','candidate_id':CANDIDATE,'primary_gap':{'value':GAP},'baseline_sha':'a'*40}
def persisted(): return {'status':'promotion_persisted','candidate_id':CANDIDATE,'gap':GAP,'branch':BRANCH,'commit_sha':HEAD,'pull_request':12}
def pending(): return {'status':'promotion_pending_merge','candidate_id':CANDIDATE,'gap':GAP,'branch':BRANCH,'commit_sha':HEAD,'pull_request':12}
def files(extra=None):
    names=set(expected_paths(GAP).values())|{'control/promoted_stages.json','control/evolution_rollbacks/'+CANDIDATE+'.json'}
    if extra: names.add(extra)
    return [{'filename':name,'status':'modified' if name=='control/promoted_stages.json' else 'added'} for name in sorted(names)]
def check(name,status='completed',conclusion='success',slug='github-actions',details='https://github.com/owner/repo/actions/runs/123/job/4'):
    return {'name':name,'status':status,'conclusion':conclusion,'app':{'slug':slug},'details_url':details}

class EvolutionAutoMergeTests(unittest.TestCase):
    def test_changed_head_is_rejected_even_when_pending_reports_branch(self):
        def req(url,token,method='GET',payload=None,allow_404=False):
            if url.endswith('/pulls/12'): return {'state':'open','draft':False,'base':{'ref':'main'},'head':{'ref':BRANCH,'sha':'c'*40}}
            raise AssertionError(url)
        with patch('evolution_automerge.check_pending',return_value=pending()),patch('evolution_automerge._request',side_effect=req):
            with self.assertRaisesRegex(AutoMergeError,'head changed after approval'): attempt(order(),persisted(),'token','owner/repo')

    def test_spoofed_check_names_are_not_trusted(self):
        def req(url,token,method='GET',payload=None,allow_404=False):
            if url.endswith('/pulls/12'): return {'state':'open','draft':False,'base':{'ref':'main'},'head':{'ref':BRANCH,'sha':HEAD}}
            if '/pulls/12/files?' in url: return files()
            if '/check-runs?' in url: return {'check_runs':[check('validate',slug='other-app'),check('mobile-smoke',slug='other-app')]}
            raise AssertionError(url)
        with patch('evolution_automerge.check_pending',return_value=pending()),patch('evolution_automerge._request',side_effect=req):
            result=attempt(order(),persisted(),'token','owner/repo')
        self.assertEqual(result['status'],'awaiting_required_checks'); self.assertEqual(result['missing_checks'],['mobile-smoke','validate'])

    def test_wrong_actions_repository_is_not_trusted(self):
        def req(url,token,method='GET',payload=None,allow_404=False):
            if url.endswith('/pulls/12'): return {'state':'open','draft':False,'base':{'ref':'main'},'head':{'ref':BRANCH,'sha':HEAD}}
            if '/pulls/12/files?' in url: return files()
            if '/check-runs?' in url: return {'check_runs':[check('validate',details='https://github.com/attacker/repo/actions/runs/1'),check('mobile-smoke',details='https://github.com/attacker/repo/actions/runs/2')]}
            raise AssertionError(url)
        with patch('evolution_automerge.check_pending',return_value=pending()),patch('evolution_automerge._request',side_effect=req):
            result=attempt(order(),persisted(),'token','owner/repo')
        self.assertEqual(result['status'],'awaiting_required_checks')

    def test_green_trusted_checks_merge_exact_approved_sha(self):
        calls=[]; count={'pr':0}
        def req(url,token,method='GET',payload=None,allow_404=False):
            calls.append((url,method,payload))
            if url.endswith('/pulls/12'):
                count['pr']+=1
                return {'state':'open','draft':False,'mergeable':True,'mergeable_state':'clean','base':{'ref':'main'},'head':{'ref':BRANCH,'sha':HEAD}}
            if '/pulls/12/files?' in url: return files()
            if '/check-runs?' in url: return {'check_runs':[check('validate'),check('mobile-smoke')]}
            if url.endswith('/pulls/12/merge') and method=='PUT': return {'merged':True,'sha':'d'*40}
            raise AssertionError(url)
        with patch('evolution_automerge.check_pending',return_value=pending()),patch('evolution_automerge._request',side_effect=req):
            result=attempt(order(),persisted(),'token','owner/repo')
        self.assertEqual(result['status'],'promotion_merged')
        merge=[item for item in calls if item[0].endswith('/pulls/12/merge')][0]
        self.assertEqual(merge[2]['sha'],HEAD)

    def test_local_persistence_proof_is_required(self):
        with self.assertRaisesRegex(AutoMergeError,'Local persistence proof missing'):
            attempt(order(),{},'token','owner/repo')

if __name__=='__main__': unittest.main()

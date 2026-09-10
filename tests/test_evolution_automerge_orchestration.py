from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from orchestrator import run_registered_stages


class EvolutionAutoMergeOrchestrationTests(unittest.TestCase):
    def test_restarted_runner_merges_pending_promotion_without_regeneration(self):
        report={'completion':{'finished':False,'next_stage':'future_capability_qa'}}
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            with patch('orchestrator.get_stage',return_value=None), \
                 patch('orchestrator._write_adaptation_handoff',return_value={'status':'adaptation_required'}), \
                 patch('orchestrator._run_adaptation_pending',return_value='pending_merge'), \
                 patch('orchestrator._run_adaptation_automerge',return_value='merged') as merge, \
                 patch('orchestrator._run_adaptation_research') as research:
                result=run_registered_stages('request.json',out,tmp,report,100,lambda *a,**k:None,lambda:0,'a'*40)
        self.assertEqual(result['status'],'adaptation_required')
        self.assertEqual(result['pending_status'],'restart_required')
        self.assertEqual(result['automerge_status'],'merged')
        merge.assert_called_once(); research.assert_not_called()

    def test_restarted_runner_waits_without_regenerating_when_checks_are_running(self):
        report={'completion':{'finished':False,'next_stage':'future_capability_qa'}}
        with tempfile.TemporaryDirectory() as tmp:
            with patch('orchestrator.get_stage',return_value=None), \
                 patch('orchestrator._write_adaptation_handoff',return_value={'status':'adaptation_required'}), \
                 patch('orchestrator._run_adaptation_pending',return_value='pending_merge'), \
                 patch('orchestrator._run_adaptation_automerge',return_value='awaiting_checks'), \
                 patch('orchestrator._run_adaptation_research') as research:
                result=run_registered_stages('request.json',Path(tmp),tmp,report,100,lambda *a,**k:None,lambda:0,'a'*40)
        self.assertEqual(result['pending_status'],'pending_merge')
        self.assertEqual(result['automerge_status'],'awaiting_checks')
        research.assert_not_called()

    def test_blocked_pending_proof_fails_closed_without_regeneration(self):
        report={'completion':{'finished':False,'next_stage':'future_capability_qa'}}
        with tempfile.TemporaryDirectory() as tmp:
            with patch('orchestrator.get_stage',return_value=None), \
                 patch('orchestrator._write_adaptation_handoff',return_value={'status':'adaptation_required'}), \
                 patch('orchestrator._run_adaptation_pending',return_value='blocked'), \
                 patch('orchestrator._run_adaptation_research') as research:
                result=run_registered_stages('request.json',Path(tmp),tmp,report,100,lambda *a,**k:None,lambda:0,'a'*40)
        self.assertEqual(result['status'],'adaptation_required')
        self.assertEqual(result['pending_status'],'blocked')
        self.assertEqual(result['automerge_status'],'blocked')
        research.assert_not_called()


if __name__=='__main__': unittest.main()

from pathlib import Path
import json,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))
from evolution_candidate import CandidateRejected,PROTECTED_PATHS,expected_paths,validate_candidate
class EvolutionCandidateTests(unittest.TestCase):
    def work_order(self): return {'status':'candidate_planned','candidate_id':'billing-qa-abc123def456','candidate_branch':'evolution/billing-qa-abc123def456','baseline_sha':'a'*40,'primary_gap':{'kind':'missing_stage_executor','value':'billing_qa','reason':'missing trusted billing QA'}}
    def research(self): return {'status':'research_complete','candidate_id':'billing-qa-abc123def456','items':[]}
    def candidate(self):
        benchmark=json.dumps({'version':1,'id':'billing-qa-core','gap':'billing_qa','purpose':'Prove the new billing QA fails closed without verified purchase evidence.','assertions':['stage requires trusted billing evidence','unavailable Play test environment cannot be reported as success']})
        return {'version':1,'candidate_id':'billing-qa-abc123def456','gap':'billing_qa','files':[{'path':'studio/billing_qa.py','content':'from __future__ import annotations\n\ndef validate_billing(root):\n    return {"passed": False, "blockers": ["play_test_evidence_missing"]}\n'},{'path':'studio/billing_stage.py','content':'from __future__ import annotations\n\ndef main():\n    return 1\n'},{'path':'tests/test_billing_qa.py','content':'import unittest\n\nclass BillingCandidateTests(unittest.TestCase):\n    def test_requires_trusted_evidence(self):\n        self.assertTrue(True)\n\n    def test_unavailable_environment_fails_closed(self):\n        self.assertTrue(True)\n'},{'path':'tests/benchmarks/billing_qa.json','content':benchmark}]}
    def test_accepts_only_complete_scoped_candidate(self):
        result=validate_candidate(self.work_order(),self.research(),self.candidate()); self.assertEqual(result['status'],'candidate_validated'); self.assertEqual(result['benchmark_assertions'],2); self.assertEqual(result['differential_tests'],2); self.assertEqual(set(expected_paths('billing_qa').values()),{f['path'] for f in result['files']})
    def test_completion_registry_smoke_and_evolution_judges_are_protected(self):
        for path in ('studio/completion.py','studio/stage_registry.py','studio/smoke.py','studio/evolution_differential.py','studio/evolution_isolated_runner.py','studio/godot_android_export.py','studio/godot_android_stage.py','studio/godot_device_qa.py','studio/godot_device_stage.py','studio/godot_runtime_journeys.py','studio/godot_runtime_journey_stage.py','studio/godot_visual_qa.py','studio/godot_visual_stage.py','studio/godot_release_qa.py','studio/godot_release_stage.py','studio/engine_entry.py','studio/engine_detect.py','studio/multi_engine_orchestrator.py'): self.assertIn(path,PROTECTED_PATHS)
        candidate=self.candidate(); candidate['files'][0]['path']='studio/completion.py'
        with self.assertRaises(CandidateRejected): validate_candidate(self.work_order(),self.research(),candidate)
    def test_missing_test_or_benchmark_is_rejected(self):
        for path in ('tests/test_billing_qa.py','tests/benchmarks/billing_qa.json'):
            candidate=self.candidate(); candidate['files']=[item for item in candidate['files'] if item['path']!=path]
            with self.assertRaises(CandidateRejected): validate_candidate(self.work_order(),self.research(),candidate)
    def test_test_count_must_match_benchmark_assertions(self):
        candidate=self.candidate(); candidate['files'][2]['content']='import unittest\nclass BillingCandidateTests(unittest.TestCase):\n    def test_only_one(self):\n        self.assertTrue(True)\n'
        with self.assertRaisesRegex(CandidateRejected,'one concrete test per benchmark assertion'): validate_candidate(self.work_order(),self.research(),candidate)
    def test_skipped_tests_are_rejected(self):
        candidate=self.candidate(); candidate['files'][2]['content']='import unittest\nclass BillingCandidateTests(unittest.TestCase):\n    @unittest.skip("no")\n    def test_one(self):\n        pass\n    def test_two(self):\n        pass\n'
        with self.assertRaisesRegex(CandidateRejected,'skipped tests'): validate_candidate(self.work_order(),self.research(),candidate)
    def test_candidate_module_cannot_be_imported_at_collection_time(self):
        candidate=self.candidate(); candidate['files'][2]['content']='import unittest\nfrom billing_qa import validate_billing\nclass BillingCandidateTests(unittest.TestCase):\n    def test_one(self): self.assertTrue(True)\n    def test_two(self): self.assertTrue(True)\n'
        with self.assertRaisesRegex(CandidateRejected,'inside each test'): validate_candidate(self.work_order(),self.research(),candidate)
    def test_shell_true_eval_and_secret_are_rejected(self):
        for bad in ['import subprocess\nsubprocess.run(["echo", "x"], shell=True)\n','value = eval("1 + 1")\n','TOKEN = "ghp_abcdefghijklmnopqrstuvwxyz123456"\n']:
            candidate=self.candidate(); candidate['files'][0]['content']=bad
            with self.assertRaises(CandidateRejected): validate_candidate(self.work_order(),self.research(),candidate)
if __name__=='__main__': unittest.main()
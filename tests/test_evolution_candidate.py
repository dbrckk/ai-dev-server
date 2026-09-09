from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_candidate import CandidateRejected, PROTECTED_PATHS, expected_paths, validate_candidate


class EvolutionCandidateTests(unittest.TestCase):
    def work_order(self):
        return {
            'status': 'candidate_planned',
            'candidate_id': 'billing-qa-abc123def456',
            'candidate_branch': 'evolution/billing-qa-abc123def456',
            'baseline_sha': 'a' * 40,
            'primary_gap': {'kind': 'missing_stage_executor', 'value': 'billing_qa', 'reason': 'missing trusted billing QA'},
        }

    def research(self):
        return {'status': 'research_complete', 'candidate_id': 'billing-qa-abc123def456', 'items': []}

    def candidate(self):
        benchmark = json.dumps({'version': 1, 'id': 'billing-qa-core', 'gap': 'billing_qa', 'purpose': 'Prove the new billing QA fails closed without verified purchase evidence.', 'assertions': ['stage requires trusted billing evidence', 'unavailable Play test environment cannot be reported as success']})
        return {'version': 1, 'candidate_id': 'billing-qa-abc123def456', 'gap': 'billing_qa', 'files': [
            {'path': 'studio/billing_qa.py', 'content': 'from __future__ import annotations\n\ndef validate_billing(root):\n    return {"passed": False, "blockers": ["play_test_evidence_missing"]}\n'},
            {'path': 'studio/billing_stage.py', 'content': 'from __future__ import annotations\n\ndef main():\n    return 1\n'},
            {'path': 'tests/test_billing_qa.py', 'content': 'import unittest\n\nclass BillingCandidateTests(unittest.TestCase):\n    def test_fail_closed(self):\n        self.assertTrue(True)\n'},
            {'path': 'tests/benchmarks/billing_qa.json', 'content': benchmark},
        ]}

    def test_accepts_only_complete_scoped_candidate(self):
        result = validate_candidate(self.work_order(), self.research(), self.candidate())
        self.assertEqual(result['status'], 'candidate_validated')
        self.assertEqual(set(expected_paths('billing_qa').values()), {f['path'] for f in result['files']})

    def test_completion_and_registry_are_protected(self):
        self.assertIn('studio/completion.py', PROTECTED_PATHS)
        self.assertIn('studio/stage_registry.py', PROTECTED_PATHS)
        candidate = self.candidate(); candidate['files'][0]['path'] = 'studio/completion.py'
        with self.assertRaises(CandidateRejected): validate_candidate(self.work_order(), self.research(), candidate)

    def test_missing_test_or_benchmark_is_rejected(self):
        for path in ('tests/test_billing_qa.py', 'tests/benchmarks/billing_qa.json'):
            candidate = self.candidate(); candidate['files'] = [item for item in candidate['files'] if item['path'] != path]
            with self.assertRaises(CandidateRejected): validate_candidate(self.work_order(), self.research(), candidate)

    def test_shell_true_eval_and_secret_are_rejected(self):
        bad_values = ['import subprocess\nsubprocess.run(["echo", "x"], shell=True)\n', 'value = eval("1 + 1")\n', 'TOKEN = "ghp_abcdefghijklmnopqrstuvwxyz123456"\n']
        for bad in bad_values:
            candidate = self.candidate(); candidate['files'][0]['content'] = bad
            with self.assertRaises(CandidateRejected): validate_candidate(self.work_order(), self.research(), candidate)


if __name__ == '__main__': unittest.main()

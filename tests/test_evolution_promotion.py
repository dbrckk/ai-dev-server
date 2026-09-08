from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_promotion import REQUIRED_GATES, decide


class EvolutionPromotionTests(unittest.TestCase):
    def work_order(self):
        return {
            'candidate_id': 'future-capability-qa-deadbeef1234',
            'candidate_branch': 'evolution/future-capability-qa-deadbeef1234',
            'baseline_sha': 'a' * 40,
            'resume_stage': 'future_capability_qa',
            'promotion_gates': sorted(REQUIRED_GATES),
        }

    def research(self):
        return {'status': 'research_complete', 'candidate_id': self.work_order()['candidate_id'], 'items': []}

    def evaluation(self):
        return {
            'version': 1,
            'candidate_id': self.work_order()['candidate_id'],
            'baseline_sha': 'a' * 40,
            'candidate_sha': 'b' * 40,
            'changed_files': [
                {'path': 'studio/future_capability_qa.py', 'status': 'added'},
                {'path': 'studio/future_capability_stage.py', 'status': 'added'},
                {'path': 'studio/stage_registry.py', 'status': 'modified'},
                {'path': 'tests/test_future_capability_qa.py', 'status': 'added'},
            ],
            'tests': {'baseline_passed': 140, 'candidate_passed': 145, 'candidate_failed': 0, 'new_trusted_tests': 5},
            'benchmark': {'baseline_supports_gap': False, 'candidate_supports_gap': True, 'passed': True},
            'gates': {name: True for name in REQUIRED_GATES},
            'security': {'passed': True, 'new_high_findings': 0},
            'registry_change': {'addition_only': True, 'stage_name': 'future_capability_qa'},
        }

    def test_strong_candidate_can_be_promoted(self):
        result = decide(self.work_order(), self.research(), self.evaluation())
        self.assertEqual(result['decision'], 'promote')
        self.assertEqual(result['blockers'], [])

    def test_protected_gate_change_is_rejected(self):
        value = self.evaluation()
        value['changed_files'].append({'path': 'studio/completion.py', 'status': 'modified'})
        result = decide(self.work_order(), self.research(), value)
        self.assertEqual(result['decision'], 'reject')
        self.assertIn('candidate_modifies_protected_factory_gate', result['blockers'])

    def test_test_deletion_or_regression_is_rejected(self):
        value = self.evaluation()
        value['changed_files'].append({'path': 'tests/test_security.py', 'status': 'deleted'})
        value['tests']['candidate_passed'] = 130
        result = decide(self.work_order(), self.research(), value)
        self.assertIn('candidate_deletes_or_renames_files', result['blockers'])
        self.assertIn('candidate_modifies_existing_test', result['blockers'])
        self.assertIn('candidate_regression_detected', result['blockers'])

    def test_missing_capability_improvement_is_rejected(self):
        value = self.evaluation()
        value['benchmark']['candidate_supports_gap'] = False
        result = decide(self.work_order(), self.research(), value)
        self.assertIn('capability_benchmark_not_improved', result['blockers'])

    def test_candidate_must_match_baseline_and_research(self):
        value = self.evaluation()
        value['baseline_sha'] = 'c' * 40
        research = self.research(); research['candidate_id'] = 'other'
        result = decide(self.work_order(), research, value)
        self.assertIn('candidate_baseline_mismatch', result['blockers'])
        self.assertIn('trusted_research_incomplete', result['blockers'])


if __name__ == '__main__':
    unittest.main()

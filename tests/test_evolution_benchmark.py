from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_benchmark import BenchmarkRejected, evaluate


class EvolutionBenchmarkTests(unittest.TestCase):
    def order(self):
        return {'status': 'candidate_planned', 'candidate_id': 'billing-qa-abc123', 'baseline_sha': 'a' * 40, 'primary_gap': {'value': 'billing_qa'}, 'promotion_gates': ['trusted_unit_tests_pass','existing_regression_suite_non_regressing','real_flutter_smoke_passes','security_boundaries_not_weakened','definition_of_done_not_weakened','candidate_is_reversible']}

    def result(self, sha, count=140):
        return {'version': 1, 'commit_sha': sha, 'compile_passed': True, 'unit_tests': {'passed': True, 'count': count, 'failures': 0, 'errors': 0}, 'flutter_smoke_passed': True, 'protected_hashes': {'studio/completion.py': '1' * 64, 'studio/core.py': '2' * 64, '.github/workflows/validate.yml': '3' * 64}, 'capability_benchmark': {'gap': 'billing_qa', 'passed': True, 'assertions_total': 4, 'assertions_passed': 4}, 'reversible': True}

    def test_approves_only_non_regressing_candidate(self):
        decision = evaluate(self.order(), self.result('a' * 40, 140), self.result('b' * 40, 145))
        self.assertEqual(decision['promotion_decision'], 'approve')

    def test_protected_contract_drift_rejects_promotion(self):
        baseline = self.result('a' * 40); candidate = self.result('b' * 40); candidate['protected_hashes']['studio/completion.py'] = '9' * 64
        decision = evaluate(self.order(), baseline, candidate)
        self.assertEqual(decision['promotion_decision'], 'reject')

    def test_losing_existing_tests_is_a_regression(self):
        decision = evaluate(self.order(), self.result('a' * 40, 150), self.result('b' * 40, 149))
        self.assertIn('regression_suite_regressed', decision['blockers'])

    def test_capability_benchmark_is_mandatory(self):
        baseline = self.result('a' * 40); candidate = self.result('b' * 40); candidate['capability_benchmark']['passed'] = False; candidate['capability_benchmark']['assertions_passed'] = 3
        self.assertEqual(evaluate(self.order(), baseline, candidate)['promotion_decision'], 'reject')

    def test_baseline_and_unknown_gate_fail_closed(self):
        with self.assertRaises(BenchmarkRejected): evaluate(self.order(), self.result('c' * 40), self.result('b' * 40))
        order = self.order(); order['promotion_gates'].append('skip_security_for_speed')
        with self.assertRaises(BenchmarkRejected): evaluate(order, self.result('a' * 40), self.result('b' * 40))


if __name__ == '__main__': unittest.main()

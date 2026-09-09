from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_differential import DifferentialRejected, evaluate


class EvolutionDifferentialTests(unittest.TestCase):
    def order(self):
        return {
            'status': 'candidate_planned',
            'candidate_id': 'future-capability-abc123',
            'baseline_sha': 'a' * 40,
        }

    def validated(self):
        return {
            'status': 'candidate_validated',
            'candidate_id': 'future-capability-abc123',
            'files': [
                {'path': 'studio/future_capability_qa.py', 'content': 'pass\n'},
                {'path': 'studio/future_capability_stage.py', 'content': 'pass\n'},
                {'path': 'tests/test_future_capability_qa.py', 'content': 'pass\n'},
                {'path': 'tests/benchmarks/future_capability_qa.json', 'content': '{}'},
            ],
        }

    def result(self, sha, *, failures=0, errors=0, passed=True, count=3):
        return {
            'commit_sha': sha,
            'test_file': 'tests/test_future_capability_qa.py',
            'tests_collected': count,
            'failures': failures,
            'errors': errors,
            'passed': passed,
        }

    def test_requires_red_baseline_and_green_candidate(self):
        baseline = self.result('a' * 40, failures=2, passed=False)
        candidate = self.result('b' * 40)
        proof = evaluate(self.order(), self.validated(), baseline, candidate)
        self.assertEqual(proof['status'], 'differential_proved')
        self.assertTrue(proof['improvement_proved'])
        self.assertEqual(proof['blockers'], [])

    def test_trivial_test_that_already_passes_on_baseline_is_rejected(self):
        proof = evaluate(
            self.order(), self.validated(),
            self.result('a' * 40), self.result('b' * 40),
        )
        self.assertEqual(proof['status'], 'differential_rejected')
        self.assertIn('candidate_test_did_not_fail_on_baseline', proof['blockers'])

    def test_candidate_failure_is_rejected(self):
        proof = evaluate(
            self.order(), self.validated(),
            self.result('a' * 40, failures=1, passed=False),
            self.result('b' * 40, errors=1, passed=False),
        )
        self.assertFalse(proof['improvement_proved'])
        self.assertIn('candidate_test_did_not_pass_on_candidate', proof['blockers'])

    def test_test_collection_must_be_identical(self):
        with self.assertRaisesRegex(DifferentialRejected, 'collection changed'):
            evaluate(
                self.order(), self.validated(),
                self.result('a' * 40, failures=1, passed=False, count=3),
                self.result('b' * 40, count=4),
            )

    def test_evidence_must_match_pinned_baseline_and_candidate_test(self):
        wrong = self.result('c' * 40, failures=1, passed=False)
        with self.assertRaisesRegex(DifferentialRejected, 'pinned SHA'):
            evaluate(self.order(), self.validated(), wrong, self.result('b' * 40))
        mismatch = self.result('a' * 40, failures=1, passed=False)
        mismatch['test_file'] = 'tests/test_other.py'
        with self.assertRaisesRegex(DifferentialRejected, 'test file mismatch'):
            evaluate(self.order(), self.validated(), mismatch, self.result('b' * 40))

    def test_inconsistent_pass_flag_is_rejected(self):
        bad = self.result('a' * 40, failures=1, passed=True)
        with self.assertRaisesRegex(DifferentialRejected, 'inconsistent'):
            evaluate(self.order(), self.validated(), bad, self.result('b' * 40))


if __name__ == '__main__':
    unittest.main()

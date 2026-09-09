from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from adaptation import PROMOTION_GATES
from evolution_benchmark import evaluate as evaluate_promotion
from evolution_differential import DifferentialRejected, evaluate


class EvolutionDifferentialTests(unittest.TestCase):
    def order(self):
        return {'status':'candidate_planned','candidate_id':'future-capability-abc123','baseline_sha':'a'*40,
                'primary_gap':{'value':'future_capability_qa'},'promotion_gates':list(PROMOTION_GATES)}
    def validated(self):
        return {'status':'candidate_validated','candidate_id':'future-capability-abc123','files':[
            {'path':'studio/future_capability_qa.py','content':'pass\n'},
            {'path':'studio/future_capability_stage.py','content':'pass\n'},
            {'path':'tests/test_future_capability_qa.py','content':'pass\n'},
            {'path':'tests/benchmarks/future_capability_qa.json','content':'{}'}]}
    def diff_result(self, sha, failures=0, errors=0, passed=True):
        return {'commit_sha':sha,'test_file':'tests/test_future_capability_qa.py','tests_collected':3,
                'failures':failures,'errors':errors,'passed':passed}
    def benchmark_result(self, sha):
        return {'version':1,'commit_sha':sha,'compile_passed':True,
                'unit_tests':{'passed':True,'count':170,'failures':0,'errors':0},'flutter_smoke_passed':True,
                'protected_hashes':{'studio/core.py':'1'*64,'studio/completion.py':'2'*64},
                'capability_benchmark':{'gap':'future_capability_qa','passed':True,'assertions_total':3,'assertions_passed':3},
                'reversible':True}
    def test_promotion_contract_requires_differential_improvement(self):
        self.assertIn('differential_improvement_proved', PROMOTION_GATES)
        proof = evaluate(self.order(), self.validated(), self.diff_result('a'*40, failures=2, passed=False), self.diff_result('b'*40))
        decision = evaluate_promotion(self.order(), self.benchmark_result('a'*40), self.benchmark_result('b'*40), proof)
        self.assertEqual(decision['promotion_decision'], 'approve')
        self.assertTrue(decision['gates']['differential_improvement_proved'])
    def test_trivial_baseline_green_test_blocks_promotion(self):
        proof = evaluate(self.order(), self.validated(), self.diff_result('a'*40), self.diff_result('b'*40))
        decision = evaluate_promotion(self.order(), self.benchmark_result('a'*40), self.benchmark_result('b'*40), proof)
        self.assertEqual(decision['promotion_decision'], 'reject')
        self.assertIn('differential_improvement_not_proved', decision['blockers'])
    def test_missing_differential_proof_blocks_promotion(self):
        decision = evaluate_promotion(self.order(), self.benchmark_result('a'*40), self.benchmark_result('b'*40))
        self.assertEqual(decision['promotion_decision'], 'reject')
        self.assertFalse(decision['gates']['differential_improvement_proved'])
    def test_pinned_baseline_is_required(self):
        with self.assertRaisesRegex(DifferentialRejected, 'pinned SHA'):
            evaluate(self.order(), self.validated(), self.diff_result('c'*40, failures=1, passed=False), self.diff_result('b'*40))


if __name__ == '__main__':
    unittest.main()

import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from architecture_replacement_promotion import ReplacementPromotionError, review, write

class ReplacementPromotionTests(unittest.TestCase):
    def order(self):
        return {
            "id":"replace-1",
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "required_gates":["dependency_policy_approved","rollback_path_verified"],
        }

    def candidate(self):
        return {
            "status":"replacement_candidate_validated",
            "work_order_id":"replace-1",
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "baseline_sha":"0"*40,
            "files":[{"path":"lib/a.dart","content":"void main() {}\n"}],
        }

    def execution(self):
        return {
            "status":"replacement_isolated_benchmark_complete",
            "work_order_id":"replace-1",
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "baseline_sha":"0"*40,
            "candidate_sha":"1"*40,
            "go_no_go":"GO_FOR_MANUAL_PROMOTION_REVIEW",
            "network":"disabled",
            "credentials_exposed_to_candidate":False,
            "default_branch_modified":False,
            "reversible":True,
            "baseline_validation":{"passed":True},
            "candidate_validation":{"passed":True},
            "changed_files":["lib/a.dart"],
        }

    def test_clean_evidence_is_review_ready(self):
        result=review(self.order(),self.candidate(),self.execution())
        self.assertEqual(result["decision"],"READY_FOR_EXPLICIT_PROMOTION_ACTION")
        self.assertFalse(result["policy"]["auto_push"])
        self.assertFalse(result["policy"]["auto_merge"])
        self.assertEqual(result["changed_files"],["lib/a.dart"])

    def test_network_not_disabled_is_blocked(self):
        execution=self.execution()
        execution["network"]="enabled"
        with self.assertRaises(ReplacementPromotionError):
            review(self.order(),self.candidate(),execution)

    def test_candidate_validation_failure_is_blocked(self):
        execution=self.execution()
        execution["candidate_validation"]={"passed":False}
        with self.assertRaises(ReplacementPromotionError):
            review(self.order(),self.candidate(),execution)

    def test_identity_mismatch_is_blocked(self):
        candidate=self.candidate()
        candidate["replacement_repo"]="other/repo"
        with self.assertRaises(ReplacementPromotionError):
            review(self.order(),candidate,self.execution())

    def test_write_persists_review_package(self):
        with tempfile.TemporaryDirectory() as td:
            result=write(self.order(),self.candidate(),self.execution(),Path(td))
            self.assertTrue((Path(td)/"architecture-replacement-promotion-review.json").is_file())
            self.assertEqual(result["status"],"promotion_review_ready")

if __name__=="__main__":
    unittest.main()

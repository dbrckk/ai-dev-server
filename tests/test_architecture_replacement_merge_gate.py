import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from architecture_replacement_merge_gate import ReplacementMergeGateError, build, write

class ReplacementMergeGateTests(unittest.TestCase):
    def inputs(self):
        validation={
            "status":"ready_to_merge",
            "ready_to_merge":True,
            "draft":False,
            "mergeable_clean":True,
            "pull_request":7,
            "branch":"architecture/replacement-abc",
            "head_sha":"1"*40,
        }
        review={
            "status":"promotion_review_ready",
            "work_order_id":"replace-1",
            "candidate_digest":"2"*64,
        }
        package={
            "status":"pr_package_ready",
            "work_order_id":"replace-1",
            "branch":"architecture/replacement-abc",
        }
        persisted={
            "status":"replacement_pr_created",
            "work_order_id":"replace-1",
            "pull_request":7,
            "branch":"architecture/replacement-abc",
            "commit_sha":"1"*40,
        }
        return validation,review,package,persisted

    def test_gate_requires_explicit_authorization(self):
        result=build(*self.inputs())
        self.assertEqual(result["status"],"merge_authorization_required")
        self.assertFalse(result["authorization_template"]["authorized"])
        self.assertFalse(result["policy"]["auto_merge"])
        self.assertFalse(result["policy"]["network_write"])

    def test_head_mismatch_is_blocked(self):
        validation,review,package,persisted=self.inputs()
        persisted["commit_sha"]="3"*40
        with self.assertRaises(ReplacementMergeGateError):
            build(validation,review,package,persisted)

    def test_not_ready_pr_is_blocked(self):
        validation,review,package,persisted=self.inputs()
        validation["status"]="validated_draft"
        validation["ready_to_merge"]=False
        with self.assertRaises(ReplacementMergeGateError):
            build(validation,review,package,persisted)

    def test_write_persists_gate(self):
        with tempfile.TemporaryDirectory() as td:
            result=write(*self.inputs(),Path(td))
            self.assertTrue((Path(td)/"architecture-replacement-merge-gate.json").is_file())
            self.assertEqual(len(result["authorization_id"]),64)

if __name__=="__main__":
    unittest.main()

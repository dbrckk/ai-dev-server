import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
from architecture_replacement_rollback_gate import ReplacementRollbackGateError, build

class ReplacementRollbackGateTests(unittest.TestCase):
    def fixtures(self):
        return (
            {"status":"post_merge_regression","rollback_required":True,"work_order_id":"r1","failed_checks":["validate"],"content_mismatches":[]},
            {"status":"replacement_merged","work_order_id":"r1","pull_request":7,"merge_sha":"3"*40,"head_sha":"1"*40},
            {"status":"pr_package_ready","work_order_id":"r1","baseline_sha":"0"*40},
        )
    def test_regression_creates_explicit_gate(self):
        result=build(*self.fixtures())
        self.assertEqual(result["status"],"rollback_authorization_required")
        self.assertFalse(result["authorization_template"]["authorized"])
        self.assertFalse(result["policy"]["automatic_rollback"])
    def test_healthy_state_cannot_create_rollback_gate(self):
        p,m,k=self.fixtures()
        p["status"]="post_merge_healthy"; p["rollback_required"]=False
        with self.assertRaises(ReplacementRollbackGateError):
            build(p,m,k)

if __name__=="__main__":
    unittest.main()

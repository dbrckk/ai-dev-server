import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
from architecture_replacement_outcome import build

class ReplacementOutcomeTests(unittest.TestCase):
    def fixtures(self):
        work={"id":"r1","current_repo":"a/current","replacement_repo":"a/better","risk":"low","scope":"narrow"}
        merged={"status":"replacement_merged","work_order_id":"r1","merge_sha":"3"*40}
        return work,merged
    def test_healthy_merge_is_success(self):
        work,merged=self.fixtures()
        result=build(work,merged,{"status":"post_merge_healthy","work_order_id":"r1","post_merge_healthy":True})
        self.assertTrue(result["successful"]); self.assertEqual(result["quality_score"],100.0)
    def test_regression_is_failure(self):
        work,merged=self.fixtures()
        result=build(work,merged,{"status":"post_merge_regression","work_order_id":"r1","rollback_required":True,"failed_checks":["validate"]})
        self.assertFalse(result["successful"]); self.assertTrue(result["regressed"]); self.assertLess(result["quality_score"],50.0)

if __name__=="__main__": unittest.main()

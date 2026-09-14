import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from architecture_replacement_work_order import build, write

class ReplacementWorkOrderTests(unittest.TestCase):
    def plan(self):
        return {"replacement_plans":[{
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "risk":"medium",
            "estimated_change_scope":"moderate",
            "framework":"flutter",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
            "current_major_version":1,
            "replacement_major_version":2,
            "required_gates":["dependency_policy_approved","rollback_path_verified"],
        }]}

    def test_build_is_fail_closed(self):
        result=build(self.plan())
        self.assertEqual(len(result["work_orders"]),1)
        order=result["work_orders"][0]
        self.assertEqual(order["go_no_go"],"NO_GO_PENDING_EXECUTION")
        self.assertTrue(order["isolation"]["required"])
        self.assertFalse(order["isolation"]["external_source_execution"])
        self.assertFalse(result["policy"]["execute_automatically"])

    def test_context_is_carried_into_work_order(self):
        order=build(self.plan())["work_orders"][0]
        self.assertEqual(order["framework"],"flutter")
        self.assertEqual(order["project_type"],"game")
        self.assertEqual(order["platform"],"android")
        self.assertEqual(order["current_major_version"],1)
        self.assertEqual(order["replacement_major_version"],2)

    def test_id_is_deterministic(self):
        first=build(self.plan())["work_orders"][0]["id"]
        second=build(self.plan())["work_orders"][0]["id"]
        self.assertEqual(first,second)

    def test_write_persists(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            result=write(self.plan(),out)
            saved=json.loads((out/"architecture-replacement-work-orders.json").read_text())
            self.assertEqual(saved,result)

if __name__=="__main__":
    unittest.main()

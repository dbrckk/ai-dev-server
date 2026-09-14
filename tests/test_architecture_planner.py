import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from architecture_planner import plan, write

class ArchitecturePlannerTests(unittest.TestCase):
    def test_selects_ranked_candidates_without_authorizing_dependencies(self):
        recs={"matches":[
            {"repo":"a/core","score":92.0,"quality_score":9.8,"tier":"core","domain":"software_engineering","capabilities":["testing"],"best_for":["qa"],"alternatives":["a/alt"]},
            {"repo":"b/reject","tier":"recommended","capabilities":["ui"],"avoid_when":["native-only"]},
        ]}
        result=plan({"target_repo":"o/r","app_name":"demo"},recs)
        self.assertEqual(result["status"],"planned")
        self.assertFalse(result["dependency_policy"]["allow_automatic_dependency_addition"])
        self.assertEqual(result["chosen"][0]["repo"],"a/core")
        self.assertEqual(result["chosen"][0]["selection_score"],92.0)
        self.assertEqual(result["chosen"][0]["quality_score"],9.8)
        self.assertEqual(result["rejected"][0]["repo"],"b/reject")
        self.assertEqual(result["fallbacks"][0]["alternatives"],["a/alt"])

    def test_write_persists_machine_readable_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            result=write({"target_repo":"o/r","app_name":"demo"},{"matches":[]},out)
            saved=json.loads((out/"architecture-decision.json").read_text())
            self.assertEqual(saved,result)
            self.assertTrue(saved["advisory_only"])


    def test_learning_below_threshold_does_not_change_selection_score(self):
        recs={"matches":[
            {"repo":"a/core","score":90.0,"quality_score":9.0,"tier":"core","capabilities":["testing"]},
        ]}
        learning={"rankings":[{"repo":"a/core","samples":4,"success_rate":1.0}]}
        result=plan({"target_repo":"o/r","app_name":"demo"},recs,learning=learning)
        self.assertFalse(result["feedback_applied"])
        self.assertEqual(result["chosen"][0]["selection_score"],90.0)
        self.assertEqual(result["chosen"][0]["base_selection_score"],90.0)

    def test_verified_history_can_reorder_with_small_bounded_bonus(self):
        recs={"matches":[
            {"repo":"a/core","score":90.0,"quality_score":9.0,"tier":"core","capabilities":["testing"]},
            {"repo":"b/other","score":91.0,"quality_score":8.0,"tier":"core","capabilities":["ui"]},
        ]}
        learning={"rankings":[
            {"repo":"a/core","samples":8,"success_rate":1.0,"mean_model_calls":2.0,"mean_cycles":1.0,"mean_blockers":0.0}
        ]}
        result=plan({"target_repo":"o/r","app_name":"demo"},recs,learning=learning)
        self.assertTrue(result["feedback_applied"])
        self.assertEqual(result["chosen"][0]["repo"],"a/core")
        self.assertEqual(result["chosen"][0]["selection_score"],93.0)
        self.assertEqual(result["chosen"][0]["historical_evidence"]["samples"],8)


if __name__=="__main__":
    unittest.main()

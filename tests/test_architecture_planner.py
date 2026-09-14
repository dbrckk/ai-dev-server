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
            {"repo":"a/core","score":90.0,"quality_score":9.0,"tier":"core","domain":"software_engineering","capabilities":["testing"]},
            {"repo":"b/other","score":91.0,"quality_score":8.0,"tier":"core","domain":"software_engineering","capabilities":["ui"]},
        ]}
        learning={"rankings":[
            {"repo":"a/core","domain":"software_engineering","framework":"flutter","project_type":"general","primary_domain":"software_engineering","samples":8,"success_rate":1.0,"mean_model_calls":2.0,"mean_cycles":1.0,"mean_blockers":0.0}
        ]}
        result=plan({"target_repo":"o/r","app_name":"demo"},recs,learning=learning)
        self.assertTrue(result["feedback_applied"])
        self.assertEqual(result["chosen"][0]["repo"],"a/core")
        self.assertEqual(result["chosen"][0]["selection_score"],93.0)
        self.assertEqual(result["chosen"][0]["historical_evidence"]["samples"],8)

    def test_verified_stack_history_can_break_close_tie(self):
        recs={"matches":[
            {"repo":"a/base","score":95.0,"quality_score":9.5,"tier":"core","domain":"mobile","capabilities":["mobile"]},
            {"repo":"b/plain","score":91.0,"quality_score":9.0,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
            {"repo":"c/synergy","score":90.0,"quality_score":9.0,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
        ]}
        learning={"stack_rankings":[
            {"repos":["a/base","c/synergy"],"framework":"flutter","project_type":"general","primary_domain":"mobile","samples":8,"success_rate":1.0}
        ]}
        result=plan({"target_repo":"o/r","app_name":"demo"},recs,learning=learning)
        self.assertEqual(result["chosen"][0]["repo"],"a/base")
        self.assertEqual(result["chosen"][1]["repo"],"c/synergy")
        self.assertEqual(result["chosen"][1]["stack_synergy_bonus"],2.0)
        self.assertTrue(result["chosen"][1]["stack_historical_evidence"])

    def test_stack_history_below_threshold_is_ignored(self):
        recs={"matches":[
            {"repo":"a/base","score":95.0,"quality_score":9.5,"tier":"core","domain":"mobile","capabilities":["mobile"]},
            {"repo":"b/plain","score":91.0,"quality_score":9.0,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
            {"repo":"c/synergy","score":90.0,"quality_score":9.0,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
        ]}
        learning={"stack_rankings":[
            {"repos":["a/base","c/synergy"],"framework":"flutter","project_type":"general","primary_domain":"mobile","samples":4,"success_rate":1.0}
        ]}
        result=plan({"target_repo":"o/r","app_name":"demo"},recs,learning=learning)
        self.assertEqual(result["chosen"][1]["repo"],"b/plain")
        self.assertEqual(result["chosen"][1]["stack_synergy_bonus"],0.0)

    def test_negative_stack_history_can_demote_combination(self):
        recs={"matches":[
            {"repo":"a/base","score":95.0,"quality_score":9.5,"tier":"core","domain":"mobile","capabilities":["mobile"]},
            {"repo":"b/risky","score":91.0,"quality_score":9.0,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
            {"repo":"c/stable","score":90.5,"quality_score":9.0,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
        ]}
        learning={"stack_rankings":[
            {"repos":["a/base","b/risky"],"framework":"flutter","project_type":"general","primary_domain":"mobile","samples":8,"success_rate":0.0}
        ]}
        result=plan({"target_repo":"o/r","app_name":"demo"},recs,learning=learning)
        self.assertEqual(result["chosen"][1]["repo"],"c/stable")
    def test_stack_history_does_not_cross_project_type(self):
        recs={"matches":[
            {"repo":"a/base","score":95.0,"quality_score":9.5,"tier":"core","domain":"mobile","capabilities":["mobile"]},
            {"repo":"b/plain","score":91.0,"quality_score":9.0,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
            {"repo":"c/game","score":90.0,"quality_score":9.0,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
        ]}
        learning={"stack_rankings":[
            {
                "repos":["a/base","c/game"],
                "framework":"flutter",
                "project_type":"game",
                "primary_domain":"mobile",
                "samples":8,
                "success_rate":1.0,
            }
        ]}
        result=plan(
            {"target_repo":"o/r","app_name":"demo","brief":"Trading dashboard for XAUUSD"},
            recs,
            learning=learning,
            framework="flutter",
        )
        self.assertEqual(result["constraints"]["project_type"],"trading")
        self.assertEqual(result["chosen"][1]["repo"],"b/plain")
        self.assertEqual(result["chosen"][1]["stack_synergy_bonus"],0.0)

    def test_matching_project_type_can_apply_stack_history(self):
        recs={"matches":[
            {"repo":"a/base","score":95.0,"quality_score":9.5,"tier":"core","domain":"mobile","capabilities":["mobile"]},
            {"repo":"b/plain","score":91.0,"quality_score":9.0,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
            {"repo":"c/game","score":90.0,"quality_score":9.0,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
        ]}
        learning={"stack_rankings":[
            {
                "repos":["a/base","c/game"],
                "framework":"flutter",
                "project_type":"game",
                "primary_domain":"mobile",
                "samples":8,
                "success_rate":1.0,
            }
        ]}
        result=plan(
            {"target_repo":"o/r","app_name":"demo","brief":"A multiplayer game for Android"},
            recs,
            learning=learning,
            framework="flutter",
        )
        self.assertEqual(result["constraints"]["project_type"],"game")
        self.assertEqual(result["chosen"][1]["repo"],"c/game")
        self.assertEqual(result["chosen"][1]["stack_synergy_bonus"],2.0)

    def test_primary_domain_is_recorded_in_constraints(self):
        recs={"matches":[
            {"repo":"a/one","score":95.0,"quality_score":9.5,"tier":"core","domain":"graphics","capabilities":["rendering"]},
            {"repo":"b/two","score":94.0,"quality_score":9.4,"tier":"recommended","domain":"graphics","capabilities":["animation"]},
            {"repo":"c/three","score":90.0,"quality_score":9.0,"tier":"recommended","domain":"mobile","capabilities":["mobile"]},
        ]}
        result=plan({"target_repo":"o/r","app_name":"demo","brief":"Vector animation app"},recs)
        self.assertEqual(result["constraints"]["primary_domain"],"graphics")

    def test_selection_margin_exposes_near_tie_confidence(self):
        recs={"matches":[
            {"repo":"a/first","score":90.4,"quality_score":9.0,"tier":"core","domain":"mobile","capabilities":["ui"]},
            {"repo":"b/second","score":90.0,"quality_score":8.9,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
        ]}
        result=plan({"target_repo":"o/r","app_name":"demo"},recs)
        self.assertEqual(result["version"],4)
        self.assertEqual(result["chosen"][0]["repo"],"a/first")
        self.assertEqual(result["chosen"][0]["selection_margin"],0.4)
        self.assertEqual(result["chosen"][0]["selection_confidence"],"low")
        self.assertTrue(result["stack_feedback_policy"]["selection_margin_confidence"])

    def test_selection_margin_marks_clear_winner_high_confidence(self):
        recs={"matches":[
            {"repo":"a/first","score":95.0,"quality_score":9.5,"tier":"core","domain":"mobile","capabilities":["ui"]},
            {"repo":"b/second","score":90.0,"quality_score":8.9,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
        ]}
        result=plan({"target_repo":"o/r","app_name":"demo"},recs)
        self.assertEqual(result["chosen"][0]["selection_margin"],5.0)
        self.assertEqual(result["chosen"][0]["selection_confidence"],"high")


    def test_low_confidence_requires_independent_architecture_review(self):
        recs={"matches":[
            {"repo":"a/first","score":90.4,"quality_score":9.0,"tier":"core","domain":"mobile","capabilities":["ui"]},
            {"repo":"b/second","score":90.0,"quality_score":8.9,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
            {"repo":"c/third","score":89.8,"quality_score":8.8,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
            {"repo":"d/fourth","score":89.6,"quality_score":8.7,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
            {"repo":"e/fifth","score":89.4,"quality_score":8.6,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
            {"repo":"f/sixth","score":89.2,"quality_score":8.5,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
            {"repo":"g/fallback","score":89.0,"quality_score":8.4,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
        ]}
        result=plan({"target_repo":"o/r","app_name":"demo"},recs)
        policy=result["autonomy_policy"]
        self.assertEqual(policy["decision_confidence"],"low")
        self.assertTrue(policy["validation_required"])
        self.assertEqual(policy["validation_mode"],"independent_review")
        self.assertFalse(policy["allow_architecture_changes_without_review"])
        self.assertTrue(policy["normal_code_changes_may_continue"])
        self.assertEqual(policy["scope"],"architecture_changes_only")
        self.assertLessEqual(len(policy["retained_fallback_repos"]),3)

    def test_clear_architecture_choice_allows_normal_autonomous_flow(self):
        recs={"matches":[
            {"repo":"a/first","score":95.0,"quality_score":9.5,"tier":"core","domain":"mobile","capabilities":["ui"]},
            {"repo":"b/second","score":90.0,"quality_score":8.9,"tier":"recommended","domain":"mobile","capabilities":["ui"]},
        ]}
        result=plan({"target_repo":"o/r","app_name":"demo"},recs)
        policy=result["autonomy_policy"]
        self.assertEqual(policy["decision_confidence"],"high")
        self.assertFalse(policy["validation_required"])
        self.assertEqual(policy["validation_mode"],"standard")
        self.assertTrue(policy["allow_architecture_changes_without_review"])


if __name__=="__main__":
    unittest.main()

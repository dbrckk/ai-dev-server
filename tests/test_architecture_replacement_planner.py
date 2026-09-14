import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from architecture_replacement_planner import plan, write

class ArchitectureReplacementPlannerTests(unittest.TestCase):
    def obsolescence(self):
        return {"deprecation_candidates":[{
            "repo":"a/current",
            "replacement_candidate":"a/better",
            "benchmark_delta":16.0,
            "drift_score":0.9,
            "maintenance_signal":"stale",
            "maintenance_evidence_available":True,
        }]}

    def recommendations(self):
        return {"matches":[
            {
                "repo":"a/current",
                "capabilities":["testing","browser"],
                "languages":["python"],
                "platforms":["linux"],
                "runtime":["local"],
                "integrationComplexity":"medium",
                "resourceLevel":"medium",
            },
            {
                "repo":"a/better",
                "capabilities":["testing","browser","observability"],
                "languages":["python"],
                "platforms":["linux"],
                "runtime":["local"],
                "integrationComplexity":"low",
                "resourceLevel":"low",
            },
        ]}

    def test_low_risk_when_capabilities_are_preserved(self):
        result=plan(self.obsolescence(),self.recommendations())
        row=result["replacement_plans"][0]
        self.assertEqual(row["risk"],"low")
        self.assertEqual(row["estimated_change_scope"],"narrow")
        self.assertEqual(row["impact"]["capabilities_missing"],[])
        self.assertIn("observability",row["impact"]["capabilities_added"])
        self.assertEqual(row["go_no_go"],"NO_GO_PENDING_ISOLATED_BENCHMARK")
        self.assertFalse(result["policy"]["auto_apply_migration"])

    def test_missing_capability_is_high_risk(self):
        recs=self.recommendations()
        recs["matches"][1]["capabilities"]=["testing"]
        result=plan(self.obsolescence(),recs)
        row=result["replacement_plans"][0]
        self.assertEqual(row["risk"],"high")
        self.assertIn("browser",row["impact"]["capabilities_missing"])
        self.assertIn("missing_capabilities_resolved",row["required_gates"])

    def test_missing_maintenance_requires_gate(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0]["maintenance_evidence_available"]=False
        result=plan(obs,self.recommendations())
        self.assertIn("maintenance_evidence_completed",result["replacement_plans"][0]["required_gates"])

    def test_bad_historical_replacement_raises_risk(self):
        learning={"rankings":[{
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "samples":10,
            "eligible_for_bias":True,
            "evidence_confidence":0.5,
            "regression_rate":0.4,
            "wilson_lower_95":0.35,
        }]}
        result=plan(self.obsolescence(),self.recommendations(),learning=learning)
        row=result["replacement_plans"][0]
        self.assertEqual(row["risk"],"high")
        self.assertEqual(row["empirical_status"],"historically_risky")
        self.assertIn("historical_replacement_risk_reviewed",row["required_gates"])
        self.assertLess(row["empirical_priority_adjustment"],0.0)

    def test_strong_historical_replacement_is_recorded_but_does_not_skip_gates(self):
        learning={"rankings":[{
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "samples":20,
            "eligible_for_bias":True,
            "evidence_confidence":1.0,
            "regression_rate":0.0,
            "wilson_lower_95":0.82,
        }]}
        result=plan(self.obsolescence(),self.recommendations(),learning=learning)
        row=result["replacement_plans"][0]
        self.assertEqual(row["empirical_status"],"historically_supported")
        self.assertGreater(row["priority_score"],row["benchmark_delta"])
        self.assertIn("dependency_policy_approved",row["required_gates"])
        self.assertEqual(row["go_no_go"],"NO_GO_PENDING_ISOLATED_BENCHMARK")

    def test_historical_evidence_does_not_cross_framework_context(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0].update({
            "framework":"flutter",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
            "current_major_version":1,
            "replacement_major_version":2,
        })
        learning={"rankings":[
            {
                "current_repo":"a/current",
                "replacement_repo":"a/better",
                "framework":"python",
                "project_type":"trading",
                "primary_domain":"backend",
                "platform":"linux",
                "current_major_version":1,
                "replacement_major_version":2,
                "samples":20,
                "eligible_for_bias":True,
                "evidence_confidence":1.0,
                "regression_rate":0.5,
                "wilson_lower_95":0.2,
            }
        ]}
        result=plan(obs,self.recommendations(),learning=learning)
        row=result["replacement_plans"][0]
        self.assertEqual(row["empirical_status"],"unobserved")
        self.assertEqual(row["risk"],"low")

    def test_matching_context_can_apply_history(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0].update({
            "framework":"flutter",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
            "current_major_version":1,
            "replacement_major_version":2,
        })
        learning={"rankings":[
            {
                "current_repo":"a/current",
                "replacement_repo":"a/better",
                "framework":"flutter",
                "project_type":"game",
                "primary_domain":"mobile",
                "platform":"android",
                "current_major_version":1,
                "replacement_major_version":2,
                "samples":20,
                "eligible_for_bias":True,
                "evidence_confidence":1.0,
                "regression_rate":0.0,
                "wilson_lower_95":0.85,
            }
        ]}
        result=plan(obs,self.recommendations(),learning=learning)
        row=result["replacement_plans"][0]
        self.assertEqual(row["empirical_status"],"historically_supported")
        self.assertEqual(row["historical_replacement_evidence"]["framework"],"flutter")
        self.assertEqual(row["platform"],"android")

    def test_generic_history_is_downweighted_for_specific_context(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0].update({
            "framework":"flutter",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
        })
        learning={"rankings":[{
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "samples":20,
            "eligible_for_bias":True,
            "evidence_confidence":1.0,
            "regression_rate":0.5,
            "wilson_lower_95":0.2,
        }]}
        result=plan(obs,self.recommendations(),learning=learning)
        row=result["replacement_plans"][0]
        self.assertEqual(row["empirical_status"],"mixed_history")
        self.assertLess(row["history_context_weight"],0.75)
        self.assertEqual(row["risk"],"low")

    def test_nearby_major_versions_are_partially_transferable(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0].update({
            "framework":"flutter",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
            "current_major_version":2,
            "replacement_major_version":4,
        })
        learning={"rankings":[{
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "framework":"flutter",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
            "current_major_version":1,
            "replacement_major_version":3,
            "samples":20,
            "eligible_for_bias":True,
            "evidence_confidence":1.0,
            "regression_rate":0.0,
            "wilson_lower_95":0.85,
        }]}
        row=plan(obs,self.recommendations(),learning=learning)["replacement_plans"][0]
        self.assertGreater(row["compatibility_distance"]["transferability"],0.75)
        self.assertLess(row["compatibility_distance"]["transferability"],1.0)
        self.assertFalse(row["compatibility_distance"]["exact_context_match"])
        self.assertEqual(row["empirical_status"],"historically_supported")

    def test_large_version_distance_is_strongly_downweighted(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0].update({
            "framework":"flutter",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
            "current_major_version":7,
            "replacement_major_version":11,
        })
        learning={"rankings":[{
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "framework":"flutter",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
            "current_major_version":1,
            "replacement_major_version":2,
            "samples":30,
            "eligible_for_bias":True,
            "evidence_confidence":1.0,
            "regression_rate":0.0,
            "wilson_lower_95":0.9,
        }]}
        row=plan(obs,self.recommendations(),learning=learning)["replacement_plans"][0]
        self.assertLess(row["compatibility_distance"]["transferability"],0.85)
        self.assertGreater(row["compatibility_distance"]["distance"],0.15)
        self.assertLess(row["empirical_priority_adjustment"],5.0)

    def test_closest_history_is_selected_instead_of_largest_sample(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0].update({
            "framework":"flutter",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
            "current_major_version":3,
            "replacement_major_version":4,
        })
        learning={"rankings":[
            {
                "current_repo":"a/current",
                "replacement_repo":"a/better",
                "framework":"flutter",
                "project_type":"game",
                "primary_domain":"mobile",
                "platform":"android",
                "current_major_version":3,
                "replacement_major_version":4,
                "samples":5,
                "eligible_for_bias":True,
                "evidence_confidence":0.25,
                "regression_rate":0.0,
                "wilson_lower_95":0.56,
            },
            {
                "current_repo":"a/current",
                "replacement_repo":"a/better",
                "framework":"python",
                "project_type":"trading",
                "primary_domain":"backend",
                "platform":"linux",
                "current_major_version":3,
                "replacement_major_version":4,
                "samples":100,
                "eligible_for_bias":True,
                "evidence_confidence":1.0,
                "regression_rate":0.0,
                "wilson_lower_95":0.95,
            },
        ]}
        row=plan(obs,self.recommendations(),learning=learning)["replacement_plans"][0]
        self.assertEqual(row["historical_replacement_evidence"]["framework"],"flutter")
        self.assertTrue(row["compatibility_distance"]["exact_context_match"])

    def test_framework_mismatch_caps_transferability(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0].update({
            "framework":"flutter",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
            "current_major_version":3,
            "replacement_major_version":4,
        })
        learning={"rankings":[{
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "framework":"python",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
            "current_major_version":3,
            "replacement_major_version":4,
            "samples":50,
            "eligible_for_bias":True,
            "evidence_confidence":1.0,
            "regression_rate":0.0,
            "wilson_lower_95":0.95,
        }]}
        row=plan(obs,self.recommendations(),learning=learning)["replacement_plans"][0]
        self.assertLessEqual(row["compatibility_distance"]["transferability"],0.35)
        self.assertEqual(row["empirical_status"],"mixed_history")

    def test_version_jump_similarity_handles_downgrades(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0].update({
            "framework":"flutter",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
            "current_major_version":5,
            "replacement_major_version":4,
        })
        learning={"rankings":[{
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "framework":"flutter",
            "project_type":"game",
            "primary_domain":"mobile",
            "platform":"android",
            "current_major_version":4,
            "replacement_major_version":3,
            "samples":20,
            "eligible_for_bias":True,
            "evidence_confidence":1.0,
            "regression_rate":0.0,
            "wilson_lower_95":0.85,
        }]}
        row=plan(obs,self.recommendations(),learning=learning)["replacement_plans"][0]
        self.assertEqual(row["compatibility_distance"]["components"]["version_jump"],1.0)
        self.assertGreater(row["compatibility_distance"]["transferability"],0.8)

    def test_multiple_nearby_histories_are_fused(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0].update({
            "framework":"flutter","project_type":"game","primary_domain":"mobile",
            "platform":"android","current_major_version":3,"replacement_major_version":4,
        })
        learning={"rankings":[
            {
                "current_repo":"a/current","replacement_repo":"a/better",
                "framework":"flutter","project_type":"game","primary_domain":"mobile","platform":"android",
                "current_major_version":3,"replacement_major_version":4,
                "samples":10,"eligible_for_bias":True,"evidence_confidence":0.5,
                "success_rate":1.0,"posterior_success_rate":0.92,"regression_rate":0.0,
                "rollback_rate":0.0,"wilson_lower_95":0.72,"mean_quality_score":95.0,
            },
            {
                "current_repo":"a/current","replacement_repo":"a/better",
                "framework":"flutter","project_type":"game","primary_domain":"mobile","platform":"android",
                "current_major_version":2,"replacement_major_version":3,
                "samples":20,"eligible_for_bias":True,"evidence_confidence":1.0,
                "success_rate":0.9,"posterior_success_rate":0.86,"regression_rate":0.05,
                "rollback_rate":0.0,"wilson_lower_95":0.70,"mean_quality_score":90.0,
            },
        ]}
        row=plan(obs,self.recommendations(),learning=learning)["replacement_plans"][0]
        fused=row["fused_historical_evidence"]
        self.assertEqual(fused["contributor_count"],2)
        self.assertGreater(fused["effective_samples"],20)
        self.assertGreater(fused["success_rate"],0.9)
        self.assertEqual(row["empirical_status"],"historically_supported")

    def test_distant_framework_history_has_small_fusion_weight(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0].update({
            "framework":"flutter","project_type":"game","primary_domain":"mobile",
            "platform":"android","current_major_version":3,"replacement_major_version":4,
        })
        learning={"rankings":[
            {
                "current_repo":"a/current","replacement_repo":"a/better",
                "framework":"flutter","project_type":"game","primary_domain":"mobile","platform":"android",
                "current_major_version":3,"replacement_major_version":4,
                "samples":10,"eligible_for_bias":True,"evidence_confidence":0.5,
                "success_rate":1.0,"posterior_success_rate":0.92,"regression_rate":0.0,
                "rollback_rate":0.0,"wilson_lower_95":0.72,"mean_quality_score":95.0,
            },
            {
                "current_repo":"a/current","replacement_repo":"a/better",
                "framework":"python","project_type":"trading","primary_domain":"backend","platform":"linux",
                "current_major_version":3,"replacement_major_version":4,
                "samples":100,"eligible_for_bias":True,"evidence_confidence":1.0,
                "success_rate":0.0,"posterior_success_rate":0.01,"regression_rate":1.0,
                "rollback_rate":1.0,"wilson_lower_95":0.0,"mean_quality_score":0.0,
            },
        ]}
        row=plan(obs,self.recommendations(),learning=learning)["replacement_plans"][0]
        contributors=row["fused_historical_evidence"]["contributors"]
        exact=next(x for x in contributors if x["framework"]=="flutter")
        distant=next(x for x in contributors if x["framework"]=="python")
        self.assertGreater(exact["normalized_weight"],distant["normalized_weight"])
        self.assertGreater(row["fused_historical_evidence"]["success_rate"],0.5)

    def test_low_sample_histories_can_accumulate_effective_evidence(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0].update({
            "framework":"flutter","project_type":"game","primary_domain":"mobile",
            "platform":"android","current_major_version":3,"replacement_major_version":4,
        })
        rows=[]
        for current,replacement in [(3,4),(2,3),(4,5)]:
            rows.append({
                "current_repo":"a/current","replacement_repo":"a/better",
                "framework":"flutter","project_type":"game","primary_domain":"mobile","platform":"android",
                "current_major_version":current,"replacement_major_version":replacement,
                "samples":4,"eligible_for_bias":False,"evidence_confidence":0.2,
                "success_rate":1.0,"posterior_success_rate":0.83,"regression_rate":0.0,
                "rollback_rate":0.0,"wilson_lower_95":0.51,"mean_quality_score":95.0,
            })
        row=plan(obs,self.recommendations(),learning={"rankings":rows})["replacement_plans"][0]
        fused=row["fused_historical_evidence"]
        self.assertEqual(fused["contributor_count"],3)
        self.assertLess(fused["effective_samples"],5)
        self.assertFalse(fused["eligible_for_bias"])

    def test_write_persists_plan(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            result=write(self.obsolescence(),self.recommendations(),out)
            saved=json.loads((out/"architecture-replacement-plan.json").read_text())
            self.assertEqual(saved,result)

if __name__=="__main__":
    unittest.main()

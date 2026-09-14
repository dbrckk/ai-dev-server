import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import architecture_feedback as af


class ArchitectureFeedbackTests(unittest.TestCase):
    def test_insufficient_history_does_not_bias(self):
        recs = {"matches": [{"repo": "a/core", "score": 90.0, "quality_score": 9.0}]}
        learning = {"rankings": [{"repo": "a/core", "samples": 4, "success_rate": 1.0}]}

        result = af.apply(recs, learning)

        self.assertFalse(result["feedback_applied"])
        self.assertEqual(result["matches"][0]["feedback_score"], 90.0)
        self.assertNotIn("historical_evidence", result["matches"][0])

    def test_success_history_applies_bounded_bonus(self):
        recs = {
            "matches": [
                {"repo": "a/core", "score": 90.0, "quality_score": 9.0},
                {"repo": "b/other", "score": 91.0, "quality_score": 8.0},
            ]
        }
        learning = {
            "rankings": [
                {
                    "repo": "a/core",
                    "samples": 8,
                    "success_rate": 1.0,
                    "mean_model_calls": 2.0,
                    "mean_cycles": 1.0,
                    "mean_blockers": 0.0,
                }
            ]
        }

        result = af.apply(recs, learning)

        self.assertTrue(result["feedback_applied"])
        self.assertEqual(result["matches"][0]["repo"], "a/core")
        self.assertEqual(result["matches"][0]["feedback_score"], 90.75)
        self.assertLessEqual(
            abs(result["matches"][0]["historical_evidence"]["advisory_bonus"]),
            af.MAX_SCORE_BONUS,
        )
        self.assertFalse(result["feedback_policy"]["can_add_dependency"])

    def test_poor_history_can_only_apply_small_penalty(self):
        recs = {"matches": [{"repo": "a/core", "score": 90.0}]}
        learning = {"rankings": [{"repo": "a/core", "samples": 10, "success_rate": 0.0}]}

        result = af.apply(recs, learning)

        self.assertEqual(result["matches"][0]["feedback_score"], 89.25)


    def test_unrelated_history_does_not_claim_feedback_applied(self):
        recs = {"matches": [{"repo": "a/core", "score": 90.0}]}
        learning = {"rankings": [{"repo": "other/repo", "samples": 10, "success_rate": 1.0}]}

        result = af.apply(recs, learning)

        self.assertFalse(result["feedback_applied"])
        self.assertEqual(result["feedback_rows_applied"], 0)
        self.assertEqual(result["matches"][0]["feedback_score"], 90.0)



    def test_domain_mismatch_does_not_bias_current_recommendation(self):
        recs = {
            "matches": [
                {
                    "repo": "a/core",
                    "domain": "mobile",
                    "score": 90.0,
                }
            ]
        }
        learning = {
            "rankings": [
                {
                    "repo": "a/core",
                    "domain": "backend",
                    "samples": 10,
                    "success_rate": 1.0,
                }
            ]
        }

        result = af.apply(recs, learning)

        self.assertFalse(result["feedback_applied"])
        self.assertEqual(result["matches"][0]["feedback_score"], 90.0)

    def test_matching_domain_can_apply_feedback(self):
        recs = {
            "matches": [
                {
                    "repo": "a/core",
                    "domain": "mobile",
                    "score": 90.0,
                }
            ]
        }
        learning = {
            "rankings": [
                {
                    "repo": "a/core",
                    "domain": "mobile",
                    "samples": 10,
                    "success_rate": 1.0,
                }
            ]
        }

        result = af.apply(recs, learning)

        self.assertTrue(result["feedback_applied"])
        self.assertEqual(result["matches"][0]["feedback_score"], 91.5)
        self.assertEqual(
            result["matches"][0]["historical_evidence"]["domain"],
            "mobile",
        )



    def test_stale_evidence_is_ignored(self):
        now = 10_000_000.0
        recs = {"matches": [{"repo": "a/core", "domain": "mobile", "score": 90.0}]}
        learning = {
            "rankings": [
                {
                    "repo": "a/core",
                    "domain": "mobile",
                    "samples": 10,
                    "success_rate": 1.0,
                    "latest_observed_at": now - af.MAX_EVIDENCE_AGE_SECONDS - 1,
                }
            ]
        }

        result = af.apply(recs, learning, now=now)

        self.assertFalse(result["feedback_applied"])
        self.assertEqual(result["matches"][0]["feedback_score"], 90.0)

    def test_fresh_evidence_is_allowed(self):
        now = 10_000_000.0
        recs = {"matches": [{"repo": "a/core", "domain": "mobile", "score": 90.0}]}
        learning = {
            "rankings": [
                {
                    "repo": "a/core",
                    "domain": "mobile",
                    "samples": 10,
                    "success_rate": 1.0,
                    "latest_observed_at": now - 60,
                }
            ]
        }

        result = af.apply(recs, learning, now=now)

        self.assertTrue(result["feedback_applied"])
        self.assertEqual(result["matches"][0]["feedback_score"], 91.5)



    def test_framework_mismatch_does_not_bias(self):
        recs = {"matches": [{"repo": "a/core", "domain": "mobile", "score": 90.0}]}
        learning = {
            "rankings": [
                {
                    "repo": "a/core",
                    "domain": "mobile",
                    "framework": "flutter",
                    "samples": 10,
                    "success_rate": 1.0,
                }
            ]
        }

        result = af.apply(recs, learning, framework="godot")

        self.assertFalse(result["feedback_applied"])
        self.assertEqual(result["matches"][0]["feedback_score"], 90.0)

    def test_matching_framework_can_bias(self):
        recs = {"matches": [{"repo": "a/core", "domain": "mobile", "score": 90.0}]}
        learning = {
            "rankings": [
                {
                    "repo": "a/core",
                    "domain": "mobile",
                    "framework": "godot",
                    "samples": 10,
                    "success_rate": 1.0,
                }
            ]
        }

        result = af.apply(recs, learning, framework="godot")

        self.assertTrue(result["feedback_applied"])
        self.assertEqual(result["matches"][0]["feedback_score"], 92.25)
        self.assertEqual(result["matches"][0]["historical_evidence"]["framework"], "godot")

    def test_stack_synergy_is_framework_scoped(self):
        learning = {
            "stack_rankings": [
                {
                    "repos": ["a/core", "b/ui"],
                    "framework": "flutter",
                    "samples": 10,
                    "success_rate": 1.0,
                }
            ]
        }

        mismatch = af.stack_adjustment("b/ui", ["a/core"], learning, framework="godot")
        matching = af.stack_adjustment("b/ui", ["a/core"], learning, framework="flutter")

        self.assertEqual(mismatch["bonus"], 0.0)
        self.assertGreater(matching["bonus"], 0.0)
    def test_project_type_mismatch_does_not_bias(self):
        recs = {"matches": [{"repo": "a/core", "domain": "mobile", "score": 90.0}]}
        learning = {"rankings": [{
            "repo": "a/core",
            "domain": "mobile",
            "framework": "flutter",
            "project_type": "game",
            "primary_domain": "mobile",
            "samples": 10,
            "success_rate": 1.0,
        }]}
        result = af.apply(
            recs,
            learning,
            framework="flutter",
            project_type="trading",
            primary_domain="mobile",
        )
        self.assertFalse(result["feedback_applied"])
        self.assertEqual(result["matches"][0]["feedback_score"], 90.0)

    def test_full_context_gets_full_bonus(self):
        recs = {"matches": [{"repo": "a/core", "domain": "mobile", "score": 90.0}]}
        learning = {"rankings": [{
            "repo": "a/core",
            "domain": "mobile",
            "framework": "flutter",
            "project_type": "game",
            "primary_domain": "mobile",
            "samples": 10,
            "success_rate": 1.0,
        }]}
        result = af.apply(
            recs,
            learning,
            framework="flutter",
            project_type="game",
            primary_domain="mobile",
        )
        self.assertEqual(result["matches"][0]["feedback_score"], 93.0)
        self.assertEqual(result["matches"][0]["historical_evidence"]["context_weight"], 1.0)

    def test_stack_synergy_is_project_type_scoped(self):
        learning = {"stack_rankings": [{
            "repos": ["a/core", "b/ui"],
            "framework": "flutter",
            "project_type": "game",
            "primary_domain": "mobile",
            "samples": 10,
            "success_rate": 1.0,
        }]}
        mismatch = af.stack_adjustment(
            "b/ui", ["a/core"], learning,
            framework="flutter", project_type="trading", primary_domain="mobile"
        )
        matching = af.stack_adjustment(
            "b/ui", ["a/core"], learning,
            framework="flutter", project_type="game", primary_domain="mobile"
        )
        self.assertEqual(mismatch["bonus"], 0.0)
        self.assertEqual(matching["bonus"], 2.0)
    def test_quality_score_changes_feedback_with_same_success_rate(self):
        recs = {"matches": [
            {"repo": "a/clean", "domain": "mobile", "score": 90.0, "quality_score": 9.0},
            {"repo": "b/costly", "domain": "mobile", "score": 90.0, "quality_score": 9.0},
        ]}
        learning = {"rankings": [
            {
                "repo": "a/clean",
                "domain": "mobile",
                "framework": "flutter",
                "project_type": "general",
                "primary_domain": "mobile",
                "samples": 10,
                "success_rate": 1.0,
                "mean_quality_score": 95.0,
            },
            {
                "repo": "b/costly",
                "domain": "mobile",
                "framework": "flutter",
                "project_type": "general",
                "primary_domain": "mobile",
                "samples": 10,
                "success_rate": 1.0,
                "mean_quality_score": 55.0,
            },
        ]}
        result = af.apply(
            recs, learning,
            framework="flutter",
            project_type="general",
            primary_domain="mobile",
        )
        by_repo = {x["repo"]: x for x in result["matches"]}
        self.assertGreater(by_repo["a/clean"]["feedback_score"], by_repo["b/costly"]["feedback_score"])
        self.assertGreater(
            by_repo["a/clean"]["historical_evidence"]["combined_outcome_rate"],
            by_repo["b/costly"]["historical_evidence"]["combined_outcome_rate"],
        )
    def test_large_sample_can_outweigh_perfect_small_sample(self):
        recs = {"matches": [
            {"repo": "small/perfect", "score": 90.0, "quality_score": 9.0},
            {"repo": "large/strong", "score": 90.0, "quality_score": 9.0},
        ]}
        learning = {"rankings": [
            {
                "repo": "small/perfect",
                "samples": 5,
                "success_rate": 1.0,
                "posterior_success_rate": 0.8571,
                "wilson_lower_95": 0.5655,
                "evidence_confidence": 0.25,
                "mean_quality_score": 100.0,
                "quality_shrunk_mean": 75.0,
            },
            {
                "repo": "large/strong",
                "samples": 50,
                "success_rate": 0.96,
                "posterior_success_rate": 0.9423,
                "wilson_lower_95": 0.8654,
                "evidence_confidence": 1.0,
                "mean_quality_score": 96.0,
                "quality_shrunk_mean": 91.818,
            },
        ]}
        result = af.apply(recs, learning)
        by_repo = {x["repo"]: x for x in result["matches"]}
        self.assertGreater(by_repo["large/strong"]["feedback_score"], by_repo["small/perfect"]["feedback_score"])
        self.assertLess(
            by_repo["small/perfect"]["historical_evidence"]["conservative_success_rate"],
            by_repo["large/strong"]["historical_evidence"]["conservative_success_rate"],
        )
        self.assertLess(
            by_repo["small/perfect"]["historical_evidence"]["evidence_confidence"],
            by_repo["large/strong"]["historical_evidence"]["evidence_confidence"],
        )

    def test_uncertainty_never_authorizes_dependencies(self):
        recs = {"matches": [{"repo": "a/core", "score": 90.0}]}
        learning = {"rankings": [{
            "repo": "a/core",
            "samples": 50,
            "success_rate": 1.0,
            "posterior_success_rate": 0.9808,
            "wilson_lower_95": 0.9286,
            "evidence_confidence": 1.0,
            "quality_shrunk_mean": 95.0,
        }]}
        result = af.apply(recs, learning)
        self.assertFalse(result["feedback_policy"]["can_add_dependency"])

if __name__ == "__main__":
    unittest.main()

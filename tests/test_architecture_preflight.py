import json
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import architecture_preflight as ap


class ArchitecturePreflightTests(unittest.TestCase):
    def test_low_confidence_convergent_baseline_passes(self):
        decision = {
            "autonomy_policy": {
                "validation_required": True,
                "validation_mode": "independent_review",
            },
            "constraints": {"primary_domain": "mobile"},
            "chosen": [
                {"repo": "a/core"},
                {"repo": "b/ui"},
            ],
        }
        recommendations = {"matches": [
            {"repo": "a/core", "score": 95.0, "quality_score": 9.5, "domain": "mobile"},
            {"repo": "b/ui", "score": 92.0, "quality_score": 9.0, "domain": "mobile"},
            {"repo": "c/other", "score": 80.0, "quality_score": 8.0, "domain": "backend"},
        ]}
        result = ap.validate(decision, recommendations)
        self.assertEqual(result["verdict"], "pass")
        self.assertTrue(result["architecture_changes_allowed"])
        self.assertTrue(result["top_choice_matches"])
        self.assertFalse(result["historical_feedback_used"])

    def test_low_confidence_divergent_baseline_holds_architecture_changes(self):
        decision = {
            "autonomy_policy": {
                "validation_required": True,
                "validation_mode": "independent_review",
            },
            "constraints": {"primary_domain": "mobile"},
            "chosen": [
                {"repo": "b/ui"},
                {"repo": "c/other"},
            ],
        }
        recommendations = {"matches": [
            {"repo": "a/core", "score": 99.0, "quality_score": 9.9, "domain": "mobile"},
            {"repo": "b/ui", "score": 82.0, "quality_score": 8.0, "domain": "mobile"},
            {"repo": "c/other", "score": 80.0, "quality_score": 8.0, "domain": "backend"},
        ]}
        result = ap.validate(decision, recommendations)
        self.assertEqual(result["verdict"], "hold")
        self.assertFalse(result["architecture_changes_allowed"])
        self.assertTrue(result["normal_code_changes_allowed"])
        self.assertFalse(result["top_choice_matches"])

    def test_high_confidence_is_not_blocked_by_preflight_disagreement(self):
        decision = {
            "autonomy_policy": {
                "validation_required": False,
                "validation_mode": "standard",
            },
            "constraints": {"primary_domain": "mobile"},
            "chosen": [{"repo": "b/ui"}],
        }
        recommendations = {"matches": [
            {"repo": "a/core", "score": 99.0, "quality_score": 9.9, "domain": "mobile"},
            {"repo": "b/ui", "score": 82.0, "quality_score": 8.0, "domain": "mobile"},
        ]}
        result = ap.validate(decision, recommendations)
        self.assertEqual(result["verdict"], "pass")
        self.assertTrue(result["architecture_changes_allowed"])
        self.assertFalse(result["validation_required"])

    def test_write_persists_machine_readable_result(self):
        with tempfile.TemporaryDirectory() as td:
            result = ap.write(
                {
                    "autonomy_policy": {"validation_required": False},
                    "chosen": [],
                    "constraints": {},
                },
                {"matches": []},
                Path(td),
            )
            saved = json.loads((Path(td) / "architecture-preflight.json").read_text())
            self.assertEqual(saved, result)


if __name__ == "__main__":
    unittest.main()

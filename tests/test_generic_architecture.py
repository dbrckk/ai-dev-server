import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import generic_project as gp


class GenericArchitectureTests(unittest.TestCase):
    def test_prepare_architecture_is_generic_and_advisory(self):
        state = {"engine": "generic", "toolchain": "python"}
        req = {
            "id": "demo",
            "target_repo": "owner/repo",
            "app_name": "demo",
            "brief": "Improve the backend.",
        }
        recommendations = {"matches": [{"repo": "a/core", "score": 90.0}]}
        decision = {
            "status": "planned",
            "advisory_only": True,
            "autonomy_policy": {
                "decision_confidence": "low",
                "validation_required": True,
                "validation_mode": "independent_review",
            },
            "constraints": {
                "framework": "generic",
                "publication_target": "unspecified",
            },
        }

        with tempfile.TemporaryDirectory() as td, \
             patch("generic_project.recommend", return_value=recommendations) as recommend, \
             patch("generic_project.architecture_learning_root", return_value=Path(td)) as root_for_output, \
             patch("generic_project.summarize_architecture_learning", return_value={"rankings": []}) as summarize, \
             patch("generic_project.write_architecture_plan", return_value=decision) as planner:
            root = gp._prepare_architecture(req, Path(td) / "project", state)

        self.assertEqual(root, Path(td))
        self.assertEqual(state["architecture_recommendations"], recommendations)
        self.assertEqual(state["architecture_decision"], decision)
        self.assertEqual(state["architecture_autonomy_policy"]["decision_confidence"], "low")
        self.assertIn("architecture_changes_allowed", state["architecture_autonomy_policy"])
        self.assertEqual(state["architecture_preflight"]["status"], "validated")
        self.assertEqual(state["architecture_preflight"]["validation_mode"], "independent_review")
        recommend.assert_called_once()
        root_for_output.assert_called_once()
        summarize.assert_called_once_with(Path(td))
        self.assertEqual(planner.call_args.kwargs["framework"], "generic")
        self.assertEqual(planner.call_args.kwargs["publication_target"], "unspecified")

    def test_record_architecture_writes_full_evidence_chain(self):
        state = {
            "status": "complete",
            "architecture_decision": {"status": "planned", "chosen": []},
            "architecture_recommendations": {"matches": []},
        }
        evaluation = {"status": "evaluated", "verdict": "retain"}
        benchmark = {"status": "benchmarked", "migration_candidates": []}
        learning = {"schema": 1, "rankings": []}

        with tempfile.TemporaryDirectory() as td, \
             patch("generic_project.write_architecture_evaluation", return_value=evaluation) as evaluate, \
             patch("generic_project.write_architecture_benchmark", return_value=benchmark) as benchmark_write, \
             patch("generic_project.write_architecture_outcome") as outcome, \
             patch("generic_project.write_architecture_learning", return_value=learning) as learn:
            out = Path(td) / "project"
            gp._record_architecture(state, out, Path(td))

        self.assertEqual(state["architecture_evaluation"], evaluation)
        self.assertEqual(state["architecture_benchmark"], benchmark)
        self.assertEqual(state["architecture_learning"], learning)
        evaluate.assert_called_once()
        benchmark_write.assert_called_once()
        outcome.assert_called_once_with(state, out)
        learn.assert_called_once_with(Path(td))

    def test_learning_failure_is_non_fatal_after_verified_round(self):
        state = {
            "status": "complete",
            "architecture_decision": {"status": "planned", "chosen": []},
            "architecture_recommendations": {"matches": []},
        }
        with tempfile.TemporaryDirectory() as td, \
             patch("generic_project.write_architecture_evaluation", return_value={"status": "evaluated"}), \
             patch("generic_project.write_architecture_benchmark", return_value={"status": "benchmarked"}), \
             patch("generic_project.write_architecture_outcome"), \
             patch("generic_project.write_architecture_learning", side_effect=OSError("disk")):
            gp._record_architecture(state, Path(td) / "project", Path(td))

        self.assertEqual(state["architecture_learning"], {"status": "unavailable"})


if __name__ == "__main__":
    unittest.main()

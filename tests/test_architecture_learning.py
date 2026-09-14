import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import architecture_learning as al


class ArchitectureLearningTests(unittest.TestCase):
    def _write(self, root, project, repos, successful, calls, cycles, blockers):
        out = root / project
        out.mkdir(parents=True)
        payload = {
            "schema": 1,
            "decision_id": project,
            "chosen_repositories": repos,
            "outcome": {
                "successful": successful,
                "model_calls_this_cycle": calls,
                "cycles": cycles,
                "blocker_count": blockers,
            },
        }
        (out / "architecture-outcome.json").write_text(
            json.dumps(payload),
            encoding="utf-8",
        )

    def test_requires_multiple_samples_before_advisory_bias(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "p1", ["a/core"], True, 2, 1, 0)
            result = al.summarize(root)
            row = result["rankings"][0]
            self.assertEqual(row["samples"], 1)
            self.assertFalse(row["eligible_for_advisory_bias"])

    def test_aggregates_success_and_cost_metrics(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "p1", ["a/core"], True, 2, 1, 0)
            self._write(root, "p2", ["a/core"], True, 4, 2, 1)
            self._write(root, "p3", ["a/core"], False, 6, 3, 2)
            self._write(root, "p4", ["a/core"], True, 3, 1, 0)
            self._write(root, "p5", ["a/core"], True, 3, 1, 0)

            result = al.summarize(root)
            row = result["rankings"][0]

            self.assertEqual(row["samples"], 5)
            self.assertEqual(row["success_rate"], 0.8)
            self.assertEqual(row["mean_model_calls"], 3.6)
            self.assertEqual(row["mean_cycles"], 1.6)
            self.assertEqual(row["mean_blockers"], 0.6)
            self.assertTrue(row["eligible_for_advisory_bias"])

    def test_better_evidence_ranks_higher(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for i in range(5):
                self._write(root, f"good-{i}", ["good/repo"], True, 2, 1, 0)
                self._write(root, f"bad-{i}", ["bad/repo"], i == 0, 5, 3, 2)

            rankings = al.summarize(root)["rankings"]
            self.assertEqual(rankings[0]["repo"], "good/repo")
            self.assertEqual(rankings[1]["repo"], "bad/repo")


    def test_write_persists_bounded_learning_summary(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "p1", ["a/core"], True, 2, 1, 0)
            result = al.write(root)
            saved = json.loads((root / "architecture-learning.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, result)
            self.assertTrue(saved["advisory_only"])



    def test_same_repo_is_separated_by_domain(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            mobile = root / "mobile"
            mobile.mkdir()
            (mobile / "architecture-outcome.json").write_text(
                json.dumps({
                    "schema": 1,
                    "chosen_contexts": [{"repo": "a/core", "domain": "mobile"}],
                    "outcome": {
                        "successful": True,
                        "model_calls_this_cycle": 2,
                        "cycles": 1,
                        "blocker_count": 0,
                    },
                }),
                encoding="utf-8",
            )

            backend = root / "backend"
            backend.mkdir()
            (backend / "architecture-outcome.json").write_text(
                json.dumps({
                    "schema": 1,
                    "chosen_contexts": [{"repo": "a/core", "domain": "backend"}],
                    "outcome": {
                        "successful": False,
                        "model_calls_this_cycle": 5,
                        "cycles": 3,
                        "blocker_count": 2,
                    },
                }),
                encoding="utf-8",
            )

            rankings = al.summarize(root)["rankings"]

            by_domain = {row["domain"]: row for row in rankings}
            self.assertEqual(set(by_domain), {"mobile", "backend"})
            self.assertEqual(by_domain["mobile"]["success_rate"], 1.0)
            self.assertEqual(by_domain["backend"]["success_rate"], 0.0)


    def test_stack_rankings_aggregate_joint_outcomes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for i in range(5):
                self._write(root, f"p{i}", ["a/core", "b/helper"], True, 2, 1, 0)
            result = al.summarize(root)
            self.assertEqual(result["schema"], 2)
            self.assertEqual(result["stack_rankings"][0]["repos"], ["a/core", "b/helper"])
            self.assertEqual(result["stack_rankings"][0]["samples"], 5)
            self.assertTrue(result["stack_rankings"][0]["eligible_for_advisory_bias"])

    def test_learning_root_does_not_escape_arbitrary_output_directory(self):
        self.assertEqual(
            al.root_for_output(Path("/tmp/demo-output")),
            Path("/tmp/demo-output"),
        )
        self.assertEqual(
            al.root_for_output(Path("studio-output/project-a")),
            Path("studio-output"),
        )
        self.assertEqual(
            al.root_for_output(Path("studio-output")),
            Path("studio-output"),
        )



    def test_same_repo_and_domain_are_separated_by_framework(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name, framework, successful in [
                ("flutter", "flutter", True),
                ("godot", "godot", False),
            ]:
                out = root / name
                out.mkdir()
                (out / "architecture-outcome.json").write_text(
                    json.dumps({
                        "schema": 1,
                        "decision_constraints": {"framework": framework},
                        "chosen_contexts": [{"repo": "a/core", "domain": "mobile"}],
                        "outcome": {
                            "successful": successful,
                            "model_calls_this_cycle": 2,
                            "cycles": 1,
                            "blocker_count": 0 if successful else 1,
                        },
                    }),
                    encoding="utf-8",
                )

            rankings = al.summarize(root)["rankings"]
            keyed = {(row["framework"], row["domain"]): row for row in rankings}

            self.assertEqual(keyed[("flutter", "mobile")]["success_rate"], 1.0)
            self.assertEqual(keyed[("godot", "mobile")]["success_rate"], 0.0)



if __name__ == "__main__":
    unittest.main()

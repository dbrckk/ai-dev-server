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
            self.assertEqual(row["mean_quality_score"], 80.0)
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
            self.assertEqual(result["schema"], 7)
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


    def test_stack_learning_is_separated_by_project_type_and_domain(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for i, (ptype, domain, success) in enumerate([
                ("game", "game_dev", True),
                ("game", "game_dev", True),
                ("trading", "trading", False),
                ("trading", "trading", False),
            ]):
                out = root / f"p{i}"
                out.mkdir()
                (out / "architecture-outcome.json").write_text(
                    json.dumps({
                        "schema": 1,
                        "decision_constraints": {
                            "framework": "flutter",
                            "project_type": ptype,
                            "primary_domain": domain,
                        },
                        "chosen_repositories": ["a/core", "b/helper"],
                        "outcome": {
                            "successful": success,
                            "model_calls_this_cycle": 2,
                            "cycles": 1,
                            "blocker_count": 0 if success else 2,
                        },
                    }),
                    encoding="utf-8",
                )
            stacks = al.summarize(root)["stack_rankings"]
            by_context = {(x["project_type"], x["primary_domain"]): x for x in stacks}
            self.assertEqual(by_context[("game", "game_dev")]["success_rate"], 1.0)
            self.assertEqual(by_context[("trading", "trading")]["success_rate"], 0.0)

    def test_repo_learning_is_separated_by_project_type(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for i, ptype in enumerate(["game", "trading"]):
                out = root / f"p{i}"
                out.mkdir()
                (out / "architecture-outcome.json").write_text(
                    json.dumps({
                        "schema": 1,
                        "decision_constraints": {
                            "framework": "flutter",
                            "project_type": ptype,
                            "primary_domain": "mobile",
                        },
                        "chosen_contexts": [{"repo": "a/core", "domain": "mobile"}],
                        "outcome": {
                            "successful": ptype == "game",
                            "model_calls_this_cycle": 2,
                            "cycles": 1,
                            "blocker_count": 0,
                        },
                    }),
                    encoding="utf-8",
                )
            rankings = al.summarize(root)["rankings"]
            by_type = {x["project_type"]: x for x in rankings}
            self.assertEqual(by_type["game"]["success_rate"], 1.0)
            self.assertEqual(by_type["trading"]["success_rate"], 0.0)
    def test_continuous_quality_distinguishes_successful_stacks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for i, quality in enumerate([95.0, 92.0, 90.0, 94.0, 93.0]):
                out = root / f"good-{i}"
                out.mkdir()
                (out / "architecture-outcome.json").write_text(json.dumps({
                    "schema": 3,
                    "decision_constraints": {"framework": "flutter", "project_type": "general", "primary_domain": "mobile"},
                    "chosen_repositories": ["good/a", "good/b"],
                    "outcome": {
                        "successful": True,
                        "quality_score": quality,
                        "model_calls_this_cycle": 2,
                        "cycles": 1,
                        "blocker_count": 0,
                    },
                }), encoding="utf-8")
            for i, quality in enumerate([60.0, 62.0, 58.0, 61.0, 59.0]):
                out = root / f"weak-{i}"
                out.mkdir()
                (out / "architecture-outcome.json").write_text(json.dumps({
                    "schema": 3,
                    "decision_constraints": {"framework": "flutter", "project_type": "general", "primary_domain": "mobile"},
                    "chosen_repositories": ["weak/a", "weak/b"],
                    "outcome": {
                        "successful": True,
                        "quality_score": quality,
                        "model_calls_this_cycle": 10,
                        "cycles": 5,
                        "blocker_count": 1,
                    },
                }), encoding="utf-8")
            stacks = al.summarize(root)["stack_rankings"]
            self.assertEqual(stacks[0]["repos"], ["good/a", "good/b"])
            self.assertGreater(stacks[0]["mean_quality_score"], stacks[1]["mean_quality_score"])
    def test_uncertainty_metrics_favor_large_samples(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for i in range(5):
                self._write(root, f"small-{i}", ["small/repo"], True, 2, 1, 0)
            for i in range(50):
                self._write(root, f"large-{i}", ["large/repo"], i < 48, 2, 1, 0)
            rows = {x["repo"]: x for x in al.summarize(root)["rankings"]}
            self.assertEqual(rows["small/repo"]["success_rate"], 1.0)
            self.assertEqual(rows["large/repo"]["success_rate"], 0.96)
            self.assertLess(rows["small/repo"]["wilson_lower_95"], rows["large/repo"]["wilson_lower_95"])
            self.assertLess(rows["small/repo"]["evidence_confidence"], rows["large/repo"]["evidence_confidence"])
            self.assertLess(rows["small/repo"]["quality_shrunk_mean"], rows["large/repo"]["quality_shrunk_mean"])
    def test_detects_recent_quality_degradation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qualities = [95, 94, 93, 92, 91, 60, 58, 55, 52, 50]
            for i, quality in enumerate(qualities):
                out = root / f"p{i}"
                out.mkdir()
                (out / "architecture-outcome.json").write_text(json.dumps({
                    "schema": 3,
                    "observed_at": float(i + 1),
                    "decision_constraints": {
                        "framework": "flutter",
                        "project_type": "general",
                        "primary_domain": "mobile",
                    },
                    "chosen_contexts": [{"repo": "a/core", "domain": "mobile"}],
                    "outcome": {
                        "successful": True,
                        "quality_score": quality,
                        "model_calls_this_cycle": 2,
                        "cycles": 1,
                        "blocker_count": 0,
                    },
                }), encoding="utf-8")
            row = al.summarize(root)["rankings"][0]
            self.assertEqual(row["drift"]["status"], "degraded")
            self.assertLess(row["drift"]["quality_delta"], -15.0)
            self.assertGreater(row["drift"]["score"], 0.0)

    def test_detects_recent_success_degradation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            successes = [True] * 5 + [True, False, False, False, False]
            for i, success in enumerate(successes):
                out = root / f"p{i}"
                out.mkdir()
                (out / "architecture-outcome.json").write_text(json.dumps({
                    "schema": 3,
                    "observed_at": float(i + 1),
                    "chosen_repositories": ["a/core", "b/helper"],
                    "outcome": {
                        "successful": success,
                        "quality_score": 90.0 if success else 30.0,
                        "model_calls_this_cycle": 2,
                        "cycles": 1,
                        "blocker_count": 0 if success else 2,
                    },
                }), encoding="utf-8")
            stack = al.summarize(root)["stack_rankings"][0]
            self.assertEqual(stack["drift"]["status"], "degraded")
            self.assertLess(stack["drift"]["success_delta"], -0.2)

    def test_drift_requires_recent_and_baseline_windows(self):
        observations = [
            {"observed_at": float(i), "successful": True, "quality": 90.0}
            for i in range(9)
        ]
        result = al._drift(observations)
        self.assertEqual(result["status"], "insufficient_evidence")

    def test_stable_history_is_not_marked_degraded(self):
        observations = [
            {"observed_at": float(i), "successful": True, "quality": 90.0 + (i % 2)}
            for i in range(12)
        ]
        result = al._drift(observations)
        self.assertEqual(result["status"], "stable")
    def test_degraded_history_is_exposed_as_drift_alert(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qualities = [95, 95, 95, 95, 95, 50, 50, 50, 50, 50]
            for i, quality in enumerate(qualities):
                out = root / f"p{i}"
                out.mkdir()
                (out / "architecture-outcome.json").write_text(json.dumps({
                    "schema": 3,
                    "observed_at": float(i + 1),
                    "decision_constraints": {
                        "framework": "flutter",
                        "project_type": "general",
                        "primary_domain": "mobile",
                    },
                    "chosen_contexts": [{"repo": "a/core", "domain": "mobile"}],
                    "outcome": {
                        "successful": True,
                        "quality_score": quality,
                        "model_calls_this_cycle": 2,
                        "cycles": 1,
                        "blocker_count": 0,
                    },
                }), encoding="utf-8")
            result = al.summarize(root)
            alerts = [x for x in result["drift_alerts"] if x.get("type") == "repository"]
            self.assertTrue(alerts)
            self.assertEqual(alerts[0]["repo"], "a/core")
            self.assertLess(alerts[0]["quality_delta"], 0.0)

if __name__ == "__main__":
    unittest.main()

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from studio.autonomous_project import ensure_project_goal, run_persistent_project
from studio.human_input_request import write_request


class HumanHandoffStatusV3Tests(unittest.TestCase):
    def test_handoff_never_persists_secret_value_and_records_exact_name(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            secret_value = "canary-super-secret-value"
            text_path = write_request(
                root,
                "demo",
                f"Missing CUSTOM_API_KEY={secret_value}",
                target_repo="owner/repo",
            )
            text = text_path.read_text(encoding="utf-8")
            machine_text = (root / "user-input-required.json").read_text(encoding="utf-8")
            machine = json.loads(machine_text)

        self.assertNotIn(secret_value, text)
        self.assertNotIn(secret_value, machine_text)
        self.assertEqual(machine["required_secret_names"], ["CUSTOM_API_KEY"])
        self.assertIn("CUSTOM_API_KEY", text)

    def test_named_secret_resumes_terminal_goal_before_worker_runs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            first_calls = {"n": 0}

            def require_secret(*args):
                first_calls["n"] += 1
                return {
                    "status": "blocked",
                    "report": {"blockers": ["Missing CUSTOM_API_KEY"]},
                    "next_stage": "provider_setup",
                }

            first = run_persistent_project(
                "request.json",
                out,
                str(root / "work"),
                runner=lambda *a, **k: None,
                deadline=100,
                clock=lambda: 0,
                run_once=require_secret,
                max_cycles=2,
            )
            self.assertEqual(first["status"], "human_action_required")
            self.assertEqual(first_calls["n"], 1)
            self.assertTrue((out / "USER_INPUT_REQUIRED.txt").is_file())
            self.assertTrue((out / "user-input-required.json").is_file())

            resumed_calls = {"n": 0}

            def complete(*args):
                resumed_calls["n"] += 1
                return {
                    "status": "complete",
                    "report": {
                        "status": "finished",
                        "completion": {"finished": True},
                        "release_status": "store_ready",
                    },
                    "next_stage": None,
                }

            with patch.dict(os.environ, {"CUSTOM_API_KEY": "present-only-in-env"}, clear=False):
                second = run_persistent_project(
                    "request.json",
                    out,
                    str(root / "work"),
                    runner=lambda *a, **k: None,
                    deadline=100,
                    clock=lambda: 0,
                    run_once=complete,
                    max_cycles=2,
                )

            self.assertEqual(second["status"], "complete")
            self.assertEqual(resumed_calls["n"], 1)
            self.assertFalse((out / "USER_INPUT_REQUIRED.txt").exists())
            self.assertFalse((out / "user-input-required.json").exists())

    def test_missing_named_secret_does_not_reinvoke_worker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"

            first = run_persistent_project(
                "request.json",
                out,
                str(root / "work"),
                runner=lambda *a, **k: None,
                deadline=100,
                clock=lambda: 0,
                run_once=lambda *args: {
                    "status": "blocked",
                    "report": {"blockers": ["Missing CUSTOM_API_KEY"]},
                    "next_stage": "provider_setup",
                },
                max_cycles=2,
            )
            self.assertEqual(first["status"], "human_action_required")

            calls = {"n": 0}

            def should_not_run(*args):
                calls["n"] += 1
                raise AssertionError("worker must not run while prerequisite is absent")

            with patch.dict(os.environ, {}, clear=True):
                second = run_persistent_project(
                    "request.json",
                    out,
                    str(root / "work"),
                    runner=lambda *a, **k: None,
                    deadline=100,
                    clock=lambda: 0,
                    run_once=should_not_run,
                    max_cycles=2,
                )
            self.assertEqual(second["status"], "human_action_required")
            self.assertEqual(calls["n"], 0)

    def test_project_status_reads_sealed_goal_without_running_work(self):
        from studio.project_status import read_status

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            ensure_project_goal(out, "demo", "Complete demo", max_attempts=7)
            status = read_status(out)

        self.assertEqual(status["goal_id"], "demo")
        self.assertEqual(status["status"], "active")
        self.assertEqual(status["attempt"], 0)
        self.assertEqual(status["max_attempts"], 7)
        self.assertEqual(status["missing_evidence"], ["project_completion"])
        self.assertFalse(status["human_action_required"])


if __name__ == "__main__":
    unittest.main()

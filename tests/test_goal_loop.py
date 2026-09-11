from pathlib import Path
import tempfile
import unittest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from capability_registry import new_registry, save as save_registry, load as load_registry
from goal_engine import new_goal, save as save_goal, load as load_goal
from goal_loop import run_goal


class GoalLoopTests(unittest.TestCase):
    def make_paths(self, root):
        goal_path = root / "goal.json"
        registry_path = root / "registry.json"
        save_goal(goal_path, new_goal(
            "g1",
            "finish autonomously",
            [{"name": "done", "required_evidence": ["ok"]}],
            max_attempts=5,
        ))
        save_registry(registry_path, new_registry())
        return goal_path, registry_path

    def test_relaunch_until_required_evidence_exists(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            goal_path, registry_path = self.make_paths(root)
            calls = {"n": 0}
            def execute(state):
                calls["n"] += 1
                if calls["n"] < 3:
                    return {"failure": "not yet"}
                return {"evidence": {"ok": "proved"}}
            state = run_goal(goal_path, registry_path, execute, max_cycles=5)
            self.assertEqual(state["status"], "complete")
            self.assertEqual(calls["n"], 3)
            self.assertEqual(state["evidence"]["ok"], "proved")
            self.assertEqual(load_goal(goal_path)["status"], "complete")

    def test_missing_capability_is_adapted_registered_and_goal_resumes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            goal_path, registry_path = self.make_paths(root)
            calls = {"execute": 0, "adapt": 0}
            def execute(state):
                calls["execute"] += 1
                if calls["execute"] == 1:
                    return {"missing_capability": "image_assets"}
                return {"evidence": {"ok": "proved"}}
            def adapt(name, state):
                calls["adapt"] += 1
                self.assertEqual(name, "image_assets")
                return {"provider": "builtin-assets", "evidence": {"validated": True}}
            state = run_goal(goal_path, registry_path, execute, adapt, max_cycles=6)
            self.assertEqual(state["status"], "complete")
            self.assertEqual(calls["adapt"], 1)
            registry = load_registry(registry_path)
            self.assertIn("image_assets", registry["capabilities"])
            self.assertIn("capability:image_assets", state["evidence"])

    def test_unverified_adaptation_never_registers_capability(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            goal_path, registry_path = self.make_paths(root)
            def execute(state):
                return {"missing_capability": "x"}
            def adapt(name, state):
                return {"provider": "adapter", "evidence": {}}
            state = run_goal(goal_path, registry_path, execute, adapt, max_cycles=3)
            self.assertEqual(state["status"], "active")
            self.assertTrue(any("capability adaptation unverified:x" in x for x in state["failures"]))
            self.assertNotIn("x", load_registry(registry_path)["capabilities"])

    def test_yield_run_preserves_attempt_budget_and_returns_active(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            goal_path,registry_path=self.make_paths(root)
            state=run_goal(goal_path,registry_path,lambda state: {"yield_run":True,"evidence":{"adaptation_progress":{"phase":"pending_merge"}}},max_cycles=3)
            self.assertEqual(state["status"],"active")
            self.assertEqual(state["attempt"],0)
            self.assertIn("adaptation_progress",state["evidence"])

    def test_human_action_stops_and_persists_terminal_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            goal_path, registry_path = self.make_paths(root)
            state = run_goal(goal_path, registry_path, lambda state: {"human_action": "approve_release"}, max_cycles=3)
            self.assertEqual(state["status"], "human_action_required")
            self.assertEqual(state["human_action"], "approve_release")
            self.assertEqual(load_goal(goal_path)["status"], "human_action_required")

    def test_absent_adapter_leads_to_blocked_terminal_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            goal_path, registry_path = self.make_paths(root)
            state = run_goal(goal_path, registry_path, lambda state: {"missing_capability": "missing_tool"}, max_cycles=4)
            self.assertEqual(state["status"], "blocked")
            self.assertIn("no adapter for capability:missing_tool", state["blocked_reason"])

    def test_local_cycle_budget_does_not_fake_completion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            goal_path, registry_path = self.make_paths(root)
            state = run_goal(goal_path, registry_path, lambda state: {"failure": "still incomplete"}, max_cycles=2)
            self.assertEqual(state["status"], "active")
            self.assertEqual(state["attempt"], 2)
            self.assertNotEqual(state["status"], "complete")


if __name__ == "__main__":
    unittest.main()

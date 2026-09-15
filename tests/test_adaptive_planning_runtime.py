import ast
import importlib
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "studio"))
GENERIC_PROJECT = ROOT / "studio" / "generic_project.py"


class AdaptivePlanningRuntimeTests(unittest.TestCase):
    def test_planning_requirement_is_shared_with_role_allocator(self):
        allocator = importlib.import_module("adaptive_role_allocator")
        self.assertTrue(hasattr(allocator, "planning_required"))
        planning_required = allocator.planning_required

        self.assertFalse(planning_required(
            difficulty=0.2,
            remaining_seconds=1000,
            verification_seconds=30,
        ))
        self.assertTrue(planning_required(
            difficulty=0.7,
            remaining_seconds=1000,
            verification_seconds=60,
        ))
        self.assertFalse(planning_required(
            difficulty=1.0,
            remaining_seconds=20,
            verification_seconds=120,
        ))

    def test_planning_budget_pressure_is_exposed_for_telemetry(self):
        allocator = importlib.import_module("adaptive_role_allocator")
        self.assertTrue(hasattr(allocator, "budget_pressure"))
        budget_pressure = allocator.budget_pressure

        self.assertEqual(budget_pressure(
            remaining_seconds=None,
            verification_seconds=60,
        ), 0.0)
        self.assertAlmostEqual(budget_pressure(
            remaining_seconds=20,
            verification_seconds=120,
        ), 0.9166666667, places=6)

    def test_planning_policy_reports_stable_reason(self):
        policy = importlib.import_module("adaptive_phase_policy")
        planning_phase_decision = policy.planning_phase_decision

        skipped = planning_phase_decision(
            require_planning=False,
            brief="Fix the typo in the README",
        )
        self.assertEqual(skipped["reason"], "adaptive policy skipped model planning")

        required = planning_phase_decision(
            require_planning=True,
            brief="Refactor the scheduler architecture",
        )
        self.assertEqual(required["reason"], "adaptive planning required")

        invalid = planning_phase_decision(
            require_planning=False,
            brief="   ",
        )
        self.assertEqual(invalid["reason"], "invalid brief requires model planning")

    def test_planning_policy_skips_only_when_safe_and_has_deterministic_plan(self):
        policy = importlib.import_module("adaptive_phase_policy")
        self.assertTrue(hasattr(policy, "planning_phase_decision"))
        planning_phase_decision = policy.planning_phase_decision

        skipped = planning_phase_decision(
            require_planning=False,
            brief="Fix the typo in the README",
        )
        self.assertFalse(skipped["launch_model"])
        self.assertTrue(skipped["plan"]["adaptive_skipped"])
        self.assertEqual(skipped["plan"]["objective"], "Fix the typo in the README")
        self.assertTrue(skipped["plan"]["work_items"])
        self.assertTrue(skipped["plan"]["done_when"])

        required = planning_phase_decision(
            require_planning=True,
            brief="Refactor the scheduler architecture",
        )
        self.assertTrue(required["launch_model"])
        self.assertIsNone(required["plan"])

        invalid = planning_phase_decision(
            require_planning=False,
            brief="   ",
        )
        self.assertTrue(invalid["launch_model"])
        self.assertIsNone(invalid["plan"])

    def test_generic_runtime_wires_preplanning_decision_before_plan_model(self):
        source = GENERIC_PROJECT.read_text(encoding="utf-8")
        tree = ast.parse(source)

        allocator_import = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "adaptive_role_allocator"
            and any(alias.name == "planning_required" for alias in node.names)
            for node in tree.body
        )
        policy_import = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "adaptive_phase_policy"
            and any(alias.name == "planning_phase_decision" for alias in node.names)
            for node in tree.body
        )
        self.assertTrue(allocator_import)
        self.assertTrue(policy_import)
        self.assertIn("planning_required(", source)
        self.assertIn("planning_phase_decision(", source)
        self.assertIn('if planning_policy["launch_model"]:', source)
        self.assertIn('plan = planning_policy["plan"]', source)
        self.assertLess(source.index("planning_required("), source.index("planning_phase_decision("))
        self.assertLess(source.index("planning_phase_decision("), source.index("PLAN_SYSTEM,"))

    def test_round_state_persists_planning_decision_telemetry(self):
        source = GENERIC_PROJECT.read_text(encoding="utf-8")

        self.assertIn("planning_decision = {", source)
        self.assertIn('"model_launched": bool(planning_policy["launch_model"])', source)
        self.assertIn('"adaptive_skipped": not bool(planning_policy["launch_model"])', source)
        self.assertIn('"require_planning": round_require_planning', source)
        self.assertIn('"difficulty": round(normalized_difficulty, 4)', source)
        self.assertIn('"budget_pressure": round(', source)
        self.assertIn('"reason": planning_policy["reason"]', source)
        self.assertIn('"planning_decision": planning_decision', source)


if __name__ == "__main__":
    unittest.main()

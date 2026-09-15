import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GENERIC_PROJECT = ROOT / "studio" / "generic_project.py"


class GenericAdaptiveReviewWiringTests(unittest.TestCase):
    def test_generic_runtime_wires_allocator_review_requirement_into_phase_policy(self):
        source = GENERIC_PROJECT.read_text(encoding="utf-8")
        tree = ast.parse(source)

        imported = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "adaptive_phase_policy"
            and any(alias.name == "review_phase_decision" for alias in node.names)
            for node in tree.body
        )
        self.assertTrue(imported, "generic runtime must import review_phase_decision")

        fail_closed_default = any(
            isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "round_require_review" for target in node.targets)
            and isinstance(node.value, ast.Constant)
            and node.value.value is True
            for node in ast.walk(tree)
        )
        self.assertTrue(fail_closed_default, "round review requirement must default to True")

        allocator_override = any(
            isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "round_require_review" for target in node.targets)
            and isinstance(node.value, ast.Attribute)
            and node.value.attr == "require_review"
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id == "role_allocation"
            for node in ast.walk(tree)
        )
        self.assertTrue(allocator_override, "allocator must be able to lower the review requirement")

        policy_calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "review_phase_decision"
        ]
        self.assertEqual(len(policy_calls), 1)
        keywords = {item.arg: item.value for item in policy_calls[0].keywords if item.arg}
        self.assertIsInstance(keywords.get("require_review"), ast.Name)
        self.assertEqual(keywords["require_review"].id, "round_require_review")
        self.assertIsInstance(keywords.get("verification"), ast.Name)
        self.assertEqual(keywords["verification"].id, "verification")
        self.assertIsInstance(keywords.get("review_remaining"), ast.Name)
        self.assertEqual(keywords["review_remaining"].id, "review_remaining")

        self.assertIn('if review_policy["launch_model"]:', source)
        self.assertIn('review = review_policy["review"]', source)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from task_context import classify, hierarchy, weighted_contexts


class TaskContextTests(unittest.TestCase):
    def test_explicit_bugfix_beats_backend_toolchain(self):
        self.assertEqual(
            classify("Fix crash when API returns 500", {"stacks":["python"]}),
            "bugfix",
        )

    def test_tests_context_is_detected(self):
        self.assertEqual(
            classify("Improve pytest coverage for authentication", {"stacks":["python"]}),
            "tests",
        )

    def test_mobile_context_is_detected(self):
        self.assertEqual(
            classify("Implement Android mobile settings screen", {"stacks":["gradle"]}),
            "mobile",
        )

    def test_frontend_context_is_detected(self):
        self.assertEqual(
            classify("Refine React component UI spacing", {"stacks":["node"]}),
            "frontend",
        )

    def test_backend_fallback_uses_toolchain(self):
        self.assertEqual(
            classify("Implement the requested feature", {"stacks":["go"]}),
            "backend",
        )

    def test_hierarchy_falls_back_through_stack_and_general(self):
        self.assertEqual(
            hierarchy("Fix API crash", {"stacks":["python","node"]}),
            ["bugfix","stack:node","stack:python","general"],
        )

    def test_weighted_contexts_capture_multiple_task_signals(self):
        weighted = dict(weighted_contexts(
            "Fix backend API bug and add regression tests",
            {"stacks":["python"]},
        ))
        self.assertIn("bugfix", weighted)
        self.assertIn("backend", weighted)
        self.assertIn("tests", weighted)
        self.assertIn("stack:python", weighted)
        self.assertAlmostEqual(sum(weighted.values()), 1.0)
        self.assertGreater(weighted["bugfix"], weighted["general"])

    def test_general_when_no_signal_exists(self):
        self.assertEqual(classify("Improve the project", {"stacks":[]}), "general")


if __name__=="__main__":
    unittest.main()

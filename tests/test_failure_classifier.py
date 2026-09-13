from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from failure_classifier import classify, policy


def verification(log="", returncode=1, status="failed", passed=False):
    return {
        "status": status,
        "passed": passed,
        "results": [{
            "passed": passed,
            "returncode": returncode,
            "log_tail": log,
            "command": ["pytest", "-q"],
        }] if status != "no_verifier" else [],
    }


class FailureClassifierTests(unittest.TestCase):
    def test_dependency_failure(self):
        result = classify(verification("ModuleNotFoundError: No module named 'x'"), changed_files=["a.py"])
        self.assertEqual(result["category"], "dependency_failure")
        self.assertEqual(policy(result)["action"], "repair_dependencies")

    def test_compile_failure(self):
        result = classify(verification("SyntaxError: invalid syntax"), changed_files=["a.py"])
        self.assertEqual(result["category"], "compile_failure")

    def test_test_failure(self):
        result = classify(verification("AssertionError: expected 2 got 3"), changed_files=["a.py"])
        self.assertEqual(result["category"], "test_failure")

    def test_timeout_switches_provider(self):
        result = classify(verification("TimeoutExpired", returncode=124), changed_files=["a.py"])
        self.assertEqual(result["category"], "timeout")
        self.assertTrue(policy(result)["provider_switch"])

    def test_environment_failure(self):
        result = classify(verification("Permission denied"), changed_files=["a.py"])
        self.assertEqual(result["category"], "environment_failure")

    def test_regression_failure(self):
        result = classify(verification("snapshot mismatch against baseline"), changed_files=["ui.ts"])
        self.assertEqual(result["category"], "regression")
        self.assertEqual(policy(result)["priority"], "critical")

    def test_no_progress(self):
        result = classify(verification("opaque failure"), changed_files=[])
        self.assertEqual(result["category"], "no_progress")
        self.assertTrue(policy(result)["provider_switch"])

    def test_passed(self):
        result = classify({"status": "passed", "passed": True, "results": []}, changed_files=[])
        self.assertEqual(result["category"], "passed")
        self.assertEqual(policy(result)["action"], "continue")

    def test_no_verifier(self):
        result = classify(verification(status="no_verifier"), changed_files=[])
        self.assertEqual(result["category"], "environment_failure")
        self.assertEqual(result["recovery"], "synthesize_verifier")


if __name__ == "__main__":
    unittest.main()

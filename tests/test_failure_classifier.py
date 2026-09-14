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
    def test_no_history_starts_cleanly(self):
        result = classify(None)
        self.assertEqual(result["category"], "no_history")
        self.assertEqual(policy(result)["action"], "continue")

    def test_objective_no_progress_overrides_opaque_failure(self):
        result = classify(
            verification("opaque failure"),
            changed_files=["a.py"],
            progress={"status": "churn_without_verified_progress"},
        )
        self.assertEqual(result["category"], "no_progress")
        self.assertEqual(policy(result)["action"], "switch_strategy")

    def test_objective_regression_has_priority(self):
        result = classify(
            verification("opaque failure"),
            changed_files=["a.py"],
            progress={"status": "regression"},
        )
        self.assertEqual(result["category"], "regression")

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

    def test_explicit_external_secret_prerequisite(self):
        result = classify(
            verification("API key required: set OPENAI_API_KEY before running tests"),
            changed_files=["a.py"],
        )
        self.assertEqual(result["category"], "external_prerequisite")
        self.assertEqual(result["required_env"], ["OPENAI_API_KEY"])
        self.assertEqual(policy(result)["action"], "request_external_input")

    def test_unauthorized_without_explicit_env_name_is_not_user_input(self):
        result = classify(
            verification("401 unauthorized"),
            changed_files=["a.py"],
        )
        self.assertNotEqual(result["category"], "external_prerequisite")

    def test_env_name_without_required_signal_is_not_user_input(self):
        result = classify(
            verification("debug output mentions OPENAI_API_KEY"),
            changed_files=["a.py"],
        )
        self.assertNotEqual(result["category"], "external_prerequisite")

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

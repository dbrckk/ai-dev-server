from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from failure_loop import decide, failure_signature


def failed(log: str = "AssertionError: expected 1 got 2", provider: str = "p1", model: str = "m1"):
    return {
        "verification": {
            "status": "failed",
            "passed": False,
            "results": [{
                "command": ["pytest", "-q"],
                "returncode": 1,
                "passed": False,
                "log_tail": log,
            }],
        },
        "models": {
            "plan": {"provider": provider, "model": model},
            "implementation": [{"provider": provider, "model": model}],
            "review": {"provider": provider, "model": model},
        },
    }


class FailureLoopTests(unittest.TestCase):
    def test_same_failure_switches_strategy_after_two_rounds(self):
        decision = decide([failed(), failed(provider="p2", model="m2")])
        self.assertEqual(decision["action"], "switch_strategy")
        self.assertEqual(decision["repeated_failures"], 2)
        self.assertEqual(decision["avoid_providers"], ["p1", "p2"])
        self.assertEqual(decision["avoid_models"], ["m1", "m2"])

    def test_same_failure_stops_after_four_rounds(self):
        decision = decide([failed(), failed(), failed(), failed()])
        self.assertEqual(decision["action"], "stop")
        self.assertEqual(decision["repeated_failures"], 4)

    def test_different_failure_resets_consecutive_count(self):
        decision = decide([
            failed("AssertionError: expected 1 got 2"),
            failed("TypeError: missing argument"),
        ])
        self.assertEqual(decision["action"], "continue")
        self.assertEqual(decision["repeated_failures"], 1)

    def test_dynamic_temp_paths_and_shas_do_not_break_signature(self):
        a = failure_signature(failed(
            "failed at /tmp/work-a/cache abcdef1234567890"
        )["verification"])
        b = failure_signature(failed(
            "failed at /tmp/work-b/cache fedcba0987654321"
        )["verification"])
        self.assertEqual(a, b)

    def test_passing_verification_breaks_loop(self):
        rounds = [
            failed(),
            {
                "verification": {
                    "status": "passed",
                    "passed": True,
                    "results": [],
                },
                "models": {},
            },
        ]
        decision = decide(rounds)
        self.assertEqual(decision["action"], "continue")
        self.assertEqual(decision["repeated_failures"], 0)


if __name__ == "__main__":
    unittest.main()

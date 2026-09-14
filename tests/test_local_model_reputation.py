import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import local_model_reputation as rep
import local_model_benchmark as bench


class LocalModelReputationTests(unittest.TestCase):
    def test_reputation_requires_minimum_samples(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rep.json"
            for _ in range(rep.MIN_SAMPLES - 1):
                rep.record(
                    path,
                    provider="ollama",
                    model="coder",
                    role="implementation",
                    success=True,
                    latency_seconds=1.0,
                )
            data = rep.load(path)
            self.assertEqual(
                rep.score(
                    data,
                    provider="ollama",
                    model="coder",
                    role="implementation",
                ),
                0.0,
            )

    def test_good_model_gets_positive_reputation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rep.json"
            for _ in range(5):
                rep.record(
                    path,
                    provider="ollama",
                    model="coder",
                    role="implementation",
                    success=True,
                    latency_seconds=1.0,
                )
            score = rep.score(
                rep.load(path),
                provider="ollama",
                model="coder",
                role="implementation",
            )
            self.assertGreater(score, 0.0)
            self.assertLessEqual(score, rep.MAX_BONUS)

    def test_protocol_failures_reduce_reputation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rep.json"
            for index in range(5):
                rep.record(
                    path,
                    provider="ollama",
                    model="coder",
                    role="implementation",
                    success=index >= 2,
                    latency_seconds=1.0,
                    protocol_failure=index < 2,
                )
            data = rep.load(path)
            score = rep.score(
                data,
                provider="ollama",
                model="coder",
                role="implementation",
            )
            self.assertLess(score, rep.MAX_BONUS)

    def test_verified_success_dominates_after_minimum_samples(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rep.json"
            for _ in range(5):
                rep.record(
                    path,
                    provider="ollama",
                    model="coder",
                    role="implementation",
                    success=True,
                    latency_seconds=1.0,
                )
            for outcome in [False, False, False]:
                rep.record_verified_outcome(
                    path,
                    provider="ollama",
                    model="coder",
                    role="implementation",
                    verified_success=outcome,
                )
            score = rep.score(
                rep.load(path),
                provider="ollama",
                model="coder",
                role="implementation",
            )
            self.assertLess(score, 0.0)

    def test_verified_success_can_rehabilitate_model(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rep.json"
            for _ in range(5):
                rep.record(
                    path,
                    provider="ollama",
                    model="coder",
                    role="implementation",
                    success=True,
                    latency_seconds=1.0,
                )
            for outcome in [True, True, True, True]:
                rep.record_verified_outcome(
                    path,
                    provider="ollama",
                    model="coder",
                    role="implementation",
                    verified_success=outcome,
                )
            score = rep.score(
                rep.load(path),
                provider="ollama",
                model="coder",
                role="implementation",
            )
            self.assertGreater(score, 0.0)

    def test_benchmark_bonus_is_bounded(self):
        data = {
            "ollama|great": {"score": 100.0},
            "ollama|bad": {"score": 0.0},
        }
        self.assertEqual(bench.routing_bonus(data, "ollama", "great"), 8.0)
        self.assertEqual(bench.routing_bonus(data, "ollama", "bad"), -8.0)


if __name__ == "__main__":
    unittest.main()

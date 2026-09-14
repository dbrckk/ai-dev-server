import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import local_model_specialization as spec


class LocalModelSpecializationTests(unittest.TestCase):
    def test_context_requires_minimum_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "specialization.json"
            for _ in range(spec.MIN_CONTEXT_SAMPLES - 1):
                spec.record_verified(
                    path,
                    provider="ollama",
                    model="coder",
                    role="implementation",
                    contexts=[("stack:python", 1.0)],
                    success=True,
                )
            result = spec.specialization_score(
                spec.load(path),
                provider="ollama",
                model="coder",
                role="implementation",
                contexts=[("stack:python", 1.0)],
            )
            self.assertEqual(result["score"], 0.0)

    def test_same_model_can_be_good_in_python_and_bad_in_flutter(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "specialization.json"
            for _ in range(6):
                spec.record_verified(
                    path,
                    provider="ollama",
                    model="coder",
                    role="implementation",
                    contexts=[("stack:python", 1.0)],
                    success=True,
                )
                spec.record_verified(
                    path,
                    provider="ollama",
                    model="coder",
                    role="implementation",
                    contexts=[("stack:flutter", 1.0)],
                    success=False,
                )
            data = spec.load(path)
            python_score = spec.specialization_score(
                data,
                provider="ollama",
                model="coder",
                role="implementation",
                contexts=[("stack:python", 1.0)],
            )["score"]
            flutter_score = spec.specialization_score(
                data,
                provider="ollama",
                model="coder",
                role="implementation",
                contexts=[("stack:flutter", 1.0)],
            )["score"]
            self.assertGreater(python_score, 0.0)
            self.assertLess(flutter_score, 0.0)

    def test_weighted_contexts_blend_specialization(self):
        data = {
            "ollama|coder|implementation|backend": {
                "samples": 8,
                "successes": 8,
                "ema_verified_success": 0.9,
            },
            "ollama|coder|implementation|stack:rust": {
                "samples": 8,
                "successes": 2,
                "ema_verified_success": 0.2,
            },
        }
        backend_heavy = spec.specialization_score(
            data,
            provider="ollama",
            model="coder",
            role="implementation",
            contexts=[("backend", 0.8), ("stack:rust", 0.2)],
        )["score"]
        rust_heavy = spec.specialization_score(
            data,
            provider="ollama",
            model="coder",
            role="implementation",
            contexts=[("backend", 0.2), ("stack:rust", 0.8)],
        )["score"]
        self.assertGreater(backend_heavy, rust_heavy)

    def test_score_is_bounded(self):
        data = {
            "ollama|coder|implementation|backend": {
                "samples": 100,
                "successes": 100,
                "ema_verified_success": 1.0,
            }
        }
        score = spec.specialization_score(
            data,
            provider="ollama",
            model="coder",
            role="implementation",
            contexts=[("backend", 1.0)],
        )["score"]
        self.assertLessEqual(score, spec.MAX_CONTEXT_BONUS)


if __name__ == "__main__":
    unittest.main()

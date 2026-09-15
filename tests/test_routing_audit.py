import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from routing_audit import append


class RoutingAuditTests(unittest.TestCase):
    def test_audit_persists_explainable_decision_without_secrets(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "routing-audit.json"
            event = append(path, {
                "role": "implementation",
                "winner": "fast",
                "winner_model": "coder",
                "candidates": [{
                    "provider": "fast", "model": "coder", "score": 90,
                    "components": {"latency": 12, "runtime_reliability": 8},
                }],
                "rejected": [{"provider": "broken", "reason": "circuit_breaker_open"}],
                "key": "must-not-persist",
                "prompt": "must-not-persist",
            }, now=100)
            self.assertEqual(event["winner"], "fast")
            raw = path.read_text()
            self.assertNotIn("must-not-persist", raw)
            data = json.loads(raw)
            self.assertEqual(data["events"][0]["rejected"][0]["reason"], "circuit_breaker_open")

    def test_audit_is_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "routing-audit.json"
            for index in range(520):
                append(path, {"role": "tests", "winner": str(index)}, now=index)
            data = json.loads(path.read_text())
            self.assertEqual(len(data["events"]), 512)
            self.assertEqual(data["events"][0]["winner"], "8")


if __name__ == "__main__":
    unittest.main()

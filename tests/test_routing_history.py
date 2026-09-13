from pathlib import Path
import tempfile
import unittest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from routing_history import learned_weights, load, record, weighted_total


class RoutingHistoryTests(unittest.TestCase):
    def test_history_is_bounded_and_sanitized(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "routing-history.json"
            for i in range(510):
                record(
                    path,
                    kind="provider",
                    name="p",
                    role="product",
                    score={"total": 10.0, "components": {"priority": 10.0}},
                    success=(i % 2 == 0),
                    duration_seconds=1.0,
                )
            self.assertEqual(len(load(path)), 500)

    def test_learning_adjusts_weights_conservatively(self):
        events = []
        for _ in range(5):
            events.append({
                "kind":"provider","name":"fast","role":"product","success":True,
                "duration_seconds":1.0,
                "score":{"total":12.0,"components":{"priority":10.0,"latency":8.0,"reliability":10.0,"free":20.0}},
            })
        for _ in range(5):
            events.append({
                "kind":"provider","name":"slow","role":"product","success":False,
                "duration_seconds":10.0,
                "score":{"total":12.0,"components":{"priority":10.0,"latency":-8.0,"reliability":-10.0,"free":20.0}},
            })
        weights = learned_weights(events, kind="provider", role="product")
        self.assertGreater(weights["latency"], 1.0)
        self.assertGreater(weights["reliability"], 1.0)
        self.assertGreaterEqual(min(weights.values()), 0.75)
        self.assertLessEqual(max(weights.values()), 1.25)

    def test_weighted_total_applies_component_weights(self):
        total = weighted_total({"priority":100.0,"latency":10.0},{"priority":1.0,"latency":0.5})
        self.assertEqual(total,105.0)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from provider_runtime_reliability import summarize, routing_bonus


class ProviderRuntimeReliabilityTests(unittest.TestCase):
    def test_reliable_route_gets_positive_bonus(self):
        report = summarize({"workers": [
            {"provider": "p", "model": "m", "classification": "completed"}
            for _ in range(8)
        ]})
        self.assertGreater(routing_bonus(report, "p", "m"), 0)

    def test_unstable_route_gets_negative_bonus(self):
        report = summarize({"workers": [
            {"provider": "p", "model": "m", "classification": "crashed"}
            for _ in range(8)
        ]})
        self.assertLess(routing_bonus(report, "p", "m"), 0)

    def test_sparse_evidence_has_bounded_influence(self):
        report = summarize({"workers": [
            {"provider": "p", "model": "m", "classification": "crashed"}
        ]})
        self.assertGreater(routing_bonus(report, "p", "m"), -2.0)

    def test_admission_slot_events_do_not_pollute_provider_reputation(self):
        report = summarize({"workers": [
            {"provider": "__admission_slot__", "model": "", "classification": "orphaned"}
        ]})
        self.assertFalse(report["routes"])


if __name__ == "__main__":
    unittest.main()

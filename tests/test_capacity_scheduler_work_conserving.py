import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from capacity_scheduler import ProviderCapacity, allocate


class WorkConservingCapacityTests(unittest.TestCase):
    def test_finite_capacity_is_redistributed_when_peer_hits_cap(self):
        providers = [ProviderCapacity("free", 1000, unmetered=False)]
        report = allocate([
            {"id": "small", "requested_tokens": 100, "priority": 100},
            {"id": "large", "requested_tokens": 1000, "priority": 1},
        ], providers, critical_reserve_ratio=0.0)
        by_id = {row["id"]: row for row in report["projects"]}
        self.assertEqual(by_id["small"]["token_envelope"], 100)
        self.assertEqual(by_id["large"]["token_envelope"], 900)
        self.assertEqual(report["summary"]["allocated_tokens"], 1000)

    def test_reserved_capacity_is_not_spent_by_ordinary_projects(self):
        providers = [ProviderCapacity("free", 1000, unmetered=False)]
        report = allocate([
            {"id": "ordinary", "requested_tokens": 1000, "priority": 100},
        ], providers, critical_reserve_ratio=0.2)
        self.assertEqual(report["projects"][0]["token_envelope"], 800)
        self.assertEqual(report["critical_reserve_tokens"], 200)

    def test_critical_project_can_consume_unused_ordinary_pool(self):
        providers = [ProviderCapacity("free", 1000, unmetered=False)]
        report = allocate([
            {
                "id": "critical",
                "requested_tokens": 1000,
                "priority": 50,
                "phase": "verification",
            },
        ], providers, critical_reserve_ratio=0.2)
        self.assertEqual(report["projects"][0]["token_envelope"], 1000)

    def test_redistribution_respects_pause_stagnation_caps_and_total_capacity(self):
        providers = [ProviderCapacity("free", 1000, unmetered=False)]
        report = allocate([
            {
                "id": "paused",
                "requested_tokens": 900,
                "priority": 100,
                "capacity_paused": True,
            },
            {
                "id": "capped",
                "requested_tokens": 500,
                "priority": 90,
                "stagnation_multiplier": 0.2,
            },
            {"id": "runner", "requested_tokens": 1000, "priority": 10},
        ], providers, critical_reserve_ratio=0.0)
        by_id = {row["id"]: row for row in report["projects"]}
        self.assertEqual(by_id["paused"]["token_envelope"], 0)
        self.assertEqual(by_id["capped"]["token_envelope"], 100)
        self.assertEqual(by_id["runner"]["token_envelope"], 900)
        self.assertEqual(report["summary"]["allocated_tokens"], 1000)


if __name__ == "__main__":
    unittest.main()

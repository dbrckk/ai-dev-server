import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from capacity_scheduler import ProviderCapacity, allocate, provider_capacities


class CapacitySchedulerTests(unittest.TestCase):
    def test_unmetered_capacity_removes_token_constraint(self):
        providers = [
            ProviderCapacity("ollama:qwen", None, unmetered=True),
            ProviderCapacity("omniroute", 1_000_000, unmetered=False),
        ]
        report = allocate([
            {"id": "a", "requested_tokens": 900_000, "priority": 50},
            {"id": "b", "requested_tokens": 900_000, "priority": 50},
        ], providers)
        self.assertTrue(report["has_unmetered_capacity"])
        self.assertEqual([p["token_envelope"] for p in report["projects"]], [900_000, 900_000])
        self.assertFalse(any(p["constrained"] for p in report["projects"]))

    def test_critical_project_can_use_reserved_capacity(self):
        providers = [ProviderCapacity("omniroute", 1_000, unmetered=False)]
        report = allocate([
            {"id": "work", "requested_tokens": 1_000, "priority": 50, "phase": "implementation"},
            {"id": "verify", "requested_tokens": 1_000, "priority": 50, "phase": "verification"},
        ], providers, critical_reserve_ratio=0.20)
        by_id = {row["id"]: row for row in report["projects"]}
        self.assertGreater(by_id["verify"]["token_envelope"], by_id["work"]["token_envelope"])
        self.assertEqual(report["critical_reserve_tokens"], 200)

    def test_provider_order_prefers_unmetered_then_free_then_paid(self):
        providers = [
            ProviderCapacity("paid", 10_000, paid=True, free_preferred=False),
            ProviderCapacity("free", 10_000, paid=False, free_preferred=True),
            ProviderCapacity("local", None, unmetered=True),
        ]
        report = allocate([{"id": "p", "requested_tokens": 100}], providers)
        order = [row["name"] for row in report["projects"][0]["provider_order"]]
        self.assertEqual(order, ["local", "free", "paid"])

    def test_terminal_projects_are_excluded(self):
        providers = [ProviderCapacity("free", 10_000)]
        report = allocate([
            {"id": "done", "status": "complete", "requested_tokens": 100},
            {"id": "blocked", "status": "blocked", "requested_tokens": 100},
            {"id": "active", "status": "running", "requested_tokens": 100},
        ], providers)
        self.assertEqual([row["id"] for row in report["projects"]], ["active"])

    def test_parser_normalizes_provider_capacity_rows(self):
        rows = provider_capacities([
            {"name": "local", "unmetered": True},
            {"name": "pool", "available_tokens": 500, "free_preferred": True},
            {"name": "paid", "available_tokens": 100, "paid": True, "free_preferred": False},
        ])
        self.assertEqual(len(rows), 3)
        self.assertIsNone(rows[0].available_tokens)
        self.assertEqual(rows[1].available_tokens, 500)
        self.assertTrue(rows[2].paid)


if __name__ == "__main__":
    unittest.main()

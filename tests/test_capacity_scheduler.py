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


    def test_provider_peers_rank_by_runtime_evidence(self):
        providers = [
            ProviderCapacity("slow-unreliable", 100_000, reliability=0.2, latency_ms=4000),
            ProviderCapacity("fast-reliable", 100_000, reliability=0.95, latency_ms=100),
        ]
        report = allocate([{"id": "p", "requested_tokens": 100}], providers)
        order = [row["name"] for row in report["projects"][0]["provider_order"]]
        self.assertEqual(order, ["fast-reliable", "slow-unreliable"])
        self.assertGreater(
            report["projects"][0]["provider_order"][0]["adaptive_score"],
            report["projects"][0]["provider_order"][1]["adaptive_score"],
        )

    def test_adaptive_score_does_not_override_free_first_policy(self):
        providers = [
            ProviderCapacity(
                "paid-excellent", 1_000_000, paid=True, free_preferred=False,
                reliability=1.0, latency_ms=1, cost_per_million_tokens=0.01,
            ),
            ProviderCapacity(
                "free-poor", 1_000, paid=False, free_preferred=True,
                reliability=0.1, latency_ms=5000,
            ),
        ]
        report = allocate([{"id": "p", "requested_tokens": 100}], providers)
        order = [row["name"] for row in report["projects"][0]["provider_order"]]
        self.assertEqual(order, ["free-poor", "paid-excellent"])

    def test_parser_normalizes_adaptive_provider_metrics(self):
        rows = provider_capacities([{
            "name": "provider",
            "available_tokens": 500,
            "reliability": 1.5,
            "latency_ms": -20,
            "cost_per_million_tokens": -1,
        }])
        self.assertEqual(rows[0].reliability, 1.0)
        self.assertEqual(rows[0].latency_ms, 0.0)
        self.assertEqual(rows[0].cost_per_million_tokens, 0.0)

    def test_health_history_supplies_smoothed_reliability(self):
        rows = provider_capacities(
            [{"name": "provider", "available_tokens": 1000}],
            health_data={"provider": {"successes": 8, "failures": 2}},
        )
        self.assertAlmostEqual(rows[0].reliability, 0.75)

    def test_explicit_reliability_overrides_health_history(self):
        rows = provider_capacities(
            [{"name": "provider", "available_tokens": 1000, "reliability": 0.9}],
            health_data={"provider": {"successes": 0, "failures": 10}},
        )
        self.assertEqual(rows[0].reliability, 0.9)

    def test_sparse_health_history_is_bayesian_smoothed(self):
        rows = provider_capacities(
            [{"name": "provider", "available_tokens": 1000}],
            health_data={"provider": {"successes": 1, "failures": 0}},
        )
        self.assertAlmostEqual(rows[0].reliability, 2 / 3)

    def test_health_history_supplies_observed_latency(self):
        rows = provider_capacities(
            [{"name": "provider", "available_tokens": 1000}],
            health_data={"provider": {
                "successes": 5, "failures": 1, "latency_ms_ema": 275.5,
            }},
        )
        self.assertEqual(rows[0].latency_ms, 275.5)

    def test_explicit_latency_overrides_health_history(self):
        rows = provider_capacities(
            [{"name": "provider", "available_tokens": 1000, "latency_ms": 50}],
            health_data={"provider": {
                "successes": 5, "failures": 1, "latency_ms_ema": 900,
            }},
        )
        self.assertEqual(rows[0].latency_ms, 50.0)

    def test_open_circuit_provider_is_excluded(self):
        rows = provider_capacities(
            [
                {"name": "broken", "available_tokens": 1000},
                {"name": "healthy", "available_tokens": 1000},
            ],
            health_data={
                "broken": {"opened_until": 200.0},
                "healthy": {"opened_until": 0.0},
            },
            now=100.0,
        )
        report = allocate([{"id": "p", "requested_tokens": 100}], rows)
        order = [row["name"] for row in report["projects"][0]["provider_order"]]
        self.assertEqual(order, ["healthy"])

    def test_provider_returns_after_circuit_cooldown(self):
        rows = provider_capacities(
            [{"name": "recovered", "available_tokens": 1000}],
            health_data={"recovered": {"opened_until": 200.0}},
            now=201.0,
        )
        report = allocate([{"id": "p", "requested_tokens": 100}], rows)
        self.assertEqual(
            [row["name"] for row in report["projects"][0]["provider_order"]],
            ["recovered"],
        )

    def test_open_circuit_capacity_is_not_counted(self):
        rows = provider_capacities(
            [
                {"name": "broken", "available_tokens": 900},
                {"name": "healthy", "available_tokens": 100},
            ],
            health_data={"broken": {"opened_until": 200.0}},
            now=100.0,
        )
        report = allocate(
            [{"id": "p", "requested_tokens": 1000}],
            rows,
            critical_reserve_ratio=0.0,
        )
        self.assertEqual(report["finite_capacity_tokens"], 100)
        self.assertEqual(report["projects"][0]["token_envelope"], 100)

    def test_capacity_pressure_increases_scarce_capacity_share(self):
        providers = [ProviderCapacity("omniroute", 1000, unmetered=False)]
        report = allocate([
            {
                "id": "hot",
                "requested_tokens": 1000,
                "priority": 50,
                "capacity_pressure": 1.0,
            },
            {
                "id": "cold",
                "requested_tokens": 1000,
                "priority": 50,
                "capacity_pressure": 0.0,
            },
        ], providers, critical_reserve_ratio=0.0)
        by_id = {row["id"]: row for row in report["projects"]}
        self.assertGreater(
            by_id["hot"]["token_envelope"],
            by_id["cold"]["token_envelope"],
        )



    def test_verified_efficiency_changes_scarce_capacity_share(self):
        providers = [ProviderCapacity("omniroute", 1000, unmetered=False)]
        report = allocate([
            {
                "id": "efficient",
                "requested_tokens": 1000,
                "priority": 50,
                "efficiency_multiplier": 1.25,
            },
            {
                "id": "stagnant",
                "requested_tokens": 1000,
                "priority": 50,
                "efficiency_multiplier": 0.75,
            },
        ], providers, critical_reserve_ratio=0.0)
        by_id = {row["id"]: row for row in report["projects"]}
        self.assertGreater(
            by_id["efficient"]["token_envelope"],
            by_id["stagnant"]["token_envelope"],
        )



    def test_stagnation_throttle_reduces_capacity_share(self):
        providers = [ProviderCapacity("omniroute", 1000, unmetered=False)]
        report = allocate([
            {
                "id": "healthy",
                "requested_tokens": 1000,
                "priority": 50,
                "stagnation_multiplier": 1.0,
            },
            {
                "id": "stagnant",
                "requested_tokens": 1000,
                "priority": 50,
                "stagnation_multiplier": 0.60,
            },
        ], providers, critical_reserve_ratio=0.0)
        by_id = {row["id"]: row for row in report["projects"]}
        self.assertGreater(
            by_id["healthy"]["token_envelope"],
            by_id["stagnant"]["token_envelope"],
        )

    def test_paused_stagnant_project_gets_zero_envelope(self):
        providers = [ProviderCapacity("omniroute", 1000, unmetered=False)]
        report = allocate([
            {
                "id": "paused",
                "requested_tokens": 1000,
                "priority": 100,
                "capacity_paused": True,
                "stagnation_multiplier": 0.0,
                "stagnation_level": "pause",
            },
            {
                "id": "active",
                "requested_tokens": 1000,
                "priority": 1,
            },
        ], providers, critical_reserve_ratio=0.0)
        by_id = {row["id"]: row for row in report["projects"]}
        self.assertEqual(by_id["paused"]["token_envelope"], 0)
        self.assertTrue(by_id["paused"]["constrained"])
        self.assertEqual(report["summary"]["paused_projects"], 1)



    def test_recovery_project_receives_bounded_nonzero_envelope(self):
        providers = [ProviderCapacity("omniroute", 10000, unmetered=False)]
        report = allocate([
            {
                "id": "recovery",
                "requested_tokens": 10000,
                "priority": 50,
                "capacity_paused": False,
                "stagnation_multiplier": 0.15,
                "recovery_active": True,
                "force_diversify": True,
            },
            {
                "id": "healthy",
                "requested_tokens": 10000,
                "priority": 50,
            },
        ], providers, critical_reserve_ratio=0.0)
        by_id = {row["id"]: row for row in report["projects"]}
        self.assertGreater(by_id["recovery"]["token_envelope"], 0)
        self.assertLess(
            by_id["recovery"]["token_envelope"],
            by_id["healthy"]["token_envelope"],
        )
        self.assertTrue(by_id["recovery"]["recovery_active"])



    def test_recovery_cap_applies_even_with_unmetered_provider(self):
        providers = [ProviderCapacity("local", None, unmetered=True)]
        report = allocate([
            {
                "id": "recovery",
                "requested_tokens": 10000,
                "stagnation_multiplier": 0.15,
                "recovery_active": True,
            }
        ], providers, critical_reserve_ratio=0.0)
        row = report["projects"][0]
        self.assertEqual(row["token_envelope"], 1500)
        self.assertTrue(row["constrained"])


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

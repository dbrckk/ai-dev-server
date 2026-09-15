import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import capacity_ledger as ledger


class CapacityLedgerTests(unittest.TestCase):
    def test_provider_capacity_cannot_be_double_reserved(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.json"
            first = ledger.reserve(
                path,
                project_id="a",
                provider="omniroute",
                estimated_tokens=700,
                provider_remaining_tokens=1000,
                now=10,
            )
            second = ledger.reserve(
                path,
                project_id="b",
                provider="omniroute",
                estimated_tokens=400,
                provider_remaining_tokens=1000,
                now=11,
            )
            self.assertTrue(first["admitted"])
            self.assertFalse(second["admitted"])
            self.assertEqual(second["reason"], "provider_capacity_reserved")

    def test_project_envelope_is_enforced_across_providers(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.json"
            first = ledger.reserve(
                path,
                project_id="a",
                provider="local",
                estimated_tokens=600,
                provider_remaining_tokens=None,
                project_envelope_tokens=1000,
                now=10,
            )
            second = ledger.reserve(
                path,
                project_id="a",
                provider="omniroute",
                estimated_tokens=500,
                provider_remaining_tokens=5000,
                project_envelope_tokens=1000,
                now=11,
            )
            self.assertTrue(first["admitted"])
            self.assertFalse(second["admitted"])
            self.assertEqual(second["reason"], "project_envelope_exhausted")

    def test_settle_releases_unused_reservation_and_records_actual_usage(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.json"
            reservation = ledger.reserve(
                path,
                project_id="a",
                provider="omniroute",
                estimated_tokens=800,
                provider_remaining_tokens=1000,
                now=10,
            )
            result = ledger.settle(
                path,
                reservation["reservation_id"],
                actual_tokens=300,
                now=11,
            )
            data = ledger.load(path)
            self.assertTrue(result["settled"])
            self.assertEqual(result["released_tokens"], 500)
            self.assertEqual(ledger.reserved_tokens(data), 0)
            self.assertEqual(ledger.consumed_tokens(data, project_id="a"), 300)

    def test_release_on_failed_call_returns_full_reservation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.json"
            reservation = ledger.reserve(
                path,
                project_id="a",
                provider="omniroute",
                estimated_tokens=800,
                provider_remaining_tokens=1000,
                now=10,
            )
            result = ledger.release(path, reservation["reservation_id"], now=11)
            self.assertTrue(result["released"])
            self.assertEqual(result["released_tokens"], 800)
            self.assertEqual(ledger.snapshot(path, now=12)["reserved_tokens"], 0)

    def test_expired_reservations_are_reaped_before_new_claim(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.json"
            first = ledger.reserve(
                path,
                project_id="a",
                provider="omniroute",
                estimated_tokens=900,
                provider_remaining_tokens=1000,
                ttl_seconds=30,
                now=10,
            )
            self.assertTrue(first["admitted"])
            second = ledger.reserve(
                path,
                project_id="b",
                provider="omniroute",
                estimated_tokens=900,
                provider_remaining_tokens=1000,
                ttl_seconds=30,
                now=50,
            )
            self.assertTrue(second["admitted"])
            self.assertEqual(second["reaped"], 1)


    def test_release_project_releases_only_owned_reservations(self):
        from capacity_ledger import release_project
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.json"
            reserve(path, project_id="a", provider="p", estimated_tokens=10,
                    provider_remaining_tokens=100, now=100)
            reserve(path, project_id="a", provider="q", estimated_tokens=20,
                    provider_remaining_tokens=100, now=100)
            reserve(path, project_id="b", provider="p", estimated_tokens=30,
                    provider_remaining_tokens=100, now=100)
            result = release_project(path, "a", now=101)
            self.assertEqual(result["reservations_released"], 2)
            self.assertEqual(result["released_tokens"], 30)
            remaining = load(path)["reservations"]
            self.assertEqual(len(remaining), 1)
            self.assertEqual(next(iter(remaining.values()))["project_id"], "b")


    def test_atomic_preemption_transfer_releases_victim_and_leases_contender(self):
        from capacity_ledger import transfer_project_reservations
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.json"
            reserve(path, project_id="low", provider="p", estimated_tokens=100,
                    provider_remaining_tokens=1000, now=100)
            result = transfer_project_reservations(
                path,
                victim_project_id="low",
                contender_project_id="high",
                reserve_tokens=80,
                now=101,
            )
            self.assertTrue(result["transferred"])
            data = load(path)
            self.assertEqual(reserved_tokens(data, project_id="low"), 0)
            self.assertEqual(reserved_tokens(data, project_id="high"), 80)
            lease = next(iter(data["reservations"].values()))
            self.assertEqual(lease["kind"], "preemption_admission_lease")
            self.assertEqual(lease["victim_project_id"], "low")



    def test_claim_preemption_lease_converts_lease_to_worker_reservation(self):
        from capacity_ledger import transfer_project_reservations, claim_preemption_lease
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.json"
            reserve(path, project_id="low", provider="p", estimated_tokens=100,
                    provider_remaining_tokens=1000, now=100)
            transfer = transfer_project_reservations(
                path,
                victim_project_id="low",
                contender_project_id="high",
                reserve_tokens=80,
                now=101,
            )
            claim = claim_preemption_lease(path, "high", now=102, ttl_seconds=600)
            self.assertTrue(claim["claimed"])
            self.assertEqual(claim["reservation_id"], transfer["lease_reservation_id"])
            row = load(path)["reservations"][claim["reservation_id"]]
            self.assertEqual(row["kind"], "worker_capacity_reservation")
            self.assertEqual(row["claimed_at"], 102)
            self.assertEqual(row["expires_at"], 702)

    def test_expired_preemption_lease_cannot_be_claimed(self):
        from capacity_ledger import transfer_project_reservations, claim_preemption_lease
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.json"
            transfer_project_reservations(
                path,
                victim_project_id="low",
                contender_project_id="high",
                reserve_tokens=80,
                ttl_seconds=30,
                now=100,
            )
            claim = claim_preemption_lease(path, "high", now=131)
            self.assertFalse(claim["claimed"])
            self.assertEqual(claim["reason"], "preemption_lease_missing")
            self.assertFalse(load(path)["reservations"])



if __name__ == "__main__":
    unittest.main()

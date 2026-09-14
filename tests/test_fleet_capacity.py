import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import fleet_capacity
import provider_monthly_quota
from provider_router import ProviderSpec


class FleetCapacityTests(unittest.TestCase):
    def test_project_demand_uses_explicit_capacity_request(self):
        with patch("fleet_capacity.collect", return_value={"projects": [
            {"id": "a", "runtime_status": "running"}
        ]}), patch("fleet_capacity.matrix", return_value=[
            {"id": "a", "capacity_request_tokens": 12345, "priority": 70}
        ]), patch("fleet_capacity._runtime_state", return_value={"phase": "verification"}):
            rows = fleet_capacity._project_rows(Path("out"), Path("requests"))

        self.assertEqual(rows[0]["requested_tokens"], 12345)
        self.assertEqual(rows[0]["phase"], "verification")
        self.assertEqual(rows[0]["priority"], 70)

    def test_project_demand_uses_configured_call_upper_bound(self):
        with patch("fleet_capacity.collect", return_value={"projects": [
            {"id": "a", "runtime_status": "running"}
        ]}), patch("fleet_capacity.matrix", return_value=[
            {"id": "a", "max_calls": 3}
        ]), patch("fleet_capacity._runtime_state", return_value={}):
            rows = fleet_capacity._project_rows(Path("out"), Path("requests"))

        self.assertEqual(
            rows[0]["requested_tokens"],
            3 * fleet_capacity.DEFAULT_MAX_TOKENS_PER_MODEL_CALL,
        )

    def test_known_monthly_quota_is_reported_as_remaining_capacity(self):
        provider = ProviderSpec(
            "omniroute",
            "http://127.0.0.1:20128/v1",
            "",
            "auto",
            monthly_token_quota=1000,
        )
        quota_data = {
            "schema": 1,
            "months": {
                fleet_capacity.quota_status.__globals__["month_key"](): {
                    "omniroute": {"total_tokens": 250}
                }
            },
        }
        with patch("fleet_capacity.load_providers", return_value=(provider,)), patch(
            "fleet_capacity.load_monthly_quota", return_value=quota_data
        ), patch.dict(
            fleet_capacity.os.environ,
            {"STUDIO_PROVIDER_MONTHLY_QUOTA_PATH": "quota.json"},
            clear=False,
        ):
            providers = fleet_capacity._provider_rows()

        self.assertEqual(providers[0].available_tokens, 750)
        self.assertFalse(providers[0].unmetered)


    def test_provider_capacity_subtracts_inflight_reservations(self):
        provider = ProviderSpec(
            "omniroute",
            "http://127.0.0.1:20128/v1",
            "",
            "auto",
            monthly_token_quota=1000,
        )
        quota_data = {
            "schema": 1,
            "months": {
                fleet_capacity.quota_status.__globals__["month_key"](): {
                    "omniroute": {"total_tokens": 250}
                }
            },
        }
        with patch("fleet_capacity.load_providers", return_value=(provider,)), patch(
            "fleet_capacity.load_monthly_quota", return_value=quota_data
        ), patch.dict(
            fleet_capacity.os.environ,
            {"STUDIO_PROVIDER_MONTHLY_QUOTA_PATH": "quota.json"},
            clear=False,
        ):
            providers = fleet_capacity._provider_rows(
                reservations_by_provider={"omniroute": 200}
            )

        self.assertEqual(providers[0].available_tokens, 550)

    def test_project_pressure_uses_committed_tokens_against_previous_envelope(self):
        previous = {
            "projects": [
                {"id": "a", "token_envelope": 1000}
            ]
        }
        usage = {
            "a": {
                "reserved_tokens": 100,
                "consumed_tokens": 750,
                "committed_tokens": 850,
            }
        }
        with patch("fleet_capacity.collect", return_value={"projects": [
            {"id": "a", "runtime_status": "running"}
        ]}), patch("fleet_capacity.matrix", return_value=[
            {"id": "a", "capacity_request_tokens": 1000, "priority": 50}
        ]), patch("fleet_capacity._runtime_state", return_value={}):
            rows = fleet_capacity._project_rows(
                Path("out"),
                Path("requests"),
                ledger_usage=usage,
                previous_plan=previous,
            )

        self.assertEqual(rows[0]["capacity_pressure"], 0.85)
        self.assertEqual(rows[0]["committed_tokens"], 850)
        self.assertEqual(rows[0]["previous_envelope_tokens"], 1000)



    def test_explicit_fleet_quota_path_is_used_for_provider_capacity(self):
        provider = ProviderSpec(
            "omniroute",
            "http://127.0.0.1:20128/v1",
            "",
            "auto",
            monthly_token_quota=1000,
        )
        with tempfile.TemporaryDirectory() as td:
            quota_path = Path(td) / "provider-monthly-quota.json"
            provider_monthly_quota.record(
                quota_path,
                "omniroute",
                prompt_tokens=200,
                completion_tokens=100,
            )
            with patch("fleet_capacity.load_providers", return_value=(provider,)):
                providers = fleet_capacity._provider_rows(quota_path=quota_path)

        self.assertEqual(providers[0].available_tokens, 700)


    def test_persist_writes_machine_readable_plan(self):
        report = {
            "schema": 1,
            "projects": [],
            "summary": {"active_projects": 0},
        }
        with tempfile.TemporaryDirectory() as td, patch(
            "fleet_capacity.plan", return_value=report
        ):
            root = Path(td)
            result = fleet_capacity.persist(root, "requests")
            target = root / "capacity-plan.json"
            self.assertTrue(target.is_file())
            self.assertEqual(result, report)
            self.assertIn('"schema": 1', target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

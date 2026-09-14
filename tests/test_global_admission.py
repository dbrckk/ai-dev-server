import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from global_admission import decide, decision_for


class GlobalAdmissionTests(unittest.TestCase):
    def test_zero_capacity_is_deferred(self):
        report = decide([{"id": "a", "requested_tokens": 10000, "token_envelope": 0}])
        row = decision_for(report, "a")
        self.assertFalse(row["admitted"])
        self.assertEqual(row["reason"], "capacity_unavailable")

    def test_recovery_probe_is_admitted_with_small_bounded_budget(self):
        report = decide([{
            "id": "a",
            "requested_tokens": 100000,
            "token_envelope": 15000,
            "recovery_active": True,
        }])
        row = decision_for(report, "a")
        self.assertTrue(row["admitted"])
        self.assertEqual(row["action"], "admit_recovery")

    def test_critical_project_bypasses_standard_slot_saturation(self):
        projects = [
            {"id": "critical", "critical": True, "requested_tokens": 20000, "token_envelope": 20000},
            {"id": "a", "requested_tokens": 20000, "token_envelope": 20000},
            {"id": "b", "requested_tokens": 20000, "token_envelope": 20000},
        ]
        report = decide(projects, max_standard_admissions=1)
        self.assertTrue(decision_for(report, "critical")["admitted"])
        admitted_standard = [
            row for row in report["decisions"]
            if row["action"] == "admit"
        ]
        self.assertEqual(len(admitted_standard), 1)

    def test_ranking_prefers_priority_success_and_efficiency(self):
        projects = [
            {
                "id": "strong",
                "priority": 80,
                "predicted_success_probability": 0.8,
                "efficiency_multiplier": 1.2,
                "requested_tokens": 20000,
                "token_envelope": 20000,
            },
            {
                "id": "weak",
                "priority": 40,
                "predicted_success_probability": 0.3,
                "efficiency_multiplier": 0.8,
                "requested_tokens": 20000,
                "token_envelope": 20000,
            },
        ]
        report = decide(projects, max_standard_admissions=1)
        self.assertTrue(decision_for(report, "strong")["admitted"])
        self.assertFalse(decision_for(report, "weak")["admitted"])

    def test_tiny_ordinary_envelope_is_deferred(self):
        report = decide([{
            "id": "a",
            "requested_tokens": 100000,
            "token_envelope": 4000,
        }])
        row = decision_for(report, "a")
        self.assertFalse(row["admitted"])
        self.assertEqual(row["reason"], "insufficient_useful_round_capacity")


if __name__ == "__main__":
    unittest.main()

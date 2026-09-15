import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from preemption_controller import plan


class PreemptionControllerTests(unittest.TestCase):
    def _plan(self, victim_priority=20, contender_priority=95):
        return {
            "projects": [
                {"id": "low", "status": "running", "priority": victim_priority},
                {"id": "high", "status": "queued", "priority": contender_priority},
            ],
            "admission": {
                "decisions": [
                    {"id": "low", "admitted": True, "score": 0.20, "critical": False, "recovery_active": False},
                    {"id": "high", "admitted": False, "score": 0.75, "reason": "fleet_admission_slots_saturated"},
                ]
            },
        }

    def test_high_value_contender_preempts_safe_checkpointed_victim(self):
        report = plan(self._plan(), {
            "low": {"checkpoint_valid": True, "checkpoint_phase": "verified"},
        })
        self.assertEqual(report["summary"]["preempt"], 1)
        self.assertEqual(report["actions"][0]["victim_id"], "low")
        self.assertEqual(report["actions"][0]["contender_id"], "high")

    def test_missing_checkpoint_blocks_preemption(self):
        report = plan(self._plan(), {
            "low": {"checkpoint_valid": False, "checkpoint_phase": None},
        })
        self.assertEqual(report["summary"]["preempt"], 0)
        self.assertEqual(report["actions"][0]["action"], "keep_deferred")

    def test_unverified_checkpoint_phase_blocks_preemption(self):
        report = plan(self._plan(), {
            "low": {"checkpoint_valid": True, "checkpoint_phase": "implemented"},
        })
        self.assertEqual(report["summary"]["preempt"], 0)

    def test_small_priority_delta_blocks_preemption(self):
        report = plan(self._plan(victim_priority=70, contender_priority=80), {
            "low": {"checkpoint_valid": True, "checkpoint_phase": "verified"},
        })
        self.assertEqual(report["summary"]["preempt"], 0)

    def test_critical_victim_is_never_preempted(self):
        value = self._plan()
        value["admission"]["decisions"][0]["critical"] = True
        report = plan(value, {
            "low": {"checkpoint_valid": True, "checkpoint_phase": "verified"},
        })
        self.assertEqual(report["summary"]["preempt"], 0)


if __name__ == "__main__":
    unittest.main()

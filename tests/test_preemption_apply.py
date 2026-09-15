import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from capacity_ledger import reserve, load
from execution_checkpoint import new, advance, save
from preemption_apply import execute


class PreemptionApplyTests(unittest.TestCase):
    def _fixture(self, root: Path, phase="verified"):
        victim = root / "low" / ".autonomy"
        victim.mkdir(parents=True, exist_ok=True)
        checkpoint = new("low", "generic", "a" * 40)
        checkpoint = advance(checkpoint, round_index=2, phase=phase)
        save(victim / "execution-checkpoint.json", checkpoint)
        reserve(
            root / "capacity-ledger.json",
            project_id="low",
            provider="free",
            estimated_tokens=12000,
            provider_remaining_tokens=100000,
            project_envelope_tokens=50000,
            now=1000.0,
        )
        plan = {
            "projects": [
                {"id": "low", "requested_tokens": 12000, "token_envelope": 12000},
                {"id": "high", "requested_tokens": 10000, "token_envelope": 8000},
            ],
            "preemption": {
                "actions": [{
                    "action": "preempt",
                    "victim_id": "low",
                    "contender_id": "high",
                }]
            }
        }
        (root / "capacity-plan.json").write_text(json.dumps(plan))

    def test_dry_run_preserves_reservations(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._fixture(root)
            report = execute(root, apply=False, now=1000.0)
            self.assertEqual(report["results"][0]["status"], "dry_run")
            self.assertTrue(load(root / "capacity-ledger.json")["reservations"])

    def test_apply_releases_reservations_and_records_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._fixture(root)
            report = execute(root, apply=True, now=1000.0)
            self.assertEqual(report["preemptions_executed"], 1)
            ledger = load(root / "capacity-ledger.json")
            self.assertTrue(ledger["reservations"])
            lease = next(iter(ledger["reservations"].values()))
            self.assertEqual(lease["project_id"], "high")
            self.assertEqual(lease["kind"], "preemption_admission_lease")
            self.assertEqual(lease["reserved_tokens"], 8000)
            state = json.loads(
                (root / "low" / ".autonomy" / "preemption-state.json").read_text()
            )
            self.assertEqual(state["status"], "preempted")
            self.assertEqual(state["victim_checkpoint"]["phase"], "verified")
            self.assertEqual(state["transfer"]["released_tokens"], 12000)
            self.assertEqual(state["transfer"]["contender_project_id"], "high")

    def test_unsafe_checkpoint_blocks_apply(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._fixture(root, phase="implemented")
            report = execute(root, apply=True, now=1000.0)
            self.assertEqual(report["results"][0]["status"], "checkpoint_not_safe")
            self.assertTrue(load(root / "capacity-ledger.json")["reservations"])

    def test_cooldown_blocks_immediate_reverse_or_repeat_preemption(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._fixture(root)
            first = execute(root, apply=True, now=1000.0, cooldown_seconds=300)
            self.assertEqual(first["preemptions_executed"], 1)
            self._fixture(root)
            second = execute(root, apply=True, now=1100.0, cooldown_seconds=300)
            self.assertEqual(second["preemptions_executed"], 0)
            self.assertEqual(second["results"][0]["status"], "cooldown_active")


if __name__ == "__main__":
    unittest.main()

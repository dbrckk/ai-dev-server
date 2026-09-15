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
        victim.mkdir(parents=True)
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
            now=100.0,
        )
        plan = {
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
            report = execute(root, apply=False)
            self.assertEqual(report["results"][0]["status"], "dry_run")
            self.assertTrue(load(root / "capacity-ledger.json")["reservations"])

    def test_apply_releases_reservations_and_records_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._fixture(root)
            report = execute(root, apply=True)
            self.assertEqual(report["preemptions_executed"], 1)
            self.assertFalse(load(root / "capacity-ledger.json")["reservations"])
            state = json.loads(
                (root / "low" / ".autonomy" / "preemption-state.json").read_text()
            )
            self.assertEqual(state["status"], "preempted")
            self.assertEqual(state["victim_checkpoint"]["phase"], "verified")
            self.assertEqual(state["released"]["released_tokens"], 12000)

    def test_unsafe_checkpoint_blocks_apply(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._fixture(root, phase="implemented")
            report = execute(root, apply=True)
            self.assertEqual(report["results"][0]["status"], "checkpoint_not_safe")
            self.assertTrue(load(root / "capacity-ledger.json")["reservations"])


if __name__ == "__main__":
    unittest.main()

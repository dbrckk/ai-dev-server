import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import durable_state
import telemetry
import workflow_checkpoint
from task_lease import claim, heartbeat, release


class ResilienceSoakTests(unittest.TestCase):
    def test_repeated_state_checkpoint_lease_cycles_remain_bounded_and_clean(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state_path = root / "runtime-state.json"
            checkpoint_path = root / "workflow-checkpoints.json"
            telemetry_path = root / "telemetry.jsonl"
            lease_path = root / "task-leases.json"
            env = {
                "STUDIO_CHECKPOINT_PATH": str(checkpoint_path),
                "STUDIO_TELEMETRY_PATH": str(telemetry_path),
                "STUDIO_TASK_LEASE_PATH": str(lease_path),
            }

            cycles = max(1, int(os.environ.get("STUDIO_SOAK_CYCLES", "40")))
            with patch.dict(os.environ, env, clear=False):
                for index in range(cycles):
                    durable_state.save(
                        state_path,
                        {
                            "generation": index,
                            "status": "running" if index < cycles - 1 else "complete",
                        },
                    )
                    loaded = durable_state.load_recovering(state_path)
                    self.assertEqual(loaded["generation"], index)

                    key = workflow_checkpoint.operation_key(
                        "soak",
                        {"generation": index},
                    )
                    workflow_checkpoint.put(
                        key,
                        {"generation": index},
                        kind="soak",
                    )
                    self.assertEqual(
                        workflow_checkpoint.get(key),
                        {"generation": index},
                    )

                    task = {
                        "id": "task-soak",
                        "status": "running",
                    }
                    claim(
                        task,
                        owner="worker-soak",
                        lease_seconds=60,
                        now=float(index * 10),
                    )
                    heartbeat(
                        task,
                        owner="worker-soak",
                        token=task["lease_token"],
                        lease_seconds=60,
                        now=float(index * 10 + 1),
                    )
                    release(task)

                    telemetry.emit("soak_cycle", generation=index)

            final_state = durable_state.load(state_path)
            self.assertEqual(final_state["generation"], cycles - 1)
            self.assertEqual(final_state["status"], "complete")

            checkpoint_payload = json.loads(
                checkpoint_path.read_text(encoding="utf-8")
            )
            self.assertLessEqual(
                len(checkpoint_payload["entries"]),
                workflow_checkpoint.MAX_ENTRIES,
            )

            lease_payload = json.loads(lease_path.read_text(encoding="utf-8"))
            self.assertEqual(lease_payload["claims"], {})

            summary = telemetry.summarize(telemetry_path)
            self.assertEqual(summary["events"], cycles)
            self.assertEqual(summary["kinds"]["soak_cycle"], cycles)


if __name__ == "__main__":
    unittest.main()

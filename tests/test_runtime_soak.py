import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import persistent_quick_gate_cache as pqc
import workflow_checkpoint as wc
import telemetry


class RuntimeSoakTests(unittest.TestCase):
    def test_persistent_stores_remain_bounded_under_repeated_cycles(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env = {
                "STUDIO_QUICK_GATE_CACHE_PATH": str(root / "quick.json"),
                "STUDIO_CHECKPOINT_PATH": str(root / "checkpoint.json"),
                "STUDIO_TELEMETRY_PATH": str(root / "telemetry.jsonl"),
            }
            with patch.dict(os.environ, env, clear=False):
                quick_entries = {
                    f"q-{i}": {"passed": True, "logs": []}
                    for i in range(pqc.MAX_ENTRIES + 100)
                }
                pqc.save(quick_entries)
                self.assertEqual(len(pqc.load()), pqc.MAX_ENTRIES)

                for i in range(wc.MAX_ENTRIES + 40):
                    key = wc.operation_key("soak", {"i": i})
                    wc.put(key, {"i": i}, kind="soak")
                    telemetry.emit("soak_cycle", i=i)

                checkpoints = wc.load()
                self.assertLessEqual(len(checkpoints), wc.MAX_ENTRIES)
                self.assertEqual(
                    telemetry.summarize(root / "telemetry.jsonl")["events"],
                    wc.MAX_ENTRIES + 40,
                )


if __name__ == "__main__":
    unittest.main()

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import telemetry


class TelemetryTests(unittest.TestCase):
    def test_emit_and_summarize(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "telemetry.jsonl"
            with patch.dict(os.environ, {"STUDIO_TELEMETRY_PATH": str(path)}, clear=False):
                telemetry.emit("repair_started", task_id="a")
                telemetry.emit("repair_finished", task_id="a", changed=True)

            summary = telemetry.summarize(path)
            self.assertEqual(summary["events"], 2)
            self.assertEqual(summary["kinds"]["repair_started"], 1)
            self.assertEqual(summary["kinds"]["repair_finished"], 1)
            self.assertIsNotNone(summary["last_ts"])

    def test_invalid_lines_do_not_break_summary(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "telemetry.jsonl"
            path.write_text('{"ts":1,"kind":"ok"}\nnot-json\n', encoding="utf-8")
            summary = telemetry.summarize(path)
            self.assertEqual(summary["events"], 1)
            self.assertEqual(summary["kinds"], {"ok": 1})


if __name__ == "__main__":
    unittest.main()

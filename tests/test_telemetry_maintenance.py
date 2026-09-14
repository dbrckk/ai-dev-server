import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import telemetry_maintenance as tm


class TelemetryMaintenanceTests(unittest.TestCase):
    def test_large_log_is_compacted_to_recent_tail(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "telemetry.jsonl"
            lines = [f'{{"kind":"event","n":{i}}}' for i in range(200)]
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")

            with patch.object(tm, "MAX_BYTES", 500), patch.object(tm, "TARGET_BYTES", 250):
                result = tm.compact(path)

            self.assertTrue(result["compacted"])
            self.assertLessEqual(result["bytes_after"], 300)
            text = path.read_text(encoding="utf-8")
            self.assertIn('"n":199', text)
            self.assertNotIn('"n":0}', text)

    def test_small_log_is_left_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "telemetry.jsonl"
            path.write_text('{"kind":"ok"}\n', encoding="utf-8")
            before = path.read_bytes()
            result = tm.compact(path)
            self.assertFalse(result["compacted"])
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()

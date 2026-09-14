import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import persistent_quick_gate_cache as pqc


class PersistentQuickGateCacheTests(unittest.TestCase):
    def test_roundtrip_with_matching_toolchain(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "cache.json"
            with patch.dict(os.environ, {"STUDIO_QUICK_GATE_CACHE_PATH": str(path)}, clear=False):
                entries = {
                    "abc": {
                        "passed": True,
                        "logs": [{"command": ["flutter", "analyze"], "exit_code": 0, "output": ""}],
                    }
                }
                pqc.save(entries)
                self.assertEqual(pqc.load(), entries)

    def test_toolchain_mismatch_invalidates_cache(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "cache.json"
            payload = {
                "schema": pqc.SCHEMA,
                "toolchain_fingerprint": "0" * 64,
                "entries": {"abc": {"passed": True, "logs": []}},
            }
            path.write_text(json.dumps(payload))
            with patch.dict(os.environ, {"STUDIO_QUICK_GATE_CACHE_PATH": str(path)}, clear=False):
                self.assertEqual(pqc.load(), {})

    def test_cache_is_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "cache.json"
            with patch.dict(os.environ, {"STUDIO_QUICK_GATE_CACHE_PATH": str(path)}, clear=False):
                entries = {
                    str(i): {"passed": True, "logs": []}
                    for i in range(pqc.MAX_ENTRIES + 20)
                }
                pqc.save(entries)
                loaded = pqc.load()
                self.assertEqual(len(loaded), pqc.MAX_ENTRIES)
                self.assertNotIn("0", loaded)
                self.assertIn(str(pqc.MAX_ENTRIES + 19), loaded)


if __name__ == "__main__":
    unittest.main()

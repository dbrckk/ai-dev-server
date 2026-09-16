import json
import unittest
from pathlib import Path

from core import request_check


class JumpyV13MigrationTests(unittest.TestCase):
    def test_jumpy_is_an_enabled_v13_mobile_studio_request(self):
        request_path = Path("control/mobile-requests/jumpy.json")
        self.assertTrue(
            request_path.is_file(),
            "Jumpy must be owned by the v1.3 Autonomous Mobile Studio queue",
        )
        request = request_check(json.loads(request_path.read_text(encoding="utf-8")))
        self.assertEqual(request["id"], "jumpy")
        self.assertEqual(request["target_repo"], "dbrckk/Jumpy")
        self.assertTrue(request["enabled"])
        self.assertEqual(request["priority"], 100)
        self.assertFalse(request["play_publish"]["enabled"])
        self.assertFalse(request["play_publish"]["commit"])

    def test_legacy_jumpy_scheduler_is_removed(self):
        legacy = Path(".github/workflows/jumpy-autocycle.yml")
        self.assertFalse(
            legacy.exists(),
            "Legacy Jumpy scheduler must not compete with Autonomous Mobile Studio",
        )


if __name__ == "__main__":
    unittest.main()

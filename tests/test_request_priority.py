import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError, request_check


def _request(**overrides):
    value = {
        "id": "demo",
        "target_repo": "owner/repo",
        "app_name": "demo_app",
        "brief": "Create a complete working application with verified tests.",
        "enabled": True,
    }
    value.update(overrides)
    return value


class RequestPriorityTests(unittest.TestCase):
    def test_priority_defaults_to_fifty(self):
        self.assertEqual(request_check(_request())["priority"], 50)

    def test_priority_accepts_valid_range(self):
        self.assertEqual(request_check(_request(priority=100))["priority"], 100)
        self.assertEqual(request_check(_request(priority=1))["priority"], 1)

    def test_priority_rejects_invalid_values(self):
        for value in (0, 101, True, 2.5, "50"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(StudioError, "Invalid priority"):
                    request_check(_request(priority=value))


if __name__ == "__main__":
    unittest.main()

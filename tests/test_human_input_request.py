from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
if str(STUDIO) not in sys.path:
    sys.path.insert(0, str(STUDIO))

from human_input_request import prerequisite_satisfied, requires_human_input, write_request


class HumanInputRequestTests(unittest.TestCase):
    def test_detects_credentials(self):
        self.assertTrue(requires_human_input("Missing STUDIO_API_KEY"))
        self.assertTrue(requires_human_input("release credentials required"))
        self.assertFalse(requires_human_input("unit tests failed"))

    def test_secret_is_requested_by_name_but_never_embedded(self):
        with tempfile.TemporaryDirectory() as td:
            p = write_request(Path(td), "demo", "Missing STUDIO_API_KEY", target_repo="owner/repo")
            text = p.read_text()
        self.assertIn("STUDIO_API_KEY", text)
        self.assertIn("Do NOT paste API keys", text)
        self.assertIn("owner/repo", text)

    def test_prerequisite_satisfied_when_named_secret_exists(self):
        from unittest.mock import patch
        with patch.dict("os.environ", {"STUDIO_API_KEY":"present"}, clear=True):
            self.assertTrue(prerequisite_satisfied("Missing STUDIO_API_KEY"))
        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(prerequisite_satisfied("Missing STUDIO_API_KEY"))


if __name__ == "__main__":
    unittest.main()

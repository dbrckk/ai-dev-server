from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/"studio"
if str(STUDIO) not in sys.path:
    sys.path.insert(0,str(STUDIO))

from generic_policy import editable, validate_patch


class GenericPolicyTests(unittest.TestCase):
    def test_common_source_is_editable(self):
        self.assertTrue(editable("src/main.ts"))
        self.assertTrue(editable("pyproject.toml"))

    def test_sensitive_and_ci_paths_are_blocked(self):
        self.assertFalse(editable(".env"))
        self.assertFalse(editable(".github/workflows/ci.yml"))
        self.assertFalse(editable("keys/release.keystore"))

    def test_patch_rejects_secret_pattern(self):
        with self.assertRaises(ValueError):
            validate_patch({"files":[{"path":"src/config.py","content":"TOKEN='sk-abcdefghijklmnopqrstuvwxyz123456'"}]})


if __name__=="__main__":
    unittest.main()

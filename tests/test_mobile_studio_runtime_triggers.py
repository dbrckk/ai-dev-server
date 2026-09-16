import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/mobile-studio.yml"


class MobileStudioRuntimeTriggerTests(unittest.TestCase):
    def test_runtime_changes_retrigger_autonomous_mobile_studio(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("'.github/workflows/mobile-studio.yml'", text)
        self.assertIn("'scripts/bootstrap-android-ci.sh'", text)


if __name__ == "__main__":
    unittest.main()

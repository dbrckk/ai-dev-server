import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError, request_check
from generic_project import _run_browser_validation


CONTRACT = {
    "schema":"production-os/browser-validation/v1",
    "report_schema":"production-os/browser-validation-report/v1",
    "script":".production-os/browser_validate.py",
    "artifacts_dir":".production-os/browser-artifacts",
    "runtime":"python-playwright-chromium",
}


def request():
    return {
        "id":"pos-browser-contract",
        "target_repo":"owner/repo",
        "app_name":"sample_app",
        "brief":"Validate the changed user interface in a real browser.",
        "enabled":True,
        "tool_contracts":{"browser_validation":dict(CONTRACT)},
    }


class BrowserValidationContractTests(unittest.TestCase):
    def _write_script(self, root: Path, *, console_errors=None, page_errors=None):
        script = root / ".production-os" / "browser_validate.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version":"production-os/browser-validation-report/v1",
            "url":"http://127.0.0.1:4173/",
            "console_errors":console_errors or [],
            "page_errors":page_errors or [],
            "screenshots":["home.png"],
        }
        script.write_text(
            "import json\n"
            "from pathlib import Path\n"
            "root=Path('.production-os/browser-artifacts')\n"
            "root.mkdir(parents=True,exist_ok=True)\n"
            "(root/'home.png').write_bytes(b'fake-png-evidence')\n"
            f"(root/'report.json').write_text({json.dumps(json.dumps(payload))},encoding='utf-8')\n",
            encoding="utf-8",
        )

    def test_request_check_accepts_browser_validation_contract(self):
        checked = request_check(request())
        self.assertEqual(
            checked["tool_contracts"]["browser_validation"],
            CONTRACT,
        )

    def test_request_check_rejects_mutated_browser_validation_contract(self):
        value = request()
        value["tool_contracts"]["browser_validation"]["script"] = "../escape.py"
        with self.assertRaisesRegex(
            StudioError,
            "Invalid browser validation tool contract",
        ):
            request_check(value)

    def test_browser_validation_requires_script(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = _run_browser_validation(
                request(),
                root / "work",
                root / "out",
            )
        self.assertFalse(result["passed"])
        self.assertEqual(
            result["reason"],
            "browser-validation-script-missing",
        )

    def test_browser_validation_accepts_report_and_copies_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            work = root / "work"
            out = root / "out"
            work.mkdir()
            self._write_script(work)

            result = _run_browser_validation(request(), work, out)

            self.assertTrue(result["passed"])
            self.assertEqual(
                result["screenshots"],
                ["home.png"],
            )
            self.assertIn("home.png", result["copied_artifacts"])
            self.assertIn("report.json", result["copied_artifacts"])
            self.assertTrue(
                (out / "browser-validation" / "home.png").is_file()
            )

    def test_browser_validation_fails_on_console_errors(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            work = root / "work"
            work.mkdir()
            self._write_script(
                work,
                console_errors=["Uncaught TypeError: boom"],
            )

            result = _run_browser_validation(
                request(),
                work,
                root / "out",
            )

            self.assertFalse(result["passed"])
            self.assertEqual(result["reason"], "browser-console-errors")
            self.assertEqual(
                result["console_errors"],
                ["Uncaught TypeError: boom"],
            )


if __name__ == "__main__":
    unittest.main()

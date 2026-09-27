import base64
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError, request_check
from generic_project import _run_mobile_validation
from generic_policy import editable


CONTRACT = {
    "schema":"production-os/mobile-validation/v1",
    "report_schema":"production-os/mobile-validation-report/v1",
    "script":".production-os/mobile_validate.py",
    "artifacts_dir":".production-os/mobile-artifacts",
    "runtime":"android-adb-emulator",
}


def request():
    return {
        "id":"pos-mobile-contract",
        "target_repo":"owner/repo",
        "app_name":"sample_app",
        "brief":"Validate the changed native Android UI on an emulator.",
        "enabled":True,
        "tool_contracts":{"mobile_validation":dict(CONTRACT)},
    }


class MobileValidationContractTests(unittest.TestCase):
    def _write_script(self, root: Path, *, fatal_errors=None):
        script = root / ".production-os" / "mobile_validate.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version":"production-os/mobile-validation-report/v1",
            "package_name":"com.example.sample",
            "activity":"com.example.sample.MainActivity",
            "device_serial":"emulator-5554",
            "fatal_errors":fatal_errors or [],
            "screenshots":["home.png"],
        }
        png = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwC"
            "AAAAC0lEQVR42mP8/x8AAusB9Y9Zl3sAAAAASUVORK5CYII="
        )
        script.write_text(
            "import base64, json\n"
            "from pathlib import Path\n"
            "root=Path('.production-os/mobile-artifacts')\n"
            "root.mkdir(parents=True,exist_ok=True)\n"
            f"(root/'home.png').write_bytes(base64.b64decode({png!r}))\n"
            f"(root/'report.json').write_text({json.dumps(json.dumps(payload))},encoding='utf-8')\n",
            encoding="utf-8",
        )

    def test_mobile_runtime_artifacts_are_not_publishable(self):
        self.assertTrue(editable(".production-os/mobile_validate.py"))
        self.assertFalse(
            editable(".production-os/mobile-artifacts/report.json")
        )
        self.assertFalse(
            editable(".production-os/mobile-artifacts/home.png")
        )

    def test_request_check_accepts_mobile_validation_contract(self):
        checked = request_check(request())
        self.assertEqual(
            checked["tool_contracts"]["mobile_validation"],
            CONTRACT,
        )

    def test_request_check_rejects_mutated_mobile_validation_contract(self):
        value = request()
        value["tool_contracts"]["mobile_validation"]["runtime"] = "fake"
        with self.assertRaisesRegex(
            StudioError,
            "Invalid mobile validation tool contract",
        ):
            request_check(value)

    def test_mobile_validation_accepts_structured_emulator_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            work = root / "work"
            out = root / "out"
            work.mkdir()
            self._write_script(work)

            result = _run_mobile_validation(request(), work, out)

            self.assertTrue(result["passed"])
            self.assertEqual(result["package_name"], "com.example.sample")
            self.assertEqual(result["device_serial"], "emulator-5554")
            self.assertEqual(result["screenshots"], ["home.png"])
            self.assertIn("home.png", result["copied_artifacts"])
            self.assertTrue(
                (out / "mobile-validation" / "home.png").is_file()
            )

    def test_mobile_validation_fails_on_fatal_device_errors(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            work = root / "work"
            work.mkdir()
            self._write_script(
                work,
                fatal_errors=["FATAL EXCEPTION: main"],
            )

            result = _run_mobile_validation(
                request(),
                work,
                root / "out",
            )

            self.assertFalse(result["passed"])
            self.assertEqual(result["reason"], "mobile-fatal-errors")
            self.assertEqual(
                result["fatal_errors"],
                ["FATAL EXCEPTION: main"],
            )


if __name__ == "__main__":
    unittest.main()

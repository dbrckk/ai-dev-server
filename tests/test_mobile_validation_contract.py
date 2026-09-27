import base64
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError, request_check
from generic_project import _run_mobile_validation
from generic_policy import editable
from production_os_worker import worker_capabilities


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
        "brief":"Validate the changed native user interface on Android.",
        "enabled":True,
        "tool_contracts":{"mobile_validation":dict(CONTRACT)},
    }


class MobileValidationContractTests(unittest.TestCase):
    def _write_script(self, root: Path, *, fatal_errors=None):
        script = root / ".production-os" / "mobile_validate.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version":"production-os/mobile-validation-report/v1",
            "package_name":"com.example.app",
            "activity":"com.example.app/.MainActivity",
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
        self.assertFalse(editable(".production-os/mobile-artifacts/report.json"))
        self.assertFalse(editable(".production-os/mobile-artifacts/home.png"))

    def test_request_check_accepts_mobile_contract(self):
        checked = request_check(request())
        self.assertEqual(
            checked["tool_contracts"]["mobile_validation"],
            CONTRACT,
        )

    def test_request_check_rejects_mutated_mobile_contract(self):
        value = request()
        value["tool_contracts"]["mobile_validation"]["script"] = "../escape.py"
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
            self.assertEqual(result["device_serial"], "emulator-5554")
            self.assertEqual(result["screenshots"], ["home.png"])
            self.assertTrue(
                (out / "mobile-validation" / "home.png").is_file()
            )

    def test_mobile_validation_fails_on_fatal_errors(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            work = root / "work"
            work.mkdir()
            self._write_script(work, fatal_errors=["FATAL EXCEPTION: main"])

            result = _run_mobile_validation(
                request(),
                work,
                root / "out",
            )

            self.assertFalse(result["passed"])
            self.assertEqual(result["reason"], "mobile-fatal-errors")

    def test_mobile_specialty_requires_android_toolchain_probe(self):
        completed = type("Completed", (), {"returncode": 0})()
        with patch("production_os_worker.shutil.which") as which, patch(
            "production_os_worker.subprocess.run",
            return_value=completed,
        ):
            which.side_effect = lambda name, path=None: "/sdk/" + name
            caps = worker_capabilities({
                "PRODUCTION_OS_WORKER_SPECIALTIES":"mobile",
                "PATH":"/sdk",
            })
        self.assertIn("mobile-ui-validation", caps)

    def test_mobile_specialty_is_not_advertised_without_emulator(self):
        with patch("production_os_worker.shutil.which") as which:
            which.side_effect = lambda name, path=None: (
                None if name == "emulator" else "/sdk/" + name
            )
            caps = worker_capabilities({
                "PRODUCTION_OS_WORKER_SPECIALTIES":"mobile",
                "PATH":"/sdk",
            })
        self.assertNotIn("mobile-ui-validation", caps)


if __name__ == "__main__":
    unittest.main()

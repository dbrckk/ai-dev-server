import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "studio"))
from release import build_release


class FakeSandbox:
    def __init__(self, root, fail_at=None):
        self.root = root
        self.fail_at = fail_at
        self.calls = []

    def run(self, args, network=False, timeout=0):
        self.calls.append((args, network, timeout))
        if self.fail_at == len(self.calls):
            return 1, "failed"
        if args[:3] == ["flutter", "build", "appbundle"]:
            p = self.root / "build/app/outputs/bundle/release/app-release.aab"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"a" * 2000)
        if args[:3] == ["flutter", "build", "apk"]:
            p = self.root / "build/app/outputs/flutter-apk/app-release.apk"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"b" * 2500)
        return 0, "ok"


class ReleaseBuildTests(unittest.TestCase):
    def test_release_build_collects_store_and_installable_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = build_release(root, FakeSandbox(root))
            self.assertTrue(result["passed"])
            self.assertEqual(result["artifact"], "app-release.aab")
            self.assertEqual(result["bytes"], 2000)
            self.assertEqual(len(result["sha256"]), 64)
            self.assertEqual(result["installable_artifact"], "app-release.apk")
            self.assertEqual(result["installable_bytes"], 2500)
            self.assertEqual(len(result["installable_sha256"]), 64)

    def test_release_build_stops_on_first_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sandbox = FakeSandbox(root, fail_at=2)
            result = build_release(root, sandbox)
            self.assertFalse(result["passed"])
            self.assertEqual(len(sandbox.calls), 2)
            self.assertEqual(len(result["logs"]), 2)


if __name__ == "__main__":
    unittest.main()

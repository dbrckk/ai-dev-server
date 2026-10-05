import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from generic_project import _existing_worker_canary_verification


class ExistingWorkerCanaryVerificationTests(unittest.TestCase):
    def _request(self, sequence=2):
        return {
            "target_repo": "dbrckk/repo-standards",
            "production_os": {
                "workflow_id": "1" * 32,
                "workflow_task_id": "implementation",
            },
            "brief": (
                f"Production-OS worker canary {sequence}. "
                "Make exactly one intentional product-file change: "
                f"create .production-os/worker-canary-{sequence}.txt "
                "containing exactly one line: "
                f"production-os-worker-canary sequence {sequence}. "
                "Do not change dependencies, workflows, secrets, configuration, "
                "or existing source files. Previous autonomous attempt failed."
            ),
        }

    def test_accepts_exact_existing_canary_with_or_without_final_newline(self):
        for suffix in ("", "\n"):
            with self.subTest(suffix=repr(suffix)), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                target = root / ".production-os" / "worker-canary-2.txt"
                target.parent.mkdir(parents=True)
                target.write_text(
                    "production-os-worker-canary sequence 2" + suffix,
                    encoding="utf-8",
                )
                result = _existing_worker_canary_verification(
                    self._request(),
                    root,
                )
                self.assertIsNotNone(result)
                self.assertTrue(result["passed"])
                self.assertEqual(result["status"], "passed")
                self.assertEqual(
                    result["files"][0]["path"],
                    ".production-os/worker-canary-2.txt",
                )

    def test_rejects_wrong_content(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / ".production-os" / "worker-canary-2.txt"
            target.parent.mkdir(parents=True)
            target.write_text("wrong", encoding="utf-8")
            self.assertIsNone(
                _existing_worker_canary_verification(self._request(), root)
            )

    def test_rejects_non_canary_repository_or_missing_contract(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / ".production-os" / "worker-canary-2.txt"
            target.parent.mkdir(parents=True)
            target.write_text(
                "production-os-worker-canary sequence 2",
                encoding="utf-8",
            )
            wrong_repo = self._request()
            wrong_repo["target_repo"] = "dbrckk/other"
            self.assertIsNone(
                _existing_worker_canary_verification(wrong_repo, root)
            )
            incomplete = self._request()
            incomplete["brief"] = "Production-OS worker canary 2."
            self.assertIsNone(
                _existing_worker_canary_verification(incomplete, root)
            )


if __name__ == "__main__":
    unittest.main()

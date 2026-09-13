from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from repository_progress import compare, snapshot


def failed(log="AssertionError: expected 1 got 2"):
    return {
        "status":"failed",
        "passed":False,
        "results":[{
            "passed":False,
            "returncode":1,
            "command":["pytest","-q"],
            "log_tail":log,
        }],
    }


class RepositoryProgressTests(unittest.TestCase):
    def test_no_change_same_failure_is_no_progress(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.py").write_text("x=1\n")
            before=snapshot(root)
            after=snapshot(root)
            result=compare(before,after,previous_verification=failed(),current_verification=failed())
            self.assertEqual(result["status"],"no_progress")
            self.assertFalse(result["changed"])

    def test_changed_files_same_failure_is_churn(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.py").write_text("x=1\n")
            before=snapshot(root)
            (root/"a.py").write_text("x=2\n")
            after=snapshot(root)
            result=compare(before,after,previous_verification=failed(),current_verification=failed())
            self.assertEqual(result["status"],"churn_without_verified_progress")
            self.assertEqual(result["modified"],["a.py"])

    def test_changed_failure_signature_is_unverified_progress(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.py").write_text("x=1\n")
            before=snapshot(root)
            (root/"a.py").write_text("x=2\n")
            after=snapshot(root)
            result=compare(
                before,after,
                previous_verification=failed("AssertionError: one"),
                current_verification=failed("TypeError: two"),
            )
            self.assertEqual(result["status"],"progress_unverified")

    def test_failed_to_passed_is_verified_progress(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.py").write_text("x=1\n")
            before=snapshot(root)
            (root/"a.py").write_text("x=2\n")
            after=snapshot(root)
            result=compare(
                before,after,
                previous_verification=failed(),
                current_verification={"status":"passed","passed":True,"results":[]},
            )
            self.assertEqual(result["status"],"verified_progress")

    def test_passed_to_failed_is_regression(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.py").write_text("x=1\n")
            before=snapshot(root)
            (root/"a.py").write_text("broken\n")
            after=snapshot(root)
            result=compare(
                before,after,
                previous_verification={"status":"passed","passed":True,"results":[]},
                current_verification=failed(),
            )
            self.assertEqual(result["status"],"regression")


if __name__=="__main__":
    unittest.main()

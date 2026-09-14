import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from replacement_ci_policy import REQUIRED_GITHUB_CHECKS, validate_check_runs, validate_workflow, validate_workflow_text

class ReplacementCIPolicyTests(unittest.TestCase):
    def test_repository_ci_exposes_required_check_ids(self):
        root=Path(__file__).resolve().parents[1]
        result=validate_workflow(root/".github/workflows/ci.yml")
        self.assertTrue(result["valid"],result)
        self.assertEqual(set(result["required_checks"]),set(REQUIRED_GITHUB_CHECKS))

    def test_missing_required_check_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"ci.yml"
            path.write_text("jobs:\n  python-tests:\n    runs-on: ubuntu-latest\n")
            result=validate_workflow(path)
            self.assertFalse(result["valid"])
            self.assertIn("validate",result["missing_checks"])

    def test_required_check_runs_must_be_trusted_and_successful(self):
        runs=[
            {"id":1,"name":"validate","head_sha":"abc","status":"completed","conclusion":"success","started_at":"2026-01-01T00:00:10Z","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/1"},
            {"id":2,"name":"python-tests","head_sha":"abc","status":"completed","conclusion":"success","started_at":"2026-01-01T00:00:20Z","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/1"},
        ]
        result=validate_check_runs(runs,"o/r",commit_sha="abc",head_commit_timestamp=1767225600.0)
        self.assertTrue(result["valid"])
        self.assertEqual(set(result["passed_checks"]),set(REQUIRED_GITHUB_CHECKS))

    def test_untrusted_check_run_does_not_satisfy_policy(self):
        runs=[
            {"name":"validate","status":"completed","conclusion":"success","app":{"slug":"other"},"details_url":"https://github.com/o/r/actions/runs/1"},
            {"id":2,"name":"python-tests","head_sha":"abc","status":"completed","conclusion":"success","started_at":"2026-01-01T00:00:20Z","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/1"},
        ]
        result=validate_check_runs(runs,"o/r")
        self.assertFalse(result["valid"])
        self.assertIn("validate",result["missing_checks"])

    def test_stale_check_run_is_rejected(self):
        runs=[
            {"id":1,"name":"validate","head_sha":"abc","status":"completed","conclusion":"success","started_at":"2025-12-31T23:59:59Z","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/1"},
            {"id":2,"name":"python-tests","head_sha":"abc","status":"completed","conclusion":"success","started_at":"2026-01-01T00:00:20Z","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/1"},
        ]
        result=validate_check_runs(runs,"o/r",commit_sha="abc",head_commit_timestamp=1767225600.0)
        self.assertFalse(result["valid"])
        self.assertIn("validate",result["stale_checks"])

    def test_wrong_sha_check_run_is_rejected(self):
        runs=[
            {"id":1,"name":"validate","head_sha":"old","status":"completed","conclusion":"success","started_at":"2026-01-01T00:00:10Z","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/1"},
            {"id":2,"name":"python-tests","head_sha":"abc","status":"completed","conclusion":"success","started_at":"2026-01-01T00:00:20Z","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/1"},
        ]
        result=validate_check_runs(runs,"o/r",commit_sha="abc",head_commit_timestamp=1767225600.0)
        self.assertFalse(result["valid"])
        self.assertIn("validate",result["missing_checks"])

    def test_required_checks_from_multiple_workflow_runs_are_rejected(self):
        runs=[
            {"id":1,"name":"validate","head_sha":"abc","status":"completed","conclusion":"success","started_at":"2026-01-01T00:00:10Z","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/11"},
            {"id":2,"name":"python-tests","head_sha":"abc","status":"completed","conclusion":"success","started_at":"2026-01-01T00:00:20Z","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/12"},
        ]
        result=validate_check_runs(runs,"o/r",commit_sha="abc",head_commit_timestamp=1767225600.0)
        self.assertFalse(result["valid"])
        self.assertTrue(result["mixed_workflow_runs"])
        self.assertEqual(result["workflow_run_ids"],[11,12])
        self.assertIsNone(result["common_workflow_run_id"])

    def test_workflow_text_requires_canonical_name_and_jobs(self):
        result=validate_workflow_text("name: CI\njobs:\n  validate:\n  python-tests:\n")
        self.assertTrue(result["valid"])
        self.assertEqual(result["workflow_name"],"CI")

    def test_workflow_text_rejects_wrong_name(self):
        result=validate_workflow_text("name: Other\njobs:\n  validate:\n  python-tests:\n")
        self.assertFalse(result["valid"])

    def test_workflow_text_rejects_missing_required_job(self):
        result=validate_workflow_text("name: CI\njobs:\n  python-tests:\n")
        self.assertFalse(result["valid"])
        self.assertIn("validate",result["missing_checks"])

if __name__=="__main__":
    unittest.main()

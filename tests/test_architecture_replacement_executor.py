import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from architecture_replacement_executor import (
    ReplacementExecutionError,
    _safe_path,
    _validate_candidate,
    _commands,
)

class ReplacementExecutorTests(unittest.TestCase):
    def order(self):
        return {
            "id":"replace-123",
            "current_repo":"a/current",
            "replacement_repo":"a/better",
        }

    def candidate(self):
        return {
            "status":"replacement_candidate_validated",
            "work_order_id":"replace-123",
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "baseline_sha":"0"*40,
            "files":[{"path":"lib/example.dart","content":"void main() {}\n"}],
        }

    def test_candidate_identity_and_files_are_validated(self):
        files=_validate_candidate(self.order(),self.candidate())
        self.assertEqual(files[0]["path"],"lib/example.dart")

    def test_protected_studio_path_is_rejected(self):
        c=self.candidate()
        c["files"]=[{"path":"studio/run.py","content":"x"}]
        with self.assertRaises(ReplacementExecutionError):
            _validate_candidate(self.order(),c)

    def test_workflow_path_is_rejected(self):
        with self.assertRaises(ReplacementExecutionError):
            _safe_path(".github/workflows/ci.yml")

    def test_parent_traversal_is_rejected(self):
        with self.assertRaises(ReplacementExecutionError):
            _safe_path("../secret")

    def test_default_validation_commands_are_bounded(self):
        commands=_commands(self.candidate())
        self.assertGreaterEqual(len(commands),1)
        self.assertLessEqual(len(commands),8)

    def test_candidate_cannot_change_identity(self):
        c=self.candidate()
        c["replacement_repo"]="evil/other"
        with self.assertRaises(ReplacementExecutionError):
            _validate_candidate(self.order(),c)

if __name__=="__main__":
    unittest.main()

import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from architecture_replacement_candidate import ReplacementCandidateRejected, validate
from architecture_replacement_synthesis import _collect_context

class ReplacementCandidateTests(unittest.TestCase):
    def order(self):
        return {"id":"replace-1","current_repo":"a/current","replacement_repo":"a/better"}

    def candidate(self):
        return {
            "version":1,
            "work_order_id":"replace-1",
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "baseline_sha":"0"*40,
            "files":[{"path":"pubspec.yaml","content":"name: demo\n"}],
            "validation_commands":[["flutter","test"]],
            "notes":"migration",
        }

    def test_valid_candidate_is_normalized(self):
        result=validate(self.order(),self.candidate())
        self.assertEqual(result["status"],"replacement_candidate_validated")
        self.assertEqual(result["files"][0]["path"],"pubspec.yaml")

    def test_shell_command_is_rejected(self):
        candidate=self.candidate()
        candidate["validation_commands"]=[["bash","-lc","true"]]
        with self.assertRaises(ReplacementCandidateRejected):
            validate(self.order(),candidate)

    def test_protected_path_is_rejected(self):
        candidate=self.candidate()
        candidate["files"]=[{"path":"studio/run.py","content":"x"}]
        with self.assertRaises(ReplacementCandidateRejected):
            validate(self.order(),candidate)

    def test_context_collection_is_bounded_and_finds_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"pubspec.yaml").write_text("dependencies:\n  current: any\n")
            (root/"lib").mkdir()
            (root/"lib"/"a.dart").write_text("import 'package:current/current.dart';\n")
            rows=_collect_context(root,"a/current","a/better")
            paths={x["path"] for x in rows}
            self.assertIn("pubspec.yaml",paths)
            self.assertIn("lib/a.dart",paths)
            self.assertLessEqual(len(rows),20)

if __name__=="__main__":
    unittest.main()

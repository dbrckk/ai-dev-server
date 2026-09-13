from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from agents.workspace import snapshot
from selective_rollback import isolate


class SelectiveRollbackTests(unittest.TestCase):
    def test_keeps_healthy_changes_and_reverts_single_culprit(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.py").write_text("a=1\n")
            (root/"b.py").write_text("b=1\n")
            before=snapshot(root)

            (root/"a.py").write_text("a=2\n")
            (root/"b.py").write_text("BROKEN\n")

            def verify():
                passed="BROKEN" not in (root/"b.py").read_text()
                return {"passed":passed,"status":"passed" if passed else "failed"}

            result=isolate(root,before=before,verify=verify,max_runs=4)
            self.assertEqual(result["status"],"partial_rollback_passed")
            self.assertEqual(result["reverted_files"],["b.py"])
            self.assertEqual(result["kept_files"],["a.py"])
            self.assertEqual((root/"a.py").read_text(),"a=2\n")
            self.assertEqual((root/"b.py").read_text(),"b=1\n")

    def test_multiple_culprits_can_be_rolled_back(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for name in ("a.py","b.py","c.py"):
                (root/name).write_text("ok\n")
            before=snapshot(root)
            (root/"a.py").write_text("BROKEN A\n")
            (root/"b.py").write_text("good improvement\n")
            (root/"c.py").write_text("BROKEN C\n")

            def verify():
                text="".join((root/name).read_text() for name in ("a.py","b.py","c.py"))
                passed="BROKEN" not in text
                return {"passed":passed,"status":"passed" if passed else "failed"}

            result=isolate(root,before=before,verify=verify,max_runs=6)
            self.assertEqual(result["status"],"partial_rollback_passed")
            self.assertEqual(result["reverted_files"],["a.py","c.py"])
            self.assertEqual(result["kept_files"],["b.py"])
            self.assertEqual((root/"b.py").read_text(),"good improvement\n")

    def test_budget_exhaustion_falls_back_to_full_rollback(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for name in ("a.py","b.py","c.py"):
                (root/name).write_text("ok\n")
            before=snapshot(root)
            for name in ("a.py","b.py","c.py"):
                (root/name).write_text("BROKEN\n")

            def verify():
                return {"passed":False,"status":"failed"}

            result=isolate(root,before=before,verify=verify,max_runs=2)
            self.assertEqual(result["status"],"full_rollback_required")
            self.assertEqual((root/"a.py").read_text(),"ok\n")
            self.assertEqual((root/"b.py").read_text(),"ok\n")
            self.assertEqual((root/"c.py").read_text(),"ok\n")

    def test_new_file_can_be_identified_as_culprit(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.py").write_text("ok\n")
            before=snapshot(root)
            (root/"a.py").write_text("better\n")
            (root/"bad.py").write_text("BROKEN\n")

            def verify():
                passed=not (root/"bad.py").exists()
                return {"passed":passed,"status":"passed" if passed else "failed"}

            result=isolate(root,before=before,verify=verify,max_runs=4)
            self.assertEqual(result["status"],"partial_rollback_passed")
            self.assertIn("bad.py",result["reverted_files"])
            self.assertFalse((root/"bad.py").exists())
            self.assertEqual((root/"a.py").read_text(),"better\n")


if __name__=="__main__":
    unittest.main()

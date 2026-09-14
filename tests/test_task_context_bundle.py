from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from task_context_bundle import build


class TaskContextBundleTests(unittest.TestCase):
    def test_selects_recent_files_and_neighbors(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for rel,text in {
                "src/core.py":"core\n",
                "src/api.py":"api\n",
                "tests/test_api.py":"test\n",
                "other.py":"other\n",
            }.items():
                p=root/rel
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(text)
            semantic={
                "recent_attempts":[{
                    "changed_files":["src/api.py"],
                    "impacted_tests":["tests/test_api.py"],
                }]
            }
            graph={
                "edges":{"src/api.py":["src/core.py"]},
                "reverse":{"src/api.py":["tests/test_api.py"]},
            }
            result=build(root,semantic_context=semantic,dependency_graph=graph)
            self.assertEqual(result["mode"],"task_local_semantic")
            self.assertIn("src/api.py",result["files"])
            self.assertIn("src/core.py",result["files"])
            self.assertIn("tests/test_api.py",result["files"])
            self.assertNotIn("other.py",result["files"])

    def test_no_semantic_seeds_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(build(Path(td),semantic_context={"recent_attempts":[]},dependency_graph={}))

    def test_byte_budget_is_respected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.py").write_text("a"*80)
            (root/"b.py").write_text("b"*80)
            semantic={"recent_attempts":[{"changed_files":["a.py","b.py"],"impacted_tests":[]}]}
            result=build(root,semantic_context=semantic,dependency_graph={},max_bytes=100)
            self.assertLessEqual(result["bytes"],100)
            self.assertEqual(len(result["files"]),1)


if __name__=="__main__":
    unittest.main()

from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from dependency_graph import assess, build, patch_guard


class DependencyGraphTests(unittest.TestCase):
    def test_python_import_and_impacted_test(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"pkg").mkdir()
            (root/"tests").mkdir()
            (root/"pkg"/"core.py").write_text("VALUE=1\n")
            (root/"pkg"/"api.py").write_text("from . import core\n")
            (root/"tests"/"test_api.py").write_text("from pkg import api\n")
            graph=build(root)
            self.assertIn("pkg/core.py",graph["edges"]["pkg/api.py"])
            impact=assess(graph,["pkg/core.py"])
            self.assertIn("tests/test_api.py",impact["impacted_tests"])

    def test_js_relative_imports_are_resolved(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"src").mkdir()
            (root/"src"/"util.ts").write_text("export const x=1\n")
            (root/"src"/"main.ts").write_text("import {x} from './util'\n")
            graph=build(root)
            self.assertEqual(graph["edges"]["src/main.ts"],["src/util.ts"])

    def test_hotspot_is_selected_without_explicit_focus(self):
        graph={
            "edges":{"core.py":[],"leaf.py":[]},
            "reverse":{"core.py":[f"m{i}.py" for i in range(8)],"leaf.py":[]},
            "tests":[],
            "edge_count":8,
        }
        result=assess(graph,[])
        self.assertEqual(result["focus"][0]["path"],"core.py")
        self.assertEqual(result["level"],"high")

    def test_high_coupling_direct_pair_is_rejected(self):
        graph={
            "edges":{"core.py":["api.py"],"api.py":[]},
            "reverse":{"core.py":[f"m{i}.py" for i in range(8)],"api.py":["client.py"]},
            "tests":[],
            "edge_count":10,
        }
        result=patch_guard(graph,["core.py","api.py"])
        self.assertTrue(result["reject"])
        self.assertEqual(result["direct_pairs"],[["api.py","core.py"]])

    def test_uncoupled_pair_is_allowed(self):
        graph={
            "edges":{"a.py":[],"b.py":[]},
            "reverse":{"a.py":[],"b.py":[]},
            "tests":[],
            "edge_count":0,
        }
        self.assertFalse(patch_guard(graph,["a.py","b.py"])["reject"])

    def test_high_coupling_reduces_patch_width(self):
        graph={"edges":{"core.py":[]},"reverse":{"core.py":[f"m{i}.py" for i in range(9)]},"tests":[],"edge_count":9}
        result=assess(graph,["core.py"])
        self.assertEqual(result["level"],"high")
        self.assertEqual(result["max_patch_files"],2)


if __name__=="__main__":
    unittest.main()

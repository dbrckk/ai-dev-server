from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from done_when_evaluator import classify, evaluate, evaluate_static


class DoneWhenEvaluatorTests(unittest.TestCase):
    def test_file_criterion_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"README.md").write_text("ok")
            result=evaluate_static(root,"file:README.md")
            self.assertTrue(result["passed"])
            self.assertEqual(result["evidence_refs"],["README.md"])

    def test_python_symbol_criterion(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"app.py").write_text("def run():\n    return 1\n")
            result=evaluate_static(root,"symbol:app.py#run")
            self.assertTrue(result["passed"])
            self.assertEqual(result["evidence_refs"],["app.py"])

    def test_review_criterion_is_left_to_reviewer(self):
        self.assertEqual(classify("user experience feels clear")["kind"],"review")

    @patch("done_when_evaluator.run_command")
    def test_test_criterion_runs_without_network(self, run_command):
        run_command.return_value={"passed":True}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            result=evaluate(root,["test:tests/test_api.py::test_ok"])
            self.assertTrue(result["deterministic"][0]["passed"])
            _,kwargs=run_command.call_args
            self.assertFalse(kwargs["network"])

    @patch("done_when_evaluator.run_command")
    def test_build_criterion_uses_known_build_script(self, run_command):
        run_command.return_value={"passed":True}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"package.json").write_text('{"scripts":{"build":"vite build"}}')
            result=evaluate(root,["build:default"])
            self.assertTrue(result["deterministic"][0]["passed"])
            args,_=run_command.call_args
            self.assertEqual(args[0],["npm","run","build"])

    def test_mixed_criteria_split_deterministic_and_reviewer(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.py").write_text("VALUE=1\n")
            result=evaluate(root,["file:a.py","manual UX review"])
            self.assertEqual(len(result["deterministic"]),1)
            self.assertEqual(result["reviewer"],["manual UX review"])


if __name__=="__main__":
    unittest.main()

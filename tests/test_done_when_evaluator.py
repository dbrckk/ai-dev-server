from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from done_when_evaluator import apply_causality, baseline_static, classify, evaluate, evaluate_static, validate_contract


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
    def test_reuses_targeted_test_precheck_without_rerun(self, run_command):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            result=evaluate(
                root,
                ["test:tests/test_api.py::test_ok"],
                verification={
                    "passed":True,
                    "targeted_precheck":{
                        "passed":True,
                        "impacted_tests":["tests/test_api.py"],
                        "command":["pytest","-q","tests/test_api.py"],
                    },
                },
            )
            self.assertTrue(result["deterministic"][0]["passed"])
            self.assertEqual(result["deterministic"][0]["source"],"verification_reuse")
            run_command.assert_not_called()

    @patch("done_when_evaluator.run_command")
    def test_reuses_trusted_build_result_without_rerun(self, run_command):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            result=evaluate(
                root,
                ["build:default"],
                verification={
                    "passed":True,
                    "commands":[["npm","run","build"]],
                    "results":[{"passed":True}],
                },
            )
            self.assertTrue(result["deterministic"][0]["passed"])
            self.assertEqual(result["deterministic"][0]["source"],"verification_reuse")
            run_command.assert_not_called()

    @patch("done_when_evaluator.run_command")
    def test_build_criterion_uses_known_build_script(self, run_command):
        run_command.return_value={"passed":True}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"package.json").write_text('{"scripts":{"build":"vite build"}}')
            result=evaluate(root,["build:default"])
            self.assertTrue(result["deterministic"][0]["passed"])
            self.assertEqual(
                result["deterministic"][0]["evidence_refs"],
                ["command:npm run build"],
            )
            args,_=run_command.call_args
            self.assertEqual(args[0],["npm","run","build"])

    def test_contract_rejects_malformed_symbol(self):
        result=validate_contract(["symbol:app.py"])
        self.assertFalse(result["valid"])
        self.assertIn("invalid symbol criterion",result["errors"][0])

    def test_critical_contract_requires_deterministic_criterion(self):
        result=validate_contract(["manual UX review"],critical=True)
        self.assertFalse(result["valid"])
        self.assertIn("critical task requires",result["errors"][-1])

    def test_critical_contract_rejects_file_only_evidence(self):
        result=validate_contract(["file:README.md"],critical=True)
        self.assertFalse(result["valid"])
        self.assertEqual(result["strong_deterministic_count"],0)
        self.assertIn("strong deterministic",result["errors"][-1])

    def test_critical_contract_accepts_symbol_evidence(self):
        result=validate_contract(["symbol:src/api.py#handle_request"],critical=True)
        self.assertTrue(result["valid"])
        self.assertEqual(result["strong_deterministic_count"],1)

    def test_critical_contract_accepts_structured_evidence(self):
        result=validate_contract(["test:tests/test_api.py::test_ok","manual UX review"],critical=True)
        self.assertTrue(result["valid"])
        self.assertEqual(result["deterministic_count"],1)
        self.assertEqual(result["review_count"],1)

    def test_contract_rejects_path_escape(self):
        result=validate_contract(["file:../secret.txt"])
        self.assertFalse(result["valid"])
        self.assertIn("unsafe file criterion",result["errors"][0])

    def test_json_criterion_matches_nested_value(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"package.json").write_text('{"scripts":{"build":"vite build"},"flags":[true,false]}')
            result=evaluate_static(root,'json:package.json#scripts.build="vite build"')
            self.assertTrue(result["passed"])
            self.assertEqual(result["evidence_refs"],["package.json"])

    def test_json_criterion_supports_array_index(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"config.json").write_text('{"flags":[true,false]}')
            result=evaluate_static(root,'json:config.json#flags.0=true')
            self.assertTrue(result["passed"])
            self.assertEqual(result["actual"],True)

    def test_json_criterion_detects_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"config.json").write_text('{"mode":"dev"}')
            result=evaluate_static(root,'json:config.json#mode="prod"')
            self.assertFalse(result["passed"])

    def test_contract_rejects_invalid_json_expected_value(self):
        result=validate_contract(['json:config.json#mode=prod'])
        self.assertFalse(result["valid"])
        self.assertIn("invalid json expected value",result["errors"][0])

    def test_preexisting_static_criterion_is_not_first_attempt_proof(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"config.json").write_text('{"mode":"prod"}')
            criteria=['json:config.json#mode="prod"']
            before=baseline_static(root,criteria)
            result=evaluate(root,criteria)
            causal=apply_causality(result,before,first_attempt=True)
            self.assertFalse(causal["deterministic"][0]["passed"])
            self.assertTrue(causal["deterministic"][0]["preexisting"])

    def test_new_static_criterion_counts_as_causal_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            criteria=["file:created.txt"]
            before=baseline_static(root,criteria)
            (root/"created.txt").write_text("done")
            result=evaluate(root,criteria)
            causal=apply_causality(result,before,first_attempt=True)
            self.assertTrue(causal["deterministic"][0]["passed"])
            self.assertEqual(causal["preexisting_static_criteria"],[])

    def test_retry_may_reuse_preexisting_static_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"created.txt").write_text("done")
            criteria=["file:created.txt"]
            before=baseline_static(root,criteria)
            result=evaluate(root,criteria)
            causal=apply_causality(result,before,first_attempt=False)
            self.assertTrue(causal["deterministic"][0]["passed"])

    def test_mixed_criteria_split_deterministic_and_reviewer(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.py").write_text("VALUE=1\n")
            result=evaluate(root,["file:a.py","manual UX review"])
            self.assertEqual(len(result["deterministic"]),1)
            self.assertEqual(result["reviewer"],["manual UX review"])


if __name__=="__main__":
    unittest.main()

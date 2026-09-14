from pathlib import Path
import json
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from user_input_required import (
    UserInputRequiredError,
    build,
    clear,
    extract_secret_names,
    load,
    missing_env,
    satisfied,
    resume_decision,
    write,
)


class UserInputRequiredTests(unittest.TestCase):
    def test_extracts_only_explicit_secret_env_names(self):
        text="API key required: set OPENAI_API_KEY and MY_SERVICE_TOKEN"
        self.assertEqual(
            extract_secret_names(text),
            ["MY_SERVICE_TOKEN","OPENAI_API_KEY"],
        )

    def test_write_never_contains_secret_values(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            state=build(
                project_id="demo",
                reason="OPENAI_API_KEY is required",
                required_env=["OPENAI_API_KEY"],
            )
            write(root,state)
            machine=(root/"user-input-required.json").read_text()
            human=(root/"USER_INPUT_REQUIRED.txt").read_text()
            self.assertIn("OPENAI_API_KEY",machine)
            self.assertIn("OPENAI_API_KEY",human)
            self.assertNotIn("super-secret-value",machine+human)
            restored=load(root/"user-input-required.json")
            self.assertEqual(restored["required_env"],["OPENAI_API_KEY"])

    def test_missing_and_satisfied_environment(self):
        state=build(
            project_id="demo",
            reason="token required",
            required_env=["SERVICE_TOKEN"],
        )
        self.assertEqual(missing_env(state,{}),["SERVICE_TOKEN"])
        self.assertFalse(satisfied(state,{}))
        self.assertTrue(satisfied(state,{"SERVICE_TOKEN":"present"}))

    def test_resume_decision_waits_then_resumes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            state=build(
                project_id="demo",
                reason="token required",
                required_env=["SERVICE_TOKEN"],
            )
            write(root,state)
            waiting=resume_decision(
                root/"user-input-required.json",
                project_id="demo",
                environ={},
            )
            self.assertEqual(waiting["action"],"wait")
            self.assertEqual(waiting["missing_env"],["SERVICE_TOKEN"])
            resumed=resume_decision(
                root/"user-input-required.json",
                project_id="demo",
                environ={"SERVICE_TOKEN":"present"},
            )
            self.assertEqual(resumed["action"],"resume")
            self.assertEqual(resumed["missing_env"],[])

    def test_resume_decision_rejects_project_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            write(root,build(
                project_id="demo",
                reason="token required",
                required_env=["SERVICE_TOKEN"],
            ))
            decision=resume_decision(
                root/"user-input-required.json",
                project_id="other",
                environ={"SERVICE_TOKEN":"present"},
            )
            self.assertEqual(decision["action"],"invalid")
            self.assertIn("project mismatch",decision["error"])

    def test_clear_removes_both_state_files(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            state=build(
                project_id="demo",
                reason="token required",
                required_env=["SERVICE_TOKEN"],
            )
            write(root,state)
            clear(root)
            self.assertFalse((root/"user-input-required.json").exists())
            self.assertFalse((root/"USER_INPUT_REQUIRED.txt").exists())

    def test_invalid_env_name_is_rejected(self):
        with self.assertRaisesRegex(UserInputRequiredError,"required_env"):
            build(project_id="demo",reason="x",required_env=["not-safe"])


if __name__=="__main__":
    unittest.main()

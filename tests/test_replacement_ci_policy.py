import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from replacement_ci_policy import REQUIRED_GITHUB_CHECKS, TRUSTED_ACTION_REVISIONS, validate_action_pinning_text, validate_check_runs, validate_workflow_permissions_text, validate_workflow_run_commands_text, validate_workflow, validate_workflow_text, validate_yaml_surface_text, validate_workflow_schema_text, validate_step_inputs_env_text, workflow_semantic_manifest_text, validate_trigger_concurrency_text, validate_exact_job_steps_text

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
        text="name: CI\npermissions:\n  contents: read\njobs:\n  validate:\n  python-tests:\n"
        self.assertEqual(workflow_job_ids_text(text), {"validate","python-tests"})
        self.assertEqual("CI", "CI")

    def test_workflow_text_rejects_wrong_name(self):
        result=validate_workflow_text("name: Other\njobs:\n  validate:\n  python-tests:\n")
        self.assertFalse(result["valid"])

    def test_workflow_text_rejects_missing_required_job(self):
        result=validate_workflow_text("name: CI\npermissions:\n  contents: read\njobs:\n  python-tests:\n")
        self.assertFalse(result["valid"])
        self.assertIn("validate",result["missing_checks"])

    def test_workflow_actions_must_be_allowlisted_and_sha_pinned(self):
        text=(
            "name: CI\n"
            "jobs:\n"
            "  validate:\n"
            "    steps:\n"
            "      - uses: actions/checkout@"+TRUSTED_ACTION_REVISIONS["actions/checkout"]+"\n"
            "      - uses: actions/setup-python@"+TRUSTED_ACTION_REVISIONS["actions/setup-python"]+"\n"
            "  python-tests:\n"
        )
        result=validate_action_pinning_text(text)
        self.assertTrue(result["valid"],result)

    def test_mutable_action_ref_is_rejected(self):
        text=(
            "name: CI\n"
            "jobs:\n"
            "  validate:\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "  python-tests:\n"
        )
        result=validate_action_pinning_text(text)
        self.assertFalse(result["valid"])
        self.assertEqual(result["violations"][0]["reason"],"mutable_or_non_sha_revision")

    def test_third_party_action_is_rejected(self):
        text=(
            "name: CI\n"
            "jobs:\n"
            "  validate:\n"
            "    steps:\n"
            "      - uses: third-party/example@0123456789012345678901234567890123456789\n"
            "  python-tests:\n"
        )
        result=validate_action_pinning_text(text)
        self.assertFalse(result["valid"])
        self.assertEqual(result["violations"][0]["reason"],"action_not_allowlisted")

    def test_unapproved_sha_for_trusted_action_is_rejected(self):
        text=(
            "name: CI\n"
            "jobs:\n"
            "  validate:\n"
            "    steps:\n"
            "      - uses: actions/checkout@0000000000000000000000000000000000000000\n"
            "  python-tests:\n"
        )
        result=validate_action_pinning_text(text)
        self.assertFalse(result["valid"])
        self.assertEqual(result["violations"][0]["reason"],"unapproved_action_revision")

    def test_local_action_is_fail_closed(self):
        result=validate_action_pinning_text("jobs:\n  validate:\n    steps:\n      - uses: ./local-action\n")
        self.assertFalse(result["valid"])
        self.assertEqual(result["violations"][0]["reason"],"local_action_not_allowlisted")

    def test_workflow_permissions_are_exact_least_privilege(self):
        result=validate_workflow_permissions_text("permissions:\n  contents: read\njobs:\n")
        self.assertTrue(result["valid"],result)
        self.assertEqual(result["workflow_permissions"],{"contents":"read"})

    def test_workflow_write_permission_is_rejected(self):
        result=validate_workflow_permissions_text("permissions:\n  contents: write\njobs:\n")
        self.assertFalse(result["valid"])
        self.assertEqual(result["violations"][0]["reason"],"workflow_permissions_not_exact")

    def test_extra_sensitive_permission_is_rejected(self):
        result=validate_workflow_permissions_text(
            "permissions:\n  contents: read\n  id-token: write\njobs:\n"
        )
        self.assertFalse(result["valid"])

    def test_job_permission_override_is_rejected(self):
        result=validate_workflow_permissions_text(
            "permissions:\n"
            "  contents: read\n"
            "jobs:\n"
            "  validate:\n"
            "    permissions:\n"
            "      contents: write\n"
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["violations"][-1]["reason"],"job_permissions_override_forbidden")

    def test_missing_explicit_permissions_is_rejected(self):
        result=validate_workflow_permissions_text("name: CI\njobs:\n  validate:\n")
        self.assertFalse(result["valid"])
        self.assertIsNone(result["workflow_permissions"])

    def test_runtime_policy_accepts_repository_ci(self):
        root=Path(__file__).resolve().parents[1]
        result=validate_workflow_runtime_text((root/".github/workflows/ci.yml").read_text())
        self.assertTrue(result["valid"],result)

    def test_pull_request_target_is_rejected(self):
        result=validate_workflow_runtime_text("on:\n  pull_request_target:\njobs:\n")
        self.assertFalse(result["valid"])

    def test_container_is_rejected(self):
        result=validate_workflow_runtime_text("jobs:\n  validate:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n    container: python:3.12\n")
        self.assertFalse(result["valid"])

    def test_secret_expression_is_rejected(self):
        result=validate_workflow_runtime_text("jobs:\n  validate:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n    env:\n      TOKEN: ${{ secrets.TOKEN }}\n")
        self.assertFalse(result["valid"])

    def test_required_runner_and_timeout_are_exact(self):
        result=validate_workflow_runtime_text("jobs:\n  validate:\n    runs-on: self-hosted\n    timeout-minutes: 30\n  python-tests:\n    runs-on: ubuntu-latest\n    timeout-minutes: 20\n")
        self.assertFalse(result["valid"])
        reasons={v["reason"] for v in result["violations"]}
        self.assertIn("untrusted_job_runner",reasons)
        self.assertIn("job_timeout_not_exact",reasons)

    def test_expression_policy_rejects_untrusted_contexts(self):
        result=validate_workflow_expression_policy_text("jobs:\n  validate:\n    env:\n      X: ${{ github.event.pull_request.title }}\n")
        self.assertFalse(result["valid"])
        self.assertTrue(any(v["reason"]=="forbidden_expression_context" for v in result["violations"]))

    def test_matrix_strategy_is_rejected(self):
        result=validate_workflow_expression_policy_text("jobs:\n  validate:\n    strategy:\n      matrix:\n        python: [3.12]\n")
        self.assertFalse(result["valid"])
        self.assertTrue(any(v.get("key")=="strategy" for v in result["violations"]))

    def test_job_needs_and_if_are_rejected(self):
        result=validate_workflow_expression_policy_text("jobs:\n  validate:\n    needs: build\n    if: success()\n")
        self.assertFalse(result["valid"])
        keys={v.get("key") for v in result["violations"]}
        self.assertIn("needs",keys)
        self.assertIn("if",keys)

    def test_continue_on_error_is_rejected(self):
        result=validate_workflow_expression_policy_text("jobs:\n  validate:\n    continue-on-error: true\n")
        self.assertFalse(result["valid"])

    def test_static_safe_workflow_has_no_expression_violations(self):
        root=Path(__file__).resolve().parents[1]
        result=validate_workflow_expression_policy_text((root/".github/workflows/ci.yml").read_text())
        self.assertTrue(result["valid"],result)

    def test_run_policy_accepts_repository_ci(self):
        root=Path(__file__).resolve().parents[1]
        result=validate_workflow_run_commands_text((root/".github/workflows/ci.yml").read_text())
        self.assertTrue(result["valid"],result)

    def test_run_policy_rejects_network_download(self):
        result=validate_workflow_run_commands_text("jobs:\n  validate:\n    steps:\n      - run: curl https://example.invalid/file\n")
        self.assertFalse(result["valid"])

    def test_run_policy_rejects_runtime_dependency_install(self):
        result=validate_workflow_run_commands_text("jobs:\n  validate:\n    steps:\n      - run: pip install example\n")
        self.assertFalse(result["valid"])

    def test_run_policy_rejects_github_command_file(self):
        result=validate_workflow_run_commands_text("jobs:\n  validate:\n    steps:\n      - run: echo X=1 >> $GITHUB_ENV\n")
        self.assertFalse(result["valid"])

    def test_run_policy_rejects_expression_in_command(self):
        result=validate_workflow_run_commands_text("jobs:\n  validate:\n    steps:\n      - run: echo ${{ github.ref }}\n")
        self.assertFalse(result["valid"])

    def test_run_policy_rejects_untrusted_shell(self):
        result=validate_workflow_run_commands_text("jobs:\n  validate:\n    steps:\n      - shell: pwsh\n        run: echo ok\n")
        self.assertFalse(result["valid"])

    def test_yaml_surface_rejects_anchors_aliases_and_merge_keys(self):
        for text in ("x: &base value\n","x: *base\n","<<: *base\n"):
            result=validate_yaml_surface_text(text)
            self.assertFalse(result["valid"],result)

    def test_yaml_surface_rejects_tags(self):
        result=validate_yaml_surface_text("value: !custom thing\n")
        self.assertFalse(result["valid"])

    def test_yaml_surface_rejects_duplicate_mapping_keys(self):
        result=validate_yaml_surface_text("permissions:\n  contents: read\n  contents: write\n")
        self.assertFalse(result["valid"])
        self.assertTrue(any(v["reason"]=="duplicate_key" for v in result["violations"]))

    def test_yaml_surface_rejects_tab_indentation(self):
        result=validate_yaml_surface_text("jobs:\n\tvalidate:\n")
        self.assertFalse(result["valid"])

    def test_repository_ci_yaml_surface_is_unambiguous(self):
        root=Path(__file__).resolve().parents[1]
        result=validate_yaml_surface_text((root/".github/workflows/ci.yml").read_text())
        self.assertTrue(result["valid"],result)

    def test_schema_rejects_unknown_root_job_and_step_keys(self):
        samples=(
            "name: CI\nunknown: true\n",
            "jobs:\n  validate:\n    runs-on: ubuntu-latest\n    mystery: true\n",
            "jobs:\n  validate:\n    steps:\n      - mystery: true\n",
        )
        for text in samples:
            result=validate_workflow_schema_text(text)
            self.assertFalse(result["valid"],result)

    def test_schema_accepts_repository_ci(self):
        root=Path(__file__).resolve().parents[1]
        result=validate_workflow_schema_text((root/".github/workflows/ci.yml").read_text())
        self.assertTrue(result["valid"],result)

    def test_schema_allowlists_are_reported(self):
        result=validate_workflow_schema_text("name: CI\n")
        self.assertEqual(result["allowed_root_keys"],["concurrency","jobs","name","on","permissions"])
        self.assertIn("runs-on",result["allowed_job_keys"])
        self.assertIn("uses",result["allowed_step_keys"])

    def test_step_inputs_env_accepts_repository_ci(self):
        root=Path(__file__).resolve().parents[1]
        result=validate_step_inputs_env_text((root/".github/workflows/ci.yml").read_text())
        self.assertTrue(result["valid"],result)

    def test_setup_python_only_accepts_312(self):
        text="jobs:\n  validate:\n    steps:\n      - name: Setup\n        uses: actions/setup-python@sha\n        with:\n          python-version: \"3.13\"\n"
        result=validate_step_inputs_env_text(text)
        self.assertFalse(result["valid"])
        self.assertEqual(result["violations"][0]["reason"],"unapproved_action_input_value")

    def test_unknown_action_input_is_rejected(self):
        text="jobs:\n  validate:\n    steps:\n      - name: Setup\n        uses: actions/setup-python@sha\n        with:\n          cache: pip\n"
        result=validate_step_inputs_env_text(text)
        self.assertFalse(result["valid"])

    def test_checkout_inputs_are_fail_closed(self):
        text="jobs:\n  validate:\n    steps:\n      - name: Checkout\n        uses: actions/checkout@sha\n        with:\n          persist-credentials: true\n"
        result=validate_step_inputs_env_text(text)
        self.assertFalse(result["valid"])

    def test_run_env_only_allows_static_pythonpath(self):
        good="jobs:\n  validate:\n    steps:\n      - name: Test\n        env:\n          PYTHONPATH: studio\n        run: python -m unittest\n"
        bad="jobs:\n  validate:\n    steps:\n      - name: Test\n        env:\n          TOKEN: value\n        run: python -m unittest\n"
        self.assertTrue(validate_step_inputs_env_text(good)["valid"])
        self.assertFalse(validate_step_inputs_env_text(bad)["valid"])

    def test_trigger_concurrency_accepts_repository_ci(self):
        root=Path(__file__).resolve().parents[1]
        result=validate_trigger_concurrency_text((root/".github/workflows/ci.yml").read_text())
        self.assertTrue(result["valid"],result)

    def test_extra_trigger_is_rejected(self):
        text="on:\n  push:\n    branches: [\"main\"]\n  pull_request:\n  workflow_dispatch:\nconcurrency:\n  group: ci-${{ github.workflow }}-${{ github.ref }}\n  cancel-in-progress: true\n"
        self.assertFalse(validate_trigger_concurrency_text(text)["valid"])

    def test_non_main_push_branch_is_rejected(self):
        text="on:\n  push:\n    branches: [\"dev\"]\n  pull_request:\nconcurrency:\n  group: ci-${{ github.workflow }}-${{ github.ref }}\n  cancel-in-progress: true\n"
        self.assertFalse(validate_trigger_concurrency_text(text)["valid"])

    def test_concurrency_group_must_be_exact(self):
        text="on:\n  push:\n    branches: [\"main\"]\n  pull_request:\nconcurrency:\n  group: arbitrary\n  cancel-in-progress: true\n"
        self.assertFalse(validate_trigger_concurrency_text(text)["valid"])

    def test_concurrency_cancellation_must_be_enabled(self):
        text="on:\n  push:\n    branches: [\"main\"]\n  pull_request:\nconcurrency:\n  group: ci-${{ github.workflow }}-${{ github.ref }}\n  cancel-in-progress: false\n"
        self.assertFalse(validate_trigger_concurrency_text(text)["valid"])

    def test_exact_job_steps_accept_repository_ci(self):
        root=Path(__file__).resolve().parents[1]
        result=validate_exact_job_steps_text((root/".github/workflows/ci.yml").read_text())
        self.assertTrue(result["valid"],result)

    def test_exact_job_steps_reject_extra_job(self):
        root=Path(__file__).resolve().parents[1]
        text=(root/".github/workflows/ci.yml").read_text()+"\n  surprise:\n    runs-on: ubuntu-latest\n    steps:\n      - name: Surprise\n        run: echo nope\n"
        self.assertFalse(validate_exact_job_steps_text(text)["valid"])

    def test_exact_job_steps_reject_reordered_steps(self):
        root=Path(__file__).resolve().parents[1]
        text=(root/".github/workflows/ci.yml").read_text()
        text=text.replace("      - name: Checkout\n        uses: actions/checkout@", "      - name: Checkout changed\n        uses: actions/checkout@",1)
        self.assertFalse(validate_exact_job_steps_text(text)["valid"])

    def test_exact_job_steps_reject_changed_command(self):
        root=Path(__file__).resolve().parents[1]
        text=(root/".github/workflows/ci.yml").read_text().replace("python -m compileall -q studio tests","python -m compileall studio tests")
        self.assertFalse(validate_exact_job_steps_text(text)["valid"])

    def test_semantic_digest_is_stable_for_repository_ci(self):
        root=Path(__file__).resolve().parents[1]
        text=(root/".github/workflows/ci.yml").read_text()
        first=workflow_semantic_manifest_text(text)
        second=workflow_semantic_manifest_text(text)
        self.assertTrue(first["valid"],first)
        self.assertEqual(first["digest"],second["digest"])
        self.assertEqual(len(first["digest"]),64)

    def test_validate_workflow_exposes_semantic_digest(self):
        root=Path(__file__).resolve().parents[1]
        result=validate_workflow(root/".github/workflows/ci.yml")
        self.assertTrue(result["valid"],result)
        self.assertEqual(len(result["semantic_digest"]),64)
        self.assertEqual(result["semantic_manifest"]["workflow_name"],"CI")

    def test_semantic_digest_refuses_untrusted_workflow(self):
        result=workflow_semantic_manifest_text("name: Other\njobs:\n")
        self.assertFalse(result["valid"])
        self.assertIsNone(result["digest"])

if __name__=="__main__":
    unittest.main()

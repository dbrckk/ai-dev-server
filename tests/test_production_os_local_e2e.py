import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from production_os_worker import main, run_once
from github_goal_store import load as FakeGitHubGoalLoad, persist_local, restore_local
from goal_engine import new_goal, record_cycle, finalize, load as load_goal, save as save_goal
from capability_registry import new_registry, save as save_registry
from improvement_backlog import new_backlog, save as save_backlog
from test_github_goal_store import FakeGitHub
from autonomous_project import run_persistent_project


class _ControlPlane:
    def __init__(self, jobs=None):
        self.calls = []
        self.job_claimed = False
        self.jobs = list(jobs) if jobs is not None else None
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                return

            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length) or b"{}")
                outer.calls.append(
                    {
                        "path": self.path,
                        "authorization": self.headers.get("Authorization"),
                        "payload": payload,
                    }
                )

                if self.path in {"/v1/workers/register", "/v1/workers/session"}:
                    body = {"worker": {"worker_id": payload["worker_id"]}}
                    self._send(200, body)
                    return

                if self.path == "/v1/jobs/claim":
                    if outer.jobs is not None:
                        if not outer.jobs:
                            self._send(204, None)
                        else:
                            self._send(200, {"job": outer.jobs.pop(0)})
                        return
                    if outer.job_claimed:
                        self._send(204, None)
                        return
                    outer.job_claimed = True
                    self._send(
                        200,
                        {
                            "job": {
                                "key": "job-e2e-001",
                                "repository": "dbrckk/e2e-fixture",
                                "task": "Create enemy sprites and integrate them into the Android game",
                                "payload": {
                                    "workflow_id": "e" * 32,
                                    "workflow_task_id": "acceptance",
                                    "handoff": {
                                        "repository": "dbrckk/e2e-fixture",
                                        "task": "Create enemy sprites and integrate them into the Android game",
                                        "final_goal": "Create enemy sprites and integrate them into the Android game",
                                        "agent_preference": "codex",
                                        "token_budget": 5000,
                                    },
                                },
                            }
                        },
                    )
                    return

                if self.path in {
                    "/v1/jobs/ack",
                    "/v1/workers/heartbeat",
                    "/v1/jobs/complete",
                    "/v1/jobs/fail",
                }:
                    self._send(200, {"ok": True})
                    return

                self._send(404, {"error": "not found"})

            def _send(self, status, body):
                self.send_response(status)
                if body is None:
                    self.end_headers()
                    return
                encoded = json.dumps(body).encode("utf-8")
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            name="production-os-e2e-control-plane",
            daemon=True,
        )

    @property
    def url(self):
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2.0)


class ProductionOSLocalE2ETests(unittest.TestCase):
    def test_worker_completes_real_http_control_plane_cycle(self):
        with _ControlPlane() as control_plane, tempfile.TemporaryDirectory() as td:
            output_root = Path(td)

            def runner(request_path, project_out, **kwargs):
                request = json.loads(
                    Path(request_path).read_text(encoding="utf-8")
                )
                envelope = {
                    "schema_version": "ai-dev-server/production-os-result/v1",
                    "workflow_id": request["production_os"]["workflow_id"],
                    "workflow_task_id": request["production_os"]["workflow_task_id"],
                    "project_id": request["id"],
                    "target_repo": request["target_repo"],
                    "status": "complete",
                    "succeeded": True,
                    "usage": {
                        "input_tokens": 120,
                        "cached_input_tokens": 20,
                        "output_tokens": 30,
                        "reasoning_tokens": 5,
                        "total_tokens": 150,
                        "runs": 1,
                        "agents": {"codex": 1},
                    },
                    "evidence": {
                        "pipeline_status": "complete",
                        "next_stage": None,
                        "finished": True,
                    },
                }
                (Path(project_out) / "production-os-result.json").write_text(
                    json.dumps(envelope, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8",
                )
                return {
                    "status": "complete",
                    "finished": True,
                    "usage": envelope["usage"],
                }

            def execute_once(client, **kwargs):
                return run_once(
                    client,
                    run_project=runner,
                    heartbeat_interval_seconds=60.0,
                    **kwargs,
                )

            rc = main(
                [
                    "--worker-id",
                    "ai-dev-e2e",
                    "--once",
                    "--output-root",
                    str(output_root),
                ],
                environ={
                    "PRODUCTION_OS_URL": control_plane.url,
                    "PRODUCTION_OS_WORKER_TOKEN": "worker-e2e-secret",
                    "PRODUCTION_OS_OPERATOR_TOKEN": "operator-e2e-secret",
                },
                run_once_fn=execute_once,
                capacity_provider=lambda env: None,
                capabilities_provider=lambda env: [
                    "android",
                    "node",
                    "python",
                    "repo-analysis",
                    "software-development",
                    "visual-asset-production",
                ],
            )

            self.assertEqual(rc, 0)

            request_files = list(
                output_root.glob("*/production-os-request.json")
            )
            result_files = list(
                output_root.glob("*/production-os-result.json")
            )
            self.assertEqual(len(request_files), 1)
            self.assertEqual(len(result_files), 1)

            request = json.loads(
                request_files[0].read_text(encoding="utf-8")
            )
            result = json.loads(
                result_files[0].read_text(encoding="utf-8")
            )
            self.assertEqual(
                request["production_os"],
                {
                    "workflow_id": "e" * 32,
                    "workflow_task_id": "acceptance",
                },
            )
            self.assertIn("dbrckk/asset-forge", request["brief"])
            self.assertIn("asset-forge fulfill", request["brief"])
            self.assertEqual(result["workflow_id"], "e" * 32)
            self.assertEqual(result["workflow_task_id"], "acceptance")

        paths = [call["path"] for call in control_plane.calls]
        self.assertEqual(
            paths,
            [
                "/v1/workers/register",
                "/v1/workers/heartbeat",
                "/v1/jobs/claim",
                "/v1/jobs/ack",
                "/v1/workers/heartbeat",
                "/v1/jobs/complete",
                "/v1/workers/heartbeat",
            ],
        )

        register = control_plane.calls[0]
        self.assertEqual(
            register["authorization"],
            "Bearer operator-e2e-secret",
        )
        self.assertIn("android", register["payload"]["capabilities"])
        self.assertIn(
            "visual-asset-production",
            register["payload"]["capabilities"],
        )
        for call in control_plane.calls[1:]:
            self.assertEqual(
                call["authorization"],
                "Bearer worker-e2e-secret",
            )

        complete = next(
            call for call in control_plane.calls
            if call["path"] == "/v1/jobs/complete"
        )
        self.assertEqual(complete["payload"]["key"], "job-e2e-001")
        self.assertEqual(
            complete["payload"]["result"]["usage"]["total_tokens"],
            150,
        )
        self.assertEqual(
            complete["payload"]["result"]["evidence"]["pipeline_status"],
            "complete",
        )


    def test_two_separate_worker_sessions_restore_verified_partial_progress(self):
        """A new workflow queue key must not restart an already checkpointed goal."""
        def task_job(key, attempt):
            return {
                "key": key,
                "repository": "dbrckk/e2e-fixture",
                "task": "Build, validate, and ship the existing project",
                "payload": {
                    "workflow_id": "d" * 32,
                    "workflow_task_id": "implementation",
                    "workflow_attempt": attempt,
                    "handoff": {
                        "repository": "dbrckk/e2e-fixture",
                        "task": "Build, validate, and ship the existing project",
                        "final_goal": "Ship the verified build",
                        "agent_preference": "codex",
                        "token_budget": 5000,
                        **({
                            "retry_context": {"summary": "continuation_limit: retry"}
                        } if attempt > 1 else {}),
                    },
                },
            }

        remote = FakeGitHub()
        projects = []
        builds = []
        restored_attempts = []
        statuses = []
        jobs = [task_job("session-job-01", 1), task_job("session-job-02", 2)]

        def runner(request_path, project_out, **kwargs):
            request = json.loads(Path(request_path).read_text(encoding="utf-8"))
            project_out = Path(project_out)
            projects.append(request)
            goal_path = project_out / ".autonomy" / "goal.json"
            if len(projects) == 1:
                self.assertFalse(restore_local(remote, request["id"], project_out))
                state = new_goal(
                    request["id"], "Ship the verified build",
                    [{"name": "release", "required_evidence": ["build", "tests"]}],
                    max_attempts=5,
                )
                state = record_cycle(state, evidence={"build": "sha-build-once"})
                save_goal(goal_path, state)
                save_registry(project_out / ".autonomy/capabilities.json", new_registry())
                save_backlog(project_out / ".autonomy/improvement-backlog.json", new_backlog())
                persist_local(remote, request["id"], project_out)
                builds.append("sha-build-once")
                return {
                    "status": "active", "finished": False,
                    "next_stage": "tests",
                    "usage": {"total_tokens": 12},
                }

            # The second GitHub Actions session starts on a fresh disk.
            self.assertFalse(goal_path.exists())
            self.assertTrue(restore_local(remote, request["id"], project_out))
            state = load_goal(goal_path)
            restored_attempts.append(state["attempt"])
            self.assertEqual(state["evidence"], {"build": "sha-build-once"})
            self.assertEqual(state["status"], "active")
            self.assertEqual(len(builds), 1, "build must not be repeated")
            completed = finalize(
                record_cycle(state, evidence={"tests": "validated"})
            )
            save_goal(goal_path, completed)
            persist_local(remote, request["id"], project_out)
            return {
                "status": "complete", "finished": True,
                "next_stage": None,
                "usage": {"total_tokens": 25},
            }

        def execute_once(client, **kwargs):
            return run_once(
                client, run_project=runner,
                heartbeat_interval_seconds=60.0,
                **kwargs,
            )

        with _ControlPlane(jobs=jobs) as plane, tempfile.TemporaryDirectory() as td:
            # Distinct local session roots emulate GitHub's ephemeral runners.
            for attempt in (1, 2):
                result = main(
                    [
                        "--worker-id", "github-actions-worker",
                        "--once",
                        "--max-continuations", "0",
                        "--output-root", str(Path(td) / f"runner-{attempt}"),
                    ],
                    environ={
                        "PRODUCTION_OS_URL": plane.url,
                        "PRODUCTION_OS_WORKER_TOKEN": "worker-e2e-secret",
                    },
                    run_once_fn=execute_once,
                    capacity_provider=lambda env: None,
                    capabilities_provider=lambda env: ["python"],
                )
                statuses.append(result)

            self.assertEqual(statuses, [1, 0])
            self.assertEqual(len(projects), 2)
            self.assertEqual(projects[0]["id"], projects[1]["id"])
            self.assertNotEqual(projects[0]["brief"], projects[1]["brief"])
            self.assertEqual(restored_attempts, [1])
            self.assertEqual(builds, ["sha-build-once"])
            result_files = list(Path(td).rglob("production-os-result.json"))
            self.assertEqual(len(result_files), 2)
            results = [
                json.loads(p.read_text(encoding="utf-8"))
                for p in result_files
            ]
            self.assertEqual(
                sorted(row["succeeded"] for row in results), [False, True]
            )
            final_goal = load_goal(
                next(Path(td).glob("runner-2/*/.autonomy/goal.json"))
            )
            self.assertEqual(final_goal["status"], "complete")
            self.assertEqual(final_goal["attempt"], 2)
            remote_final = FakeGitHubGoalLoad(remote, projects[0]["id"])
            self.assertEqual(remote_final["goal"]["status"], "complete")
            self.assertEqual(remote_final["goal"]["attempt"], 2)

        paths = [c["path"] for c in plane.calls]
        self.assertEqual(paths.count("/v1/jobs/fail"), 1)
        self.assertEqual(paths.count("/v1/jobs/complete"), 1)
        self.assertEqual(paths.count("/v1/workers/session"), 2)
        self.assertEqual(paths.count("/v1/jobs/claim"), 2)
        self.assertNotEqual(
            next(c for c in plane.calls if c["path"] == "/v1/jobs/fail")[
                "payload"]["key"],
            next(c for c in plane.calls if c["path"] == "/v1/jobs/complete")[
                "payload"]["key"],
        )


    def test_crash_after_remote_cycle_checkpoint_resumes_on_fresh_disk(self):
        """Remote state survives a crash before normal end-of-run persistence."""
        remote = FakeGitHub()
        project_id = "two-session-crash-proof"
        executions = []
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first_out = root / "first-runner"

            def step(*args):
                executions.append("first")
                return {"status": "failed", "report": {}, "next_stage": "verify"}

            def persist_then_crash(state, result):
                self.assertEqual(
                    load_goal(first_out / ".autonomy/goal.json"), state,
                )
                persist_local(remote, project_id, first_out)
                raise RuntimeError("runner unexpectedly terminated")

            with self.assertRaisesRegex(RuntimeError, "runner unexpectedly terminated"):
                run_persistent_project(
                    "request.json", first_out, str(root / "work1"),
                    runner=lambda *args: None, deadline=100, clock=lambda: 0,
                    goal_id=project_id,
                    run_once=step, max_cycles=4,
                    checkpoint_observer=persist_then_crash,
                )

            remote_partial = FakeGitHubGoalLoad(remote, project_id)
            self.assertIsNotNone(remote_partial)
            self.assertEqual(remote_partial["goal"]["attempt"], 1)
            self.assertEqual(remote_partial["goal"]["status"], "active")

            # GitHub Actions starts a different runner with no local project files.
            second_out = root / "second-runner"
            self.assertFalse((second_out / ".autonomy/goal.json").exists())
            self.assertTrue(restore_local(remote, project_id, second_out))
            restored = load_goal(second_out / ".autonomy/goal.json")
            self.assertEqual(restored, remote_partial["goal"])

            def resumed_step(*args):
                executions.append("resumed")
                return {
                    "status": "complete",
                    "report": {
                        "completion": {"finished": True},
                        "release_status": "store_ready",
                    },
                    "next_stage": None,
                }

            result = run_persistent_project(
                "request.json", second_out, str(root / "work2"),
                runner=lambda *args: None, deadline=100, clock=lambda: 0,
                goal_id=project_id,
                run_once=resumed_step, max_cycles=2,
                checkpoint_observer=lambda state, value: persist_local(
                    remote, project_id, second_out,
                ),
            )
            self.assertEqual(result["status"], "complete")
            self.assertEqual(executions, ["first", "resumed"])
            self.assertEqual(result["attempt"], 2)
            final = FakeGitHubGoalLoad(remote, project_id)
            self.assertEqual(final["goal"]["status"], "complete")
            self.assertEqual(final["goal"]["attempt"], 2)



if __name__ == "__main__":
    unittest.main()

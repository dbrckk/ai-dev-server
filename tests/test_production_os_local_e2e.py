import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from production_os_worker import main, run_once


class _ControlPlane:
    def __init__(self):
        self.calls = []
        self.job_claimed = False
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

                if self.path == "/v1/workers/register":
                    body = {"worker": {"worker_id": payload["worker_id"]}}
                    self._send(200, body)
                    return

                if self.path == "/v1/jobs/claim":
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
                                "task": "Verify Production-OS bridge end to end",
                                "payload": {
                                    "workflow_id": "e" * 32,
                                    "workflow_task_id": "acceptance",
                                    "handoff": {
                                        "repository": "dbrckk/e2e-fixture",
                                        "task": "Verify Production-OS bridge end to end",
                                        "final_goal": "Verify Production-OS bridge end to end",
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
            )

            self.assertEqual(rc, 0)

        paths = [call["path"] for call in control_plane.calls]
        self.assertEqual(
            paths,
            [
                "/v1/workers/register",
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

        request_files = list(output_root.glob("*/production-os-request.json"))
        result_files = list(output_root.glob("*/production-os-result.json"))
        self.assertEqual(len(request_files), 1)
        self.assertEqual(len(result_files), 1)

        request = json.loads(request_files[0].read_text(encoding="utf-8"))
        result = json.loads(result_files[0].read_text(encoding="utf-8"))
        self.assertEqual(
            request["production_os"],
            {
                "workflow_id": "e" * 32,
                "workflow_task_id": "acceptance",
            },
        )
        self.assertEqual(result["workflow_id"], "e" * 32)
        self.assertEqual(result["workflow_task_id"], "acceptance")


if __name__ == "__main__":
    unittest.main()

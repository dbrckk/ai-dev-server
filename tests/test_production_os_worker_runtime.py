import io
import json
import tempfile
import threading
import unittest
from unittest.mock import patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from production_os_worker import (
    ProductionOSClient,
    ProductionOSWorkerError,
    run_once,
    worker_capabilities,
)


def sample_job():
    return {
        "key": "job-abc123",
        "repository": "dbrckk/example",
        "task": "Ship the final verified version",
        "payload": {
            "workflow_id": "f" * 32,
            "workflow_task_id": "goal",
            "handoff": {
                "repository": "dbrckk/example",
                "task": "Ship the final verified version",
                "final_goal": "Ship the final verified version",
                "agent_preference": "codex",
                "token_budget": 250000,
            },
        },
    }


class _FakeClient:
    def __init__(self, job):
        self.job = job
        self.calls = []

    def claim(self, worker_id, capabilities):
        self.calls.append(("claim", worker_id, tuple(capabilities)))
        return self.job

    def ack(self, key, worker_id):
        self.calls.append(("ack", key, worker_id))

    def complete(self, payload):
        self.calls.append(("complete", payload))

    def fail(self, payload):
        self.calls.append(("fail", payload))

    def heartbeat(self, worker_id, *, active_job_keys=(), capacity=None):
        self.calls.append(
            ("heartbeat", worker_id, tuple(active_job_keys), capacity)
        )


class _Response:
    def __init__(self, status, payload=None):
        self.status = status
        self._body = (
            b""
            if payload is None
            else json.dumps(payload).encode("utf-8")
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, limit=-1):
        return self._body if limit < 0 else self._body[:limit]




class ProductionOSWorkerRuntimeTests(unittest.TestCase):
    def test_worker_capabilities_require_ready_visual_backend(self):
        with patch("production_os_worker.shutil.which", return_value=None):
            caps = worker_capabilities(
                {"POLLINATIONS_API_KEY": "secret"},
                home=Path("/definitely/not/real"),
            )
        self.assertEqual(caps, ["android", "node", "python", "repo-analysis", "software-development"])

        with patch("production_os_worker.shutil.which", return_value="/usr/bin/polli"):
            caps = worker_capabilities(
                {"POLLINATIONS_API_KEY": "secret"},
                home=Path("/definitely/not/real"),
            )
        self.assertIn("visual-asset-production", caps)
        self.assertIn("visual-asset-3d-production", caps)

    def test_client_rejects_insecure_remote_control_plane(self):
        with self.assertRaisesRegex(
            ProductionOSWorkerError,
            "HTTPS",
        ):
            ProductionOSClient(
                "http://example.com:8787",
                "secret",
            )

    def test_client_allows_loopback_http(self):
        client = ProductionOSClient(
            "http://127.0.0.1:8787",
            "secret",
        )
        self.assertEqual(client.base_url, "http://127.0.0.1:8787")


    def test_client_claim_posts_bearer_json_and_handles_no_content(self):
        seen = []

        def opener(request, timeout):
            seen.append({
                "url": request.full_url,
                "method": request.get_method(),
                "authorization": request.get_header("Authorization"),
                "content_type": request.get_header("Content-type"),
                "body": json.loads(request.data.decode("utf-8")),
                "timeout": timeout,
            })
            return _Response(
                200,
                {"job": sample_job()},
            )

        client = ProductionOSClient(
            "http://127.0.0.1:8787",
            "worker-secret",
            opener=opener,
        )
        job = client.claim(
            "ai-dev-1",
            ["software-development", "repo-analysis"],
        )

        self.assertEqual(job["key"], "job-abc123")
        self.assertEqual(
            seen[0]["url"],
            "http://127.0.0.1:8787/v1/jobs/claim",
        )
        self.assertEqual(seen[0]["method"], "POST")
        self.assertEqual(
            seen[0]["authorization"],
            "Bearer worker-secret",
        )
        self.assertEqual(
            seen[0]["body"]["worker_id"],
            "ai-dev-1",
        )

        client = ProductionOSClient(
            "http://127.0.0.1:8787",
            "worker-secret",
            opener=lambda request, timeout: _Response(204),
        )
        self.assertIsNone(
            client.claim(
                "ai-dev-1",
                ["software-development"],
            )
        )

    def test_run_once_returns_idle_when_no_job_is_available(self):
        client = _FakeClient(None)

        result = run_once(
            client,
            worker_id="ai-dev-1",
            output_root=Path("unused"),
            run_project=lambda *args, **kwargs: self.fail("runner must not execute"),
            capabilities=[
                "android",
                "node",
                "python",
                "repo-analysis",
                "software-development",
                "visual-asset-production",
            ],
        )

        self.assertEqual(result["status"], "idle")
        self.assertEqual(client.calls[0][0], "claim")
        self.assertIn("visual-asset-production", client.calls[0][2])

    def test_run_once_acks_executes_and_completes_with_usage(self):
        client = _FakeClient(sample_job())

        def runner(request_path, out, **kwargs):
            request = json.loads(Path(request_path).read_text(encoding="utf-8"))
            self.assertEqual(request["agent_preference"], "codex")
            self.assertEqual(
                request["production_os"]["workflow_task_id"],
                "goal",
            )
            return {
                "status": "complete",
                "finished": True,
                "next_stage": None,
                "usage": {
                    "input_tokens": 100,
                    "cached_input_tokens": 20,
                    "output_tokens": 30,
                    "reasoning_tokens": 7,
                    "total_tokens": 130,
                    "runs": 1,
                    "agents": {"codex": 1},
                },
            }

        with tempfile.TemporaryDirectory() as td:
            result = run_once(
                client,
                worker_id="ai-dev-1",
                output_root=Path(td),
                run_project=runner,
                clock=lambda: 10.0,
            )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(
            [call[0] for call in client.calls],
            ["claim", "ack", "heartbeat", "complete", "heartbeat"],
        )
        completed = client.calls[3][1]
        self.assertEqual(completed["key"], "job-abc123")
        self.assertEqual(completed["result"]["usage"]["total_tokens"], 130)

    def test_run_once_reports_failed_pipeline_to_control_plane(self):
        client = _FakeClient(sample_job())

        def runner(request_path, out, **kwargs):
            return {
                "status": "blocked",
                "finished": False,
                "next_stage": "human_action",
                "usage": {"total_tokens": 55},
            }

        with tempfile.TemporaryDirectory() as td:
            result = run_once(
                client,
                worker_id="ai-dev-1",
                output_root=Path(td),
                run_project=runner,
                clock=lambda: 20.0,
            )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(
            [call[0] for call in client.calls],
            ["claim", "ack", "heartbeat", "fail", "heartbeat"],
        )
        failed = client.calls[3][1]
        self.assertEqual(failed["result"]["usage"]["total_tokens"], 55)
        self.assertIn("blocked", failed["reason"])



    def test_run_once_refreshes_heartbeat_during_long_runner_execution(self):
        client = _FakeClient(sample_job())
        refreshed = threading.Event()
        original_heartbeat = client.heartbeat
        active_heartbeats = {"count": 0}

        def heartbeat(worker_id, *, active_job_keys=(), capacity=None):
            original_heartbeat(
                worker_id,
                active_job_keys=active_job_keys,
                capacity=capacity,
            )
            if active_job_keys:
                active_heartbeats["count"] += 1
                if active_heartbeats["count"] >= 2:
                    refreshed.set()

        client.heartbeat = heartbeat

        def runner(request_path, out, **kwargs):
            self.assertTrue(
                refreshed.wait(0.5),
                "periodic heartbeat was not sent while runner was active",
            )
            return {
                "status": "complete",
                "finished": True,
                "next_stage": None,
                "usage": {"total_tokens": 1},
            }

        with tempfile.TemporaryDirectory() as td:
            result = run_once(
                client,
                worker_id="ai-dev-1",
                output_root=Path(td),
                run_project=runner,
                clock=lambda: 10.0,
                heartbeat_interval_seconds=0.01,
            )

        self.assertEqual(result["status"], "completed")
        self.assertGreaterEqual(active_heartbeats["count"], 2)
        self.assertEqual(client.calls[-1][0], "heartbeat")
        self.assertEqual(client.calls[-1][2], ())


    def test_run_once_reports_runner_exception_and_clears_active_job(self):
        client = _FakeClient(sample_job())

        def runner(request_path, out, **kwargs):
            raise RuntimeError("codex crashed")

        with tempfile.TemporaryDirectory() as td:
            result = run_once(
                client,
                worker_id="ai-dev-1",
                output_root=Path(td),
                run_project=runner,
                clock=lambda: 30.0,
            )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(
            [call[0] for call in client.calls],
            ["claim", "ack", "heartbeat", "fail", "heartbeat"],
        )
        failed = client.calls[3][1]
        self.assertEqual(failed["key"], "job-abc123")
        self.assertIn("runner_error", failed["reason"])
        self.assertIn("RuntimeError", failed["result"]["evidence"]["error_type"])
        self.assertEqual(client.calls[4][2], ())

    def test_capacity_snapshot_prefers_authenticated_omniroute(self):
        from production_os_worker import production_capacity_snapshot

        class Snapshot:
            authenticated_usage = True
            steady_recurring_tokens = 1_500_000_000
            used_this_month = 125_000_000
            remaining_tokens = 1_375_000_000
            catalog_updated_at = "2026-09-18"
            catalog_source = "free-tier-catalog"

        seen = {}

        def fetch(url, *, api_key=None, timeout=5.0):
            seen["url"] = url
            seen["api_key"] = api_key
            seen["timeout"] = timeout
            return Snapshot()

        result = production_capacity_snapshot(
            {
                "OMNIROUTE_URL": "http://127.0.0.1:20128",
                "OMNIROUTE_API_KEY": "secret",
            },
            fetch_summary=fetch,
        )

        self.assertEqual(result["source"], "omniroute")
        self.assertTrue(result["authenticated_usage"])
        self.assertEqual(result["steady_recurring_tokens"], 1_500_000_000)
        self.assertEqual(result["remaining_tokens"], 1_375_000_000)
        self.assertEqual(seen["api_key"], "secret")
        self.assertNotIn("secret", json.dumps(result))

    def test_capacity_snapshot_fails_closed_without_authenticated_usage(self):
        from production_os_worker import production_capacity_snapshot

        class Snapshot:
            authenticated_usage = False
            steady_recurring_tokens = 1_500_000_000
            used_this_month = None
            remaining_tokens = None
            catalog_updated_at = "2026-09-18"
            catalog_source = "free-tier-catalog"

        result = production_capacity_snapshot(
            {"OMNIROUTE_URL": "http://127.0.0.1:20128"},
            fetch_summary=lambda *args, **kwargs: Snapshot(),
        )

        self.assertEqual(result["source"], "omniroute")
        self.assertEqual(result["status"], "unavailable")
        self.assertFalse(result["authenticated_usage"])
        self.assertIsNone(result["remaining_tokens"])


    def test_client_heartbeat_posts_capacity_snapshot(self):
        seen = []

        def opener(request, timeout):
            seen.append(json.loads(request.data.decode("utf-8")))
            return _Response(
                200,
                {
                    "worker": {
                        "worker_id": "ai-dev-1",
                        "capacity": seen[-1].get("capacity"),
                    },
                    "stale_job_keys": [],
                },
            )

        client = ProductionOSClient(
            "http://127.0.0.1:8787",
            "worker-secret",
            opener=opener,
        )
        capacity = {
            "source": "omniroute",
            "status": "ok",
            "authenticated_usage": True,
            "steady_recurring_tokens": 1_500_000_000,
            "used_this_month": 125_000_000,
            "remaining_tokens": 1_375_000_000,
            "catalog_updated_at": "2026-09-18",
            "catalog_source": "free-tier-catalog",
        }

        client.heartbeat(
            "ai-dev-1",
            active_job_keys=(),
            capacity=capacity,
        )

        self.assertEqual(seen[0]["capacity"], capacity)


    def test_run_once_writes_project_token_envelope_before_execution(self):
        client = _FakeClient(sample_job())
        capacity = {
            "source": "omniroute",
            "status": "ok",
            "authenticated_usage": True,
            "remaining_tokens": 1_375_000_000,
        }

        def runner(request_path, out, **kwargs):
            request = json.loads(Path(request_path).read_text(encoding="utf-8"))
            plan = json.loads(
                (Path(out).parent / "capacity-plan.json").read_text(
                    encoding="utf-8"
                )
            )
            row = next(
                item for item in plan["projects"]
                if item["id"] == request["id"]
            )
            self.assertEqual(row["requested_tokens"], 250000)
            self.assertEqual(row["token_envelope"], 250000)
            self.assertEqual(row["budget_source"], "production-os")
            self.assertEqual(row["capacity_source"], "omniroute")
            return {
                "status": "complete",
                "finished": True,
                "next_stage": None,
                "usage": {"total_tokens": 100},
            }

        with tempfile.TemporaryDirectory() as td:
            result = run_once(
                client,
                worker_id="ai-dev-1",
                output_root=Path(td),
                run_project=runner,
                clock=lambda: 10.0,
                capacity=capacity,
            )

        self.assertEqual(result["status"], "completed")

    def test_project_token_envelope_is_capped_by_live_global_remaining_capacity(self):
        client = _FakeClient(sample_job())
        capacity = {
            "source": "omniroute",
            "status": "ok",
            "authenticated_usage": True,
            "remaining_tokens": 100000,
        }

        def runner(request_path, out, **kwargs):
            request = json.loads(Path(request_path).read_text(encoding="utf-8"))
            plan = json.loads(
                (Path(out).parent / "capacity-plan.json").read_text(
                    encoding="utf-8"
                )
            )
            row = next(
                item for item in plan["projects"]
                if item["id"] == request["id"]
            )
            self.assertEqual(row["requested_tokens"], 250000)
            self.assertEqual(row["token_envelope"], 100000)
            self.assertTrue(row["constrained"])
            return {
                "status": "complete",
                "finished": True,
                "next_stage": None,
                "usage": {"total_tokens": 100},
            }

        with tempfile.TemporaryDirectory() as td:
            result = run_once(
                client,
                worker_id="ai-dev-1",
                output_root=Path(td),
                run_project=runner,
                clock=lambda: 10.0,
                capacity=capacity,
            )

        self.assertEqual(result["status"], "completed")


if __name__ == "__main__":
    unittest.main()

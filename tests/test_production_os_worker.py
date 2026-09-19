import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import request_check
from production_os_worker import (
    build_studio_request,
    completion_payload,
    failure_payload,
)


class ProductionOSWorkerTests(unittest.TestCase):
    def job(self):
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

    def test_build_studio_request_preserves_goal_and_workflow_correlation(self):
        request = build_studio_request(self.job())

        checked = request_check(request)
        self.assertEqual(checked["target_repo"], "dbrckk/example")
        self.assertEqual(
            checked["brief"],
            "Ship the final verified version",
        )
        self.assertEqual(
            checked["production_os"],
            {
                "workflow_id": "f" * 32,
                "workflow_task_id": "goal",
            },
        )
        self.assertEqual(request["agent_preference"], "codex")
        self.assertTrue(request["id"].startswith("pos-"))
        self.assertLessEqual(len(request["id"]), 48)

    def test_visual_reuse_adds_asset_forge_guidance(self):
        job = self.job()
        job["payload"]["handoff"]["reuse_candidates"] = [
            {
                "source": "dbrckk/asset-forge",
                "target": "dbrckk/example",
                "capability": "visual-asset-pipeline",
            }
        ]

        request = build_studio_request(job)

        self.assertIn("dbrckk/asset-forge", request["brief"])
        self.assertIn("asset-forge/production-request/v1", request["brief"])
        request_check(request)

    def test_short_task_is_expanded_to_valid_studio_brief(self):
        job = self.job()
        job["task"] = "Fix CI"
        job["payload"]["handoff"]["task"] = "Fix CI"
        job["payload"]["handoff"]["final_goal"] = "Fix CI"

        request = build_studio_request(job)

        self.assertGreaterEqual(len(request["brief"]), 20)
        self.assertIn("Fix CI", request["brief"])
        request_check(request)

    def test_completion_payload_forwards_usage_and_evidence(self):
        result = {
            "schema_version": "ai-dev-server/production-os-result/v1",
            "workflow_id": "f" * 32,
            "workflow_task_id": "goal",
            "status": "complete",
            "succeeded": True,
            "usage": {
                "input_tokens": 100,
                "cached_input_tokens": 20,
                "output_tokens": 30,
                "reasoning_tokens": 7,
                "total_tokens": 130,
                "runs": 1,
                "agents": {"codex": 1},
            },
            "evidence": {
                "pipeline_status": "complete",
                "next_stage": None,
                "finished": True,
            },
        }

        payload = completion_payload(
            "job-abc123",
            "ai-dev-1",
            result,
            duration_seconds=12.5,
        )

        self.assertEqual(payload["key"], "job-abc123")
        self.assertEqual(payload["worker_id"], "ai-dev-1")
        self.assertEqual(payload["duration_seconds"], 12.5)
        self.assertEqual(payload["result"]["usage"]["total_tokens"], 130)
        self.assertEqual(
            payload["result"]["evidence"]["pipeline_status"],
            "complete",
        )

    def test_failure_payload_is_bounded_and_preserves_usage(self):
        result = {
            "status": "blocked",
            "succeeded": False,
            "usage": {"total_tokens": 42},
            "evidence": {"next_stage": "human_action"},
        }

        payload = failure_payload(
            "job-abc123",
            "ai-dev-1",
            result,
            duration_seconds=4.0,
        )

        self.assertEqual(payload["key"], "job-abc123")
        self.assertEqual(payload["worker_id"], "ai-dev-1")
        self.assertEqual(payload["result"]["usage"]["total_tokens"], 42)
        self.assertIn("blocked", payload["reason"])


if __name__ == "__main__":
    unittest.main()

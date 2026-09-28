import json
import os
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError, request_check
from production_os_worker import (
    build_studio_request,
    completion_payload,
    failure_payload,
    _production_os_model_route,
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

    def test_build_studio_request_sanitizes_production_os_model_route(self):
        job = self.job()
        job["payload"]["handoff"]["model_route"] = {
            "schema_version":"production-os/model-route/v1",
            "provider":"cloudflare",
            "model":"qwen-code",
            "fallbacks":[
                {"provider":"ollama","model":"qwen-local"},
            ],
            "ranking":[
                {
                    "provider":"cloudflare",
                    "model":"qwen-code",
                    "score":42,
                },
            ],
            "rejected":[
                {
                    "provider":"paid",
                    "model":"expensive",
                    "reason":"provider quota is exhausted",
                },
            ],
        }

        request = build_studio_request(job)
        checked = request_check(request)

        self.assertEqual(
            checked["model_route"],
            {
                "schema_version":"production-os/model-route/v1",
                "provider":"cloudflare",
                "model":"qwen-code",
                "fallbacks":[
                    {"provider":"ollama","model":"qwen-local"},
                ],
            },
        )
        self.assertNotIn("ranking", checked["model_route"])
        self.assertNotIn("rejected", checked["model_route"])

    def test_build_studio_request_rejects_secret_bearing_route_fields(self):
        job = self.job()
        job["payload"]["handoff"]["model_route"] = {
            "schema_version":"production-os/model-route/v1",
            "provider":"cloudflare",
            "model":"qwen-code",
            "fallbacks":[],
            "api_key":"secret",
        }

        with self.assertRaises(StudioError):
            build_studio_request(job)

    def test_model_route_environment_is_scoped_and_restored(self):
        route = {
            "schema_version":"production-os/model-route/v1",
            "provider":"cloudflare",
            "model":"qwen-code",
            "fallbacks":[],
        }
        os.environ["STUDIO_PRODUCTION_OS_MODEL_ROUTE"] = "previous"
        try:
            with _production_os_model_route(route):
                current = json.loads(
                    os.environ["STUDIO_PRODUCTION_OS_MODEL_ROUTE"]
                )
                self.assertEqual(current["provider"], "cloudflare")
                self.assertEqual(current["model"], "qwen-code")
            self.assertEqual(
                os.environ["STUDIO_PRODUCTION_OS_MODEL_ROUTE"],
                "previous",
            )
        finally:
            os.environ.pop("STUDIO_PRODUCTION_OS_MODEL_ROUTE", None)

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

    def test_explicit_visual_task_adds_asset_forge_guidance_without_reuse_metadata(self):
        job = self.job()
        job["task"] = "Create enemy sprites and integrate them"
        job["payload"]["handoff"]["task"] = "Create enemy sprites and integrate them"
        job["payload"]["handoff"]["final_goal"] = "Create enemy sprites and integrate them"
        job["payload"]["handoff"].pop("reuse_candidates", None)

        request = build_studio_request(job)

        self.assertIn("dbrckk/asset-forge", request["brief"])
        self.assertIn("asset-forge operational-status", request["brief"])
        self.assertIn("rasterPng", request["brief"])
        self.assertIn("automatic backend selection", request["brief"])
        self.assertIn("asset-forge fulfill", request["brief"])
        request_check(request)

    def test_french_visual_task_adds_asset_forge_guidance(self):
        job = self.job()
        job["task"] = "Améliore les graphismes et les icônes du jeu"
        job["payload"]["handoff"]["task"] = "Améliore les graphismes et les icônes du jeu"
        job["payload"]["handoff"]["final_goal"] = "Améliore les graphismes et les icônes du jeu"
        job["payload"]["handoff"].pop("reuse_candidates", None)

        request = build_studio_request(job)

        self.assertIn("dbrckk/asset-forge", request["brief"])
        self.assertIn("asset-forge fulfill", request["brief"])
        request_check(request)

    def test_structured_asset_forge_contract_enables_guidance_without_keywords(self):
        job = self.job()
        job["payload"]["handoff"]["task"] = "Complete media task"
        job["payload"]["handoff"]["final_goal"] = "Complete media task"
        job["payload"]["handoff"]["tool_contracts"] = {
            "asset_forge": {
                "request_schema": "asset-forge/production-request/v1",
                "report_schema": "asset-forge/production-report/v1",
                "command": "asset-forge fulfill",
                "required_capability": "visual-asset-production",
            }
        }

        request = build_studio_request(job)

        self.assertIn("dbrckk/asset-forge", request["brief"])
        self.assertIn("asset-forge fulfill", request["brief"])
        self.assertEqual(
            request["tool_contracts"],
            job["payload"]["handoff"]["tool_contracts"],
        )
        checked = request_check(request)
        self.assertEqual(
            checked["tool_contracts"]["asset_forge"]["command"],
            "asset-forge fulfill",
        )

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
                "visual_assets": {
                    "quality_status": "regenerated",
                    "checked": 2,
                    "regenerated": 1,
                    "minimum_score": 0.79,
                },
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
        self.assertEqual(
            payload["result"]["evidence"]["visual_assets"]["quality_status"],
            "regenerated",
        )
        self.assertEqual(
            payload["result"]["evidence"]["visual_assets"]["minimum_score"],
            0.79,
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

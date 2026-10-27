"""Integrity and ordering guarantees for intra-cycle published-round checkpoints."""
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from execution_checkpoint import (
    ExecutionCheckpointError,
    advance, load, new,
)
from generic_project import _save_published_checkpoint, run_project


class GenericPublishedCheckpointTests(unittest.TestCase):
    def test_observer_reads_sealed_checkpoint_after_verified_round(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / ".autonomy/generic-execution-checkpoint.json"
            checkpoint = advance(
                new("demo-project", "generic", "a" * 40),
                base_sha="b" * 40,
                round_index=2,
                phase="published",
                last_verification={"passed": True, "checks": 3},
            )
            observed = []

            def observer(value):
                self.assertEqual(load(path), checkpoint)
                self.assertEqual(value, checkpoint)
                observed.append(value)

            _save_published_checkpoint(path, checkpoint, observer)
            self.assertEqual(observed, [checkpoint])
            self.assertEqual(load(path)["base_sha"], "b" * 40)

    def test_unpublished_phase_is_rejected_and_not_persisted(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "checkpoint.json"
            checkpoint = advance(
                new("demo-project", "generic", "a" * 40),
                round_index=1,
                phase="planned",
            )
            seen = []
            with self.assertRaisesRegex(
                ExecutionCheckpointError, "only published rounds",
            ):
                _save_published_checkpoint(path, checkpoint, seen.append)
            self.assertFalse(path.exists())
            self.assertEqual(seen, [])

    def test_remote_persistence_failure_stops_after_local_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "checkpoint.json"
            checkpoint = advance(
                new("demo-project", "generic", "a" * 40),
                round_index=1,
                phase="complete",
                last_verification={"passed": True},
            )

            def failure(_value):
                raise RuntimeError("remote checkpoint rejected")

            with self.assertRaisesRegex(RuntimeError, "remote checkpoint rejected"):
                _save_published_checkpoint(path, checkpoint, failure)
            self.assertEqual(load(path), checkpoint)

    def test_real_generic_canary_path_mirrors_only_after_sealed_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out"
            out.mkdir()
            checkpoint_path = out / ".autonomy/generic-execution-checkpoint.json"
            observed = []
            proof = {"passed": True, "reason": "existing verified contract"}
            with patch("generic_project.GitHub"), patch(
                "generic_project.GenericRepository",
            ) as repository, patch(
                "generic_project._existing_worker_canary_verification",
                return_value=proof,
            ):
                repository.return_value.restore.return_value = (
                    "a" * 40, {"status": "restored"},
                )

                repository.return_value.ensure_pull_request.return_value = {
                    "number": 1, "state": "open", "url": "https://github.com/owner/app/pull/1",
                }

                def observer(value):
                    repository.return_value.ensure_pull_request.assert_called_once_with(
                        title="Review resumed Production-OS worker canary",
                        body="Verified existing marker; review the restored checkpoint before merging.",
                        expected_sha="a" * 40,
                    )
                    self.assertEqual(load(checkpoint_path), value)
                    observed.append(value)

                result = run_project(
                    {"id": "demo", "target_repo": "owner/app"},
                    out,
                    Path(temp) / "work",
                    checkpoint_observer=observer,
                )
            self.assertEqual(result["status"], "complete")
            self.assertEqual(len(observed), 1)
            self.assertEqual(observed[0]["phase"], "complete")
            self.assertEqual(observed[0]["last_verification"], proof)

    def test_missing_observer_keeps_original_local_behavior(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "checkpoint.json"
            checkpoint = advance(
                new("demo-project", "generic", "a" * 40),
                round_index=1,
                phase="published",
                last_verification={"passed": False},
            )
            _save_published_checkpoint(path, checkpoint)
            self.assertEqual(load(path), checkpoint)

        # A completed implementation with failed PR publication must resume
        # delivery only, preserving its exact commit and avoiding model work.
        from core import StudioError
        from generic_delivery import deliver
        from autonomous_project import translate_orchestrator_result
        from source_delivery_checkpoint import SourceCheckpointError
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out"
            out.mkdir()
            request = {"id": "managed", "target_repo": "owner/app", "brief": "Fix parsing",
                       "production_os": {"workflow_id": "1" * 32, "workflow_task_id": "implementation", "objective_sha256": "a" * 64}}
            checkpoint = advance(new("managed", "generic", "a" * 40),
                                 base_sha="b" * 40, round_index=1, phase="published",
                                 last_verification={"passed": True})
            with patch("generic_project.GitHub"), patch("generic_project.GenericRepository") as factory, \
                 patch("generic_delivery.inspect_ci", return_value={"status": "pending", "reason": "exact_commit_ci_in_progress"}) as ci, \
                 patch("generic_project.ask", side_effect=AssertionError("delivery must not invoke model")) as model:
                repo = factory.return_value
                repo.restore.return_value = ("b" * 40, {"files": 1})
                repo.delivery_head.return_value = "b" * 40
                repo.ensure_pull_request.side_effect = StudioError("API HTTP 403")
                for outcome in ("not_configured", "rejected", "missing_token", "invalid_branch"):
                    repo.request_trusted_review_handoff.return_value = {"status": outcome}
                    blocked = deliver(request, repo, checkpoint, {"rounds": []}, out)
                    self.assertEqual(blocked["status"], "human_action_required")
                    self.assertEqual(blocked["report"]["ci"]["reason"], "review_handoff_" + outcome)
                repo.request_trusted_review_handoff.reset_mock()
                repo.request_trusted_review_handoff.return_value = {"status": "unavailable"}
                pending = deliver(request, repo, checkpoint, {"rounds": []}, out)
                self.assertEqual(pending["status"], "deferred")
                self.assertFalse(pending["report"]["completion"]["finished"])
                self.assertEqual(translate_orchestrator_result(pending), {"yield_run": True})
                saved_path = out / ".autonomy/generic-execution-checkpoint.json"
                self.assertEqual(load(saved_path)["phase"], "published")
                pending_again = run_project({**request, "brief": request["brief"] + " Retry publication"},
                                            out, Path(temp) / "retry")
                self.assertEqual(pending_again["status"], "deferred")
                repo.request_trusted_review_handoff.assert_called_once()
                started = load(saved_path)["last_verification"]["managed_review_delivery"]["review_wait_started"]
                with patch("generic_delivery.time.time", return_value=started + 3601):
                    expired = run_project(request, out, Path(temp) / "expired-review")
                self.assertEqual(expired["status"], "human_action_required")
                self.assertEqual(expired["report"]["ci"]["reason"], "review_handoff_wait_expired")
                repo.ensure_pull_request.side_effect = None
                repo.ensure_pull_request.return_value = {
                    "number": 3, "state": "open", "url": "https://github.com/owner/app/pull/3"}
                ci.return_value = {"status": "pending", "reason": "exact_commit_ci_not_started", "workflow_id": 7}
                with patch("generic_delivery.dispatch_ci", return_value={"status": "unavailable", "reason": "CI_dispatch_HTTP_403"}) as dispatch:
                    awaiting_ci = run_project(request, out, Path(temp) / "ci-wait")
                    started_ci = load(saved_path)["last_verification"]["managed_review_delivery"]["ci_wait_started"]
                    with patch("generic_delivery.time.time", return_value=started_ci + 59):
                        handoff_starting_ci = run_project(request, out, Path(temp) / "handoff-starting-ci")
                    self.assertEqual(handoff_starting_ci["status"], "deferred")
                    dispatch.assert_not_called()
                self.assertEqual(awaiting_ci["status"], "deferred")
                receipt = load(saved_path)["last_verification"]["managed_review_delivery"]
                self.assertTrue(receipt["review_confirmed"])
                self.assertIsNotNone(receipt["ci_wait_started"])
                self.assertFalse(awaiting_ci["report"]["completion"]["finished"])
                self.assertEqual(translate_orchestrator_result(awaiting_ci), {"yield_run": True})
                from core import APIError
                for outage in (APIError(503), StudioError("API unavailable or timed out")):
                    ci.side_effect = outage
                    unavailable = run_project(request, out, Path(temp) / "ci-outage")
                    self.assertEqual(unavailable["status"], "deferred")
                    self.assertFalse(unavailable["report"]["completion"]["finished"])
                ci.side_effect = None
                ci.return_value = {"status": "passed", "sha": "b" * 40}
                for outage in (APIError(503), StudioError("API unavailable or timed out")):
                    repo._find_open_pull_request.side_effect = outage
                    review_unavailable = run_project(request, out, Path(temp) / "review-outage-after-ci")
                    self.assertEqual(review_unavailable["status"], "deferred")
                    self.assertEqual(review_unavailable["report"]["ci"]["reason"], "review_temporarily_unavailable_after_CI")
                    self.assertFalse(review_unavailable["report"]["completion"]["finished"])
                repo._find_open_pull_request.side_effect = None
                complete = run_project(request, out, Path(temp) / "resume")
                self.assertEqual(complete["status"], "complete")
                self.assertEqual(load(saved_path)["phase"], "complete")
                self.assertEqual(complete["report"]["checkpoint_commit"], "b" * 40)
                self.assertEqual(repo.ensure_pull_request.call_args.kwargs["expected_sha"], "b" * 40)
                model.assert_not_called()
                repo.publish.assert_not_called()
                repo.restore.assert_not_called()
                ci.return_value = {"status": "failed", "reason": "independent_CI_failed", "failed_jobs": ["test"]}
                failed = run_project(request, out, Path(temp) / "ci-failed")
                self.assertEqual(failed["next_stage"], "generic_ci_repair")
                self.assertIn("failure", translate_orchestrator_result(failed))
                from generic_delivery import resumable
                self.assertFalse(resumable(load(saved_path), request, "b" * 40))
                self.assertFalse(load(saved_path)["last_verification"]["passed"])
                with self.assertRaises(SourceCheckpointError):
                    run_project({**request, "production_os": {**request["production_os"],
                                "objective_sha256": "c" * 64}}, out, Path(temp) / "changed")
                repo.restore.return_value = ("c" * 40, {"files": 1})
                repo.delivery_head.return_value = "c" * 40
                with self.assertRaises(SourceCheckpointError):
                    run_project(request, out, Path(temp) / "moved")


if __name__ == "__main__":
    unittest.main()

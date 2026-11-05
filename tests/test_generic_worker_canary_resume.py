import os
import hashlib
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from generic_project import _existing_worker_canary_verification, run_project
from production_os_review_canary import contract as review_contract, run as run_review_canary
from production_os_worker_canary import canary_instruction, validate_control
from core import StudioError


class ExistingWorkerCanaryVerificationTests(unittest.TestCase):
    def _request(self, sequence=2):
        return {
            "target_repo": "dbrckk/repo-standards",
            "production_os": {
                "workflow_id": "1" * 32,
                "workflow_task_id": "implementation",
            },
            "brief": (
                f"Production-OS worker canary {sequence}. "
                "Make exactly one intentional product-file change: "
                f"create .production-os/worker-canary-{sequence}.txt "
                "containing exactly one line: "
                f"production-os-worker-canary sequence {sequence}. "
                "Do not change dependencies, workflows, secrets, configuration, "
                "or existing source files. Previous autonomous attempt failed."
            ),
        }

    def test_accepts_exact_existing_canary_with_or_without_final_newline(self):
        for suffix in ("", "\n"):
            with self.subTest(suffix=repr(suffix)), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                target = root / ".production-os" / "worker-canary-2.txt"
                target.parent.mkdir(parents=True)
                target.write_text(
                    "production-os-worker-canary sequence 2" + suffix,
                    encoding="utf-8",
                )
                result = _existing_worker_canary_verification(
                    self._request(),
                    root,
                )
                self.assertIsNotNone(result)
                self.assertTrue(result["passed"])
                self.assertEqual(result["status"], "passed")
                self.assertEqual(
                    result["files"][0]["path"],
                    ".production-os/worker-canary-2.txt",
                )

                # A restored marker must still reach review at its exact SHA.
                for index, failure in enumerate((None, "API HTTP 403", "Generic review pull request head revision unverified", "confirmed handoff", "pending handoff")):
                    with self.subTest(failure=failure), patch.dict(os.environ), patch(
                        "generic_project.GitHub"
                    ), patch("generic_project.GenericRepository") as repository, patch(
                        "generic_delivery.inspect_ci", return_value={"status": "passed", "sha": "a" * 40}
                    ) as ci:
                        repo = repository.return_value
                        repo.restore.return_value = ("a" * 40, {"files": 1})
                        repo.delivery_head.return_value = "a" * 40
                        repo.branch = "studio/canary-resume"
                        repo.ensure_pull_request.side_effect = StudioError(
                            "API HTTP 403" if failure in {"confirmed handoff", "pending handoff"} else failure
                        ) if failure else None
                        repo.ensure_pull_request.return_value = {
                            "number": 7, "state": "open",
                            "url": "https://github.com/dbrckk/repo-standards/pull/7",
                        }
                        handoff = failure in {"confirmed handoff", "pending handoff"}
                        delivered = failure is None or failure == "confirmed handoff"
                        repo.request_trusted_review_handoff.return_value = {"status": "accepted" if handoff else "unavailable"}
                        repo.await_trusted_review.return_value = (
                            repo.ensure_pull_request.return_value if delivered else None
                        )
                        observed = []
                        request = {**self._request(), "id": "canary-resume"}
                        outcome = run_project(request, root / ("output-" + str(index)), root,
                                              checkpoint_observer=observed.append)
                        expected = "human_action_required" if failure == "Generic review pull request head revision unverified" else "deferred"
                        self.assertEqual(outcome["status"], "complete" if delivered else expected)
                        self.assertEqual(outcome["report"]["completion"]["finished"], delivered)
                        self.assertEqual(observed[-1]["phase"], "complete" if delivered else "published")
                        self.assertEqual(repo.ensure_pull_request.call_args.kwargs["expected_sha"], "a" * 40)
                        repo.publish.assert_not_called()
                        self.assertEqual(ci.call_count, 1 if delivered else 0)
                        if handoff:
                            repo.await_trusted_review.assert_called_once_with("a" * 40)

    def test_rejects_wrong_content(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / ".production-os" / "worker-canary-2.txt"
            target.parent.mkdir(parents=True)
            target.write_text("wrong", encoding="utf-8")
            self.assertIsNone(
                _existing_worker_canary_verification(self._request(), root)
            )

    def test_rejects_non_canary_repository_or_missing_contract(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / ".production-os" / "worker-canary-2.txt"
            target.parent.mkdir(parents=True)
            target.write_text(
                "production-os-worker-canary sequence 2",
                encoding="utf-8",
            )
            wrong_repo = self._request()
            wrong_repo["target_repo"] = "dbrckk/other"
            self.assertIsNone(
                _existing_worker_canary_verification(wrong_repo, root)
            )
            incomplete = self._request()
            incomplete["brief"] = "Production-OS worker canary 2."
            self.assertIsNone(
                _existing_worker_canary_verification(incomplete, root)
            )

        # The old live canary #48 produced ls.txt and passed only a
        # structural text check. It must not be published or replayed as a
        # verified exact marker, even when the checkpoint says "passed".
        from generic_delivery import require_exact_canary_evidence, resumable, _fingerprint
        from generic_project import _require_exact_canary_workspace
        from execution_checkpoint import advance, new
        from source_delivery_checkpoint import SourceCheckpointError

        sequence = 48
        request = {**self._request(sequence), "id": "pos-canary-48",
                   "target_repo": "dbrckk/ai-dev-server",
                   "brief": canary_instruction(sequence)}
        expected_path = ".production-os/worker-canary-48.txt"
        expected_content = b"production-os-worker-canary sequence 48\n"
        verified = {
            "passed": True, "status": "passed", "structural_only": True,
            "files": [{
                "path": expected_path, "bytes": len(expected_content),
                "sha256": hashlib.sha256(expected_content).hexdigest(),
            }],
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "ls.txt").write_text("list of top-level entries", encoding="utf-8")
            with self.assertRaisesRegex(StudioError, "changed-file scope"):
                _require_exact_canary_workspace(request, root, ["ls.txt"])
            with self.assertRaisesRegex(SourceCheckpointError, "changed-file scope"):
                require_exact_canary_evidence(request, verified, ["ls.txt"])

            target = root / expected_path
            target.parent.mkdir(parents=True)
            target.write_bytes(b"wrong")
            with self.assertRaisesRegex(StudioError, "content verification"):
                _require_exact_canary_workspace(request, root, [expected_path])
            target.write_bytes(expected_content)
            _require_exact_canary_workspace(request, root, [expected_path])
            require_exact_canary_evidence(request, verified, [expected_path])
            tampered = {**verified, "files": [{
                **verified["files"][0], "sha256": hashlib.sha256(b"wrong").hexdigest(),
            }]}
            with self.assertRaisesRegex(SourceCheckpointError, "content verification"):
                require_exact_canary_evidence(request, tampered, [expected_path])
            invalid_brief = {**request, "brief": request["brief"] + " Also create ls.txt."}
            with self.assertRaisesRegex(SourceCheckpointError, "instruction"):
                require_exact_canary_evidence(invalid_brief, verified, [expected_path])

            receipt = {
                "request_fingerprint": _fingerprint(request),
                "implementation_complete": True, "changed_files": [expected_path],
            }
            checkpoint = advance(
                new(request["id"], "generic", "a" * 40),
                base_sha="b" * 40, round_index=1, phase="published",
                last_verification={
                    **verified, "managed_review_delivery": receipt,
                },
            )
            self.assertTrue(resumable(checkpoint, request, "b" * 40))
            bad_checkpoint = advance(
                checkpoint, last_verification={
                    **verified, "managed_review_delivery": {
                        **receipt, "changed_files": ["ls.txt"],
                    },
                },
            )
            with self.assertRaisesRegex(SourceCheckpointError, "changed-file scope"):
                resumable(bad_checkpoint, request, "b" * 40)

        # The producer and both consumers must agree at the inclusive limit.
        for sequence in (1, 999_999_999, 1_000_000_000, 0, 1_000_000_001):
            with self.subTest(sequence=sequence), tempfile.TemporaryDirectory() as td:
                valid = 1 <= sequence <= 1_000_000_000
                control = {"sequence": sequence, "repository": "dbrckk/Jumpy"}
                if valid:
                    self.assertEqual(validate_control(control)[0], sequence)
                else:
                    with self.assertRaises(ValueError):
                        validate_control(control)
                request = self._request(sequence)
                request["brief"] = canary_instruction(sequence)
                relative = f".production-os/worker-canary-{sequence}.txt"
                line = f"production-os-worker-canary sequence {sequence}"
                root = Path(td)
                target = root / relative
                target.parent.mkdir(parents=True)
                target.write_text(line + "\n", encoding="utf-8")
                self.assertEqual(
                    _existing_worker_canary_verification(request, root) is not None,
                    valid,
                )
                request["target_repo"] = "dbrckk/Jumpy"
                self.assertEqual(review_contract(request), (relative, line) if valid else None)
                request["target_repo"] = "dbrckk/ai-dev-server"
                self.assertEqual(review_contract(request), (relative, line) if valid else None)

        # Extend the existing canary regression: Jumpy's exact marker-only
        # request must bypass the expensive Godot game-production pipeline.
        # Nearby or adversarial instructions keep normal engine routing.
        seq = 30
        path = f".production-os/worker-canary-{seq}.txt"
        line = f"production-os-worker-canary sequence {seq}"
        brief = (
            f"Production-OS worker canary {seq}. "
            f"Make exactly one intentional product-file change: create {path} "
            f"containing exactly one line: {line}. "
            "Do not change dependencies, workflows, secrets, configuration, "
            "or existing source files. Verify the file content, persist the normal "
            "autonomous checkpoint branch, and finish the task successfully."
        )
        req = {
            "id": "mp-" + "a" * 24,
            "target_repo": "dbrckk/Jumpy",
            "brief": brief,
            "production_os": {"workflow_id": "1" * 32, "workflow_task_id": "implementation"},
        }
        self.assertEqual(review_contract(req), (path, line))
        # The same exact, finite contract may exercise the target repository's
        # GitHub transport without asking a model to invent a marker file.
        ai_dev_request = {**req, "target_repo": "dbrckk/ai-dev-server"}
        self.assertEqual(review_contract(ai_dev_request), (path, line))
        self.assertIsNone(review_contract({
            **ai_dev_request, "brief": brief + " Also write ls.txt."
        }))
        self.assertIsNone(review_contract({**req, "brief": brief + " Also modify scripts."}))
        self.assertIsNone(review_contract({**req, "target_repo": "stranger/Jumpy"}))
        self.assertIsNone(review_contract({**req, "production_os": {}}))
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out"
            work = Path(temp) / "work"
            published = "b" * 40
            observed = []
            with patch("production_os_review_canary.GitHub"), patch(
                "production_os_review_canary.GenericRepository"
            ) as repository:
                instance = repository.return_value
                instance.restore.return_value = ("a" * 40, {"files": 3})
                instance.publish.return_value = published
                instance.branch = "studio/mp-" + "a" * 24
                instance.ensure_pull_request.return_value = {
                    "number": 42, "state": "open",
                    "url": "https://github.com/dbrckk/Jumpy/pull/42",
                }
                instance.await_trusted_review.return_value = {
                    "number": 42, "state": "open",
                    "url": "https://github.com/dbrckk/Jumpy/pull/42",
                    "handoff_confirmed": True,
                }
                result = run_review_canary(
                    req, out, work, checkpoint_observer=observed.append,
                )
                self.assertEqual((work / path).read_bytes(), (line + "\n").encode())
                self.assertEqual(instance.publish.call_count, 1)
                self.assertEqual([entry["phase"] for entry in observed], ["published", "complete"])
                self.assertEqual(result["status"], "complete")
                self.assertEqual(result["report"]["checkpoint_commit"], published)
                self.assertEqual(result["report"]["pull_request"]["number"], 42)
                instance.await_trusted_review.assert_called_once_with(published)
                self.assertEqual(result["report"]["rounds"][0]["changed_files"], [path])
                # A restarted worker must reuse the exact already-published
                # marker without creating another commit or spending tokens.
                instance.restore.return_value = (published, {"files": 3})
                resumed = run_review_canary(
                    req, Path(temp) / "resumed-out", work,
                )
                self.assertEqual(resumed["status"], "complete")
                self.assertEqual(resumed["report"]["checkpoint_commit"], published)
                instance.publish.assert_called_once()
                # AI Dev Server uses the same restricted real Git transport.
                # The PR URL must match this repository, never Jumpy.
                instance.restore.return_value = ("a" * 40, {"files": 3})
                instance.await_trusted_review.return_value = {
                    "number": 44, "state": "open",
                    "url": "https://github.com/dbrckk/ai-dev-server/pull/44",
                    "handoff_confirmed": True,
                }
                ai_delivered = run_review_canary(
                    ai_dev_request, Path(temp) / "ai-out",
                    Path(temp) / "ai-work",
                )
                self.assertEqual(ai_delivered["status"], "complete")
                self.assertEqual(
                    ai_delivered["report"]["rounds"][0]["changed_files"], [path],
                )
                self.assertEqual(ai_delivered["report"]["pull_request"]["number"], 44)
                # An old PR number/URL without this exact published commit
                # must not finish the delivery canary.
                instance.await_trusted_review.return_value = None
                rejected = run_review_canary(
                    req, Path(temp) / "unverified-out",
                    Path(temp) / "unverified-work",
                )
                self.assertEqual(rejected["status"], "blocked")
                self.assertEqual(
                    rejected["report"]["pull_request"]["reason"],
                    "review_commit_unverified",
                )
                self.assertFalse(rejected["report"]["completion"]["finished"])
        with tempfile.TemporaryDirectory() as temp:
            with patch("production_os_review_canary.GitHub"), patch(
                "production_os_review_canary.GenericRepository"
            ) as repository:
                instance = repository.return_value
                instance.restore.return_value = ("a" * 40, {"files": 3})
                instance.publish.return_value = "b" * 40
                instance.branch = "studio/mp-" + "a" * 24
                instance.ensure_pull_request.side_effect = StudioError("API HTTP 403")
                instance.request_trusted_review_handoff.return_value = {"status": "accepted"}
                instance.await_trusted_review.return_value = {
                    "number": 43, "state": "open",
                    "url": "https://github.com/dbrckk/Jumpy/pull/43",
                    "handoff_confirmed": True,
                }
                result = run_review_canary(
                    req, Path(temp) / "out", Path(temp) / "work",
                )
                self.assertEqual(result["status"], "complete")
                instance.request_trusted_review_handoff.assert_called_once_with("b" * 40)
                instance.await_trusted_review.assert_called_once_with("b" * 40)
                self.assertEqual(result["report"]["pull_request"]["number"], 43)
                instance.await_trusted_review.return_value = None
                result = run_review_canary(
                    req, Path(temp) / "out2", Path(temp) / "work2",
                )
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["report"]["pull_request"]["state"], "unavailable")
                self.assertFalse(result["report"]["completion"]["finished"])


if __name__ == "__main__":
    unittest.main()

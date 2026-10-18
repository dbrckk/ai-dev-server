import sys
from pathlib import Path

import unittest
import tempfile
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError, request_check
from generic_repository import GenericRepository


BASE = {
    "id":"pos-123",
    "target_repo":"owner/repo",
    "app_name":"sample_app",
    "brief":"Implement the requested change safely and verify it.",
    "enabled":True,
}


class RepositoryBranchIdentityTests(unittest.TestCase):
    def test_request_check_accepts_safe_repository_branch_identity(self):
        request = dict(BASE)
        request["repository_branch_id"] = "mp-abcdef123456"

        checked = request_check(request)

        self.assertEqual(checked["id"], "pos-123")
        self.assertEqual(
            checked["repository_branch_id"],
            "mp-abcdef123456",
        )

    def test_request_check_rejects_unsafe_repository_branch_identity(self):
        request = dict(BASE)
        request["repository_branch_id"] = "../main"

        with self.assertRaisesRegex(
            StudioError,
            "Invalid repository_branch_id",
        ):
            request_check(request)

    def test_generic_repository_branch_is_independent_from_execution_request_id(self):
        repository = GenericRepository(
            github=object(),
            repo="owner/repo",
            project_id="mp-abcdef123456",
        )

        self.assertEqual(
            repository.branch,
            "studio/mp-abcdef123456",
        )

        # Extend the existing branch-identity contract: a successful ref
        # mutation cannot mark a checkpoint as published until GitHub reads
        # back the exact new commit from the managed branch.
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text("Changed\\n", encoding="utf-8")
            base_sha, commit_sha = "a" * 40, "b" * 40
            tree_sha = "c" * 40
            github = Mock()
            github.repo = "/repos/owner/repo"
            current = {"sha": base_sha}

            def get(path):
                if path == "/git/commits/" + base_sha:
                    return {"tree": {"sha": tree_sha}}
                if path == "/git/matching-refs/heads/studio/mp-abcdef123456":
                    return [{"ref": "refs/heads/studio/mp-abcdef123456",
                             "object": {"sha": current["sha"]}}]
                raise AssertionError(path)

            def call(method, path, payload):
                if path.endswith("/git/trees"):
                    return {"sha": tree_sha}
                if path.endswith("/git/commits"):
                    return {"sha": commit_sha}
                if path.endswith("/git/refs/heads/studio/mp-abcdef123456"):
                    if current["sha"] != base_sha:
                        raise AssertionError("Already updated")
                    if advance_branch:
                        current["sha"] = payload["sha"]
                    return {"ref": "refs/heads/studio/mp-abcdef123456"}
                raise AssertionError((method, path))

            github.get.side_effect = get
            github.call.side_effect = call
            producer = GenericRepository(github, "owner/repo", "mp-abcdef123456")
            advance_branch = False
            with self.assertRaisesRegex(StudioError, "branch SHA unverified"):
                producer.publish(base_sha, root, "checkpoint")
            advance_branch = True
            self.assertEqual(producer.publish(base_sha, root, "checkpoint"), commit_sha)



if __name__ == "__main__":
    unittest.main()

import sys
from pathlib import Path

import unittest

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


if __name__ == "__main__":
    unittest.main()

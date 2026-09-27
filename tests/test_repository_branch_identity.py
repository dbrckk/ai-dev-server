import sys
from pathlib import Path

import pytest

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


def test_request_check_accepts_safe_repository_branch_identity():
    request = dict(BASE)
    request["repository_branch_id"] = "mp-abcdef123456"

    checked = request_check(request)

    assert checked["id"] == "pos-123"
    assert checked["repository_branch_id"] == "mp-abcdef123456"


def test_request_check_rejects_unsafe_repository_branch_identity():
    request = dict(BASE)
    request["repository_branch_id"] = "../main"

    with pytest.raises(StudioError, match="Invalid repository_branch_id"):
        request_check(request)


def test_generic_repository_branch_is_independent_from_execution_request_id():
    repository = GenericRepository(
        github=object(),
        repo="owner/repo",
        project_id="mp-abcdef123456",
    )

    assert repository.branch == "studio/mp-abcdef123456"

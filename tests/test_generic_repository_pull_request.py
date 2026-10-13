import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from generic_repository import GenericRepository


class FakeGitHub:
    def __init__(self, pulls=None):
        self.repo = "/repos/owner/repo"
        self.pulls = list(pulls or [])
        self.calls = []

    def get(self, path):
        self.calls.append(("GET", path))
        if path == "":
            return {"default_branch":"main"}
        if path == "/pulls?state=open&head=owner%3Astudio%2Fmp-abc&base=main&per_page=100":
            return self.pulls
        raise AssertionError(path)

    def call(self, method, path, payload):
        self.calls.append((method, path, payload))
        if method == "POST" and path == "/repos/owner/repo/pulls":
            created = {
                "number":17,
                "state":"open",
                "html_url":"https://github.com/owner/repo/pull/17",
                "head":{"ref":"studio/mp-abc", "repo":{"full_name":"owner/repo"}},
                "base":{"ref":"main", "repo":{"full_name":"owner/repo"}},
            }
            self.pulls.append(created)
            return created
        raise AssertionError((method, path, payload))


def test_ensure_pull_request_creates_one_for_managed_branch():
    github = FakeGitHub()
    repository = GenericRepository(
        github,
        "owner/repo",
        "mp-abc",
    )

    result = repository.ensure_pull_request(
        title="Managed project",
        body="Automated",
    )

    assert result == {
        "number":17,
        "state":"open",
        "url":"https://github.com/owner/repo/pull/17",
        "head":"studio/mp-abc",
        "base":"main",
        "reused":False,
    }
    posts = [
        call for call in github.calls
        if call[0] == "POST"
    ]
    assert len(posts) == 1


def test_ensure_pull_request_reuses_existing_exact_branch_pr():
    github = FakeGitHub([
        {
            "number":23,
            "state":"open",
            "html_url":"https://github.com/owner/repo/pull/23",
            "head":{"ref":"studio/mp-abc", "repo":{"full_name":"owner/repo"}},
            "base":{"ref":"main", "repo":{"full_name":"owner/repo"}},
        }
    ])
    repository = GenericRepository(
        github,
        "owner/repo",
        "mp-abc",
    )

    first = repository.ensure_pull_request(title="Managed project")
    second = repository.ensure_pull_request(title="Managed project")

    assert first["number"] == 23
    assert first["reused"] is True
    assert second["number"] == 23
    assert second["reused"] is True
    assert not any(call[0] == "POST" for call in github.calls)


def test_ensure_pull_request_ignores_other_studio_branch():
    github = FakeGitHub([
        {
            "number":22,
            "state":"open",
            "html_url":"https://github.com/owner/repo/pull/22",
            "head":{"ref":"studio/mp-other", "repo":{"full_name":"owner/repo"}},
            "base":{"ref":"main", "repo":{"full_name":"owner/repo"}},
        },
        {
            # A fork can have the SAME branch name. Never report a fork
            # author's open PR as this worker's own verified delivery.
            "number":21,
            "state":"open",
            "html_url":"https://github.com/owner/repo/pull/21",
            "head":{"ref":"studio/mp-abc", "repo":{"full_name":"stranger/repo"}},
            "base":{"ref":"main", "repo":{"full_name":"owner/repo"}},
        },
        {
            # Missing repository identity is not sufficient evidence.
            "number":20,
            "state":"open",
            "head":{"ref":"studio/mp-abc"},
            "base":{"ref":"main"},
        },
    ])
    repository = GenericRepository(
        github,
        "owner/repo",
        "mp-abc",
    )

    result = repository.ensure_pull_request(title="Managed project")

    assert result["number"] == 17
    assert result["reused"] is False
    assert ("GET", "/pulls?state=open&head=owner%3Astudio%2Fmp-abc&base=main&per_page=100") in github.calls
    assert len([item for item in github.calls if item[0] == "POST"]) == 1

import sys
from pathlib import Path
from unittest.mock import patch

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
        if path.startswith("/pulls?state=open&head=") and path.endswith("&base=main&per_page=100"):
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

    # A trusted target workflow creates its PR asynchronously after the
    # dispatch returns 204. Never claim successful delivery from the dispatch
    # or a different SHA, even if the branch name matches.
    sha = "1" * 40
    wrong_sha = "2" * 40
    branch = "studio/mp-" + "a" * 24
    target = FakeGitHub([{
        "number": 40,
        "state": "open",
        "html_url": "https://github.com/dbrckk/repo-standards/pull/40",
        "head": {
            "ref": branch,
            "sha": wrong_sha,
            "repo": {"full_name": "dbrckk/repo-standards"},
        },
        "base": {"ref": "main", "repo": {"full_name": "dbrckk/repo-standards"}},
    }])
    target.repo = "/repos/dbrckk/repo-standards"
    producer = GenericRepository(target, "dbrckk/repo-standards", "mp-" + "a" * 24)
    assert producer._find_open_pull_request(expected_sha=sha) is None
    confirmed = {
        "number": 41,
        "state": "open",
        "html_url": "https://github.com/dbrckk/repo-standards/pull/41",
        "head": {
            "ref": branch,
            "sha": sha,
            "repo": {"full_name": "dbrckk/repo-standards"},
        },
        "base": {"ref": "main", "repo": {"full_name": "dbrckk/repo-standards"}},
    }
    with patch("time.sleep", side_effect=lambda delay: target.pulls.append(confirmed)) as sleep:
        actual = producer.await_trusted_review(sha)
    sleep.assert_called_once_with(3)
    assert actual["url"] == confirmed["html_url"]
    assert actual["handoff_confirmed"] is True
    assert not any(call[0] == "POST" for call in target.calls)

    # No target PR with the exact commit: remain blocked, not a fake success.
    with patch("time.sleep") as sleep:
        missing = producer.await_trusted_review("3" * 40)
    assert missing is None
    assert sleep.call_count == 3

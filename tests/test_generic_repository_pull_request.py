import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from generic_repository import GenericRepository
from core import StudioError


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
                "draft":True,
                "html_url":"https://github.com/owner/repo/pull/17",
                "head":{"ref":"studio/mp-abc", "sha":"a" * 40, "repo":{"full_name":"owner/repo"}},
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
        expected_sha="a" * 40,
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
    assert posts[0][2]["draft"] is True

    # A bounded public source task must restore and publish only its one
    # operator-approved source file, not hundreds of unrelated repository
    # blobs. The target's own CI still validates the proposed patch later.
    import base64
    from tempfile import TemporaryDirectory
    source_path = "scripts/validate_websites.py"
    original = b"def check_websites(data, schema):\n    root = website.hostname.lower()\n"
    base = "a" * 40
    proposed_commit = "b" * 40
    branch = "studio/mp-" + "f" * 24

    class OneFileGitHub:
        def __init__(self):
            self.repo = "/repos/dbrckk/star-list"
            self.calls = []
            self.branch_sha = None
            self.changed = [{"filename": source_path, "status": "modified"}]
        def get(self, path):
            self.calls.append(("GET", path))
            if path == "":
                return {"private": False, "archived": False, "default_branch": "main"}
            if path == "/git/matching-refs/heads/" + branch:
                return ([{"ref": "refs/heads/" + branch,
                          "object": {"sha": self.branch_sha}}]
                        if self.branch_sha else [])
            if path == "/branches/main":
                return {"commit": {"sha": base}}
            if path == "/contents/" + source_path + "?ref=" + base:
                return {"type": "file", "path": source_path, "encoding": "base64",
                        "size": len(original), "sha": "e" * 40,
                        "content": base64.b64encode(original).decode()}
            if path == "/git/commits/" + base:
                return {"tree": {"sha": "c" * 40}}
            if path == "/compare/" + base + "..." + proposed_commit:
                return {"files": self.changed}
            raise AssertionError(path)
        def call(self, method, path, payload):
            self.calls.append((method, path))
            if method == "POST" and path.endswith("/git/trees"):
                assert len(payload["tree"]) == 1
                assert payload["tree"][0]["path"] == source_path
                return {"sha": "d" * 40}
            if method == "POST" and path.endswith("/git/commits"):
                assert payload["parents"] == [base]
                return {"sha": proposed_commit}
            if method == "POST" and path.endswith("/git/refs"):
                self.branch_sha = payload["sha"]
                return {}
            raise AssertionError((method, path))

    with TemporaryDirectory() as directory:
        endpoint = OneFileGitHub()
        bounded = GenericRepository(endpoint, "dbrckk/star-list", "mp-" + "f" * 24)
        restored, evidence = bounded.restore_approved_source(Path(directory), source_path)
        assert restored == base and evidence["files"] == 1
        assert evidence["bytes"] == len(original)
        assert not any("/git/blobs/" in call[1] for call in endpoint.calls)
        modified = Path(directory) / source_path
        modified.write_bytes(original + b"\n")
        endpoint.changed = [{"filename": "unapproved.py", "status": "modified"}]
        try:
            bounded.publish_approved_source(restored, Path(directory),
                                            source_path, "one file")
        except StudioError as exc:
            assert "unexpected files" in str(exc)
        else:
            raise AssertionError("Unapproved file change reached a review branch")
        assert endpoint.branch_sha is None
        endpoint.changed = [{"filename": source_path, "status": "modified"}]
        published = bounded.publish_approved_source(
            restored, Path(directory), source_path, "one file")
        assert published == proposed_commit
        assert endpoint.branch_sha == published

    # A POST receipt does not prove delivery unless GitHub attests the exact
    # branch, target, draft state and numeric URL. Stay fail-closed.
    valid = {
        "number":17,
        "state":"open",
        "draft":True,
        "html_url":"https://github.com/owner/repo/pull/17",
        "head":{"ref":"studio/mp-abc", "sha":"a" * 40, "repo":{"full_name":"owner/repo"}},
        "base":{"ref":"main", "repo":{"full_name":"owner/repo"}},
    }
    invalid_receipts = [
        {**valid, "number":True},
        {**valid, "html_url":"https://github.com/other/repo/pull/17"},
        {**valid, "html_url":"https://github.com/owner/repo/pull/17extra"},
        {**valid, "draft":False},
        {**valid, "draft":None},
        {**valid, "head":{"ref":"studio/another", "repo":{"full_name":"owner/repo"}}},
        {**valid, "head":{"ref":"studio/mp-abc", "repo":{"full_name":"other/repo"}}},
        {**valid, "base":{"ref":"main", "repo":{"full_name":"other/repo"}}},
        {**valid, "state":"closed"},
        {**valid, "head":{"ref":"studio/mp-abc", "sha":"b" * 40, "repo":{"full_name":"owner/repo"}}},
    ]
    for malformed in invalid_receipts:
        candidate = FakeGitHub()
        with patch.object(candidate, "call", return_value=malformed):
            try:
                GenericRepository(candidate, "owner/repo", "mp-abc").ensure_pull_request(
                    title="Managed project",
                    expected_sha="a" * 40,
                )
            except StudioError as exc:
                assert str(exc) == "Generic review pull request receipt unverified"
            else:
                raise AssertionError("Malformed GitHub PR receipt was accepted")


def test_ensure_pull_request_reuses_existing_exact_branch_pr():
    github = FakeGitHub([
        {
            "number":23,
            "state":"open",
            "html_url":"https://github.com/owner/repo/pull/23",
            "head":{"ref":"studio/mp-abc", "sha":"a" * 40, "repo":{"full_name":"owner/repo"}},
            "base":{"ref":"main", "repo":{"full_name":"owner/repo"}},
        }
    ])
    repository = GenericRepository(
        github,
        "owner/repo",
        "mp-abc",
    )

    first = repository.ensure_pull_request(title="Managed project", expected_sha="a" * 40)
    second = repository.ensure_pull_request(title="Managed project", expected_sha="a" * 40)

    assert first["number"] == 23
    assert first["reused"] is True
    assert second["number"] == 23
    assert second["reused"] is True
    assert not any(call[0] == "POST" for call in github.calls)

    # A stale PR at the same head/base must block delivery, never cause a
    # duplicate POST or count as the newly published checkpoint.
    try:
        repository.ensure_pull_request(title="Managed project", expected_sha="b" * 40)
    except StudioError as exc:
        assert str(exc) == "Generic review pull request head revision unverified"
    else:
        raise AssertionError("Stale open PR was accepted as the published checkpoint")
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
    # The target Actions runner can queue for over a minute. It should
    # still be recognized when its real PR appears after 8 x 15 seconds.
    ticks = [0]

    def finish_target_actions(delay):
        assert delay == 15
        ticks[0] += 1
        if ticks[0] == 8:
            target.pulls.append(confirmed)

    with patch("time.sleep", side_effect=finish_target_actions) as sleep:
        actual = producer.await_trusted_review(sha)
    assert sleep.call_count == 8
    assert actual["url"] == confirmed["html_url"]
    assert actual["handoff_confirmed"] is True
    assert not any(call[0] == "POST" for call in target.calls)

    # No target PR with the exact commit: stop within the finite 3-minute
    # window and keep the review blocker visible; never fabricate a PR.
    with patch("time.sleep") as sleep:
        missing = producer.await_trusted_review("3" * 40)
    assert missing is None
    assert sleep.call_count == 12
    for call in sleep.call_args_list:
        assert call.args == (15,)

    # Extend the existing PR-delivery integration contract to the explicitly
    # opted-in Jumpy target. A 204 dispatch is only a request; the confirmed
    # PR must still match the exact commit and the destination repository.
    jumpy = FakeGitHub([{
        **confirmed,
        "number": 42,
        "html_url": "https://github.com/dbrckk/Jumpy/pull/42",
        "head": {
            "ref": branch,
            "sha": sha,
            "repo": {"full_name": "dbrckk/Jumpy"},
        },
        "base": {"ref": "main", "repo": {"full_name": "dbrckk/Jumpy"}},
    }])
    jumpy.repo = "/repos/dbrckk/Jumpy"
    jumpy.key = "test-only-credential"
    jumpy_producer = GenericRepository(jumpy, "dbrckk/Jumpy", "mp-" + "a" * 24)
    exact = jumpy_producer.await_trusted_review(sha)
    assert exact["url"] == "https://github.com/dbrckk/Jumpy/pull/42"
    assert exact["handoff_confirmed"] is True
    with patch("time.sleep") as fake_wait:
        assert jumpy_producer.await_trusted_review(wrong_sha) is None
    assert fake_wait.call_count == 12
    with patch("generic_repository.urllib.request.build_opener") as opener:
        opener.return_value.open.return_value.__enter__.return_value.status = 204
        dispatched = jumpy_producer.request_trusted_review_handoff(sha)
        request = opener.return_value.open.call_args.args[0]
    assert dispatched == {"status": "accepted"}
    assert request.full_url == "https://api.github.com/repos/dbrckk/Jumpy/dispatches"
    assert b'production_os_review_handoff' in request.data
    assert GenericRepository(FakeGitHub(), "owner/repo", "mp-" + "a" * 24).request_trusted_review_handoff(sha) == {"status": "not_configured"}

    # Ai-trading must opt in through its own independently reviewed
    # default-branch workflow. No automatic merge or forged PR proof.
    trading = FakeGitHub([{
        **confirmed,
        "number": 145,
        "html_url": "https://github.com/dbrckk/Ai-trading/pull/145",
        "head": {
            "ref": branch,
            "sha": sha,
            "repo": {"full_name": "dbrckk/Ai-trading"},
        },
        "base": {"ref": "main", "repo": {"full_name": "dbrckk/Ai-trading"}},
    }])
    trading.repo = "/repos/dbrckk/Ai-trading"
    trading.key = "test-only-credential"
    trading_producer = GenericRepository(trading, "dbrckk/Ai-trading", "mp-" + "a" * 24)
    attested = trading_producer.await_trusted_review(sha)
    assert attested["url"] == "https://github.com/dbrckk/Ai-trading/pull/145"
    assert attested["handoff_confirmed"] is True
    with patch("generic_repository.urllib.request.build_opener") as opener:
        opener.return_value.open.return_value.__enter__.return_value.status = 204
        requested = trading_producer.request_trusted_review_handoff(sha)
        request = opener.return_value.open.call_args.args[0]
    assert requested == {"status": "accepted"}
    assert request.full_url == "https://api.github.com/repos/dbrckk/Ai-trading/dispatches"


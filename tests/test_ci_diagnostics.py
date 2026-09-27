import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from ci_diagnostics import _log_excerpt, collect_failed_ci


class FakeAPI:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def call(self, method, path, timeout_seconds=30):
        self.calls.append((method, path, timeout_seconds))
        return self.responses.pop(0)


def test_collect_failed_ci_selects_failed_run_job_step_and_log_excerpt():
    api = FakeAPI([
        {
            "workflow_runs": [
                {
                    "id": 10,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "success",
                    "updated_at": "2026-09-27T07:00:00Z",
                },
                {
                    "id": 11,
                    "name": "Validate",
                    "status": "completed",
                    "conclusion": "failure",
                    "updated_at": "2026-09-27T07:10:00Z",
                    "html_url": "https://github.com/owner/app/actions/runs/11",
                },
            ]
        },
        {
            "jobs": [
                {
                    "id": 99,
                    "name": "tests",
                    "conclusion": "failure",
                    "steps": [
                        {"name": "Checkout", "conclusion": "success"},
                        {"name": "pytest", "conclusion": "failure"},
                    ],
                }
            ]
        },
    ])

    diagnostic = collect_failed_ci(
        "owner/app",
        "0123456789abcdef0123456789abcdef01234567",
        "secret",
        api=api,
        log_fetcher=lambda repo, job_id, token: (
            "setup complete\n"
            "tests/test_app.py::test_login FAILED\n"
            "E   AssertionError: expected 200\n"
            "##[error]Process completed with exit code 1.\n"
        ),
    )

    assert diagnostic["provider"] == "github-actions"
    assert diagnostic["workflow"] == "Validate"
    assert diagnostic["job"] == "tests"
    assert diagnostic["step"] == "pytest"
    assert diagnostic["conclusion"] == "failure"
    assert diagnostic["sha"] == "0123456789abcdef0123456789abcdef01234567"
    assert "AssertionError" in diagnostic["log_excerpt"]
    assert "/actions/runs?head_sha=" in api.calls[0][1]
    assert api.calls[1][1] == "/repos/owner/app/actions/runs/11/jobs?per_page=100"


def test_collect_failed_ci_returns_none_when_commit_has_no_failed_run():
    api = FakeAPI([
        {
            "workflow_runs": [
                {
                    "id": 10,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "success",
                }
            ]
        }
    ])

    assert collect_failed_ci(
        "owner/app",
        "0123456",
        "secret",
        api=api,
        log_fetcher=lambda *args: "should not be fetched",
    ) is None
    assert len(api.calls) == 1


def test_log_excerpt_is_bounded_around_error_signal():
    raw = "\n".join(
        [f"before {index}" for index in range(120)]
        + ["FAILED tests/test_x.py::test_x", "E AssertionError: boom"]
        + [f"after {index}" for index in range(120)]
    )
    excerpt = _log_excerpt(raw, max_chars=1200)

    assert "FAILED tests/test_x.py::test_x" in excerpt
    assert "AssertionError" in excerpt
    assert len(excerpt) <= 1200
    assert "before 0" not in excerpt

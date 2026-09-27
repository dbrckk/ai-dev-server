"""Bounded GitHub Actions failure diagnostics for autonomous repair."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from urllib.parse import urlencode, urlsplit

from core import API, APIError, StudioError


_FAILURES = {"failure", "timed_out", "cancelled", "action_required", "startup_failure"}
_ERROR_MARKERS = (
    "##[error]",
    "error:",
    "failed",
    "failure",
    "traceback",
    "assertionerror",
    "exception",
)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _clean_repo(repository: str) -> str:
    value = str(repository or "").strip()
    parts = value.split("/")
    if (
        len(parts) != 2
        or any(not part or part in {".", ".."} for part in parts)
        or any(not re.fullmatch(r"[A-Za-z0-9_.-]+", part) for part in parts)
    ):
        raise ValueError("repository must be owner/name")
    return value


def _clean_sha(sha: str) -> str:
    value = str(sha or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{7,40}", value):
        raise ValueError("commit sha is invalid")
    return value


def _failed_step(job: dict) -> dict | None:
    steps = job.get("steps")
    if not isinstance(steps, list):
        return None
    for step in steps:
        if (
            isinstance(step, dict)
            and str(step.get("conclusion") or "").lower() in _FAILURES
        ):
            return step
    return None


def _log_excerpt(raw: str, *, max_chars: int = 8000) -> str:
    lines = str(raw or "").splitlines()
    if not lines:
        return ""
    candidates = [
        index
        for index, line in enumerate(lines)
        if any(marker in line.lower() for marker in _ERROR_MARKERS)
    ]
    if not candidates:
        selected = lines[-80:]
    else:
        start = max(0, candidates[0] - 8)
        end = min(len(lines), candidates[-1] + 14)
        selected = lines[start:end]
    cleaned = []
    for line in selected:
        line = re.sub(r"^\d{4}-\d\d-\d\dT\S+Z\s+", "", line)
        if len(line) > 1200:
            line = line[:1200]
        cleaned.append(line)
    value = "\n".join(cleaned).strip()
    return value[-max_chars:]


def _fetch_job_log(
    repository: str,
    job_id: int,
    token: str,
    *,
    opener=None,
    timeout: float = 20.0,
) -> str:
    repo = _clean_repo(repository)
    if not token:
        raise StudioError("Missing STUDIO_GITHUB_TOKEN with access to target repository")
    if opener is None:
        opener = urllib.request.build_opener(_NoRedirect).open

    endpoint = (
        "https://api.github.com/repos/"
        + repo
        + "/actions/jobs/"
        + str(int(job_id))
        + "/logs"
    )
    request = urllib.request.Request(
        endpoint,
        method="GET",
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        response = opener(request, timeout)
    except urllib.error.HTTPError as exc:
        if exc.code not in {301, 302, 303, 307, 308}:
            raise StudioError(f"GitHub job log HTTP {exc.code}") from None
        location = exc.headers.get("Location")
    else:
        with response:
            status = int(getattr(response, "status", 200))
            if status in {301, 302, 303, 307, 308}:
                location = response.headers.get("Location")
            else:
                raw = response.read(2_000_001)
                if len(raw) > 2_000_000:
                    raise StudioError("GitHub job log is too large")
                return raw.decode("utf-8", errors="replace")

    target = urlsplit(str(location or ""))
    if (
        target.scheme != "https"
        or not target.netloc
        or target.username
        or target.password
    ):
        raise StudioError("GitHub job log redirect is invalid")

    redirected = urllib.request.Request(
        str(location),
        method="GET",
        headers={"Accept": "text/plain,*/*"},
    )
    try:
        with urllib.request.urlopen(redirected, timeout=timeout) as response:
            raw = response.read(2_000_001)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise StudioError(
            "GitHub job log download failed: " + type(exc).__name__
        ) from None
    if len(raw) > 2_000_000:
        raise StudioError("GitHub job log is too large")
    return raw.decode("utf-8", errors="replace")


def collect_failed_ci(
    repository: str,
    commit_sha: str,
    token: str,
    *,
    api: API | None = None,
    log_fetcher=None,
) -> dict | None:
    """Return one compact failed GitHub Actions diagnostic for a commit."""
    repo = _clean_repo(repository)
    sha = _clean_sha(commit_sha)
    if api is None:
        api = API("https://api.github.com", token)
    query = urlencode({"head_sha": sha, "per_page": 50})
    try:
        payload = api.call(
            "GET",
            f"/repos/{repo}/actions/runs?{query}",
            timeout_seconds=30,
        )
    except APIError as exc:
        if exc.status == 404:
            return None
        raise
    runs = payload.get("workflow_runs") if isinstance(payload, dict) else None
    if not isinstance(runs, list):
        return None

    failed_runs = [
        run for run in runs
        if isinstance(run, dict)
        and str(run.get("status") or "").lower() == "completed"
        and str(run.get("conclusion") or "").lower() in _FAILURES
    ]
    if not failed_runs:
        return None
    failed_runs.sort(
        key=lambda run: str(run.get("updated_at") or run.get("created_at") or ""),
        reverse=True,
    )
    run = failed_runs[0]
    run_id = run.get("id")
    if isinstance(run_id, bool) or not isinstance(run_id, int):
        return None

    jobs_payload = api.call(
        "GET",
        f"/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100",
        timeout_seconds=30,
    )
    jobs = jobs_payload.get("jobs") if isinstance(jobs_payload, dict) else None
    if not isinstance(jobs, list):
        return None
    failed_job = next(
        (
            job for job in jobs
            if isinstance(job, dict)
            and str(job.get("conclusion") or "").lower() in _FAILURES
        ),
        None,
    )
    if failed_job is None:
        return None

    step = _failed_step(failed_job)
    job_id = failed_job.get("id")
    excerpt = ""
    if isinstance(job_id, int) and not isinstance(job_id, bool):
        fetch = log_fetcher or _fetch_job_log
        try:
            excerpt = _log_excerpt(fetch(repo, job_id, token))
        except StudioError:
            excerpt = ""

    html_url = str(run.get("html_url") or "").strip()
    return {
        "provider": "github-actions",
        "status": "failed",
        "workflow": str(run.get("name") or "").strip()[:300] or None,
        "job": str(failed_job.get("name") or "").strip()[:300] or None,
        "step": (
            str(step.get("name") or "").strip()[:300]
            if isinstance(step, dict)
            else None
        ),
        "conclusion": str(failed_job.get("conclusion") or "").strip()[:120] or None,
        "url": html_url[:2000] or None,
        "sha": sha,
        "log_excerpt": excerpt or None,
    }

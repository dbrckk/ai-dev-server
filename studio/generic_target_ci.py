"""Observe an independently executed, unchanged repository CI workflow."""
import re
import json
import urllib.request
import urllib.error
from urllib.parse import quote

from core import StudioError, NoRedirect


def dispatch(repo, workflow_id):
    """One POST only; an ambiguous transport result must be observed, not replayed."""
    token = getattr(repo.github, "key", "")
    if not token:
        return {"status": "unavailable", "reason": "CI_dispatch_token_missing"}
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo.repo}/actions/workflows/{workflow_id}/dispatches",
        method="POST", data=json.dumps({"ref": repo.branch}).encode(),
        headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json", "X-GitHub-Api-Version": "2022-11-28"})
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=20) as response:
            return {"status": "accepted" if response.status == 204 else "ambiguous"}
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403, 404, 422}:
            return {"status": "unavailable", "reason": "CI_dispatch_HTTP_" + str(exc.code)}
        return {"status": "ambiguous"}
    except (urllib.error.URLError, TimeoutError, StudioError, OSError):
        return {"status": "ambiguous"}


def inspect(repo, sha):
    github = repo.github
    if not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise StudioError("Invalid generic CI source commit")
    inventory = github.get("/actions/workflows?per_page=100")
    workflows = inventory.get("workflows") if isinstance(inventory, dict) else None
    if (not isinstance(workflows, list) or inventory.get("total_count") != len(workflows)
            or len(workflows) > 100):
        raise StudioError("Generic CI workflow inventory incomplete")
    candidates = [w for w in workflows if isinstance(w, dict)
                  and w.get("name") == "CI" and w.get("state") == "active"]
    if len(candidates) != 1:
        return {"status": "unavailable", "reason": "one_active_CI_workflow_required"}
    workflow = candidates[0]
    path, wid = workflow.get("path"), workflow.get("id")
    if (type(wid) is not int or wid < 1 or not isinstance(path, str)
            or not re.fullmatch(r"\.github/workflows/[A-Za-z0-9_.-]+\.ya?ml", path)):
        raise StudioError("Generic CI workflow identity invalid")
    default = repo.default_branch
    if not isinstance(default, str) or not default:
        raise StudioError("Generic CI default branch unavailable")
    definitions = [github.get("/contents/" + path + "?ref=" + quote(ref, safe=""))
                   for ref in (default, sha)]
    if (any(not isinstance(d, dict) or d.get("type") != "file"
            or not re.fullmatch(r"[a-f0-9]{40}", str(d.get("sha") or "")) for d in definitions)
            or definitions[0]["sha"] != definitions[1]["sha"]):
        return {"status": "unavailable", "reason": "CI_definition_differs_from_default_branch"}
    proof = {"provider": "github_actions", "sha": sha, "workflow": path,
             "workflow_id": wid, "definition_sha": definitions[0]["sha"]}
    inventory = github.get(f"/actions/workflows/{wid}/runs?head_sha={sha}&per_page=100")
    runs = inventory.get("workflow_runs") if isinstance(inventory, dict) else None
    if not isinstance(runs, list) or len(runs) > 100:
        raise StudioError("Generic CI run inventory unavailable")
    eligible = [r for r in runs if isinstance(r, dict) and r.get("head_sha") == sha
                and r.get("head_branch") == repo.branch and r.get("path") == path
                and r.get("workflow_id") == wid
                and r.get("event") in {"push", "pull_request", "workflow_dispatch"}
                and type(r.get("id")) is int and r["id"] > 0]
    if not eligible:
        return {**proof, "status": "pending", "reason": "exact_commit_ci_not_started"}
    run = max(eligible, key=lambda r: r["id"])
    rid, attempt = run["id"], run.get("run_attempt")
    if type(attempt) is not int or attempt < 1:
        raise StudioError("Generic CI run attempt unavailable")
    proof.update(run_id=rid, run_attempt=attempt,
                 url=f"https://github.com/{repo.repo}/actions/runs/{rid}")
    if run.get("status") != "completed":
        return {**proof, "status": "pending", "reason": "exact_commit_ci_in_progress"}
    response = github.get(f"/actions/runs/{rid}/attempts/{attempt}/jobs?per_page=100")
    jobs = response.get("jobs") if isinstance(response, dict) else None
    if not isinstance(jobs, list) or not jobs or response.get("total_count") != len(jobs) or len(jobs) > 100:
        raise StudioError("Generic CI job evidence incomplete")
    if any(not isinstance(j, dict) or j.get("head_sha") != sha
           or type(j.get("run_id")) is not int or j["run_id"] != rid
           or type(j.get("run_attempt")) is not int or j["run_attempt"] != attempt for j in jobs):
        raise StudioError("Generic CI job identity changed")
    current = github.get(f"/actions/runs/{rid}")
    keys = ("id", "run_attempt", "head_sha", "head_branch", "path", "event", "workflow_id", "status", "conclusion")
    if not isinstance(current, dict) or any(current.get(k) != run.get(k) for k in keys):
        return {**proof, "status": "pending", "reason": "CI_changed_during_inspection"}
    failed = [str(j.get("name") or "unnamed")[:160] for j in jobs
              if j.get("status") != "completed" or j.get("conclusion") != "success"]
    if run.get("conclusion") != "success" or failed:
        repairable = run.get("conclusion") == "failure" and any(j.get("conclusion") == "failure" for j in jobs)
        return {**proof, "status": "failed" if repairable else "unavailable",
                "reason": "independent_CI_failed" if repairable else "CI_execution_requires_attention",
                "failed_jobs": failed,
                "failed_steps": [str(s.get("name") or "unnamed")[:160] for j in jobs
                                 for s in (j.get("steps") or []) if isinstance(s, dict)
                                 and s.get("conclusion") == "failure"][:30]}
    if any(not isinstance(j.get("steps"), list) or not any(
            isinstance(s, dict) and s.get("status") == "completed" and s.get("conclusion") == "success"
            for s in j["steps"]) for j in jobs):
        raise StudioError("Generic CI executed steps missing")
    return {**proof, "status": "passed", "conclusion": "success"}

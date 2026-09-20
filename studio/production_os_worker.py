"""Production-OS worker bridge helpers for AI Dev Server."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from atomic_file import write_text as atomic_write_text
from file_lock import exclusive


BASE_WORKER_CAPABILITIES = [
    "android",
    "node",
    "python",
    "repo-analysis",
    "software-development",
]


def _asset_forge_operational_status(environ=None) -> dict | None:
    executable = shutil.which("asset-forge")
    if not executable:
        return None
    env = dict(os.environ)
    if environ is not None:
        env.update({str(key): str(value) for key, value in environ.items()})
    try:
        completed = subprocess.run(
            [executable, "operational-status"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15,
            check=False,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    try:
        payload = json.loads(completed.stdout)
    except (TypeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def worker_capabilities(environ=None, *, home: Path | None = None) -> list[str]:
    del home  # Kept for backwards-compatible callers/tests.
    capabilities = list(BASE_WORKER_CAPABILITIES)
    status = _asset_forge_operational_status(environ)
    if not isinstance(status, dict):
        return capabilities
    visual = status.get("capabilities")
    if not isinstance(visual, dict):
        return capabilities
    if any(
        visual.get(name) is True
        for name in ("rasterPng", "rasterWebp", "vectorSvg", "threeDGlb")
    ):
        capabilities.append("visual-asset-production")
    if visual.get("threeDGlb") is True:
        capabilities.append("visual-asset-3d-production")
    return capabilities


class ProductionOSWorkerError(RuntimeError):
    pass


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ProductionOSWorkerError(
            "credential-bearing Production-OS redirects are refused"
        )


def _default_opener(request, timeout):
    return urllib.request.build_opener(_NoRedirect).open(
        request,
        timeout=timeout,
    )


class ProductionOSClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout: float = 30.0,
        opener=_default_opener,
    ):
        parsed = urlsplit(str(base_url or "").strip())
        loopback = {"127.0.0.1", "localhost", "::1", "0.0.0.0"}
        local_http = (
            parsed.scheme == "http"
            and (parsed.hostname or "").lower() in loopback
        )
        if (
            not (parsed.scheme == "https" or local_http)
            or not parsed.netloc
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ProductionOSWorkerError(
                "Production-OS URL must use HTTPS, except loopback-local HTTP"
            )
        secret = str(token or "").strip()
        if not secret:
            raise ProductionOSWorkerError("Production-OS worker token is required")
        try:
            timeout_value = float(timeout)
        except (TypeError, ValueError) as exc:
            raise ProductionOSWorkerError("timeout must be positive") from exc
        if timeout_value <= 0:
            raise ProductionOSWorkerError("timeout must be positive")

        self.base_url = str(base_url).strip().rstrip("/")
        self._token = secret
        self.timeout = timeout_value
        self._opener = opener

    def _post(
        self,
        path: str,
        payload: dict,
        *,
        token: str | None = None,
    ) -> dict | None:
        request = urllib.request.Request(
            self.base_url + path,
            method="POST",
            data=json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + (
                    str(token).strip() if token is not None else self._token
                ),
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with self._opener(request, self.timeout) as response:
                status = int(getattr(response, "status", 200))
                if status == 204:
                    return None
                raw = response.read(1_000_001)
        except urllib.error.HTTPError as exc:
            raise ProductionOSWorkerError(
                f"Production-OS HTTP {exc.code}"
            ) from None
        except (
            urllib.error.URLError,
            TimeoutError,
            ConnectionError,
            OSError,
        ) as exc:
            raise ProductionOSWorkerError(
                f"Production-OS unavailable: {type(exc).__name__}"
            ) from None

        if len(raw) > 1_000_000:
            raise ProductionOSWorkerError("Production-OS response too large")
        if not raw:
            return {}
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProductionOSWorkerError(
                "Production-OS returned invalid JSON"
            ) from exc
        if not isinstance(value, dict):
            raise ProductionOSWorkerError(
                "Production-OS response must be a JSON object"
            )
        return value

    def claim(self, worker_id: str, capabilities: list[str]) -> dict | None:
        payload = self._post(
            "/v1/jobs/claim",
            {
                "worker_id": str(worker_id),
                "capabilities": [str(item) for item in capabilities],
            },
        )
        if payload is None:
            return None
        job = payload.get("job")
        if not isinstance(job, dict):
            raise ProductionOSWorkerError(
                "Production-OS claim response missing job"
            )
        return job

    def ack(self, key: str, worker_id: str) -> dict | None:
        return self._post(
            "/v1/jobs/ack",
            {"key": str(key), "worker_id": str(worker_id)},
        )

    def complete(self, payload: dict) -> dict | None:
        return self._post("/v1/jobs/complete", payload)

    def fail(self, payload: dict) -> dict | None:
        return self._post("/v1/jobs/fail", payload)

    def register(
        self,
        worker_id: str,
        capabilities: list[str],
        operator_token: str,
    ) -> dict | None:
        secret = str(operator_token or "").strip()
        if not secret:
            raise ProductionOSWorkerError(
                "Production-OS operator token is required"
            )
        return self._post(
            "/v1/workers/register",
            {
                "worker_id": str(worker_id),
                "capabilities": [str(item) for item in capabilities],
                "max_concurrency": 1,
            },
            token=secret,
        )

    def heartbeat(
        self,
        worker_id: str,
        *,
        active_job_keys=(),
        capacity: dict | None = None,
    ) -> dict | None:
        payload = {
            "worker_id": str(worker_id),
            "active_tasks": len(tuple(active_job_keys)),
            "active_job_keys": [
                str(key) for key in active_job_keys
            ],
        }
        if capacity is not None:
            payload["capacity"] = dict(capacity)
        return self._post(
            "/v1/workers/heartbeat",
            payload,
        )


def production_capacity_snapshot(
    environ=None,
    *,
    fetch_summary=None,
) -> dict | None:
    """Return a safe global token-capacity snapshot for Production-OS."""
    env = os.environ if environ is None else environ
    base_url = str(env.get("OMNIROUTE_URL") or "").strip()
    if not base_url:
        return None
    if fetch_summary is None:
        from omniroute_capacity import fetch_summary as fetch_summary

    try:
        snapshot = fetch_summary(
            base_url,
            api_key=str(env.get("OMNIROUTE_API_KEY") or "").strip() or None,
            timeout=5.0,
        )
    except Exception as exc:
        return {
            "source": "omniroute",
            "status": "unavailable",
            "authenticated_usage": False,
            "steady_recurring_tokens": None,
            "used_this_month": None,
            "remaining_tokens": None,
            "catalog_updated_at": None,
            "catalog_source": None,
        }

    authenticated = bool(snapshot.authenticated_usage)
    return {
        "source": "omniroute",
        "status": "ok" if authenticated else "unavailable",
        "authenticated_usage": authenticated,
        "steady_recurring_tokens": (
            int(snapshot.steady_recurring_tokens)
            if authenticated
            else int(snapshot.steady_recurring_tokens)
        ),
        "used_this_month": (
            int(snapshot.used_this_month)
            if snapshot.used_this_month is not None
            else None
        ),
        "remaining_tokens": (
            int(snapshot.remaining_tokens)
            if snapshot.remaining_tokens is not None
            else None
        ),
        "catalog_updated_at": snapshot.catalog_updated_at,
        "catalog_source": snapshot.catalog_source,
    }


def _project_id(job_key: str) -> str:
    digest = hashlib.sha256(str(job_key).encode("utf-8")).hexdigest()[:24]
    return "pos-" + digest


def _app_name(repository: str) -> str:
    name = str(repository).rsplit("/", 1)[-1].lower()
    name = re.sub(r"[^a-z0-9_]+", "_", name).strip("_")
    if not name or not name[0].isalpha():
        name = "app_" + name
    if len(name) < 3:
        name = (name + "_app")[:40]
    return name[:40]


def _brief(task: str, final_goal: str) -> str:
    task = str(task or "").strip()
    final_goal = str(final_goal or "").strip()
    value = task or final_goal
    if len(value) >= 20:
        return value[:24000]
    expanded = (
        f"Complete this repository objective: {value}. "
        f"Final goal: {final_goal or value}."
    )
    return expanded[:24000]


def _is_visual_handoff(handoff: dict[str, Any]) -> bool:
    text = " ".join(
        str(value)
        for value in (
            handoff.get("task"),
            handoff.get("final_goal"),
            handoff.get("rationale"),
        )
        if isinstance(value, str)
    ).lower()
    patterns = (
        r"\basset(?:s)?\b",
        r"\bsprite(?:s|sheet| sheets)?\b",
        r"\bpixel[ -]?art\b",
        r"\bgraphic(?:s|al)?\b",
        r"\bartwork\b",
        r"\btexture(?:s)?\b",
        r"\bicon(?:s)?\b",
        r"\bvector(?:s)?\b",
        r"\bsvg\b",
        r"\bglb\b",
        r"\bgltf\b",
        r"\b3d\s+(?:asset|model|character|environment|prop)",
        r"\bmesh(?:es)?\b",
        r"\bvisual(?:s| design| quality| polish)?\b",
        r"\bui\s+(?:art|design|graphics|assets|icons)\b",
        r"\bgraphisme(?:s)?\b",
        r"\bgraphique(?:s)?\b",
        r"\bic[oô]ne(?:s)?\b",
        r"\bvecteur(?:s)?\b",
        r"\bvectoriel(?:le|les|s)?\b",
        r"\bmod[eè]le(?:s)?\s+3d\b",
        r"\bpersonnage(?:s)?\s+3d\b",
        r"\benvironnement(?:s)?\s+3d\b",
        r"\bobjet(?:s)?\s+3d\b",
        r"\bmaillage(?:s)?\b",
        r"\bvisuel(?:s|le|les)?\b",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def _asset_forge_guidance(handoff: dict[str, Any]) -> str:
    candidates = handoff.get("reuse_candidates", [])
    if not isinstance(candidates, list):
        candidates = []
    visual_caps = {
        "visual-asset-pipeline",
        "sprite-atlas-pipeline",
        "gltf-asset-pipeline",
        "vector-asset-pipeline",
        "godot-asset-handoff",
    }
    asset_forge_candidate = any(
        isinstance(item, dict)
        and str(item.get("source") or "") == "dbrckk/asset-forge"
        and str(item.get("capability") or "") in visual_caps
        for item in candidates
    )
    contracts = handoff.get("tool_contracts")
    contract = (
        contracts.get("asset_forge")
        if isinstance(contracts, dict)
        else None
    )
    contract_declared = (
        isinstance(contract, dict)
        and contract.get("request_schema") == "asset-forge/production-request/v1"
        and contract.get("command") == "asset-forge fulfill"
    )
    if (
        not asset_forge_candidate
        and not contract_declared
        and not _is_visual_handoff(handoff)
    ):
        return ""
    return (
        " Use dbrckk/asset-forge for visual asset production. "
        "Represent asset work with the asset-forge/production-request/v1 contract. "
        "Run asset-forge operational-status before choosing the asset type and target format; "
        "when only rasterPng is ready, choose a raster-compatible asset type and PNG target instead of SVG. "
        "Run the request end-to-end with asset-forge fulfill <request.json> using automatic backend selection, "
        "require a successful production-report.json, then integrate and verify the produced assets before completion."
    )


def build_studio_request(job: dict[str, Any]) -> dict[str, Any]:
    """Convert one claimed Production-OS job to the trusted Studio request."""
    if not isinstance(job, dict):
        raise ValueError("Production-OS job must be an object")
    payload = job.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("Production-OS job payload missing")
    handoff = payload.get("handoff")
    if not isinstance(handoff, dict):
        raise ValueError("Production-OS handoff missing")

    repository = str(
        handoff.get("repository")
        or job.get("repository")
        or ""
    ).strip()
    task = str(handoff.get("task") or job.get("task") or "").strip()
    final_goal = str(handoff.get("final_goal") or task).strip()
    workflow_id = str(payload.get("workflow_id") or "").strip()
    workflow_task_id = str(payload.get("workflow_task_id") or "").strip()
    job_key = str(job.get("key") or "").strip()

    if not all((repository, task, workflow_id, workflow_task_id, job_key)):
        raise ValueError("Production-OS job correlation is incomplete")

    brief = (_brief(task, final_goal) + _asset_forge_guidance(handoff))[:24000]
    request = {
        "id": _project_id(job_key),
        "target_repo": repository,
        "app_name": _app_name(repository),
        "brief": brief,
        "enabled": True,
        "production_os": {
            "workflow_id": workflow_id,
            "workflow_task_id": workflow_task_id,
        },
    }
    tool_contracts = handoff.get("tool_contracts")
    if isinstance(tool_contracts, dict) and tool_contracts:
        request["tool_contracts"] = dict(tool_contracts)
    preference = str(handoff.get("agent_preference") or "auto").strip()
    if preference:
        request["agent_preference"] = preference
    return request


def _write_project_capacity_plan(
    output_root: Path,
    request: dict[str, Any],
    handoff: dict[str, Any],
    capacity: dict | None,
) -> dict[str, Any] | None:
    raw_budget = handoff.get("token_budget")
    if isinstance(raw_budget, bool):
        raise ValueError("Production-OS token_budget must be a positive integer")
    try:
        requested = int(raw_budget)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Production-OS token_budget must be a positive integer"
        ) from exc
    if requested <= 0:
        raise ValueError("Production-OS token_budget must be a positive integer")

    envelope = requested
    capacity_source = "production-os"
    constrained = False
    if (
        isinstance(capacity, dict)
        and capacity.get("authenticated_usage") is True
        and isinstance(capacity.get("remaining_tokens"), int)
        and not isinstance(capacity.get("remaining_tokens"), bool)
    ):
        remaining = max(0, int(capacity["remaining_tokens"]))
        envelope = min(envelope, remaining)
        constrained = envelope < requested
        capacity_source = str(capacity.get("source") or "omniroute")

    row = {
        "id": str(request["id"]),
        "status": "running",
        "phase": "implementation",
        "requested_tokens": requested,
        "token_envelope": envelope,
        "constrained": constrained,
        "budget_source": "production-os",
        "capacity_source": capacity_source,
    }

    path = Path(output_root) / "capacity-plan.json"
    with exclusive(path):
        payload = {"schema": 1, "projects": []}
        if path.is_file():
            try:
                current = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                current = None
            if isinstance(current, dict):
                payload = dict(current)
        projects = payload.get("projects")
        if not isinstance(projects, list):
            projects = []
        projects = [
            item
            for item in projects
            if not isinstance(item, dict)
            or str(item.get("id") or "") != str(request["id"])
        ]
        projects.append(row)
        payload["schema"] = 1
        payload["projects"] = projects
        atomic_write_text(
            path,
            json.dumps(payload, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    return row


def _result_payload(result: dict[str, Any]) -> dict[str, Any]:
    usage = result.get("usage")
    evidence = result.get("evidence")
    return {
        "usage": dict(usage) if isinstance(usage, dict) else {},
        "evidence": dict(evidence) if isinstance(evidence, dict) else {},
        "ai_dev_server_status": str(result.get("status") or "unknown"),
    }


def completion_payload(
    key: str,
    worker_id: str,
    result: dict[str, Any],
    *,
    duration_seconds: float,
    capabilities: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "key": str(key),
        "worker_id": str(worker_id),
        "duration_seconds": max(0.0, float(duration_seconds)),
        "capabilities": list(capabilities or BASE_WORKER_CAPABILITIES),
        "result": _result_payload(result),
    }


def failure_payload(
    key: str,
    worker_id: str,
    result: dict[str, Any],
    *,
    duration_seconds: float,
    capabilities: list[str] | None = None,
) -> dict[str, Any]:
    status = str(result.get("status") or "failed")
    next_stage = result.get("evidence", {}).get("next_stage") if isinstance(
        result.get("evidence"), dict
    ) else None
    reason = status if not next_stage else f"{status}: {next_stage}"
    return {
        "key": str(key),
        "worker_id": str(worker_id),
        "duration_seconds": max(0.0, float(duration_seconds)),
        "capabilities": list(capabilities or BASE_WORKER_CAPABILITIES),
        "reason": reason[:1000],
        "result": _result_payload(result),
    }


def run_once(
    client: ProductionOSClient,
    *,
    worker_id: str,
    output_root: Path,
    run_project=None,
    clock=None,
    baseline_sha: str | None = None,
    capacity: dict | None = None,
    heartbeat_interval_seconds: float = 30.0,
    capabilities: list[str] | None = None,
) -> dict:
    """Claim and execute at most one Production-OS job."""
    if run_project is None:
        from github_runner import run as run_project
    if clock is None:
        import time
        clock = time.monotonic

    capabilities = list(capabilities or worker_capabilities())
    job = client.claim(worker_id, capabilities)
    if job is None:
        return {"status": "idle", "worker_id": worker_id}

    key = str(job.get("key") or "")
    if not key:
        raise ProductionOSWorkerError("claimed job has no key")
    client.ack(key, worker_id)
    if capacity is None:
        client.heartbeat(worker_id, active_job_keys=(key,))
    else:
        client.heartbeat(
            worker_id,
            active_job_keys=(key,),
            capacity=capacity,
        )

    request = build_studio_request(job)
    root = Path(output_root)
    handoff = dict((job.get("payload") or {}).get("handoff") or {})
    _write_project_capacity_plan(root, request, handoff, capacity)
    project_out = root / request["id"]
    project_out.mkdir(parents=True, exist_ok=True)
    request_path = project_out / "production-os-request.json"
    request_path.write_text(
        json.dumps(
            request,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    try:
        heartbeat_interval = float(heartbeat_interval_seconds)
    except (TypeError, ValueError) as exc:
        raise ProductionOSWorkerError(
            "heartbeat interval must be positive"
        ) from exc
    if heartbeat_interval <= 0:
        raise ProductionOSWorkerError("heartbeat interval must be positive")

    stop_heartbeat = threading.Event()
    heartbeat_errors: list[str] = []

    def keep_job_alive():
        while not stop_heartbeat.wait(heartbeat_interval):
            try:
                if capacity is None:
                    client.heartbeat(worker_id, active_job_keys=(key,))
                else:
                    client.heartbeat(
                        worker_id,
                        active_job_keys=(key,),
                        capacity=capacity,
                    )
            except Exception as exc:
                heartbeat_errors.append(type(exc).__name__)

    heartbeat_thread = threading.Thread(
        target=keep_job_alive,
        name=f"production-os-heartbeat-{request['id']}",
        daemon=True,
    )
    heartbeat_thread.start()

    started = float(clock())
    try:
        summary = run_project(
            request_path,
            project_out,
            baseline_sha=baseline_sha,
        )
    except Exception as exc:
        stop_heartbeat.set()
        heartbeat_thread.join(timeout=min(heartbeat_interval, 1.0))
        duration = max(0.0, float(clock()) - started)
        envelope = {
            "schema_version": "ai-dev-server/production-os-result/v1",
            "workflow_id": request["production_os"]["workflow_id"],
            "workflow_task_id": request["production_os"]["workflow_task_id"],
            "project_id": request["id"],
            "target_repo": request["target_repo"],
            "status": "runner_error",
            "succeeded": False,
            "usage": {},
            "evidence": {
                "pipeline_status": "runner_error",
                "next_stage": "retry",
                "finished": False,
                "error_type": type(exc).__name__,
            },
        }
        client.fail(
            failure_payload(
                key,
                worker_id,
                envelope,
                duration_seconds=duration,
                capabilities=capabilities,
            )
        )
        if capacity is None:
            client.heartbeat(worker_id, active_job_keys=())
        else:
            client.heartbeat(
                worker_id,
                active_job_keys=(),
                capacity=capacity,
            )
        return {
            "status": "failed",
            "worker_id": worker_id,
            "key": key,
            "project_id": request["id"],
            "usage": {},
        }

    stop_heartbeat.set()
    heartbeat_thread.join(timeout=min(heartbeat_interval, 1.0))
    duration = max(0.0, float(clock()) - started)

    result_path = project_out / "production-os-result.json"
    if result_path.is_file():
        try:
            envelope = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ProductionOSWorkerError(
                "Production-OS result envelope is unreadable"
            ) from exc
    else:
        from github_runner import write_production_os_result
        envelope = write_production_os_result(
            project_out,
            request,
            summary,
        )

    if not isinstance(envelope, dict):
        raise ProductionOSWorkerError(
            "AI Dev Server did not produce a correlated result"
        )

    if envelope.get("succeeded") is True:
        client.complete(
            completion_payload(
                key,
                worker_id,
                envelope,
                duration_seconds=duration,
                capabilities=capabilities,
            )
        )
        status = "completed"
    else:
        client.fail(
            failure_payload(
                key,
                worker_id,
                envelope,
                duration_seconds=duration,
                capabilities=capabilities,
            )
        )
        status = "failed"

    if capacity is None:
        client.heartbeat(worker_id, active_job_keys=())
    else:
        client.heartbeat(
            worker_id,
            active_job_keys=(),
            capacity=capacity,
        )
    return {
        "status": status,
        "worker_id": worker_id,
        "key": key,
        "project_id": request["id"],
        "usage": dict(envelope.get("usage") or {}),
    }


def main(
    argv=None,
    *,
    environ=None,
    client_factory=ProductionOSClient,
    run_once_fn=run_once,
    capacity_provider=production_capacity_snapshot,
    capabilities_provider=worker_capabilities,
    sleeper=None,
) -> int:
    parser = argparse.ArgumentParser(
        description="Execute one Production-OS job through AI Dev Server"
    )
    parser.add_argument("--worker-id", default="ai-dev-server-1")
    parser.add_argument(
        "--output-root",
        default="studio-output/production-os",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Claim and execute at most one job",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Maximum number of sequential jobs to process",
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Keep polling Production-OS after the queue becomes idle",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=10.0,
        help="Seconds to wait between idle polls in continuous mode",
    )
    args = parser.parse_args(argv)

    env = os.environ if environ is None else environ
    base_url = str(env.get("PRODUCTION_OS_URL") or "").strip()
    worker_token = str(
        env.get("PRODUCTION_OS_WORKER_TOKEN") or ""
    ).strip()
    operator_token = str(
        env.get("PRODUCTION_OS_OPERATOR_TOKEN") or ""
    ).strip()

    missing = []
    if not base_url:
        missing.append("PRODUCTION_OS_URL")
    if not worker_token:
        missing.append("PRODUCTION_OS_WORKER_TOKEN")
    if not operator_token:
        missing.append("PRODUCTION_OS_OPERATOR_TOKEN")
    if missing:
        raise RuntimeError(
            "Missing Production-OS configuration: " + ", ".join(missing)
        )
    cycles = 1 if args.once else int(args.cycles)
    if cycles < 1 or cycles > 1000:
        raise RuntimeError("--cycles must be between 1 and 1000")
    if args.once and args.continuous:
        raise RuntimeError("--once and --continuous are mutually exclusive")
    try:
        poll_interval = float(args.poll_interval)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("--poll-interval must be positive") from exc
    if poll_interval <= 0:
        raise RuntimeError("--poll-interval must be positive")
    if sleeper is None:
        import time
        sleeper = time.sleep

    client = client_factory(base_url, worker_token)
    capabilities = capabilities_provider(env)
    client.register(
        args.worker_id,
        capabilities,
        operator_token,
    )
    completed_cycles = 0
    try:
        while args.continuous or completed_cycles < cycles:
            capacity = capacity_provider(env)
            result = run_once_fn(
                client,
                worker_id=args.worker_id,
                output_root=Path(args.output_root),
                capacity=capacity,
                capabilities=capabilities,
            )
            if not isinstance(result, dict):
                raise RuntimeError("Production-OS worker returned invalid result")
            completed_cycles += 1
            if result.get("status") == "idle":
                if not args.continuous:
                    break
                sleeper(poll_interval)
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

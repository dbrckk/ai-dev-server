#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.parse import urlsplit


REQUIRED = (
    "PRODUCTION_OS_URL",
    "PRODUCTION_OS_WORKER_TOKEN",
    "PRODUCTION_OS_OPERATOR_TOKEN",
)


def _valid_service_url(raw: str) -> bool:
    value = str(raw or "").strip()
    parsed = urlsplit(value)
    host = (parsed.hostname or "").lower()
    loopback = host in {"127.0.0.1", "localhost", "::1", "0.0.0.0"}
    return bool(
        parsed.netloc
        and not parsed.username
        and not parsed.password
        and not parsed.query
        and not parsed.fragment
        and (parsed.scheme == "https" or (parsed.scheme == "http" and loopback))
    )


def _positive_float(value: str) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def _check_output_root(path_value: str) -> tuple[bool, str]:
    path = Path(path_value).expanduser()
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".production-os-preflight"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return False, f"output root is not writable ({type(exc).__name__})"
    return True, str(path)


def _codex_version() -> tuple[bool, str]:
    executable = shutil.which("codex")
    if not executable:
        return False, "Codex CLI is not installed"
    try:
        result = subprocess.run(
            [executable, "--version"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"Codex CLI probe failed ({type(exc).__name__})"
    output = (result.stdout or result.stderr).strip().splitlines()
    if result.returncode != 0:
        return False, "Codex CLI --version returned non-zero"
    return True, output[0][:160] if output else executable


def _pollinations_status(environ: dict[str, str]) -> tuple[bool, str]:
    if not shutil.which("asset-forge"):
        return False, "Asset Forge CLI not installed"
    executable = shutil.which("polli")
    if not executable:
        return False, "polli CLI not installed"
    api_key = bool(str(environ.get("POLLINATIONS_API_KEY") or "").strip())
    stored = (Path.home() / ".pollinations" / "credentials.json").is_file()
    if not (api_key or stored):
        return False, "polli installed but not authenticated"
    return True, "polli installed and authenticated"


def run_preflight(env: dict[str, str] | None = None) -> tuple[int, list[str]]:
    environ = os.environ if env is None else env
    lines: list[str] = []
    failures = 0

    missing = [name for name in REQUIRED if not str(environ.get(name) or "").strip()]
    if missing:
        failures += 1
        lines.append("FAIL required environment: missing " + ", ".join(missing))
    else:
        lines.append("OK required environment: configured")

    production_url = str(environ.get("PRODUCTION_OS_URL") or "").strip()
    if production_url:
        if _valid_service_url(production_url):
            lines.append("OK Production-OS URL: accepted")
        else:
            failures += 1
            lines.append("FAIL Production-OS URL: HTTPS required except loopback HTTP")

    omniroute_url = str(environ.get("OMNIROUTE_URL") or "").strip()
    omniroute_key = str(environ.get("OMNIROUTE_API_KEY") or "").strip()
    if bool(omniroute_url) != bool(omniroute_key):
        failures += 1
        lines.append("FAIL OmniRoute: OMNIROUTE_URL and OMNIROUTE_API_KEY must be set together")
    elif omniroute_url:
        if _valid_service_url(omniroute_url):
            lines.append("OK OmniRoute: configured")
        else:
            failures += 1
            lines.append("FAIL OmniRoute URL: HTTPS required except loopback HTTP")
    else:
        lines.append("OK OmniRoute: disabled; normal Codex profile will be used")

    poll_interval = str(environ.get("PRODUCTION_OS_POLL_INTERVAL") or "10").strip()
    if _positive_float(poll_interval):
        lines.append(f"OK poll interval: {poll_interval}s")
    else:
        failures += 1
        lines.append("FAIL poll interval: must be a positive number")

    output_root = str(
        environ.get("PRODUCTION_OS_OUTPUT_ROOT")
        or "studio-output/production-os"
    ).strip()
    writable, detail = _check_output_root(output_root)
    if writable:
        lines.append(f"OK output root: {detail}")
    else:
        failures += 1
        lines.append("FAIL " + detail)

    codex_ok, codex_detail = _codex_version()
    if codex_ok:
        lines.append("OK Codex CLI: " + codex_detail)
    else:
        failures += 1
        lines.append("FAIL Codex CLI: " + codex_detail)

    visual_ready, visual_detail = _pollinations_status(environ)
    if visual_ready:
        lines.append("OK visual assets: " + visual_detail)
    else:
        lines.append("INFO visual assets: disabled (" + visual_detail + ")")

    if failures:
        lines.append(f"NOT READY: {failures} preflight check(s) failed")
        return 2, lines
    lines.append("READY: Production-OS worker preflight passed")
    return 0, lines


def main() -> int:
    code, lines = run_preflight()
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    raise SystemExit(main())

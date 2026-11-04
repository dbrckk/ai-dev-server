"""Acquire short-lived Production-OS role credentials via GitHub Actions OIDC.

Run only inside the trusted Actions job after checkout. Never put a credential
in shell output, source control, artifacts, or the job summary.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

AUDIENCE = "production-os-control-plane"
ROLE_ENV = {
    "worker": "PRODUCTION_OS_WORKER_TOKEN",
    "operator": "PRODUCTION_OS_OPERATOR_TOKEN",
}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _https_origin(base):
    parsed = urllib.parse.urlsplit(str(base or "").strip())
    if (parsed.scheme != "https" or not parsed.netloc or parsed.username
            or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ("", "/")):
        raise ValueError("invalid Production-OS HTTPS origin")
    return parsed.geturl().rstrip("/")


def _read_json(response, max_bytes):
    raw = response.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError("OIDC response too large")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("invalid OIDC response")
    return value


def acquire_session(*, role, env=None, opener=None):
    env = env or os.environ
    if role not in ROLE_ENV or env.get("GITHUB_ACTIONS") != "true":
        raise ValueError("trusted GitHub Actions context required")
    request_url = str(env.get("ACTIONS_ID_TOKEN_REQUEST_URL") or "")
    bootstrap = str(env.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN") or "")
    parsed = urllib.parse.urlsplit(request_url)
    if (parsed.scheme != "https" or not parsed.hostname
            or not parsed.hostname.endswith(".actions.githubusercontent.com")
            or parsed.username or parsed.password or parsed.fragment
            or parsed.port not in (None, 443) or not bootstrap):
        raise ValueError("GitHub Actions OIDC provider unavailable")
    origin = _https_origin(env.get("PRODUCTION_OS_URL"))
    if opener is None:
        opener = urllib.request.build_opener(_NoRedirect()).open
    delimiter = "&" if parsed.query else "?"
    request = urllib.request.Request(
        request_url + delimiter + urllib.parse.urlencode({"audience": AUDIENCE}),
        headers={"Authorization": "bearer " + bootstrap, "Accept": "application/json"},
    )
    with opener(request, timeout=12) as response:
        assertion = _read_json(response, 16000).get("value")
    if not isinstance(assertion, str) or not 30 <= len(assertion) <= 12000:
        raise ValueError("GitHub Actions OIDC token invalid")
    exchange = urllib.request.Request(
        origin + "/v1/auth/github-actions",
        method="POST",
        data=json.dumps({"id_token": assertion, "role": role}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with opener(exchange, timeout=15) as response:
        payload = _read_json(response, 2048)
    bearer = payload.get("access_token")
    if (payload.get("role") != role or payload.get("token_type") != "Bearer"
            or type(payload.get("expires_in")) is not int
            or not 300 <= payload["expires_in"] <= 7200
            or not isinstance(bearer, str)
            or not bearer.startswith("pos-gha-")
            or not 32 <= len(bearer) <= 100
            or not bearer.isascii() or "\n" in bearer or "\r" in bearer):
        raise ValueError("Production-OS OIDC exchange returned invalid credential")
    return bearer


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1 or arguments[0] not in ROLE_ENV:
        print("Usage: production_os_oidc.py worker|operator", file=sys.stderr)
        return 2
    try:
        bearer = acquire_session(role=arguments[0])
        path = os.environ.get("GITHUB_ENV")
        if not path:
            raise ValueError("GitHub Actions environment file unavailable")
        # Register masking before exporting the ephemeral session.
        print("::add-mask::" + bearer, flush=True)
        with open(path, "a", encoding="utf-8") as out:
            out.write(ROLE_ENV[arguments[0]] + "=" + bearer + "\n")
    except (ValueError, OSError, TimeoutError, UnicodeError, urllib.error.URLError):
        print("Production-OS GitHub OIDC exchange failed (no credentials logged)",
              file=sys.stderr)
        return 1
    print("Production-OS GitHub OIDC session ready: " + arguments[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

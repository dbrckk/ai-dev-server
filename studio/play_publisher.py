"""Trusted Google Play publication boundary.

The client uses the Android Publisher v3 edit transaction. Publication is
validate-only by default; committing an edit requires an explicit trusted flag.
Generated/model-controlled code never receives the OAuth access token.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

from core import StudioError
from android_signing import valid_aab

API_BASE = "https://androidpublisher.googleapis.com/androidpublisher/v3"
UPLOAD_BASE = "https://androidpublisher.googleapis.com/upload/androidpublisher/v3"
PACKAGE_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+")
TRACKS = {"internal", "alpha", "beta", "production"}
RELEASE_STATUSES = {"draft", "completed"}


def publication_credentials(env: dict | None = None) -> dict:
    current = os.environ if env is None else env
    token = current.get("STUDIO_PLAY_ACCESS_TOKEN")
    if not token:
        return {"available": False, "blocker": "play_access_token_required"}
    if len(token) < 20 or any(ch.isspace() for ch in token):
        raise StudioError("Play access token format invalid")
    return {"available": True, "access_token": token}


class PlayPublisher:
    def __init__(self, access_token: str, opener=urllib.request.urlopen):
        if not isinstance(access_token, str) or len(access_token) < 20:
            raise StudioError("Play access token missing")
        self._token = access_token
        self._opener = opener

    def _request(self, method: str, url: str, body: bytes | None = None, *, content_type="application/json") -> dict:
        headers = {
            "Authorization": "Bearer " + self._token,
            "Accept": "application/json",
        }
        if body is not None:
            headers["Content-Type"] = content_type
        req = urllib.request.Request(url, method=method, data=body, headers=headers)
        try:
            with self._opener(req, timeout=180) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raise StudioError("Google Play API request failed with HTTP " + str(exc.code)) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise StudioError("Google Play API unavailable or timed out") from None
        if not raw:
            return {}
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise StudioError("Google Play API returned invalid JSON") from None
        if not isinstance(value, dict):
            raise StudioError("Google Play API returned invalid response")
        return value

    def create_edit(self, package_name: str) -> str:
        if not PACKAGE_RE.fullmatch(package_name):
            raise StudioError("Android package name invalid")
        package = urllib.parse.quote(package_name, safe="")
        value = self._request("POST", f"{API_BASE}/applications/{package}/edits", b"{}")
        edit_id = value.get("id")
        if not isinstance(edit_id, str) or not edit_id or len(edit_id) > 200:
            raise StudioError("Google Play edit id missing")
        return edit_id

    def upload_bundle(self, package_name: str, edit_id: str, bundle: Path) -> int:
        if not valid_aab(bundle):
            raise StudioError("Signed AAB artifact invalid")
        package = urllib.parse.quote(package_name, safe="")
        edit = urllib.parse.quote(edit_id, safe="")
        url = f"{UPLOAD_BASE}/applications/{package}/edits/{edit}/bundles?uploadType=media"
        value = self._request(
            "POST", url, bundle.read_bytes(),
            content_type="application/octet-stream",
        )
        version_code = value.get("versionCode")
        if isinstance(version_code, str) and version_code.isdigit():
            version_code = int(version_code)
        if type(version_code) is not int or version_code <= 0:
            raise StudioError("Google Play bundle upload returned invalid version code")
        return version_code

    def update_track(self, package_name: str, edit_id: str, track: str, version_code: int, *, status="completed") -> dict:
        if track not in TRACKS:
            raise StudioError("Google Play track not allowed")
        if status not in RELEASE_STATUSES:
            raise StudioError("Google Play release status not allowed")
        if type(version_code) is not int or version_code <= 0:
            raise StudioError("Google Play version code invalid")
        package = urllib.parse.quote(package_name, safe="")
        edit = urllib.parse.quote(edit_id, safe="")
        track_q = urllib.parse.quote(track, safe="")
        payload = json.dumps({
            "track": track,
            "releases": [{
                "status": status,
                "versionCodes": [str(version_code)],
            }],
        }, separators=(",", ":")).encode()
        value = self._request(
            "PUT",
            f"{API_BASE}/applications/{package}/edits/{edit}/tracks/{track_q}",
            payload,
        )
        if value.get("track") not in (None, track):
            raise StudioError("Google Play track response mismatch")
        return value

    def validate_edit(self, package_name: str, edit_id: str) -> dict:
        package = urllib.parse.quote(package_name, safe="")
        edit = urllib.parse.quote(edit_id, safe="")
        return self._request("POST", f"{API_BASE}/applications/{package}/edits/{edit}:validate", b"{}")

    def commit_edit(self, package_name: str, edit_id: str) -> dict:
        package = urllib.parse.quote(package_name, safe="")
        edit = urllib.parse.quote(edit_id, safe="")
        return self._request("POST", f"{API_BASE}/applications/{package}/edits/{edit}:commit", b"{}")


def publish_bundle(
    *,
    package_name: str,
    signed_aab: Path,
    track: str,
    access_token: str,
    commit: bool = False,
    opener=urllib.request.urlopen,
) -> dict:
    if not PACKAGE_RE.fullmatch(package_name):
        raise StudioError("Android package name invalid")
    if track not in TRACKS:
        raise StudioError("Google Play track not allowed")
    client = PlayPublisher(access_token, opener=opener)
    edit_id = client.create_edit(package_name)
    version_code = client.upload_bundle(package_name, edit_id, signed_aab)
    client.update_track(package_name, edit_id, track, version_code, status="completed")
    client.validate_edit(package_name, edit_id)
    committed = False
    if commit:
        client.commit_edit(package_name, edit_id)
        committed = True
    return {
        "passed": True,
        "package_name": package_name,
        "track": track,
        "version_code": version_code,
        "edit_validated": True,
        "committed": committed,
        "publication_scope": "play_edit_transaction",
    }

"""Render the only permitted human handoff for autonomous projects.

The factory should continue by itself whenever it can. This module is used only
when an external secret, identity, payment, legal approval, store action, or
other non-automatable prerequisite is genuinely required.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

SECRET_HINTS = {
    "STUDIO_API_KEY": "Add an AI provider API key as the GitHub Actions secret STUDIO_API_KEY.",
    "NVIDIA_NIM_API_KEY": "Add the NVIDIA NIM API key as the GitHub Actions secret NVIDIA_NIM_API_KEY.",
    "STUDIO_GITHUB_TOKEN": "Add a GitHub token with the required target-repository permissions as STUDIO_GITHUB_TOKEN.",
    "CODESPACES_PAT": "Add the GitHub token as the repository secret CODESPACES_PAT.",
}

_HUMAN_PATTERNS = (
    r"missing .*api.?key",
    r"missing .*token",
    r"credentials? required",
    r"credential",
    r"signing",
    r"play submission",
    r"google play",
    r"app store",
    r"legal",
    r"identity",
    r"payment",
    r"human.action",
    r"secret",
)
_SECRET_SUFFIXES = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "CREDENTIALS")
_ENV_NAME_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")


def requires_human_input(detail: object) -> bool:
    text = str(detail or "").lower()
    return any(re.search(pattern, text) for pattern in _HUMAN_PATTERNS)


def requested_secret_names(detail: object) -> list[str]:
    """Return exact environment-variable names without inspecting their values."""
    text = str(detail or "")
    names: list[str] = []
    for candidate in _ENV_NAME_RE.findall(text):
        if candidate in SECRET_HINTS or candidate.endswith(_SECRET_SUFFIXES):
            if candidate not in names:
                names.append(candidate)
    return names


def _reason_category(detail: object) -> str:
    text = str(detail or "").lower()
    if requested_secret_names(detail):
        return "external_secret_required"
    if "legal" in text:
        return "legal_approval_required"
    if "payment" in text:
        return "payment_action_required"
    if "identity" in text or "kyc" in text:
        return "identity_action_required"
    if "play" in text or "app store" in text or "store console" in text:
        return "store_action_required"
    if "signing" in text or "credential" in text:
        return "credential_action_required"
    return "external_human_action_required"


def safe_handoff_detail(detail: object) -> str:
    """Return a persistence-safe reason that keeps names but never raw values."""
    names = requested_secret_names(detail)
    if names:
        return "Missing required secret(s): " + ", ".join(names)
    return _reason_category(detail)


def _requested_items(detail: str) -> list[str]:
    names = requested_secret_names(detail)
    if names:
        return [
            SECRET_HINTS.get(
                name,
                f"Add the required secret {name} to GitHub repository/environment secrets or the configured secure secret manager.",
            )
            for name in names
        ]

    category = _reason_category(detail)
    instructions = {
        "legal_approval_required": "Complete the required legal approval in the external service.",
        "payment_action_required": "Complete the required payment or billing action in the external service.",
        "identity_action_required": "Complete the required identity/KYC action in the external service.",
        "store_action_required": "Complete the required store-console action using the account owner credentials.",
        "credential_action_required": "Complete the required credential or signing setup in the external secure environment.",
        "external_human_action_required": "Complete the external prerequisite reported by the project status.",
    }
    return [instructions[category]]


def render(project_id: str, detail: str, *, target_repo: str | None = None) -> str:
    items = _requested_items(detail)
    names = requested_secret_names(detail)
    target = target_repo or "unknown"
    lines = [
        "AI DEV SERVER — USER INPUT REQUIRED",
        "",
        f"Project: {project_id}",
        f"Target repository: {target}",
        "",
        "The autonomous worker has paused because this step cannot be completed safely by the worker itself.",
        "",
        "Required action:",
    ]
    lines.extend(f"- {item}" for item in items)
    if names:
        lines += ["", "Required secret names:"]
        lines.extend(f"- {name}" for name in names)
    lines += [
        "",
        "Important:",
        "- Do NOT paste API keys, passwords, private keys, tokens, or recovery codes into this file.",
        "- Put secrets in GitHub repository/environment secrets (or the external service's secure secret manager).",
        "- Keep the secret name requested above exactly unchanged when one is specified.",
        "- After the prerequisite is supplied, the scheduled autonomous worker can resume from its persisted checkpoint.",
        "",
        f"Reason category: {_reason_category(detail)}",
        "",
    ]
    return "\n".join(lines)


def write_request(out: Path, project_id: str, detail: str, *, target_repo: str | None = None) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    names = requested_secret_names(detail)
    reason_category = _reason_category(detail)
    text_path = out / "USER_INPUT_REQUIRED.txt"
    text_path.write_text(render(project_id, detail, target_repo=target_repo), encoding="utf-8")
    machine = {
        "status": "human_action_required",
        "project_id": project_id,
        "target_repo": target_repo,
        "reason_category": reason_category,
        "required_secret_names": names,
        "text_file": text_path.name,
    }
    (out / "user-input-required.json").write_text(
        json.dumps(machine, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return text_path


def prerequisite_satisfied(detail: str) -> bool:
    names = requested_secret_names(detail)
    if not names:
        return False
    return all(bool(os.environ.get(name)) for name in names)

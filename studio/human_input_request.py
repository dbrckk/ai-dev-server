"""Render the only permitted human handoff for autonomous projects.

The factory should continue by itself whenever it can. This module is used only
when an external secret, identity, payment, legal approval, store action, or
other non-automatable prerequisite is genuinely required.
"""
from __future__ import annotations

import json
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


def requires_human_input(detail: object) -> bool:
    text = str(detail or "").lower()
    return any(re.search(pattern, text) for pattern in _HUMAN_PATTERNS)


def _requested_items(detail: str) -> list[str]:
    items = []
    for name, instruction in SECRET_HINTS.items():
        if name.lower() in detail.lower():
            items.append(instruction)
    if not items:
        items.append(detail.strip() or "Complete the external prerequisite described by the project status.")
    return items


def render(project_id: str, detail: str, *, target_repo: str | None = None) -> str:
    items = _requested_items(detail)
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
    lines += [
        "",
        "Important:",
        "- Do NOT paste API keys, passwords, private keys, tokens, or recovery codes into this file.",
        "- Put secrets in GitHub repository/environment secrets (or the external service's secure secret manager).",
        "- Keep the secret name requested above exactly unchanged when one is specified.",
        "- After the prerequisite is supplied, the scheduled autonomous worker can resume from its persisted checkpoint.",
        "",
        "Original blocking detail:",
        detail.strip() or "unspecified external prerequisite",
        "",
    ]
    return "\n".join(lines)


def write_request(out: Path, project_id: str, detail: str, *, target_repo: str | None = None) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    text_path = out / "USER_INPUT_REQUIRED.txt"
    text_path.write_text(render(project_id, detail, target_repo=target_repo), encoding="utf-8")
    machine = {
        "status": "human_action_required",
        "project_id": project_id,
        "target_repo": target_repo,
        "detail": detail,
        "text_file": text_path.name,
    }
    (out / "user-input-required.json").write_text(
        json.dumps(machine, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return text_path


def prerequisite_satisfied(detail: str) -> bool:
    import os
    text=str(detail or "")
    matched=False
    for name in SECRET_HINTS:
        if name.lower() in text.lower():
            matched=True
            if not os.environ.get(name):
                return False
    return matched

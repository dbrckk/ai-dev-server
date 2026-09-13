"""Detect repeated generic-project failures and force bounded strategy changes."""
from __future__ import annotations

import hashlib
import json
import re

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_SHA_RE = re.compile(r"\b[0-9a-f]{7,64}\b", re.IGNORECASE)
_TMP_RE = re.compile(r"/(?:tmp|var/tmp)/[^\s:]+")


def _normalize_log(value: str) -> str:
    text = _ANSI_RE.sub("", value or "")
    text = _TMP_RE.sub("<tmp>", text)
    text = _SHA_RE.sub("<sha>", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[-80:])[-6000:]


def failure_signature(verification: dict | None) -> str | None:
    if not isinstance(verification, dict) or verification.get("passed") is True:
        return None
    failed = None
    for result in verification.get("results", []):
        if isinstance(result, dict) and result.get("passed") is not True:
            failed = result
            break
    payload = {
        "status": verification.get("status"),
        "command": failed.get("command") if isinstance(failed, dict) else None,
        "returncode": failed.get("returncode") if isinstance(failed, dict) else None,
        "log": _normalize_log(failed.get("log_tail", "")) if isinstance(failed, dict) else "",
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _model_identities(round_state: dict) -> tuple[set[str], set[str]]:
    providers: set[str] = set()
    models: set[str] = set()
    model_groups = round_state.get("models", {}) if isinstance(round_state, dict) else {}
    values = []
    if isinstance(model_groups, dict):
        values.extend([model_groups.get("plan"), model_groups.get("review")])
        implementation = model_groups.get("implementation", [])
        if isinstance(implementation, list):
            values.extend(implementation)
    for item in values:
        if not isinstance(item, dict):
            continue
        provider = item.get("provider")
        model = item.get("model")
        if isinstance(provider, str) and provider:
            providers.add(provider)
        if isinstance(model, str) and model:
            models.add(model)
    return providers, models

def decide(rounds: list[dict], *, prior: dict | None = None, switch_after: int = 2, stop_after: int = 4) -> dict:
    if switch_after < 2 or stop_after < switch_after:
        raise ValueError("failure loop thresholds invalid")
    if not isinstance(rounds, list):
        raise ValueError("failure loop rounds invalid")

    prior = prior or {}
    prior_signature = prior.get("signature") if isinstance(prior, dict) else None
    prior_repeated = prior.get("repeated_failures", 0) if isinstance(prior, dict) else 0
    prior_providers = set(prior.get("avoid_providers", [])) if isinstance(prior, dict) else set()
    prior_models = set(prior.get("avoid_models", [])) if isinstance(prior, dict) else set()
    if type(prior_repeated) is not int or prior_repeated < 0:
        raise ValueError("failure loop prior count invalid")

    signature = None
    repeated = 0
    matched_rounds: list[dict] = []
    for item in reversed(rounds):
        if not isinstance(item, dict):
            break
        current = failure_signature(item.get("verification"))
        if current is None:
            break
        if signature is None:
            signature = current
        if current != signature:
            break
        repeated += 1
        matched_rounds.append(item)

    if signature is None and not rounds and prior_signature is not None and prior_repeated > 0:
        signature = prior_signature
        repeated = prior_repeated
    elif signature is not None and signature == prior_signature:
        repeated += prior_repeated

    providers: set[str] = set(prior_providers if signature == prior_signature else set())
    models: set[str] = set(prior_models if signature == prior_signature else set())
    for item in matched_rounds:
        p, m = _model_identities(item)
        providers.update(p)
        models.update(m)

    if repeated >= stop_after:
        action = "stop"
        reason = f"same verification failure repeated {repeated} consecutive rounds"
    elif repeated >= switch_after:
        action = "switch_strategy"
        reason = f"same verification failure repeated {repeated} consecutive rounds"
    else:
        action = "continue"
        reason = "no repeated verification failure loop detected"

    return {
        "action": action,
        "reason": reason,
        "signature": signature,
        "repeated_failures": repeated,
        "avoid_providers": sorted(providers) if action != "continue" else [],
        "avoid_models": sorted(models) if action != "continue" else [],
    }

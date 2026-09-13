"""Second-pass stability gate for fragile generic-project changes."""
from __future__ import annotations


def should_recheck(fragility: dict | None, verification: dict | None) -> bool:
    if not isinstance(fragility, dict) or not isinstance(verification, dict):
        return False
    if verification.get("passed") is not True:
        return False
    return fragility.get("extra_verification") is True


def combine(primary: dict, recheck: dict) -> dict:
    if not isinstance(primary, dict) or not isinstance(recheck, dict):
        raise ValueError("stability verification evidence invalid")
    result = dict(primary)
    result["stability_recheck"] = recheck
    result["elapsed_seconds"] = round(
        float(primary.get("elapsed_seconds", 0.0) or 0.0)
        + float(recheck.get("elapsed_seconds", 0.0) or 0.0),
        3,
    )
    if recheck.get("passed") is True:
        result["stability_confirmed"] = True
        return result

    result["passed"] = False
    result["status"] = "failed"
    result["stability_confirmed"] = False
    primary_results = primary.get("results", [])
    recheck_results = recheck.get("results", [])
    result["results"] = [
        *(primary_results if isinstance(primary_results, list) else []),
        *(recheck_results if isinstance(recheck_results, list) else []),
    ]
    return result

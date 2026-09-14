"""Convert advisory replacement plans into bounded isolated migration work orders."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text

MAX_WORK_ORDERS = 4

def _id(current_repo: str, replacement_repo: str) -> str:
    payload=f"{current_repo}->{replacement_repo}".encode("utf-8")
    return "replace-" + hashlib.sha256(payload).hexdigest()[:16]

def build(replacement_plan: dict) -> dict:
    rows = replacement_plan.get("replacement_plans", []) if isinstance(replacement_plan, dict) else []
    work_orders = []

    for row in rows[:MAX_WORK_ORDERS]:
        if not isinstance(row, dict):
            continue
        current = row.get("current_repo")
        replacement = row.get("replacement_repo")
        if not isinstance(current, str) or not isinstance(replacement, str):
            continue

        work_orders.append({
            "id": _id(current, replacement),
            "status": "planned",
            "current_repo": current,
            "replacement_repo": replacement,
            "risk": row.get("risk"),
            "scope": row.get("estimated_change_scope"),
            "go_no_go": "NO_GO_PENDING_EXECUTION",
            "isolation": {
                "required": True,
                "mode": "dedicated_branch_or_worktree",
                "external_source_execution": False,
            },
            "baseline_requirements": [
                "capture current dependency manifest and lockfile",
                "capture current passing unit/integration/release evidence",
                "record current artifact size and test duration when available",
            ],
            "migration_requirements": [
                "inventory API usage of current dependency",
                "map only actually-used APIs to replacement APIs",
                "pin replacement dependency/version before testing",
                "preserve all user-visible behavior unless change is explicitly required",
                "add migration-specific regression tests",
            ],
            "benchmark_requirements": [
                "all baseline tests remain passing",
                "all migration tests pass",
                "release build succeeds",
                "no new privacy/security/accessibility regression",
                "no unresolved capability loss",
                "before/after evidence is recorded",
            ],
            "promotion_requirements": [
                "replacement benchmark score is strictly better than baseline",
                "required gates are all satisfied",
                "rollback has been proven",
                "dependency-policy approval exists",
            ],
            "rollback": {
                "required": True,
                "strategy": "restore baseline manifest, lockfile and API usage",
            },
            "required_gates": list(row.get("required_gates", []))[:16],
        })

    return {
        "version": 1,
        "status": "planned",
        "advisory_only": True,
        "work_orders": work_orders,
        "policy": {
            "execute_automatically": False,
            "modify_default_branch": False,
            "allow_untrusted_code_execution": False,
            "require_isolated_benchmark": True,
        },
    }

def write(replacement_plan: dict, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    result=build(replacement_plan)
    atomic_write_text(
        out/"architecture-replacement-work-orders.json",
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return result

"""Operator-reviewed public one-file repair tasks; never inferred from briefs.

Adding a task requires reviewing its source, behavioral acceptance and target
workflow first. The shared engine has no repository-specific edit logic.
"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SourceTask:
    task_id: str
    repo: str
    path: str
    function: str
    old_line: str
    method: str
    argument: str
    objective: str
    workflow_path: str
    required_steps: tuple[str, ...]

TASKS = {
    "starlist_mcp_www_guard": SourceTask(
        task_id="starlist_mcp_www_guard",
        repo="dbrckk/star-list",
        path="scripts/validate_websites.py",
        function="check_websites",
        old_line="                root = website.hostname.lower()",
        method="removeprefix",
        argument="www.",
        objective=(
            "Fix only the source bug that rejects a provider-owned MCP endpoint "
            "https://mcp.example.org/mcp when the provider website is "
            "https://www.example.org/. Normalize the provider website hostname "
            "to remove one leading www. before the existing trusted subdomain "
            "comparison. Preserve the exact hostname/subdomain security check, "
            "same-host support and foreign-host rejection. Do not modify other "
            "files, imports, workflows, dependencies, docs or tests."
        ),
        workflow_path=".github/workflows/validate.yml",
        required_steps=(
            "Compile Python utilities",
            "Validate normalized website URLs and identities",
            "Test pipeline JSON contracts",
        ),
    ),
}


def instruction(sequence: int, task_id: str) -> str:
    task = TASKS[task_id]
    if type(sequence) is not int or not 1 <= sequence <= 1_000_000_000:
        raise ValueError("Source task sequence invalid")
    return (
        f"Production-OS approved bounded public source repair {sequence} "
        f"task {task.task_id}. " + task.objective + " "
        f"Change ONLY {task.path} inside {task.function}(). "
        "One small genuinely model-authored source edit, no deterministic fallback. "
        "Require actual independent exact-commit catalog CI and a verified draft "
        "pull request. Do not merge or publish a release; report failure accurately."
    )

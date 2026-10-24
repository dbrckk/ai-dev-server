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
    second_argument: str | None = None
    replacement_line: str | None = None
    model_instruction: str = ""

TASKS = {
    "production_os_latest_reviewer_state": SourceTask(
        task_id="production_os_latest_reviewer_state",
        repo="dbrckk/Production-OS",
        path="src/production_os/github_work_state.py",
        function="_review_state",
        old_line='    states = [str(r.get("state", "")).upper() for r in reviews]',
        method="", argument="",
        replacement_line='    states = list({(r.get("user") or {}).get("id") or id(r): str(r.get("state", "")).upper() for r in reviews if str(r.get("state", "")).upper() in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}}.values())',
        model_instruction=(
            "Replace only the states assignment. Use states = list({...}.values()) "
            "with a dict comprehension iterating r in reviews in their supplied "
            "chronological order. Its key is (r.get('user') or {}).get('id') or id(r), "
            "and value is str(r.get('state', '')).upper(). Filter using that same "
            "normalized state in the set {'APPROVED', 'CHANGES_REQUESTED', 'DISMISSED'}, "
            "in that order. Preserve indentation and all remaining function logic."
        ),
        objective=(
            "Fix stale GitHub review decisions: when one reviewer requests changes "
            "then approves, only that reviewer's latest decision should count. "
            "Keep other reviewers' outstanding change requests blocking. Ignore "
            "COMMENTED/PENDING events when choosing a decision; allow DISMISSED "
            "to clear that reviewer's old request. Preserve case-insensitive states "
            "and keep reviews without a reviewer ID separate. Do not change CI, "
            "promotion policy, repository APIs or any other source bytes."
        ),
        workflow_path=".github/workflows/production-os-review-state-qualification.yml",
        required_steps=("Compile", "Existing GitHub reconciliation checks",
                        "Verify chronological review decisions", "Build distribution"),
    ),
    "production_os_worktree_git_ref": SourceTask(
        task_id="production_os_worktree_git_ref",
        repo="dbrckk/Production-OS",
        path="src/production_os/worktree_contract.py",
        function="_slug",
        old_line='    text = re.sub(r"-+", "-", text).strip("-.").lower()',
        method="replace",
        argument=".",
        second_argument="-",
        objective=(
            "Fix invalid Git worktree branch names produced by identifiers containing "
            "consecutive dots or a workflow segment ending in .lock. In _slug, "
            "normalize periods to hyphens after the existing normalization assignment. "
            "Preserve length limits, fallback, digest inputs, attempt isolation and all "
            "other source bytes. Change only src/production_os/worktree_contract.py. "
            "Require real Git worktree creation and independent exact-commit CI. "
            "Open a draft PR only; do not merge or deploy the resulting source change."
        ),
        workflow_path=".github/workflows/production-os-source-qualification.yml",
        required_steps=(
            "Compile",
            "Existing worktree and runner checks",
            "Create real worktrees for adversarial identifiers",
            "Build distribution",
        ),
    ),
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

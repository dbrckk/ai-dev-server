"""Render a deterministic Markdown review for a reputation policy migration plan."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from atomic_file import write_text as atomic_write_text

def render(plan: dict) -> str:
    explanation=plan.get("explanation") if isinstance(plan.get("explanation"),dict) else {}
    risk=plan.get("risk") if isinstance(plan.get("risk"),dict) else {}
    impact=explanation.get("state_impact") if isinstance(explanation.get("state_impact"),dict) else {}
    lines=[
        "# Reputation Policy Migration Review","",
        f"- Migration ID: `{plan.get('migration_id','unknown')}`",
        f"- Risk: **{risk.get('level','UNKNOWN')}**",
        f"- Review: **{explanation.get('review_action','explicit_authorization_required')}**",
        f"- Changed entries: **{impact.get('changed_entries',0)}**","",
        "## Policy changes","",
    ]
    policy_changes=explanation.get("policy_changes") if isinstance(explanation.get("policy_changes"),list) else []
    if not policy_changes:
        lines.append("No effective transition-policy edge changes.")
    for edge in policy_changes:
        lines.append(f"### {edge.get('transition','unknown')}")
        lines.append("")
        for change in edge.get("changes",[]):
            if "change" in change:
                lines.append(f"- {change.get('field')}: {change.get('change')} `{change.get('value')}`")
            else:
                lines.append(f"- {change.get('field')}: `{change.get('before')}` → `{change.get('after')}`")
        lines.append("")
    lines.extend(["## Persisted-state impact",""])
    transitions=impact.get("transitions") if isinstance(impact.get("transitions"),list) else []
    if not transitions:
        lines.append("No persisted reputation state changes.")
    else:
        for row in transitions:
            lines.append(f"- {row.get('transition')}: **{row.get('count',0)}**")
    lines.extend(["","## Authorization",""])
    if risk.get("reinforced_review_required") is True:
        lines.append("This migration requires explicit authorization **and reinforced review** before apply.")
    else:
        lines.append("This migration requires explicit authorization before apply.")
    return "\n".join(lines).rstrip()+"\n"

def main(argv=None) -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("plan")
    parser.add_argument("--out")
    args=parser.parse_args(argv)
    try:
        plan=json.loads(Path(args.plan).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        return 1
    if not isinstance(plan,dict):
        return 1
    text=render(plan)
    if args.out:
        atomic_write_text(Path(args.out),text,encoding="utf-8")
    else:
        print(text,end="")
    return 0

if __name__=="__main__":
    sys.exit(main())

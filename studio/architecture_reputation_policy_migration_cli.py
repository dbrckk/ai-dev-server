"""CLI for dry-run and explicitly authorized reputation policy migrations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from architecture_reputation_policy_migration import (
    ReputationPolicyMigrationError,
    apply_migration,
    dry_run,
)
from core import canonical

def _load(path: Path, label: str) -> dict:
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        raise ReputationPolicyMigrationError(label+" unreadable") from None
    if not isinstance(value,dict):
        raise ReputationPolicyMigrationError(label+" malformed")
    return value

def main(argv=None) -> int:
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="command",required=True)

    review=sub.add_parser("review")
    review.add_argument("registry")
    review.add_argument("--learning")
    review.add_argument("--out",default="studio-output")

    apply_cmd=sub.add_parser("apply")
    apply_cmd.add_argument("registry")
    apply_cmd.add_argument("plan")
    apply_cmd.add_argument("authorization")
    apply_cmd.add_argument("--out")

    args=parser.parse_args(argv)
    try:
        if args.command=="review":
            registry=_load(Path(args.registry),"registry")
            learning=_load(Path(args.learning),"learning") if args.learning else None
            result=dry_run(registry,learning)
            out=Path(args.out)
            out.mkdir(parents=True,exist_ok=True)
            target=out/"architecture-reputation-policy-migration-review.json"
            target.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
            print(canonical(result))
            return 0

        registry_path=Path(args.registry)
        registry=_load(registry_path,"registry")
        plan=_load(Path(args.plan),"migration plan")
        authorization=_load(Path(args.authorization),"authorization")
        migrated=apply_migration(registry,plan,authorization)
        target=Path(args.out) if args.out else registry_path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(migrated,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(canonical({
            "status":"reputation_policy_migration_applied",
            "migration_id":plan.get("migration_id"),
            "entries":len(migrated.get("entries",{})),
            "output":str(target),
        }))
        return 0
    except ReputationPolicyMigrationError:
        return 1

if __name__=="__main__":
    sys.exit(main())

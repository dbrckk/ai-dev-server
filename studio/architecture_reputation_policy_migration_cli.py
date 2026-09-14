"""CLI for dry-run and explicitly authorized reputation policy migrations."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from architecture_reputation_policy_migration import (
    ReputationPolicyMigrationError,
    apply_migration,
    bind_github_review_target,
    dry_run,
)
from architecture_reputation_policy_github_collect import (
    GitHubAttestationCollectionError,
    collect as collect_github_attestation,
    collect_review_target,
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

    bind_target=sub.add_parser("bind-target")
    bind_target.add_argument("plan")
    bind_target.add_argument("--repository",required=True)
    bind_target.add_argument("--pull-request",type=int,required=True)
    bind_target.add_argument("--out",required=True)

    apply_cmd=sub.add_parser("apply")
    apply_cmd.add_argument("registry")
    apply_cmd.add_argument("plan")
    apply_cmd.add_argument("authorization")
    apply_cmd.add_argument("--approval")
    apply_cmd.add_argument("--github-attestation")
    apply_cmd.add_argument("--repository")
    apply_cmd.add_argument("--pull-request",type=int)
    apply_cmd.add_argument("--ledger")
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

        if args.command=="bind-target":
            plan=_load(Path(args.plan),"migration plan")
            target=collect_review_target(
                token=os.environ.get("STUDIO_GITHUB_TOKEN",""),
                repository=args.repository,
                pull_request=args.pull_request,
            )
            bound=bind_github_review_target(plan,target)
            Path(args.out).write_text(
                json.dumps(bound,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
                encoding="utf-8",
            )
            print(canonical({
                "status":"reputation_policy_migration_target_bound",
                "migration_id":bound.get("migration_id"),
                "review_digest":bound.get("review_digest"),
                "github_review_target":bound.get("github_review_target"),
                "output":args.out,
            }))
            return 0

        registry_path=Path(args.registry)
        registry=_load(registry_path,"registry")
        plan=_load(Path(args.plan),"migration plan")
        authorization=_load(Path(args.authorization),"authorization")
        approval=_load(Path(args.approval),"approval provenance") if args.approval else None
        ledger=_load(Path(args.ledger),"approval ledger") if args.ledger else None
        if args.github_attestation:
            github_attestation=_load(Path(args.github_attestation),"GitHub attestation")
        else:
            repository=args.repository or os.environ.get("GITHUB_REPOSITORY","")
            pull_request=args.pull_request
            if not repository or not isinstance(pull_request,int):
                raise ReputationPolicyMigrationError("GitHub repository and pull request required")
            github_attestation=collect_github_attestation(
                plan,
                token=os.environ.get("STUDIO_GITHUB_TOKEN",""),
                repository=repository,
                pull_request=pull_request,
            )
        migrated=apply_migration(
            registry,plan,authorization,
            approval=approval,
            github_attestation=github_attestation,
            approval_ledger=ledger,
        )
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
    except (ReputationPolicyMigrationError,GitHubAttestationCollectionError):
        return 1

if __name__=="__main__":
    sys.exit(main())

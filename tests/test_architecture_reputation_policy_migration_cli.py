import json
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

import architecture_replacement_reputation as reputation
import architecture_reputation_policy_migration_cli as cli
from architecture_reputation_policy_migration import bind_github_review_target, dry_run

class ReputationPolicyMigrationCLITests(unittest.TestCase):
    def registry(self):
        context={
            "current_repo":"a/current","replacement_repo":"a/better",
            "framework":"flutter","project_type":"game","primary_domain":"mobile",
            "platform":"android","current_major_version":1,"replacement_major_version":2,
        }
        evidence={
            "effective_samples":20,"evidence_confidence":1.0,
            "wilson_lower_95":0.82,"regression_rate":0.02,
        }
        registry,_=reputation.apply(None,context,evidence,now=100.0)
        registry["policy"]["version"]=reputation.TRANSITION_POLICY_VERSION-1
        registry["policy"]["digest"]="0"*64
        entry=next(iter(registry["entries"].values()))
        entry["transition_policy_version"]=reputation.TRANSITION_POLICY_VERSION-1
        entry["transition_policy_digest"]="0"*64
        return registry

    def test_review_writes_plan(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            registry=root/"registry.json"
            registry.write_text(json.dumps(self.registry()))
            rc=cli.main(["review",str(registry),"--out",str(root/"out")])
            self.assertEqual(rc,0)
            plan=root/"out"/"architecture-reputation-policy-migration-review.json"
            self.assertTrue(plan.is_file())
            self.assertFalse(json.loads(plan.read_text())["authorization_template"]["authorized"])

    def test_apply_requires_authorized_record(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            registry_value=self.registry()
            registry=root/"registry.json"
            registry.write_text(json.dumps(registry_value))
            plan_value=dry_run(registry_value,None,now=200.0)
            plan=root/"plan.json"; plan.write_text(json.dumps(plan_value))
            auth=root/"auth.json"; auth.write_text(json.dumps(plan_value["authorization_template"]))
            rc=cli.main(["apply",str(registry),str(plan),str(auth)])
            self.assertEqual(rc,1)

    def test_apply_can_auto_collect_github_attestation(self):
        from architecture_reputation_policy_github_attestation import build
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            registry_value=self.registry()
            registry=root/"registry.json"; registry.write_text(json.dumps(registry_value))
            plan_value=dry_run(registry_value,None,now=200.0)
            plan_value=bind_github_review_target(plan_value,{
                "repository":"dbrckk/ai-dev-server","pull_request":7,"commit_sha":"a"*40,
                "head_ref":"policy/migration","base_ref":"main","author":"alice",
                "workflow_path":".github/workflows/ci.yml",
                "workflow_blob_sha":"blob123",
                "workflow_sha256":"5949de6344caa241ad89c8f9dfa16d52628f893809c8fc436cac9565c8f9fdb4",
            },now=200.0)
            plan=root/"plan.json"; plan.write_text(json.dumps(plan_value))
            auth_value=dict(plan_value["authorization_template"]); auth_value["authorized"]=True
            if plan_value.get("risk",{}).get("reinforced_review_required") is True:
                auth_value["reinforced_reviewed"]=True
            auth=root/"auth.json"; auth.write_text(json.dumps(auth_value))
            reinforced=plan_value.get("risk",{}).get("reinforced_review_required") is True
            reviews=[{"user":{"login":"alice"},"state":"APPROVED","commit_id":"a"*40,"submitted_at":"2026-01-01T00:00:10Z"}]
            permissions={"alice":"write"}
            if reinforced:
                reviews.append({"user":{"login":"bob"},"state":"APPROVED","commit_id":"a"*40,"submitted_at":"2026-01-01T00:00:20Z"})
                permissions["bob"]="maintain"
            attestation=build(
                plan_value,repository="dbrckk/ai-dev-server",pull_request=7,commit_sha="a"*40,
                reviews=reviews,permissions=permissions,
                workflow_runs=[{"id":9,"head_sha":"a"*40,"conclusion":"success","name":"CI","path":".github/workflows/ci.yml@refs/pull/7/merge","created_at":"2026-01-01T00:00:25Z"}],
                check_runs=[
                    {"id":11,"name":"validate","head_sha":"a"*40,"status":"completed","conclusion":"success","started_at":"2026-01-01T00:00:30Z","app":{"slug":"github-actions"},"details_url":"https://github.com/dbrckk/ai-dev-server/actions/runs/9"},
                    {"id":12,"name":"python-tests","head_sha":"a"*40,"status":"completed","conclusion":"success","started_at":"2026-01-01T00:00:40Z","app":{"slug":"github-actions"},"details_url":"https://github.com/dbrckk/ai-dev-server/actions/runs/9"},
                ],
                pr_identity={"number":7,"state":"open","draft":False,"head_ref":"policy/migration","head_sha":"a"*40,"base_ref":"main","author":"alice"},
                workflow_file={"path":".github/workflows/ci.yml","blob_sha":"blob123","size":44,"sha256":"5949de6344caa241ad89c8f9dfa16d52628f893809c8fc436cac9565c8f9fdb4","content_b64":"bmFtZTogQ0kKam9iczoKICB2YWxpZGF0ZToKICBweXRob24tdGVzdHM6Cg==","policy_validation":{"valid":True}},
                head_commit_timestamp=1767225600.0,
                reinforced=reinforced,
            )
            with patch.object(cli,"collect_github_attestation",return_value=attestation):
                with patch.dict("os.environ",{"STUDIO_GITHUB_TOKEN":"token"},clear=False):
                    rc=cli.main([
                        "apply",str(registry),str(plan),str(auth),
                        "--repository","dbrckk/ai-dev-server","--pull-request","7",
                    ])
            self.assertEqual(rc,0)

    def test_bind_target_reissues_content_bound_plan(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            registry_value=self.registry()
            plan_value=dry_run(registry_value,None,now=200.0)
            original_id=plan_value["migration_id"]
            plan=root/"plan.json"; plan.write_text(json.dumps(plan_value))
            target={
                "repository":"dbrckk/ai-dev-server","pull_request":7,"commit_sha":"a"*40,
                "head_ref":"policy/migration","base_ref":"main","author":"alice",
                "workflow_path":".github/workflows/ci.yml",
                "workflow_blob_sha":"blob123",
                "workflow_sha256":"5949de6344caa241ad89c8f9dfa16d52628f893809c8fc436cac9565c8f9fdb4",
            }
            out=root/"bound.json"
            with patch.object(cli,"collect_review_target",return_value=target):
                with patch.dict("os.environ",{"STUDIO_GITHUB_TOKEN":"token"},clear=False):
                    rc=cli.main([
                        "bind-target",str(plan),
                        "--repository","dbrckk/ai-dev-server","--pull-request","7",
                        "--out",str(out),
                    ])
            self.assertEqual(rc,0)
            bound=json.loads(out.read_text())
            self.assertNotEqual(bound["migration_id"],original_id)
            self.assertEqual(bound["github_review_target"]["commit_sha"],"a"*40)
            self.assertFalse(bound["authorization_template"]["authorized"])

if __name__=="__main__":
    unittest.main()

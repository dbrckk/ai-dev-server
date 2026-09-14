import json
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

import architecture_replacement_reputation as reputation
import architecture_reputation_policy_migration_cli as cli
from architecture_reputation_policy_migration import dry_run

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

if __name__=="__main__":
    unittest.main()

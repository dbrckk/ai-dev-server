import copy
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

import architecture_replacement_reputation as reputation
from architecture_reputation_policy_migration import (
    ReputationPolicyMigrationError,
    apply_migration,
    classify_migration_risk,
    dry_run,
)

class ReputationPolicyMigrationTests(unittest.TestCase):
    def context(self):
        return {
            "current_repo":"a/current","replacement_repo":"a/better",
            "framework":"flutter","project_type":"game","primary_domain":"mobile",
            "platform":"android","current_major_version":1,"replacement_major_version":2,
        }

    def registry(self):
        strong={
            "effective_samples":20,"evidence_confidence":1.0,
            "wilson_lower_95":0.82,"regression_rate":0.02,
        }
        registry,_=reputation.apply(None,self.context(),strong,now=100.0)
        # Simulate a registry created under an older policy.
        registry["policy"]["version"]=reputation.TRANSITION_POLICY_VERSION-1
        registry["policy"]["digest"]="0"*64
        entry=next(iter(registry["entries"].values()))
        entry["transition_policy_version"]=reputation.TRANSITION_POLICY_VERSION-1
        entry["transition_policy_digest"]="0"*64
        return registry

    def learning(self,strong=True):
        return {"rankings":[{
            **self.context(),
            "effective_samples":20,"samples":20,"evidence_confidence":1.0,
            "wilson_lower_95":0.82 if strong else 0.30,
            "regression_rate":0.02 if strong else 0.40,
        }]}

    def authorize(self,plan):
        auth=dict(plan["authorization_template"])
        auth["authorized"]=True
        return auth

    def test_dry_run_is_content_bound_and_non_mutating(self):
        registry=self.registry()
        original=copy.deepcopy(registry)
        plan=dry_run(registry,self.learning(),now=200.0)
        self.assertEqual(registry,original)
        self.assertEqual(plan["status"],"reputation_policy_migration_review_ready")
        self.assertEqual(len(plan["migration_id"]),64)
        self.assertFalse(plan["authorization_template"]["authorized"])
        self.assertEqual(plan["summary"]["trusted_revalidated"],1)

    def test_policy_migration_can_downgrade_trusted(self):
        plan=dry_run(self.registry(),self.learning(strong=False),now=200.0)
        row=plan["changes"][0]
        self.assertEqual(row["previous_state"],"TRUSTED")
        self.assertEqual(row["target_state"],"DEGRADED")
        self.assertEqual(plan["summary"]["trusted_downgrades"],1)

    def test_policy_migration_never_promotes_nontrusted_directly(self):
        registry=self.registry()
        entry=next(iter(registry["entries"].values()))
        entry["state"]="QUARANTINED"
        entry["promotion_eligible"]=False
        plan=dry_run(registry,self.learning(strong=True),now=200.0)
        row=plan["changes"][0]
        self.assertEqual(row["desired_state"],"TRUSTED")
        self.assertEqual(row["target_state"],"QUARANTINED")
        self.assertFalse(row["promotion_eligible_after_migration"])

    def test_apply_requires_explicit_authorization(self):
        registry=self.registry()
        plan=dry_run(registry,self.learning(),now=200.0)
        with self.assertRaises(ReputationPolicyMigrationError):
            apply_migration(registry,plan,plan["authorization_template"],now=300.0)

    def test_apply_is_bound_to_exact_registry(self):
        registry=self.registry()
        plan=dry_run(registry,self.learning(),now=200.0)
        changed=copy.deepcopy(registry)
        next(iter(changed["entries"].values()))["updated_at"]=999.0
        with self.assertRaises(ReputationPolicyMigrationError):
            apply_migration(changed,plan,self.authorize(plan),now=300.0)

    def test_authorized_apply_updates_policy_and_audit(self):
        registry=self.registry()
        plan=dry_run(registry,self.learning(),now=200.0)
        migrated=apply_migration(registry,plan,self.authorize(plan),now=300.0)
        self.assertEqual(migrated["policy"]["version"],reputation.TRANSITION_POLICY_VERSION)
        self.assertEqual(migrated["policy"]["digest"],reputation.transition_policy_digest())
        entry=next(iter(migrated["entries"].values()))
        self.assertEqual(entry["transition_policy_version"],reputation.TRANSITION_POLICY_VERSION)
        self.assertEqual(entry["transition_policy_digest"],reputation.transition_policy_digest())
        self.assertEqual(entry["policy_migration_id"],plan["migration_id"])
        self.assertEqual(migrated["last_policy_migration"]["migration_id"],plan["migration_id"])
        self.assertTrue(migrated["audit"][-1]["migration_authorized"])

    def test_preserved_quarantine_keeps_revalidation_gate(self):
        registry=self.registry()
        entry=next(iter(registry["entries"].values()))
        entry["state"]="QUARANTINED"
        entry["promotion_eligible"]=False
        plan=dry_run(registry,self.learning(strong=True),now=200.0)
        migrated=apply_migration(registry,plan,self.authorize(plan),now=300.0)
        migrated_entry=next(iter(migrated["entries"].values()))
        self.assertEqual(migrated_entry["state"],"QUARANTINED")
        self.assertIn("quarantined_replacement_revalidated",migrated_entry["required_transition_gates"])
        self.assertFalse(migrated_entry["promotion_eligible"])

    def test_policy_migration_does_not_mutate_source_registry(self):
        registry=self.registry()
        original=copy.deepcopy(registry)
        plan=dry_run(registry,self.learning(),now=200.0)
        apply_migration(registry,plan,self.authorize(plan),now=300.0)
        self.assertEqual(registry,original)

    def test_trust_downgrade_risk_classification(self):
        registry=self.registry()
        plan=dry_run(registry,self.learning(strong=False),now=200.0)
        self.assertEqual(plan["risk"]["level"],"TRUST_DOWNGRADE")
        self.assertEqual(plan["risk"]["trusted_downgrades"],1)
        self.assertFalse(plan["risk"]["reinforced_review_required"])

    def test_promotion_path_change_requires_reinforced_review(self):
        registry=self.registry()
        # Simulate an older policy whose RECOVERING -> TRUSTED rule differs.
        registry["policy"]["transition_matrix"]=copy.deepcopy(reputation.TRANSITION_POLICY)
        registry["policy"]["transition_matrix"]["RECOVERING"]["TRUSTED"]={
            **registry["policy"]["transition_matrix"]["RECOVERING"]["TRUSTED"],
            "minimum_confirmations":1,
        }
        plan=dry_run(registry,self.learning(),now=200.0)
        self.assertEqual(plan["risk"]["level"],"PROMOTION_PATH_CHANGE")
        self.assertTrue(plan["risk"]["reinforced_review_required"])
        self.assertFalse(plan["authorization_template"]["reinforced_reviewed"])

    def test_reinforced_review_is_required_for_promotion_path_change(self):
        registry=self.registry()
        registry["policy"]["transition_matrix"]=copy.deepcopy(reputation.TRANSITION_POLICY)
        registry["policy"]["transition_matrix"]["RECOVERING"]["TRUSTED"]={
            **registry["policy"]["transition_matrix"]["RECOVERING"]["TRUSTED"],
            "minimum_confirmations":1,
        }
        plan=dry_run(registry,self.learning(),now=200.0)
        auth=self.authorize(plan)
        with self.assertRaises(ReputationPolicyMigrationError):
            apply_migration(registry,plan,auth,now=300.0)
        auth["reinforced_reviewed"]=True
        migrated=apply_migration(registry,plan,auth,now=300.0)
        self.assertEqual(migrated["last_policy_migration"]["migration_id"],plan["migration_id"])

    def test_no_impact_when_registry_already_matches_current_policy(self):
        registry,_=reputation.apply(None,self.context(),self.learning()["rankings"][0],now=100.0)
        plan=dry_run(registry,self.learning(),now=200.0)
        self.assertEqual(plan["risk"]["level"],"NO_IMPACT")
        self.assertEqual(plan["summary"]["changed"],0)

    def test_source_invalid_policy_is_critical(self):
        registry=self.registry()
        registry["policy"]["validation"]={"valid":False}
        plan=dry_run(registry,self.learning(),now=200.0)
        self.assertEqual(plan["risk"]["level"],"CRITICAL")
        self.assertTrue(plan["risk"]["reinforced_review_required"])

    def test_explainer_describes_policy_edge_and_state_impact(self):
        registry=self.registry()
        registry["policy"]["transition_matrix"]=copy.deepcopy(reputation.TRANSITION_POLICY)
        registry["policy"]["transition_matrix"]["RECOVERING"]["TRUSTED"]={
            **registry["policy"]["transition_matrix"]["RECOVERING"]["TRUSTED"],
            "minimum_confirmations":1,
            "required_gates":[],
        }
        plan=dry_run(registry,self.learning(strong=False),now=200.0)
        explanation=plan["explanation"]
        self.assertEqual(explanation["risk_level"],"PROMOTION_PATH_CHANGE")
        self.assertEqual(explanation["review_action"],"reinforced_review_required")
        edge=next(x for x in explanation["policy_changes"] if x["transition"]=="RECOVERING -> TRUSTED")
        fields={x["field"] for x in edge["changes"]}
        self.assertIn("minimum_confirmations",fields)
        self.assertIn("required_gate",fields)
        self.assertEqual(explanation["state_impact"]["changed_entries"],1)
        self.assertTrue(any(x["transition"]=="TRUSTED -> DEGRADED" for x in explanation["state_impact"]["transitions"]))

    def test_explainer_no_impact_is_compact(self):
        registry,_=reputation.apply(None,self.context(),self.learning()["rankings"][0],now=100.0)
        plan=dry_run(registry,self.learning(),now=200.0)
        explanation=plan["explanation"]
        self.assertEqual(explanation["risk_level"],"NO_IMPACT")
        self.assertEqual(explanation["policy_changes"],[])
        self.assertEqual(explanation["state_impact"]["changed_entries"],0)

if __name__=="__main__":
    unittest.main()

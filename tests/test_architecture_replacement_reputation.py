import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

import architecture_replacement_reputation as arr

class ReplacementReputationTests(unittest.TestCase):
    def context(self):
        return {
            "current_repo":"a/current","replacement_repo":"a/better",
            "framework":"flutter","project_type":"game","primary_domain":"mobile",
            "platform":"android","current_major_version":1,"replacement_major_version":2,
        }

    def strong(self):
        return {
            "effective_samples":20,"evidence_confidence":1.0,
            "wilson_lower_95":0.82,"regression_rate":0.02,
        }

    def test_unobserved_can_become_trusted_with_strong_evidence(self):
        registry,entry=arr.apply(None,self.context(),self.strong(),now=100.0)
        self.assertEqual(entry["state"],"TRUSTED")
        self.assertTrue(entry["promotion_eligible"])
        self.assertEqual(registry["audit"][-1]["previous_state"],"UNOBSERVED")

    def test_trusted_quarantines_immediately_on_drift(self):
        registry,entry=arr.apply(None,self.context(),self.strong(),now=100.0)
        evidence={**self.strong(),"sequential_drift":True}
        registry,entry=arr.apply(registry,self.context(),evidence,now=200.0)
        self.assertEqual(entry["state"],"QUARANTINED")
        self.assertEqual(entry["transition_reason"],"immediate_safety_quarantine")

    def test_quarantine_cannot_jump_directly_to_trusted(self):
        registry,_=arr.apply(None,self.context(),self.strong(),now=100.0)
        registry,_=arr.apply(registry,self.context(),{**self.strong(),"regime_shift":True},now=200.0)
        registry,entry=arr.apply(registry,self.context(),self.strong(),now=300.0)
        self.assertEqual(entry["state"],"RECOVERING")
        self.assertFalse(entry["promotion_eligible"])

    def test_recovery_requires_time_new_evidence_and_confirmations(self):
        registry,_=arr.apply(None,self.context(),self.strong(),now=100.0)
        registry,_=arr.apply(registry,self.context(),{**self.strong(),"sequential_drift":True},now=200.0)
        registry,first=arr.apply(registry,self.context(),self.strong(),now=300.0)
        self.assertEqual(first["state"],"RECOVERING")
        self.assertTrue(first["transition_pending"])

        # Time alone is insufficient because no new effective evidence arrived.
        later=300.0+arr.RECOVERY_MIN_DWELL_SECONDS+1
        registry,second=arr.apply(registry,self.context(),self.strong(),now=later)
        self.assertEqual(second["state"],"RECOVERING")
        self.assertEqual(second["transition_reason"],"recovery_new_evidence_pending")

        stronger={**self.strong(),"effective_samples":22}
        registry,third=arr.apply(registry,self.context(),stronger,now=later+1)
        self.assertEqual(third["state"],"TRUSTED")
        self.assertTrue(third["promotion_eligible"])
        self.assertFalse(third["transition_pending"])

    def test_recovery_dwell_blocks_fast_repromotion(self):
        registry,_=arr.apply(None,self.context(),self.strong(),now=100.0)
        registry,_=arr.apply(registry,self.context(),{**self.strong(),"regime_shift":True},now=200.0)
        registry,entry=arr.apply(registry,self.context(),self.strong(),now=300.0)
        self.assertEqual(entry["state"],"RECOVERING")
        richer={**self.strong(),"effective_samples":25}
        registry,entry=arr.apply(registry,self.context(),richer,now=301.0)
        self.assertEqual(entry["state"],"RECOVERING")
        self.assertEqual(entry["transition_reason"],"recovery_minimum_dwell_pending")
        self.assertFalse(entry["promotion_eligible"])

    def test_degradation_from_trusted_is_immediate(self):
        registry,_=arr.apply(None,self.context(),self.strong(),now=100.0)
        weak={
            "effective_samples":20,"evidence_confidence":1.0,
            "wilson_lower_95":0.30,"regression_rate":0.40,
        }
        registry,entry=arr.apply(registry,self.context(),weak,now=101.0)
        self.assertEqual(entry["state"],"DEGRADED")
        self.assertEqual(entry["transition_reason"],"trusted_degraded")

    def test_policy_is_exported_in_registry(self):
        registry,_=arr.apply(None,self.context(),self.strong(),now=100.0)
        policy=registry["policy"]
        self.assertEqual(policy["recovery_confirmations_required"],arr.RECOVERY_CONFIRMATIONS_REQUIRED)
        self.assertEqual(policy["recovery_min_dwell_seconds"],arr.RECOVERY_MIN_DWELL_SECONDS)
        self.assertEqual(policy["recovery_min_new_effective_samples"],arr.RECOVERY_MIN_NEW_EFFECTIVE_SAMPLES)

    def test_transition_matrix_is_fail_closed(self):
        rule=arr.transition_policy("TRUSTED","RECOVERING")
        self.assertFalse(rule["allowed"])
        self.assertEqual(rule["severity"],"critical")
        self.assertIn("replacement_reputation_transition_reviewed",rule["required_gates"])

    def test_recovery_policy_declares_all_upward_requirements(self):
        rule=arr.transition_policy("RECOVERING","TRUSTED")
        self.assertTrue(rule["allowed"])
        self.assertEqual(rule["minimum_dwell_seconds"],arr.RECOVERY_MIN_DWELL_SECONDS)
        self.assertEqual(rule["minimum_new_effective_samples"],arr.RECOVERY_MIN_NEW_EFFECTIVE_SAMPLES)
        self.assertEqual(rule["minimum_confirmations"],arr.RECOVERY_CONFIRMATIONS_REQUIRED)
        self.assertIn("replacement_reputation_transition_completed",rule["required_gates"])

    def test_entry_exposes_versioned_transition_rule(self):
        registry,entry=arr.apply(None,self.context(),self.strong(),now=100.0)
        self.assertEqual(entry["transition_policy_version"],arr.TRANSITION_POLICY_VERSION)
        self.assertTrue(entry["transition_rule"]["allowed"])
        self.assertEqual(registry["policy"]["version"],arr.TRANSITION_POLICY_VERSION)
        self.assertIn("transition_matrix",registry["policy"])

    def test_quarantine_rule_is_critical(self):
        registry,_=arr.apply(None,self.context(),self.strong(),now=100.0)
        registry,entry=arr.apply(
            registry,self.context(),
            {**self.strong(),"sequential_drift":True},
            now=101.0,
        )
        self.assertEqual(entry["state"],"QUARANTINED")
        self.assertEqual(entry["transition_rule"]["severity"],"critical")
        self.assertIn("quarantined_replacement_revalidated",entry["required_transition_gates"])

    def test_audit_records_every_transition(self):
        registry,_=arr.apply(None,self.context(),self.strong(),now=100.0)
        registry,_=arr.apply(registry,self.context(),{**self.strong(),"sequential_drift":True},now=200.0)
        self.assertEqual(len(registry["audit"]),2)
        self.assertEqual(registry["audit"][-1]["new_state"],"QUARANTINED")

    def test_update_persists_registry(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"architecture-replacement-reputation.json"
            entry=arr.update(path,self.context(),self.strong(),now=100.0)
            self.assertTrue(path.is_file())
            loaded=arr.load(path)
            self.assertEqual(arr.lookup(loaded,self.context())["state"],entry["state"])

    def test_learning_style_sequential_dict_drives_quarantine(self):
        evidence={**self.strong(),"sequential_drift":{"drift_detected":True,"status":"drift"}}
        state=arr.desired_state(evidence)
        self.assertEqual(state["state"],"QUARANTINED")

    def test_learning_style_recovery_dict_drives_recovering(self):
        evidence={
            "effective_samples":20,"evidence_confidence":1.0,
            "wilson_lower_95":0.30,"regression_rate":0.30,
            "sequential_drift":{"drift_detected":False,"recovery_detected":True,"status":"recovery"},
        }
        state=arr.desired_state(evidence)
        self.assertEqual(state["state"],"RECOVERING")

if __name__=="__main__":
    unittest.main()

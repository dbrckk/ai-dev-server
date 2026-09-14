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

    def test_recovery_requires_multiple_confirmations(self):
        registry,_=arr.apply(None,self.context(),self.strong(),now=100.0)
        registry,_=arr.apply(registry,self.context(),{**self.strong(),"sequential_drift":True},now=200.0)
        registry,first=arr.apply(registry,self.context(),self.strong(),now=300.0)
        self.assertEqual(first["state"],"RECOVERING")
        registry,second=arr.apply(registry,self.context(),self.strong(),now=400.0)
        self.assertEqual(second["state"],"TRUSTED")
        self.assertTrue(second["promotion_eligible"])

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

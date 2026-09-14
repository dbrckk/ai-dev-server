import itertools
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
import architecture_replacement_reputation as arr

class ReplacementReputationStateMachineExhaustiveTests(unittest.TestCase):
    def setUp(self):
        self.context={
            "current_repo":"a/current","replacement_repo":"a/better",
            "framework":"flutter","project_type":"game","primary_domain":"mobile",
            "platform":"android","current_major_version":1,"replacement_major_version":2,
        }
        self.evidence={
            "UNOBSERVED":None,
            "EXPERIMENTAL":{"effective_samples":2,"evidence_confidence":0.1,"wilson_lower_95":0.2,"regression_rate":0.0},
            "TRUSTED":{"effective_samples":20,"evidence_confidence":1.0,"wilson_lower_95":0.82,"regression_rate":0.02},
            "DEGRADED":{"effective_samples":20,"evidence_confidence":1.0,"wilson_lower_95":0.3,"regression_rate":0.4},
            "QUARANTINED":{"effective_samples":20,"evidence_confidence":1.0,"wilson_lower_95":0.82,"regression_rate":0.02,"sequential_drift":True},
            "RECOVERING":{"effective_samples":20,"evidence_confidence":1.0,"wilson_lower_95":0.3,"regression_rate":0.3,"sequential_drift":{"drift_detected":False,"recovery_detected":True}},
        }

    def test_no_two_step_path_from_quarantine_to_trusted_bypasses_recovering(self):
        states=sorted(arr.REPUTATION_STATES)
        for middle in states:
            first=arr.transition_policy("QUARANTINED",middle)
            second=arr.transition_policy(middle,"TRUSTED")
            if first["allowed"] and second["allowed"]:
                self.assertEqual(
                    middle,"RECOVERING",
                    f"unsafe QUARANTINED -> {middle} -> TRUSTED path"
                )

    def test_all_allowed_dangerous_targets_have_required_gate(self):
        for source,row in arr.TRANSITION_POLICY.items():
            for target,rule in row.items():
                if not isinstance(rule,dict) or rule.get("allowed") is not True:
                    continue
                required=arr.DANGEROUS_STATE_GATES.get(target)
                if required:
                    self.assertIn(required,rule.get("required_gates",[]),f"{source}->{target}")

    def test_exhaustive_desired_state_sequences_never_jump_quarantine_to_trusted(self):
        desired_states=["TRUSTED","DEGRADED","QUARANTINED","RECOVERING","EXPERIMENTAL"]
        for sequence in itertools.product(desired_states,repeat=3):
            registry=None
            now=100.0
            previous=None
            saw_quarantine=False
            for desired in sequence:
                evidence=self.evidence[desired]
                registry,entry=arr.apply(registry,self.context,evidence,now=now)
                now+=1.0
                if entry["state"]=="QUARANTINED":
                    saw_quarantine=True
                if saw_quarantine and entry["state"]=="TRUSTED":
                    self.fail(f"unsafe direct recovery sequence: {sequence}; previous={previous}")
                previous=entry["state"]

    def test_recovery_to_trusted_requires_elapsed_time_and_new_samples(self):
        registry,_=arr.apply(None,self.context,self.evidence["TRUSTED"],now=100.0)
        registry,_=arr.apply(registry,self.context,self.evidence["QUARANTINED"],now=200.0)
        registry,entry=arr.apply(registry,self.context,self.evidence["TRUSTED"],now=300.0)
        self.assertEqual(entry["state"],"RECOVERING")

        for dt,samples in [
            (1.0,20),
            (arr.RECOVERY_MIN_DWELL_SECONDS+1,20),
        ]:
            e={**self.evidence["TRUSTED"],"effective_samples":samples}
            registry2,entry2=arr.apply(registry,self.context,e,now=300.0+dt)
            self.assertNotEqual(entry2["state"],"TRUSTED")

        e={**self.evidence["TRUSTED"],"effective_samples":22}
        _,entry3=arr.apply(
            registry,self.context,e,
            now=300.0+arr.RECOVERY_MIN_DWELL_SECONDS+1
        )
        self.assertEqual(entry3["state"],"TRUSTED")

if __name__=="__main__":
    unittest.main()

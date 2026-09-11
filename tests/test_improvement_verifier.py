import unittest

from studio.improvement_verifier import ImprovementVerificationError, verify_improvement_result


class ImprovementVerifierTests(unittest.TestCase):
    def complete(self,extra=None):
        result={
            "status":"complete",
            "report":{
                "completion":{"finished":True},
                "release_evidence":{},
            },
        }
        if extra:
            result.update(extra)
        return result

    def test_full_regression_requires_machine_completion(self):
        candidate={
            "kind":"repeated_failure",
            "source":{"failure":"flaky emulator"},
        }
        self.assertNotIn("full_regression_passed",verify_improvement_result(candidate,{"status":"complete","report":{"completion":{"finished":False}}}))
        self.assertTrue(verify_improvement_result(candidate,self.complete())["full_regression_passed"])

    def test_repeated_failure_needs_matching_targeted_verification(self):
        candidate={"kind":"repeated_failure","source":{"failure":"flaky emulator"}}
        result=self.complete({
            "improvement_verification":{
                "kind":"repeated_failure",
                "failure":"different",
                "passed":True,
                "targeted_test_passed":True,
            }
        })
        evidence=verify_improvement_result(candidate,result)
        self.assertNotIn("targeted_regression_passed",evidence)
        result["improvement_verification"]["failure"]="flaky emulator"
        self.assertTrue(verify_improvement_result(candidate,result)["targeted_regression_passed"])

    def test_capability_churn_needs_matching_preflight(self):
        candidate={"kind":"capability_churn","source":{"capability":"billing_qa"}}
        result=self.complete({
            "improvement_verification":{
                "kind":"capability_churn",
                "capability":"billing_qa",
                "passed":True,
                "preflight_passed":True,
            }
        })
        evidence=verify_improvement_result(candidate,result)
        self.assertTrue(evidence["capability_preflight_passed"])
        self.assertTrue(evidence["full_regression_passed"])

    def test_warning_removed_is_derived_from_revalidated_stage(self):
        candidate={
            "kind":"persistent_warning",
            "source":{"stage":"artwork_qa","warnings":["contrast close to threshold"]},
        }
        result=self.complete()
        result["report"]["release_evidence"]["artwork_qa"]={
            "passed":True,
            "warnings":[],
        }
        evidence=verify_improvement_result(candidate,result)
        self.assertTrue(evidence["warning_removed"])
        self.assertTrue(evidence["stage_revalidated"])
        self.assertTrue(evidence["full_regression_passed"])

    def test_warning_still_present_is_not_proved(self):
        candidate={
            "kind":"persistent_warning",
            "source":{"stage":"artwork_qa","warnings":["contrast close to threshold"]},
        }
        result=self.complete()
        result["report"]["release_evidence"]["artwork_qa"]={
            "passed":True,
            "warnings":["contrast close to threshold"],
        }
        evidence=verify_improvement_result(candidate,result)
        self.assertNotIn("warning_removed",evidence)

    def test_unknown_kind_rejected(self):
        with self.assertRaisesRegex(ImprovementVerificationError,"unsupported"):
            verify_improvement_result({"kind":"magic","source":{}},self.complete())


if __name__=="__main__":
    unittest.main()

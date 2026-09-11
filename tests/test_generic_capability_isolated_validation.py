import hashlib
import json
import unittest
from unittest.mock import patch

from studio.generic_capability_isolated_validation import (
    IsolatedCapabilityValidationError,
    validate_in_isolation,
)


def envelope():
    candidate={
        "version":1,
        "capability":"improvement.apply.repeated_failure",
        "provider":"studio.capabilities.improvement_apply_repeated_failure",
        "implementation":"def run(context):\n    return {'passed': True, 'evidence': {'ok': True}}\n",
        "tests":"import unittest\nfrom studio.capabilities.improvement_apply_repeated_failure import run\nclass T(unittest.TestCase):\n    def test_run(self):\n        self.assertTrue(run({})['passed'])\n",
        "risk_notes":["isolated"],
        "research":[],
    }
    digest=hashlib.sha256(json.dumps(candidate,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    return {
        "status":"candidate_synthesized",
        "candidate_id":"capability-candidate:improvement.apply.repeated_failure:"+digest[:16],
        "candidate_sha256":digest,
        "candidate":candidate,
        "benchmark_status":"required",
        "regression_status":"required",
        "promotion_status":"not_ready",
        "capability_registered":False,
    }


class GenericCapabilityIsolatedValidationTests(unittest.TestCase):
    @patch("studio.generic_capability_isolated_validation._docker")
    def test_passed_isolation_makes_candidate_eligible_only(self,docker):
        docker.side_effect=[
            (1,"Ran 1 test in 0.001s\nFAILED (errors=1)"),
            (0,""),
            (0,"Ran 1 test in 0.001s\nOK"),
            (0,"Ran 120 tests in 1.0s\nOK"),
        ]
        result=validate_in_isolation(envelope())
        self.assertEqual(result["validation"]["status"],"candidate_validated")
        self.assertEqual(result["validation"]["promotion_status"],"eligible")
        self.assertFalse(result["validation"]["capability_registered"])
        self.assertFalse(result["candidate_materialized_in_trusted_repo"])

    def test_forbidden_import_fails_before_execution(self):
        value=envelope()
        value["candidate"]["implementation"]="import socket\ndef run(context): return {}\n"
        value["candidate_sha256"]=hashlib.sha256(json.dumps(value["candidate"],sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
        value["candidate_id"]="capability-candidate:improvement.apply.repeated_failure:"+value["candidate_sha256"][:16]
        with self.assertRaisesRegex(IsolatedCapabilityValidationError,"forbidden"):
            validate_in_isolation(value)


if __name__=="__main__":
    unittest.main()

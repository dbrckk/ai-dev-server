import hashlib
import json
import unittest

from studio.generic_capability_isolated_validation import (
    IsolatedCapabilityValidationError,
    validate_isolated_validation_result,
)


def report():
    sha="a"*64
    def proof(kind, **extra):
        value={"kind":kind,"candidate_sha256":sha,"passed":True,**extra}
        digest=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
        value["evidence_sha256"]=digest
        return value
    validation={
        "status":"candidate_validated",
        "candidate_id":"capability-candidate:test:1234",
        "candidate_sha256":sha,
        "capability":"test.capability",
        "provider":"studio.capabilities.test_capability",
        "benchmark_status":"passed",
        "regression_status":"passed",
        "promotion_status":"eligible",
        "capability_registered":False,
        "evidence":{
            "targeted_test_sha256":"b"*64,
            "benchmark_sha256":"c"*64,
            "regression_sha256":"d"*64,
        },
    }
    return {
        "status":"isolated_validation_complete",
        "candidate_id":"capability-candidate:test:1234",
        "candidate_sha256":sha,
        "targeted_test":proof("targeted_test",tests_collected=1,compile_passed=True),
        "benchmark":proof("benchmark",score=1,baseline_score=0,differential_improvement=True),
        "regression":proof("regression",tests_collected=100),
        "validation":validation,
        "candidate_materialized_in_trusted_repo":False,
        "network":"disabled",
        "capabilities":"dropped",
    }


class GenericCapabilityValidationReportTests(unittest.TestCase):
    def test_report_validates(self):
        value=report()
        self.assertEqual(validate_isolated_validation_result(value),value)

    def test_tampered_proof_fails_closed(self):
        value=report()
        value["benchmark"]["score"]=99
        with self.assertRaisesRegex(IsolatedCapabilityValidationError,"integrity"):
            validate_isolated_validation_result(value)

    def test_trust_boundary_claim_fails_closed(self):
        value=report()
        value["candidate_materialized_in_trusted_repo"]=True
        with self.assertRaisesRegex(IsolatedCapabilityValidationError,"mutation"):
            validate_isolated_validation_result(value)


if __name__=="__main__":
    unittest.main()

import hashlib
import json
import unittest

from studio.generic_capability_isolated_validation import (
    IsolatedCapabilityValidationError,
    validate_isolated_validation_result,
)


def seal(value):
    return hashlib.sha256(
        json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    ).hexdigest()


def report():
    sha="a"*64
    candidate_id="capability-candidate:test:1234"

    def proof(kind, **extra):
        value={"kind":kind,"candidate_sha256":sha,"passed":True,**extra}
        value["evidence_sha256"]=seal(value)
        return value

    targeted=proof("targeted_test",tests_collected=1,compile_passed=True)
    benchmark=proof("benchmark",score=1,baseline_score=0,differential_improvement=True)
    regression=proof("regression",tests_collected=100)
    validation={
        "status":"candidate_validated",
        "candidate_id":candidate_id,
        "candidate_sha256":sha,
        "capability":"test.capability",
        "provider":"studio.capabilities.test_capability",
        "benchmark_status":"passed",
        "regression_status":"passed",
        "promotion_status":"eligible",
        "capability_registered":False,
        "evidence":{
            "targeted_test_sha256":targeted["evidence_sha256"],
            "benchmark_sha256":benchmark["evidence_sha256"],
            "regression_sha256":regression["evidence_sha256"],
        },
    }
    value={
        "status":"isolated_validation_complete",
        "candidate_id":candidate_id,
        "candidate_sha256":sha,
        "targeted_test":targeted,
        "benchmark":benchmark,
        "regression":regression,
        "validation":validation,
        "candidate_materialized_in_trusted_repo":False,
        "network":"disabled",
        "capabilities":"dropped",
    }
    value["report_sha256"]=seal(value)
    return value


def reseal(value):
    unsigned=dict(value)
    unsigned.pop("report_sha256",None)
    value["report_sha256"]=seal(unsigned)


class GenericCapabilityValidationReportTests(unittest.TestCase):
    def test_report_validates(self):
        value=report()
        self.assertEqual(validate_isolated_validation_result(value),value)

    def test_tampered_proof_fails_closed(self):
        value=report()
        value["benchmark"]["score"]=99
        reseal(value)
        with self.assertRaisesRegex(IsolatedCapabilityValidationError,"proof integrity"):
            validate_isolated_validation_result(value)

    def test_report_digest_tampering_fails_closed(self):
        value=report()
        value["network"]="enabled"
        with self.assertRaisesRegex(IsolatedCapabilityValidationError,"report integrity"):
            validate_isolated_validation_result(value)

    def test_validation_evidence_must_match_proofs(self):
        value=report()
        value["validation"]["evidence"]["benchmark_sha256"]="b"*64
        reseal(value)
        with self.assertRaisesRegex(IsolatedCapabilityValidationError,"decision evidence mismatch"):
            validate_isolated_validation_result(value)

    def test_candidate_identity_must_match_decision(self):
        value=report()
        value["validation"]["candidate_id"]="capability-candidate:other:1234"
        reseal(value)
        with self.assertRaisesRegex(IsolatedCapabilityValidationError,"decision mismatch"):
            validate_isolated_validation_result(value)

    def test_validated_decision_requires_all_proofs_passed(self):
        value=report()
        proof=value["regression"]
        proof["passed"]=False
        proof["evidence_sha256"]=seal({k:v for k,v in proof.items() if k!="evidence_sha256"})
        value["validation"]["evidence"]["regression_sha256"]=proof["evidence_sha256"]
        reseal(value)
        with self.assertRaisesRegex(IsolatedCapabilityValidationError,"lacks passing proof"):
            validate_isolated_validation_result(value)

    def test_validated_decision_requires_non_regressing_benchmark(self):
        value=report()
        proof=value["benchmark"]
        proof["score"]=-1
        proof["evidence_sha256"]=seal({k:v for k,v in proof.items() if k!="evidence_sha256"})
        value["validation"]["evidence"]["benchmark_sha256"]=proof["evidence_sha256"]
        reseal(value)
        with self.assertRaisesRegex(IsolatedCapabilityValidationError,"lacks passing proof"):
            validate_isolated_validation_result(value)

    def test_non_boolean_proof_result_fails_closed(self):
        value=report()
        proof=value["targeted_test"]
        proof["passed"]=1
        proof["evidence_sha256"]=seal({k:v for k,v in proof.items() if k!="evidence_sha256"})
        value["validation"]["evidence"]["targeted_test_sha256"]=proof["evidence_sha256"]
        reseal(value)
        with self.assertRaisesRegex(IsolatedCapabilityValidationError,"proof result"):
            validate_isolated_validation_result(value)

    def test_trust_boundary_claim_fails_closed(self):
        value=report()
        value["candidate_materialized_in_trusted_repo"]=True
        reseal(value)
        with self.assertRaisesRegex(IsolatedCapabilityValidationError,"mutation"):
            validate_isolated_validation_result(value)


if __name__=="__main__":
    unittest.main()

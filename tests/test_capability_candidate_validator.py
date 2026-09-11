import hashlib
import json
import unittest

from studio.capability_candidate_validator import CapabilityValidationError, validate_candidate


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def envelope():
    candidate={
        "version":1,
        "capability":"image_assets",
        "provider":"studio.capabilities.image_assets",
        "implementation":"def provide():\n    return {'ok': True}\n",
        "tests":"def test_provider():\n    assert True\n",
        "risk_notes":["sandbox"],
        "research":[
            {"entry_id":"research:1","content_sha256":"a"*64,"item_sha256":"b"*64,"source":"https://example.org/a"},
            {"entry_id":"research:2","content_sha256":"c"*64,"item_sha256":"d"*64,"source":"https://example.org/b"},
        ],
    }
    return {
        "status":"candidate_synthesized",
        "candidate_id":"capability-candidate:image_assets:"+digest(candidate)[:16],
        "candidate_sha256":digest(candidate),
        "candidate":candidate,
        "benchmark_status":"required",
        "regression_status":"required",
        "promotion_status":"not_ready",
        "capability_registered":False,
    }


def proof(candidate_sha, *, passed=True, score=None, baseline_score=None, marker="e"):
    out={"candidate_sha256":candidate_sha,"passed":passed,"evidence_sha256":marker*64}
    if score is not None: out["score"]=score
    if baseline_score is not None: out["baseline_score"]=baseline_score
    return out


class CapabilityCandidateValidatorTests(unittest.TestCase):
    def test_all_gates_make_candidate_only_eligible(self):
        env=envelope(); sha=env["candidate_sha256"]
        result=validate_candidate(
            env,
            proof(sha,marker="a"),
            proof(sha,score=12,baseline_score=10,marker="b"),
            proof(sha,marker="c"),
        )
        self.assertEqual(result["status"],"candidate_validated")
        self.assertEqual(result["promotion_status"],"eligible")
        self.assertFalse(result["capability_registered"])
        self.assertEqual(result["provider"],"studio.capabilities.image_assets")

    def test_targeted_test_failure_rejects_candidate(self):
        env=envelope(); sha=env["candidate_sha256"]
        result=validate_candidate(
            env,
            proof(sha,passed=False,marker="a"),
            proof(sha,score=12,baseline_score=10,marker="b"),
            proof(sha,marker="c"),
        )
        self.assertEqual(result["status"],"candidate_rejected")
        self.assertEqual(result["failed_gate"],"targeted_test")
        self.assertEqual(result["promotion_status"],"not_ready")

    def test_benchmark_regression_rejects_candidate(self):
        env=envelope(); sha=env["candidate_sha256"]
        result=validate_candidate(
            env,
            proof(sha,marker="a"),
            proof(sha,score=9,baseline_score=10,marker="b"),
            proof(sha,marker="c"),
        )
        self.assertEqual(result["failed_gate"],"benchmark_regression")
        self.assertEqual(result["promotion_status"],"not_ready")

    def test_tampered_candidate_fails_closed(self):
        env=envelope()
        env["candidate"]["implementation"]="tampered"
        sha=env["candidate_sha256"]
        with self.assertRaisesRegex(CapabilityValidationError,"integrity"):
            validate_candidate(
                env,
                proof(sha,marker="a"),
                proof(sha,score=12,baseline_score=10,marker="b"),
                proof(sha,marker="c"),
            )

    def test_cross_candidate_proof_is_rejected(self):
        env=envelope(); sha=env["candidate_sha256"]
        with self.assertRaisesRegex(CapabilityValidationError,"mismatch"):
            validate_candidate(
                env,
                proof("f"*64,marker="a"),
                proof(sha,score=12,baseline_score=10,marker="b"),
                proof(sha,marker="c"),
            )


if __name__=="__main__":
    unittest.main()

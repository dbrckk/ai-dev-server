import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from studio.capability_synthesis import validate_candidate_envelope


class GenericCapabilityCandidatePersistenceTests(unittest.TestCase):
    def envelope(self):
        candidate={
            "version":1,
            "capability":"improvement.apply.repeated_failure",
            "provider":"studio.capabilities.improvement_apply_repeated_failure",
            "implementation":"def run(context):\n    return {'passed': False, 'evidence': {}}\n",
            "tests":"import unittest\n",
            "risk_notes":["candidate only"],
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

    def test_candidate_envelope_integrity(self):
        value=self.envelope()
        self.assertEqual(validate_candidate_envelope(value),value)

    def test_tampering_is_rejected(self):
        value=self.envelope()
        value["candidate"]["tests"]="changed"
        with self.assertRaisesRegex(ValueError,"integrity"):
            validate_candidate_envelope(value)


if __name__=="__main__":
    unittest.main()

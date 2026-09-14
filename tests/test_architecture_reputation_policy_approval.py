import copy
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
from architecture_reputation_policy_approval import *

class ApprovalProvenanceTests(unittest.TestCase):
    def approval(self,reinforced=False):
        a={"migration_id":"m1","review_digest":"r1","reviewer":{"id":"alice","roles":["reviewer"]}}
        if reinforced:a["second_reviewer"]={"id":"bob","roles":["risk_owner"]}
        a["approval_digest"]=approval_digest(a)
        return a
    def test_standard_approval(self):
        self.assertEqual(validate_approval(self.approval(),{"migration_id":"m1","review_digest":"r1"},reinforced=False)["reviewer_id"],"alice")
    def test_reinforced_requires_separation(self):
        a=self.approval(True);a["second_reviewer"]["id"]="alice";a["approval_digest"]=approval_digest(a)
        with self.assertRaises(ApprovalProvenanceError):validate_approval(a,{"migration_id":"m1","review_digest":"r1"},reinforced=True)
    def test_reinforced_accepts_distinct_risk_owner(self):
        self.assertEqual(validate_approval(self.approval(True),{"migration_id":"m1","review_digest":"r1"},reinforced=True)["second_reviewer_id"],"bob")
    def test_ledger_is_append_only_and_replay_safe(self):
        a=self.approval();ledger=consume(None,migration_id="m1",review_digest="r1",approval_digest_value=a["approval_digest"],applied_at=1)
        self.assertTrue(validate_ledger(ledger)["valid"])
        with self.assertRaises(ApprovalProvenanceError):consume(ledger,migration_id="m1",review_digest="r1",approval_digest_value=a["approval_digest"],applied_at=2)
    def test_tampered_ledger_fails(self):
        a=self.approval();ledger=consume(None,migration_id="m1",review_digest="r1",approval_digest_value=a["approval_digest"],applied_at=1)
        ledger=copy.deepcopy(ledger);ledger["events"][0]["applied_at"]=99
        self.assertFalse(validate_ledger(ledger)["valid"])

    def github_attestation(self,reinforced=False):
        a={
            "repository":"dbrckk/ai-dev-server","commit_sha":"abc","reviewed_commit_sha":"abc",
            "pull_request":42,"workflow_run_id":99,"migration_id":"m1","review_digest":"r1",
            "reviewer":{"login":"alice","review_state":"APPROVED","permission":"write"},
            "workflow":{"head_sha":"abc","conclusion":"success"},
        }
        if reinforced:a["second_reviewer"]={"login":"bob","review_state":"APPROVED","permission":"maintain"}
        payload={k:v for k,v in a.items() if k!="attestation_digest"}
        a["attestation_digest"]=hashlib.sha256(_canonical(payload).encode()).hexdigest()
        return a
    def test_github_attestation_binds_commit_review_permission_and_workflow(self):
        got=validate_github_attestation(self.github_attestation(),{"migration_id":"m1","review_digest":"r1"},reinforced=False)
        self.assertEqual(got["github_reviewer"],"alice")
    def test_github_attestation_rejects_stale_commit(self):
        a=self.github_attestation();a["reviewed_commit_sha"]="old";a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)
    def test_github_attestation_rejects_read_only_reviewer(self):
        a=self.github_attestation();a["reviewer"]["permission"]="read";a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)
    def test_github_reinforced_requires_distinct_approver(self):
        a=self.github_attestation(True);a["second_reviewer"]["login"]="alice";a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=True)

if __name__=="__main__":unittest.main()

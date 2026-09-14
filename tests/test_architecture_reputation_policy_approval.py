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
            "pull_request":42,"workflow_run_id":99,"required_workflow_run_id":99,"migration_id":"m1","review_digest":"r1",
            "reviewer":{"login":"alice","review_state":"APPROVED","permission":"write","submitted_at_epoch":1767225610.0},
            "head_commit_timestamp":1767225600.0,
            "pr_identity":{"number":42,"state":"open","draft":False,"head_ref":"policy/migration","head_sha":"abc","base_ref":"main","author":"author"},
            "required_checks":{"valid":True,"required_checks":["validate","python-tests"],"passed_checks":["validate","python-tests"],"missing_checks":[],"incomplete_checks":[],"failed_checks":[],"stale_checks":[],"workflow_run_ids":[99],"common_workflow_run_id":99,"mixed_workflow_runs":False,"check_evidence":{"validate":{"id":1,"head_sha":"abc","timestamp":1767225630.0,"status":"completed","conclusion":"success","workflow_run_id":99},"python-tests":{"id":2,"head_sha":"abc","timestamp":1767225640.0,"status":"completed","conclusion":"success","workflow_run_id":99}}},
            "workflow_file":{"path":".github/workflows/ci.yml","blob_sha":"blob123","size":43,"sha256":"5949de6344caa241ad89c8f9dfa16d52628f893809c8fc436cac9565c8f9fdb4","content_b64":"bmFtZTogQ0kKam9iczoKICB2YWxpZGF0ZToKICBweXRob24tdGVzdHM6Cg==","policy_validation":{"valid":True}},
            "workflow":{"head_sha":"abc","conclusion":"success","name":"CI","path":".github/workflows/ci.yml","timestamp":1767225625.0},
        }
        if reinforced:a["second_reviewer"]={"login":"bob","review_state":"APPROVED","permission":"maintain","submitted_at_epoch":1767225620.0}
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

    def test_github_attestation_rejects_review_before_head_commit(self):
        a=self.github_attestation()
        a["reviewer"]["submitted_at_epoch"]=1767225599.0
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

    def test_github_attestation_rejects_draft_pr(self):
        a=self.github_attestation()
        a["pr_identity"]["draft"]=True
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

    def test_github_attestation_rejects_mixed_workflow_runs(self):
        a=self.github_attestation()
        a["required_checks"]["mixed_workflow_runs"]=True
        a["required_checks"]["workflow_run_ids"]=[99,100]
        a["required_checks"]["common_workflow_run_id"]=None
        a["required_checks"]["check_evidence"]["python-tests"]["workflow_run_id"]=100
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

    def test_github_attestation_rejects_attested_workflow_id_mismatch(self):
        a=self.github_attestation()
        a["workflow_run_id"]=100
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

    def test_github_attestation_rejects_wrong_workflow_file_digest(self):
        a=self.github_attestation()
        a["workflow_file"]["sha256"]="bad"
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

    def test_github_attestation_rejects_untrusted_workflow_path(self):
        a=self.github_attestation()
        a["workflow"]["path"]=".github/workflows/other.yml"
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

    def test_github_attestation_rejects_untrusted_workflow_name(self):
        a=self.github_attestation()
        a["workflow"]["name"]="Other"
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

    def test_github_attestation_rejects_stale_workflow(self):
        a=self.github_attestation()
        a["workflow"]["timestamp"]=1767225599.0
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

    def test_github_attestation_rejects_stale_required_check(self):
        a=self.github_attestation()
        a["required_checks"]["valid"]=False
        a["required_checks"]["stale_checks"]=["validate"]
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

    def test_github_attestation_rejects_forged_pass_without_check_evidence(self):
        a=self.github_attestation()
        a["required_checks"]["check_evidence"].pop("validate")
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

    def test_github_attestation_rejects_check_evidence_for_wrong_sha(self):
        a=self.github_attestation()
        a["required_checks"]["check_evidence"]["validate"]["head_sha"]="old"
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

    def test_github_attestation_rejects_check_evidence_before_head_commit(self):
        a=self.github_attestation()
        a["required_checks"]["check_evidence"]["validate"]["timestamp"]=1767225599.0
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

    def test_github_attestation_rejects_failed_required_check(self):
        a=self.github_attestation()
        a["required_checks"]["valid"]=False
        a["required_checks"]["failed_checks"]=["validate"]
        a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
        with self.assertRaises(ApprovalProvenanceError):
            validate_github_attestation(a,{"migration_id":"m1","review_digest":"r1"},reinforced=False)

if __name__=="__main__":unittest.main()

import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
from architecture_reputation_policy_github_attestation import *
from architecture_reputation_policy_approval import ApprovalProvenanceError

class GitHubAttestationBuilderTests(unittest.TestCase):
    plan={"migration_id":"m","review_digest":"r"}

    def check_runs(self):
        return [
            {"name":"validate","status":"completed","conclusion":"success","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/1"},
            {"name":"python-tests","status":"completed","conclusion":"success","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/1"},
        ]

    def pr_identity(self):
        return {"number":7,"state":"open","draft":False,"head_ref":"feature/policy","head_sha":"abc","base_ref":"main","author":"author"}
    def test_build_standard(self):
        a=build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
            reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:10Z"}],
            permissions={"alice":"write"},workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"CI"}],
            check_runs=self.check_runs(),pr_identity=self.pr_identity(),head_commit_timestamp=1767225600.0,reinforced=False)
        self.assertEqual(a["reviewer"]["login"],"alice");self.assertEqual(a["workflow_run_id"],9)
    def test_latest_review_wins(self):
        rows=latest_approvals([
            {"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:10Z"},
            {"author":{"login":"alice"},"state":"CHANGES_REQUESTED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:20Z"}],"abc",head_commit_timestamp=1767225600.0)
        self.assertEqual(rows,[])
    def test_reinforced_requires_two_eligible(self):
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc"}],
                permissions={"alice":"write"},workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success"}],
                check_runs=self.check_runs(),pr_identity=self.pr_identity(),head_commit_timestamp=1767225600.0,reinforced=True)
    def test_missing_required_check_rejected(self):
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc"}],
                permissions={"alice":"write"},workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"CI"}],
                check_runs=self.check_runs()[:1],pr_identity=self.pr_identity(),reinforced=False)

    def test_draft_pr_rejected(self):
        identity=self.pr_identity()
        identity["draft"]=True
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc"}],
                permissions={"alice":"write"},workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"CI"}],
                check_runs=self.check_runs(),pr_identity=identity,reinforced=False)

    def test_approval_before_head_commit_is_rejected(self):
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc","submitted_at":"2025-12-31T23:59:59Z"}],
                permissions={"alice":"write"},workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"CI"}],
                check_runs=self.check_runs(),pr_identity=self.pr_identity(),head_commit_timestamp=1767225600.0,reinforced=False)

    def test_stale_workflow_rejected(self):
        with self.assertRaises(ApprovalProvenanceError):
            successful_workflow([{"id":9,"head_sha":"old","conclusion":"success"}],"abc")
if __name__=="__main__":unittest.main()

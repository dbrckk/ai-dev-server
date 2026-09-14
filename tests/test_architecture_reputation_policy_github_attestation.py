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
            {"id":1,"name":"validate","head_sha":"abc","status":"completed","conclusion":"success","started_at":"2026-01-01T00:00:30Z","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/9"},
            {"id":2,"name":"python-tests","head_sha":"abc","status":"completed","conclusion":"success","started_at":"2026-01-01T00:00:40Z","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/9"},
        ]

    def pr_identity(self):
        return {"number":7,"state":"open","draft":False,"head_ref":"feature/policy","head_sha":"abc","base_ref":"main","author":"author"}

    def workflow_file(self):
        return {"path":".github/workflows/ci.yml","blob_sha":"blob123","size":9,"sha256":"a"*64}
    def test_build_standard(self):
        a=build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
            reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:10Z"}],
            permissions={"alice":"write"},workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"CI","path":".github/workflows/ci.yml@refs/pull/7/merge","created_at":"2026-01-01T00:00:25Z"}],
            check_runs=self.check_runs(),pr_identity=self.pr_identity(),workflow_file=self.workflow_file(),head_commit_timestamp=1767225600.0,reinforced=False)
        self.assertEqual(a["reviewer"]["login"],"alice");self.assertEqual(a["workflow_run_id"],9)
    def test_latest_review_wins(self):
        rows=latest_approvals([
            {"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:10Z"},
            {"author":{"login":"alice"},"state":"CHANGES_REQUESTED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:20Z"}],"abc",head_commit_timestamp=1767225600.0)
        self.assertEqual(rows,[])
    def test_latest_review_order_is_timestamp_driven(self):
        rows=latest_approvals([
            {"id":10,"author":{"login":"alice"},"state":"CHANGES_REQUESTED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:20Z"},
            {"id":9,"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:10Z"},
        ],"abc",head_commit_timestamp=1767225600.0)
        self.assertEqual(rows,[])

    def test_reinforced_requires_two_eligible(self):
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc"}],
                permissions={"alice":"write"},workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","created_at":"2026-01-01T00:00:25Z"}],
                check_runs=self.check_runs(),pr_identity=self.pr_identity(),workflow_file=self.workflow_file(),head_commit_timestamp=1767225600.0,reinforced=True)
    def test_missing_required_check_rejected(self):
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc"}],
                permissions={"alice":"write"},workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"CI","path":".github/workflows/ci.yml@refs/pull/7/merge","created_at":"2026-01-01T00:00:25Z"}],
                check_runs=self.check_runs()[:1],pr_identity=self.pr_identity(),reinforced=False)

    def test_draft_pr_rejected(self):
        identity=self.pr_identity()
        identity["draft"]=True
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc"}],
                permissions={"alice":"write"},workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"CI","path":".github/workflows/ci.yml@refs/pull/7/merge","created_at":"2026-01-01T00:00:25Z"}],
                check_runs=self.check_runs(),pr_identity=identity,workflow_file=self.workflow_file(),head_commit_timestamp=1767225600.0,reinforced=False)

    def test_approval_before_head_commit_is_rejected(self):
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc","submitted_at":"2025-12-31T23:59:59Z"}],
                permissions={"alice":"write"},workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"CI","path":".github/workflows/ci.yml@refs/pull/7/merge","created_at":"2026-01-01T00:00:25Z"}],
                check_runs=self.check_runs(),pr_identity=self.pr_identity(),workflow_file=self.workflow_file(),head_commit_timestamp=1767225600.0,reinforced=False)

    def test_wrong_workflow_name_rejected(self):
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:10Z"}],
                permissions={"alice":"write"},
                workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"Other","created_at":"2026-01-01T00:00:25Z"}],
                check_runs=self.check_runs(),pr_identity=self.pr_identity(),workflow_file=self.workflow_file(),head_commit_timestamp=1767225600.0,reinforced=False)

    def test_wrong_workflow_path_rejected(self):
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:10Z"}],
                permissions={"alice":"write"},
                workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"CI","path":".github/workflows/other.yml","created_at":"2026-01-01T00:00:25Z"}],
                check_runs=self.check_runs(),pr_identity=self.pr_identity(),workflow_file=self.workflow_file(),head_commit_timestamp=1767225600.0,reinforced=False)

    def test_stale_workflow_time_rejected(self):
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:10Z"}],
                permissions={"alice":"write"},
                workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"CI","created_at":"2025-12-31T23:59:59Z"}],
                check_runs=self.check_runs(),pr_identity=self.pr_identity(),workflow_file=self.workflow_file(),head_commit_timestamp=1767225600.0,reinforced=False)

    def test_stale_check_time_rejected(self):
        checks=self.check_runs()
        checks[0]["started_at"]="2025-12-31T23:59:59Z"
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:10Z"}],
                permissions={"alice":"write"},
                workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"CI","path":".github/workflows/ci.yml@refs/pull/7/merge","created_at":"2026-01-01T00:00:25Z"}],
                check_runs=checks,pr_identity=self.pr_identity(),head_commit_timestamp=1767225600.0,reinforced=False)

    def test_required_checks_from_different_workflow_runs_rejected(self):
        checks=self.check_runs()
        checks[1]["details_url"]="https://github.com/o/r/actions/runs/10"
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc","submitted_at":"2026-01-01T00:00:10Z"}],
                permissions={"alice":"write"},
                workflow_runs=[
                    {"id":9,"head_sha":"abc","conclusion":"success","name":"CI","path":".github/workflows/ci.yml@refs/pull/7/merge","created_at":"2026-01-01T00:00:25Z"},
                    {"id":10,"head_sha":"abc","conclusion":"success","name":"CI","created_at":"2026-01-01T00:00:26Z"},
                ],
                check_runs=checks,pr_identity=self.pr_identity(),head_commit_timestamp=1767225600.0,reinforced=False)

    def test_stale_workflow_rejected(self):
        with self.assertRaises(ApprovalProvenanceError):
            successful_workflow([{"id":9,"head_sha":"old","conclusion":"success","created_at":"2026-01-01T00:00:25Z"}],"abc",head_commit_timestamp=1767225600.0)
if __name__=="__main__":unittest.main()

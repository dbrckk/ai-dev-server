import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
from architecture_reputation_policy_github_attestation import *
from architecture_reputation_policy_approval import ApprovalProvenanceError

class GitHubAttestationBuilderTests(unittest.TestCase):
    plan={"migration_id":"m","review_digest":"r"}
    def test_build_standard(self):
        a=build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
            reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc"}],
            permissions={"alice":"write"},workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success","name":"CI"}],reinforced=False)
        self.assertEqual(a["reviewer"]["login"],"alice");self.assertEqual(a["workflow_run_id"],9)
    def test_latest_review_wins(self):
        rows=latest_approvals([
            {"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc"},
            {"author":{"login":"alice"},"state":"CHANGES_REQUESTED","commit_sha":"abc"}],"abc")
        self.assertEqual(rows,[])
    def test_reinforced_requires_two_eligible(self):
        with self.assertRaises(ApprovalProvenanceError):
            build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
                reviews=[{"author":{"login":"alice"},"state":"APPROVED","commit_sha":"abc"}],
                permissions={"alice":"write"},workflow_runs=[{"id":9,"head_sha":"abc","conclusion":"success"}],reinforced=True)
    def test_stale_workflow_rejected(self):
        with self.assertRaises(ApprovalProvenanceError):
            successful_workflow([{"id":9,"head_sha":"old","conclusion":"success"}],"abc")
if __name__=="__main__":unittest.main()

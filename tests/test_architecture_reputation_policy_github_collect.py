import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
import architecture_reputation_policy_github_collect as collector

class GitHubAttestationCollectorTests(unittest.TestCase):
    def plan(self,reinforced=False):
        return {
            "migration_id":"m1",
            "review_digest":"r1",
            "risk":{"reinforced_review_required":reinforced},
        }

    def responses(self,reinforced=False):
        reviews=[
            {"user":{"login":"alice"},"state":"APPROVED","commit_id":"a"*40},
        ]
        if reinforced:
            reviews.append({"user":{"login":"bob"},"state":"APPROVED","commit_id":"a"*40})
        return reviews

    def fake_request(self,reinforced=False):
        reviews=self.responses(reinforced)
        def _request(url,token,method="GET",payload=None,allow_404=False):
            if "/pulls/7/reviews" in url:
                return reviews
            if url.endswith("/pulls/7"):
                return {"head":{"sha":"a"*40}}
            if "/collaborators/alice/permission" in url:
                return {"permission":"write"}
            if "/collaborators/bob/permission" in url:
                return {"permission":"maintain"}
            if "/actions/runs?" in url:
                return {"workflow_runs":[{"id":99,"head_sha":"a"*40,"conclusion":"success","name":"CI"}]}
            raise AssertionError(url)
        return _request

    def test_collects_standard_attestation(self):
        with patch.object(collector,"_request",side_effect=self.fake_request(False)):
            result=collector.collect(self.plan(False),token="t",repository="o/r",pull_request=7)
        self.assertEqual(result["reviewer"]["login"],"alice")
        self.assertEqual(result["workflow_run_id"],99)

    def test_collects_reinforced_attestation(self):
        with patch.object(collector,"_request",side_effect=self.fake_request(True)):
            result=collector.collect(self.plan(True),token="t",repository="o/r",pull_request=7)
        self.assertEqual(result["second_reviewer"]["login"],"bob")

    def test_missing_token_is_fail_closed(self):
        with self.assertRaises(collector.GitHubAttestationCollectionError):
            collector.collect(self.plan(),token="",repository="o/r",pull_request=7)

if __name__=="__main__":
    unittest.main()

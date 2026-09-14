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
            {"user":{"login":"alice"},"state":"APPROVED","commit_id":"a"*40,"submitted_at":"2026-01-01T00:00:10Z"},
        ]
        if reinforced:
            reviews.append({"user":{"login":"bob"},"state":"APPROVED","commit_id":"a"*40,"submitted_at":"2026-01-01T00:00:20Z"})
        return reviews

    def fake_request(self,reinforced=False):
        reviews=self.responses(reinforced)
        def _request(url,token,method="GET",payload=None,allow_404=False):
            if "/pulls/7/reviews" in url:
                return reviews
            if url.endswith("/pulls/7"):
                return {
                    "state":"open","draft":False,
                    "head":{"sha":"a"*40,"ref":"policy/migration"},
                    "base":{"ref":"main"},
                    "user":{"login":"alice"},
                }
            if "/commits/" in url and "/check-runs" not in url:
                return {"commit":{"committer":{"date":"2026-01-01T00:00:00Z"}}}
            if "/collaborators/alice/permission" in url:
                return {"permission":"write"}
            if "/collaborators/bob/permission" in url:
                return {"permission":"maintain"}
            if "/check-runs?per_page=100" in url:
                return {"check_runs":[
                    {"name":"validate","status":"completed","conclusion":"success","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/99"},
                    {"name":"python-tests","status":"completed","conclusion":"success","app":{"slug":"github-actions"},"details_url":"https://github.com/o/r/actions/runs/99"},
                ]}
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

    def test_collect_rejects_review_older_than_head_commit(self):
        base=self.fake_request(False)
        def req(url,token,method="GET",payload=None,allow_404=False):
            if "/pulls/7/reviews" in url:
                return [{"user":{"login":"alice"},"state":"APPROVED","commit_id":"a"*40,"submitted_at":"2025-12-31T23:59:59Z"}]
            return base(url,token,method,payload,allow_404)
        with patch.object(collector,"_request",side_effect=req):
            with self.assertRaises(collector.GitHubAttestationCollectionError):
                collector.collect(self.plan(False),token="t",repository="o/r",pull_request=7)

    def test_collect_rejects_draft_pr(self):
        base=self.fake_request(False)
        def req(url,token,method="GET",payload=None,allow_404=False):
            if url.endswith("/pulls/7"):
                value=base(url,token,method,payload,allow_404)
                value["draft"]=True
                return value
            return base(url,token,method,payload,allow_404)
        with patch.object(collector,"_request",side_effect=req):
            with self.assertRaises(collector.GitHubAttestationCollectionError):
                collector.collect(self.plan(False),token="t",repository="o/r",pull_request=7)

    def test_missing_token_is_fail_closed(self):
        with self.assertRaises(collector.GitHubAttestationCollectionError):
            collector.collect(self.plan(),token="",repository="o/r",pull_request=7)

if __name__=="__main__":
    unittest.main()

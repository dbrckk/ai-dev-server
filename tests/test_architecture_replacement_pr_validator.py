import base64
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from architecture_replacement_pr_validator import ReplacementPRValidationError, validate

class ReplacementPRValidatorTests(unittest.TestCase):
    def review(self):
        return {"status":"promotion_review_ready","work_order_id":"replace-1"}

    def package(self):
        import hashlib
        data=b"hello\n"
        return {
            "status":"pr_package_ready",
            "work_order_id":"replace-1",
            "branch":"architecture/replacement-abc",
            "files":[{"path":"lib/a.txt","sha256":hashlib.sha256(data).hexdigest()}],
        }

    def persisted(self):
        return {
            "status":"replacement_pr_created",
            "work_order_id":"replace-1",
            "branch":"architecture/replacement-abc",
            "commit_sha":"1"*40,
            "pull_request":7,
        }

    def requester(self,draft=False,mergeable=True,checks=True,content=b"hello\n"):
        def request(url,token,*args,**kwargs):
            if "/pulls/7/files" in url:
                return [{"filename":"lib/a.txt","status":"modified"}]
            if "/contents/lib/a.txt" in url:
                return {"encoding":"base64","content":base64.b64encode(content).decode()}
            if "/check-runs" in url:
                runs=[]
                if checks:
                    for name in ("validate","python-tests"):
                        runs.append({
                            "name":name,
                            "status":"completed",
                            "conclusion":"success",
                            "app":{"slug":"github-actions"},
                            "details_url":"https://github.com/owner/repo/actions/runs/123/job/1",
                        })
                return {"check_runs":runs}
            if "/pulls/7" in url:
                return {
                    "state":"open",
                    "draft":draft,
                    "base":{"ref":"main"},
                    "head":{"ref":"architecture/replacement-abc","sha":"1"*40},
                    "mergeable":mergeable,
                    "mergeable_state":"clean" if mergeable else "blocked",
                }
            raise AssertionError(url)
        return request

    def test_clean_non_draft_pr_is_ready(self):
        result=validate(
            self.review(),self.package(),self.persisted(),"token","owner/repo",
            requester=self.requester()
        )
        self.assertEqual(result["status"],"ready_to_merge")
        self.assertTrue(result["ready_to_merge"])
        self.assertFalse(result["policy"]["auto_merge"])

    def test_draft_is_validated_but_not_merge_ready(self):
        result=validate(
            self.review(),self.package(),self.persisted(),"token","owner/repo",
            requester=self.requester(draft=True)
        )
        self.assertEqual(result["status"],"validated_draft")
        self.assertFalse(result["ready_to_merge"])

    def test_missing_checks_waits(self):
        result=validate(
            self.review(),self.package(),self.persisted(),"token","owner/repo",
            requester=self.requester(checks=False)
        )
        self.assertEqual(result["status"],"awaiting_required_checks")
        self.assertIn("validate",result["missing_checks"])

    def test_content_change_is_blocked(self):
        with self.assertRaises(ReplacementPRValidationError):
            validate(
                self.review(),self.package(),self.persisted(),"token","owner/repo",
                requester=self.requester(content=b"tampered\n")
            )

if __name__=="__main__":
    unittest.main()

import base64
import hashlib
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from architecture_replacement_merge import ReplacementMergeError, merge

class ReplacementMergeTests(unittest.TestCase):
    def fixtures(self):
        content=b"hello\n"
        review={
            "status":"promotion_review_ready",
            "work_order_id":"replace-1",
        }
        package={
            "status":"pr_package_ready",
            "work_order_id":"replace-1",
            "branch":"architecture/replacement-abc",
            "title":"Replace a/current with a/better",
            "files":[{"path":"lib/a.txt","sha256":hashlib.sha256(content).hexdigest()}],
        }
        persisted={
            "status":"replacement_pr_created",
            "work_order_id":"replace-1",
            "branch":"architecture/replacement-abc",
            "commit_sha":"1"*40,
            "pull_request":7,
        }
        gate={
            "status":"merge_authorization_required",
            "authorization_id":"2"*64,
            "work_order_id":"replace-1",
            "pull_request":7,
            "branch":"architecture/replacement-abc",
            "head_sha":"1"*40,
        }
        authorization={
            "version":1,
            "status":"explicit_merge_authorization",
            "authorization_id":"2"*64,
            "work_order_id":"replace-1",
            "pull_request":7,
            "branch":"architecture/replacement-abc",
            "head_sha":"1"*40,
            "authorized":True,
        }
        return content,review,package,persisted,gate,authorization

    def requester(self,content,merged=True):
        calls={"merge":0}
        def request(url,token,method="GET",payload=None,*args,**kwargs):
            if "/pulls/7/files" in url:
                return [{"filename":"lib/a.txt","status":"modified"}]
            if "/contents/lib/a.txt" in url:
                return {"encoding":"base64","content":base64.b64encode(content).decode()}
            if "/check-runs" in url:
                return {"check_runs":[
                    {
                        "name":name,
                        "status":"completed",
                        "conclusion":"success",
                        "app":{"slug":"github-actions"},
                        "details_url":"https://github.com/owner/repo/actions/runs/123/job/1",
                    }
                    for name in ("validate","python-tests")
                ]}
            if url.endswith("/pulls/7"):
                return {
                    "state":"open",
                    "draft":False,
                    "base":{"ref":"main"},
                    "head":{"ref":"architecture/replacement-abc","sha":"1"*40},
                    "mergeable":True,
                    "mergeable_state":"clean",
                }
            if url.endswith("/pulls/7/merge"):
                calls["merge"]+=1
                return {"merged":merged,"sha":"3"*40}
            raise AssertionError(url)
        request.calls=calls
        return request

    def test_explicit_authorization_allows_single_merge_write(self):
        content,review,package,persisted,gate,authorization=self.fixtures()
        requester=self.requester(content)
        result=merge(
            review,package,persisted,gate,authorization,
            "token","owner/repo",requester=requester
        )
        self.assertEqual(result["status"],"replacement_merged")
        self.assertTrue(result["explicit_authorization_verified"])
        self.assertEqual(requester.calls["merge"],1)

    def test_missing_authorization_blocks_before_merge(self):
        content,review,package,persisted,gate,authorization=self.fixtures()
        authorization["authorized"]=False
        requester=self.requester(content)
        with self.assertRaises(ReplacementMergeError):
            merge(review,package,persisted,gate,authorization,"token","owner/repo",requester=requester)
        self.assertEqual(requester.calls["merge"],0)

if __name__=="__main__":
    unittest.main()

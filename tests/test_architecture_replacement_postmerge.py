import base64
import hashlib
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from architecture_replacement_postmerge import verify

class ReplacementPostMergeTests(unittest.TestCase):
    def fixtures(self):
        content=b"hello\n"
        merged={
            "status":"replacement_merged",
            "work_order_id":"replace-1",
            "pull_request":7,
            "merge_sha":"3"*40,
        }
        package={
            "status":"pr_package_ready",
            "work_order_id":"replace-1",
            "files":[{"path":"lib/a.txt","sha256":hashlib.sha256(content).hexdigest()}],
        }
        return content,merged,package

    def requester(self,content,failed=False,main=True):
        def request(url,token,*args,**kwargs):
            if url.endswith("/branches/main"):
                return {"commit":{"sha":"3"*40 if main else "4"*40}}
            if "/contents/lib/a.txt" in url:
                return {"encoding":"base64","content":base64.b64encode(content).decode()}
            if "/check-runs" in url:
                return {"check_runs":[
                    {
                        "name":name,
                        "status":"completed",
                        "conclusion":"failure" if failed and name=="validate" else "success",
                        "app":{"slug":"github-actions"},
                        "details_url":"https://github.com/owner/repo/actions/runs/123/job/1",
                    }
                    for name in ("validate","python-tests")
                ]}
            raise AssertionError(url)
        return request

    def test_clean_merge_is_healthy(self):
        content,merged,package=self.fixtures()
        result=verify(merged,package,"token","owner/repo",requester=self.requester(content))
        self.assertEqual(result["status"],"post_merge_healthy")
        self.assertTrue(result["post_merge_healthy"])
        self.assertFalse(result["rollback_required"])

    def test_failed_main_check_requires_rollback(self):
        content,merged,package=self.fixtures()
        result=verify(merged,package,"token","owner/repo",requester=self.requester(content,failed=True))
        self.assertEqual(result["status"],"post_merge_regression")
        self.assertTrue(result["rollback_required"])

    def test_main_not_yet_at_merge_waits(self):
        content,merged,package=self.fixtures()
        result=verify(merged,package,"token","owner/repo",requester=self.requester(content,main=False))
        self.assertEqual(result["status"],"awaiting_main_head")
        self.assertFalse(result["rollback_required"])

if __name__=="__main__":
    unittest.main()

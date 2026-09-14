import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
from architecture_replacement_rollback import ReplacementRollbackError, execute

class ReplacementRollbackTests(unittest.TestCase):
    def fixtures(self):
        gate={"status":"rollback_authorization_required","authorization_id":"2"*64,"work_order_id":"r1","merge_sha":"3"*40,"baseline_sha":"0"*40,"reason":{"failed_checks":["validate"]}}
        auth={"status":"explicit_rollback_authorization","authorization_id":"2"*64,"work_order_id":"r1","merge_sha":"3"*40,"authorized":True}
        return gate,auth
    def requester(self):
        calls={"prs":0}
        def request(url,token,method="GET",payload=None,*args,**kwargs):
            if url.endswith("/branches/main"): return {"commit":{"sha":"3"*40}}
            if url.endswith("/git/commits/"+"3"*40): return {"parents":[{"sha":"0"*40},{"sha":"1"*40}],"tree":{"sha":"9"*40}}
            if url.endswith("/git/commits/"+"0"*40): return {"tree":{"sha":"8"*40}}
            if url.endswith("/git/commits") and method=="POST": return {"sha":"4"*40}
            if url.endswith("/git/refs") and method=="POST": return {"ref":payload["ref"]}
            if url.endswith("/pulls") and method=="POST":
                calls["prs"]+=1; return {"number":8}
            raise AssertionError(url)
        request.calls=calls
        return request
    def test_authorized_regression_creates_draft_rollback_pr(self):
        gate,auth=self.fixtures(); requester=self.requester()
        result=execute(gate,auth,"token","owner/repo",requester=requester)
        self.assertEqual(result["status"],"replacement_rollback_pr_created")
        self.assertTrue(result["draft"]); self.assertFalse(result["merged"])
        self.assertEqual(requester.calls["prs"],1)
    def test_main_advance_blocks_rollback_preparation(self):
        gate,auth=self.fixtures()
        def request(url,token,*args,**kwargs):
            if url.endswith("/branches/main"): return {"commit":{"sha":"5"*40}}
            raise AssertionError(url)
        with self.assertRaises(ReplacementRollbackError):
            execute(gate,auth,"token","owner/repo",requester=request)

if __name__=="__main__":
    unittest.main()

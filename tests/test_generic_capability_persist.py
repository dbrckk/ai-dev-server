import unittest
from unittest.mock import patch

from studio.generic_capability_persist import GenericCapabilityPersistError, persist


class FakeGitHub:
    def __init__(self):
        self.repo="/repos/owner/repo"
        self.refs=[]
        self.trees={}
        self.commits={}
        self.pulls=[]
        self.calls=[]
        self.base="1"*40
        self.base_tree="2"*40
        self.commits[self.base]={"tree":{"sha":self.base_tree},"parents":[]}
        self.trees[self.base]=[]

    def get(self,path):
        if path=="/git/commits/"+self.base:
            return self.commits[self.base]
        if path=="/git/trees/"+self.base+"?recursive=1":
            return {"tree":self.trees[self.base],"truncated":False}
        if path.startswith("/git/matching-refs/heads/"):
            prefix="refs/heads/"+path.split("/git/matching-refs/heads/",1)[1]
            return [x for x in self.refs if x["ref"].startswith(prefix)]
        if path.startswith("/git/commits/"):
            return self.commits[path.rsplit("/",1)[-1]]
        if path.startswith("/pulls?"):
            return self.pulls
        raise AssertionError(path)

    def call(self,method,path,payload=None):
        self.calls.append((method,path,payload))
        if path.endswith("/git/trees"):
            sha="3"*40
            self.trees[sha]=payload["tree"]
            return {"sha":sha}
        if path.endswith("/git/commits"):
            sha="4"*40
            self.commits[sha]={"tree":{"sha":payload["tree"]},"parents":[{"sha":x} for x in payload["parents"]]}
            return {"sha":sha}
        if path.endswith("/git/refs"):
            self.refs.append({"ref":payload["ref"],"object":{"sha":payload["sha"]}})
            return {}
        if path.endswith("/pulls"):
            pr={"number":7,"head":{"ref":payload["head"],"sha":"4"*40}}
            self.pulls.append(pr)
            return pr
        raise AssertionError((method,path,payload))


def candidate():
    return {
        "candidate_id":"capability-candidate:image_assets:abc",
        "candidate_sha256":"a"*64,
        "candidate":{
            "capability":"image_assets",
            "provider":"studio.capabilities.image_assets",
            "implementation":"def run(payload):\n    return {'ok': True}\n",
            "tests":"import unittest\nclass T(unittest.TestCase):\n    def test_ok(self): self.assertTrue(True)\n",
        },
    }


def validation():
    return {
        "candidate_id":"capability-candidate:image_assets:abc",
        "candidate_sha256":"a"*64,
        "report_sha256":"b"*64,
        "validation":{"status":"candidate_validated"},
    }


def handoff():
    return {
        "status":"promotion_required",
        "candidate_id":"capability-candidate:image_assets:abc",
        "candidate_sha256":"a"*64,
        "capability":"image_assets",
        "provider":"studio.capabilities.image_assets",
        "baseline_sha":"1"*40,
        "handoff_sha256":"c"*64,
        "candidate_materialized_in_trusted_repo":False,
        "capability_registered":False,
    }


class GenericCapabilityPersistTests(unittest.TestCase):
    @patch("studio.generic_capability_persist.validate_candidate_envelope",side_effect=lambda x:x)
    @patch("studio.generic_capability_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_persists_only_candidate_provider_test_and_evidence(self,_validation,_candidate):
        gh=FakeGitHub()
        result=persist(gh,candidate(),validation(),handoff(),"1"*40)
        self.assertEqual(result["status"],"candidate_persisted")
        tree_call=next(x for x in gh.calls if x[1].endswith("/git/trees"))
        paths={x["path"] for x in tree_call[2]["tree"]}
        self.assertEqual(len(paths),3)
        self.assertIn("studio/capabilities/image_assets.py",paths)
        self.assertTrue(any(x.startswith("tests/test_candidate_image_assets_") for x in paths))
        self.assertTrue(any(x.startswith("control/capability_candidates/") for x in paths))
        self.assertNotIn("control/promoted_capabilities.json",paths)

    @patch("studio.generic_capability_persist.validate_candidate_envelope",side_effect=lambda x:x)
    @patch("studio.generic_capability_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_cross_candidate_validation_fails_closed(self,_validation,_candidate):
        gh=FakeGitHub(); bad=validation(); bad["candidate_id"]="other"
        with self.assertRaisesRegex(GenericCapabilityPersistError,"validation candidate mismatch"):
            persist(gh,candidate(),bad,handoff(),"1"*40)
        self.assertFalse(gh.calls)

    @patch("studio.generic_capability_persist.validate_candidate_envelope",side_effect=lambda x:x)
    @patch("studio.generic_capability_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_existing_target_path_fails_closed(self,_validation,_candidate):
        gh=FakeGitHub()
        gh.trees[gh.base]=[{"path":"studio/capabilities/image_assets.py","type":"blob"}]
        with self.assertRaisesRegex(GenericCapabilityPersistError,"target path already exists"):
            persist(gh,candidate(),validation(),handoff(),"1"*40)

    @patch("studio.generic_capability_persist.validate_candidate_envelope",side_effect=lambda x:x)
    @patch("studio.generic_capability_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_existing_branch_must_match_content_and_parent(self,_validation,_candidate):
        gh=FakeGitHub()
        prefix="capability/candidate-image_assets-"
        gh.refs=[{"ref":"refs/heads/"+prefix+"4"*40,"object":{"sha":"4"*40}}]
        gh.commits["4"*40]={"tree":{"sha":"f"*40},"parents":[{"sha":"1"*40}]}
        with self.assertRaisesRegex(GenericCapabilityPersistError,"content changed"):
            persist(gh,candidate(),validation(),handoff(),"1"*40)


if __name__=="__main__":
    unittest.main()

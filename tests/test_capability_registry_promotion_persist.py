import base64
import json
import unittest
from unittest.mock import patch

from studio.capability_registry_promotion_persist import (
    CapabilityRegistryPromotionPersistError,
    persist,
)


class FakeGitHub:
    def __init__(self):
        self.repo="/repos/owner/repo"
        self.main="9"*40
        self.main_tree="8"*40
        self.candidate_commit="7"*40
        self.baseline="6"*40
        self.provider_sha="5"*40
        self.registry_sha="4"*40
        self.refs=[]
        self.pulls=[]
        self.calls=[]

    def get(self,path):
        if path=="/git/commits/"+self.candidate_commit:
            return {"tree":{"sha":"3"*40},"parents":[{"sha":self.baseline}]}
        if path=="/git/commits/"+self.main:
            return {"tree":{"sha":self.main_tree},"parents":[]}
        if path=="/git/trees/"+self.main_tree+"?recursive=1":
            return {"truncated":False,"tree":[
                {"path":"studio/capabilities/image_assets.py","type":"blob","sha":self.provider_sha},
                {"path":"control/promoted_capabilities.json","type":"blob","sha":self.registry_sha},
            ]}
        if path=="/git/blobs/"+self.provider_sha:
            return {"encoding":"base64","content":base64.b64encode(b"def provide(): pass").decode()}
        if path=="/git/blobs/"+self.registry_sha:
            raw=json.dumps({"version":1,"capabilities":{}}).encode()
            return {"encoding":"base64","content":base64.b64encode(raw).decode()}
        if path.startswith("/git/matching-refs/heads/"):
            prefix="refs/heads/"+path.split("/git/matching-refs/heads/",1)[1]
            return [x for x in self.refs if x["ref"].startswith(prefix)]
        if path.startswith("/git/commits/"):
            sha=path.rsplit("/",1)[-1]
            if sha=="2"*40:
                return {"tree":{"sha":"1"*40},"parents":[{"sha":self.main}]}
        if path.startswith("/pulls?"):
            return self.pulls
        raise AssertionError(path)

    def call(self,method,path,payload=None):
        self.calls.append((method,path,payload))
        if path.endswith("/git/trees"):
            return {"sha":"1"*40}
        if path.endswith("/git/commits"):
            return {"sha":"2"*40}
        if path.endswith("/git/refs"):
            self.refs.append({"ref":payload["ref"],"object":{"sha":payload["sha"]}})
            return {}
        if path.endswith("/pulls"):
            pr={"number":23,"head":{"ref":payload["head"],"sha":"2"*40}}
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
            "implementation":"def provide(): pass",
        },
    }


def validation_report():
    return {
        "candidate_id":"capability-candidate:image_assets:abc",
        "candidate_sha256":"a"*64,
        "validation":{
            "status":"candidate_validated",
            "candidate_id":"capability-candidate:image_assets:abc",
            "candidate_sha256":"a"*64,
            "capability":"image_assets",
            "provider":"studio.capabilities.image_assets",
            "promotion_status":"eligible",
            "capability_registered":False,
            "evidence":{
                "targeted_test_sha256":"b"*64,
                "benchmark_sha256":"c"*64,
                "regression_sha256":"d"*64,
            },
        },
    }


def review(gh):
    return {
        "status":"candidate_persisted",
        "candidate_id":"capability-candidate:image_assets:abc",
        "candidate_sha256":"a"*64,
        "capability":"image_assets",
        "branch":"capability/candidate-image_assets-x-"+gh.candidate_commit,
        "commit_sha":gh.candidate_commit,
        "pull_request":17,
    }


def merged():
    return {"status":"candidate_merged","merge_commit_sha":"e"*40,"pull_request":17}


class RegistryPromotionPersistTests(unittest.TestCase):
    @patch("studio.capability_registry_promotion_persist.validate_candidate_envelope",side_effect=lambda x:x)
    @patch("studio.capability_registry_promotion_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_registry_only_pr_is_created_after_verified_merge(self,_vr,_vc):
        gh=FakeGitHub()
        result=persist(gh,candidate(),validation_report(),review(gh),merged(),gh.main)
        self.assertEqual(result["status"],"registry_promotion_persisted")
        tree_call=next(x for x in gh.calls if x[1].endswith("/git/trees"))
        paths=[x["path"] for x in tree_call[2]["tree"]]
        self.assertEqual(paths,["control/promoted_capabilities.json"])
        self.assertFalse(result["capability_registered"])
        self.assertEqual(result["pull_request"],23)

    @patch("studio.capability_registry_promotion_persist.validate_candidate_envelope",side_effect=lambda x:x)
    @patch("studio.capability_registry_promotion_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_provider_content_mismatch_fails_closed(self,_vr,_vc):
        gh=FakeGitHub()
        original=gh.get
        def bad(path):
            if path=="/git/blobs/"+gh.provider_sha:
                return {"encoding":"base64","content":base64.b64encode(b"tampered").decode()}
            return original(path)
        gh.get=bad
        with self.assertRaisesRegex(CapabilityRegistryPromotionPersistError,"content mismatch"):
            persist(gh,candidate(),validation_report(),review(gh),merged(),gh.main)
        self.assertFalse(gh.calls)

    @patch("studio.capability_registry_promotion_persist.validate_candidate_envelope",side_effect=lambda x:x)
    @patch("studio.capability_registry_promotion_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_unmerged_candidate_cannot_prepare_registry_pr(self,_vr,_vc):
        gh=FakeGitHub()
        with self.assertRaisesRegex(CapabilityRegistryPromotionPersistError,"merge proof"):
            persist(
                gh,candidate(),validation_report(),review(gh),
                {"status":"candidate_review_pending","pull_request":17},
                gh.main,
            )
        self.assertFalse(gh.calls)

    @patch("studio.capability_registry_promotion_persist.validate_candidate_envelope",side_effect=lambda x:x)
    @patch("studio.capability_registry_promotion_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_review_identity_mismatch_fails_closed(self,_vr,_vc):
        gh=FakeGitHub(); r=review(gh); r["candidate_id"]="other"
        with self.assertRaisesRegex(CapabilityRegistryPromotionPersistError,"review identity mismatch"):
            persist(gh,candidate(),validation_report(),r,merged(),gh.main)


if __name__=="__main__":
    unittest.main()

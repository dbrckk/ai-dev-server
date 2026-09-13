import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import zipfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError
from play_stage import advance, detect_package_name

REQ={
    "id":"demo-v1",
    "target_repo":"owner/app",
    "app_name":"demo_app",
    "brief":"Build a complete polished mobile application.",
    "enabled":True,
    "max_rounds":2,
    "max_calls":8,
    "max_cycles":3,
    "play_publish":{"enabled":True,"track":"internal","commit":False},
}


def valid_aab(path: Path):
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("BundleConfig.pb",b"cfg")
        z.writestr("base/manifest/AndroidManifest.xml",b"manifest")


def base_state():
    return {
        "status":"validated_preview",
        "validation_contract":2,
        "code_review":{"passed":True},
        "visual_review":{"passed":True},
        "apk_sha256":"a"*64,
        "checkpoint_commit":"b"*40,
        "publication_request":{"enabled":True,"track":"internal","commit":False},
        "release_evidence":{
            "release_build":{"passed":True},
            "real_device":{"passed":True},
            "capability_qa":{"passed":True,"required_qa_stages":[]},
            "store_metadata":{"passed":True},
            "artwork_qa":{"passed":True},
            "privacy_policy":{"passed":True},
            "security_scan":{"passed":True},
        },
    }


class FakeGitHub:
    def __init__(self,*a,**k): pass
    def publish(self,*a,**k): return "c"*40


class PlayStageTests(unittest.TestCase):
    def test_detects_gradle_kts_application_id(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            p=root/"android/app/build.gradle.kts"
            p.parent.mkdir(parents=True)
            p.write_text('android { defaultConfig { applicationId = "com.example.demo" } }')
            self.assertEqual(detect_package_name(root),"com.example.demo")

    @patch("play_stage.GitHub",FakeGitHub)
    def test_validate_only_completes_without_commit(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/"out"; work=root/"work"; out.mkdir(); work.mkdir()
            req_path=root/"request.json"; req_path.write_text(json.dumps(REQ))
            gradle=work/"android/app/build.gradle.kts"; gradle.parent.mkdir(parents=True)
            gradle.write_text('android { defaultConfig { applicationId = "com.example.demo" } }')
            artifact=out/"app-release.aab"; valid_aab(artifact)
            state=base_state()
            digest=hashlib.sha256(artifact.read_bytes()).hexdigest()
            state["release_evidence"]["release_build"]["production_signing"]={
                "passed":True,"signed_aab_sha256":digest,"certificate_sha256":"d"*64
            }
            (out/"report.json").write_text(json.dumps(state))
            seen={}
            def publisher(**kwargs):
                seen.update(kwargs)
                return {"passed":True,"edit_validated":True,"committed":False,
                        "package_name":kwargs["package_name"],"track":kwargs["track"],"version_code":7}
            result=advance(req_path,work,out,env={"STUDIO_PLAY_ACCESS_TOKEN":"x"*40},publisher=publisher)
            self.assertEqual(result["status"],"finished")
            self.assertTrue(result["completion"]["finished"])
            self.assertFalse(result["release_evidence"]["play_publish"]["committed"])
            self.assertFalse(seen["commit"])

    @patch("play_stage.GitHub",FakeGitHub)
    def test_missing_play_token_becomes_human_action(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/"out"; work=root/"work"; out.mkdir(); work.mkdir()
            req_path=root/"request.json"; req_path.write_text(json.dumps(REQ))
            gradle=work/"android/app/build.gradle.kts"; gradle.parent.mkdir(parents=True)
            gradle.write_text('android { defaultConfig { applicationId = "com.example.demo" } }')
            artifact=out/"app-release.aab"; valid_aab(artifact)
            state=base_state(); digest=hashlib.sha256(artifact.read_bytes()).hexdigest()
            state["release_evidence"]["release_build"]["production_signing"]={
                "passed":True,"signed_aab_sha256":digest,"certificate_sha256":"d"*64
            }
            (out/"report.json").write_text(json.dumps(state))
            result=advance(req_path,work,out,env={},publisher=lambda **k: self.fail("network"))
            self.assertEqual(result["status"],"human_action_required")
            self.assertEqual(result["human_action"]["action"],"play_access_token_required")
            self.assertFalse(result["completion"]["finished"])

    @patch("play_stage.GitHub",FakeGitHub)
    def test_commit_requires_trusted_approval(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/"out"; work=root/"work"; out.mkdir(); work.mkdir()
            req=dict(REQ); req["play_publish"]={"enabled":True,"track":"internal","commit":True}
            req_path=root/"request.json"; req_path.write_text(json.dumps(req))
            gradle=work/"android/app/build.gradle.kts"; gradle.parent.mkdir(parents=True)
            gradle.write_text('android { defaultConfig { applicationId = "com.example.demo" } }')
            artifact=out/"app-release.aab"; valid_aab(artifact)
            state=base_state(); state["publication_request"]=dict(req["play_publish"])
            digest=hashlib.sha256(artifact.read_bytes()).hexdigest()
            state["release_evidence"]["release_build"]["production_signing"]={
                "passed":True,"signed_aab_sha256":digest,"certificate_sha256":"d"*64
            }
            (out/"report.json").write_text(json.dumps(state))
            result=advance(req_path,work,out,env={"STUDIO_PLAY_ACCESS_TOKEN":"x"*40},publisher=lambda **k:self.fail("network"))
            self.assertEqual(result["status"],"human_action_required")
            self.assertEqual(result["human_action"]["action"],"play_commit_approval_required")


if __name__=="__main__":
    unittest.main()

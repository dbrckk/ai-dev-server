import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import zipfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from godot_play_stage import execute

REQ={
    "id":"demo-v1","target_repo":"owner/app","app_name":"demo_app",
    "brief":"Build a complete polished mobile application.","enabled":True,
    "max_rounds":2,"max_calls":8,"max_cycles":3,
    "play_publish":{"enabled":True,"track":"internal","commit":False},
}
STATE={
    "engine":"godot",
    "status":"godot_technical_store_ready",
    "release_status":"technical_store_ready",
    "completion":{"finished":False,"next_stage":"godot_play_submission"},
    "coverage":{"final_review":True},
    "release_artifact":{
        "aab_sha256":"PLACEHOLDER",
        "certificate_sha256":"c"*64,
        "package":"com.example.demo",
    },
}

class FakeGitHub: pass

def make_aab(path:Path):
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("BundleConfig.pb",b"cfg")
        z.writestr("base/manifest/AndroidManifest.xml",b"manifest")

class GodotPlayStageTests(unittest.TestCase):
    @patch("godot_play_stage._publish",return_value="d"*40)
    @patch("godot_play_stage._restore")
    def test_validate_only_finishes_requested_pipeline(self,restore,publish):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); work=root/"work"; out=root/"out"; out.mkdir()
            artifact=out/"app-release.aab"; make_aab(artifact)
            state=dict(STATE); state["release_artifact"]=dict(STATE["release_artifact"])
            state["release_artifact"]["aab_sha256"]=hashlib.sha256(artifact.read_bytes()).hexdigest()
            restore.return_value=(state,"a"*40,True)
            seen={}
            def publisher(**kwargs):
                seen.update(kwargs)
                return {"passed":True,"edit_validated":True,"committed":False,
                        "package_name":kwargs["package_name"],"track":kwargs["track"],"version_code":7}
            result=execute(REQ,work,out,FakeGitHub(),env={"STUDIO_PLAY_ACCESS_TOKEN":"x"*40},publisher=publisher)
        self.assertEqual(result["status"],"godot_play_validated")
        self.assertTrue(result["completion"]["finished"])
        self.assertTrue(result["coverage"]["play_publish"])
        self.assertFalse(seen["commit"])

    @patch("godot_play_stage._publish",return_value="d"*40)
    @patch("godot_play_stage._restore")
    def test_missing_token_is_human_action(self,restore,publish):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); work=root/"work"; out=root/"out"; out.mkdir()
            artifact=out/"app-release.aab"; make_aab(artifact)
            state=dict(STATE); state["release_artifact"]=dict(STATE["release_artifact"])
            state["release_artifact"]["aab_sha256"]=hashlib.sha256(artifact.read_bytes()).hexdigest()
            restore.return_value=(state,"a"*40,True)
            result=execute(REQ,work,out,FakeGitHub(),env={},publisher=lambda **k:self.fail("network"))
        self.assertEqual(result["status"],"human_action_required")
        self.assertEqual(result["human_action"]["action"],"play_access_token_required")
        self.assertFalse(result["completion"]["finished"])

    @patch("godot_play_stage._publish",return_value="d"*40)
    @patch("godot_play_stage._restore")
    def test_missing_exact_artifact_is_human_action(self,restore,publish):
        state=dict(STATE); state["release_artifact"]=dict(STATE["release_artifact"])
        state["release_artifact"]["aab_sha256"]="a"*64
        restore.return_value=(state,"a"*40,True)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            result=execute(REQ,root/"work",root/"out",FakeGitHub(),env={"STUDIO_PLAY_ACCESS_TOKEN":"x"*40})
        self.assertEqual(result["status"],"human_action_required")
        self.assertEqual(result["human_action"]["action"],"signed_aab_artifact_required")


if __name__=="__main__":
    unittest.main()

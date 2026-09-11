import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from studio.artwork_stage import advance
from studio.store_package import _brand_image, encode_rgba


class FakeGitHub:
    def __init__(self,*args,**kwargs):
        self.published=[]
    def publish(self,branch,parent,root,state):
        self.published.append((branch,parent,state))
        return "b"*40


class ArtworkStageTests(unittest.TestCase):
    def state(self):
        return {
            "status":"validated_preview",
            "validation_contract":2,
            "code_review":{"passed":True},
            "visual_review":{"passed":True},
            "apk_sha256":"abc",
            "checkpoint_commit":"a"*40,
            "design":{"primary":"#102030","accent":"#5060F6"},
            "release_evidence":{
                "release_build":{"passed":True},
                "real_device":{"passed":True},
                "capability_qa":{"passed":True,"required_qa_stages":[]},
                "store_metadata":{"passed":True},
            },
        }

    def request(self,path):
        path.write_text(json.dumps({
            "id":"demo",
            "target_repo":"owner/demo",
            "app_name":"demo",
            "brief":"Demo app.",
            "enabled":True,
        }))

    def test_valid_artwork_advances_to_privacy(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/"out"; work=root/"work"
            out.mkdir(); work.mkdir()
            req=root/"request.json"; self.request(req)
            (out/"report.json").write_text(json.dumps(self.state()))
            store=out/"play-store"; store.mkdir()
            (store/"icon-512.png").write_bytes(_brand_image(512,512,{"primary":"#102030","accent":"#5060F6"},False))
            (store/"feature-graphic-1024x500.png").write_bytes(_brand_image(1024,500,{"primary":"#102030","accent":"#5060F6"},True))
            with patch("studio.artwork_stage.GitHub",FakeGitHub):
                state=advance(req,work,out)
            self.assertTrue(state["release_evidence"]["artwork_qa"]["passed"])
            self.assertEqual(state["completion"]["next_stage"],"privacy_policy")
            self.assertEqual(state["checkpoint_commit"],"b"*40)

    def test_flat_artwork_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/"out"; work=root/"work"
            out.mkdir(); work.mkdir()
            req=root/"request.json"; self.request(req)
            (out/"report.json").write_text(json.dumps(self.state()))
            store=out/"play-store"; store.mkdir()
            (store/"icon-512.png").write_bytes(encode_rgba(512,512,b"\x10\x10\x10\xff"*(512*512)))
            (store/"feature-graphic-1024x500.png").write_bytes(encode_rgba(1024,500,b"\x10\x10\x10\xff"*(1024*500)))
            with patch("studio.artwork_stage.GitHub",FakeGitHub):
                state=advance(req,work,out)
            self.assertFalse(state["release_evidence"]["artwork_qa"]["passed"])
            self.assertEqual(state["completion"]["next_stage"],"artwork_qa")


if __name__=="__main__":
    unittest.main()

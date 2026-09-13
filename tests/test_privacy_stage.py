import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from privacy_stage import advance


REQ={
    "id":"demo-v1",
    "target_repo":"owner/app",
    "app_name":"demo_app",
    "brief":"Build a complete polished mobile application.",
    "enabled":True,
}


def state_before_privacy():
    return {
        "status":"validated_preview",
        "validation_contract":2,
        "code_review":{"passed":True},
        "visual_review":{"passed":True},
        "apk_sha256":"a"*64,
        "checkpoint_commit":"b"*40,
        "release_evidence":{
            "release_build":{"passed":True},
            "real_device":{"passed":True},
            "capability_qa":{"passed":True,"required_qa_stages":[]},
            "store_metadata":{"passed":True},
            "artwork_qa":{"passed":True},
        },
    }


class FakeGitHub:
    def __init__(self,*a,**k): pass
    def publish(self,*a,**k): return "c"*40


class PrivacyStageTests(unittest.TestCase):
    @patch("privacy_stage.GitHub",FakeGitHub)
    @patch("privacy_stage.build_privacy_package")
    def test_unresolved_data_safety_becomes_human_action(self,build):
        build.return_value={
            "passed":False,
            "data_safety":{"status":"needs_verified_classification"},
            "audit":{
                "potential_data_classes":["app_activity","device_or_other_ids"],
                "capability_names":["analytics"],
            },
            "blockers":["third_party_analytics_requires_verified_data_flow_classification"],
        }
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/"out"; out.mkdir()
            req=root/"request.json"; req.write_text(json.dumps(REQ))
            (out/"report.json").write_text(json.dumps(state_before_privacy()))
            result=advance(req,root/"work",out)
        self.assertEqual(result["status"],"human_action_required")
        self.assertEqual(
            result["human_action"]["action"],
            "data_safety_legal_attestation_required",
        )
        self.assertEqual(result["human_action"]["detected_capabilities"],["analytics"])
        self.assertEqual(result["completion"]["next_stage"],"privacy_policy")
        self.assertFalse(result["completion"]["finished"])

    @patch("privacy_stage.GitHub",FakeGitHub)
    @patch("privacy_stage.build_privacy_package")
    def test_derived_privacy_evidence_advances_to_security(self,build):
        build.return_value={
            "passed":True,
            "data_safety":{"status":"derived"},
            "audit":{"potential_data_classes":[],"capability_names":[]},
            "blockers":[],
        }
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/"out"; out.mkdir()
            req=root/"request.json"; req.write_text(json.dumps(REQ))
            (out/"report.json").write_text(json.dumps(state_before_privacy()))
            result=advance(req,root/"work",out)
        self.assertNotEqual(result["status"],"human_action_required")
        self.assertEqual(result["completion"]["next_stage"],"security_scan")


if __name__=="__main__":
    unittest.main()

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from security_audit import human_review_reasons
from security_stage import advance


REQ = {
    "id": "demo-v1",
    "target_repo": "owner/app",
    "app_name": "demo_app",
    "brief": "Build a complete polished mobile application.",
    "enabled": True,
}


def state_before_security():
    return {
        "status": "validated_preview",
        "validation_contract": 2,
        "code_review": {"passed": True},
        "visual_review": {"passed": True},
        "apk_sha256": "a" * 64,
        "checkpoint_commit": "b" * 40,
        "release_evidence": {
            "release_build": {"passed": True},
            "real_device": {"passed": True},
            "capability_qa": {"passed": True, "required_qa_stages": []},
            "store_metadata": {"passed": True},
            "artwork_qa": {"passed": True},
            "privacy_policy": {"passed": True},
        },
    }


class FakeGitHub:
    def __init__(self, *a, **k):
        pass

    def publish(self, *a, **k):
        return "c" * 40


class SecurityStageTests(unittest.TestCase):
    def test_human_review_classifier_only_selects_trust_decisions(self):
        blockers = [
            "credential_material_detected",
            "cleartext_network_traffic_detected",
            "dangerous_android_permissions_require_explicit_review",
            "strong_copyleft_dependency_requires_review:foo",
            "dependency_license_unresolved:bar",
            "unreviewed_hosted_registry:baz",
            "unreviewed_git_or_path_dependency",
        ]
        self.assertEqual(
            human_review_reasons(blockers),
            [
                "dangerous_android_permissions_require_explicit_review",
                "dependency_license_unresolved:bar",
                "strong_copyleft_dependency_requires_review:foo",
                "unreviewed_git_or_path_dependency",
                "unreviewed_hosted_registry:baz",
            ],
        )

    @patch("security_stage.GitHub", FakeGitHub)
    @patch("security_stage.build_security_package")
    def test_security_trust_decision_becomes_human_action(self, build):
        build.return_value = {
            "passed": False,
            "human_review_required": True,
            "human_review_reasons": [
                "dangerous_android_permissions_require_explicit_review"
            ],
            "dangerous_permissions": ["android.permission.READ_SMS"],
            "blockers": [
                "dangerous_android_permissions_require_explicit_review"
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            out.mkdir()
            req = root / "request.json"
            req.write_text(json.dumps(REQ))
            (out / "report.json").write_text(json.dumps(state_before_security()))
            result = advance(req, root / "work", out)

        self.assertEqual(result["status"], "human_action_required")
        self.assertEqual(
            result["human_action"]["action"],
            "security_trust_review_required",
        )
        self.assertEqual(
            result["human_action"]["dangerous_permissions"],
            ["android.permission.READ_SMS"],
        )
        self.assertEqual(result["completion"]["next_stage"], "security_scan")
        self.assertFalse(result["completion"]["finished"])

    @patch("security_stage.GitHub", FakeGitHub)
    @patch("security_stage.build_security_package")
    def test_auto_fixable_security_failure_stays_machine_blocked(self, build):
        build.return_value = {
            "passed": False,
            "human_review_required": False,
            "human_review_reasons": [],
            "dangerous_permissions": [],
            "blockers": ["cleartext_network_traffic_detected"],
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            out.mkdir()
            req = root / "request.json"
            req.write_text(json.dumps(REQ))
            (out / "report.json").write_text(json.dumps(state_before_security()))
            result = advance(req, root / "work", out)

        self.assertNotEqual(result["status"], "human_action_required")
        self.assertEqual(result["completion"]["next_stage"], "security_scan")
        self.assertFalse(result["completion"]["finished"])

    @patch("security_stage.GitHub", FakeGitHub)
    @patch("security_stage.build_security_package")
    def test_resolved_human_action_clears_gate_and_finishes(self, build):
        build.return_value = {
            "passed": True,
            "human_review_required": False,
            "human_review_reasons": [],
            "dangerous_permissions": [],
            "blockers": [],
        }
        state = state_before_security()
        state["status"] = "human_action_required"
        state["human_action"] = {
            "action": "security_trust_review_required",
            "reasons": ["dangerous_android_permissions_require_explicit_review"],
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            out.mkdir()
            req = root / "request.json"
            req.write_text(json.dumps(REQ))
            (out / "report.json").write_text(json.dumps(state))
            result = advance(req, root / "work", out)

        self.assertNotIn("human_action", result)
        self.assertEqual(result["status"], "finished")
        self.assertTrue(result["completion"]["finished"])
        self.assertIsNone(result["completion"]["next_stage"])


    @patch("security_stage.GitHub", FakeGitHub)
    @patch("security_stage.remediate")
    @patch("security_stage.build_security_package")
    def test_auto_remediation_rescans_until_converged(self, build, remediate_fn):
        build.side_effect = [
            {
                "passed": False,
                "human_review_required": False,
                "human_review_reasons": [],
                "dangerous_permissions": [],
                "blockers": ["release_manifest_debuggable"],
            },
            {
                "passed": True,
                "human_review_required": False,
                "human_review_reasons": [],
                "dangerous_permissions": [],
                "blockers": [],
            },
        ]
        remediate_fn.return_value = {
            "changed": True,
            "actions": [
                {
                    "action": "remove_release_debuggable_true",
                    "path": "android/app/src/main/AndroidManifest.xml",
                    "changes": 1,
                }
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            out.mkdir()
            req = root / "request.json"
            req.write_text(json.dumps(REQ))
            (out / "report.json").write_text(json.dumps(state_before_security()))
            result = advance(req, root / "work", out)

        evidence = result["release_evidence"]["security_scan"]
        self.assertEqual(build.call_count, 2)
        remediate_fn.assert_called_once()
        self.assertFalse(evidence["passed"])
        self.assertTrue(evidence["source_repaired"])
        self.assertTrue(evidence["post_repair_scan"]["passed"])
        self.assertTrue(evidence["auto_remediation"]["attempted"])
        self.assertTrue(evidence["auto_remediation"]["converged"])
        self.assertEqual(result["completion"]["next_stage"], "release_build")
        self.assertFalse(result["completion"]["finished"])



if __name__ == "__main__":
    unittest.main()

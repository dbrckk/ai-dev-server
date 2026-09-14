import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from release_stage_engine import apply_external_gate, evaluate_and_repair, invalidate_for_source_change


class ReleaseStageEngineTests(unittest.TestCase):
    def test_environment_failure_is_not_sent_to_repair_agent(self):
        calls = []

        def validator(root, out):
            calls.append(1)
            return {"passed": False, "blockers": ["adb_unavailable"]}

        with patch("release_stage_engine.repair_attempt") as repair:
            evidence = evaluate_and_repair(
                Path("."), Path("."), {}, {"app_name": "demo_app"},
                "performance_qa", validator,
            )

        repair.assert_not_called()
        self.assertEqual(len(calls), 1)
        self.assertEqual(evidence["diagnostics"]["environment"], ["adb_unavailable"])
        self.assertFalse(evidence["agentic_remediation"]["attempted"])

    def test_transient_environment_failure_retries_without_model(self):
        responses = iter([
            {"passed": False, "blockers": ["emulator_boot_timeout"]},
            {"passed": True, "blockers": []},
        ])

        def validator(root, out):
            return next(responses)

        with patch("release_stage_engine.repair_attempt") as repair:
            evidence = evaluate_and_repair(
                Path("."), Path("."), {}, {"app_name": "demo_app"},
                "native_qa", validator,
            )

        repair.assert_not_called()
        self.assertTrue(evidence["passed"])
        self.assertTrue(evidence["environment_retry"]["attempted"])
        self.assertTrue(evidence["environment_retry"]["converged"])


    def test_code_failure_repairs_then_requires_fresh_release_artifact(self):
        calls = []

        def validator(root, out):
            calls.append(1)
            return {"passed": False, "blockers": ["excessive_jank"]}

        with patch("release_stage_engine.repair_attempt") as repair:
            repair.return_value = {
                "changed": True,
                "blockers": ["excessive_jank"],
                "model_calls": 1,
                "models_used": {"release_fix": "fake"},
                "providers_used": {"release_fix": "fake"},
                "gate_count": 5,
            }
            evidence = evaluate_and_repair(
                Path("."), Path("."), {}, {"app_name": "demo_app"},
                "performance_qa", validator,
            )

        repair.assert_called_once()
        self.assertEqual(len(calls), 1)
        self.assertFalse(evidence["passed"])
        self.assertTrue(evidence["source_repaired"])
        self.assertEqual(
            evidence["blockers"],
            ["release_artifact_rebuild_required"],
        )
        self.assertFalse(evidence["agentic_remediation"]["converged"])

    def test_source_change_invalidates_all_old_release_evidence(self):
        state = {
            "release_evidence": {
                "release_build": {"passed": True},
                "real_device": {"passed": True},
                "performance_qa": {"passed": False},
                "privacy_policy": {"passed": True},
            },
            "release_status": "not_store_ready",
        }
        changed = invalidate_for_source_change(
            state,
            {"source_repaired": True},
        )
        self.assertTrue(changed)
        self.assertEqual(state["release_evidence"], {})


    def test_external_evidence_becomes_human_action(self):
        state = {"status": "validated_preview", "release_status": "not_store_ready"}
        evidence = {
            "passed": False,
            "blockers": ["play_billing_sandbox_purchase_not_verified"],
            "diagnostics": {
                "human_or_external": [
                    "play_billing_sandbox_purchase_not_verified"
                ]
            },
        }
        changed = apply_external_gate(state, "billing_qa", evidence)
        self.assertTrue(changed)
        self.assertEqual(state["status"], "human_action_required")
        self.assertEqual(
            state["human_action"]["action"],
            "release_external_evidence_required",
        )


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from task_scheduler import candidates, dispatch, pipeline_stage_for_task, select


def state_with_budget():
    return {
        "status": "validated_preview",
        "validation_contract": 2,
        "project_budget": {
            "model_call_limit": 20,
            "model_calls_spent": 0,
            "repair_call_limit": 10,
            "repair_calls_spent": 0,
        },
        "release_evidence": {
            "release_build": {"passed": True},
            "real_device": {"passed": True},
            "capability_qa": {
                "passed": True,
                "required_qa_stages": ["performance_qa"],
            },
        },
        "repair_queue": [],
    }


class TaskSchedulerTests(unittest.TestCase):
    def test_selects_highest_scoring_runnable_task(self):
        state = state_with_budget()
        state["repair_queue"] = [
            {
                "id": "low",
                "stage": "performance_qa",
                "action": "retry_environment",
                "blockers": ["emulator_boot_timeout"],
                "status": "pending",
                "attempts": 0,
                "max_attempts": 4,
                "dependencies": [],
                "estimated_model_calls": 0,
                "priority": 60,
            },
            {
                "id": "high",
                "stage": "performance_qa",
                "action": "repair_code",
                "blockers": ["excessive_jank"],
                "status": "pending",
                "attempts": 0,
                "max_attempts": 4,
                "dependencies": [],
                "estimated_model_calls": 1,
                "priority": 80,
            },
        ]
        self.assertEqual(select(state)["id"], "high")
        self.assertEqual(dispatch(state)["task_id"], "high")

    def test_human_task_is_not_auto_dispatched(self):
        state = state_with_budget()
        state["repair_queue"] = [
            {
                "id": "human",
                "stage": "billing_qa",
                "action": "human_action",
                "blockers": ["play_billing_sandbox_purchase_not_verified"],
                "status": "pending",
                "attempts": 0,
                "max_attempts": 4,
                "dependencies": [],
                "estimated_model_calls": 0,
                "priority": 100,
            }
        ]
        self.assertEqual(candidates(state), [])
        self.assertIsNone(select(state))

    def test_budget_infeasible_repair_is_not_dispatched(self):
        state = state_with_budget()
        state["project_budget"]["repair_calls_spent"] = 10
        state["repair_queue"] = [
            {
                "id": "repair",
                "stage": "performance_qa",
                "action": "repair_code",
                "blockers": ["excessive_jank"],
                "status": "pending",
                "attempts": 0,
                "max_attempts": 4,
                "dependencies": [],
                "estimated_model_calls": 1,
                "priority": 80,
            }
        ]
        self.assertIsNone(select(state))

    def test_unmet_dependency_blocks_task(self):
        state = state_with_budget()
        state["repair_queue"] = [
            {
                "id": "repair",
                "stage": "performance_qa",
                "action": "repair_code",
                "blockers": ["excessive_jank"],
                "status": "pending",
                "attempts": 0,
                "max_attempts": 4,
                "dependencies": ["missing"],
                "estimated_model_calls": 1,
                "priority": 80,
            }
        ]
        self.assertIsNone(select(state))

    def test_release_rebuild_prerequisite_dispatches_release_build(self):
        task = {
            "stage": "performance_qa",
            "action": "satisfy_prerequisite",
            "blockers": ["release_artifact_rebuild_required"],
        }
        self.assertEqual(pipeline_stage_for_task(task), "release_build")

    def test_preview_task_dispatches_preview_stage(self):
        task = {
            "stage": "code_review",
            "action": "repair_code",
            "blockers": ["Missing persistence"],
        }
        self.assertEqual(pipeline_stage_for_task(task), "preview")


if __name__ == "__main__":
    unittest.main()

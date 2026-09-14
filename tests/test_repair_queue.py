import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from repair_queue import begin_attempt, enqueue, finish_attempt, next_task, summarize


class RepairQueueTests(unittest.TestCase):
    def test_task_is_persistent_scored_and_selected(self):
        state = {}
        task = enqueue(
            state,
            {
                "stage": "performance_qa",
                "action": "repair_code",
                "blockers": ["excessive_jank"],
            },
            estimated_model_calls=1,
        )
        self.assertIsNotNone(task)
        self.assertEqual(next_task(state)["id"], task["id"])
        self.assertGreater(task["priority"], 0)
        self.assertEqual(summarize(state)["pending"], 1)

    def test_completed_recurring_task_reactivates_and_rotates_strategy(self):
        state = {}
        plan = {
            "stage": "performance_qa",
            "action": "repair_code",
            "blockers": ["excessive_jank"],
        }
        task = enqueue(state, plan, estimated_model_calls=1)
        begin_attempt(task)
        finish_attempt(
            task,
            success=True,
            model_calls=1,
            providers_used={"release_fix": "provider-a"},
        )
        self.assertEqual(task["status"], "completed")
        enqueue(state, plan, estimated_model_calls=1)
        enqueue(state, plan, estimated_model_calls=1)
        self.assertEqual(len(state["repair_queue"]), 1)
        self.assertTrue(task["rotate_strategy"])
        self.assertEqual(task["last_provider"], "provider-a")
        self.assertEqual(task["status"], "retry")

    def test_attempt_budget_exhausts_task(self):
        state = {}
        task = enqueue(
            state,
            {
                "stage": "code_review",
                "action": "repair_code",
                "blockers": ["missing persistence"],
            },
        )
        task["max_attempts"] = 1
        begin_attempt(task)
        finish_attempt(task, success=False, improved=False)
        self.assertEqual(task["status"], "exhausted")
        self.assertIsNone(next_task(state))


if __name__ == "__main__":
    unittest.main()

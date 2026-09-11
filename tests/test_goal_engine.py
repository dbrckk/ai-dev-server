import json
from pathlib import Path
import tempfile
import unittest

from studio.goal_engine import GoalStateError,decide,finalize,load,new_goal,record_cycle,save


def goal(max_attempts=3):
    return new_goal("g1","Ship validated app",[
        {"name":"build","required_evidence":["build_sha"]},
        {"name":"qa","required_evidence":["qa_report"]},
    ],max_attempts=max_attempts)


class GoalEngineTests(unittest.TestCase):
    def test_relaunch_until_required_evidence_exists(self):
        s=goal()
        self.assertEqual(decide(s)["decision"],"relaunch")
        s=record_cycle(s,evidence={"build_sha":"abc"})
        self.assertEqual(decide(s),{"decision":"relaunch","missing_evidence":["qa_report"],"next_action":"continue_goal"})

    def test_complete_requires_all_evidence(self):
        s=record_cycle(goal(),evidence={"build_sha":"abc","qa_report":{"passed":True}})
        self.assertEqual(decide(s)["decision"],"complete")
        self.assertEqual(finalize(s)["status"],"complete")

    def test_failure_never_counts_as_completion(self):
        s=record_cycle(goal(),failure="tests failed")
        self.assertEqual(decide(s)["decision"],"relaunch")
        self.assertEqual(s["failures"],["tests failed"])

    def test_missing_capability_requests_adaptation(self):
        s=record_cycle(goal(),missing_capability="unity_android_qa")
        self.assertEqual(decide(s)["decision"],"replan")
        self.assertEqual(decide(s)["next_action"],"adapt:unity_android_qa")

    def test_human_action_is_explicit_terminal_state(self):
        s=record_cycle(goal(),human_action="accept store declarations")
        self.assertEqual(decide(s)["decision"],"human_action_required")
        self.assertEqual(finalize(s)["status"],"human_action_required")

    def test_attempt_budget_blocks_infinite_loop(self):
        s=record_cycle(goal(max_attempts=1),failure="still failing")
        self.assertEqual(decide(s)["decision"],"blocked")
        self.assertEqual(decide(s)["next_action"],"attempt_budget_exhausted")

    def test_persistence_detects_tampering(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"goal.json"
            s=goal()
            save(p,s)
            self.assertEqual(load(p),s)
            value=json.loads(p.read_text())
            value["objective"]="tampered"
            p.write_text(json.dumps(value))
            with self.assertRaisesRegex(GoalStateError,"integrity"):
                load(p)

    def test_terminal_state_is_immutable(self):
        s=finalize(record_cycle(goal(),evidence={"build_sha":"abc","qa_report":"ok"}))
        with self.assertRaisesRegex(GoalStateError,"immutable"):
            record_cycle(s,evidence={"x":"y"})

    def test_false_evidence_rejected(self):
        with self.assertRaisesRegex(GoalStateError,"evidence invalid"):
            record_cycle(goal(),evidence={"build_sha":False})

    def test_attempt_budget_cannot_be_overrun(self):
        s=record_cycle(goal(max_attempts=1),failure="failed")
        with self.assertRaisesRegex(GoalStateError,"attempt budget exhausted"):
            record_cycle(s,failure="again")

    def test_resolve_capability_removes_pending_requirement(self):
        from studio.goal_engine import resolve_capability
        s=record_cycle(goal(),missing_capability="unity.qa")
        s=resolve_capability(s,"unity.qa",{"registry":"verified"})
        self.assertNotIn("unity.qa",s["missing_capabilities"])
        self.assertEqual(decide(s)["decision"],"relaunch")


if __name__=="__main__":
    unittest.main()

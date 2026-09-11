import unittest

from studio.continuous_improvement import assess, improvement_goal, next_candidate
from studio.goal_engine import decide, finalize, new_goal, record_cycle


def complete_goal(*,failures=None,history=None):
    state=new_goal("primary","Ship project",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=10)
    state=record_cycle(state,evidence={"project_completion":{"finished":True}})
    state=finalize(state)
    if failures is None and history is None:
        return state
    # Rebuild through real cycles so integrity remains valid.
    state=new_goal("primary","Ship project",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=10)
    for failure in failures or []:
        state=record_cycle(state,failure=failure)
    for capability in history or []:
        state=record_cycle(state,missing_capability=capability)
        # keep later cycles possible by resolving via a fresh state event contract is not required
        # for assessment; repeated missing-capability evidence itself is what matters.
    state=record_cycle(state,evidence={"project_completion":{"finished":True}})
    # missing capabilities prevent completion, so history-only tests use direct sealed goal below.
    if history:
        return state
    return finalize(state)


class ContinuousImprovementTests(unittest.TestCase):
    def test_active_primary_goal_defers_improvement(self):
        goal=new_goal("g","Work",[{"name":"done","required_evidence":["x"]}])
        result=assess(goal,{})
        self.assertEqual(result["status"],"deferred_until_goal_complete")
        self.assertEqual(result["candidates"],[])

    def test_repeated_failure_creates_high_priority_proof_gated_candidate(self):
        state=new_goal("primary","Ship",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=10)
        state=record_cycle(state,failure="flaky emulator")
        state=record_cycle(state,failure="flaky emulator")
        state=record_cycle(state,evidence={"project_completion":{"finished":True}})
        state=finalize(state)
        result=assess(state,{})
        candidate=next_candidate(result)
        self.assertEqual(candidate["kind"],"repeated_failure")
        self.assertEqual(candidate["priority"],100)
        goal=improvement_goal(candidate)
        self.assertEqual(decide(goal)["decision"],"relaunch")
        goal=record_cycle(goal,evidence={
            "targeted_regression_passed":True,
            "full_regression_passed":True,
        })
        self.assertEqual(decide(goal)["decision"],"complete")

    def test_single_failure_does_not_create_noise(self):
        state=new_goal("primary","Ship",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=10)
        state=record_cycle(state,failure="one-off")
        state=record_cycle(state,evidence={"project_completion":True})
        state=finalize(state)
        self.assertEqual(assess(state,{})["status"],"no_improvement_required")

    def test_passed_stage_warning_creates_candidate(self):
        state=complete_goal()
        project={
            "release_evidence":{
                "artwork_qa":{"passed":True,"warnings":["contrast close to threshold","contrast close to threshold"]}
            }
        }
        result=assess(state,project)
        candidate=next_candidate(result)
        self.assertEqual(candidate["kind"],"persistent_warning")
        self.assertIn("warning_removed",candidate["required_evidence"])

    def test_capability_churn_is_detected_from_history(self):
        state=new_goal("primary","Ship",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=10)
        state=record_cycle(state,missing_capability="billing_qa")
        # resolve to permit another missing event and final completion
        from studio.goal_engine import resolve_capability
        state=resolve_capability(state,"billing_qa",{"validated":True})
        state=record_cycle(state,missing_capability="billing_qa")
        state=resolve_capability(state,"billing_qa",{"validated":True})
        state=record_cycle(state,evidence={"project_completion":True})
        state=finalize(state)
        result=assess(state,{})
        candidate=next_candidate(result)
        self.assertEqual(candidate["kind"],"capability_churn")
        self.assertIn("capability_preflight_passed",candidate["required_evidence"])

    def test_candidate_id_is_deterministic(self):
        state=new_goal("primary","Ship",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=10)
        state=record_cycle(state,failure="repeat")
        state=record_cycle(state,failure="repeat")
        state=record_cycle(state,evidence={"project_completion":True})
        state=finalize(state)
        a=next_candidate(assess(state,{}))
        b=next_candidate(assess(state,{}))
        self.assertEqual(a["id"],b["id"])


if __name__=="__main__":
    unittest.main()

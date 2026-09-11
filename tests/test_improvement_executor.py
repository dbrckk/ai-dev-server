from pathlib import Path
import tempfile
import unittest

from studio.capability_registry import new_registry, register, save as save_registry
from studio.continuous_improvement import assess
from studio.goal_engine import finalize, new_goal, record_cycle
from studio.improvement_backlog import activate_next, load as load_backlog, merge_assessment, new_backlog, save as save_backlog
from studio.improvement_executor import ImprovementExecutionError, run_active_improvement, verified_project_cycle


def candidate_assessment():
    goal=new_goal("primary","Ship",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=10)
    goal=record_cycle(goal,failure="repeat")
    goal=record_cycle(goal,failure="repeat")
    goal=record_cycle(goal,evidence={"project_completion":True})
    goal=finalize(goal)
    return assess(goal,{})


class ImprovementExecutorTests(unittest.TestCase):
    def setup_paths(self,root):
        backlog_path=root/"backlog.json"
        goal_path=root/"improvement-goal.json"
        registry_path=root/"capabilities.json"
        backlog=activate_next(merge_assessment(new_backlog(),candidate_assessment()))
        save_backlog(backlog_path,backlog)
        registry=register(
            new_registry(),
            "improvement.apply.repeated_failure",
            "studio.failure_improver",
            {"tests":"passed","regression":"passed"},
        )
        registry=register(
            registry,
            "improvement.verify.repeated_failure",
            "studio.repeated_failure_verifier",
            {"tests":"passed","regression":"passed"},
        )
        save_registry(registry_path,registry)
        return backlog_path,goal_path,registry_path

    def test_no_active_improvement_is_idle(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            backlog=root/"backlog.json"; registry=root/"capabilities.json"
            save_backlog(backlog,new_backlog()); save_registry(registry,new_registry())
            result=run_active_improvement(backlog,root/"goal.json",registry,lambda state:{},max_cycles=1)
            self.assertEqual(result["status"],"idle")


    def test_missing_verifier_requests_adaptation_without_running_cycles(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            backlog_path=root/"backlog.json"
            goal_path=root/"improvement-goal.json"
            registry_path=root/"capabilities.json"
            backlog=activate_next(merge_assessment(new_backlog(),candidate_assessment()))
            save_backlog(backlog_path,backlog)
            registry=register(
                new_registry(),
                "improvement.apply.repeated_failure",
                "studio.failure_improver",
                {"tests":"passed","regression":"passed"},
            )
            save_registry(registry_path,registry)
            calls={"n":0}
            def execute(state):
                calls["n"]+=1
                return {}
            result=run_active_improvement(backlog_path,goal_path,registry_path,execute,max_cycles=2)
            self.assertEqual(result["status"],"adaptation_required")
            self.assertEqual(result["missing_capability"],"improvement.verify.repeated_failure")
            self.assertEqual(calls["n"],0)
            self.assertFalse(goal_path.exists())

    def test_active_improvement_relaunches_until_proved(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            backlog,goal,registry=self.setup_paths(root)
            calls={"n":0}
            def execute(state):
                calls["n"]+=1
                if calls["n"]==1:
                    return {"failure":"not fixed yet"}
                return {"evidence":{
                    "targeted_regression_passed":True,
                    "full_regression_passed":True,
                }}
            result=run_active_improvement(backlog,goal,registry,execute,max_cycles=3)
            self.assertEqual(result["status"],"proved")
            self.assertTrue(result["proved"])
            self.assertEqual(calls["n"],2)
            self.assertEqual(load_backlog(backlog)["items"][0]["status"],"proved")

    def test_incomplete_improvement_does_not_mutate_primary_success(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            backlog,goal,registry=self.setup_paths(root)
            result=run_active_improvement(
                backlog,goal,registry,
                lambda state:{"human_action":"approve risky migration"},
                max_cycles=1,
            )
            self.assertEqual(result["status"],"incomplete")
            self.assertFalse(result["proved"])
            self.assertEqual(load_backlog(backlog)["items"][0]["status"],"active")

    def test_existing_goal_must_match_active_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            backlog,goal,registry=self.setup_paths(root)
            wrong=new_goal("wrong","Wrong",[{"name":"x","required_evidence":["x"]}])
            from studio.goal_engine import save as save_goal
            save_goal(goal,wrong)
            with self.assertRaisesRegex(ImprovementExecutionError,"mismatch"):
                run_active_improvement(backlog,goal,registry,lambda state:{},max_cycles=1)


    def test_verified_project_cycle_only_emits_trusted_evidence(self):
        candidate={
            "kind":"repeated_failure",
            "source":{"failure":"flaky emulator"},
        }
        wrapped=verified_project_cycle(
            candidate,
            lambda state:{
                "status":"complete",
                "report":{"completion":{"finished":True}},
                "improvement_verification":{
                    "kind":"repeated_failure",
                    "failure":"flaky emulator",
                    "passed":True,
                    "targeted_test_passed":True,
                },
            },
        )
        result=wrapped({})
        self.assertEqual(result["evidence"],{
            "full_regression_passed":True,
            "targeted_regression_passed":True,
        })

    def test_verified_project_cycle_does_not_invent_targeted_proof(self):
        candidate={
            "kind":"repeated_failure",
            "source":{"failure":"flaky emulator"},
        }
        wrapped=verified_project_cycle(
            candidate,
            lambda state:{
                "status":"complete",
                "report":{"completion":{"finished":True}},
            },
        )
        result=wrapped({})
        self.assertEqual(result["evidence"],{"full_regression_passed":True})
        self.assertNotIn("targeted_regression_passed",result["evidence"])


if __name__=="__main__":
    unittest.main()

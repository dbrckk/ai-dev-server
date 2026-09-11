import tempfile
import unittest
from pathlib import Path

from studio.capability_registry import new_registry, register, save as save_registry
from studio.goal_engine import new_goal, save as save_goal
from studio.goal_loop import run_goal


class GoalCapabilityRuntimeTests(unittest.TestCase):
    def state(self, root):
        goal=new_goal("g","finish",[{"name":"done","required_evidence":["done"]}],max_attempts=4)
        goal["missing_capability"]="image_assets"
        goal["status"]="adaptation_required"
        gp=root/"goal.json"; rp=root/"capabilities.json"
        save_goal(gp,goal)
        registry=register(new_registry(),"image_assets","studio.capabilities.image_assets",{"source":"promoted_factory_capability"})
        save_registry(rp,registry)
        return gp,rp

    def test_registered_capability_requires_runtime(self):
        with tempfile.TemporaryDirectory() as td:
            gp,rp=self.state(Path(td))
            state=run_goal(gp,rp,lambda s: {},max_cycles=1)
            self.assertEqual(state["status"],"blocked")
            self.assertIn("no runtime",state["blocked_reason"])

    def test_runtime_must_return_verified_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            gp,rp=self.state(Path(td))
            state=run_goal(
                gp,rp,lambda s: {},max_cycles=1,
                execute_registered_capability=lambda registry,name,state:{"passed":False,"evidence":{}},
            )
            self.assertEqual(state["status"],"in_progress")
            self.assertIn("unverified",state["failures"][-1])

    def test_verified_runtime_resolves_capability(self):
        with tempfile.TemporaryDirectory() as td:
            gp,rp=self.state(Path(td))
            calls=[]
            def runtime(registry,name,state):
                calls.append(name)
                return {"passed":True,"evidence":{"runtime_sha256":"a"*64}}
            state=run_goal(gp,rp,lambda s: {},max_cycles=1,execute_registered_capability=runtime)
            self.assertEqual(calls,["image_assets"])
            self.assertIsNone(state["missing_capability"])
            self.assertEqual(state["status"],"in_progress")
            self.assertEqual(state["adaptation_evidence"]["runtime_evidence"]["runtime_sha256"],"a"*64)


if __name__=="__main__":
    unittest.main()

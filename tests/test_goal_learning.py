from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
from project_memory import new_memory,add_entry
from goal_learning import context_for_goal,learn_from_cycle

class GoalLearningTests(unittest.TestCase):
    def test_context_combines_local_and_reusable_cross_project(self):
        m=new_memory()
        m=add_entry(m,entry_id="a",kind="project",project_id="p1",summary="local",tags=["godot"],evidence={"x":1},provenance={"source":"test"})
        m=add_entry(m,entry_id="b",kind="experience",project_id="p2",summary="reusable",tags=["godot"],evidence={"x":2},provenance={"source":"test"},reusable=True,confidence=100)
        got=context_for_goal(m,"p1",["godot"])
        self.assertEqual({x["summary"] for x in got},{"local","reusable"})
        self.assertEqual(sum(x["same_project"] for x in got),1)

    def test_learning_requires_tests_and_regression_for_reuse(self):
        m=new_memory(); state={"goal_id":"g","attempt":2}; commit="a"*40
        unchanged=learn_from_cycle(m,"p",state,{"evidence":{"x":1},"learning_summary":"x"},commit)
        self.assertEqual(unchanged,m)
        unchanged=learn_from_cycle(m,"p",state,{"evidence":{"x":1},"tests_passed":True,"learning_summary":"x","reusable_learning":True},commit)
        self.assertEqual(unchanged,m)
        learned=learn_from_cycle(m,"p",state,{"evidence":{"x":1},"tests_passed":True,"regression_suite_passed":True,"learning_summary":"proved","learning_tags":["godot"],"reusable_learning":True},commit)
        self.assertEqual(len(learned["entries"]),1); self.assertTrue(learned["entries"][0]["reusable"])
        self.assertEqual(learned["entries"][0]["evidence"]["commit_sha"],commit)

if __name__=="__main__": unittest.main()

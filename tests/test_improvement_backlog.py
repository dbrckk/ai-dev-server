import json
from pathlib import Path
import tempfile
import unittest

from studio.continuous_improvement import assess
from studio.goal_engine import finalize,new_goal,record_cycle
from studio.improvement_backlog import ImprovementBacklogError,activate_next,load,merge_assessment,new_backlog,prove,save


def assessment():
    goal=new_goal("g","ship",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=10)
    goal=record_cycle(goal,failure="repeat")
    goal=record_cycle(goal,failure="repeat")
    goal=record_cycle(goal,evidence={"project_completion":True})
    goal=finalize(goal)
    return assess(goal,{})


class ImprovementBacklogTests(unittest.TestCase):
    def test_assessment_is_deduplicated(self):
        backlog=merge_assessment(new_backlog(),assessment())
        again=merge_assessment(backlog,assessment())
        self.assertEqual(len(backlog["items"]),1)
        self.assertEqual(again,backlog)

    def test_only_one_item_activates(self):
        result=assessment()
        second=dict(result["candidates"][0])
        second["id"]="improvement:second"
        second["priority"]=10
        result={"version":1,"status":"improvement_required","candidates":[result["candidates"][0],second]}
        backlog=activate_next(merge_assessment(new_backlog(),result))
        self.assertEqual(sum(x["status"]=="active" for x in backlog["items"]),1)

    def test_proof_must_cover_candidate_requirements(self):
        backlog=activate_next(merge_assessment(new_backlog(),assessment()))
        cid=backlog["items"][0]["candidate"]["id"]
        with self.assertRaisesRegex(ImprovementBacklogError,"incomplete"):
            prove(backlog,cid,{"targeted_regression_passed":True})
        proved=prove(backlog,cid,{
            "targeted_regression_passed":True,
            "full_regression_passed":True,
        })
        self.assertEqual(proved["items"][0]["status"],"proved")

    def test_persistence_detects_tampering(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"backlog.json"
            backlog=merge_assessment(new_backlog(),assessment())
            save(path,backlog)
            self.assertEqual(load(path),backlog)
            value=json.loads(path.read_text())
            value["items"][0]["status"]="proved"
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(ImprovementBacklogError,"integrity"):
                load(path)


if __name__=="__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from studio.capability_registry import new_registry, save as save_registry
from studio.continuous_improvement import assess
from studio.goal_engine import finalize, new_goal, record_cycle, save as save_goal
from studio.improvement_backlog import activate_next, merge_assessment, new_backlog, save as save_backlog
from studio.improvement_executor import run_active_improvement


class PersistentImprovementRunnerTests(unittest.TestCase):
    def test_completed_project_with_active_improvement_requests_adaptation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            goal=new_goal("primary","Ship",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=8)
            goal=record_cycle(goal,failure="repeat")
            goal=record_cycle(goal,failure="repeat")
            goal=record_cycle(goal,evidence={"project_completion":True})
            goal=finalize(goal)
            backlog=activate_next(merge_assessment(new_backlog(),assess(goal,{})))
            save_backlog(root/"backlog.json",backlog)
            save_registry(root/"capabilities.json",new_registry())
            result=run_active_improvement(
                root/"backlog.json",
                root/"improvement-goal.json",
                root/"capabilities.json",
                lambda state:self.fail("cycle must not run before required applicator exists"),
                max_cycles=1,
            )
            self.assertEqual(result["status"],"adaptation_required")
            self.assertEqual(result["missing_capability"],"improvement.apply.repeated_failure")
            self.assertFalse(result["proved"])


if __name__=="__main__":
    unittest.main()

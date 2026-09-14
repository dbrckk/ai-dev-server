import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
from architecture_reputation_policy_migration_review import render

class ReputationPolicyMigrationReviewTests(unittest.TestCase):
    def test_render_contains_human_review_information(self):
        plan={
            "migration_id":"abc",
            "risk":{"level":"PROMOTION_PATH_CHANGE","reinforced_review_required":True},
            "explanation":{
                "review_action":"reinforced_review_required",
                "policy_changes":[{
                    "transition":"RECOVERING -> TRUSTED",
                    "changes":[
                        {"field":"minimum_confirmations","before":1,"after":2},
                        {"field":"required_gate","change":"added","value":"recovery_review"},
                    ],
                }],
                "state_impact":{"changed_entries":2,"transitions":[{"transition":"TRUSTED -> DEGRADED","count":2}]},
            },
        }
        text=render(plan)
        self.assertIn("PROMOTION_PATH_CHANGE",text)
        self.assertIn("RECOVERING -> TRUSTED",text)
        self.assertIn("minimum_confirmations",text)
        self.assertIn("TRUSTED -> DEGRADED",text)
        self.assertIn("reinforced review",text)

if __name__=="__main__":
    unittest.main()

import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
import architecture_replacement_learning as arl

class ReplacementLearningTests(unittest.TestCase):
    def test_successful_replacement_pair_is_aggregated(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for i in range(5):
                out=root/f"p{i}"; out.mkdir()
                (out/"architecture-replacement-outcome.json").write_text(json.dumps({
                    "status":"replacement_outcome_recorded","current_repo":"a/current","replacement_repo":"a/better",
                    "successful":True,"regressed":False,"rolled_back":False,"quality_score":95.0,"observed_at":float(i+1)
                }))
            row=arl.summarize(root)["rankings"][0]
            self.assertEqual(row["samples"],5)
            self.assertEqual(row["success_rate"],1.0)
            self.assertTrue(row["eligible_for_bias"])
            self.assertGreater(row["wilson_lower_95"],0.5)

    def test_same_pair_is_separated_by_context(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            rows=[
                ("flutter","game","mobile","android",True),
                ("flutter","game","mobile","android",True),
                ("python","trading","backend","linux",False),
                ("python","trading","backend","linux",False),
            ]
            for i,(framework,ptype,domain,platform,success) in enumerate(rows):
                out=root/f"p{i}"; out.mkdir()
                (out/"architecture-replacement-outcome.json").write_text(json.dumps({
                    "status":"replacement_outcome_recorded",
                    "current_repo":"a/current",
                    "replacement_repo":"a/better",
                    "framework":framework,
                    "project_type":ptype,
                    "primary_domain":domain,
                    "platform":platform,
                    "current_major_version":1,
                    "replacement_major_version":2,
                    "successful":success,
                    "regressed":not success,
                    "rollback_prepared":False,
                    "rolled_back":False,
                    "quality_score":95.0 if success else 20.0,
                    "observed_at":float(i+1),
                }))
            rows=arl.summarize(root)["rankings"]
            self.assertEqual(len(rows),2)
            by_framework={x["framework"]:x for x in rows}
            self.assertEqual(by_framework["flutter"]["success_rate"],1.0)
            self.assertEqual(by_framework["python"]["success_rate"],0.0)
            self.assertEqual(by_framework["flutter"]["platform"],"android")

if __name__=="__main__": unittest.main()

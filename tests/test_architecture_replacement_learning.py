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

if __name__=="__main__": unittest.main()

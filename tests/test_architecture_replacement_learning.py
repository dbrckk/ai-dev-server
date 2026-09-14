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

    def test_observation_window_is_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for i,ts in enumerate((100.0,300.0,200.0)):
                out=root/f"p{i}"; out.mkdir()
                (out/"architecture-replacement-outcome.json").write_text(json.dumps({
                    "status":"replacement_outcome_recorded",
                    "current_repo":"a/current","replacement_repo":"a/better",
                    "successful":True,"regressed":False,"rollback_prepared":False,"rolled_back":False,
                    "quality_score":100.0,"observed_at":ts,
                }))
            row=arl.summarize(root)["rankings"][0]
            self.assertEqual(row["first_observed_at"],100.0)
            self.assertEqual(row["latest_observed_at"],300.0)

    def test_detects_recent_regime_shift(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); now=2_000_000_000.0
            outcomes=[]
            for i in range(12):
                outcomes.append((now-200*86400-i,True,False))
            for i in range(5):
                outcomes.append((now-10*86400-i,False,True))
            for i,(ts,successful,regressed) in enumerate(outcomes):
                out=root/f"p{i}"; out.mkdir()
                (out/"architecture-replacement-outcome.json").write_text(json.dumps({
                    "status":"replacement_outcome_recorded",
                    "current_repo":"a/current","replacement_repo":"a/better",
                    "successful":successful,"regressed":regressed,
                    "rollback_prepared":False,"rolled_back":False,
                    "quality_score":100.0 if successful else 0.0,"observed_at":ts,
                }))
            row=arl.summarize(root,now=now)["rankings"][0]
            self.assertTrue(row["regime_shift"])
            self.assertEqual(row["regime_window_days"],30)
            self.assertEqual(row["regime_recent_success_rate"],0.0)
            self.assertGreater(row["regime_drop"],0.2)

    def test_small_recent_sample_does_not_trigger_regime_shift(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); now=2_000_000_000.0
            outcomes=[(now-200*86400-i,True,False) for i in range(10)]
            outcomes += [(now-5*86400,False,True),(now-4*86400,False,True)]
            for i,(ts,successful,regressed) in enumerate(outcomes):
                out=root/f"p{i}"; out.mkdir()
                (out/"architecture-replacement-outcome.json").write_text(json.dumps({
                    "status":"replacement_outcome_recorded",
                    "current_repo":"a/current","replacement_repo":"a/better",
                    "successful":successful,"regressed":regressed,
                    "rollback_prepared":False,"rolled_back":False,
                    "quality_score":100.0 if successful else 0.0,"observed_at":ts,
                }))
            row=arl.summarize(root,now=now)["rankings"][0]
            self.assertFalse(row["regime_shift"])

    def test_sequential_drift_detects_gradual_degradation(self):
        rows=[]
        now=2_000_000_000.0
        sequence=[True,True,True,True,True,True,True,False,True,False,False,False]
        for i,success in enumerate(sequence):
            rows.append({"observed_at":now+i,"successful":success})
        result=arl._sequential_drift(rows)
        self.assertTrue(result["drift_detected"])
        self.assertIn(result["status"],{"drift"})
        self.assertGreater(result["ewma_drop"],0.18)

    def test_sequential_drift_stable_sequence_remains_stable(self):
        rows=[{"observed_at":float(i),"successful":True} for i in range(12)]
        result=arl._sequential_drift(rows)
        self.assertFalse(result["drift_detected"])
        self.assertEqual(result["status"],"stable")

    def test_sequential_drift_requires_minimum_samples(self):
        rows=[{"observed_at":float(i),"successful":False} for i in range(4)]
        result=arl._sequential_drift(rows)
        self.assertEqual(result["status"],"insufficient_evidence")
        self.assertFalse(result["drift_detected"])

if __name__=="__main__": unittest.main()

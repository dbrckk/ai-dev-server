import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from architecture_replacement_planner import plan, write

class ArchitectureReplacementPlannerTests(unittest.TestCase):
    def obsolescence(self):
        return {"deprecation_candidates":[{
            "repo":"a/current",
            "replacement_candidate":"a/better",
            "benchmark_delta":16.0,
            "drift_score":0.9,
            "maintenance_signal":"stale",
            "maintenance_evidence_available":True,
        }]}

    def recommendations(self):
        return {"matches":[
            {
                "repo":"a/current",
                "capabilities":["testing","browser"],
                "languages":["python"],
                "platforms":["linux"],
                "runtime":["local"],
                "integrationComplexity":"medium",
                "resourceLevel":"medium",
            },
            {
                "repo":"a/better",
                "capabilities":["testing","browser","observability"],
                "languages":["python"],
                "platforms":["linux"],
                "runtime":["local"],
                "integrationComplexity":"low",
                "resourceLevel":"low",
            },
        ]}

    def test_low_risk_when_capabilities_are_preserved(self):
        result=plan(self.obsolescence(),self.recommendations())
        row=result["replacement_plans"][0]
        self.assertEqual(row["risk"],"low")
        self.assertEqual(row["estimated_change_scope"],"narrow")
        self.assertEqual(row["impact"]["capabilities_missing"],[])
        self.assertIn("observability",row["impact"]["capabilities_added"])
        self.assertEqual(row["go_no_go"],"NO_GO_PENDING_ISOLATED_BENCHMARK")
        self.assertFalse(result["policy"]["auto_apply_migration"])

    def test_missing_capability_is_high_risk(self):
        recs=self.recommendations()
        recs["matches"][1]["capabilities"]=["testing"]
        result=plan(self.obsolescence(),recs)
        row=result["replacement_plans"][0]
        self.assertEqual(row["risk"],"high")
        self.assertIn("browser",row["impact"]["capabilities_missing"])
        self.assertIn("missing_capabilities_resolved",row["required_gates"])

    def test_missing_maintenance_requires_gate(self):
        obs=self.obsolescence()
        obs["deprecation_candidates"][0]["maintenance_evidence_available"]=False
        result=plan(obs,self.recommendations())
        self.assertIn("maintenance_evidence_completed",result["replacement_plans"][0]["required_gates"])

    def test_write_persists_plan(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            result=write(self.obsolescence(),self.recommendations(),out)
            saved=json.loads((out/"architecture-replacement-plan.json").read_text())
            self.assertEqual(saved,result)

if __name__=="__main__":
    unittest.main()

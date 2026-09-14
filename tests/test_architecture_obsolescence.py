import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from architecture_obsolescence import evaluate, write

class ArchitectureObsolescenceTests(unittest.TestCase):
    def learning(self):
        return {"drift_alerts":[{
            "type":"repository",
            "repo":"a/current",
            "score":0.9,
            "success_delta":-0.4,
            "quality_delta":-25.0,
        }]}

    def benchmark(self):
        return {"comparisons":[{
            "current_repo":"a/current",
            "migration_candidate":True,
            "best_alternative":"a/better",
            "alternatives":[{
                "repo":"a/better",
                "delta_vs_current":12.0,
            }],
        }]}

    def recommendations(self):
        return {"matches":[
            {"repo":"a/current","tier":"recommended"},
            {"repo":"a/better","tier":"core"},
        ]}

    def test_requires_drift_and_benchmark_evidence(self):
        result=evaluate(self.learning(),self.benchmark(),self.recommendations())
        self.assertEqual(len(result["deprecation_candidates"]),1)
        row=result["deprecation_candidates"][0]
        self.assertEqual(row["repo"],"a/current")
        self.assertEqual(row["replacement_candidate"],"a/better")
        self.assertFalse(result["policy"]["auto_deprecate"])
        self.assertFalse(result["policy"]["auto_migrate"])

    def test_weak_drift_is_not_candidate(self):
        learning=self.learning()
        learning["drift_alerts"][0]["score"]=0.2
        result=evaluate(learning,self.benchmark(),self.recommendations())
        self.assertEqual(result["deprecation_candidates"],[])

    def test_no_benchmark_migration_means_no_candidate(self):
        benchmark=self.benchmark()
        benchmark["comparisons"][0]["migration_candidate"]=False
        result=evaluate(self.learning(),benchmark,self.recommendations())
        self.assertEqual(result["deprecation_candidates"],[])

    def test_unknown_maintenance_is_explicit(self):
        result=evaluate(self.learning(),self.benchmark(),self.recommendations())
        row=result["deprecation_candidates"][0]
        self.assertEqual(row["maintenance_signal"],"unknown")
        self.assertFalse(row["maintenance_evidence_available"])

    def test_write_persists_sidecar(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            result=write(self.learning(),self.benchmark(),self.recommendations(),out)
            saved=json.loads((out/"architecture-obsolescence.json").read_text())
            self.assertEqual(saved,result)

if __name__=="__main__":
    unittest.main()

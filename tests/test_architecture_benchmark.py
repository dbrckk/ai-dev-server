import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from architecture_benchmark import benchmark, write

class ArchitectureBenchmarkTests(unittest.TestCase):
    def decision(self):
        return {"constraints":{"framework":"flutter","project_type":"game","primary_domain":"mobile","platform":"android"},"chosen":[{
            "repo":"a/current",
            "selection_score":60,
            "quality_score":8.5,
            "tier":"recommended",
            "alternatives":["a/better","a/unknown"],
        }]}

    def recommendations(self):
        return {"matches":[{
            "repo":"a/better",
            "score":95,
            "quality_score":9.8,
            "tier":"core",
            "capabilities":["testing"],
        }]}

    def test_review_can_surface_migration_candidate(self):
        evaluation={"verdict":"review","blockers":["testing failed","browser failed"]}
        result=benchmark(self.decision(),evaluation,self.recommendations())
        row=result["comparisons"][0]
        self.assertTrue(row["migration_candidate"])
        self.assertEqual(row["best_alternative"],"a/better")
        self.assertFalse(result["policy"]["auto_migrate"])

    def test_benchmark_carries_project_context(self):
        result=benchmark(self.decision(),{"verdict":"review","blockers":["x"]},self.recommendations())
        row=result["comparisons"][0]
        self.assertEqual(row["framework"],"flutter")
        self.assertEqual(row["project_type"],"game")
        self.assertEqual(row["primary_domain"],"mobile")
        self.assertEqual(row["platform"],"android")

    def test_clean_evidence_does_not_propose_migration(self):
        evaluation={"verdict":"retain","blockers":[]}
        result=benchmark(self.decision(),evaluation,self.recommendations())
        self.assertFalse(result["comparisons"][0]["migration_candidate"])

    def test_missing_alternative_metadata_is_explicit(self):
        result=benchmark(self.decision(),{"verdict":"review","blockers":["x"]},self.recommendations())
        alt=[x for x in result["comparisons"][0]["alternatives"] if x["repo"]=="a/unknown"][0]
        self.assertEqual(alt["status"],"metadata_unavailable")

    def test_write_persists_benchmark(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            result=write(self.decision(),{"verdict":"retain","blockers":[]},self.recommendations(),out)
            saved=json.loads((out/"architecture-benchmark.json").read_text())
            self.assertEqual(saved,result)

if __name__=="__main__":
    unittest.main()

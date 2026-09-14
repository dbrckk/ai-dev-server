import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from architecture_planner import plan, write

class ArchitecturePlannerTests(unittest.TestCase):
    def test_selects_ranked_candidates_without_authorizing_dependencies(self):
        recs={"matches":[
            {"repo":"a/core","score":92.0,"quality_score":9.8,"tier":"core","domain":"software_engineering","capabilities":["testing"],"best_for":["qa"],"alternatives":["a/alt"]},
            {"repo":"b/reject","tier":"recommended","capabilities":["ui"],"avoid_when":["native-only"]},
        ]}
        result=plan({"target_repo":"o/r","app_name":"demo"},recs)
        self.assertEqual(result["status"],"planned")
        self.assertFalse(result["dependency_policy"]["allow_automatic_dependency_addition"])
        self.assertEqual(result["chosen"][0]["repo"],"a/core")
        self.assertEqual(result["chosen"][0]["selection_score"],92.0)
        self.assertEqual(result["chosen"][0]["quality_score"],9.8)
        self.assertEqual(result["rejected"][0]["repo"],"b/reject")
        self.assertEqual(result["fallbacks"][0]["alternatives"],["a/alt"])

    def test_write_persists_machine_readable_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            result=write({"target_repo":"o/r","app_name":"demo"},{"matches":[]},out)
            saved=json.loads((out/"architecture-decision.json").read_text())
            self.assertEqual(saved,result)
            self.assertTrue(saved["advisory_only"])

if __name__=="__main__":
    unittest.main()

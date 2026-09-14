import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from architecture_evaluator import evaluate, write

class ArchitectureEvaluatorTests(unittest.TestCase):
    def decision(self):
        return {
            "chosen":[{
                "repo":"a/core",
                "capabilities":["testing","browser"],
                "alternatives":["a/alt"],
            }]
        }

    def test_retain_when_validation_is_clean(self):
        result=evaluate(self.decision(),{"status":"validated_preview","blockers":[]})
        self.assertEqual(result["verdict"],"retain")
        self.assertEqual(result["confidence"],"high")
        self.assertFalse(result["policy"]["auto_replace_dependencies"])

    def test_review_when_blockers_exist(self):
        result=evaluate(self.decision(),{"status":"repair_needed","blockers":["browser testing failed"]})
        self.assertEqual(result["verdict"],"review")
        self.assertTrue(result["reconsider_candidates"])
        self.assertIn("testing",result["findings"][0]["matched"])

    def test_failed_release_evidence_triggers_review(self):
        report={"status":"validated_preview","release_evidence":{"release_build":{"passed":False}}}
        result=evaluate(self.decision(),report)
        self.assertEqual(result["verdict"],"review")
        self.assertEqual(result["failed_release_evidence"],["release_build"])

    def test_write_persists_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            result=write(self.decision(),{"status":"validated_preview"},out)
            saved=json.loads((out/"architecture-evaluation.json").read_text())
            self.assertEqual(saved,result)

if __name__=="__main__":
    unittest.main()

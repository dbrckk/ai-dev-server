from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from fragility_memory import assess, load, record


class FragilityMemoryTests(unittest.TestCase):
    def test_culprit_file_and_zone_accumulate_risk(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"fragility.json"
            for _ in range(4):
                record(path,culprit_files=["src/auth/login.py"],safe_files=[])
            data=load(path)
            self.assertGreater(data["files"]["src/auth/login.py"]["risk"],0.75)
            self.assertGreater(data["zones"]["src/auth"]["risk"],0.75)

    def test_safe_changes_reduce_estimated_risk(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"fragility.json"
            record(path,culprit_files=["src/api.py"],safe_files=[])
            for _ in range(5):
                record(path,culprit_files=[],safe_files=["src/api.py"])
            data=load(path)
            self.assertLess(data["files"]["src/api.py"]["risk"],0.5)

    def test_high_risk_zone_reduces_patch_width(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"fragility.json"
            for _ in range(5):
                record(path,culprit_files=["src/auth/login.py"],safe_files=[])
            result=assess(load(path),["src/auth/session.py"])
            self.assertEqual(result["level"],"high")
            self.assertEqual(result["max_patch_files"],2)
            self.assertTrue(result["extra_verification"])

    def test_medium_or_low_risk_allows_broader_changes(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"fragility.json"
            record(path,culprit_files=["src/x.py"],safe_files=[])
            result=assess(load(path),["src/x.py"])
            self.assertIn(result["level"],{"low","medium"})
            self.assertGreaterEqual(result["max_patch_files"],4)


if __name__=="__main__":
    unittest.main()

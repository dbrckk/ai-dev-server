from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from model_zone_performance import load, provider_bias, record


class ModelZonePerformanceTests(unittest.TestCase):
    def test_provider_gains_positive_bias_after_zone_successes(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"models.json"
            for _ in range(3):
                record(path,"p1","m1",["src/auth/login.py"],success=True,duration=4)
            bias=provider_bias(load(path),["src/auth"])
            self.assertGreater(bias["p1"],0)

    def test_provider_gets_negative_bias_after_failures(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"models.json"
            for _ in range(3):
                record(path,"p1","m1",["src/auth/login.py"],success=False,duration=4)
            bias=provider_bias(load(path),["src/auth"])
            self.assertLess(bias["p1"],0)

    def test_unseen_zone_has_no_bias(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"models.json"
            record(path,"p1","m1",["src/api.py"],success=True,duration=4)
            self.assertEqual(provider_bias(load(path),["src/auth"]),{})


if __name__=="__main__":
    unittest.main()

from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from agent_zone_performance import bonus, load, record, zone_for


class AgentZonePerformanceTests(unittest.TestCase):
    def test_zone_is_derived_from_parent_path(self):
        self.assertEqual(zone_for("src/auth/login.py"),"src/auth")
        self.assertEqual(zone_for("main.py"),"<root>")

    def test_successful_agent_gains_zone_bonus(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"zones.json"
            for _ in range(3):
                record(path,"agent-a",["src/auth/login.py"],success=True,duration=5)
            data=load(path)
            self.assertGreater(bonus(data,"agent-a",["src/auth"]),0)

    def test_repeated_failures_reduce_zone_bonus(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"zones.json"
            for _ in range(3):
                record(path,"agent-a",["src/auth/login.py"],success=False,duration=5)
            data=load(path)
            self.assertLess(bonus(data,"agent-a",["src/auth"]),0)

    def test_unseen_zone_has_no_bonus(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"zones.json"
            record(path,"agent-a",["src/api.py"],success=True,duration=5)
            self.assertEqual(bonus(load(path),"agent-a",["src/auth"]),0.0)


if __name__=="__main__":
    unittest.main()

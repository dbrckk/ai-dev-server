from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1]; STUDIO=ROOT/"studio"
if str(STUDIO) not in sys.path: sys.path.insert(0,str(STUDIO))
from github_agent_performance_store import _validate,AgentPerformanceStoreError
class T(unittest.TestCase):
 def test_valid(self): self.assertEqual(_validate({"opencode:implementation":{"runs":2,"successes":1,"duration_total":3.5}})["opencode:implementation"]["runs"],2)
 def test_invalid_counts(self):
  with self.assertRaises(AgentPerformanceStoreError): _validate({"x:y":{"runs":1,"successes":2,"duration_total":0}})
if __name__=="__main__": unittest.main()

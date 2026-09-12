from pathlib import Path
import sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]; STUDIO=ROOT/"studio"
if str(STUDIO) not in sys.path: sys.path.insert(0,str(STUDIO))
from agents.performance import bonus,record
class T(unittest.TestCase):
 def test_success_history_changes_bounded_bonus(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"p.json"
   record(p,"a","implementation",success=True,duration=1)
   self.assertEqual(bonus(__import__("json").loads(p.read_text()),"a","implementation"),0)
   record(p,"a","implementation",success=True,duration=1)
   self.assertGreater(bonus(__import__("json").loads(p.read_text()),"a","implementation"),0)
if __name__=="__main__": unittest.main()

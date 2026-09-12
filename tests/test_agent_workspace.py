from pathlib import Path
import sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]; STUDIO=ROOT/"studio"
if str(STUDIO) not in sys.path: sys.path.insert(0,str(STUDIO))
from agents.workspace import snapshot,validate_delta,restore

class AgentWorkspaceTests(unittest.TestCase):
 def test_valid_change_is_reported(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); (root/"a.py").write_text("x=1\n")
   before=snapshot(root); (root/"a.py").write_text("x=2\n")
   self.assertEqual(validate_delta(root,before)["changed"],["a.py"])
 def test_deletion_is_rejected_and_restored(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); (root/"a.py").write_text("x=1\n")
   before=snapshot(root); (root/"a.py").unlink()
   with self.assertRaises(ValueError): validate_delta(root,before)
   self.assertTrue((root/"a.py").is_file())
if __name__=="__main__": unittest.main()

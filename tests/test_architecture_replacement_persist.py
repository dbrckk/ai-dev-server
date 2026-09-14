import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from architecture_replacement_persist import ReplacementPersistenceError, _valid_repository, _sha

class ReplacementPersistTests(unittest.TestCase):
    def test_repository_identity_validation(self):
        self.assertTrue(_valid_repository("owner/repo"))
        self.assertFalse(_valid_repository("owner"))
        self.assertFalse(_valid_repository("a/b/c"))

    def test_sha_validation(self):
        self.assertEqual(_sha("0"*40,"x"),"0"*40)
        with self.assertRaises(ReplacementPersistenceError):
            _sha("bad","x")

if __name__=="__main__":
    unittest.main()

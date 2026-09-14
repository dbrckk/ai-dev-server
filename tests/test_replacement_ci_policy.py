import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from replacement_ci_policy import REQUIRED_GITHUB_CHECKS, validate_workflow

class ReplacementCIPolicyTests(unittest.TestCase):
    def test_repository_ci_exposes_required_check_ids(self):
        root=Path(__file__).resolve().parents[1]
        result=validate_workflow(root/".github/workflows/ci.yml")
        self.assertTrue(result["valid"],result)
        self.assertEqual(set(result["required_checks"]),set(REQUIRED_GITHUB_CHECKS))

    def test_missing_required_check_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"ci.yml"
            path.write_text("jobs:\n  python-tests:\n    runs-on: ubuntu-latest\n")
            result=validate_workflow(path)
            self.assertFalse(result["valid"])
            self.assertIn("validate",result["missing_checks"])

if __name__=="__main__":
    unittest.main()

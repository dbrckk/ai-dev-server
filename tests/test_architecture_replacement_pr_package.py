import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from architecture_replacement_pr_package import ReplacementPRPackageError, build, write

class ReplacementPRPackageTests(unittest.TestCase):
    def review(self):
        return {
            "status":"promotion_review_ready",
            "work_order_id":"replace-1",
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "baseline_sha":"0"*40,
            "candidate_sha":"1"*40,
            "candidate_digest":"2"*64,
            "required_gates":["dependency_policy_approved"],
        }

    def candidate(self):
        return {
            "status":"replacement_candidate_validated",
            "work_order_id":"replace-1",
            "current_repo":"a/current",
            "replacement_repo":"a/better",
            "files":[{"path":"lib/a.dart","content":"void main() {}\n"}],
        }

    def test_package_is_non_networking(self):
        result=build(self.review(),self.candidate())
        self.assertEqual(result["status"],"pr_package_ready")
        self.assertFalse(result["policy"]["perform_network_actions"])
        self.assertFalse(result["policy"]["open_pull_request"])
        self.assertFalse(result["policy"]["merge_pull_request"])
        self.assertTrue(result["branch"].startswith("architecture/replacement-"))

    def test_identity_mismatch_is_blocked(self):
        c=self.candidate()
        c["work_order_id"]="other"
        with self.assertRaises(ReplacementPRPackageError):
            build(self.review(),c)

    def test_write_persists_package(self):
        with tempfile.TemporaryDirectory() as td:
            result=write(self.review(),self.candidate(),Path(td))
            self.assertTrue((Path(td)/"architecture-replacement-pr-package.json").is_file())
            self.assertEqual(result["files"][0]["path"],"lib/a.dart")

if __name__=="__main__":
    unittest.main()

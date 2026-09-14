import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
from repo_version_probe import _major, classify_release

class RepoVersionProbeTests(unittest.TestCase):
    def test_semver_major_is_extracted(self):
        self.assertEqual(_major("v3.12.4"),3)
        self.assertEqual(_major("release-2.0.0"),2)

    def test_non_semver_is_unknown(self):
        self.assertIsNone(_major("nightly"))
        self.assertEqual(classify_release({"tag_name":"nightly"})["status"],"unknown")

    def test_release_context_is_bounded(self):
        result=classify_release({"tag_name":"v5.1.0","prerelease":False,"draft":False})
        self.assertEqual(result["major_version"],5)
        self.assertEqual(result["status"],"known")

if __name__=="__main__":
    unittest.main()

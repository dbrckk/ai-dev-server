import tempfile
import unittest
from pathlib import Path

from studio.repository_research_provider import (
    RepositoryResearchError,
    build_repository_providers,
)


class RepositoryResearchProviderTests(unittest.TestCase):
    SHA="a"*40

    def test_search_and_fetch_use_pinned_repository_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"studio").mkdir()
            (root/"tests").mkdir()
            (root/"studio/improvement_dispatch.py").write_text(
                "APPLICATOR_CAPABILITIES={'repeated_failure':'improvement.apply.repeated_failure'}\n"
            )
            (root/"tests/test_improvement.py").write_text(
                "def test_repeated_failure():\n    assert True\n"
            )
            search,fetch=build_repository_providers(
                root,"owner/repo",self.SHA,"improvement.apply.repeated_failure"
            )
            results=search("repeated failure implementation")
            self.assertGreaterEqual(len(results),2)
            for item in results:
                self.assertIn("/blob/"+self.SHA+"/",item["url"])
                self.assertTrue(fetch(item["url"]))

    def test_symlink_and_outside_url_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/"studio").mkdir()
            outside=root/"outside.py"; outside.write_text("secret")
            (root/"studio/link.py").symlink_to(outside)
            search,fetch=build_repository_providers(
                root,"owner/repo",self.SHA,"improvement.apply.repeated_failure"
            )
            self.assertEqual(search("link"),[])
            with self.assertRaises(RepositoryResearchError):
                fetch("https://github.com/other/repo/blob/"+self.SHA+"/studio/x.py")


if __name__=="__main__":
    unittest.main()

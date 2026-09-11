import hashlib
import unittest

from studio.autonomous_research import ResearchError, run_and_remember, run_research
from studio.project_memory import new_memory, query


class AutonomousResearchTests(unittest.TestCase):
    def search(self, query):
        return [
            {"url":"https://docs.example.com/a#section","title":"Official A","kind":"docs"},
            {"url":"https://example.org/b","title":"Source B","kind":"web"},
        ]

    def fetch(self, url):
        return ("content for " + url).encode()

    def test_research_seals_exact_content_and_provenance(self):
        result=run_research("cap-1","Implement safe capability",self.search,self.fetch)
        self.assertEqual(result["status"],"research_complete")
        self.assertEqual(len(result["items"]),2)
        for item in result["items"]:
            expected=hashlib.sha256(self.fetch(item["source"])).hexdigest()
            self.assertEqual(item["content_sha256"],expected)
            self.assertTrue(item["source"].startswith("https://"))
            self.assertNotIn("#",item["source"])

    def test_research_memory_is_non_reusable(self):
        memory,research=run_and_remember(
            new_memory(),"project-a","cap-1","Implement safe capability",self.search,self.fetch
        )
        self.assertEqual(research["status"],"research_complete")
        items=query(memory,project_id="project-a",kind="research")
        self.assertEqual(len(items),2)
        self.assertTrue(all(item["reusable"] is False for item in items))
        self.assertTrue(all("content_sha256" in item["evidence"] for item in items))

    def test_insufficient_sources_never_claims_complete(self):
        result=run_research(
            "cap-2","Need evidence",
            lambda query:[{"url":"https://example.org/one","title":"One","kind":"web"}],
            self.fetch,min_sources=2,
        )
        self.assertEqual(result["status"],"research_incomplete")
        self.assertEqual(result["items"],[])

    def test_http_credentials_and_bad_provider_results_fail_closed(self):
        with self.assertRaisesRegex(ResearchError,"HTTPS"):
            run_research(
                "cap-3","Need evidence",
                lambda query:[{"url":"http://example.org/a","title":"A","kind":"web"},
                              {"url":"https://example.org/b","title":"B","kind":"web"}],
                self.fetch,
            )
        with self.assertRaisesRegex(ResearchError,"provider result"):
            run_research("cap-4","Need evidence",lambda query:None,self.fetch)

    def test_source_deduplication_is_deterministic(self):
        def search(query):
            return [
                {"url":"https://example.org/a#x","title":"A","kind":"web"},
                {"url":"https://example.org/a#y","title":"A duplicate","kind":"web"},
                {"url":"https://example.org/b","title":"B","kind":"web"},
            ]
        result=run_research("cap-5","Need evidence",search,self.fetch)
        self.assertEqual([x["source"] for x in result["items"]],
                         ["https://example.org/a","https://example.org/b"])


if __name__=="__main__":
    unittest.main()

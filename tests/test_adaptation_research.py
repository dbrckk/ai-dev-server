import unittest

from studio.adaptation_research import research_missing_capability
from studio.capability_registry import new_registry
from studio.project_memory import new_memory, query


class AdaptationResearchTests(unittest.TestCase):
    def search(self, query):
        return [
            {"url":"https://docs.example.com/capability","title":"Official docs","kind":"docs"},
            {"url":"https://security.example.org/capability","title":"Security notes","kind":"security"},
        ]

    def fetch(self, url):
        return "validated source body for " + url

    def test_complete_research_never_registers_capability(self):
        registry=new_registry()
        memory,status_memory= None,None
        memory, unchanged, status = research_missing_capability(
            new_memory(), registry, "project-a", "image_assets", self.search, self.fetch
        )
        self.assertEqual(status["status"],"adaptation_required")
        self.assertEqual(status["research_status"],"research_complete")
        self.assertEqual(status["synthesis_status"],"required")
        self.assertEqual(status["promotion_status"],"not_ready")
        self.assertFalse(status["capability_registered"])
        self.assertEqual(unchanged,registry)
        self.assertNotIn("image_assets",unchanged["capabilities"])
        entries=query(memory,project_id="project-a",kind="research")
        self.assertEqual(len(entries),2)
        self.assertTrue(all(item["reusable"] is False for item in entries))

    def test_insufficient_research_stays_in_research(self):
        registry=new_registry()
        memory, unchanged, status = research_missing_capability(
            new_memory(), registry, "project-a", "billing",
            lambda query:[{"url":"https://example.org/one","title":"One","kind":"web"}],
            self.fetch,
            min_sources=2,
        )
        self.assertEqual(status["research_status"],"research_incomplete")
        self.assertEqual(status["next_action"],"research_more")
        self.assertEqual(status["synthesis_status"],"not_started")
        self.assertEqual(status["promotion_status"],"not_ready")
        self.assertEqual(unchanged,registry)
        self.assertEqual(query(memory,project_id="project-a",kind="research"),[])

    def test_research_cannot_override_existing_registry(self):
        registry=new_registry()
        before=registry["registry_sha256"]
        _, after, status = research_missing_capability(
            new_memory(), registry, "project-a", "runtime_probe", self.search, self.fetch
        )
        self.assertEqual(after["registry_sha256"],before)
        self.assertFalse(status["capability_registered"])


if __name__=="__main__":
    unittest.main()

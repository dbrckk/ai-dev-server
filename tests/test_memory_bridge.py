import unittest

from studio.memory_bridge import remember_experience, remember_research
from studio.project_memory import new_memory, query, reusable_for_project


class MemoryBridgeTests(unittest.TestCase):
    def research(self):
        return {
            "status": "research_complete",
            "candidate_id": "billing-abc",
            "items": [{
                "kind": "official_docs",
                "source": "https://developer.android.com/billing",
                "notes": "Official billing documentation retrieved.",
                "content_sha256": "a" * 64,
            }],
        }

    def test_validated_research_is_recorded_but_not_cross_project_reusable(self):
        memory = remember_research(new_memory(), "app-a", self.research())
        items = query(memory, project_id="app-a", kind="research")
        self.assertEqual(len(items), 1)
        self.assertFalse(items[0]["reusable"])
        self.assertEqual(reusable_for_project(memory, "app-b"), [])

    def test_unvalidated_research_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not validated"):
            remember_research(new_memory(), "app-a", {"status": "draft"})

    def test_experience_can_be_reused_only_with_regression_proof(self):
        proof = {
            "tests_passed": True,
            "regression_suite_passed": True,
            "commit_sha": "b" * 40,
        }
        memory = remember_experience(
            new_memory(),
            "app-a",
            entry_id="exp-1",
            summary="Validated release-stage recovery pattern.",
            tags=["release", "recovery"],
            proof=proof,
            reusable=True,
            confidence=95,
        )
        self.assertEqual([x["id"] for x in reusable_for_project(memory, "app-b")], ["exp-1"])

    def test_reusable_experience_without_regression_proof_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "regression proof"):
            remember_experience(
                new_memory(),
                "app-a",
                entry_id="exp-1",
                summary="Unproven shortcut.",
                tags=["release"],
                proof={"tests_passed": True, "commit_sha": "c" * 40},
                reusable=True,
                confidence=95,
            )

    def test_experience_requires_valid_commit_identity(self):
        with self.assertRaisesRegex(ValueError, "commit invalid"):
            remember_experience(
                new_memory(),
                "app-a",
                entry_id="exp-1",
                summary="Broken evidence.",
                tags=["release"],
                proof={"tests_passed": True, "commit_sha": "bad"},
            )


if __name__ == "__main__":
    unittest.main()

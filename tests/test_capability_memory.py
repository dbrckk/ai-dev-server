import unittest

from studio.capability_memory import attach_capability_hints, capability_hints
from studio.project_memory import add_entry, new_memory


def memory():
    value=new_memory()
    return add_entry(
        value,
        entry_id="experience:c1",
        kind="experience",
        project_id="app-a",
        summary="Validated autonomous capability promotion for billing_qa.",
        tags=["capability","billing_qa","autonomous-promotion"],
        evidence={
            "tests_passed":True,
            "regression_suite_passed":True,
            "commit_sha":"a"*40,
            "gap":"billing_qa",
        },
        provenance={"source":"validated_project_execution"},
        reusable=True,
        confidence=95,
    )


class CapabilityMemoryTests(unittest.TestCase):
    def test_returns_cross_project_validated_hint(self):
        hints=capability_hints(memory(),"app-b","billing_qa")
        self.assertEqual(len(hints),1)
        self.assertEqual(hints[0]["source_project"],"app-a")
        self.assertEqual(hints[0]["validated_commit"],"a"*40)

    def test_same_project_is_not_reused(self):
        self.assertEqual(capability_hints(memory(),"app-a","billing_qa"),[])

    def test_unrelated_capability_has_no_hint(self):
        self.assertEqual(capability_hints(memory(),"app-b","notification_qa"),[])

    def test_attached_hints_are_explicitly_non_authoritative(self):
        request={
            "status":"adaptation_required",
            "gaps":[{"kind":"missing_stage_executor","value":"billing_qa","reason":"missing"}],
        }
        enriched=attach_capability_hints(request,memory(),"app-b")
        self.assertIn("billing_qa",enriched["prior_validated_experience"])
        policy=enriched["memory_policy"]
        self.assertEqual(policy["authority"],"hint_only")
        self.assertFalse(policy["may_skip_validation"])
        self.assertFalse(policy["may_register_capability"])
        self.assertTrue(policy["must_revalidate_locally"])


if __name__=="__main__":
    unittest.main()

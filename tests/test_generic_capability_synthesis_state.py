import unittest

from studio.capability_adaptation_state import new_state, record_research, record_synthesis, validate


class GenericCapabilitySynthesisStateTests(unittest.TestCase):
    def test_synthesis_advances_only_after_research(self):
        state=new_state("project-a","improvement.apply.repeated_failure","improvement:abc")
        state=record_research(state,"research_complete")
        state=record_synthesis(state,"a"*64)
        self.assertEqual(state["status"],"validation_required")
        self.assertEqual(state["validation_status"],"required")
        self.assertIn("a"*64,state["synthesis_status"])
        validate(state)

    def test_synthesis_before_research_fails_closed(self):
        state=new_state("project-a","improvement.apply.repeated_failure","improvement:abc")
        with self.assertRaisesRegex(ValueError,"transition"):
            record_synthesis(state,"a"*64)


if __name__=="__main__":
    unittest.main()

import unittest

from studio.capability_adaptation_state import (
    CapabilityAdaptationStateError,
    new_state,
    validate,
    record_research,
)


class CapabilityAdaptationStateTests(unittest.TestCase):
    def test_state_is_deterministic_and_sealed(self):
        one=new_state("project-a","improvement.apply.repeated_failure","improvement:abc")
        two=new_state("project-a","improvement.apply.repeated_failure","improvement:abc")
        self.assertEqual(one,two)
        self.assertEqual(validate(one)["status"],"research_required")
        self.assertEqual(one["adaptation_candidate_id"],
                         "capability:improvement.apply.repeated_failure")

    def test_tampering_fails_closed(self):
        state=new_state("project-a","improvement.apply.repeated_failure","improvement:abc")
        state["status"]="complete"
        with self.assertRaisesRegex(CapabilityAdaptationStateError,"integrity"):
            validate(state)

    def test_research_completion_advances_to_synthesis(self):
        state=new_state("project-a","improvement.apply.repeated_failure","improvement:abc")
        state=record_research(state,"research_complete")
        self.assertEqual(state["status"],"synthesis_required")
        self.assertEqual(state["research_status"],"research_complete")
        self.assertEqual(state["synthesis_status"],"required")
        validate(state)

    def test_validated_candidate_advances_to_promotion_required(self):
        state=new_state("project-a","improvement.apply.repeated_failure","improvement:abc")
        state=record_research(state,"research_complete")
        state=record_synthesis(state,"a"*64)
        state=record_validation(state,"candidate_validated")
        self.assertEqual(state["status"],"promotion_required")
        self.assertEqual(state["promotion_status"],"eligible")
        validate(state)

    def test_rejected_candidate_blocks_adaptation(self):
        state=new_state("project-a","improvement.apply.repeated_failure","improvement:abc")
        state=record_research(state,"research_complete")
        state=record_synthesis(state,"a"*64)
        state=record_validation(state,"candidate_rejected")
        self.assertEqual(state["status"],"blocked")
        self.assertEqual(state["promotion_status"],"not_ready")
        validate(state)

    def test_invalid_capability_rejected(self):
        with self.assertRaisesRegex(CapabilityAdaptationStateError,"capability"):
            new_state("project-a","../escape","improvement:abc")


if __name__=="__main__":
    unittest.main()

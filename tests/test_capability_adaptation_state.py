import unittest

from studio.capability_adaptation_state import (
    CapabilityAdaptationStateError,
    new_state,
    validate,
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

    def test_invalid_capability_rejected(self):
        with self.assertRaisesRegex(CapabilityAdaptationStateError,"capability"):
            new_state("project-a","../escape","improvement:abc")


if __name__=="__main__":
    unittest.main()

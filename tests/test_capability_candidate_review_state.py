import unittest

from studio.capability_adaptation_state import (
    CapabilityAdaptationStateError,
    new_state,
    record_research,
    record_synthesis,
    record_validation,
    record_candidate_persistence,
)


def eligible():
    state=new_state("project","image_assets","improvement:1")
    state=record_research(state,"research_complete")
    state=record_synthesis(state,"a"*64)
    return record_validation(state,"candidate_validated")


class CapabilityCandidateReviewStateTests(unittest.TestCase):
    def test_persisted_candidate_transitions_to_awaiting_merge(self):
        state=record_candidate_persistence(eligible(),"candidate_persisted")
        self.assertEqual(state["status"],"awaiting_merge")
        self.assertEqual(state["promotion_status"],"candidate_review_required")

    def test_idempotent_persistence_result_transitions_to_awaiting_merge(self):
        state=record_candidate_persistence(eligible(),"candidate_already_persisted")
        self.assertEqual(state["status"],"awaiting_merge")

    def test_unproved_persistence_status_fails_closed(self):
        with self.assertRaisesRegex(CapabilityAdaptationStateError,"persistence status"):
            record_candidate_persistence(eligible(),"candidate_branch_created")

    def test_transition_requires_eligible_promotion_state(self):
        state=new_state("project","image_assets","improvement:1")
        with self.assertRaisesRegex(CapabilityAdaptationStateError,"transition"):
            record_candidate_persistence(state,"candidate_persisted")


if __name__=="__main__":
    unittest.main()

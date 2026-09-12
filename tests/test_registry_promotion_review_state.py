import unittest

from studio.capability_adaptation_state import (
    CapabilityAdaptationStateError,
    new_state, record_research, record_synthesis, record_validation,
    record_candidate_persistence, record_registry_promotion_persistence,
)


def awaiting_candidate_review():
    state=new_state("project","image_assets","improvement:1")
    state=record_research(state,"research_complete")
    state=record_synthesis(state,"a"*64)
    state=record_validation(state,"candidate_validated")
    return record_candidate_persistence(state,"candidate_persisted")


class RegistryPromotionReviewStateTests(unittest.TestCase):
    def test_registry_pr_transitions_to_awaiting_registry_merge(self):
        state=record_registry_promotion_persistence(
            awaiting_candidate_review(),"registry_promotion_persisted"
        )
        self.assertEqual(state["status"],"awaiting_registry_merge")
        self.assertEqual(state["promotion_status"],"registry_review_required")

    def test_idempotent_registry_pr_result_is_accepted(self):
        state=record_registry_promotion_persistence(
            awaiting_candidate_review(),"registry_promotion_already_persisted"
        )
        self.assertEqual(state["status"],"awaiting_registry_merge")

    def test_unproved_registry_persistence_fails_closed(self):
        with self.assertRaisesRegex(CapabilityAdaptationStateError,"persistence status"):
            record_registry_promotion_persistence(
                awaiting_candidate_review(),"registry_branch_created"
            )

    def test_wrong_source_state_fails_closed(self):
        state=new_state("project","image_assets","improvement:1")
        with self.assertRaisesRegex(CapabilityAdaptationStateError,"transition"):
            record_registry_promotion_persistence(state,"registry_promotion_persisted")


if __name__=="__main__":
    unittest.main()

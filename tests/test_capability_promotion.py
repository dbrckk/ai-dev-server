import unittest

from studio.capability_promotion import CapabilityPromotionError, promote_candidate


def envelope():
    return {
        "status":"candidate_synthesized",
        "candidate_id":"capability-candidate:image_assets:0123456789abcdef",
        "candidate_sha256":"a"*64,
        "candidate":{
            "version":1,
            "capability":"image_assets",
            "provider":"studio.capabilities.image_assets",
            "implementation":"def provide(): pass",
            "tests":"def test_provider(): pass",
            "risk_notes":[],
            "research":[],
        },
        "benchmark_status":"required",
        "regression_status":"required",
        "promotion_status":"not_ready",
        "capability_registered":False,
    }


def validation():
    return {
        "status":"candidate_validated",
        "candidate_id":"capability-candidate:image_assets:0123456789abcdef",
        "candidate_sha256":"a"*64,
        "capability":"image_assets",
        "provider":"studio.capabilities.image_assets",
        "benchmark_status":"passed",
        "regression_status":"passed",
        "promotion_status":"eligible",
        "capability_registered":False,
        "evidence":{
            "targeted_test_sha256":"b"*64,
            "benchmark_sha256":"c"*64,
            "regression_sha256":"d"*64,
        },
    }


class CapabilityPromotionTests(unittest.TestCase):
    def test_validated_candidate_prepares_promoted_registry_only(self):
        registry={"version":1,"capabilities":{}}
        updated,status=promote_candidate(
            registry,envelope(),validation(),"1"*40,"2"*40
        )
        self.assertIn("image_assets",updated["capabilities"])
        self.assertEqual(status["promotion_status"],"promoted_registry_ready")
        self.assertFalse(status["capability_registered"])
        self.assertEqual(registry["capabilities"],{})

    def test_unvalidated_candidate_fails_closed(self):
        bad=validation(); bad["promotion_status"]="not_ready"
        with self.assertRaisesRegex(CapabilityPromotionError,"eligible"):
            promote_candidate({"version":1,"capabilities":{}},envelope(),bad,"1"*40,"2"*40)

    def test_cross_candidate_validation_is_rejected(self):
        bad=validation(); bad["candidate_sha256"]="f"*64
        with self.assertRaisesRegex(CapabilityPromotionError,"digest mismatch"):
            promote_candidate({"version":1,"capabilities":{}},envelope(),bad,"1"*40,"2"*40)

    def test_provider_must_be_deterministic(self):
        env=envelope()
        env["candidate"]["provider"]="studio.capabilities.custom_redirect"
        bad=validation(); bad["provider"]="studio.capabilities.custom_redirect"
        with self.assertRaisesRegex(CapabilityPromotionError,"deterministic"):
            promote_candidate({"version":1,"capabilities":{}},env,bad,"1"*40,"2"*40)

    def test_conflicting_existing_promotion_is_rejected(self):
        registry={
            "version":1,
            "capabilities":{
                "image_assets":{
                    "provider":"studio.capabilities.image_assets",
                    "candidate_id":"old",
                    "baseline_sha":"3"*40,
                    "candidate_sha":"4"*40,
                }
            },
        }
        with self.assertRaisesRegex(CapabilityPromotionError,"conflict"):
            promote_candidate(registry,envelope(),validation(),"1"*40,"2"*40)


if __name__=="__main__":
    unittest.main()

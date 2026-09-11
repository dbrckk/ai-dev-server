import hashlib
import unittest
from pathlib import Path

from studio.artwork_candidate_bridge import ArtworkCandidateBridgeError, build_artwork_candidate


class ArtworkCandidateBridgeTests(unittest.TestCase):
    def paths(self):
        root=Path(__file__).resolve().parents[1]
        return root/"studio/capabilities/asset_artwork.py", root/"tests/test_asset_artwork_capability.py"

    def test_builds_generic_candidate_and_eligible_validation(self):
        provider,tests=self.paths()
        envelope,validation=build_artwork_candidate(provider,tests)
        self.assertEqual(envelope["candidate"]["capability"],"asset_artwork")
        self.assertEqual(envelope["candidate"]["provider"],"studio.capabilities.asset_artwork")
        self.assertEqual(validation["status"],"candidate_validated")
        self.assertEqual(validation["promotion_status"],"eligible")
        self.assertFalse(validation["capability_registered"])
        self.assertEqual(validation["candidate_sha256"],envelope["candidate_sha256"])
        self.assertEqual(set(validation["evidence"]),{
            "targeted_test_sha256","benchmark_sha256","regression_sha256"
        })

    def test_candidate_digest_covers_provider_and_tests(self):
        provider,tests=self.paths()
        one,_=build_artwork_candidate(provider,tests)
        two,_=build_artwork_candidate(provider,tests)
        self.assertEqual(one["candidate_sha256"],two["candidate_sha256"])
        self.assertEqual(len(one["candidate_sha256"]),64)
        self.assertIn(
            hashlib.sha256(provider.read_bytes()).hexdigest(),
            one["candidate"]["research"][0]["provider_source_sha256"],
        )

    def test_missing_sources_fail_closed(self):
        provider,tests=self.paths()
        with self.assertRaises(ArtworkCandidateBridgeError):
            build_artwork_candidate(provider.with_name("missing.py"),tests)


if __name__=="__main__":
    unittest.main()

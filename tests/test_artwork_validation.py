import tempfile
import unittest
from pathlib import Path

from studio.artwork_validation import ArtworkValidationError, validate_artwork_provider


class ArtworkValidationTests(unittest.TestCase):
    def provider(self):
        return Path(__file__).resolve().parents[1]/"studio/capabilities/asset_artwork.py"

    def test_produces_three_sealed_passed_proofs_without_promotion(self):
        result=validate_artwork_provider(self.provider())
        self.assertEqual(result["status"],"artwork_candidate_validated")
        self.assertEqual(result["promotion_status"],"not_ready")
        self.assertFalse(result["capability_registered"])
        self.assertEqual(result["provider"],"studio.capabilities.asset_artwork")
        for key in ("targeted_test","benchmark","regression"):
            self.assertTrue(result[key]["passed"])
            self.assertEqual(len(result[key]["evidence_sha256"]),64)

    def test_benchmark_has_explicit_baseline(self):
        result=validate_artwork_provider(self.provider())
        self.assertGreaterEqual(result["benchmark"]["score"],result["benchmark"]["baseline_score"])
        self.assertEqual(result["benchmark"]["metric"],"validated_assets_across_fixed_scenarios")

    def test_missing_or_symlink_provider_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            missing=Path(td)/"missing.py"
            with self.assertRaises(ArtworkValidationError):
                validate_artwork_provider(missing)


if __name__=="__main__":
    unittest.main()

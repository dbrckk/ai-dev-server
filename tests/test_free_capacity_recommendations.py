import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import free_capacity_recommendations as fcr


class FreeCapacityRecommendationsTests(unittest.TestCase):
    def test_preferred_self_hosted_capacity_sources_rank_first(self):
        fake = {
            "source": "test",
            "matches": [
                {"repo": "other/tool", "quality_score": 9.9, "score": 99.0},
                {"repo": "ollama/ollama", "quality_score": 9.8, "score": 90.0},
                {"repo": "OpenHands/OpenHands", "quality_score": 9.7, "score": 89.0},
            ],
        }
        with tempfile.TemporaryDirectory() as td, patch.object(fcr, "scan", return_value=fake):
            result = fcr.discover(Path(td))
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["matches"][0]["repo"], "ollama/ollama")
            self.assertTrue(result["matches"][0]["preferred_capacity_source"])
            self.assertTrue((Path(td) / "free-capacity-recommendations.json").is_file())

    def test_policy_does_not_assume_external_unlimited_quota(self):
        with tempfile.TemporaryDirectory() as td, patch.object(
            fcr,
            "scan",
            return_value={"source": "test", "matches": []},
        ):
            result = fcr.discover(Path(td))
        self.assertTrue(result["policy"]["self_hosted_only"])
        self.assertTrue(result["policy"]["does_not_assume_external_unlimited_quota"])


if __name__ == "__main__":
    unittest.main()

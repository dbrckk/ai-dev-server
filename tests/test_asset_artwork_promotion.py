import json
import unittest
from pathlib import Path

from studio.artwork_candidate_bridge import build_artwork_candidate
from studio.capability_promotion import promote_candidate
from studio.promoted_capabilities import load, sync_into_registry
from studio.capability_registry import new_registry


class AssetArtworkPromotionTests(unittest.TestCase):
    BASELINE_SHA="0c9f44167f5b312b944027791e87fabfab44864b"
    CANDIDATE_SHA="c6b1cfcb0551a59415b2277031ff318b0cfbdd54"

    def paths(self):
        root=Path(__file__).resolve().parents[1]
        return (
            root,
            root/"studio/capabilities/asset_artwork.py",
            root/"tests/test_asset_artwork_capability.py",
            root/"control/promoted_capabilities.json",
        )

    def test_static_registry_matches_generic_promotion_gate(self):
        root,provider,tests,registry_path=self.paths()
        envelope,validation=build_artwork_candidate(provider,tests)
        self.assertEqual(
            envelope["candidate_id"],
            "capability-candidate:asset_artwork:176e24c4325c3bb5",
        )
        promoted,status=promote_candidate(
            {"version":1,"capabilities":{}},
            envelope,
            validation,
            self.BASELINE_SHA,
            self.CANDIDATE_SHA,
        )
        self.assertEqual(status["promotion_status"],"promoted_registry_ready")
        self.assertEqual(promoted,load(registry_path))

    def test_promoted_artwork_syncs_only_through_registry_gate(self):
        root,_,_,registry_path=self.paths()
        registry=sync_into_registry(new_registry(),registry_path,repo_root=root)
        item=registry["capabilities"]["asset_artwork"]
        self.assertEqual(item["provider"],"studio.capabilities.asset_artwork")
        self.assertEqual(item["evidence"]["candidate_id"],
                         "capability-candidate:asset_artwork:176e24c4325c3bb5")
        self.assertEqual(item["evidence"]["baseline_sha"],self.BASELINE_SHA)
        self.assertEqual(item["evidence"]["candidate_sha"],self.CANDIDATE_SHA)


if __name__=="__main__":
    unittest.main()

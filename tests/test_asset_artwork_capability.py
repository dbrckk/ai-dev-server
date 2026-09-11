import hashlib
import unittest

from studio.capabilities.asset_artwork import ArtworkCapabilityError, run


class ArtworkCapabilityTests(unittest.TestCase):
    def test_generates_deterministic_icon_and_feature_graphic(self):
        context={
            "label":"Focus Timer",
            "design":{"primary":"#102030","accent":"#5060F6"},
            "assets":["icon","feature_graphic"],
        }
        first=run(context)
        second=run(context)
        self.assertTrue(first["passed"])
        self.assertEqual(first,second)
        self.assertEqual(first["assets"]["icon"]["width"],512)
        self.assertEqual(first["assets"]["feature_graphic"]["height"],500)
        for asset in first["assets"].values():
            self.assertEqual(
                asset["sha256"],
                hashlib.sha256(asset["content"].encode()).hexdigest(),
            )

    def test_escapes_user_visible_label(self):
        result=run({"label":"<script>alert(1)</script>","assets":["feature_graphic"]})
        svg=result["assets"]["feature_graphic"]["content"]
        self.assertNotIn("<script>",svg)
        self.assertIn("&lt;script&gt;",svg)

    def test_invalid_color_falls_back_deterministically(self):
        result=run({"label":"Demo","design":{"primary":"red"},"assets":["icon"]})
        self.assertEqual(result["evidence"]["primary"],"#182030")

    def test_unsupported_or_duplicate_assets_fail_closed(self):
        for assets in (["video"],["icon","icon"],[],["icon","feature_graphic","icon"]):
            with self.subTest(assets=assets), self.assertRaises(ArtworkCapabilityError):
                run({"assets":assets})

    def test_provider_has_no_side_effect_contract(self):
        result=run({"objective":"Create artwork"})
        self.assertEqual(set(result),{"passed","evidence","assets"})
        self.assertEqual(result["evidence"]["generator"],"deterministic-svg-v1")


if __name__=="__main__":
    unittest.main()

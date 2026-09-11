from pathlib import Path
import tempfile
import unittest

from studio.artwork_capability import ArtworkError, select_provider, validate_artwork_set
from studio.capability_registry import new_registry, register
from studio.store_package import encode_rgba


class ArtworkCapabilityTests(unittest.TestCase):
    def png(self,path,w,h):
        path.write_bytes(encode_rgba(w,h,b"\x00\x00\x00\xff"*(w*h)))

    def test_fallback_provider_is_safe_default(self):
        selected=select_provider(new_registry())
        self.assertEqual(selected["mode"],"deterministic_fallback")
        self.assertTrue(selected["requires_local_validation"])

    def test_registered_provider_is_selected_but_still_requires_validation(self):
        registry=register(
            new_registry(),
            "store.artwork.generate",
            "studio.artwork_provider",
            {"tests":"passed","visual_qa":"passed"},
        )
        selected=select_provider(registry)
        self.assertEqual(selected["mode"],"capability")
        self.assertEqual(selected["provider"],"studio.artwork_provider")
        self.assertTrue(selected["requires_local_validation"])

    def test_valid_artwork_requires_visual_qa(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            icon=root/"icon.png"; feature=root/"feature.png"
            self.png(icon,512,512); self.png(feature,1024,500)
            selected=select_provider(new_registry())
            with self.assertRaisesRegex(ArtworkError,"visual qa"):
                validate_artwork_set(icon,feature,provider_selection=selected,visual_qa={"passed":False})
            evidence=validate_artwork_set(
                icon,feature,
                provider_selection=selected,
                visual_qa={"passed":True,"checks":["dimensions","legibility"]},
            )
            self.assertTrue(evidence["passed"])
            self.assertRegex(evidence["assets"]["icon"]["sha256"],r"^[0-9a-f]{64}$")

    def test_wrong_dimensions_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            icon=root/"icon.png"; feature=root/"feature.png"
            self.png(icon,256,256); self.png(feature,1024,500)
            with self.assertRaisesRegex(ArtworkError,"dimensions"):
                validate_artwork_set(
                    icon,feature,
                    provider_selection=select_provider(new_registry()),
                    visual_qa={"passed":True},
                )


if __name__=="__main__":
    unittest.main()

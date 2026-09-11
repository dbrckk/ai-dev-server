import json
from pathlib import Path
import tempfile
import unittest

from studio.capability_registry import CapabilityRegistryError,has_capability,load,new_registry,register,save


class CapabilityRegistryTests(unittest.TestCase):
    def test_register_requires_evidence(self):
        r=new_registry()
        with self.assertRaisesRegex(CapabilityRegistryError,"evidence"):
            register(r,"godot.android.export","studio.godot_android_stage",{})

    def test_register_and_lookup(self):
        r=register(new_registry(),"godot.android.export","studio.godot_android_stage",{"tests":"passed"})
        self.assertTrue(has_capability(r,"godot.android.export"))
        self.assertFalse(has_capability(r,"unity.android.export"))

    def test_persistence_detects_tampering(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"capabilities.json"
            r=register(new_registry(),"godot.visual.qa","studio.godot_visual_stage",{"ci":"green"})
            save(p,r)
            self.assertEqual(load(p),r)
            value=json.loads(p.read_text())
            value["capabilities"]["godot.visual.qa"]["provider"]="tampered"
            p.write_text(json.dumps(value))
            with self.assertRaisesRegex(CapabilityRegistryError,"integrity"):
                load(p)


if __name__=="__main__":
    unittest.main()

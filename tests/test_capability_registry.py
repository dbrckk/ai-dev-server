import json
import pytest
from studio.capability_registry import CapabilityRegistryError,has_capability,load,new_registry,register,save

def test_register_requires_evidence():
    r=new_registry()
    with pytest.raises(CapabilityRegistryError,match="evidence"):
        register(r,"godot.android.export","studio.godot_android_stage",{})

def test_register_and_lookup():
    r=register(new_registry(),"godot.android.export","studio.godot_android_stage",{"tests":"passed"})
    assert has_capability(r,"godot.android.export") is True
    assert has_capability(r,"unity.android.export") is False

def test_persistence_detects_tampering(tmp_path):
    p=tmp_path/"capabilities.json"; r=register(new_registry(),"godot.visual.qa","studio.godot_visual_stage",{"ci":"green"})
    save(p,r); assert load(p)==r
    value=json.loads(p.read_text()); value["capabilities"]["godot.visual.qa"]["provider"]="tampered"; p.write_text(json.dumps(value))
    with pytest.raises(CapabilityRegistryError,match="integrity"): load(p)

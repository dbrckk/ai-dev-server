from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

import godot_release_qa as qa

PRESET='''[preset.0]\nplatform="Android"\n[preset.0.options]\ngradle_build/use_gradle_build=false\ngradle_build/export_format=0\ngradle_build/target_sdk=""\narchitectures/arm64-v8a=false\nversion/code=1\nversion/name="0.1.0"\npackage/unique_name="com.example.demo"\npackage/signed=false\n'''

class GodotReleaseQATests(unittest.TestCase):
    def project(self,root):
        root.mkdir(parents=True,exist_ok=True); (root/'export_presets.cfg').write_text(PRESET); return root

    def test_prepare_normalizes_play_requirements(self):
        with tempfile.TemporaryDirectory() as td:
            root=self.project(Path(td)); result=qa.prepare_store_preset(root); audit=qa.audit_store_preset(root)
        self.assertTrue(result['changed']); self.assertTrue(audit['passed']); self.assertEqual(audit['target_api'],36)
        self.assertEqual(audit['format'],'aab'); self.assertTrue(audit['gradle']); self.assertTrue(audit['arm64'])

    def test_missing_release_keystore_is_human_action(self):
        with tempfile.TemporaryDirectory() as td:
            root=self.project(Path(td)); result=qa.preflight(root,{})
        self.assertFalse(result['passed']); self.assertTrue(result['signing']['human_action_required'])
        self.assertIn('release_keystore_required',result['blockers']); self.assertFalse(result['aab_built'])

    def test_existing_keystore_allows_only_preflight_not_aab_claim(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); project=self.project(root/'project'); key=root/'upload.keystore'; key.write_bytes(b'key')
            env={'GODOT_ANDROID_KEYSTORE_RELEASE_PATH':str(key),'GODOT_ANDROID_KEYSTORE_RELEASE_USER':'upload','GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD':'secret'}
            result=qa.preflight(project,env)
        self.assertTrue(result['passed']); self.assertFalse(result['aab_built'])

    def test_invalid_identity_stays_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root=self.project(Path(td)); p=root/'export_presets.cfg'; p.write_text(PRESET.replace('com.example.demo','bad'))
            qa.prepare_store_preset(root); audit=qa.audit_store_preset(root)
        self.assertFalse(audit['passed']); self.assertIn('invalid_package_id',audit['blockers'])

if __name__=='__main__': unittest.main()

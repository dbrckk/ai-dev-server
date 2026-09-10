from pathlib import Path
import hashlib,json,sys,tempfile,unittest,zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))
from core import StudioError
import godot_privacy_security_qa as gps

class GodotPrivacySecurityTests(unittest.TestCase):
    def _state(self,aab_hash,manifest_hash):
        return {'release_artifact':{'aab_sha256':aab_hash},'store_metadata':{'manifest_sha256':manifest_hash,'listing':{'title':'Demo'}}}
    def test_hash_mismatch_fails_before_audit(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; out.mkdir(); (root/'project.godot').write_text('[application]\n')
            (out/'app-release.aab').write_bytes(b'a')
            (out/'play-store-godot').mkdir(); (out/'play-store-godot'/'manifest.json').write_text('{}')
            with self.assertRaises(StudioError):
                gps.audit(root,out,self._state('0'*64,'1'*64))
    def test_cleartext_and_runtime_bridge_block(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; out.mkdir(); (root/'project.godot').write_text('[application]\n')
            (root/'scripts').mkdir(); (root/'scripts'/'x.gd').write_text('OS.execute("x")\nvar u="http://example.com"\n')
            aab=out/'app-release.aab'; aab.write_bytes(b'a'); store=out/'play-store-godot'; store.mkdir(); mf=store/'manifest.json'; mf.write_text('{}')
            result=gps.audit(root,out,self._state(hashlib.sha256(b'a').hexdigest(),hashlib.sha256(b'{}').hexdigest()))
            self.assertFalse(result['passed']); self.assertIn('dangerous_runtime_bridge_requires_review',result['blockers'])
            self.assertIn('cleartext_network_endpoint_detected',result['blockers'])
if __name__=='__main__': unittest.main()

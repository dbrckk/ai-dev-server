from pathlib import Path
import hashlib,json,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))
from core import StudioError
import godot_store_metadata_qa as gsm

class GodotStoreMetadataTests(unittest.TestCase):
    def test_privacy_fails_closed_on_network_marker(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'project.godot').write_text('[application]\n')
            (root/'scripts').mkdir(); (root/'scripts'/'net.gd').write_text('var r = HTTPRequest.new()\n')
            result=gsm.privacy_classification(root)
            self.assertFalse(result['can_derive_no_external_collection'])
            self.assertTrue(result['blockers'])

    def test_validated_screens_require_exact_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td); shot=out/'godot-visual-a.png'; shot.write_bytes(b'x'*2000)
            digest=hashlib.sha256(shot.read_bytes()).hexdigest()
            state={'visual_qa':{'screenshot_sha256':[digest]},'device_qa':{}}
            with self.assertRaisesRegex(StudioError,'At least two distinct'):
                gsm._validated_screens(out,state)
            state['visual_qa']['screenshot_sha256']=['0'*64]
            with self.assertRaisesRegex(StudioError,'missing or changed'):
                gsm._validated_screens(out,state)

    def test_store_build_requires_signed_aab_evidence(self):
        req={'app_name':'demo_app','brief':'Build a complete polished mobile application.'}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; out.mkdir()
            with self.assertRaisesRegex(StudioError,'validated signed AAB'):
                gsm.build(req,root,out,{'release_artifact':{}})

if __name__=='__main__': unittest.main()

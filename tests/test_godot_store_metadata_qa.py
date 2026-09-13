from pathlib import Path
import hashlib,json,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))
from core import StudioError
from store_package import encode_rgba
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

    def test_generated_store_assets_include_provenance(self):
        req={'app_name':'demo_app','brief':'Build a complete polished mobile productivity application with a focused and accessible workflow.'}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; out.mkdir()
            (root/'project.godot').write_text('[application]\n')
            pixels1=bytes((20,40,80,255))*(320*640)
            pixels2=bytes((80,40,20,255))*(320*640)
            shot1=out/'godot-visual-a.png'; shot2=out/'godot-visual-b.png'
            shot1.write_bytes(encode_rgba(320,640,pixels1))
            shot2.write_bytes(encode_rgba(320,640,pixels2))
            hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in (shot1,shot2)]
            state={
                'release_artifact':{'aab_sha256':'a'*64,'format':'aab'},
                'visual_qa':{'screenshot_sha256':hashes},
                'device_qa':{},
                'design':{'primary':'#102030','accent':'#5060F6'},
                'product':{'journeys':[]},
            }
            result=gsm.build(req,root,out,state)
            self.assertTrue(result['passed'])
            for item in result['assets'].values():
                self.assertEqual(item['provenance']['origin'],'studio_generated')
                self.assertFalse(item['provenance']['external_sources'])
                self.assertEqual(item['provenance']['license_status'],'generated_original')

    def test_store_build_requires_signed_aab_evidence(self):
        req={'app_name':'demo_app','brief':'Build a complete polished mobile application.'}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; out.mkdir()
            with self.assertRaisesRegex(StudioError,'validated signed AAB'):
                gsm.build(req,root,out,{'release_artifact':{}})

if __name__=='__main__': unittest.main()

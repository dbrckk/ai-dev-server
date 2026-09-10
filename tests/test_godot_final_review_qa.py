from pathlib import Path
import hashlib,json,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))
from core import StudioError
import godot_final_review_qa as gfr

def sha(data:bytes)->str: return hashlib.sha256(data).hexdigest()

class GodotFinalReviewTests(unittest.TestCase):
    def fixture(self,root):
        out=root/'out'; out.mkdir()
        aab=b'aab'; manifest=b'{}'; policy=b'policy'; safety=b'{}'
        (out/'app-release.aab').write_bytes(aab)
        store=out/'play-store-godot'; store.mkdir(); (store/'manifest.json').write_bytes(manifest)
        privacy=out/'privacy-godot'; privacy.mkdir(); (privacy/'privacy-policy.md').write_bytes(policy); (privacy/'data-safety.json').write_bytes(safety)
        state={
            'engine':'godot','status':'godot_privacy_security_validated','blockers':[],
            'coverage':{k:True for k in gfr.REQUIRED_COVERAGE},
            'release_preflight':{'package':'com.example.demo','version_code':7,'version_name':'1.2.3','target_api':36},
            'release_artifact':{'format':'aab','signing_scope':'artifact_only','project_code_had_signing_material':False,
                                'certificate_sha256':'1'*64,'package':'com.example.demo','version_code':7,'version_name':'1.2.3',
                                'target_api':36,'aab_sha256':sha(aab)},
            'store_metadata':{'manifest_sha256':sha(manifest),'screenshot_count':2},
            'privacy_security':{'release_aab_sha256':sha(aab),'store_manifest_sha256':sha(manifest),
                                'policy_sha256':sha(policy),'data_safety_sha256':sha(safety),
                                'data_safety':{'requires_human_legal_attestation':True}},
            'visual_qa':{'screenshot_sha256':['2'*64]},
        }
        return out,state

    def test_full_bound_evidence_becomes_technical_store_ready_only(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out,state=self.fixture(root)
            result=gfr.review(root,out,state)
            self.assertTrue(result['technical_store_ready']); self.assertFalse(result['published'])
            self.assertIn('play_console_submission',result['human_actions_required'])
            self.assertIn('data_safety_legal_attestation',result['human_actions_required'])

    def test_changed_artifact_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out,state=self.fixture(root); (out/'app-release.aab').write_bytes(b'tampered')
            with self.assertRaisesRegex(StudioError,'hash mismatch'): gfr.review(root,out,state)

    def test_cross_stage_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out,state=self.fixture(root); state['privacy_security']['release_aab_sha256']='0'*64
            with self.assertRaisesRegex(StudioError,'cross-stage hash binding'): gfr.review(root,out,state)

    def test_missing_coverage_or_attestation_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out,state=self.fixture(root); state['coverage']['security_qa']=False
            with self.assertRaisesRegex(StudioError,'missing coverage'): gfr.review(root,out,state)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out,state=self.fixture(root); state['privacy_security']['data_safety']['requires_human_legal_attestation']=False
            with self.assertRaisesRegex(StudioError,'attestation contract'): gfr.review(root,out,state)

if __name__=='__main__': unittest.main()

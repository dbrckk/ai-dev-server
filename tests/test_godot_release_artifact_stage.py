from pathlib import Path
import hashlib
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from core import StudioError
from godot_release_artifact_stage import execute

REQ={'id':'demo-v1','target_repo':'owner/app','app_name':'demo_app','brief':'Build a complete polished mobile application.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}
STATE={'engine':'godot','status':'godot_release_preflight_validated','release_preflight':{'format':'aab','target_api':36,'package':'com.example.demo','version_code':1,'version_name':'1.0'},'coverage':{'visual_qa':True},'completion':{'finished':False,'next_stage':'godot_release_artifact_qa'}}
ENV={'GODOT_ANDROID_KEYSTORE_RELEASE_PATH':'/tmp/key','GODOT_ANDROID_KEYSTORE_RELEASE_USER':'upload','GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD':'secret'}
class FakeGitHub: pass

class GodotReleaseArtifactStageTests(unittest.TestCase):
    @patch('godot_release_artifact_stage._publish',return_value='b'*40)
    @patch('godot_release_artifact_stage._restore')
    @patch('godot_release_artifact_stage.signing_credentials',return_value={'available':True})
    def test_success_advances_only_to_store_metadata(self,creds,restore,publish):
        restore.return_value=(dict(STATE),'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); key=root/'key'; key.write_bytes(b'k'); env=dict(ENV); env['GODOT_ANDROID_KEYSTORE_RELEASE_PATH']=str(key)
            def runtime(path): return path/'godot'
            def source(path): return path/'android_source.zip'
            def builder(project,binary,tpl,artifact): artifact.write_bytes(b'u'*2000); return {'passed':True,'unsigned_aab_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'network':'none','source_project':'not_mounted','signing_material_exposed':False}
            def signer(unsigned,signed,keystore,alias,password): signed.write_bytes(b's'*2000); return {'passed':True,'signed_aab_sha256':hashlib.sha256(signed.read_bytes()).hexdigest(),'certificate_sha256':'c'*64,'signing_scope':'artifact_only','project_code_had_signing_material':False}
            result=execute(REQ,root/'work',root/'out',FakeGitHub(),runtime,source,builder,signer,env)
        self.assertEqual(result['status'],'godot_release_artifact_validated'); self.assertTrue(result['coverage']['release_artifact']); self.assertTrue(result['coverage']['release_signed'])
        self.assertFalse(result['completion']['finished']); self.assertEqual(result['completion']['next_stage'],'godot_store_metadata_qa')

    @patch('godot_release_artifact_stage._publish',return_value='b'*40)
    @patch('godot_release_artifact_stage._restore')
    @patch('godot_release_artifact_stage.signing_credentials',return_value={'available':False,'blocker':'release_keystore_required'})
    def test_lost_credentials_returns_to_human_action(self,creds,restore,publish):
        restore.return_value=(dict(STATE),'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),env={})
        self.assertEqual(result['status'],'godot_release_credentials_required'); self.assertEqual(result['release_status'],'human_action_required')
        self.assertEqual(result['completion']['next_stage'],'godot_release_qa')

    @patch('godot_release_artifact_stage._publish',return_value='b'*40)
    @patch('godot_release_artifact_stage._restore')
    @patch('godot_release_artifact_stage.signing_credentials',return_value={'available':True})
    def test_project_build_cannot_claim_signing_isolation_if_exposed(self,creds,restore,publish):
        restore.return_value=(dict(STATE),'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); key=root/'key'; key.write_bytes(b'k'); env=dict(ENV); env['GODOT_ANDROID_KEYSTORE_RELEASE_PATH']=str(key)
            def builder(project,binary,tpl,artifact): artifact.write_bytes(b'u'*2000); return {'passed':True,'unsigned_aab_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'network':'none','source_project':'not_mounted','signing_material_exposed':True}
            with self.assertRaisesRegex(StudioError,'violated signing isolation'):
                execute(REQ,root/'work',root/'out',FakeGitHub(),lambda p:p/'g',lambda p:p/'s',builder,lambda *a:{},env)

if __name__=='__main__': unittest.main()

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from godot_release_stage import execute

REQ={'id':'demo-v1','target_repo':'owner/app','app_name':'demo_app','brief':'Build a complete polished mobile application.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}
STATE={'engine':'godot','status':'godot_visual_validated','coverage':{'android_export':True,'device_qa':True,'journeys_executed':True,'visual_qa':True},'completion':{'finished':False,'next_stage':'godot_release_qa'}}
AUDIT={'passed':True,'blockers':[],'package':'com.example.demo','version_code':1,'version_name':'0.1.0','target_api':36,'format':'aab','gradle':True,'arm64':True}
class FakeGitHub: pass

class GodotReleaseStageTests(unittest.TestCase):
    @patch('godot_release_stage._publish',return_value='b'*40)
    @patch('godot_release_stage._restore')
    def test_missing_signing_is_human_action_not_success(self,restore,publish):
        restore.return_value=(dict(STATE),'a'*40,True)
        evidence={'passed':False,'preset_normalized':True,'audit':dict(AUDIT),'signing':{'available':False,'human_action_required':True,'blocker':'release_keystore_required'},'blockers':['release_keystore_required'],'aab_built':False}
        with tempfile.TemporaryDirectory() as td:
            result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),lambda root:evidence)
        self.assertEqual(result['status'],'godot_release_credentials_required'); self.assertEqual(result['release_status'],'human_action_required')
        self.assertFalse(result['completion']['finished']); self.assertEqual(result['completion']['next_stage'],'godot_release_qa')

    @patch('godot_release_stage._publish',return_value='b'*40)
    @patch('godot_release_stage._restore')
    def test_signing_inputs_advance_only_to_aab_artifact(self,restore,publish):
        restore.return_value=(dict(STATE),'a'*40,True)
        evidence={'passed':True,'preset_normalized':True,'audit':dict(AUDIT),'signing':{'available':True,'human_action_required':False,'blocker':None},'blockers':[],'aab_built':False}
        with tempfile.TemporaryDirectory() as td:
            result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),lambda root:evidence)
        self.assertEqual(result['status'],'godot_release_preflight_validated'); self.assertEqual(result['completion']['next_stage'],'godot_release_artifact_qa')
        self.assertFalse(result['release_preflight']['aab_built']); self.assertFalse(result['completion']['finished'])

    @patch('godot_release_stage._publish',return_value='b'*40)
    @patch('godot_release_stage._restore')
    def test_invalid_preset_stays_on_release_qa(self,restore,publish):
        restore.return_value=(dict(STATE),'a'*40,True)
        evidence={'passed':False,'audit':{'passed':False},'signing':{'available':False},'blockers':['target_api_36_required'],'aab_built':False}
        with tempfile.TemporaryDirectory() as td:
            result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),lambda root:evidence)
        self.assertEqual(result['status'],'godot_release_qa_failed'); self.assertEqual(result['completion']['next_stage'],'godot_release_qa')

if __name__=='__main__': unittest.main()

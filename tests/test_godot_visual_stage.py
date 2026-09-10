from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from core import StudioError
from godot_visual_stage import execute

REQ={'id':'demo-v1','target_repo':'owner/app','app_name':'demo_app','brief':'Build a complete polished mobile application.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}
JOURNEYS=[{'id':'home','steps':[{'action':'tap','key':'start_button'},{'action':'expect_text','value':'Ready'}]},
          {'id':'settings','steps':[{'action':'tap','key':'settings_button'},{'action':'expect_text','value':'Settings'}]}]
STATE={'engine':'godot','status':'godot_runtime_journeys_validated','product':{'journeys':JOURNEYS},'design':{'direction':'clean'},
       'coverage':{'android_export':True,'device_qa':True,'journeys_executed':True,'visual_qa':False},
       'completion':{'finished':False,'next_stage':'godot_visual_qa'}}

class FakeGitHub: pass

class GodotVisualStageTests(unittest.TestCase):
    @patch('godot_visual_stage._publish',return_value='b'*40)
    @patch('godot_visual_stage._restore')
    def test_success_advances_only_to_release_qa(self,restore,publish):
        restore.return_value=(dict(STATE),'a'*40,True)
        evidence={'passed':True,'visual_reviewed':True,'blockers':[],'journey_ids':['home','settings'],
                  'screenshot_sha256':['1'*64,'2'*64],'environment':'android_emulator','network':'airplane_mode','review_model':'vision'}
        with tempfile.TemporaryDirectory() as td:
            result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),lambda *args:evidence)
        self.assertEqual(result['status'],'godot_visual_validated'); self.assertTrue(result['coverage']['visual_qa'])
        self.assertFalse(result['completion']['finished']); self.assertEqual(result['completion']['next_stage'],'godot_release_qa')

    @patch('godot_visual_stage._publish',return_value='b'*40)
    @patch('godot_visual_stage._restore')
    def test_rejected_visual_stays_on_visual_qa(self,restore,publish):
        restore.return_value=(dict(STATE),'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),lambda *args:{'passed':False,'blockers':['clipping']})
        self.assertEqual(result['status'],'godot_visual_qa_failed'); self.assertEqual(result['completion']['next_stage'],'godot_visual_qa')

    @patch('godot_visual_stage._restore')
    def test_requires_real_journey_coverage(self,restore):
        bad=dict(STATE); bad['coverage']=dict(STATE['coverage']); bad['coverage']['journeys_executed']=False
        restore.return_value=(bad,'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(StudioError,'checkpoint contract'):
                execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),lambda *args:{})

if __name__=='__main__': unittest.main()

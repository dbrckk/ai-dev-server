from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from core import StudioError
from godot_runtime_journey_stage import execute

REQ={'id':'jumpy','target_repo':'dbrckk/Jumpy','app_name':'jumpy','brief':'Build a polished mobile game.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}
JOURNEYS=[{'id':'settings','steps':[{'action':'tap','key':'settings_button'},{'action':'expect_text','value':'Settings'}]}]

class FakeGitHub: pass

class GodotRuntimeJourneyStageTests(unittest.TestCase):
    @patch('godot_runtime_journey_stage._publish',return_value='b'*40)
    @patch('godot_runtime_journey_stage._restore')
    def test_all_journeys_advance_only_to_visual_qa(self,restore,publish):
        restore.return_value=({'engine':'godot','status':'godot_device_validated','product':{'journeys':JOURNEYS},'coverage':{'device_qa':True},'completion':{'finished':False,'next_stage':'godot_runtime_journey_qa'}},'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            def installer(_): return Path(td)/'godot'
            def runner(root,binary,journeys): return {'passed':True,'journeys_executed':True,'journey_count':1,'passed_ids':['settings'],'network':'none','source_project':'not_mounted','binary_sha256':'c'*64,'harness':'trusted_ephemeral_v1'}
            result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),installer,runner)
        self.assertEqual(result['status'],'godot_runtime_journeys_validated')
        self.assertTrue(result['coverage']['journeys_executed']); self.assertFalse(result['coverage']['visual_qa'])
        self.assertFalse(result['completion']['finished']); self.assertEqual(result['completion']['next_stage'],'godot_visual_qa')

    @patch('godot_runtime_journey_stage._publish',return_value='b'*40)
    @patch('godot_runtime_journey_stage._restore')
    def test_partial_success_stays_on_journey_stage(self,restore,publish):
        restore.return_value=({'engine':'godot','status':'godot_device_validated','product':{'journeys':JOURNEYS},'completion':{'finished':False,'next_stage':'godot_runtime_journey_qa'}},'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),lambda _:Path(td)/'godot',lambda *args:{'passed':False,'journeys_executed':False,'journey_count':1})
        self.assertEqual(result['status'],'godot_runtime_journey_qa_failed'); self.assertEqual(result['completion']['next_stage'],'godot_runtime_journey_qa')

    @patch('godot_runtime_journey_stage._restore')
    def test_requires_device_validated_checkpoint(self,restore):
        restore.return_value=({'engine':'godot','status':'godot_android_export_validated','completion':{'finished':False,'next_stage':'godot_device_qa'}},'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(StudioError,'validated device checkpoint'):
                execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub())

if __name__=='__main__': unittest.main()

from pathlib import Path
import hashlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from core import StudioError
from godot_device_stage import execute

REQ={'id':'jumpy','target_repo':'dbrckk/Jumpy','app_name':'jumpy','brief':'Build a polished mobile game.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}

class FakeGitHub: pass


def state(apk_sha):
    return {'engine':'godot','status':'godot_android_export_validated','completion':{'finished':False,'next_stage':'godot_device_qa'},
            'android_export':{'apk_sha256':apk_sha},'coverage':{'android_export':True,'device_qa':False}}

class GodotDeviceStageTests(unittest.TestCase):
    @patch('godot_device_stage._publish',return_value='b'*40)
    @patch('godot_device_stage._restore')
    def test_matching_local_apk_advances_only_to_journey_qa(self,restore,publish):
        payload=b'a'*2000; digest=hashlib.sha256(payload).hexdigest(); restore.return_value=(state(digest),'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'work'; out=Path(td)/'out'; out.mkdir(); (out/'app-debug.apk').write_bytes(payload)
            def validator(project,apk,expected,target):
                return {'passed':True,'environment':'android_emulator','package':'com.dbrckk.jumpy','apk_sha256':expected,
                        'screenshot_sha256':'c'*64,'network':'airplane_mode','journeys_executed':False,'visual_reviewed':False}
            result=execute(REQ,root,out,FakeGitHub(),device_validator=validator)
        self.assertEqual(result['status'],'godot_device_validated')
        self.assertEqual(result['completion']['next_stage'],'godot_runtime_journey_qa')
        self.assertFalse(result['completion']['finished']); self.assertTrue(result['coverage']['device_qa'])
        self.assertFalse(result['coverage']['journeys_executed']); self.assertFalse(result['coverage']['visual_qa'])

    @patch('godot_device_stage._publish',return_value='b'*40)
    @patch('godot_device_stage._restore')
    def test_missing_local_apk_is_reexported_and_rebound(self,restore,publish):
        restore.return_value=(state('a'*64),'a'*40,True); payload=b'z'*2000; digest=hashlib.sha256(payload).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'work'; out=Path(td)/'out'
            def runtime(_): return Path(td)/'godot'
            def templates(_): return Path(td)/'templates'
            def exporter(project,binary,tpls,artifact_path=None):
                artifact_path.parent.mkdir(parents=True,exist_ok=True); artifact_path.write_bytes(payload)
                return {'passed':True,'apk_sha256':digest}
            def validator(project,apk,expected,target):
                self.assertEqual(expected,digest)
                return {'passed':True,'environment':'android_emulator','package':'com.dbrckk.jumpy','apk_sha256':expected,
                        'screenshot_sha256':'c'*64,'network':'airplane_mode','journeys_executed':False,'visual_reviewed':False}
            result=execute(REQ,root,out,FakeGitHub(),validator,runtime,templates,exporter)
        self.assertEqual(result['android_export']['apk_sha256'],digest)
        self.assertTrue(result['android_export']['reexported_for_device_qa'])
        self.assertTrue(result['device_qa']['reexported'])

    @patch('godot_device_stage._restore')
    def test_requires_android_export_checkpoint(self,restore):
        restore.return_value=({'engine':'godot','status':'godot_preview_validated','completion':{'finished':False,'next_stage':'godot_android_export_qa'}},'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(StudioError,'validated Android export checkpoint'):
                execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub())

    @patch('godot_device_stage._publish',return_value='b'*40)
    @patch('godot_device_stage._restore')
    def test_device_cannot_spoof_journey_or_visual_evidence(self,restore,publish):
        payload=b'a'*2000; digest=hashlib.sha256(payload).hexdigest(); restore.return_value=(state(digest),'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'work'; out=Path(td)/'out'; out.mkdir(); (out/'app-debug.apk').write_bytes(payload)
            def validator(*args): return {'passed':True,'apk_sha256':digest,'journeys_executed':True,'visual_reviewed':False}
            with self.assertRaisesRegex(StudioError,'invalid evidence contract'):
                execute(REQ,root,out,FakeGitHub(),device_validator=validator)

if __name__=='__main__': unittest.main()

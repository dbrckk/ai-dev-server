import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from core import StudioError
from godot_android_stage import execute

REQ={'id':'jumpy','target_repo':'dbrckk/Jumpy','app_name':'Jumpy','brief':'Build a polished mobile game.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}

class FakeGitHub: pass

class GodotAndroidStageTests(unittest.TestCase):
    @patch('godot_android_stage._publish', return_value='b'*40)
    @patch('godot_android_stage._restore')
    def test_success_advances_only_to_device_qa(self, restore, publish):
        state={'engine':'godot','status':'godot_preview_validated','completion':{'finished':False,'next_stage':'godot_android_export_qa'},'coverage':{}}
        restore.return_value=(state,'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'work'; out=Path(td)/'out'
            def runtime(_): return Path(td)/'godot'
            def templates(_): return Path(td)/'templates'
            def exporter(project,binary,tpls,artifact_path=None):
                artifact_path.parent.mkdir(parents=True,exist_ok=True); artifact_path.write_bytes(b'apk')
                return {'passed':True,'apk_sha256':'c'*64,'preset':'Android','engine_version':'4.7.2-stable','templates_sha256':'d'*64,'release_signed':False}
            result=execute(REQ,root,out,FakeGitHub(),runtime,templates,exporter)
        self.assertEqual(result['status'],'godot_android_export_validated')
        self.assertFalse(result['completion']['finished'])
        self.assertEqual(result['completion']['next_stage'],'godot_device_qa')
        self.assertTrue(result['coverage']['android_export'])
        self.assertFalse(result['coverage']['device_qa'])

    @patch('godot_android_stage._restore')
    def test_requires_validated_preview_checkpoint(self, restore):
        restore.return_value=({'engine':'godot','status':'pending','completion':{'finished':False,'next_stage':'preview'}},'a'*40,True)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(StudioError,'validated preview checkpoint'):
                execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub())

if __name__=='__main__': unittest.main()

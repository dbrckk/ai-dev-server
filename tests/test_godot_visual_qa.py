from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from core import StudioError
import godot_visual_qa as qa


class FakeModel:
    def __init__(self,limit): self.models_used={}
    def ask(self,role,context,screenshots=()):
        self.models_used[role]='vision-test'; return {'passed':True,'blockers':[]}


class GodotVisualQATests(unittest.TestCase):
    def project(self,root):
        root.mkdir(parents=True,exist_ok=True)
        (root/'project.godot').write_text('[application]\nrun/main_scene="res://scenes/Main.tscn"\n')
        (root/'export_presets.cfg').write_text('package/unique_name="com.example.demo"\n')
        (root/'scenes').mkdir(); (root/'scenes/Main.tscn').write_text('[gd_scene format=3]\n[node name="Main" type="Node"]\n')
        return root

    def journeys(self):
        return [{'id':'home','steps':[{'action':'tap','key':'start_button'},{'action':'expect_text','value':'Ready'}]},
                {'id':'settings','steps':[{'action':'tap','key':'settings_button'},{'action':'expect_text','value':'Settings'}]}]

    def test_instrumentation_changes_only_ephemeral_copy(self):
        with tempfile.TemporaryDirectory() as td:
            source=self.project(Path(td)/'source'); before=(source/'project.godot').read_text(); target=Path(td)/'copy'; target.mkdir()
            qa._instrument(source,target,self.journeys())
            self.assertEqual((source/'project.godot').read_text(),before)
            self.assertIn('res://.studio_visual_runner.tscn',(target/'project.godot').read_text())
            self.assertTrue((target/'.studio_visual_journeys.json').is_file())

    def test_safe_env_drops_ci_credentials(self):
        with patch.dict(os.environ,{'PATH':'/bin','HOME':'/tmp','GITHUB_TOKEN':'secret','STUDIO_API_KEY':'secret'},clear=True):
            env=qa._safe_env()
        self.assertEqual(env,{'PATH':'/bin','HOME':'/tmp'})

    @patch('godot_visual_qa._pull_png')
    @patch('godot_visual_qa.shutil.which',return_value='/usr/bin/adb')
    def test_success_requires_every_android_frame_and_vision_review(self,which,pull):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=self.project(root/'source'); out=root/'out'; calls=[]
            def runtime(path): path.mkdir(parents=True,exist_ok=True); p=path/'godot'; p.write_bytes(b'x'); return p
            def templates(path): path.mkdir(parents=True,exist_ok=True); return path
            def exporter(project,binary,tpls,artifact_path=None): artifact_path.write_bytes(b'a'*2000); return {'passed':True}
            def runner(args,timeout=120,**kwargs):
                calls.append(args)
                import subprocess
                if args[-1:] == ['devices']: return subprocess.CompletedProcess(args,0,'List of devices attached\nemulator-5554\tdevice\n')
                if 'logcat' in args and '-d' in args:
                    text='STUDIO_VISUAL_PASS:home\nSTUDIO_VISUAL_PASS:settings\nSTUDIO_VISUAL_COMPLETE:2\n'
                    return subprocess.CompletedProcess(args,0,text)
                return subprocess.CompletedProcess(args,0,'')
            def write_png(adb,serial,package,jid,target):
                target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(qa.PNG_SIG+(jid.encode()*600)[:1800])
            pull.side_effect=write_png
            result=qa.capture_and_review(source,self.journeys(),{'direction':'clean'},out,FakeModel,runtime,templates,exporter,runner,lambda _:None)
        self.assertTrue(result['passed']); self.assertTrue(result['visual_reviewed']); self.assertEqual(result['journey_ids'],['home','settings'])
        self.assertEqual(len(set(result['screenshot_sha256'])),2)

    @patch('godot_visual_qa._pull_png')
    @patch('godot_visual_qa.shutil.which',return_value='/usr/bin/adb')
    def test_missing_visual_marker_fails_closed(self,which,pull):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=self.project(root/'source')
            def runtime(path): path.mkdir(parents=True,exist_ok=True); p=path/'godot'; p.write_bytes(b'x'); return p
            def templates(path): path.mkdir(parents=True,exist_ok=True); return path
            def exporter(project,binary,tpls,artifact_path=None): artifact_path.write_bytes(b'a'*2000); return {'passed':True}
            def runner(args,timeout=120,**kwargs):
                import subprocess
                if args[-1:] == ['devices']: return subprocess.CompletedProcess(args,0,'List of devices attached\nemulator-5554\tdevice\n')
                if 'logcat' in args and '-d' in args: return subprocess.CompletedProcess(args,0,'STUDIO_VISUAL_PASS:home\n')
                return subprocess.CompletedProcess(args,0,'')
            with self.assertRaisesRegex(StudioError,'did not complete every journey'):
                qa.capture_and_review(source,self.journeys(),{'direction':'clean'},root/'out',FakeModel,runtime,templates,exporter,runner,lambda _:None)

if __name__=='__main__': unittest.main()

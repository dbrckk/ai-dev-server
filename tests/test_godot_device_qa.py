from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from core import StudioError
import godot_device_qa as qa


class GodotDeviceQATests(unittest.TestCase):
    def project(self, root: Path):
        root.mkdir(parents=True,exist_ok=True)
        (root/'export_presets.cfg').write_text('package/unique_name="com.dbrckk.jumpy"\n')
        return root

    def test_package_id_must_be_exact_and_unambiguous(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.project(root)
            self.assertEqual(qa.package_name(root),'com.dbrckk.jumpy')
            (root/'export_presets.cfg').write_text('package/unique_name="bad"\n')
            with self.assertRaisesRegex(StudioError,'package id'):
                qa.package_name(root)

    def test_apk_hash_mismatch_fails_before_adb(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.project(root); apk=root/'app.apk'; apk.write_bytes(b'x'*2000)
            with self.assertRaisesRegex(StudioError,'hash does not match'):
                qa.validate_debug_apk(root,apk,'0'*64,root/'out')

    @patch('godot_device_qa.shutil.which', return_value='/usr/bin/tool')
    @patch('godot_device_qa.subprocess.run')
    def test_success_keeps_app_offline_and_claims_no_journeys(self, run, which):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.project(root); apk=root/'app.apk'; apk.write_bytes(b'a'*2000)
            import hashlib
            digest=hashlib.sha256(apk.read_bytes()).hexdigest(); calls=[]
            def fake(args, **kwargs):
                calls.append(args)
                if args[-1:] == ['devices'] or (len(args)>=2 and args[1]=='devices'):
                    return subprocess.CompletedProcess(args,0,'List of devices attached\nemulator-5554\tdevice\n')
                if 'airplane_mode_on' in args and args[-2:] == ['airplane_mode_on','1']:
                    return subprocess.CompletedProcess(args,0,'')
                if 'airplane_mode_on' in args and args[-2:] != ['airplane_mode_on','1']:
                    return subprocess.CompletedProcess(args,0,'1\n')
                if 'screencap' in args:
                    handle=kwargs['stdout']; handle.write(b'p'*2000); handle.flush()
                    return subprocess.CompletedProcess(args,0,b'')
                return subprocess.CompletedProcess(args,0,'')
            run.side_effect=fake
            result=qa.validate_debug_apk(root,apk,digest,root/'out',sleeper=lambda _:None)
        self.assertTrue(result['passed'])
        self.assertEqual(result['network'],'airplane_mode')
        self.assertFalse(result['journeys_executed'])
        self.assertFalse(result['visual_reviewed'])
        self.assertTrue(any(any('AIRPLANE_MODE' in part for part in call) for call in calls))

    def test_safe_env_drops_ci_credentials(self):
        with patch.dict('os.environ',{'PATH':'/bin','HOME':'/tmp','GITHUB_TOKEN':'secret','STUDIO_GITHUB_TOKEN':'secret'},clear=True):
            env=qa._safe_env()
        self.assertEqual(env,{'PATH':'/bin','HOME':'/tmp'})


if __name__=='__main__': unittest.main()

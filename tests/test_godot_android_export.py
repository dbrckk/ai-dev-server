import hashlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from core import StudioError
import godot_android_export as gae


def archive_bytes():
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w') as z:
        z.writestr('templates/android_debug.apk',b'debug')
        z.writestr('templates/android_release.apk',b'release')
        z.writestr('templates/linux_debug.x86_64',b'ignored')
    return buf.getvalue()

class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self,*args): return False

class GodotAndroidExportTests(unittest.TestCase):
    def test_installs_only_verified_android_templates(self):
        data=archive_bytes()
        with tempfile.TemporaryDirectory() as td, patch.object(gae,'TEMPLATE_SHA256',hashlib.sha256(data).hexdigest()):
            target=gae.install_android_templates(Path(td), opener=lambda *a,**k:Response(data))
            self.assertEqual(sorted(p.name for p in target.iterdir()),['android_debug.apk','android_release.apk'])
    def test_wrong_template_digest_fails_closed(self):
        data=archive_bytes()
        with tempfile.TemporaryDirectory() as td, patch.object(gae,'TEMPLATE_SHA256','0'*64), self.assertRaises(StudioError):
            gae.install_android_templates(Path(td), opener=lambda *a,**k:Response(data))
    def test_requires_exactly_one_android_preset(self):
        self.assertEqual(gae._preset_name('[preset.0]\nname="Android"\nplatform="Android"\n'),'Android')
        for text in ['', '[preset.0]\nname="Linux"\nplatform="Linux/X11"\n', '[preset.0]\nname="A"\nplatform="Android"\n[preset.1]\nname="B"\nplatform="Android"\n']:
            with self.assertRaises(StudioError): gae._preset_name(text)
    def test_export_is_offline_and_source_is_not_mounted(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); project=root/'src'; project.mkdir(); (project/'project.godot').write_text('[application]\n'); (project/'export_presets.cfg').write_text('[preset.0]\nname="Android"\nplatform="Android"\n')
            binary=root/'godot'; binary.write_bytes(b'godot'); (root/'godot.sha256').write_text(hashlib.sha256(b'godot').hexdigest()); binary.chmod(0o755)
            templates=root/'templates'; templates.mkdir(); (templates/'android_debug.apk').write_bytes(b'd'); (templates/'android_release.apk').write_bytes(b'r')
            seen={}
            def runner(cmd,**kwargs):
                seen['cmd']=cmd
                out=Path(cmd[cmd.index('-v')+1]) if False else None
                host_out=next(x.split(':/out:rw')[0] for x in cmd if x.endswith(':/out:rw'))
                Path(host_out,'app-debug.apk').write_bytes(b'apk')
                return subprocess.CompletedProcess(cmd,0,stdout=b'')
            result=gae.export_debug_apk(project,binary,templates,runner=runner)
            self.assertTrue(result['passed']); self.assertIn('--network=none',seen['cmd'])
            self.assertFalse(any(str(project.resolve()) in x for x in seen['cmd']))
            self.assertFalse(result['release_signed'])

if __name__=='__main__': unittest.main()

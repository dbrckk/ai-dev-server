import hashlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from core import StudioError
import godot_release_artifact as gra


def valid_aab(path:Path):
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('BundleConfig.pb',b'cfg'); z.writestr('base/manifest/AndroidManifest.xml',b'manifest')

class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self,*args): return False

class GodotReleaseArtifactTests(unittest.TestCase):
    def project(self,root):
        root.mkdir(parents=True,exist_ok=True); (root/'project.godot').write_text('[application]\n')
        (root/'export_presets.cfg').write_text('[preset.0]\nname="Android"\nplatform="Android"\n[preset.0.options]\ngradle_build/use_gradle_build=true\ngradle_build/export_format=1\npackage/signed=true\n')
        return root

    def test_source_template_requires_verified_official_archive(self):
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z: z.writestr('templates/android_source.zip',b'source-template')
        data=buf.getvalue()
        with tempfile.TemporaryDirectory() as td, patch.object(gra,'TEMPLATE_SHA256',hashlib.sha256(data).hexdigest()):
            target=gra.install_source_template(Path(td),opener=lambda *a,**k:Response(data))
            self.assertEqual(target.read_bytes(),b'source-template')
        with tempfile.TemporaryDirectory() as td, patch.object(gra,'TEMPLATE_SHA256','0'*64):
            with self.assertRaises(StudioError): gra.install_source_template(Path(td),opener=lambda *a,**k:Response(data))

    def test_unsigned_build_is_offline_and_receives_no_signing_material(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); project=self.project(root/'project'); binary=root/'godot'; binary.write_bytes(b'godot'); binary.chmod(0o755)
            (root/'godot.sha256').write_text(hashlib.sha256(b'godot').hexdigest()); source=root/'android_source.zip'; source.write_bytes(b'source'); artifact=root/'out.aab'; seen={}
            def runner(cmd,**kwargs):
                seen['cmd']=cmd; seen['env']=kwargs.get('env',{})
                host_out=next(x.split(':/out:rw')[0] for x in cmd if isinstance(x,str) and x.endswith(':/out:rw'))
                valid_aab(Path(host_out)/'app-unsigned.aab')
                return subprocess.CompletedProcess(cmd,0,stdout=b'')
            result=gra.build_unsigned_aab(project,binary,source,artifact,runner=runner)
        self.assertTrue(result['passed']); self.assertEqual(result['network'],'none'); self.assertFalse(result['signing_material_exposed'])
        self.assertIn('--network=none',seen['cmd']); self.assertFalse(any('KEYSTORE' in k or 'PASSWORD' in k for k in seen['env']))
        self.assertFalse(any(str(project.resolve()) in str(x) for x in seen['cmd']))

    def test_signer_uses_password_environment_not_argv_and_only_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); unsigned=root/'u.aab'; signed=root/'s.aab'; key=root/'upload.keystore'; key.write_bytes(b'key'); valid_aab(unsigned); calls=[]
            def runner(cmd,**kwargs):
                calls.append((list(cmd),dict(kwargs.get('env',{}))))
                if cmd[0]=='jarsigner' and '-verify' not in cmd:
                    shutil_copy=__import__('shutil').copyfile; shutil_copy(unsigned,signed); return subprocess.CompletedProcess(cmd,0,stdout=b'signed')
                if cmd[0]=='jarsigner': return subprocess.CompletedProcess(cmd,0,stdout=b'jar verified.')
                return subprocess.CompletedProcess(cmd,0,stdout=('SHA256: '+':'.join(['AA']*32)).encode())
            result=gra.sign_aab(unsigned,signed,key,'upload','SecretPassword',runner=runner)
        self.assertTrue(result['passed']); self.assertEqual(result['signing_scope'],'artifact_only'); self.assertFalse(result['project_code_had_signing_material'])
        self.assertTrue(all('SecretPassword' not in ' '.join(call[0]) for call in calls))
        sign_call=calls[0]; self.assertIn('-storepass:env',sign_call[0]); self.assertEqual(sign_call[1]['STUDIO_AAB_STOREPASS'],'SecretPassword')

if __name__=='__main__': unittest.main()

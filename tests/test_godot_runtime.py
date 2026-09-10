import hashlib
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

import godot_runtime
from core import StudioError


class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()


def archive_bytes(payload=b'godot-binary'):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_STORED) as zf:
        zf.writestr(godot_runtime.GODOT_BINARY, payload)
    return buf.getvalue()


class GodotRuntimeTests(unittest.TestCase):
    def test_verified_archive_is_extracted_and_binary_gets_bound_digest(self):
        raw = archive_bytes()
        expected = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as tmp, patch.object(godot_runtime, 'GODOT_ARCHIVE_SHA256', expected):
            binary = godot_runtime.install(Path(tmp), opener=lambda request, timeout: Response(raw))
            self.assertEqual(binary.read_bytes(), b'godot-binary')
            self.assertEqual(binary.with_name(binary.name + '.sha256').read_text().strip(), hashlib.sha256(b'godot-binary').hexdigest())

    def test_wrong_release_digest_is_rejected(self):
        raw = archive_bytes()
        with tempfile.TemporaryDirectory() as tmp, patch.object(godot_runtime, 'GODOT_ARCHIVE_SHA256', '0' * 64):
            with self.assertRaisesRegex(StudioError, 'SHA-256 mismatch'):
                godot_runtime.install(Path(tmp), opener=lambda request, timeout: Response(raw))

    def test_binary_tampering_after_extraction_is_rejected(self):
        raw = archive_bytes()
        expected = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as tmp, patch.object(godot_runtime, 'GODOT_ARCHIVE_SHA256', expected):
            binary = godot_runtime.install(Path(tmp), opener=lambda request, timeout: Response(raw))
            binary.write_bytes(b'tampered')
            with self.assertRaisesRegex(StudioError, 'changed after verified extraction'):
                godot_runtime._trusted_binary_hash(binary)

    def test_docker_validation_is_offline_and_project_is_read_only(self):
        raw = archive_bytes()
        expected = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as tmp, patch.object(godot_runtime, 'GODOT_ARCHIVE_SHA256', expected):
            base = Path(tmp); project = base / 'project'; project.mkdir(); (project / 'project.godot').write_text('[application]\n')
            binary = godot_runtime.install(base / 'cache', opener=lambda request, timeout: Response(raw))
            command = godot_runtime.docker_command(project, binary, base / 'godot-cache')
            self.assertIn('--network=none', command)
            self.assertIn(str(project.resolve()) + ':/project:ro', command)
            self.assertIn(str(binary.resolve()) + ':/opt/godot:ro', command)
            self.assertIn('--cap-drop=ALL', command)
            self.assertIn('--security-opt=no-new-privileges', command)

    def test_host_environment_does_not_forward_credentials(self):
        with patch.dict(os.environ, {'PATH':'/bin','HOME':'/tmp','GH_TOKEN':'secret','STUDIO_API_KEY':'secret'}, clear=True):
            self.assertEqual(godot_runtime._host_env(), {'PATH':'/bin','HOME':'/tmp'})

    def test_blocking_godot_marker_fails_even_with_zero_exit_code(self):
        raw = archive_bytes(); expected = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as tmp, patch.object(godot_runtime, 'GODOT_ARCHIVE_SHA256', expected):
            base=Path(tmp); project=base/'project'; project.mkdir(); (project/'project.godot').write_text('[application]\n')
            binary=godot_runtime.install(base/'cache', opener=lambda request, timeout: Response(raw))
            def runner(command, **kwargs): return subprocess.CompletedProcess(command, 0, stdout=b'Parse Error: broken')
            result=godot_runtime.validate(project,binary,runner=runner)
            self.assertFalse(result['passed']); self.assertEqual(result['network'],'none'); self.assertEqual(result['project_mount'],'read_only')


if __name__ == '__main__': unittest.main()

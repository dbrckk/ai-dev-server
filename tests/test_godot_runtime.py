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


def project(root: Path) -> Path:
    p = root / 'project'; p.mkdir(); (p / 'project.godot').write_text('[application]\n')
    scripts = p / 'scripts'; scripts.mkdir(); (scripts / 'smoke.gd').write_text('extends Node\n')
    return p


class GodotRuntimeTests(unittest.TestCase):
    def test_verified_archive_is_extracted_and_binary_gets_bound_digest(self):
        raw = archive_bytes(); expected = hashlib.sha256(raw).hexdigest()
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
        raw = archive_bytes(); expected = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as tmp, patch.object(godot_runtime, 'GODOT_ARCHIVE_SHA256', expected):
            binary = godot_runtime.install(Path(tmp), opener=lambda request, timeout: Response(raw))
            binary.write_bytes(b'tampered')
            with self.assertRaisesRegex(StudioError, 'changed after verified extraction'):
                godot_runtime._trusted_binary_hash(binary)

    def test_docker_validation_is_offline_and_uses_only_ephemeral_copy(self):
        raw = archive_bytes(); expected = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as tmp, patch.object(godot_runtime, 'GODOT_ARCHIVE_SHA256', expected):
            base = Path(tmp); source = project(base); staged = base / 'staged'; staged.mkdir(); godot_runtime._copy_project(source, staged)
            binary = godot_runtime.install(base / 'cache', opener=lambda request, timeout: Response(raw))
            command = godot_runtime.docker_command(staged, binary)
            self.assertIn('--network=none', command)
            self.assertIn(str(staged.resolve()) + ':/project:rw', command)
            self.assertNotIn(str(source.resolve()) + ':/project:rw', command)
            self.assertIn(str(binary.resolve()) + ':/opt/godot:ro', command)
            self.assertIn('--cap-drop=ALL', command)
            self.assertIn('--security-opt=no-new-privileges', command)

    def test_source_project_is_not_mounted_or_mutated(self):
        raw = archive_bytes(); expected = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as tmp, patch.object(godot_runtime, 'GODOT_ARCHIVE_SHA256', expected):
            base = Path(tmp); source = project(base); binary = godot_runtime.install(base / 'cache', opener=lambda request, timeout: Response(raw))
            before = (source / 'scripts/smoke.gd').read_bytes(); captured = {}
            def runner(command, **kwargs):
                captured['command'] = command
                return subprocess.CompletedProcess(command, 0, stdout=b'Godot Engine')
            result = godot_runtime.validate(source, binary, runner=runner)
            self.assertEqual((source / 'scripts/smoke.gd').read_bytes(), before)
            self.assertFalse(any(str(source.resolve()) in arg for arg in captured['command']))
            self.assertEqual(result['source_project'], 'not_mounted')
            self.assertEqual(result['sandbox_project'], 'ephemeral_writable')

    def test_symlink_in_source_project_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); source = project(base); outside = base / 'outside'; outside.write_text('x')
            try:
                (source / 'scripts/link.gd').symlink_to(outside)
            except OSError:
                self.skipTest('symlink unavailable')
            staged = base / 'staged'; staged.mkdir()
            with self.assertRaisesRegex(StudioError, 'symlink rejected'):
                godot_runtime._copy_project(source, staged)

    def test_host_environment_does_not_forward_credentials(self):
        with patch.dict(os.environ, {'PATH':'/bin','HOME':'/tmp','GH_TOKEN':'secret','STUDIO_API_KEY':'secret'}, clear=True):
            self.assertEqual(godot_runtime._host_env(), {'PATH':'/bin','HOME':'/tmp'})

    def test_blocking_godot_marker_fails_even_with_zero_exit_code(self):
        raw = archive_bytes(); expected = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as tmp, patch.object(godot_runtime, 'GODOT_ARCHIVE_SHA256', expected):
            base=Path(tmp); source=project(base); binary=godot_runtime.install(base/'cache', opener=lambda request, timeout: Response(raw))
            def runner(command, **kwargs): return subprocess.CompletedProcess(command, 0, stdout=b'Parse Error: broken')
            result=godot_runtime.validate(source,binary,runner=runner)
            self.assertFalse(result['passed']); self.assertEqual(result['network'],'none')


if __name__ == '__main__': unittest.main()

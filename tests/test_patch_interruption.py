import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from core import apply_patch
from run import GitHub


class PatchInterruptionTests(unittest.TestCase):
    def test_cancelled_new_file_removes_created_directories(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            replace = os.replace
            def interrupt(src, dst):
                replace(src, dst)
                raise KeyboardInterrupt()
            with patch('core.os.replace', side_effect=interrupt), self.assertRaises(KeyboardInterrupt):
                apply_patch(root, {'files': [{'path': 'lib/new/app.dart', 'content': 'changed'}]})
            self.assertEqual(list(root.iterdir()), [])

    def test_interrupt_after_replacement_restores_original_and_propagates(self):
        for failure in (KeyboardInterrupt, SystemExit):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                (root / 'lib').mkdir()
                target = root / 'lib/app.dart'
                target.write_bytes(b'original\r\n')
                target.chmod(0o640)
                replace = os.replace
                calls = 0
                def interrupt(src, dst):
                    nonlocal calls
                    calls += 1
                    replace(src, dst)
                    if calls == 1:
                        raise failure()
                with patch('core.os.replace', side_effect=interrupt), self.assertRaises(failure):
                    apply_patch(root, {'files': [{'path': 'lib/app.dart', 'content': 'changed'}]})
                self.assertEqual(target.read_bytes(), b'original\r\n')
                self.assertEqual(target.stat().st_mode & 0o777, 0o640)
                self.assertFalse(list(root.glob('.__studio-patch-*')))

    def test_interruption_during_rollback_retains_backups(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'lib').mkdir()
            (root / 'lib/app.dart').write_text('original')
            replace = os.replace
            calls = 0
            def interrupt(src, dst):
                nonlocal calls
                calls += 1
                if calls == 1:
                    replace(src, dst)
                raise KeyboardInterrupt()
            with patch('core.os.replace', side_effect=interrupt), self.assertRaises(RuntimeError):
                apply_patch(root, {'files': [{'path': 'lib/app.dart', 'content': 'changed'}]})
            backups = list(root.glob('.__studio-patch-*/0.backup'))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), 'original')

    def test_abrupt_process_exit_blocks_reuse_and_publication(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'lib').mkdir()
            target = root / 'lib/app.dart'
            target.write_text('original')
            script = '''
import os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[2])
import core
replace = os.replace
def stop(src, dst):
    replace(src, dst)
    os._exit(73)
core.os.replace = stop
core.apply_patch(Path(sys.argv[1]), {'files': [{'path': 'lib/app.dart', 'content': 'changed'}]})
'''
            result = subprocess.run([sys.executable, '-c', script, d,
                str(Path(__file__).resolve().parents[1] / 'studio')], timeout=10)
            self.assertEqual(result.returncode, 73)
            self.assertEqual(target.read_text(), 'changed')
            with self.assertRaises(RuntimeError):
                apply_patch(root, {'files': [{'path': 'lib/app.dart', 'content': 'overwrite'}]})
            gh = GitHub.__new__(GitHub)
            gh.get = Mock(side_effect=AssertionError('remote read'))
            gh.call = Mock(side_effect=AssertionError('remote write'))
            with self.assertRaises(RuntimeError):
                gh.publish('studio/demo', None, root, {'status': 'blocked'})
            gh.get.assert_not_called()
            gh.call.assert_not_called()
            self.assertEqual(target.read_text(), 'changed')
            self.assertEqual(next(root.glob('.__studio-patch-*/0.backup')).read_text(), 'original')

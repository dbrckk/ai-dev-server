import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from core import StudioError
from godot_baseline import config_check, verify_archive, gate_ok

class GodotBaselineTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((Path(__file__).resolve().parents[1] /
            'control/existing-projects/jumpy.json').read_text())

    def test_reviewed_pinned_manifest(self):
        self.assertEqual(config_check(self.config)['engine'], 'godot')

    def test_mutable_or_unreviewed_target_rejected(self):
        for key, value in [('baseline_commit', 'main'), ('repository', 'other/project'),
                           ('engine_version', 'latest'), ('mode', 'write'), ('engine_sha256', '')]:
            c = copy.deepcopy(self.config)
            c[key] = value
            with self.subTest(key=key), self.assertRaises(StudioError):
                config_check(c)

    def test_download_integrity(self):
        data = b'fixture'
        verify_archive(data, hashlib.sha256(data).hexdigest())
        with self.assertRaises(StudioError):
            verify_archive(b'changed', hashlib.sha256(data).hexdigest())

    def test_engine_errors_fail_even_with_zero_exit(self):
        for log in ['SCRIPT ERROR: broken', 'Parse Error: bad', 'ERROR: failed']:
            self.assertFalse(gate_ok(0, log))

    def test_gameplay_requires_marker_and_success(self):
        self.assertFalse(gate_ok(0, '', 'JUMPY_BASELINE_PASS'))
        self.assertFalse(gate_ok(1, 'JUMPY_BASELINE_PASS', 'JUMPY_BASELINE_PASS'))
        self.assertTrue(gate_ok(0, 'JUMPY_BASELINE_PASS', 'JUMPY_BASELINE_PASS'))

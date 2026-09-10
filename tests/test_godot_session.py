from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

import godot_session
from core import StudioError


class GodotSessionTests(unittest.TestCase):
    def test_requires_existing_godot_project(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(StudioError, 'project.godot'):
                godot_session.GodotSandbox(Path(td)).create('x')

    def test_gate_preserves_non_claimed_journey_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / 'project.godot').write_text('[application]\n')
            fake = {'passed': True, 'exit_code': 0, 'output': 'ok', 'engine_version': '4.7.2-stable',
                    'archive_sha256': 'a' * 64, 'binary_sha256': 'b' * 64, 'network': 'none',
                    'source_project_immutable': True}
            with patch.object(godot_session, 'install', return_value=Path('/tmp/godot')), patch.object(godot_session, 'validate', return_value=fake):
                passed, logs = godot_session.GodotSandbox(root).gates('x', [{'id':'play'}])
            self.assertTrue(passed)
            self.assertFalse(logs[0]['journeys_executed'])
            self.assertTrue(logs[0]['source_project_immutable'])
            self.assertEqual(logs[0]['network'], 'none')


if __name__ == '__main__': unittest.main()

import base64
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

import godot_repository_probe
from core import StudioError


class FakeSandbox:
    def __init__(self, root): self.root = root
    def create(self, name): self.created = name
    def gates(self, name, journeys):
        return True, [{'exit_code':0,'engine_version':'4.7.2-stable','network':'none','source_project_immutable':True,'journeys_executed':False}]


def blob(text):
    raw = text.encode()
    return {'encoding':'base64','content':base64.b64encode(raw).decode()}, len(raw)


class GodotRepositoryProbeTests(unittest.TestCase):
    def test_requires_pinned_commit(self):
        with self.assertRaisesRegex(StudioError, 'full pinned commit'):
            godot_repository_probe.probe('dbrckk/Jumpy', 'main', fetch_json=lambda url: {})

    def test_imports_pinned_godot_tree_before_runtime(self):
        project_blob, project_size = blob('[application]\n')
        script_blob, script_size = blob('extends Node\n')
        tree = {'truncated':False,'tree':[
            {'path':'project.godot','type':'blob','mode':'100644','sha':'1'*40,'size':project_size},
            {'path':'scripts/main.gd','type':'blob','mode':'100644','sha':'2'*40,'size':script_size},
        ]}
        def fetch(url):
            if '/git/trees/' in url: return tree
            if url.endswith('/' + '1'*40): return project_blob
            if url.endswith('/' + '2'*40): return script_blob
            raise AssertionError(url)
        with patch.object(godot_repository_probe, 'GodotSandbox', FakeSandbox):
            result = godot_repository_probe.probe('dbrckk/Jumpy', 'f'*40, fetch_json=fetch)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['engine'], 'godot')
        self.assertEqual(result['imported_files'], 2)
        self.assertEqual(result['imported_bytes'], project_size + script_size)
        self.assertFalse(result['runtime']['journeys_executed'])


if __name__ == '__main__': unittest.main()

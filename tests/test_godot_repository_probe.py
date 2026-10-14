import base64
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
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

        # Extend the existing contract: the Actions token only reaches the
        # canonical GitHub API, with automatic credential redirects disabled.
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b'{}'
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'unit-test-token'}, clear=True), \
             patch('godot_repository_probe.urllib.request.build_opener') as make_opener:
            make_opener.return_value.open.return_value = response
            self.assertEqual(
                godot_repository_probe._get_json(
                    'https://api.github.com/repos/dbrckk/Jumpy/git/trees/' + 'f' * 40
                ),
                {},
            )
            request = make_opener.return_value.open.call_args.args[0]
            self.assertEqual(request.get_header('Authorization'), 'Bearer unit-test-token')
            self.assertEqual(request.get_header('Accept'), 'application/vnd.github+json')
            self.assertIsInstance(make_opener.call_args.args[0], godot_repository_probe.NoRedirect)
            with self.assertRaisesRegex(StudioError, 'GitHub API URL is invalid'):
                godot_repository_probe._get_json('https://api.github.com.evil.invalid/repos/x/y')
            self.assertEqual(make_opener.return_value.open.call_count, 1)

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

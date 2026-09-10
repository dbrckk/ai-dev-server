import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from core import StudioError
from engine_entry import detect_engine

SHA = 'a' * 40
CHECKPOINT = 'b' * 40


class FakeGitHub:
    def __init__(self, size=1, default_paths=None, checkpoint_paths=None):
        self.size = size
        self.default_paths = default_paths if default_paths is not None else ['pubspec.yaml']
        self.checkpoint_paths = checkpoint_paths
        self.calls = []
    def get(self, path):
        self.calls.append(path)
        if path == '':
            return {'size': self.size, 'archived': False, 'default_branch': 'main'}
        if path == '/git/matching-refs/heads/studio/demo-v1':
            return [] if self.checkpoint_paths is None else [{'ref':'refs/heads/studio/demo-v1','object':{'sha':CHECKPOINT}}]
        if path == '/branches/main':
            return {'commit': {'sha': SHA}}
        if path == '/git/trees/' + SHA + '?recursive=1':
            return {'truncated': False, 'tree': [{'type':'blob','path':p} for p in self.default_paths]}
        if path == '/git/trees/' + CHECKPOINT + '?recursive=1':
            return {'truncated': False, 'tree': [{'type':'blob','path':p} for p in self.checkpoint_paths]}
        raise AssertionError(path)

REQ = {'id':'demo-v1'}


class EngineEntryTests(unittest.TestCase):
    def test_empty_repository_keeps_flutter_bootstrap(self):
        gh = FakeGitHub(size=0)
        self.assertEqual(detect_engine(REQ, gh), 'flutter')

    def test_docs_only_repository_keeps_flutter_bootstrap(self):
        gh = FakeGitHub(default_paths=['README.md', '.gitignore'])
        self.assertEqual(detect_engine(REQ, gh), 'flutter')

    def test_existing_flutter_marker(self):
        self.assertEqual(detect_engine(REQ, FakeGitHub(default_paths=['pubspec.yaml','lib/app.dart'])), 'flutter')

    def test_existing_godot_marker(self):
        self.assertEqual(detect_engine(REQ, FakeGitHub(default_paths=['project.godot','scripts/main.gd'])), 'godot')

    def test_ambiguous_markers_fail_closed(self):
        with self.assertRaisesRegex(StudioError, 'Ambiguous'):
            detect_engine(REQ, FakeGitHub(default_paths=['pubspec.yaml','project.godot']))

    def test_checkpoint_branch_is_authoritative_for_resume(self):
        gh = FakeGitHub(default_paths=['pubspec.yaml'], checkpoint_paths=['project.godot','scripts/main.gd'])
        self.assertEqual(detect_engine(REQ, gh), 'godot')
        self.assertNotIn('/branches/main', gh.calls)

    def test_unknown_existing_engine_fails_closed(self):
        with self.assertRaisesRegex(StudioError, 'Unsupported project engine'):
            detect_engine(REQ, FakeGitHub(default_paths=['package.json','src/index.js']))


if __name__ == '__main__':
    unittest.main()

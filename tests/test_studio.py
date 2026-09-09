import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from core import StudioError, API, APIError, Model, Sandbox, allowed, apply_patch, patch_check, request_check, verdict
from run import execute, GitHub
from queue import matrix

REQUEST = {'id': 'demo-v1', 'target_repo': 'owner/mobile', 'app_name': 'demo_app',
           'brief': 'Create a complete working focus timer mobile app.', 'enabled': True,
           'max_rounds': 3, 'max_calls': 12, 'max_cycles': 5}
JOURNEYS = [{'id': 'settings', 'steps': [{'action': 'tap', 'key': 'settings_button'}, {'action': 'expect_text', 'value': 'Settings'}]}]
PATCH = {'files': [{'path': 'lib/app.dart', 'content': 'source'}, {'path': 'test/app_test.dart', 'content': 'test'}]}

class FakeGitHub:
    def __init__(self):
        self.state = None
        self.files = {}
        self.published = []
    def restore(self, branch, root):
        for p, content in self.files.items():
            apply_patch(root, {'files': [{'path': p, 'content': content}]})
        return copy.deepcopy(self.state), 'base'
    def publish(self, branch, parent, root, state):
        self.state = copy.deepcopy(state)
        self.files = {p.relative_to(root).as_posix(): p.read_text() for p in root.rglob('*') if p.is_file() and allowed(p.relative_to(root).as_posix())}
        self.published.append(copy.deepcopy(state))
        return 'commit'

class FakeModel:
    vision = 'vision-model'
    calls = 0
    def __init__(self, limit):
        self.calls = 0
    def ask(self, role, context, screenshots=()):
        self.calls += 1
        if role == 'implementation':
            return PATCH
        if role in ('review', 'visual'):
            return {'passed': True, 'blockers': []}
        return {'acceptance': ['timer works'], 'journeys': copy.deepcopy(JOURNEYS)}

class FakeSandbox:
    def __init__(self, root):
        self.root = root
        self.attempt = 0
    def create(self, name):
        (self.root / 'test').mkdir(exist_ok=True)
    def gates(self, name, journeys):
        self.attempt += 1
        p = self.root / 'build/app/outputs/flutter-apk/app-debug.apk'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b'actual fixture apk')
        d = self.root / 'test/goldens'
        d.mkdir(parents=True, exist_ok=True)
        for screen in ['initial'] + [j['id'] for j in journeys]:
            for i in range(4):
                (d / f'{screen}--{i}.png').write_bytes(b'fixture')
        return True, [{'exit_code': 0}]

class StudioTests(unittest.TestCase):
    def test_request_defaults(self):
        req = {k: v for k, v in REQUEST.items() if not k.startswith('max_')}
        self.assertEqual(request_check(req)['max_cycles'], 5)
    def test_request_rejects_injection_and_bad_types(self):
        for key, val in [('target_repo', 'x/y; echo secret'), ('id', '../x'), ('app_name', '-x'), ('max_calls', True), ('enabled', 'true'), ('brief', 'x')]:
            with self.subTest(key=key), self.assertRaises(StudioError):
                request_check(dict(REQUEST, **{key: val}))
    def test_paths(self):
        for p in ['../x', '/tmp/x', 'lib/../x.dart', 'lib//x.dart', '.github/workflows/x.yml', 'test/__studio_visual_test.dart', 'lib\\x.dart', 'android/build.gradle', 'lib/.env.dart']:
            self.assertFalse(allowed(p), p)
        self.assertTrue(allowed('lib/screens/home.dart'))
    def test_patch_atomic_validation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaises(StudioError):
                apply_patch(root, {'files': [PATCH['files'][0], {'path': '../escape', 'content': 'x'}]})
            self.assertFalse(list(root.iterdir()))
    def test_duplicate_and_secrets(self):
        for files in [[PATCH['files'][0]] * 2, [{'path': 'lib/a.dart', 'content': 'ghp_abcd'}]]:
            with self.assertRaises(StudioError):
                patch_check({'files': files})
    def test_patch_replacement_failure_restores_bytes_mode_and_directories(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'lib').mkdir()
            source = root / 'lib/app.dart'
            source.write_bytes(b'original\r\n')
            source.chmod(0o640)
            replace = os.replace
            count = 0
            def fail_third(src, dst):
                nonlocal count
                count += 1
                if count == 3:
                    raise OSError('disk failure')
                return replace(src, dst)
            value = {'files': [PATCH['files'][0],
                {'path': 'lib/new/created.dart', 'content': 'new'},
                {'path': 'test/failure.dart', 'content': 'fail'}]}
            with patch('core.os.replace', side_effect=fail_third), self.assertRaises(StudioError):
                apply_patch(root, value)
            self.assertEqual(source.read_bytes(), b'original\r\n')
            self.assertEqual(source.stat().st_mode & 0o777, 0o640)
            self.assertEqual(sorted(p.relative_to(root).as_posix() for p in root.rglob('*')),
                             ['lib', 'lib/app.dart'])
    def test_patch_staging_failure_never_replaces_source(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            apply_patch(root, PATCH)
            with patch('core.shutil.copy2', side_effect=OSError('disk full')), self.assertRaises(StudioError):
                apply_patch(root, {'files': [{'path': 'lib/app.dart', 'content': 'replacement'}]})
            self.assertEqual((root / 'lib/app.dart').read_text(), 'source')
            self.assertFalse(list(root.glob('.__studio-patch-*')))
    def test_patch_failed_rollback_is_fatal_and_retains_backup(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            apply_patch(root, PATCH)
            replace = os.replace
            calls = 0
            def fail_after_first(src, dst):
                nonlocal calls
                calls += 1
                if calls > 1:
                    raise OSError('persistent failure')
                return replace(src, dst)
            with patch('core.os.replace', side_effect=fail_after_first), self.assertRaises(RuntimeError):
                apply_patch(root, PATCH)
            recovery = list(root.glob('.__studio-patch-*'))
            self.assertEqual(len(recovery), 1)
            self.assertEqual((recovery[0] / '0.backup').read_text(), 'source')
            manifest = json.loads((recovery[0] / 'manifest.json').read_text())
            self.assertEqual(manifest['files'][0],
                {'path': 'lib/app.dart', 'backup': '0.backup', 'existed': True})
    def test_patch_utf8_success_preserves_existing_mode(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'new-root'
            apply_patch(root, PATCH)
            source = root / 'lib/app.dart'
            source.chmod(0o640)
            apply_patch(root, {'files': [{'path': 'lib/app.dart', 'content': 'été ☀'}]})
            self.assertEqual(source.read_bytes(), 'été ☀'.encode('utf-8'))
            self.assertEqual(source.stat().st_mode & 0o777, 0o640)
            self.assertFalse(list(root.glob('.__studio-patch-*')))
    def test_patch_filesystem_conflicts_leave_existing_source_unchanged(self):
        for conflict in ('directory', 'parent_file', 'batch_parent', 'unicode'):
            with self.subTest(conflict=conflict), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                (root / 'lib').mkdir()
                source = root / 'lib/app.dart'
                source.write_text('original')
                files = [{'path': 'lib/app.dart', 'content': 'replacement'}]
                if conflict == 'directory':
                    (root / 'lib/conflict.dart').mkdir()
                    files.append({'path': 'lib/conflict.dart', 'content': 'x'})
                elif conflict == 'parent_file':
                    (root / 'lib/parent').write_text('original parent')
                    files.append({'path': 'lib/parent/child.dart', 'content': 'x'})
                elif conflict == 'batch_parent':
                    files.extend([{'path': 'lib/new.dart', 'content': 'x'},
                                  {'path': 'lib/new.dart/child.dart', 'content': 'y'}])
                else:
                    files.append({'path': 'lib/invalid.dart', 'content': '\ud800'})
                with self.assertRaises(StudioError):
                    apply_patch(root, {'files': files})
                self.assertEqual(source.read_text(), 'original')
                self.assertFalse((root / 'lib/new.dart').exists())
    def test_paths_reject_control_characters_and_surrogates(self):
        for char in ('\x00', '\n', '\r', '\t', '\x7f', '\ud800'):
            self.assertFalse(allowed('lib/a' + char + '.dart'))
    def test_symlink(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
            root = Path(d)
            (root / 'lib').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(StudioError):
                apply_patch(root, PATCH)
            self.assertFalse(list(Path(outside).iterdir()))
    def test_verdict_fail_closed(self):
        for v in [{'passed': True, 'blockers': ['bad']}, {'passed': False, 'blockers': []}, {'passed': 'true', 'blockers': []}, {'passed': True}]:
            with self.assertRaises(StudioError):
                verdict(v)
    def test_http_endpoint(self):
        for url in ['http://example.com', 'https://user:key@example.com', 'https://example.com?key=x']:
            with self.assertRaises(StudioError):
                API(url, 'key')
    def run_fixture(self, model=FakeModel, sandbox=FakeSandbox, gh=None):
        gh = gh or FakeGitHub()
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        state = execute(copy.deepcopy(REQUEST), root / 'work', root / 'out', gh, model, sandbox)
        return state, root, gh
    def test_full_pipeline_and_artifact(self):
        state, root, gh = self.run_fixture()
        self.assertEqual(state['status'], 'validated_preview')
        self.assertEqual(state['release_status'], 'not_store_ready')
        self.assertTrue((root / 'out/app-debug.apk').exists())
        self.assertEqual(len(list((root / 'out').glob('*.png'))), 8)
    def test_repair_loop(self):
        class RepairSandbox(FakeSandbox):
            def gates(self, name, journeys):
                passed, logs = super().gates(name, journeys)
                return self.attempt >= 2, logs
        state, _, _ = self.run_fixture(sandbox=RepairSandbox)
        self.assertEqual(state['rounds'], 2)
    def test_no_vision_is_not_completed(self):
        class NoVision(FakeModel):
            vision = ''
        state, root, _ = self.run_fixture(model=NoVision)
        self.assertEqual(state['status'], 'awaiting_visual_review')
        self.assertTrue((root / 'out/app-debug.apk').exists())
    def test_failed_build_does_not_export_stale_apk(self):
        class Failed(FakeSandbox):
            def gates(self, name, journeys):
                super().gates(name, journeys)
                return False, [{'exit_code': 1}]
        state, root, _ = self.run_fixture(sandbox=Failed)
        self.assertEqual(state['status'], 'repair_needed')
        self.assertFalse((root / 'out/app-debug.apk').exists())
    def test_visual_rejection_repairs(self):
        class Reject(FakeModel):
            def ask(self, role, context, screenshots=()):
                r = super().ask(role, context, screenshots)
                return {'passed': False, 'blockers': ['clipping']} if role == 'visual' else r
        state, root, _ = self.run_fixture(model=Reject)
        self.assertEqual(state['status'], 'repair_needed')
        self.assertFalse((root / 'out/app-debug.apk').exists())
    def test_provider_error_checkpoints(self):
        class Broken(FakeModel):
            def ask(self, role, context, screenshots=()):
                raise StudioError('Provider unavailable')
        state, _, gh = self.run_fixture(model=Broken)
        self.assertEqual(state['status'], 'blocked')
        self.assertTrue(gh.published)
    def test_fatal_patch_recovery_never_publishes_checkpoint(self):
        gh = FakeGitHub()
        prior_checkpoints = []
        def fail_patch(*args):
            prior_checkpoints.extend(copy.deepcopy(gh.published))
            raise RuntimeError('Patch rollback incomplete')
        with patch('run.apply_patch', side_effect=fail_patch):
            with self.assertRaises(RuntimeError):
                self.run_fixture(gh=gh)
        self.assertEqual(gh.published, prior_checkpoints)
    def test_completed_resume_skips_model_and_build(self):
        state, _, gh = self.run_fixture()
        def forbidden(*args):
            self.fail('Completed run must not start model or sandbox')
        resumed, _, _ = self.run_fixture(model=forbidden, sandbox=forbidden, gh=gh)
        self.assertEqual(resumed['status'], 'validated_preview')
    def test_old_validation_contract_is_revalidated(self):
        _, _, gh = self.run_fixture()
        gh.state.pop('validation_contract')
        previous_rounds = gh.state['rounds']
        state, _, _ = self.run_fixture(gh=gh)
        self.assertEqual(state['status'], 'validated_preview')
        self.assertEqual(state['validation_contract'], 2)
        self.assertEqual(state['rounds'], previous_rounds + 1)
    def test_changed_brief_rejected(self):
        _, _, gh = self.run_fixture()
        gh.state['request_hash'] = 'changed'
        with self.assertRaises(StudioError):
            self.run_fixture(gh=gh)
    def test_total_cycles_are_bounded(self):
        _, _, gh = self.run_fixture()
        gh.state.update(status='repair_needed', cycles=5)
        def forbidden(*args):
            self.fail('Cycle budget exhausted')
        state, _, _ = self.run_fixture(model=forbidden, sandbox=forbidden, gh=gh)
        self.assertEqual(state['cycles'], 5)
    def test_queue_duplicate_targets(self):
        with tempfile.TemporaryDirectory() as d:
            for i in range(2):
                (Path(d) / f'{i}.json').write_text(json.dumps(dict(REQUEST, id=f'demo-{i}')))
            with self.assertRaises(StudioError):
                matrix(d)
    def test_empty_repository_initialized_through_contents(self):
        class Empty(GitHub):
            def __init__(self):
                self.repo = '/repos/owner/mobile'
                self.writes = []
            def get(self, path):
                if path == '':
                    return {'size': 0}
                raise APIError(409)
            def call(self, method, path, data=None):
                self.writes.append((method, path))
                return {'commit': {'sha': 'seed'}}
        gh = Empty()
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(gh.restore('studio/demo', Path(d)), (None, 'seed'))
        self.assertEqual(gh.writes, [('PUT', '/repos/owner/mobile/contents/README.md')])
    def test_repository_access_error_never_initializes(self):
        class Denied(GitHub):
            def __init__(self):
                self.repo = '/repos/owner/mobile'
            def get(self, path):
                if path == '':
                    return {'size': 0}
                raise APIError(403)
            def call(self, *args):
                raise AssertionError('Must not mutate inaccessible repository')
        with tempfile.TemporaryDirectory() as d, self.assertRaises(APIError):
            Denied().restore('studio/demo', Path(d))
    def test_disabled_request_no_access(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(execute(dict(REQUEST, enabled=False), Path(d), Path(d)), {'status': 'disabled'})
    def test_qa_supplies_missing_implementation_tests(self):
        class QA(FakeModel):
            def ask(self, role, context, screenshots=()):
                if role == 'implementation':
                    return {'files': [PATCH['files'][0]]}
                if role == 'tests':
                    return {'files': [PATCH['files'][1]]}
                return super().ask(role, context, screenshots)
        state, _, _ = self.run_fixture(model=QA)
        self.assertEqual(state['status'], 'validated_preview')
    def test_missing_tests_fails(self):
        class NoTests(FakeModel):
            def ask(self, role, context, screenshots=()):
                if role == 'implementation':
                    return {'files': [PATCH['files'][0]]}
                return super().ask(role, context, screenshots)
        state, _, _ = self.run_fixture(model=NoTests)
        self.assertEqual(state['status'], 'blocked')

if __name__ == '__main__':
    unittest.main()

import hashlib
import json
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_persist import PersistenceError, persist
from orchestrator import _run_adaptation_persistence

BASELINE = 'a' * 40
CANDIDATE_SHA = 'b' * 40
CANDIDATE = 'candidate-12345678'
GAP = 'future_capability_qa'


class EvolutionPersistTests(unittest.TestCase):
    def fixture(self, root):
        candidate_files = {
            'studio/future_capability_stage.py': 'stage-fixture',
            'studio/future_capability_qa.py': 'implementation-fixture',
            'tests/test_future_capability_qa.py': 'tests-fixture',
            'tests/benchmarks/future_capability_qa.json': 'benchmark-fixture',
        }
        for rel, content in candidate_files.items():
            path = root / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content)
        registry = root / 'control/promoted_stages.json'; registry.parent.mkdir(parents=True, exist_ok=True)
        registry.write_text(json.dumps({'version': 1, 'stages': {GAP: {
            'script': 'studio/future_capability_stage.py', 'candidate_id': CANDIDATE,
            'baseline_sha': BASELINE, 'candidate_sha': CANDIDATE_SHA}}}))
        rollback = root / 'control/evolution_rollbacks' / (CANDIDATE + '.json'); rollback.parent.mkdir(parents=True, exist_ok=True)
        rollback.write_text(json.dumps({'version': 2, 'candidate_id': CANDIDATE, 'gap': GAP,
            'baseline_sha': BASELINE, 'candidate_sha': CANDIDATE_SHA,
            'created_paths': sorted(candidate_files),
            'created_sha256': {rel: hashlib.sha256(content.encode()).hexdigest() for rel, content in candidate_files.items()},
            'registry_before': {'version': 1, 'stages': {}}, 'registry_sha256_before': '0' * 64}))
        return {'status': 'promoted', 'candidate_id': CANDIDATE, 'gap': GAP, 'candidate_sha': CANDIDATE_SHA}

    def test_existing_identical_branch_and_pr_are_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); applied = self.fixture(root); blob_index = {'value': 0}; methods = []
            def fake_request(url, token, method='GET', payload=None, allow_404=False):
                methods.append((url, method))
                if url.endswith('/git/commits/' + BASELINE): return {'tree': {'sha': 'base-tree'}}
                if url.endswith('/git/blobs'):
                    blob_index['value'] += 1; return {'sha': 'blob-' + str(blob_index['value'])}
                if url.endswith('/git/trees'): return {'sha': 'candidate-tree'}
                if '/git/ref/heads/' in url: return {'object': {'sha': 'existing-commit'}}
                if url.endswith('/git/commits/existing-commit'): return {'tree': {'sha': 'candidate-tree'}, 'parents': [{'sha': BASELINE}]}
                if '/pulls?' in url: return [{'number': 17, 'head': {'sha': 'existing-commit'}}]
                raise AssertionError(url)
            with patch('evolution_persist._request', side_effect=fake_request):
                result = persist(root, applied, 'token', 'owner/repo', BASELINE)
            self.assertEqual(result['status'], 'already_persisted'); self.assertEqual(result['pull_request'], 17)
            self.assertFalse(any(url.endswith('/git/commits') and method == 'POST' for url, method in methods))
            self.assertFalse(any(url.endswith('/git/refs') and method == 'POST' for url, method in methods))

    def test_existing_branch_with_different_tree_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); applied = self.fixture(root); blob_index = {'value': 0}
            def fake_request(url, token, method='GET', payload=None, allow_404=False):
                if url.endswith('/git/commits/' + BASELINE): return {'tree': {'sha': 'base-tree'}}
                if url.endswith('/git/blobs'):
                    blob_index['value'] += 1; return {'sha': 'blob-' + str(blob_index['value'])}
                if url.endswith('/git/trees'): return {'sha': 'candidate-tree'}
                if '/git/ref/heads/' in url: return {'object': {'sha': 'existing-commit'}}
                if url.endswith('/git/commits/existing-commit'): return {'tree': {'sha': 'different-tree'}, 'parents': [{'sha': BASELINE}]}
                raise AssertionError(url)
            with patch('evolution_persist._request', side_effect=fake_request):
                with self.assertRaisesRegex(PersistenceError, 'different content'): persist(root, applied, 'token', 'owner/repo', BASELINE)

    def test_modified_promoted_file_is_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); applied = self.fixture(root)
            (root / 'studio/future_capability_qa.py').write_text('tampered')
            with patch('evolution_persist._request') as request:
                with self.assertRaisesRegex(PersistenceError, 'changed after approval'): persist(root, applied, 'token', 'owner/repo', BASELINE)
            request.assert_not_called()

    def test_github_orchestrator_requires_persistence_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp); (out / 'evolution-applied.json').write_text(json.dumps({'status': 'promoted', 'candidate_id': CANDIDATE, 'gap': GAP, 'candidate_sha': CANDIDATE_SHA}))
            calls = []
            def runner(args, timeout):
                calls.append(args); (out / 'evolution-persisted.json').write_text(json.dumps({'status': 'promotion_persisted', 'candidate_id': CANDIDATE, 'gap': GAP, 'pull_request': 17})); return subprocess.CompletedProcess(args, 0)
            with patch.dict('os.environ', {'STUDIO_CI_PROVIDER': 'github'}, clear=True): status = _run_adaptation_persistence(out, 100, runner, lambda: 0)
            self.assertEqual(status, 'persisted'); self.assertTrue(any('studio/evolution_persist.py' in call for call in calls))

    def test_non_github_provider_does_not_attempt_github_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = []
            with patch.dict('os.environ', {'STUDIO_CI_PROVIDER': 'circleci'}, clear=True): status = _run_adaptation_persistence(Path(tmp), 100, lambda args, timeout: calls.append(args), lambda: 0)
            self.assertEqual(status, 'not_applicable'); self.assertEqual(calls, [])


if __name__ == '__main__': unittest.main()

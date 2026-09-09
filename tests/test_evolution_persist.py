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
CANDIDATE = 'candidate-12345678'
GAP = 'future_capability_qa'


class EvolutionPersistTests(unittest.TestCase):
    def fixture(self, root):
        files = [
            root / 'control/promoted_stages.json',
            root / 'control/evolution_rollbacks' / (CANDIDATE + '.json'),
            root / 'studio/future_capability_stage.py',
            root / 'studio/future_capability_qa.py',
            root / 'tests/test_future_capability_qa.py',
            root / 'tests/benchmarks/future_capability_qa.json',
        ]
        for index, path in enumerate(files):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('fixture-' + str(index))
        return {'status': 'promoted', 'candidate_id': CANDIDATE, 'gap': GAP}

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
                if url.endswith('/git/commits/existing-commit'):
                    return {'tree': {'sha': 'candidate-tree'}, 'parents': [{'sha': BASELINE}]}
                if '/pulls?' in url: return [{'number': 17, 'head': {'sha': 'existing-commit'}}]
                raise AssertionError(url)
            with patch('evolution_persist._request', side_effect=fake_request):
                result = persist(root, applied, 'token', 'owner/repo', BASELINE)
            self.assertEqual(result['status'], 'already_persisted')
            self.assertEqual(result['pull_request'], 17)
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
                if url.endswith('/git/commits/existing-commit'):
                    return {'tree': {'sha': 'different-tree'}, 'parents': [{'sha': BASELINE}]}
                raise AssertionError(url)
            with patch('evolution_persist._request', side_effect=fake_request):
                with self.assertRaisesRegex(PersistenceError, 'different content'):
                    persist(root, applied, 'token', 'owner/repo', BASELINE)

    def test_github_orchestrator_requires_persistence_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp); (out / 'evolution-applied.json').write_text(json.dumps({
                'status': 'promoted', 'candidate_id': CANDIDATE, 'gap': GAP}))
            calls = []
            def runner(args, timeout):
                calls.append(args)
                (out / 'evolution-persisted.json').write_text(json.dumps({
                    'status': 'promotion_persisted', 'candidate_id': CANDIDATE, 'gap': GAP,
                    'pull_request': 17}))
                return subprocess.CompletedProcess(args, 0)
            with patch.dict('os.environ', {'STUDIO_CI_PROVIDER': 'github'}, clear=True):
                status = _run_adaptation_persistence(out, 100, runner, lambda: 0)
            self.assertEqual(status, 'persisted')
            self.assertTrue(any('studio/evolution_persist.py' in call for call in calls))

    def test_non_github_provider_does_not_attempt_github_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = []
            with patch.dict('os.environ', {'STUDIO_CI_PROVIDER': 'circleci'}, clear=True):
                status = _run_adaptation_persistence(Path(tmp), 100, lambda args, timeout: calls.append(args), lambda: 0)
            self.assertEqual(status, 'not_applicable')
            self.assertEqual(calls, [])


if __name__ == '__main__':
    unittest.main()

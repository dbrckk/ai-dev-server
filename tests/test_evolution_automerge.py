from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_automerge import AutoMergeError, attempt
from evolution_candidate import expected_paths

CANDIDATE = 'future-capability-qa-123456789abc'
GAP = 'future_capability_qa'
HEAD = 'b' * 40
BRANCH = 'evolution/promote-future-capability-qa-abcdef123456'


def order():
    return {'status': 'candidate_planned', 'candidate_id': CANDIDATE,
            'primary_gap': {'value': GAP}, 'baseline_sha': 'a' * 40}


def pending():
    return {'status': 'promotion_pending_merge', 'candidate_id': CANDIDATE, 'gap': GAP,
            'branch': BRANCH, 'commit_sha': HEAD, 'pull_request': 12}


def files(extra=None):
    names = set(expected_paths(GAP).values()) | {
        'control/promoted_stages.json', 'control/evolution_rollbacks/' + CANDIDATE + '.json'}
    if extra: names.add(extra)
    return [{'filename': name, 'status': 'added' if name != 'control/promoted_stages.json' else 'modified'} for name in sorted(names)]


class EvolutionAutoMergeTests(unittest.TestCase):
    def test_waits_until_both_required_checks_exist(self):
        def request(url, token, method='GET', payload=None, allow_404=False):
            if url.endswith('/pulls/12'): return {'state': 'open', 'draft': False, 'base': {'ref': 'main'}, 'head': {'ref': BRANCH, 'sha': HEAD}}
            if '/pulls/12/files?' in url: return files()
            if '/check-runs?' in url: return {'check_runs': [{'name': 'validate', 'status': 'completed', 'conclusion': 'success'}]}
            raise AssertionError(url)
        with patch('evolution_automerge.check_pending', return_value=pending()), patch('evolution_automerge._request', side_effect=request):
            result = attempt(order(), 'token', 'owner/repo')
        self.assertEqual(result['status'], 'awaiting_required_checks')
        self.assertEqual(result['missing_checks'], ['mobile-smoke'])

    def test_extra_file_blocks_merge_before_checks(self):
        def request(url, token, method='GET', payload=None, allow_404=False):
            if url.endswith('/pulls/12'): return {'state': 'open', 'draft': False, 'base': {'ref': 'main'}, 'head': {'ref': BRANCH, 'sha': HEAD}}
            if '/pulls/12/files?' in url: return files('studio/orchestrator.py')
            raise AssertionError(url)
        with patch('evolution_automerge.check_pending', return_value=pending()), patch('evolution_automerge._request', side_effect=request):
            with self.assertRaisesRegex(AutoMergeError, 'file scope changed'):
                attempt(order(), 'token', 'owner/repo')

    def test_failed_required_check_blocks_merge(self):
        def request(url, token, method='GET', payload=None, allow_404=False):
            if url.endswith('/pulls/12'): return {'state': 'open', 'draft': False, 'base': {'ref': 'main'}, 'head': {'ref': BRANCH, 'sha': HEAD}}
            if '/pulls/12/files?' in url: return files()
            if '/check-runs?' in url: return {'check_runs': [
                {'name': 'validate', 'status': 'completed', 'conclusion': 'success'},
                {'name': 'mobile-smoke', 'status': 'completed', 'conclusion': 'failure'}]}
            raise AssertionError(url)
        with patch('evolution_automerge.check_pending', return_value=pending()), patch('evolution_automerge._request', side_effect=request):
            with self.assertRaisesRegex(AutoMergeError, 'Required promotion check failed'):
                attempt(order(), 'token', 'owner/repo')

    def test_clean_pr_with_two_green_checks_merges(self):
        calls = []
        def request(url, token, method='GET', payload=None, allow_404=False):
            calls.append((url, method, payload))
            if url.endswith('/pulls/12'):
                return {'state': 'open', 'draft': False, 'mergeable': True, 'mergeable_state': 'clean',
                        'base': {'ref': 'main'}, 'head': {'ref': BRANCH, 'sha': HEAD}}
            if '/pulls/12/files?' in url: return files()
            if '/check-runs?' in url: return {'check_runs': [
                {'name': 'validate', 'status': 'completed', 'conclusion': 'success'},
                {'name': 'mobile-smoke', 'status': 'completed', 'conclusion': 'success'}]}
            if url.endswith('/pulls/12/merge') and method == 'PUT': return {'merged': True, 'sha': 'c' * 40}
            raise AssertionError(url)
        with patch('evolution_automerge.check_pending', return_value=pending()), patch('evolution_automerge._request', side_effect=request):
            result = attempt(order(), 'token', 'owner/repo')
        self.assertEqual(result['status'], 'promotion_merged')
        self.assertEqual(result['merge_sha'], 'c' * 40)
        self.assertTrue(any(url.endswith('/pulls/12/merge') and method == 'PUT' for url, method, _ in calls))


if __name__ == '__main__': unittest.main()

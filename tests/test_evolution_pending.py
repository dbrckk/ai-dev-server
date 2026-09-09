import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_pending import check
from orchestrator import _run_adaptation_pending

CANDIDATE = 'future-capability-qa-123456789abc'
GAP = 'future_capability_qa'
BASELINE = 'a' * 40
COMMIT = 'b' * 40


def order():
    return {'status': 'candidate_planned', 'candidate_id': CANDIDATE,
            'baseline_sha': BASELINE, 'primary_gap': {'value': GAP}}


class EvolutionPendingTests(unittest.TestCase):
    def test_no_branch_allows_new_evolution(self):
        with patch('evolution_pending._request', return_value=None):
            result = check(order(), 'token', 'owner/repo')
        self.assertEqual(result['status'], 'no_pending_promotion')

    def test_open_pr_blocks_regeneration(self):
        def request(url, token, method='GET', payload=None, allow_404=False):
            if '/git/ref/heads/' in url: return {'object': {'sha': COMMIT}}
            if '/pulls?' in url: return [{'number': 9, 'state': 'open', 'merged_at': None, 'head': {'sha': COMMIT}}]
            raise AssertionError(url)
        with patch('evolution_pending._request', side_effect=request):
            result = check(order(), 'token', 'owner/repo')
        self.assertEqual(result['status'], 'promotion_pending_merge')
        self.assertEqual(result['pull_request'], 9)

    def test_merged_pr_requests_clean_restart(self):
        def request(url, token, method='GET', payload=None, allow_404=False):
            if '/git/ref/heads/' in url: return {'object': {'sha': COMMIT}}
            if '/pulls?' in url: return [{'number': 9, 'state': 'closed', 'merged_at': '2026-09-09T19:00:00Z', 'head': {'sha': COMMIT}}]
            raise AssertionError(url)
        with patch('evolution_pending._request', side_effect=request):
            result = check(order(), 'token', 'owner/repo')
        self.assertEqual(result['status'], 'promotion_merged_restart_required')

    def test_orchestrator_maps_open_pr_to_pending_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp); (out / 'evolution-work-order.json').write_text(json.dumps(order()))
            def runner(args, timeout):
                (out / 'evolution-pending.json').write_text(json.dumps({'status': 'promotion_pending_merge'}))
                return type('Result', (), {'returncode': 0})()
            with patch.dict('os.environ', {'STUDIO_CI_PROVIDER': 'github'}, clear=True):
                status = _run_adaptation_pending(out, 100, runner, lambda: 0)
            self.assertEqual(status, 'pending_merge')


if __name__ == '__main__': unittest.main()

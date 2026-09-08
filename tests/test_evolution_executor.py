import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_executor import REQUIRED_PROMOTION_GATES, build_work_order, consume, validate_request


class EvolutionExecutorTests(unittest.TestCase):
    def request(self):
        return {
            'version': 1,
            'status': 'adaptation_required',
            'next_stage': 'billing_qa',
            'gaps': [{
                'kind': 'missing_stage_executor',
                'value': 'billing_qa',
                'reason': 'Completion requires billing QA.',
            }],
            'resource_research': [
                {'kind': 'official_docs', 'query': 'Google Play Billing integration and test purchases'},
                {'kind': 'package_registry', 'query': 'Flutter in_app_purchase maintained package and changelog'},
            ],
            'candidate_policy': {
                'isolation': 'dedicated_branch',
                'external_code_execution': 'forbidden_until_reviewed_and_pinned',
                'promotion': 'only_after_all_gates_pass',
                'rollback': 'required',
            },
            'promotion_gates': sorted(REQUIRED_PROMOTION_GATES),
        }

    def test_builds_deterministic_isolated_candidate(self):
        order = build_work_order(self.request(), 'a' * 40)
        self.assertEqual(order['status'], 'candidate_planned')
        self.assertTrue(order['candidate_branch'].startswith('evolution/billing-qa-'))
        self.assertEqual(order['baseline_sha'], 'a' * 40)
        self.assertEqual(order['resume_stage'], 'billing_qa')
        self.assertTrue(order['implementation_contract']['must_add_trusted_tests'])
        self.assertFalse(order['implementation_contract']['external_code_execution_before_review'])
        self.assertTrue(order['rollback']['required'])

    def test_rejects_weakened_promotion_gate(self):
        request = self.request()
        request['promotion_gates'].remove('security_boundaries_not_weakened')
        with self.assertRaisesRegex(ValueError, 'mandatory promotion gates'):
            validate_request(request)

    def test_rejects_unreviewed_external_execution_policy(self):
        request = self.request()
        request['candidate_policy']['external_code_execution'] = 'allowed'
        with self.assertRaisesRegex(ValueError, 'external-code policy'):
            validate_request(request)

    def test_rejects_unknown_resource_kind(self):
        request = self.request()
        request['resource_research'].append({'kind': 'arbitrary_shell', 'query': 'download and execute'})
        with self.assertRaisesRegex(ValueError, 'Unsupported evolution resource kind'):
            validate_request(request)

    def test_consume_writes_machine_readable_work_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'evolution-request.json'
            source.write_text(json.dumps(self.request()))
            result = consume(source, root / 'out', 'b' * 40)
            written = json.loads((root / 'out/evolution-work-order.json').read_text())
            self.assertEqual(written, result)
            self.assertEqual(written['promotion_decision'], 'pending')
            self.assertEqual(len(written['research_tasks']), 2)
            self.assertIn('do_not_execute_discovered_code', written['research_tasks'][0]['requirements'])


if __name__ == '__main__':
    unittest.main()

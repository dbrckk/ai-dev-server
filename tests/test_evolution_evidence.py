from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_evidence import validate_evidence


class EvolutionEvidenceTests(unittest.TestCase):
    def work_order(self):
        return {
            'candidate_id': 'billing-qa-abc123',
            'research_tasks': [
                {'id': 'research-1', 'kind': 'official_docs'},
                {'id': 'research-2', 'kind': 'package_registry'},
                {'id': 'research-3', 'kind': 'device_runtime'},
            ],
        }

    def evidence(self):
        return {
            'version': 1,
            'candidate_id': 'billing-qa-abc123',
            'items': [
                {
                    'task_id': 'research-1',
                    'kind': 'official_docs',
                    'source': 'https://developer.android.com/google/play/billing',
                    'version_or_revision': 'current',
                    'license': 'documentation terms',
                    'maintenance_signal': 'official Android documentation',
                    'risks': ['Play Console setup required for end-to-end purchase validation'],
                    'notes': 'Use official billing test guidance.',
                },
                {
                    'task_id': 'research-2',
                    'kind': 'package_registry',
                    'source': 'https://pub.dev/packages/in_app_purchase',
                    'version_or_revision': 'registry metadata',
                    'license': 'package metadata must be checked before adoption',
                    'maintenance_signal': 'pub.dev package entry',
                    'risks': ['Package compatibility must be benchmarked'],
                    'notes': 'Metadata only; do not execute package code from this evidence step.',
                },
                {
                    'task_id': 'research-3',
                    'kind': 'device_runtime',
                    'source': 'play-console-test-track',
                    'version_or_revision': 'n/a',
                    'license': 'n/a',
                    'maintenance_signal': 'Google Play test environment',
                    'risks': ['Requires external account/test configuration'],
                    'notes': 'Needed for real billing purchase evidence.',
                },
            ],
        }

    def test_accepts_complete_allowlisted_evidence(self):
        result = validate_evidence(self.work_order(), self.evidence())
        self.assertEqual(result['status'], 'research_complete')
        self.assertEqual(len(result['items']), 3)

    def test_rejects_non_official_docs_domain(self):
        evidence = self.evidence()
        evidence['items'][0]['source'] = 'https://example.com/billing-guide'
        with self.assertRaisesRegex(ValueError, 'not allowlisted'):
            validate_evidence(self.work_order(), evidence)

    def test_rejects_missing_task(self):
        evidence = self.evidence()
        evidence['items'].pop()
        with self.assertRaisesRegex(ValueError, 'cover every task'):
            validate_evidence(self.work_order(), evidence)

    def test_rejects_candidate_mismatch(self):
        evidence = self.evidence()
        evidence['candidate_id'] = 'other-candidate'
        with self.assertRaisesRegex(ValueError, 'does not match candidate'):
            validate_evidence(self.work_order(), evidence)

    def test_rejects_arbitrary_device_identifier(self):
        evidence = self.evidence()
        evidence['items'][2]['source'] = 'random-shell-device'
        with self.assertRaisesRegex(ValueError, 'Unknown device runtime'):
            validate_evidence(self.work_order(), evidence)


if __name__ == '__main__':
    unittest.main()

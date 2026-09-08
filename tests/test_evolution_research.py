from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_evidence import validate_evidence
from evolution_research import FetchResult, ResearchBlocked, execute, research_task, _validate_network_url


class FakeFetch:
    def __init__(self):
        self.urls = []

    def __call__(self, url, **kwargs):
        self.urls.append(url)
        headers = {'date': 'Mon, 08 Sep 2026 20:00:00 GMT', 'etag': '"rev-1"'}
        if url == 'https://developer.android.com/google/play/billing/integrate':
            return FetchResult(url, url, 200, headers, b'<html><title>Google Play Billing integration</title></html>')
        if url == 'https://pub.dev/api/packages/in_app_purchase':
            payload = {
                'latest': {
                    'version': '4.0.0',
                    'published': '2026-08-20T10:00:00Z',
                    'pubspec': {'repository': 'https://github.com/flutter/packages/tree/main/packages/in_app_purchase/in_app_purchase'},
                }
            }
            return FetchResult(url, url, 200, {'content-type': 'application/json'}, json.dumps(payload).encode())
        if url == 'https://api.github.com/repos/flutter/packages':
            payload = {
                'html_url': 'https://github.com/flutter/packages',
                'pushed_at': '2026-09-01T12:00:00Z',
                'archived': False,
                'license': {'spdx_id': 'BSD-3-Clause'},
            }
            return FetchResult(url, url, 200, {'content-type': 'application/json'}, json.dumps(payload).encode())
        if url.startswith('https://api.github.com/search/repositories?'):
            payload = {
                'items': [{
                    'html_url': 'https://github.com/flutter/packages',
                    'pushed_at': '2026-09-01T12:00:00Z',
                    'archived': False,
                    'license': {'spdx_id': 'BSD-3-Clause'},
                    'stargazers_count': 5000,
                    'default_branch': 'main',
                }]
            }
            return FetchResult(url, url, 200, {'content-type': 'application/json'}, json.dumps(payload).encode())
        raise AssertionError('unexpected URL: ' + url)


class EvolutionResearchTests(unittest.TestCase):
    def work_order(self):
        return {
            'candidate_id': 'billing-qa-deadbeef1234',
            'research_tasks': [
                {
                    'id': 'research-1',
                    'kind': 'official_docs',
                    'query': 'Google Play Billing integration and test purchases',
                    'requirements': [],
                },
                {
                    'id': 'research-2',
                    'kind': 'package_registry',
                    'query': 'Flutter in_app_purchase maintained package and changelog',
                    'requirements': [],
                },
                {
                    'id': 'research-3',
                    'kind': 'github_source',
                    'query': 'Flutter billing reference implementation tests',
                    'requirements': [],
                },
            ],
        }

    def test_executes_known_research_without_external_code_execution(self):
        fetch = FakeFetch()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = execute(self.work_order(), out, fetch)
            self.assertEqual(result['version'], 2)
            self.assertEqual(result['status'], 'research_complete')
            self.assertEqual(len(result['items']), 3)
            package = result['items'][1]
            self.assertEqual(package['source'], 'https://pub.dev/packages/in_app_purchase')
            self.assertEqual(package['version_or_revision'], '4.0.0')
            self.assertEqual(package['license'], 'BSD-3-Clause')
            self.assertIn('archived=false', package['maintenance_signal'])
            for item in result['items']:
                self.assertRegex(item['content_sha256'], r'^[0-9a-f]{64}$')
            self.assertTrue((out / 'evolution-research.json').is_file())
            provenance = json.loads((out / 'evolution-research-provenance.json').read_text())
            self.assertEqual(provenance['status'], 'research_provenance_recorded')
            self.assertEqual(len(provenance['tasks']), 3)
            self.assertNotIn('raw_source_code', (out / 'evolution-research.json').read_text())

    def test_unknown_official_mapping_fails_closed(self):
        task = {'id': 'research-1', 'kind': 'official_docs', 'query': 'unknown quantum sensor SDK'}
        with self.assertRaisesRegex(ResearchBlocked, 'No trusted official source'):
            research_task(task, FakeFetch())

    def test_network_url_rejects_non_allowlisted_host_and_nonstandard_port(self):
        with self.assertRaisesRegex(ResearchBlocked, 'not allowlisted'):
            _validate_network_url('https://example.com/resource')
        with self.assertRaisesRegex(ResearchBlocked, 'safe HTTPS'):
            _validate_network_url('https://developer.android.com:8443/resource')

    def test_v2_evidence_requires_content_hash(self):
        order = {
            'candidate_id': 'x',
            'research_tasks': [{'id': 'research-1', 'kind': 'official_docs'}],
        }
        evidence = {
            'version': 2,
            'candidate_id': 'x',
            'items': [{
                'task_id': 'research-1',
                'kind': 'official_docs',
                'source': 'https://developer.android.com/resource',
                'version_or_revision': '1',
                'license': 'official_documentation_terms',
                'maintenance_signal': 'current',
                'risks': ['cross_check_required'],
                'notes': 'metadata only',
                'content_sha256': 'bad',
            }],
        }
        with self.assertRaisesRegex(ValueError, 'content hash'):
            validate_evidence(order, evidence)


if __name__ == '__main__':
    unittest.main()

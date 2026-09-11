import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from adaptation import build_adaptation_request, write_adaptation_request


class AdaptationTests(unittest.TestCase):
    def test_missing_billing_stage_requests_research_and_safe_promotion(self):
        report = {
            'completion': {'finished': False, 'next_stage': 'billing_qa', 'blockers': ['billing_qa_missing']},
            'release_evidence': {'capability_qa': {
                'passed': True,
                'required_qa_stages': ['billing_qa'],
                'permissions': [],
                'reasons': [{'profile': 'billing_qa', 'source': 'dependency', 'value': 'in_app_purchase'}],
            }},
        }
        result = build_adaptation_request(report, frozenset({'real_device', 'capability_qa'}))
        self.assertEqual(result['status'], 'adaptation_required')
        self.assertTrue(any(g['value'] == 'billing_qa' for g in result['gaps']))
        kinds = {item['kind'] for item in result['resource_research']}
        self.assertIn('official_docs', kinds)
        self.assertIn('sdk_tool', kinds)
        self.assertIn('existing_regression_suite_non_regressing', result['promotion_gates'])
        self.assertIn('security_boundaries_not_weakened', result['promotion_gates'])
        self.assertEqual(result['candidate_policy']['rollback'], 'required')

    def test_registered_capability_needs_no_adaptation(self):
        report = {
            'completion': {'finished': False, 'next_stage': 'notification_qa', 'blockers': ['notification_qa_missing']},
            'release_evidence': {'capability_qa': {
                'passed': True,
                'required_qa_stages': ['notification_qa'],
                'permissions': ['android.permission.POST_NOTIFICATIONS'],
                'reasons': [{'profile': 'notification_qa', 'source': 'permission', 'value': 'android.permission.POST_NOTIFICATIONS'}],
            }},
        }
        result = build_adaptation_request(report, frozenset({'notification_qa'}))
        self.assertEqual(result['status'], 'no_adaptation_required')
        self.assertEqual(result['gaps'], [])

    def test_unfinished_without_next_stage_fails_closed(self):
        result = build_adaptation_request({'completion': {'finished': False, 'blockers': []}}, frozenset())
        self.assertEqual(result['status'], 'adaptation_required')
        self.assertIn('invalid_completion_state', {g['kind'] for g in result['gaps']})

    def test_unclassified_android_permission_requests_adaptation(self):
        report = {
            'completion': {'finished': False, 'next_stage': 'store_metadata', 'blockers': ['store_metadata_missing']},
            'release_evidence': {'capability_qa': {
                'passed': True,
                'required_qa_stages': [],
                'permissions': ['android.permission.UWB_RANGING'],
                'reasons': [],
            }},
        }
        result = build_adaptation_request(report, frozenset({'store_metadata'}))
        self.assertTrue(any(g['value'] == 'android.permission.UWB_RANGING' for g in result['gaps']))
        self.assertIn('github_source', {item['kind'] for item in result['resource_research']})

    def test_writes_machine_readable_evolution_request_only_when_needed(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            report = {'completion': {'finished': False, 'next_stage': 'platform_view_qa', 'blockers': []}}
            result = write_adaptation_request(report, out, frozenset())
            path = out / 'evolution-request.json'
            self.assertTrue(path.is_file())
            self.assertEqual(json.loads(path.read_text())['status'], 'adaptation_required')
            path.unlink()
            complete = {'completion': {'finished': True, 'next_stage': None, 'blockers': []}}
            result = write_adaptation_request(complete, out, frozenset())
            self.assertEqual(result['status'], 'no_adaptation_required')
            self.assertFalse(path.exists())


    def test_validated_cross_project_memory_is_attached_as_hint_only(self):
        from project_memory import add_entry, new_memory, save as save_memory
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            memory = add_entry(
                new_memory(),
                entry_id='experience:c1',
                kind='experience',
                project_id='app-a',
                summary='Validated autonomous capability promotion for billing_qa.',
                tags=['capability','billing_qa','autonomous-promotion'],
                evidence={'tests_passed':True,'regression_suite_passed':True,'commit_sha':'a'*40,'gap':'billing_qa'},
                provenance={'source':'validated_project_execution'},
                reusable=True,
                confidence=95,
            )
            save_memory(out/'.memory/memory.json', memory)
            report = {'completion': {'finished': False, 'next_stage': 'billing_qa', 'blockers': ['billing_qa_missing']}}
            with patch.dict('os.environ', {'STUDIO_PROJECT_ID':'app-b'}, clear=False):
                result = write_adaptation_request(report, out, frozenset())
            self.assertIn('billing_qa', result['prior_validated_experience'])
            self.assertEqual(result['memory_policy']['authority'], 'hint_only')
            self.assertFalse(result['memory_policy']['may_skip_validation'])
            self.assertTrue(result['memory_policy']['must_revalidate_locally'])



if __name__ == '__main__':
    unittest.main()

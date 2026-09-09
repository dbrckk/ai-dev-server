from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_candidate import CandidateRejected
from evolution_synthesis import consume, synthesize


class FakeAPI:
    base = 'https://example.invalid/v1'
    def __init__(self, payload):
        self.payload = payload
        self.calls = []
    def call(self, method, path, data=None):
        self.calls.append((method, path, data))
        return {'choices': [{'finish_reason': 'stop', 'message': {'content': json.dumps(self.payload)}}]}


class EvolutionSynthesisTests(unittest.TestCase):
    def order(self):
        return {
            'status': 'candidate_planned',
            'candidate_id': 'future-qa-abc123def456',
            'candidate_branch': 'evolution/future-qa-abc123def456',
            'baseline_sha': 'a' * 40,
            'primary_gap': {'kind': 'missing_stage_executor', 'value': 'future_qa', 'reason': 'missing trusted stage'},
        }

    def research(self):
        return {'status': 'research_complete', 'candidate_id': 'future-qa-abc123def456', 'items': []}

    def candidate(self):
        benchmark = json.dumps({'version': 1, 'id': 'future-qa-core', 'gap': 'future_qa', 'purpose': 'Prove fail-closed evidence validation.', 'assertions': ['missing evidence fails', 'valid evidence passes']})
        return {
            'version': 1,
            'candidate_id': 'future-qa-abc123def456',
            'gap': 'future_qa',
            'files': [
                {'path': 'studio/future_qa.py', 'content': 'def validate(root):\n    return {"passed": False, "blockers": ["evidence_missing"]}\n'},
                {'path': 'studio/future_stage.py', 'content': 'def main():\n    return 1\n'},
                {'path': 'tests/test_future_qa.py', 'content': 'import unittest\nclass T(unittest.TestCase):\n    def test_missing_evidence_fails(self): self.assertTrue(True)\n    def test_valid_evidence_passes(self): self.assertTrue(True)\n'},
                {'path': 'tests/benchmarks/future_qa.json', 'content': benchmark},
            ],
        }

    def test_validated_model_output_is_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            order = root / 'order.json'; order.write_text(json.dumps(self.order()))
            research = root / 'research.json'; research.write_text(json.dumps(self.research()))
            api = FakeAPI(self.candidate())
            result = consume(order, research, root / 'out', api=api, model='test-model')
            self.assertEqual(result['status'], 'candidate_validated')
            self.assertEqual(result['benchmark_assertions'], 2)
            self.assertEqual(result['differential_tests'], 2)
            self.assertTrue((root / 'out/evolution-candidate.json').is_file())
            self.assertEqual(api.calls[0][0:2], ('POST', '/chat/completions'))

    def test_model_cannot_escape_candidate_scope(self):
        candidate = self.candidate()
        candidate['files'][0]['path'] = 'studio/core.py'
        with self.assertRaises(CandidateRejected):
            synthesize(self.order(), self.research(), api=FakeAPI(candidate), model='test-model')

    def test_research_is_required_before_model_call(self):
        api = FakeAPI(self.candidate())
        with self.assertRaisesRegex(CandidateRejected, 'completed trusted research'):
            synthesize(self.order(), {'status': 'blocked'}, api=api, model='test-model')
        self.assertEqual(api.calls, [])


if __name__ == '__main__':
    unittest.main()

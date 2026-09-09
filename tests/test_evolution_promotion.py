import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_promotion import PromotionError, apply
from stage_registry import get_stage


class EvolutionPromotionTests(unittest.TestCase):
    def test_fake_approval_cannot_install_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            order = {'status': 'candidate_planned', 'candidate_id': 'candidate-1', 'baseline_sha': 'a' * 40,
                     'primary_gap': {'value': 'future_capability_qa'}}
            candidate = {'status': 'candidate_validated', 'candidate_id': 'candidate-1', 'gap': 'future_capability_qa',
                         'files': [], 'candidate_sha256': '0' * 64}
            benchmark = {'status': 'isolated_benchmark_complete', 'candidate_id': 'candidate-1', 'baseline_sha': 'a' * 40}
            promotion = {'status': 'promotion_approved', 'promotion_decision': 'approve', 'candidate_id': 'candidate-1'}
            with self.assertRaises(PromotionError):
                apply(root, order, candidate, benchmark, promotion)
            self.assertFalse((root / 'control' / 'promoted_stages.json').exists())

    def test_promoted_registry_is_strict_and_dynamic(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = Path(tmp) / 'promoted_stages.json'
            registry.write_text(json.dumps({'version': 1, 'stages': {'future_capability_qa': {
                'script': 'studio/future_capability_stage.py', 'candidate_id': 'candidate-1',
                'baseline_sha': 'a' * 40, 'candidate_sha': 'b' * 40}}}))
            with patch('stage_registry.PROMOTED_REGISTRY', registry):
                stage = get_stage('future_capability_qa')
                self.assertIsNotNone(stage)
                self.assertEqual(stage.script, 'studio/future_capability_stage.py')
                self.assertEqual(stage.deferred_status, 'deferred_future_capability')

    def test_registry_script_cannot_redirect_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = Path(tmp) / 'promoted_stages.json'
            registry.write_text(json.dumps({'version': 1, 'stages': {'future_capability_qa': {
                'script': 'studio/orchestrator.py', 'candidate_id': 'candidate-1',
                'baseline_sha': 'a' * 40, 'candidate_sha': 'b' * 40}}}))
            with patch('stage_registry.PROMOTED_REGISTRY', registry):
                with self.assertRaisesRegex(RuntimeError, 'script mismatch'):
                    get_stage('future_capability_qa')


if __name__ == '__main__':
    unittest.main()

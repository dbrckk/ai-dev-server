import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from core import canonical
from evolution_rollback import RollbackError, rollback


class EvolutionRollbackTests(unittest.TestCase):
    def make_promoted(self, root):
        candidate_id = 'candidate-1'
        gap = 'future_capability_qa'
        baseline = 'a' * 40
        candidate = 'b' * 40
        paths = [
            'studio/future_capability_qa.py',
            'studio/future_capability_stage.py',
            'tests/test_future_capability_qa.py',
            'tests/benchmarks/future_capability_qa.json',
        ]
        contents = {path: 'content:' + path for path in paths}
        for path, content in contents.items():
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        previous = {'version': 1, 'stages': {'existing_qa': {
            'script': 'studio/existing_stage.py', 'candidate_id': 'old-candidate',
            'baseline_sha': 'c' * 40, 'candidate_sha': 'd' * 40}}}
        registry = {'version': 1, 'stages': dict(previous['stages'])}
        registry['stages'][gap] = {
            'script': 'studio/future_capability_stage.py', 'candidate_id': candidate_id,
            'baseline_sha': baseline, 'candidate_sha': candidate}
        registry_path = root / 'control/promoted_stages.json'
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(canonical(registry) + '\n')
        previous_text = canonical(previous) + '\n'
        record = {
            'version': 2, 'candidate_id': candidate_id, 'gap': gap, 'baseline_sha': baseline,
            'candidate_sha': candidate, 'created_paths': sorted(paths),
            'created_sha256': {path: hashlib.sha256(contents[path].encode()).hexdigest() for path in sorted(paths)},
            'registry_before': previous,
            'registry_sha256_before': hashlib.sha256(previous_text.encode()).hexdigest(),
        }
        record_path = root / 'control/evolution_rollbacks' / (candidate_id + '.json')
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(canonical(record) + '\n')
        return candidate_id, paths, previous

    def test_rollback_restores_registry_and_removes_only_promoted_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate_id, paths, previous = self.make_promoted(root)
            unrelated = root / 'studio/unrelated.py'
            unrelated.write_text('keep')
            result = rollback(root, candidate_id)
            self.assertEqual(result['status'], 'rolled_back')
            self.assertEqual(json.loads((root / 'control/promoted_stages.json').read_text()), previous)
            self.assertTrue(unrelated.is_file())
            for path in paths:
                self.assertFalse((root / path).exists())
            self.assertTrue((root / 'control/evolution_rollbacks' / (candidate_id + '.applied.json')).is_file())

    def test_changed_promoted_file_blocks_entire_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate_id, paths, _ = self.make_promoted(root)
            (root / paths[0]).write_text('tampered')
            registry_before = (root / 'control/promoted_stages.json').read_text()
            with self.assertRaisesRegex(RollbackError, 'changed after promotion'):
                rollback(root, candidate_id)
            self.assertEqual((root / 'control/promoted_stages.json').read_text(), registry_before)
            self.assertTrue(all((root / path).exists() for path in paths))

    def test_registry_identity_mismatch_blocks_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate_id, paths, _ = self.make_promoted(root)
            registry_path = root / 'control/promoted_stages.json'
            registry = json.loads(registry_path.read_text())
            registry['stages']['future_capability_qa']['candidate_sha'] = 'e' * 40
            registry_path.write_text(canonical(registry) + '\n')
            with self.assertRaisesRegex(RollbackError, 'registry no longer matches'):
                rollback(root, candidate_id)
            self.assertTrue(all((root / path).exists() for path in paths))


if __name__ == '__main__':
    unittest.main()

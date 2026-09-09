from pathlib import Path
import base64
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_promote import PromotionError, publish, registry_update

BASELINE = 'a' * 40
CANDIDATE_SHA = 'b' * 40
PROMOTED = 'c' * 40
REGISTRY = """from dataclasses import dataclass
@dataclass(frozen=True)
class Stage:
    name: str
    script: str
    deferred_status: str
    failed_status: str
STAGES = {
    'real_device': Stage('real_device', 'studio/device_stage.py', 'deferred_device', 'device_failed'),
}


def get_stage(name: str):
    return STAGES.get(name)
"""


class FakeGitHub:
    def __init__(self, main=BASELINE, branch_exists=False):
        self.main = main
        self.branch_exists = branch_exists
        self.posts = []

    def get(self, path):
        if path == '':
            return {'default_branch': 'main', 'archived': False}
        if path == '/branches/main':
            return {'commit': {'sha': self.main}}
        if path == '/git/commits/' + BASELINE:
            return {'tree': {'sha': 'tree-base'}}
        if path == '/git/trees/tree-base?recursive=1':
            return {'truncated': False, 'tree': [{'path': 'studio/stage_registry.py', 'type': 'blob', 'sha': 'registry-blob'}]}
        if path == '/git/blobs/registry-blob':
            return {'content': base64.b64encode(REGISTRY.encode()).decode()}
        if path.startswith('/git/matching-refs/heads/evolution/'):
            return [{'ref': 'refs/heads/evolution/future-capability-abc'}] if self.branch_exists else []
        raise AssertionError('unexpected GET ' + path)

    def post(self, path, data):
        self.posts.append((path, data))
        if path == '/git/trees':
            return {'sha': 'tree-promoted'}
        if path == '/git/commits':
            return {'sha': PROMOTED}
        if path == '/git/refs':
            return {'ref': data['ref']}
        if path == '/pulls':
            return {'number': 42}
        raise AssertionError('unexpected POST ' + path)


class EvolutionPromotionTests(unittest.TestCase):
    def order(self):
        return {
            'status': 'candidate_planned',
            'candidate_id': 'future-capability-abc',
            'candidate_branch': 'evolution/future-capability-abc',
            'baseline_sha': BASELINE,
            'primary_gap': {'value': 'future_capability_qa'},
        }

    def candidate(self):
        return {
            'status': 'candidate_validated',
            'candidate_id': 'future-capability-abc',
            'candidate_branch': 'evolution/future-capability-abc',
            'gap': 'future_capability_qa',
            'files': [
                {'path': 'studio/future_capability_qa.py', 'content': 'def validate():\n    return False\n'},
                {'path': 'studio/future_capability_stage.py', 'content': 'def main():\n    return 1\n'},
                {'path': 'tests/test_future_capability_qa.py', 'content': 'import unittest\n'},
                {'path': 'tests/benchmarks/future_capability_qa.json', 'content': '{}'},
            ],
        }

    def promotion(self):
        return {
            'status': 'promotion_approved',
            'promotion_decision': 'approve',
            'candidate_id': 'future-capability-abc',
            'baseline_sha': BASELINE,
            'candidate_sha': CANDIDATE_SHA,
            'gap': 'future_capability_qa',
        }

    def test_registry_update_is_deterministic_and_scoped(self):
        updated = registry_update(REGISTRY, 'future_capability_qa')
        self.assertIn("'future_capability_qa': Stage('future_capability_qa', 'studio/future_capability_stage.py', 'deferred_future_capability', 'future_capability_failed')", updated)
        self.assertEqual(updated.count('future_capability_qa'), 2)
        with self.assertRaisesRegex(PromotionError, 'already registered'):
            registry_update(updated, 'future_capability_qa')

    def test_approved_candidate_opens_pr_without_direct_main_write(self):
        github = FakeGitHub()
        result = publish(self.order(), self.candidate(), self.promotion(), repository='owner/control', github=github)
        self.assertEqual(result['status'], 'promotion_pr_opened')
        self.assertEqual(result['rollback_ref'], BASELINE)
        self.assertFalse(result['direct_main_write'])
        self.assertTrue(result['requires_fresh_ci_before_merge'])
        tree_post = next(data for path, data in github.posts if path == '/git/trees')
        paths = {item['path'] for item in tree_post['tree']}
        self.assertEqual(paths, {
            'studio/future_capability_qa.py', 'studio/future_capability_stage.py',
            'tests/test_future_capability_qa.py', 'tests/benchmarks/future_capability_qa.json',
            'studio/stage_registry.py',
        })
        ref_post = next(data for path, data in github.posts if path == '/git/refs')
        self.assertEqual(ref_post['ref'], 'refs/heads/evolution/future-capability-abc')
        pr_post = next(data for path, data in github.posts if path == '/pulls')
        self.assertEqual(pr_post['base'], 'main')

    def test_stale_main_is_never_promoted(self):
        github = FakeGitHub(main='d' * 40)
        with self.assertRaisesRegex(PromotionError, 'stale'):
            publish(self.order(), self.candidate(), self.promotion(), repository='owner/control', github=github)
        self.assertEqual(github.posts, [])

    def test_rejected_decision_and_existing_branch_fail_closed(self):
        rejected = self.promotion(); rejected['status'] = 'promotion_rejected'; rejected['promotion_decision'] = 'reject'
        with self.assertRaisesRegex(PromotionError, 'not approved'):
            publish(self.order(), self.candidate(), rejected, repository='owner/control', github=FakeGitHub())
        with self.assertRaisesRegex(PromotionError, 'already exists'):
            publish(self.order(), self.candidate(), self.promotion(), repository='owner/control', github=FakeGitHub(branch_exists=True))


if __name__ == '__main__':
    unittest.main()

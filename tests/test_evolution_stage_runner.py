import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_stage_runner import PromotedStageError, scrubbed_env


class PromotedStageRunnerTests(unittest.TestCase):
    def test_scrubs_tokens_keys_and_secrets(self):
        env = scrubbed_env({
            'PATH': '/bin',
            'STUDIO_GITHUB_TOKEN': 'token',
            'GITHUB_TOKEN': 'token',
            'STUDIO_API_KEY': 'key',
            'CUSTOM_API_KEY': 'key',
            'OTHER_SECRET': 'secret',
            'SAFE_VALUE': 'ok',
        })
        self.assertEqual(env['SAFE_VALUE'], 'ok')
        self.assertEqual(env['STUDIO_PROMOTED_STAGE'], '1')
        for key in ('STUDIO_GITHUB_TOKEN','GITHUB_TOKEN','STUDIO_API_KEY','CUSTOM_API_KEY','OTHER_SECRET'):
            self.assertNotIn(key, env)

    def test_rejects_paths_outside_stage_scope(self):
        from evolution_stage_runner import run
        for path in ('../evil.py', '/tmp/evil.py', 'studio/orchestrator.py', 'tests/test_x.py'):
            with self.assertRaises(PromotedStageError):
                run(path, [])


if __name__ == '__main__':
    unittest.main()

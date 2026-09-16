from pathlib import Path
import unittest


WORKFLOW = Path('.github/workflows/mobile-studio.yml')


class MobileStudioProviderFallbackTests(unittest.TestCase):
    def test_autonomous_runner_exports_free_nim_fallbacks_using_existing_key(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('STUDIO_PROVIDERS_JSON:', text)
        self.assertIn('nvidia/nemotron-3.5-lightning-30b-a3b', text)
        self.assertIn('poolside/laguna-xs-2.1', text)
        self.assertGreaterEqual(text.count('"key_env":"STUDIO_API_KEY"'), 2)


if __name__ == '__main__':
    unittest.main()

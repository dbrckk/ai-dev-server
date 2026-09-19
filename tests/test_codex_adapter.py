from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
if str(STUDIO) not in sys.path:
    sys.path.insert(0, str(STUDIO))

from agents.codex import codex_invocation, codex_omniroute_invocation, parse_codex_usage


class CodexAdapterTests(unittest.TestCase):
    def test_invocation_uses_headless_json_ephemeral_workspace_write_exec(self):
        argv, extra_env = codex_invocation("finish the repository")

        self.assertEqual(
            argv,
            [
                "codex",
                "exec",
                "--json",
                "--ephemeral",
                "--sandbox",
                "workspace-write",
                "finish the repository",
            ],
        )
        self.assertEqual(extra_env, {})

    def test_parse_usage_from_completed_turn(self):
        stdout = "\n".join(
            [
                '{"type":"thread.started","thread_id":"thread-1"}',
                '{"type":"turn.started"}',
                '{"type":"turn.completed","usage":{"input_tokens":120,"cached_input_tokens":80,"cache_write_input_tokens":5,"output_tokens":30,"reasoning_output_tokens":12}}',
            ]
        )

        self.assertEqual(
            parse_codex_usage(stdout),
            {
                "input_tokens": 120,
                "cached_input_tokens": 80,
                "cache_write_input_tokens": 5,
                "output_tokens": 30,
                "reasoning_output_tokens": 12,
                "total_tokens": 150,
            },
        )

    def test_parse_usage_is_backward_compatible_with_older_streams(self):
        stdout = '{"type":"turn.completed","usage":{"input_tokens":10,"cached_input_tokens":4,"output_tokens":3}}'

        self.assertEqual(
            parse_codex_usage(stdout),
            {
                "input_tokens": 10,
                "cached_input_tokens": 4,
                "cache_write_input_tokens": 0,
                "output_tokens": 3,
                "reasoning_output_tokens": 0,
                "total_tokens": 13,
            },
        )

    def test_parse_usage_ignores_malformed_and_unrelated_lines(self):
        stdout = "\n".join(
            [
                "not-json",
                '{"type":"item.completed","item":{"type":"agent_message"}}',
                '{"type":"turn.completed","usage":{"input_tokens":7,"cached_input_tokens":0,"output_tokens":2}}',
            ]
        )

        self.assertEqual(parse_codex_usage(stdout)["total_tokens"], 9)

    def test_parse_usage_returns_none_without_completed_turn(self):
        self.assertIsNone(parse_codex_usage('{"type":"turn.started"}'))


if __name__ == "__main__":
    unittest.main()


    def test_omniroute_invocation_uses_isolated_home_and_custom_responses_provider(self):
        argv, extra_env = codex_omniroute_invocation(
            "finish the repository",
            base_url="http://127.0.0.1:20128/v1",
            codex_home="/tmp/codex-omniroute-test",
        )

        self.assertEqual(extra_env["CODEX_HOME"], "/tmp/codex-omniroute-test")
        self.assertIn("--ignore-user-config", argv)
        self.assertIn('model="auto"', argv)
        self.assertIn('model_provider="omniroute"', argv)
        provider_override = next(
            value for index, value in enumerate(argv)
            if index > 0 and argv[index - 1] == "-c"
            and value.startswith("model_providers.omniroute=")
        )
        self.assertIn("http://127.0.0.1:20128/v1", provider_override)
        self.assertIn("wire_api='responses'", provider_override)
        self.assertNotIn("OPENAI_API_KEY", extra_env)

    def test_omniroute_invocation_rejects_insecure_remote_http(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            codex_omniroute_invocation(
                "finish the repository",
                base_url="http://example.com/v1",
                codex_home="/tmp/codex-omniroute-test",
            )

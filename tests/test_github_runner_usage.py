import unittest

from studio.github_runner import collect_agent_usage


class GitHubRunnerUsageTests(unittest.TestCase):
    def test_collect_agent_usage_sums_codex_attempts_across_rounds(self):
        report = {
            "rounds": [
                {
                    "agent_trace": [
                        {
                            "status": "passed",
                            "selected": "codex",
                            "attempts": [
                                {
                                    "agent": "codex",
                                    "status": "passed",
                                    "usage": {
                                        "input_tokens": 100,
                                        "cached_input_tokens": 25,
                                        "output_tokens": 40,
                                        "reasoning_output_tokens": 10,
                                        "total_tokens": 140,
                                    },
                                }
                            ],
                        }
                    ]
                },
                {
                    "agent_trace": [
                        {
                            "status": "passed",
                            "selected": "codex",
                            "attempts": [
                                {
                                    "agent": "codex",
                                    "status": "passed",
                                    "usage": {
                                        "input_tokens": 20,
                                        "cached_input_tokens": 5,
                                        "output_tokens": 8,
                                        "reasoning_output_tokens": 3,
                                        "total_tokens": 28,
                                    },
                                }
                            ],
                        }
                    ]
                },
            ]
        }

        self.assertEqual(
            collect_agent_usage(report),
            {
                "input_tokens": 120,
                "cached_input_tokens": 30,
                "output_tokens": 48,
                "reasoning_tokens": 13,
                "total_tokens": 168,
                "runs": 2,
                "agents": {"codex": 2},
            },
        )

    def test_collect_agent_usage_ignores_duplicate_non_attempt_usage_and_bad_values(self):
        report = {
            "rounds": [
                {
                    "agent_trace": [
                        {
                            "usage": {"total_tokens": 999999},
                            "attempts": [
                                {
                                    "agent": "codex",
                                    "usage": {
                                        "input_tokens": "7",
                                        "cached_input_tokens": True,
                                        "output_tokens": 2,
                                        "reasoning_output_tokens": -5,
                                    },
                                },
                                {
                                    "agent": "opencode",
                                    "usage": {
                                        "input_tokens": 4,
                                        "output_tokens": 1,
                                        "total_tokens": 5,
                                    },
                                },
                            ],
                        }
                    ]
                }
            ]
        }

        self.assertEqual(
            collect_agent_usage(report),
            {
                "input_tokens": 11,
                "cached_input_tokens": 0,
                "output_tokens": 3,
                "reasoning_tokens": 0,
                "total_tokens": 12,
                "runs": 2,
                "agents": {"codex": 1, "opencode": 1},
            },
        )

    def test_collect_agent_usage_empty_report_is_zeroed(self):
        self.assertEqual(
            collect_agent_usage({}),
            {
                "input_tokens": 0,
                "cached_input_tokens": 0,
                "output_tokens": 0,
                "reasoning_tokens": 0,
                "total_tokens": 0,
                "runs": 0,
                "agents": {},
            },
        )


if __name__ == "__main__":
    unittest.main()

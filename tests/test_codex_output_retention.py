from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
if str(STUDIO) not in sys.path:
    sys.path.insert(0, str(STUDIO))

from agents.adapters import AgentAdapter
from agents.codex import parse_codex_usage
from agents.registry import AgentSpec


class CodexAdapterOutputRetentionTests(unittest.TestCase):
    def test_codex_terminal_usage_event_survives_large_trailing_output(self):
        completed = (
            '{"type":"turn.completed","usage":'
            '{"input_tokens":120,"cached_input_tokens":40,'
            '"output_tokens":30,"reasoning_output_tokens":9}}'
        )
        stdout = completed + "\n" + ("x" * 40000)
        result = subprocess.CompletedProcess(
            args=["codex"],
            returncode=0,
            stdout=stdout,
            stderr="",
        )
        spec = AgentSpec(
            "codex",
            "codex",
            frozenset({"code_editing"}),
            priority=100,
            free_preferred=True,
        )

        with tempfile.TemporaryDirectory() as td, patch(
            "agents.adapters.AgentAdapter.probe",
            return_value=True,
        ), patch(
            "agents.adapters.subprocess.run",
            return_value=result,
        ):
            run = AgentAdapter(spec).run(
                ["codex", "exec", "--json", "work"],
                cwd=Path(td),
            )

        self.assertLessEqual(len(run.stdout_tail), 24500)
        usage = parse_codex_usage(run.stdout_tail)
        self.assertIsNotNone(usage)
        self.assertEqual(usage["total_tokens"], 150)
        self.assertEqual(usage["cached_input_tokens"], 40)


if __name__ == "__main__":
    unittest.main()

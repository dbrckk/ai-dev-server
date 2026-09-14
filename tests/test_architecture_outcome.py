import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from architecture_outcome import build, write


class ArchitectureOutcomeTests(unittest.TestCase):
    def test_build_links_decision_to_verified_outcome(self):
        state = {
            "status": "validated_preview",
            "cycles": 2,
            "rounds": 3,
            "model_calls_this_cycle": 4,
            "checkpoint_replays_this_cycle": 1,
            "blockers": [],
            "architecture_decision": {
                "status": "planned",
                "chosen": [{"repo": "a/core"}, {"repo": "b/ui"}],
            },
        }
        result = build(state)

        self.assertTrue(result["outcome"]["successful"])
        self.assertEqual(result["chosen_repositories"], ["a/core", "b/ui"])
        self.assertEqual(result["outcome"]["model_calls_this_cycle"], 4)
        self.assertEqual(result["outcome"]["checkpoint_replays_this_cycle"], 1)

    def test_blocked_outcome_is_not_successful(self):
        result = build({
            "status": "blocked",
            "blockers": ["validation failed"],
            "architecture_decision": {"status": "planned", "chosen": []},
        })

        self.assertFalse(result["outcome"]["successful"])
        self.assertEqual(result["outcome"]["blocker_count"], 1)

    def test_write_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            result = write(
                {
                    "status": "validated_preview",
                    "architecture_decision": {"status": "planned", "chosen": []},
                },
                out,
            )
            saved = json.loads((out / "architecture-outcome.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, result)
            self.assertEqual(len(saved["decision_id"]), 64)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from meta_router import choose_execution_mode


class MetaRouterTests(unittest.TestCase):
    def test_no_agent_forces_model_only(self):
        decision = choose_execution_mode([], role="implementation", agent_available=False)
        self.assertEqual(decision.mode, "model_only")
        self.assertEqual(decision.agent_limit, 0)

    def test_insufficient_history_keeps_dual_mode(self):
        events = [
            {"kind":"agent","role":"implementation","success":True},
            {"kind":"provider","role":"implementation","success":True},
        ]
        decision = choose_execution_mode(events, role="implementation", agent_available=True)
        self.assertEqual(decision.mode, "dual")
        self.assertEqual(decision.agent_limit, 2)

    def test_model_advantage_reduces_agent_exploration(self):
        events = []
        for _ in range(6):
            events.append({"kind":"agent","role":"implementation","success":False})
            events.append({"kind":"provider","role":"implementation","success":True})
        decision = choose_execution_mode(events, role="implementation", agent_available=True)
        self.assertEqual(decision.mode, "model_focus")
        self.assertEqual(decision.agent_limit, 1)

    def test_agent_advantage_keeps_agent_focus(self):
        events = []
        for _ in range(6):
            events.append({"kind":"agent","role":"implementation","success":True})
            events.append({"kind":"provider","role":"implementation","success":False})
        decision = choose_execution_mode(events, role="implementation", agent_available=True)
        self.assertEqual(decision.mode, "agent_focus")
        self.assertEqual(decision.agent_limit, 2)


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import unittest
from pathlib import Path

from studio.queue import matrix


class QueueTerminalStateTests(unittest.TestCase):
    def request(self, root, project_id, target):
        value={
            "id":project_id,
            "target_repo":target,
            "app_name":"demo_app",
            "brief":"Create a complete working demo mobile app.",
            "enabled":True,
            "max_rounds":3,
            "max_calls":12,
            "max_cycles":5,
        }
        path=Path(root)/(project_id+".json")
        path.write_text(json.dumps(value))

    def test_terminal_goal_is_not_requeued(self):
        with tempfile.TemporaryDirectory() as td:
            self.request(td,"done","owner/done")
            self.request(td,"active","owner/active")
            rows=matrix(td,{"done"})
            self.assertEqual([x["id"] for x in rows],["active"])

    def test_unknown_terminal_id_is_harmless(self):
        with tempfile.TemporaryDirectory() as td:
            self.request(td,"active","owner/active")
            self.assertEqual([x["id"] for x in matrix(td,{"other"})],["active"])


if __name__=="__main__":
    unittest.main()

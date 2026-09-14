import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import ci_runner


class MultiProjectCanaryTests(unittest.TestCase):
    def _request(self, root: Path, index: int) -> None:
        payload = {
            "id": f"canary-{index}",
            "target_repo": f"owner/app-{index}",
            "app_name": f"app_{index}",
            "brief": "Build a complete deterministic mobile application for canary validation.",
            "enabled": True,
            "max_rounds": 2,
            "max_calls": 4,
            "max_cycles": 2,
        }
        (root / f"canary-{index}.json").write_text(
            json.dumps(payload),
            encoding="utf-8",
        )

    def test_three_projects_complete_without_state_cross_talk(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            requests = root / "requests"
            requests.mkdir()
            out = root / "out"
            for index in range(3):
                self._request(requests, index)

            seen = []

            def fake_project(project, project_out, work, runner, deadline, clock, baseline_sha):
                seen.append((project["id"], Path(project_out).name))
                Path(project_out).mkdir(parents=True, exist_ok=True)
                (Path(project_out) / "marker.json").write_text(
                    json.dumps({"id": project["id"]}),
                    encoding="utf-8",
                )
                return {"status": "complete", "next_stage": None}

            with patch("ci_runner._run_project_for_queue", side_effect=fake_project):
                code = ci_runner.run_queue(
                    directory=str(requests),
                    out=out,
                    runner=lambda *a, **k: None,
                    clock=lambda: 0,
                )

            self.assertEqual(code, 0)
            self.assertEqual(
                sorted(project_id for project_id, _ in seen),
                ["canary-0", "canary-1", "canary-2"],
            )
            report = json.loads((out / "queue.json").read_text(encoding="utf-8"))
            self.assertEqual(
                [item["status"] for item in report["projects"]],
                ["complete", "complete", "complete"],
            )
            for index in range(3):
                marker = json.loads(
                    (out / f"canary-{index}" / "marker.json").read_text(encoding="utf-8")
                )
                self.assertEqual(marker["id"], f"canary-{index}")


if __name__ == "__main__":
    unittest.main()

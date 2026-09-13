import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from artifact_handoff import ArtifactHandoffError, select_latest_project_artifact


class ArtifactHandoffTests(unittest.TestCase):
    def test_selects_latest_exact_project_artifact(self):
        payload={"artifacts":[
            {"id":1,"name":"mobile-demo-v1-10","expired":False,"created_at":"2026-09-13T10:00:00Z","workflow_run":{"id":100}},
            {"id":2,"name":"mobile-demo-v1-11","expired":False,"created_at":"2026-09-13T11:00:00Z","workflow_run":{"id":101}},
            {"id":3,"name":"mobile-other-99","expired":False,"created_at":"2026-09-13T12:00:00Z","workflow_run":{"id":102}},
        ]}
        selected=select_latest_project_artifact(payload,"demo-v1")
        self.assertEqual(selected["name"],"mobile-demo-v1-11")
        self.assertEqual(selected["run_id"],101)

    def test_expired_and_forged_names_are_ignored(self):
        payload={"artifacts":[
            {"id":1,"name":"mobile-demo-v1-12","expired":True,"created_at":"2026-09-13T12:00:00Z","workflow_run":{"id":100}},
            {"id":2,"name":"mobile-demo-v1-not-a-run","expired":False,"created_at":"2026-09-13T13:00:00Z","workflow_run":{"id":101}},
            {"id":3,"name":"mobile-demo-v10-13","expired":False,"created_at":"2026-09-13T14:00:00Z","workflow_run":{"id":102}},
        ]}
        self.assertIsNone(select_latest_project_artifact(payload,"demo-v1"))

    def test_invalid_project_id_fails_closed(self):
        with self.assertRaisesRegex(ArtifactHandoffError,"project id invalid"):
            select_latest_project_artifact({"artifacts":[]},"../demo")

    def test_invalid_listing_fails_closed(self):
        with self.assertRaisesRegex(ArtifactHandoffError,"artifact listing invalid"):
            select_latest_project_artifact({"artifacts":None},"demo-v1")

    def test_same_timestamp_uses_artifact_id_deterministically(self):
        payload={"artifacts":[
            {"id":10,"name":"mobile-demo-v1-20","expired":False,"created_at":"2026-09-13T12:00:00Z","workflow_run":{"id":100}},
            {"id":11,"name":"mobile-demo-v1-21","expired":False,"created_at":"2026-09-13T12:00:00Z","workflow_run":{"id":101}},
        ]}
        selected=select_latest_project_artifact(payload,"demo-v1")
        self.assertEqual(selected["artifact_id"],11)


if __name__=="__main__":
    unittest.main()

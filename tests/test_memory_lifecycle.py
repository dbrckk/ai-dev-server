import json
from pathlib import Path
import tempfile
import unittest

from studio.memory_lifecycle import ingest_run
from studio.project_memory import new_memory, query, reusable_for_project


class MemoryLifecycleTests(unittest.TestCase):
    def test_research_is_ingested(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            (out/"evolution-research.json").write_text(json.dumps({
                "status":"research_complete","candidate_id":"c1","items":[{
                    "kind":"official_docs","source":"https://developer.android.com/x",
                    "notes":"Official docs.","content_sha256":"a"*64
                }]
            }))
            memory=ingest_run(new_memory(),"app-a",out)
            self.assertEqual(len(query(memory,kind="research")),1)

    def test_approved_persisted_promotion_becomes_reusable_experience(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            (out/"evolution-persisted.json").write_text(json.dumps({
                "status":"promotion_persisted","candidate_id":"c1","gap":"billing_qa","commit_sha":"b"*40
            }))
            (out/"evolution-promotion.json").write_text(json.dumps({
                "status":"promotion_approved","promotion_decision":"approve"
            }))
            (out/"evolution-isolated-benchmark.json").write_text(json.dumps({
                "candidate":{"unit_tests":{"passed":True},"flutter_smoke_passed":True}
            }))
            memory=ingest_run(new_memory(),"app-a",out)
            items=reusable_for_project(memory,"app-b")
            self.assertEqual([x["id"] for x in items],["experience:c1"])

    def test_unapproved_or_unpersisted_candidate_is_not_learned(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            (out/"evolution-persisted.json").write_text(json.dumps({
                "status":"persistence_blocked","candidate_id":"c1","gap":"billing_qa","commit_sha":"b"*40
            }))
            (out/"evolution-promotion.json").write_text(json.dumps({
                "status":"promotion_approved","promotion_decision":"approve"
            }))
            (out/"evolution-isolated-benchmark.json").write_text(json.dumps({
                "candidate":{"unit_tests":{"passed":True},"flutter_smoke_passed":True}
            }))
            self.assertEqual(ingest_run(new_memory(),"app-a",out)["entries"],[])

    def test_duplicate_experience_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            (out/"evolution-persisted.json").write_text(json.dumps({
                "status":"already_persisted","candidate_id":"c1","gap":"billing_qa","commit_sha":"b"*40
            }))
            (out/"evolution-promotion.json").write_text(json.dumps({
                "status":"promotion_approved","promotion_decision":"approve"
            }))
            (out/"evolution-isolated-benchmark.json").write_text(json.dumps({
                "candidate":{"unit_tests":{"passed":True},"flutter_smoke_passed":True}
            }))
            memory=ingest_run(new_memory(),"app-a",out)
            memory=ingest_run(memory,"app-a",out)
            self.assertEqual(len(memory["entries"]),1)


if __name__=="__main__":
    unittest.main()

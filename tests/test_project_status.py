from pathlib import Path
import json
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from objective_dag import mark_running, mark_verified, new as new_dag, save as save_dag
from project_status import inspect
from release_proof_manifest import build as build_release_proof, save as save_release_proof
from task_proof_bundle import build as build_task_proof, filename as task_proof_filename, save as save_task_proof


class ProjectStatusTests(unittest.TestCase):
    def test_ready_dag_reports_working_and_next_task(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            autonomy=root/".autonomy"
            autonomy.mkdir()
            dag=new_dag("demo","x",{"work_items":["implement parser"]},"a"*40)
            save_dag(autonomy/"objective-dag.json",dag)
            status=inspect(root)
            self.assertEqual(status["status"],"working")
            self.assertEqual(status["next_task"]["id"],"task-1")

    def test_report_blocker_reports_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"generic-report.json").write_text(json.dumps({
                "status":"deferred",
                "completion":{"finished":False,"blockers":["API key required"]},
            }))
            status=inspect(root)
            self.assertEqual(status["status"],"blocked")
            self.assertEqual(status["blockers"],["API key required"])

    def test_verified_dag_and_release_proof_report_complete(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            autonomy=root/".autonomy"
            proofs=autonomy/"proofs"
            proofs.mkdir(parents=True)
            (root/"a.py").write_text("x=1\n")

            dag=new_dag("demo","x",{"work_items":["implement parser"]},"a"*40)
            dag=mark_running(dag,"task-1")
            dag=mark_verified(dag,"task-1",commit="b"*40,confidence=90)
            save_dag(autonomy/"objective-dag.json",dag)

            proof=build_task_proof(
                project_root=root,
                project_id="demo",
                task={"id":"task-1","title":"implement parser","done_when":["file:a.py"]},
                commit="b"*40,
                review={
                    "complete":True,
                    "criteria":[{
                        "criterion":"file:a.py",
                        "passed":True,
                        "evidence":"exists",
                        "evidence_refs":["a.py"],
                    }],
                },
                verification={"status":"passed","passed":True},
                confidence={"score":90},
            )
            save_task_proof(
                proofs/task_proof_filename("task-1","b"*40),
                proof,
            )
            manifest=build_release_proof(
                proof_dir=proofs,
                project_id="demo",
                objective_dag=dag,
                release_commit="b"*40,
                project_root=root,
            )
            save_release_proof(autonomy/"release-proof.json",manifest)

            status=inspect(root)
            self.assertEqual(status["status"],"complete")
            self.assertEqual(status["proofs"]["task_proof_count"],1)
            self.assertEqual(status["proofs"]["release_proof"]["task_count"],1)


if __name__=="__main__":
    unittest.main()

from pathlib import Path
import json
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from release_proof_manifest import ReleaseProofError, build, load, save
from task_proof_bundle import build as build_task_proof, filename as task_proof_filename, save as save_task_proof


class ReleaseProofManifestTests(unittest.TestCase):
    def _write_task_proof(self, root: Path, task_id: str, commit: str):
        project=root/"project"
        project.mkdir(exist_ok=True)
        source=project/f"{task_id}.py"
        source.write_text("x=1\n")
        proof=build_task_proof(
            project_root=project,
            project_id="demo",
            task={"id":task_id,"title":task_id,"done_when":[f"file:{task_id}.py"]},
            commit=commit,
            review={
                "complete":True,
                "criteria":[{
                    "criterion":f"file:{task_id}.py",
                    "passed":True,
                    "evidence":"exists",
                    "evidence_refs":[f"{task_id}.py"],
                    "source":"deterministic",
                }],
            },
            verification={"status":"passed","passed":True},
            confidence={"score":90},
        )
        proof_dir=root/"proofs"
        proof_dir.mkdir(exist_ok=True)
        path=proof_dir/task_proof_filename(task_id,commit)
        save_task_proof(path,proof)
        return proof_dir,path

    def test_builds_release_manifest_from_all_verified_task_proofs(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            proof_dir,_=self._write_task_proof(root,"core","a"*40)
            self._write_task_proof(root,"api","b"*40)
            dag={
                "tasks":[
                    {"id":"core","state":"verified","last_commit":"a"*40,"confidence":90,"critical":False},
                    {"id":"api","state":"verified","last_commit":"b"*40,"confidence":95,"critical":True},
                ]
            }
            manifest=build(
                proof_dir=proof_dir,
                project_id="demo",
                objective_dag=dag,
                release_commit="c"*40,
            )
            self.assertEqual(manifest["task_count"],2)
            self.assertEqual([x["task_id"] for x in manifest["tasks"]],["api","core"])
            path=root/"release-proof.json"
            save(path,manifest)
            self.assertEqual(load(path)["sha256"],manifest["sha256"])

    def test_missing_task_proof_blocks_release(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            proof_dir,_=self._write_task_proof(root,"core","a"*40)
            dag={
                "tasks":[
                    {"id":"core","state":"verified","last_commit":"a"*40},
                    {"id":"api","state":"verified","last_commit":"b"*40},
                ]
            }
            with self.assertRaisesRegex(ReleaseProofError,"missing: api"):
                build(
                    proof_dir=proof_dir,
                    project_id="demo",
                    objective_dag=dag,
                    release_commit="c"*40,
                )

    def test_tampered_task_proof_blocks_release(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            proof_dir,path=self._write_task_proof(root,"core","a"*40)
            value=json.loads(path.read_text())
            value["confidence"]["score"]=1
            path.write_text(json.dumps(value))
            dag={"tasks":[{"id":"core","state":"verified","last_commit":"a"*40}]}
            with self.assertRaisesRegex(ReleaseProofError,"invalid: core"):
                build(
                    proof_dir=proof_dir,
                    project_id="demo",
                    objective_dag=dag,
                    release_commit="c"*40,
                )


if __name__=="__main__":
    unittest.main()

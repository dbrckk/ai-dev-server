from pathlib import Path
import json
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from task_proof_bundle import TaskProofError, build, filename, load, save, verify_evidence_files


class TaskProofBundleTests(unittest.TestCase):
    def test_builds_and_persists_file_and_command_proof(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"src").mkdir()
            (root/"src"/"api.py").write_text("def run():\n    return 1\n")
            proof=build(
                project_root=root,
                project_id="demo",
                task={
                    "id":"api",
                    "title":"build api",
                    "critical":True,
                    "done_when":["symbol:src/api.py#run","build:default"],
                },
                commit="a"*40,
                review={
                    "complete":True,
                    "criteria":[
                        {
                            "criterion":"symbol:src/api.py#run",
                            "passed":True,
                            "evidence":"symbol found",
                            "evidence_refs":["src/api.py"],
                            "source":"deterministic",
                        },
                        {
                            "criterion":"build:default",
                            "passed":True,
                            "evidence":"build passed",
                            "evidence_refs":["command:npm run build"],
                            "source":"deterministic",
                        },
                    ],
                },
                verification={"status":"passed","passed":True,"commands":[["npm","run","build"]]},
                confidence={"score":95,"level":"high","factors":{}},
            )
            self.assertEqual(proof["evidence_files"][0]["ref"],"src/api.py")
            self.assertEqual(proof["evidence_commands"],["command:npm run build"])
            path=root/filename("api","a"*40)
            save(path,proof)
            restored=load(path)
            self.assertEqual(restored["sha256"],proof["sha256"])

    def test_missing_evidence_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaisesRegex(TaskProofError,"evidence file missing"):
                build(
                    project_root=root,
                    project_id="demo",
                    task={"id":"api","title":"api","done_when":["file:missing.py"]},
                    commit="a"*40,
                    review={
                        "complete":True,
                        "criteria":[{
                            "criterion":"file:missing.py",
                            "passed":True,
                            "evidence":"claimed",
                            "evidence_refs":["missing.py"],
                        }],
                    },
                    verification={"status":"passed","passed":True},
                    confidence={"score":80},
                )

    def test_absence_evidence_is_persisted_and_revalidated(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            proof=build(
                project_root=root,
                project_id="demo",
                task={"id":"cleanup","title":"cleanup","done_when":["absent:old.py"]},
                commit="c"*40,
                review={
                    "complete":True,
                    "criteria":[{
                        "criterion":"absent:old.py",
                        "passed":True,
                        "evidence":"path absent",
                        "evidence_refs":["absent:old.py"],
                        "source":"deterministic",
                    }],
                },
                verification={"status":"passed","passed":True},
                confidence={"score":90},
            )
            self.assertEqual(
                proof["evidence_states"],
                [{"ref":"absent:old.py","state":"absent"}],
            )
            self.assertEqual(verify_evidence_files(proof,root)["checked_states"],1)
            (root/"old.py").write_text("restored\n")
            with self.assertRaisesRegex(TaskProofError,"evidence mismatch"):
                verify_evidence_files(proof,root)

    def test_changed_evidence_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.py").write_text("x=1\n")
            proof=build(
                project_root=root,
                project_id="demo",
                task={"id":"a","title":"a","done_when":["file:a.py"]},
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
                confidence={"score":80},
            )
            (root/"a.py").write_text("x=2\n")
            with self.assertRaisesRegex(TaskProofError,"evidence mismatch"):
                verify_evidence_files(proof,root)

    def test_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.py").write_text("x=1\n")
            proof=build(
                project_root=root,
                project_id="demo",
                task={"id":"a","title":"a","done_when":["file:a.py"]},
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
                confidence={"score":80},
            )
            path=root/"proof.json"
            save(path,proof)
            value=json.loads(path.read_text())
            value["confidence"]["score"]=1
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(TaskProofError,"integrity"):
                load(path)


if __name__=="__main__":
    unittest.main()

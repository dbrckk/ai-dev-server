from pathlib import Path
import json
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from objective_dag import (
    ObjectiveDagError,
    load,
    mark_failed,
    mark_running,
    mark_verified,
    new,
    next_task,
    resume,
    save,
    summary,
)


class ObjectiveDagTests(unittest.TestCase):
    def test_legacy_work_items_become_sequential_tasks(self):
        dag=new(
            "demo",
            "build feature",
            {"objective":"build feature","work_items":["core","api","tests"]},
            "a"*40,
        )
        info=summary(dag)
        self.assertEqual(info["tasks"][0]["state"],"ready")
        self.assertEqual(info["tasks"][1]["state"],"blocked")
        self.assertEqual(info["tasks"][1]["depends_on"],["task-1"])

    def test_explicit_dependencies_unlock_after_verified_commit(self):
        dag=new(
            "demo",
            "build feature",
            {
                "objective":"build feature",
                "tasks":[
                    {"id":"core","title":"core","depends_on":[]},
                    {"id":"api","title":"api","depends_on":["core"]},
                ],
            },
            "a"*40,
        )
        dag=mark_running(dag,"core")
        dag=mark_verified(dag,"core",commit="b"*40)
        self.assertEqual(next_task(dag)["id"],"api")

    def test_running_task_resumes_as_ready_after_restart(self):
        dag=new("demo","x",{"work_items":["one"]},"a"*40)
        dag=mark_running(dag,"task-1")
        restored=resume(dag,project_id="demo",brief="x",head_sha="a"*40)
        self.assertEqual(next_task(restored)["state"],"ready")
        self.assertEqual(next_task(restored)["attempts"],1)

    def test_failed_task_is_retryable(self):
        dag=new("demo","x",{"work_items":["one"]},"a"*40)
        dag=mark_running(dag,"task-1")
        dag=mark_failed(dag,"task-1",error="tests failed")
        self.assertEqual(next_task(dag)["state"],"failed")
        dag=mark_running(dag,"task-1")
        self.assertEqual(summary(dag)["counts"]["running"],1)

    def test_cycle_is_rejected(self):
        with self.assertRaisesRegex(ObjectiveDagError,"cyclic"):
            new(
                "demo",
                "x",
                {
                    "tasks":[
                        {"id":"a","title":"a","depends_on":["b"]},
                        {"id":"b","title":"b","depends_on":["a"]},
                    ]
                },
                "a"*40,
            )

    def test_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"dag.json"
            save(path,new("demo","x",{"work_items":["one"]},"a"*40))
            value=json.loads(path.read_text())
            value["tasks"][0]["state"]="verified"
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(ObjectiveDagError,"integrity"):
                load(path)


if __name__=="__main__":
    unittest.main()

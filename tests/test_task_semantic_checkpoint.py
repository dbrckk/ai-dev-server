from pathlib import Path
import json
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from task_semantic_checkpoint import (
    TaskSemanticCheckpointError,
    load,
    new,
    record,
    resume,
    save,
    task_context,
    retry_policy,
)


class TaskSemanticCheckpointTests(unittest.TestCase):
    def test_records_verified_attempt_evidence(self):
        state=new("demo","a"*64,"b"*40)
        state=record(
            state,
            task_id="core",
            task_title="build core",
            commit="c"*40,
            status="verified",
            changed_files=["src/core.py"],
            impacted_tests=["tests/test_core.py"],
            models=[{"provider":"p1","model":"m1"}],
            agents=["agent-a"],
            failure_signature=None,
            verification={"status":"passed","passed":True,"elapsed_seconds":4.2,"stability_confirmed":True},
            dependency_context={"level":"medium","max_coupling":5,"impacted_tests":["tests/test_core.py"]},
        )
        ctx=task_context(state,"core")
        self.assertEqual(ctx["last_status"],"verified")
        self.assertEqual(ctx["last_commit"],"c"*40)
        self.assertEqual(ctx["recent_attempts"][0]["changed_files"],["src/core.py"])
        self.assertEqual(ctx["recent_attempts"][0]["impacted_tests"],["tests/test_core.py"])

    def test_failed_attempt_is_resumable(self):
        state=new("demo","a"*64,"b"*40)
        state=record(
            state,
            task_id="api",
            task_title="build api",
            commit=None,
            status="failed",
            changed_files=["src/api.py"],
            impacted_tests=[],
            models=[],
            agents=[],
            failure_signature="d"*64,
            verification={"status":"failed","passed":False},
            dependency_context={"level":"low","max_coupling":1,"impacted_tests":[]},
        )
        resumed=resume(state,project_id="demo",objective_sha256="a"*64,head_sha="e"*40)
        ctx=task_context(resumed,"api")
        self.assertEqual(ctx["last_status"],"failed")
        self.assertEqual(ctx["recent_attempts"][0]["failure_signature"],"d"*64)

    def test_retry_policy_avoids_recent_failed_routes(self):
        state=new("demo","a"*64,"b"*40)
        for provider,model,agent in [("p1","m1","a1"),("p2","m2","a2")]:
            state=record(
                state,
                task_id="api",
                task_title="build api",
                commit=None,
                status="failed",
                changed_files=["src/api.py"],
                impacted_tests=[],
                models=[{"provider":provider,"model":model}],
                agents=[agent],
                failure_signature="d"*64,
                verification={"status":"failed","passed":False},
                dependency_context={"level":"low","max_coupling":1,"impacted_tests":[]},
            )
        policy=retry_policy(state,"api")
        self.assertEqual(policy["failed_attempts"],2)
        self.assertEqual(policy["avoid_agents"],["a1","a2"])
        self.assertEqual(policy["avoid_providers"],["p1","p2"])
        self.assertEqual(policy["avoid_models"],["m1","m2"])
        self.assertEqual(policy["repeated_failure_signature"],"d"*64)

    def test_verified_attempts_do_not_pollute_retry_policy(self):
        state=new("demo","a"*64,"b"*40)
        state=record(
            state,
            task_id="core",
            task_title="core",
            commit="c"*40,
            status="verified",
            changed_files=["core.py"],
            impacted_tests=[],
            models=[{"provider":"p1","model":"m1"}],
            agents=["a1"],
            failure_signature=None,
            verification={"status":"passed","passed":True},
            dependency_context={"level":"low","max_coupling":0,"impacted_tests":[]},
        )
        policy=retry_policy(state,"core")
        self.assertEqual(policy["failed_attempts"],0)
        self.assertEqual(policy["avoid_agents"],[])
        self.assertEqual(policy["avoid_models"],[])

    def test_identity_mismatch_resets(self):
        state=new("demo","a"*64,"b"*40)
        reset=resume(state,project_id="demo",objective_sha256="f"*64,head_sha="c"*40)
        self.assertEqual(reset["tasks"],{})
        self.assertEqual(reset["head_sha"],"c"*40)

    def test_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"semantic.json"
            save(path,new("demo","a"*64,"b"*40))
            value=json.loads(path.read_text())
            value["tasks"]["evil"]={"attempts":[]}
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(TaskSemanticCheckpointError,"integrity"):
                load(path)


if __name__=="__main__":
    unittest.main()

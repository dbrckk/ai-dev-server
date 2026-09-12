import base64
import json
from pathlib import Path
import tempfile
import unittest

from studio.capability_registry import new_registry
from studio.github_goal_store import (
    RemoteStateError,
    _validate_candidate_validation_link,
    load,
    persist_local,
    restore_local,
    save,
)
from studio.goal_engine import new_goal
from studio.improvement_backlog import new_backlog


class FakeGitHub:
    def __init__(self):
        self.repo="/repos/owner/control"
        self.ref=None
        self.default="d"*40
        self.commits={self.default:{"tree":{"sha":"e"*40}}}
        self.trees={self.default:[]}
        self.blobs={}
        self.calls=[]

    def get(self,path):
        if path=="/git/matching-refs/heads/studio-autonomy-state":
            return [] if self.ref is None else [{"ref":"refs/heads/studio-autonomy-state","object":{"sha":self.ref}}]
        if path=="":
            return {"default_branch":"main"}
        if path=="/branches/main":
            return {"commit":{"sha":self.default}}
        if path.startswith("/git/commits/"):
            sha=path.rsplit("/",1)[-1]
            return self.commits[sha]
        if path.startswith("/git/trees/"):
            sha=path.split("/git/trees/",1)[1].split("?",1)[0]
            return {"tree":self.trees.get(sha,[]),"truncated":False}
        if path.startswith("/git/blobs/"):
            return self.blobs[path.rsplit("/",1)[-1]]
        raise AssertionError(path)

    def call(self,method,path,payload=None):
        self.calls.append((method,path,payload))
        if path.endswith("/git/trees"):
            sha=("1"*39)+str(len(self.calls)%10)
            base=payload["base_tree"]
            entries=[]
            for entry in payload["tree"]:
                content=entry["content"].encode()
                bsha=("2"*39)+str(len(self.blobs)%10)
                self.blobs[bsha]={"encoding":"base64","content":base64.b64encode(content).decode()}
                entries.append({"path":entry["path"],"type":"blob","sha":bsha})
            self.trees[sha]=entries
            return {"sha":sha}
        if path.endswith("/git/commits"):
            sha=("3"*39)+str(len(self.calls)%10)
            self.commits[sha]={"tree":{"sha":payload["tree"]}}
            self.trees[sha]=self.trees[payload["tree"]]
            return {"sha":sha}
        if path.endswith("/git/refs"):
            self.ref=payload["sha"]; return {}
        if "/git/refs/heads/studio-autonomy-state" in path:
            self.ref=payload["sha"]; return {}
        raise AssertionError((method,path,payload))


def goal():
    return new_goal("demo","Complete demo",[{"name":"done","required_evidence":["proof"]}],max_attempts=5)


class GitHubGoalStoreTests(unittest.TestCase):
    def test_save_and_load_round_trip(self):
        gh=FakeGitHub()
        sha=save(gh,"demo",goal(),new_registry(),new_backlog())
        self.assertEqual(sha,gh.ref)
        restored=load(gh,"demo")
        self.assertEqual(restored["goal"]["goal_id"],"demo")
        self.assertEqual(restored["registry"]["capabilities"],{})
        self.assertEqual(restored["backlog"]["items"],[])

    def test_missing_remote_state_returns_none(self):
        self.assertIsNone(load(FakeGitHub(),"demo"))

    def test_invalid_project_id_rejected(self):
        with self.assertRaisesRegex(RemoteStateError,"project id"):
            load(FakeGitHub(),"../escape")

    def test_validation_requires_persisted_candidate(self):
        validation={"candidate_id":"candidate:a","candidate_sha256":"a"*64}
        with self.assertRaisesRegex(RemoteStateError,"missing candidate"):
            _validate_candidate_validation_link(None,validation)

    def test_validation_must_match_persisted_candidate(self):
        candidate={"candidate_id":"candidate:a","candidate_sha256":"a"*64}
        validation={"candidate_id":"candidate:b","candidate_sha256":"a"*64}
        with self.assertRaisesRegex(RemoteStateError,"candidate mismatch"):
            _validate_candidate_validation_link(candidate,validation)

    def test_validation_link_accepts_exact_candidate_identity(self):
        candidate={"candidate_id":"candidate:a","candidate_sha256":"a"*64}
        validation={"candidate_id":"candidate:a","candidate_sha256":"a"*64}
        self.assertIsNone(_validate_candidate_validation_link(candidate,validation))

    def test_remote_validation_without_candidate_fails_closed(self):
        gh=FakeGitHub()
        save(gh,"demo",goal(),new_registry(),new_backlog())
        # Simulate an independently injected validation blob without a candidate.
        tree=gh.trees[gh.ref]
        validation={"candidate_id":"candidate:a","candidate_sha256":"a"*64}
        raw=json.dumps(validation).encode()
        sha="9"*40
        gh.blobs[sha]={"encoding":"base64","content":base64.b64encode(raw).decode()}
        tree.append({
            "path":".studio-autonomy/demo/capability-validation.json",
            "type":"blob",
            "sha":sha,
        })
        with self.assertRaises(Exception):
            load(gh,"demo")

    def test_local_restore_and_persist(self):
        gh=FakeGitHub(); save(gh,"demo",goal(),new_registry(),new_backlog())
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            self.assertTrue(restore_local(gh,"demo",out))
            self.assertTrue((out/".autonomy/goal.json").is_file())
            self.assertTrue((out/".autonomy/improvement-backlog.json").is_file())
            persist_local(gh,"demo",out)
            self.assertIsNotNone(gh.ref)


    def test_improvement_goal_round_trip_and_restore(self):
        gh=FakeGitHub()
        improvement=new_goal(
            "improvement:test",
            "Prove improvement",
            [{"name":"proved","required_evidence":["regression"]}],
            max_attempts=4,
        )
        save(gh,"demo",goal(),new_registry(),new_backlog(),improvement)
        restored=load(gh,"demo")
        self.assertEqual(restored["improvement_goal"]["goal_id"],"improvement:test")
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            self.assertTrue(restore_local(gh,"demo",out))
            path=out/".autonomy/improvement-goal.json"
            self.assertTrue(path.is_file())
            self.assertEqual(json.loads(path.read_text())["goal_id"],"improvement:test")


if __name__=="__main__":
    unittest.main()

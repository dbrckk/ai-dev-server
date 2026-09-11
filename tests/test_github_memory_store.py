import base64
import json
from pathlib import Path
import tempfile
import unittest

from studio.github_memory_store import GitHubMemoryError, load, persist_local, restore_local, save
from studio.project_memory import add_entry, new_memory


class FakeGitHub:
    def __init__(self):
        self.repo="/repos/owner/control"
        self.ref=None
        self.default="a"*40
        self.commits={self.default:{"tree":{"sha":"b"*40}}}
        self.trees={self.default:[]}
        self.blobs={}
        self.calls=[]

    def get(self,path):
        if path=="/git/matching-refs/heads/studio-project-memory":
            return [] if self.ref is None else [{"ref":"refs/heads/studio-project-memory","object":{"sha":self.ref}}]
        if path=="":
            return {"default_branch":"main"}
        if path=="/branches/main":
            return {"commit":{"sha":self.default}}
        if path.startswith("/git/commits/"):
            return self.commits[path.rsplit("/",1)[-1]]
        if path.startswith("/git/trees/"):
            sha=path.split("/git/trees/",1)[1].split("?",1)[0]
            return {"tree":self.trees.get(sha,[]),"truncated":False}
        if path.startswith("/git/blobs/"):
            return self.blobs[path.rsplit("/",1)[-1]]
        raise AssertionError(path)

    def call(self,method,path,payload=None):
        self.calls.append((method,path,payload))
        if path.endswith("/git/trees"):
            sha=("c"*39)+str(len(self.calls)%10)
            content=payload["tree"][0]["content"].encode()
            bsha=("d"*39)+str(len(self.blobs)%10)
            self.blobs[bsha]={"encoding":"base64","content":base64.b64encode(content).decode()}
            self.trees[sha]=[{"path":".studio-memory/memory.json","type":"blob","sha":bsha}]
            return {"sha":sha}
        if path.endswith("/git/commits"):
            sha=("e"*39)+str(len(self.calls)%10)
            self.commits[sha]={"tree":{"sha":payload["tree"]}}
            self.trees[sha]=self.trees[payload["tree"]]
            return {"sha":sha}
        if path.endswith("/git/refs"):
            self.ref=payload["sha"]; return {}
        if "/git/refs/heads/studio-project-memory" in path:
            self.ref=payload["sha"]; return {}
        raise AssertionError((method,path,payload))


def populated():
    return add_entry(
        new_memory(),
        entry_id="exp-1",
        kind="experience",
        project_id="app-a",
        summary="Validated reusable release recovery.",
        tags=["release"],
        evidence={"tests_passed":True,"regression_suite_passed":True,"commit_sha":"f"*40},
        provenance={"source":"validated_project_execution"},
        reusable=True,
        confidence=95,
    )


class GitHubMemoryStoreTests(unittest.TestCase):
    def test_empty_store_returns_new_memory(self):
        self.assertEqual(load(FakeGitHub())["entries"],[])

    def test_save_and_load_round_trip(self):
        gh=FakeGitHub(); memory=populated()
        sha=save(gh,memory)
        self.assertEqual(sha,gh.ref)
        self.assertEqual(load(gh),memory)

    def test_unchanged_memory_does_not_create_new_commit(self):
        gh=FakeGitHub(); memory=populated(); save(gh,memory)
        calls=len(gh.calls); head=gh.ref
        self.assertEqual(save(gh,memory),head)
        self.assertEqual(len(gh.calls),calls)

    def test_restore_and_persist_local(self):
        gh=FakeGitHub(); save(gh,populated())
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"memory.json"
            restore_local(gh,p)
            self.assertTrue(p.is_file())
            self.assertEqual(persist_local(gh,p),gh.ref)


if __name__=="__main__":
    unittest.main()

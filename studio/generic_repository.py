"""Bounded GitHub snapshot/publish backend for generic projects."""
from __future__ import annotations
import base64
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from core import StudioError, SECRET, NoRedirect
from generic_policy import editable

MAX_FILES=500
MAX_TOTAL=6_000_000

class GenericRepository:
    def __init__(self,github,repo:str,project_id:str):
        self.github=github; self.repo=repo; self.project_id=project_id; self.branch="studio/"+project_id
        self.default_branch=None

    def _tree(self,sha:str)->dict:
        tree=self.github.get("/git/trees/"+sha+"?recursive=1")
        if not isinstance(tree,dict) or tree.get("truncated") or not isinstance(tree.get("tree"),list):
            raise StudioError("Generic repository tree unavailable or truncated")
        return tree

    def restore(self,root:Path)->tuple[str,dict]:
        metadata=self.github.get("")
        if not isinstance(metadata,dict) or metadata.get("archived"):
            raise StudioError("Target repository unavailable or archived")
        refs=self.github.get("/git/matching-refs/heads/"+self.branch)
        exact=[r for r in refs if isinstance(r,dict) and r.get("ref")=="refs/heads/"+self.branch]
        if exact:
            source=exact[0].get("object",{}).get("sha")
        else:
            default=metadata.get("default_branch")
            if metadata.get("size",0)==0:
                init=self.github.call("PUT",self.github.repo+"/contents/README.md",{
                    "message":"Initialize autonomous project target",
                    "content":base64.b64encode(b"# Autonomous project\n").decode(),
                })
                source=init.get("commit",{}).get("sha") if isinstance(init,dict) else None
                root.mkdir(parents=True,exist_ok=True)
                (root/"README.md").write_text("# Autonomous project\n",encoding="utf-8")
                return source,{"source_sha":source,"files":1,"bytes":21,"initialized":True}
            if not isinstance(default,str) or not default:
                raise StudioError("Generic repository default branch missing")
            source=self.github.get("/branches/"+default).get("commit",{}).get("sha")
        if not isinstance(source,str) or len(source)!=40:
            raise StudioError("Generic repository source revision invalid")

        tree=self._tree(source)
        root.mkdir(parents=True,exist_ok=True)
        count=total=0
        for item in tree["tree"]:
            path=item.get("path")
            if item.get("type")!="blob" or not isinstance(path,str) or not editable(path):
                continue
            size=item.get("size",0)
            if not isinstance(size,int) or size<0 or size>400_000:
                continue
            if count>=MAX_FILES or total+size>MAX_TOTAL:
                break
            blob=self.github.get("/git/blobs/"+item["sha"])
            try:
                text=base64.b64decode(blob["content"]).decode("utf-8")
            except Exception:
                continue
            if SECRET.search(text):
                continue
            target=root/path
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(text,encoding="utf-8")
            count+=1
            total+=len(text.encode("utf-8"))
        if not any(root.rglob("*")):
            raise StudioError("No editable text source could be restored")
        return source,{"source_sha":source,"files":count,"bytes":total}

    def ensure_pull_request(self, *, title: str, body: str = "") -> dict:
        metadata = self.github.get("")
        default = metadata.get("default_branch") if isinstance(metadata, dict) else None
        if not isinstance(default, str) or not default:
            raise StudioError("Generic repository default branch missing")
        self.default_branch=default

        pulls = self.github.get("/pulls?state=open&per_page=100")
        if not isinstance(pulls, list):
            raise StudioError("Generic pull request listing unavailable")
        for pr in pulls:
            if not isinstance(pr, dict):
                continue
            head = pr.get("head") if isinstance(pr.get("head"), dict) else {}
            base = pr.get("base") if isinstance(pr.get("base"), dict) else {}
            if head.get("ref") == self.branch and base.get("ref") == default:
                return {
                    "number":pr.get("number"),
                    "state":pr.get("state") or "open",
                    "url":pr.get("html_url"),
                    "head":self.branch,
                    "base":default,
                    "reused":True,
                }

        created = self.github.call(
            "POST",
            self.github.repo + "/pulls",
            {
                "title":str(title or "Autonomous managed project")[:240],
                "head":self.branch,
                "base":default,
                "body":str(body or "")[:12000],
            },
        )
        if not isinstance(created, dict) or created.get("number") is None:
            raise StudioError("Generic pull request creation failed")
        return {
            "number":created.get("number"),
            "state":created.get("state") or "open",
            "url":created.get("html_url"),
            "head":self.branch,
            "base":default,
            "reused":False,
        }

    def request_trusted_review_handoff(self, commit_sha: str) -> dict:
        """Ask an explicitly opted-in target to create its own draft PR.

        The source credential may publish commits but lack pull-request write
        privileges. A repository_dispatch accepted by GitHub is a request,
        never evidence that a pull request exists or a release is complete.
        Only the trusted target has installed the handoff workflow.
        """
        if self.repo != "dbrckk/repo-standards":
            return {"status": "not_configured"}
        if not re.fullmatch(r"studio/mp-[a-f0-9]{24}", self.branch):
            return {"status": "invalid_branch"}
        if not isinstance(commit_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", commit_sha):
            return {"status": "invalid_commit"}
        token = str(getattr(self.github, "key", "") or "").strip()
        if not token:
            return {"status": "missing_token"}
        request = urllib.request.Request(
            "https://api.github.com/repos/dbrckk/repo-standards/dispatches",
            method="POST",
            data=json.dumps({
                "event_type": "production_os_review_handoff",
                "client_payload": {
                    "branch": self.branch,
                    "commit_sha": commit_sha,
                },
            }).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + token,
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "production-os-studio-review-handoff",
            },
        )
        try:
            # Do not retry a POST after an ambiguous timeout: duplicates can
            # happen, and the receiver already checks for an existing PR.
            with urllib.request.build_opener(NoRedirect()).open(
                request, timeout=20
            ) as response:
                if response.status != 204:
                    return {"status": "unexpected_response"}
        except urllib.error.HTTPError as exc:
            return {"status": "rejected", "http_status": exc.code}
        except (urllib.error.URLError, TimeoutError, StudioError, OSError):
            return {"status": "unavailable"}
        return {"status": "accepted"}

    def publish(self,base_sha:str,root:Path,message:str)->str:
        base_tree=self.github.get("/git/commits/"+base_sha).get("tree",{}).get("sha")
        if not isinstance(base_tree,str):
            raise StudioError("Generic base tree unavailable")
        entries=[]
        for p in sorted(root.rglob("*")):
            if not p.is_file() or p.is_symlink():
                continue
            rel=p.relative_to(root).as_posix()
            if not editable(rel):
                continue
            raw=p.read_bytes()
            if len(raw)>400_000:
                continue
            try:
                text=raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
            if SECRET.search(text):
                raise StudioError("Generic publication rejected a credential pattern")
            entries.append({"path":rel,"mode":"100644","type":"blob","content":text})

        tree=self.github.call("POST",self.github.repo+"/git/trees",{"base_tree":base_tree,"tree":entries})
        commit=self.github.call("POST",self.github.repo+"/git/commits",{"message":message,"tree":tree["sha"],"parents":[base_sha]})
        refs=self.github.get("/git/matching-refs/heads/"+self.branch)
        exists=any(r.get("ref")=="refs/heads/"+self.branch for r in refs if isinstance(r,dict))
        if exists:
            self.github.call("PATCH",self.github.repo+"/git/refs/heads/"+self.branch,{"sha":commit["sha"],"force":False})
        else:
            self.github.call("POST",self.github.repo+"/git/refs",{"ref":"refs/heads/"+self.branch,"sha":commit["sha"]})
        return commit["sha"]

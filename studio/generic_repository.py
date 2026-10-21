"""Bounded GitHub snapshot/publish backend for generic projects."""
from __future__ import annotations
import base64
import json
import re
import urllib.error
import urllib.request
from urllib.parse import quote
from pathlib import Path
from core import StudioError, SECRET, NoRedirect
from generic_policy import editable

MAX_FILES=500
MAX_TOTAL=6_000_000

# Only targets that have an independently reviewed default-branch
# repository_dispatch workflow may request a GitHub-token PR handoff.
TRUSTED_REVIEW_TARGETS = frozenset({
    "dbrckk/repo-standards",
    "dbrckk/Jumpy",
    "dbrckk/star-list",
    "dbrckk/Ai-trading",
})

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

    def restore_approved_source(self, root: Path, path: str) -> tuple[str, dict]:
        """Restore exactly one allowlisted public source file, not an entire repo.

        Normal generic projects still use restore().  The separate
        operator-approved source lane must not request hundreds of unrelated
        blobs, spend quota reading them or publish incidental file changes.
        """
        if not editable(path) or not path.startswith("scripts/"):
            raise StudioError("Approved source path rejected")
        metadata = self.github.get("")
        if (not isinstance(metadata, dict) or metadata.get("private") is not False
                or metadata.get("archived") or metadata.get("default_branch") != "main"):
            raise StudioError("Approved source must have a public main branch")
        self.default_branch = "main"
        refs = self.github.get("/git/matching-refs/heads/" + self.branch)
        if not isinstance(refs, list):
            raise StudioError("Approved branch refs unavailable")
        matches = [r for r in refs if isinstance(r, dict)
                   and r.get("ref") == "refs/heads/" + self.branch]
        if len(matches) > 1:
            raise StudioError("Approved source branch ref ambiguous")
        if matches:
            branch_head = matches[0].get("object")
            if not isinstance(branch_head, dict):
                raise StudioError("Approved source branch revision unavailable")
            base_sha = branch_head.get("sha")
        else:
            base_sha = self.github.get("/branches/main").get("commit", {}).get("sha")
        if not isinstance(base_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", base_sha):
            raise StudioError("Approved source revision invalid")
        response = self.github.get("/contents/" + quote(path, safe="/") + "?ref=" + base_sha)
        if (not isinstance(response, dict) or response.get("type") != "file"
                or response.get("path") != path or response.get("encoding") != "base64"
                or not isinstance(response.get("content"), str)
                or type(response.get("size")) is not int
                or not 1 <= response["size"] <= 400_000
                or not isinstance(response.get("sha"), str)
                or not re.fullmatch(r"[a-f0-9]{40}", response["sha"])):
            raise StudioError("Approved source response invalid")
        try:
            raw = base64.b64decode(
                "".join(response["content"].split()), validate=True,
            )
            content = raw.decode("utf-8")
        except (ValueError, UnicodeError, base64.binascii.Error) as exc:
            raise StudioError("Approved source encoding invalid") from exc
        if len(raw) != response["size"] or SECRET.search(content) or "\\x00" in content:
            raise StudioError("Approved source content unsafe")
        destination = root / path
        if any(item.is_symlink() for item in (root, *destination.parents)):
            raise StudioError("Approved source directory unsafe")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() or destination.is_symlink():
            raise StudioError("Approved source workspace not empty")
        destination.write_bytes(raw)
        return base_sha, {
            "source_sha": base_sha, "files": 1, "bytes": len(raw),
            "source_blob_sha": response["sha"], "source_path": path,
        }

    def publish_approved_source(self, base_sha: str, root: Path, path: str,
                                message: str) -> str:
        """Publish only the approved file, verify the branch and exact diff."""
        if (not editable(path) or not path.startswith("scripts/")
                or not isinstance(base_sha, str)
                or not re.fullmatch(r"[a-f0-9]{40}", base_sha)):
            raise StudioError("Approved publication source invalid")
        target = root / path
        if (not target.is_file() or target.is_symlink()
                or any(item.is_symlink() for item in (root, *target.parents))):
            raise StudioError("Approved publication file missing or symlinked")
        raw = target.read_bytes()
        if not 1 <= len(raw) <= 400_000:
            raise StudioError("Approved publication size invalid")
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise StudioError("Approved publication encoding invalid") from exc
        if SECRET.search(content) or "\\x00" in content:
            raise StudioError("Approved publication contains unsafe content")

        refs = self.github.get("/git/matching-refs/heads/" + self.branch)
        if not isinstance(refs, list):
            raise StudioError("Approved publication refs unavailable")
        existing = [r for r in refs if isinstance(r, dict)
                    and r.get("ref") == "refs/heads/" + self.branch]
        if len(existing) > 1:
            raise StudioError("Approved publication ambiguous branch")
        if existing:
            obj = existing[0].get("object")
            if not isinstance(obj, dict) or obj.get("sha") != base_sha:
                raise StudioError("Approved publication branch moved")
        elif self.github.get("/branches/main").get("commit", {}).get("sha") != base_sha:
            raise StudioError("Approved publication main branch moved")
        tree_sha = self.github.get("/git/commits/" + base_sha).get("tree", {}).get("sha")
        if not isinstance(tree_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", tree_sha):
            raise StudioError("Approved publication base tree invalid")
        tree = self.github.call("POST", self.github.repo + "/git/trees", {
            "base_tree": tree_sha,
            "tree": [{"path": path, "mode": "100644", "type": "blob", "content": content}],
        })
        if not isinstance(tree, dict) or not re.fullmatch(r"[a-f0-9]{40}", str(tree.get("sha") or "")):
            raise StudioError("Approved publication tree invalid")
        commit = self.github.call("POST", self.github.repo + "/git/commits", {
            "message": str(message or "Approved source change")[:220],
            "tree": tree["sha"], "parents": [base_sha],
        })
        sha = commit.get("sha") if isinstance(commit, dict) else None
        if not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{40}", sha):
            raise StudioError("Approved publication commit invalid")
        delta = self.github.get("/compare/" + base_sha + "..." + sha)
        files = delta.get("files") if isinstance(delta, dict) else None
        if (not isinstance(files, list) or len(files) != 1
                or files[0].get("filename") != path
                or files[0].get("status") != "modified"):
            raise StudioError("Approved publication changed unexpected files")
        if existing:
            self.github.call("PATCH", self.github.repo + "/git/refs/heads/" + self.branch,
                             {"sha": sha, "force": False})
        else:
            self.github.call("POST", self.github.repo + "/git/refs",
                             {"ref": "refs/heads/" + self.branch, "sha": sha})
        attested = self.github.get("/git/matching-refs/heads/" + self.branch)
        if not isinstance(attested, list) or not any(
            isinstance(ref, dict)
            and ref.get("ref") == "refs/heads/" + self.branch
            and isinstance(ref.get("object"), dict)
            and ref["object"].get("sha") == sha for ref in attested
        ):
            raise StudioError("Approved publication exact branch SHA unverified")
        return sha

    def _find_open_pull_request(self, *, expected_sha: str | None = None) -> dict | None:
        """Read-only lookup; optional SHA pins a trusted async review handoff."""
        metadata = self.github.get("")
        default = metadata.get("default_branch") if isinstance(metadata, dict) else None
        if not isinstance(default, str) or not default:
            raise StudioError("Generic repository default branch missing")
        self.default_branch = default
        owner = self.repo.split("/", 1)[0]
        # Server-side branch filtering avoids missing a PR amid many others.
        filter_head = quote(owner + ":" + self.branch, safe="")
        filter_base = quote(default, safe="")
        pulls = self.github.get(
            "/pulls?state=open&head=" + filter_head
            + "&base=" + filter_base + "&per_page=100"
        )
        if not isinstance(pulls, list):
            raise StudioError("Generic pull request listing unavailable")
        for pr in pulls:
            if not isinstance(pr, dict):
                continue
            head = pr.get("head") if isinstance(pr.get("head"), dict) else {}
            base = pr.get("base") if isinstance(pr.get("base"), dict) else {}
            head_repo = head.get("repo") if isinstance(head.get("repo"), dict) else {}
            base_repo = base.get("repo") if isinstance(base.get("repo"), dict) else {}
            if (
                head.get("ref") == self.branch
                and base.get("ref") == default
                and str(head_repo.get("full_name") or "").casefold() == self.repo.casefold()
                and str(base_repo.get("full_name") or "").casefold() == self.repo.casefold()
                and (expected_sha is None or head.get("sha") == expected_sha)
                and type(pr.get("number")) is int
                and isinstance(pr.get("html_url"), str)
                and pr["html_url"] == "https://github.com/" + self.repo + "/pull/" + str(pr["number"])
            ):
                return {
                    "number":pr["number"],
                    "state":pr.get("state") or "open",
                    "url":pr["html_url"],
                    "head":self.branch,
                    "base":default,
                    "reused":True,
                }
        return None

    def await_trusted_review(self, expected_sha: str) -> dict | None:
        """Read-only bounded confirmation; an accepted dispatch is not a PR."""
        if self.repo not in TRUSTED_REVIEW_TARGETS:
            return None
        if not re.fullmatch(r"studio/mp-[a-f0-9]{24}", self.branch):
            return None
        if not isinstance(expected_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", expected_sha):
            return None
        import time
        # repository_dispatch only queues a target GitHub Actions workflow.
        # Production canaries demonstrated that target job scheduling and
        # startup can exceed the former 9-second confirmation window.
        # Allow up to three minutes for an independently created PR, without
        # ever retrying POST or relaxing exact-repository/commit checks.
        attempts = 13
        for attempt in range(attempts):
            try:
                confirmed = self._find_open_pull_request(expected_sha=expected_sha)
            except StudioError:
                confirmed = None
            if confirmed is not None:
                return {**confirmed, "reused": False, "handoff_confirmed": True}
            if attempt + 1 < attempts:
                time.sleep(15)
        return None

    def ensure_pull_request(self, *, title: str, body: str = "", expected_sha: str | None = None) -> dict:
        # A prior PR at the same branch is not proof that this checkpoint
        # reached review. Pin both reuse and direct creation to its exact SHA.
        if expected_sha is not None and (
            not isinstance(expected_sha, str)
            or not re.fullmatch(r"[a-f0-9]{40}", expected_sha)
        ):
            raise StudioError("Generic review commit SHA invalid")
        existing = self._find_open_pull_request(expected_sha=expected_sha)
        if existing is not None:
            return existing
        if expected_sha is not None and self._find_open_pull_request() is not None:
            # GitHub allows only one open PR per same head/base. Do not
            # create a duplicate or misreport a stale PR as this checkpoint.
            raise StudioError("Generic review pull request head revision unverified")
        default = self.default_branch
        created = self.github.call(
            "POST",
            self.github.repo + "/pulls",
            {
                "title":str(title or "Autonomous managed project")[:240],
                "head":self.branch,
                "base":default,
                "body":str(body or "")[:12000],
                # Autonomous code is never ready for unreviewed merging.
                "draft":True,
            },
        )
        # A successful POST alone is not a verified review destination.
        # Match the exact GitHub PR identity, branch and draft state before
        # allowing downstream workflow status to count this as delivered.
        pr_number = created.get("number") if isinstance(created, dict) else None
        pr_head = created.get("head") if isinstance(created, dict) else None
        pr_base = created.get("base") if isinstance(created, dict) else None
        pr_head = pr_head if isinstance(pr_head, dict) else {}
        pr_base = pr_base if isinstance(pr_base, dict) else {}
        head_repo = pr_head.get("repo") if isinstance(pr_head.get("repo"), dict) else {}
        base_repo = pr_base.get("repo") if isinstance(pr_base.get("repo"), dict) else {}
        if (
            type(pr_number) is not int or pr_number < 1
            or created.get("html_url") != "https://github.com/" + self.repo + "/pull/" + str(pr_number)
            or created.get("draft") is not True
            or created.get("state") != "open"
            or pr_head.get("ref") != self.branch
            or (expected_sha is not None and pr_head.get("sha") != expected_sha)
            or pr_base.get("ref") != default
            or str(head_repo.get("full_name") or "").casefold() != self.repo.casefold()
            or str(base_repo.get("full_name") or "").casefold() != self.repo.casefold()
        ):
            raise StudioError("Generic review pull request receipt unverified")
        return {
            "number":pr_number,
            "state":"open",
            "url":created["html_url"],
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
        if self.repo not in TRUSTED_REVIEW_TARGETS:
            return {"status": "not_configured"}
        if not re.fullmatch(r"studio/mp-[a-f0-9]{24}", self.branch):
            return {"status": "invalid_branch"}
        if not isinstance(commit_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", commit_sha):
            return {"status": "invalid_commit"}
        token = str(getattr(self.github, "key", "") or "").strip()
        if not token:
            return {"status": "missing_token"}
        request = urllib.request.Request(
            "https://api.github.com/repos/" + self.repo + "/dispatches",
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
        # Publishing a restored text snapshot must not silently chmod every
        # executable script to 100644. GitHub compares modes as real changes,
        # which can break one-file delivery contracts and target CI.
        # Obtain modes from this exact parent revision (not the live branch).
        parent_modes = {
            item["path"]: item["mode"]
            for item in self._tree(base_sha)["tree"]
            if item.get("type") == "blob" and isinstance(item.get("path"), str)
        }
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
            mode = parent_modes.get(rel, "100644")
            # Symlinks and gitlinks are not safe plain-text publication
            # targets. Do not change their Git type through a snapshot write.
            if mode not in {"100644", "100755"}:
                raise StudioError("Generic publication rejected unsupported source mode")
            entries.append({"path":rel,"mode":mode,"type":"blob","content":text})

        tree=self.github.call("POST",self.github.repo+"/git/trees",{"base_tree":base_tree,"tree":entries})
        commit=self.github.call("POST",self.github.repo+"/git/commits",{"message":message,"tree":tree["sha"],"parents":[base_sha]})
        refs=self.github.get("/git/matching-refs/heads/"+self.branch)
        exists=any(r.get("ref")=="refs/heads/"+self.branch for r in refs if isinstance(r,dict))
        commit_sha = commit.get("sha") if isinstance(commit, dict) else None
        if not isinstance(commit_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", commit_sha):
            raise StudioError("Generic publication commit receipt invalid")
        if exists:
            self.github.call("PATCH",self.github.repo+"/git/refs/heads/"+self.branch,{"sha":commit_sha,"force":False})
        else:
            self.github.call("POST",self.github.repo+"/git/refs",{"ref":"refs/heads/"+self.branch,"sha":commit_sha})
        # The mutation response alone cannot prove the managed branch moved.
        # Fail closed before checkpoint completion, review handoff or success.
        published_refs = self.github.get("/git/matching-refs/heads/" + self.branch)
        if not isinstance(published_refs, list) or not any(
            isinstance(ref, dict)
            and ref.get("ref") == "refs/heads/" + self.branch
            and isinstance(ref.get("object"), dict)
            and ref["object"].get("sha") == commit_sha
            for ref in published_refs
        ):
            raise StudioError("Generic publication branch SHA unverified")
        return commit_sha

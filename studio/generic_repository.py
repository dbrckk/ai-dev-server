"""Bounded GitHub snapshot/publish backend for generic projects."""
from __future__ import annotations
import base64
from pathlib import Path
from core import StudioError, SECRET
from generic_policy import editable

MAX_FILES=500
MAX_TOTAL=6_000_000

class GenericRepository:
    def __init__(self,github,repo:str,project_id:str):
        self.github=github; self.repo=repo; self.project_id=project_id; self.branch="studio/"+project_id

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
                raise StudioError("Generic new project requires an initialized repository")
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

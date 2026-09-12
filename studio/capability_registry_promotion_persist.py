"""Prepare a registry-only PR after a validated capability candidate was human-merged."""
from __future__ import annotations
import base64
import hashlib
import json
import re
import urllib.parse

from core import canonical
from capability_promotion import promote_candidate, CapabilityPromotionError
from capability_synthesis import validate_candidate_envelope
from generic_capability_isolated_validation import validate_isolated_validation_result
from promoted_capabilities import provider_for

SHA40=re.compile(r"[0-9a-f]{40}")
SHA64=re.compile(r"[0-9a-f]{64}")
REGISTRY_PATH="control/promoted_capabilities.json"

class CapabilityRegistryPromotionPersistError(RuntimeError):
    pass

def _prefix(capability,candidate_id):
    ident=hashlib.sha256(candidate_id.encode()).hexdigest()[:12]
    slug=re.sub(r"[^a-z0-9]+","-",capability).strip("-")
    return "capability/promote-"+slug+"-"+ident+"-"

def _repo_owner(github):
    parts=github.repo.strip("/").split("/")
    if len(parts)!=3 or parts[0]!="repos":
        raise CapabilityRegistryPromotionPersistError("repository identity invalid")
    return parts[1]

def _refs(github,prefix):
    refs=github.get("/git/matching-refs/heads/"+prefix)
    if not isinstance(refs,list):
        raise CapabilityRegistryPromotionPersistError("promotion branch lookup invalid")
    want="refs/heads/"+prefix
    return [x for x in refs if isinstance(x,dict) and isinstance(x.get("ref"),str) and x["ref"].startswith(want)]

def _existing_pr(github,branch,commit_sha):
    query=urllib.parse.urlencode({
        "state":"all","head":_repo_owner(github)+":"+branch,"base":"main","per_page":20
    })
    pulls=github.get("/pulls?"+query)
    if not isinstance(pulls,list):
        raise CapabilityRegistryPromotionPersistError("promotion pull request lookup invalid")
    matches=[p for p in pulls if isinstance(p,dict)
             and p.get("head",{}).get("ref")==branch
             and p.get("head",{}).get("sha")==commit_sha]
    if len(matches)>1:
        raise CapabilityRegistryPromotionPersistError("multiple promotion pull requests found")
    return matches[0].get("number") if matches else None

def _load_registry(github,main_sha):
    commit=github.get("/git/commits/"+main_sha)
    tree_sha=commit.get("tree",{}).get("sha") if isinstance(commit,dict) else None
    if not isinstance(tree_sha,str):
        raise CapabilityRegistryPromotionPersistError("main tree missing")
    tree=github.get("/git/trees/"+tree_sha+"?recursive=1")
    items=tree.get("tree") if isinstance(tree,dict) else None
    if not isinstance(items,list) or tree.get("truncated"):
        raise CapabilityRegistryPromotionPersistError("main tree invalid")
    entry=next((x for x in items if isinstance(x,dict) and x.get("path")==REGISTRY_PATH and x.get("type")=="blob"),None)
    if entry is None:
        return {"version":1,"capabilities":{}}, tree_sha
    blob=github.get("/git/blobs/"+entry.get("sha"))
    if not isinstance(blob,dict) or blob.get("encoding")!="base64":
        raise CapabilityRegistryPromotionPersistError("promotion registry blob invalid")
    import base64
    try:
        registry=json.loads(base64.b64decode(blob["content"]).decode("utf-8"))
    except Exception:
        raise CapabilityRegistryPromotionPersistError("promotion registry unreadable") from None
    return registry, tree_sha

def _verify_materialized_provider(github,main_sha,candidate):
    payload=candidate.get("candidate",{})
    capability=payload.get("capability")
    provider=payload.get("provider")
    module=provider.removeprefix("studio.capabilities.") if isinstance(provider,str) else ""
    if not re.fullmatch(r"[a-z][a-z0-9_]{2,120}",module):
        raise CapabilityRegistryPromotionPersistError("provider path invalid")
    path="studio/capabilities/"+module+".py"
    commit=github.get("/git/commits/"+main_sha)
    tree_sha=commit.get("tree",{}).get("sha") if isinstance(commit,dict) else None
    if not isinstance(tree_sha,str):
        raise CapabilityRegistryPromotionPersistError("main tree missing")
    tree=github.get("/git/trees/"+tree_sha+"?recursive=1")
    items=tree.get("tree") if isinstance(tree,dict) else None
    if not isinstance(items,list) or tree.get("truncated"):
        raise CapabilityRegistryPromotionPersistError("main tree invalid")
    entry=next((x for x in items if isinstance(x,dict) and x.get("path")==path and x.get("type")=="blob"),None)
    if entry is None:
        raise CapabilityRegistryPromotionPersistError("merged candidate provider missing")
    blob=github.get("/git/blobs/"+str(entry.get("sha")))
    if not isinstance(blob,dict) or blob.get("encoding")!="base64":
        raise CapabilityRegistryPromotionPersistError("merged candidate provider blob invalid")
    try:
        materialized=base64.b64decode(blob["content"]).decode("utf-8")
    except Exception:
        raise CapabilityRegistryPromotionPersistError("merged candidate provider unreadable") from None
    if materialized!=payload.get("implementation"):
        raise CapabilityRegistryPromotionPersistError("merged candidate provider content mismatch")
    return path


def persist(github,candidate_envelope,validation_report,review_status,baseline_sha,main_sha):
    candidate=validate_candidate_envelope(candidate_envelope)
    report=validate_isolated_validation_result(validation_report)
    if not isinstance(review_status,dict) or review_status.get("status")!="candidate_merged":
        raise CapabilityRegistryPromotionPersistError("candidate merge proof required")
    merge_sha=review_status.get("merge_commit_sha")
    if not isinstance(merge_sha,str) or not SHA40.fullmatch(merge_sha):
        raise CapabilityRegistryPromotionPersistError("candidate merge sha invalid")
    if not isinstance(baseline_sha,str) or not SHA40.fullmatch(baseline_sha):
        raise CapabilityRegistryPromotionPersistError("baseline sha invalid")
    if not isinstance(main_sha,str) or not SHA40.fullmatch(main_sha):
        raise CapabilityRegistryPromotionPersistError("main sha invalid")
    cid=candidate.get("candidate_id")
    digest=candidate.get("candidate_sha256")
    payload=candidate.get("candidate",{})
    capability=payload.get("capability")
    provider=payload.get("provider")
    if provider!=provider_for(capability):
        raise CapabilityRegistryPromotionPersistError("provider mismatch")
    if report.get("candidate_id")!=cid or report.get("candidate_sha256")!=digest:
        raise CapabilityRegistryPromotionPersistError("validation candidate mismatch")
    decision=report.get("validation",{})
    if decision.get("status")!="candidate_validated":
        raise CapabilityRegistryPromotionPersistError("candidate not validated")
    _verify_materialized_provider(github,main_sha,candidate)
    registry,base_tree=_load_registry(github,main_sha)
    try:
        updated,promotion=promote_candidate(registry,candidate,decision,baseline_sha,merge_sha)
    except CapabilityPromotionError as exc:
        raise CapabilityRegistryPromotionPersistError(str(exc)) from None
    if promotion.get("status")=="already_promoted":
        return {
            "status":"registry_already_promoted",
            "capability":capability,
            "candidate_id":cid,
            "candidate_sha256":digest,
            "candidate_merge_sha":merge_sha,
            "capability_registered":False,
        }
    tree=github.call("POST",github.repo+"/git/trees",{
        "base_tree":base_tree,
        "tree":[{"path":REGISTRY_PATH,"mode":"100644","type":"blob","content":canonical(updated)}],
    })
    tree_sha=tree.get("sha") if isinstance(tree,dict) else None
    if not isinstance(tree_sha,str):
        raise CapabilityRegistryPromotionPersistError("promotion tree creation failed")
    prefix=_prefix(capability,cid)
    refs=_refs(github,prefix)
    if len(refs)>1:
        raise CapabilityRegistryPromotionPersistError("multiple promotion branches found")
    if refs:
        branch=refs[0]["ref"][len("refs/heads/"):]
        head=refs[0].get("object",{}).get("sha")
        encoded=branch[len(prefix):]
        if head!=encoded or not SHA40.fullmatch(encoded or ""):
            raise CapabilityRegistryPromotionPersistError("promotion branch identity invalid")
        commit=github.get("/git/commits/"+head)
        parents=[x.get("sha") for x in commit.get("parents",[])] if isinstance(commit,dict) else []
        if commit.get("tree",{}).get("sha")!=tree_sha or parents!=[main_sha]:
            raise CapabilityRegistryPromotionPersistError("promotion branch content changed")
        number=_existing_pr(github,branch,head)
        if not isinstance(number,int):
            raise CapabilityRegistryPromotionPersistError("promotion branch has no matching pull request")
        return {
            "status":"registry_promotion_already_persisted",
            "capability":capability,"candidate_id":cid,"candidate_sha256":digest,
            "candidate_merge_sha":merge_sha,"branch":branch,"commit_sha":head,
            "pull_request":number,"capability_registered":False,
        }
    commit=github.call("POST",github.repo+"/git/commits",{
        "message":"Prepare promoted capability registry: "+capability,
        "tree":tree_sha,"parents":[main_sha],
    })
    commit_sha=commit.get("sha") if isinstance(commit,dict) else None
    if not isinstance(commit_sha,str) or not SHA40.fullmatch(commit_sha):
        raise CapabilityRegistryPromotionPersistError("promotion commit creation failed")
    branch=prefix+commit_sha
    github.call("POST",github.repo+"/git/refs",{"ref":"refs/heads/"+branch,"sha":commit_sha})
    pr=github.call("POST",github.repo+"/pulls",{
        "title":"Promote validated capability: "+capability,
        "head":branch,"base":"main",
        "body":"Registry-only promotion PR for a previously validated and human-merged capability candidate. This PR does not activate the capability until merged and CI remains authoritative."
    })
    number=pr.get("number") if isinstance(pr,dict) else None
    if not isinstance(number,int):
        raise CapabilityRegistryPromotionPersistError("promotion pull request creation failed")
    return {
        "status":"registry_promotion_persisted",
        "capability":capability,"candidate_id":cid,"candidate_sha256":digest,
        "candidate_merge_sha":merge_sha,"branch":branch,"commit_sha":commit_sha,
        "pull_request":number,"capability_registered":False,
    }

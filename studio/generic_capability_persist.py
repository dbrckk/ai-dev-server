"""Persist a validated generic capability candidate to a dedicated GitHub PR."""
from __future__ import annotations
import hashlib,json,re,urllib.parse
from pathlib import Path

from core import canonical
from capability_synthesis import validate_candidate_envelope
from generic_capability_isolated_validation import validate_isolated_validation_result
from promoted_capabilities import provider_for

SHA40=re.compile(r"[0-9a-f]{40}")
SHA64=re.compile(r"[0-9a-f]{64}")
NAME=re.compile(r"[a-z][a-z0-9_.-]{2,80}")

class GenericCapabilityPersistError(RuntimeError): pass

def _slug(name):
    return re.sub(r"[^a-z0-9]+","_",name).strip("_")

def _prefix(capability,candidate_id):
    ident=hashlib.sha256(candidate_id.encode()).hexdigest()[:12]
    return "capability/candidate-"+_slug(capability)+"-"+ident+"-"

def _paths(capability,candidate_id):
    slug=_slug(capability)
    ident=hashlib.sha256(candidate_id.encode()).hexdigest()[:16]
    return {
        "provider":"studio/capabilities/"+slug+".py",
        "tests":"tests/test_candidate_"+slug+"_"+ident+".py",
        "evidence":"control/capability_candidates/"+ident+".json",
    }

def _exact_refs(github,prefix):
    refs=github.get("/git/matching-refs/heads/"+prefix)
    if not isinstance(refs,list): raise GenericCapabilityPersistError("candidate branch lookup invalid")
    expected="refs/heads/"+prefix
    return [x for x in refs if isinstance(x,dict) and isinstance(x.get("ref"),str) and x["ref"].startswith(expected)]

def _existing_pr(github,branch,commit_sha):
    parts=github.repo.strip("/").split("/")
    if len(parts)!=3 or parts[0]!="repos": raise GenericCapabilityPersistError("repository identity invalid")
    query=urllib.parse.urlencode({"state":"all","head":parts[1]+":"+branch,"base":"main","per_page":20})
    pulls=github.get("/pulls?"+query)
    if not isinstance(pulls,list): raise GenericCapabilityPersistError("candidate pull request lookup invalid")
    matches=[p for p in pulls if isinstance(p,dict) and p.get("head",{}).get("ref")==branch and p.get("head",{}).get("sha")==commit_sha]
    if len(matches)>1: raise GenericCapabilityPersistError("multiple candidate pull requests found")
    return matches[0].get("number") if matches else None

def persist(github,candidate_envelope,validation_report,handoff,baseline_sha):
    candidate_envelope=validate_candidate_envelope(candidate_envelope)
    validation_report=validate_isolated_validation_result(validation_report)
    if not isinstance(handoff,dict) or handoff.get("status")!="promotion_required":
        raise GenericCapabilityPersistError("promotion handoff invalid")
    if not isinstance(baseline_sha,str) or not SHA40.fullmatch(baseline_sha):
        raise GenericCapabilityPersistError("baseline sha invalid")
    cid=candidate_envelope["candidate_id"]; digest=candidate_envelope["candidate_sha256"]; payload=candidate_envelope["candidate"]
    capability=payload.get("capability"); provider=payload.get("provider")
    if not isinstance(capability,str) or not NAME.fullmatch(capability): raise GenericCapabilityPersistError("capability invalid")
    if provider!=provider_for(capability): raise GenericCapabilityPersistError("provider mismatch")
    if validation_report.get("candidate_id")!=cid or validation_report.get("candidate_sha256")!=digest:
        raise GenericCapabilityPersistError("validation candidate mismatch")
    if validation_report.get("validation",{}).get("status")!="candidate_validated":
        raise GenericCapabilityPersistError("candidate not validated")
    for key,value in (("candidate_id",cid),("candidate_sha256",digest),("capability",capability),("provider",provider),("baseline_sha",baseline_sha)):
        if handoff.get(key)!=value: raise GenericCapabilityPersistError("handoff identity mismatch")
    if handoff.get("candidate_materialized_in_trusted_repo") is not False or handoff.get("capability_registered") is not False:
        raise GenericCapabilityPersistError("handoff trust state invalid")
    implementation=payload.get("implementation"); tests=payload.get("tests")
    if not isinstance(implementation,str) or not implementation.strip() or not isinstance(tests,str) or not tests.strip():
        raise GenericCapabilityPersistError("candidate sources invalid")
    paths=_paths(capability,cid)
    base=github.get("/git/commits/"+baseline_sha)
    base_tree=base.get("tree",{}).get("sha") if isinstance(base,dict) else None
    if not isinstance(base_tree,str): raise GenericCapabilityPersistError("baseline tree missing")
    baseline_tree=github.get("/git/trees/"+base_tree+"?recursive=1")
    existing_paths={x.get("path") for x in baseline_tree.get("tree",[]) if isinstance(x,dict)} if isinstance(baseline_tree,dict) else set()
    if paths["provider"] in existing_paths or paths["tests"] in existing_paths or paths["evidence"] in existing_paths:
        raise GenericCapabilityPersistError("candidate target path already exists")
    evidence={
        "status":"validated_candidate_persisted_for_review",
        "candidate_id":cid,"candidate_sha256":digest,"capability":capability,"provider":provider,
        "baseline_sha":baseline_sha,"validation_report_sha256":validation_report.get("report_sha256"),
        "handoff_sha256":handoff.get("handoff_sha256"),"capability_registered":False,
    }
    entries=[
        {"path":paths["provider"],"mode":"100644","type":"blob","content":implementation},
        {"path":paths["tests"],"mode":"100644","type":"blob","content":tests},
        {"path":paths["evidence"],"mode":"100644","type":"blob","content":canonical(evidence)},
    ]
    tree=github.call("POST",github.repo+"/git/trees",{"base_tree":base_tree,"tree":entries})
    tree_sha=tree.get("sha") if isinstance(tree,dict) else None
    if not isinstance(tree_sha,str): raise GenericCapabilityPersistError("candidate tree creation failed")
    prefix=_prefix(capability,cid)
    refs=_exact_refs(github,prefix)
    if len(refs)>1: raise GenericCapabilityPersistError("multiple candidate branches found")
    if refs:
        branch=refs[0]["ref"][len("refs/heads/"):]
        head=refs[0].get("object",{}).get("sha")
        encoded=branch[len(prefix):]
        if head!=encoded or not SHA40.fullmatch(encoded or ""): raise GenericCapabilityPersistError("candidate branch identity invalid")
        commit=github.get("/git/commits/"+head)
        parents=[x.get("sha") for x in commit.get("parents",[])] if isinstance(commit,dict) else []
        if commit.get("tree",{}).get("sha")!=tree_sha or parents!=[baseline_sha]:
            raise GenericCapabilityPersistError("candidate branch content changed")
        number=_existing_pr(github,branch,head)
        if not isinstance(number,int): raise GenericCapabilityPersistError("candidate branch has no matching pull request")
        return {**evidence,"status":"candidate_already_persisted","branch":branch,"commit_sha":head,"pull_request":number}
    commit=github.call("POST",github.repo+"/git/commits",{"message":"Persist validated capability candidate: "+capability,"tree":tree_sha,"parents":[baseline_sha]})
    commit_sha=commit.get("sha") if isinstance(commit,dict) else None
    if not isinstance(commit_sha,str) or not SHA40.fullmatch(commit_sha): raise GenericCapabilityPersistError("candidate commit creation failed")
    branch=prefix+commit_sha
    github.call("POST",github.repo+"/git/refs",{"ref":"refs/heads/"+branch,"sha":commit_sha})
    pr=github.call("POST",github.repo+"/pulls",{
        "title":"Validated capability candidate: "+capability,
        "head":branch,"base":"main",
        "body":"Validated isolated capability candidate. Not registered or promoted. Requires repository CI and subsequent promotion gate."
    })
    number=pr.get("number") if isinstance(pr,dict) else None
    if not isinstance(number,int): raise GenericCapabilityPersistError("candidate pull request creation failed")
    return {**evidence,"status":"candidate_persisted","branch":branch,"commit_sha":commit_sha,"pull_request":number}

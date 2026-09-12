"""Verify the exact registry-only promotion PR while activation remains blocked."""
from __future__ import annotations
import re

SHA40=re.compile(r"[0-9a-f]{40}")

class CapabilityRegistryReviewError(RuntimeError): pass

def inspect(github,review):
    required={"status","candidate_id","candidate_sha256","capability","candidate_merge_sha","branch","commit_sha","pull_request"}
    if not isinstance(review,dict) or set(review)!=required:
        raise CapabilityRegistryReviewError("registry review invalid")
    branch=review.get("branch"); commit_sha=review.get("commit_sha"); number=review.get("pull_request")
    if not isinstance(branch,str) or not branch.startswith("capability/promote-"):
        raise CapabilityRegistryReviewError("registry review branch invalid")
    if not isinstance(commit_sha,str) or not SHA40.fullmatch(commit_sha):
        raise CapabilityRegistryReviewError("registry review commit invalid")
    if not isinstance(number,int) or number<1:
        raise CapabilityRegistryReviewError("registry review pull request invalid")
    pr=github.get("/pulls/"+str(number))
    if not isinstance(pr,dict):
        raise CapabilityRegistryReviewError("registry pull request lookup invalid")
    if pr.get("base",{}).get("ref")!="main":
        raise CapabilityRegistryReviewError("registry pull request base changed")
    head=pr.get("head",{})
    if head.get("ref")!=branch or head.get("sha")!=commit_sha:
        raise CapabilityRegistryReviewError("registry pull request identity changed")
    merged=pr.get("merged") is True or pr.get("merged_at") is not None
    state=pr.get("state")
    if merged:
        merge_sha=pr.get("merge_commit_sha")
        if not isinstance(merge_sha,str) or not SHA40.fullmatch(merge_sha):
            raise CapabilityRegistryReviewError("registry merge identity invalid")
        return {"status":"registry_promotion_merged","merge_commit_sha":merge_sha,"pull_request":number}
    if state=="open":
        return {"status":"registry_review_pending","pull_request":number}
    if state=="closed":
        return {"status":"registry_review_rejected","pull_request":number}
    raise CapabilityRegistryReviewError("registry pull request state invalid")

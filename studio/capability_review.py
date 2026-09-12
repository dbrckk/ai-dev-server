"""Verify the exact persisted candidate PR while adaptation waits for review."""
from __future__ import annotations
import re

SHA40=re.compile(r"[0-9a-f]{40}")

class CapabilityReviewError(RuntimeError): pass

def inspect(github,review):
    required={"status","candidate_id","candidate_sha256","capability","branch","commit_sha","pull_request"}
    if not isinstance(review,dict) or set(review)!=required:
        raise CapabilityReviewError("candidate review invalid")
    branch=review.get("branch"); commit_sha=review.get("commit_sha"); number=review.get("pull_request")
    if not isinstance(branch,str) or not branch.startswith("capability/candidate-"):
        raise CapabilityReviewError("candidate review branch invalid")
    if not isinstance(commit_sha,str) or not SHA40.fullmatch(commit_sha):
        raise CapabilityReviewError("candidate review commit invalid")
    if not isinstance(number,int) or number<1:
        raise CapabilityReviewError("candidate review pull request invalid")
    pr=github.get("/pulls/"+str(number))
    if not isinstance(pr,dict):
        raise CapabilityReviewError("candidate pull request lookup invalid")
    if pr.get("base",{}).get("ref")!="main":
        raise CapabilityReviewError("candidate pull request base changed")
    head=pr.get("head",{})
    if head.get("ref")!=branch or head.get("sha")!=commit_sha:
        raise CapabilityReviewError("candidate pull request identity changed")
    merged=pr.get("merged") is True or pr.get("merged_at") is not None
    state=pr.get("state")
    if merged:
        merge_sha=pr.get("merge_commit_sha")
        if not isinstance(merge_sha,str) or not SHA40.fullmatch(merge_sha):
            raise CapabilityReviewError("candidate merge identity invalid")
        return {"status":"candidate_merged","merge_commit_sha":merge_sha,"pull_request":number}
    if state=="open":
        return {"status":"candidate_review_pending","pull_request":number}
    if state=="closed":
        return {"status":"candidate_review_rejected","pull_request":number}
    raise CapabilityReviewError("candidate pull request state invalid")

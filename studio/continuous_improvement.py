"""Evidence-gated continuous-improvement planning for completed projects."""
from __future__ import annotations

import hashlib
import json
from collections import Counter

try:
    from .goal_engine import new_goal, validate as validate_goal
except ImportError:
    from goal_engine import new_goal, validate as validate_goal

VERSION=1


class ImprovementError(ValueError):
    pass


def _digest(value):
    return hashlib.sha256(
        json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    ).hexdigest()


def _candidate(kind,key,priority,objective,source,required_evidence):
    identity={"kind":kind,"key":key,"source":source,"required_evidence":required_evidence}
    return {
        "id":"improvement:"+_digest(identity)[:20],
        "kind":kind,
        "priority":priority,
        "objective":objective,
        "source":source,
        "required_evidence":list(required_evidence),
        "evidence_fingerprint":_digest(source),
    }


def assess(goal_state,project_state,*,max_candidates=20):
    validate_goal(goal_state)
    if not isinstance(project_state,dict):
        raise ImprovementError("project state invalid")
    if not isinstance(max_candidates,int) or isinstance(max_candidates,bool) or not 1<=max_candidates<=100:
        raise ImprovementError("max_candidates invalid")
    if goal_state.get("status")!="complete":
        return {
            "version":VERSION,
            "status":"deferred_until_goal_complete",
            "candidates":[],
        }

    candidates=[]

    failures=Counter(x for x in goal_state.get("failures",[]) if isinstance(x,str) and x.strip())
    for failure,count in sorted(failures.items()):
        if count<2:
            continue
        source={"failure":failure,"occurrences":count}
        candidates.append(_candidate(
            "repeated_failure",
            failure,
            100,
            "Eliminate repeated autonomous-cycle failure: "+failure,
            source,
            ["targeted_regression_passed","full_regression_passed"],
        ))

    missing=Counter()
    for event in goal_state.get("history",[]):
        if isinstance(event,dict):
            capability=event.get("missing_capability")
            if isinstance(capability,str) and capability.strip():
                missing[capability]+=1
    for capability,count in sorted(missing.items()):
        if count<2:
            continue
        source={"capability":capability,"missing_occurrences":count}
        candidates.append(_candidate(
            "capability_churn",
            capability,
            80,
            "Reduce repeated capability adaptation for "+capability,
            source,
            ["capability_preflight_passed","full_regression_passed"],
        ))

    release=project_state.get("release_evidence")
    if isinstance(release,dict):
        for stage,evidence in sorted(release.items()):
            if not isinstance(stage,str) or not isinstance(evidence,dict) or evidence.get("passed") is not True:
                continue
            warnings=evidence.get("warnings")
            if not isinstance(warnings,list):
                continue
            clean=sorted({w.strip() for w in warnings if isinstance(w,str) and w.strip()})
            if not clean:
                continue
            source={"stage":stage,"warnings":clean}
            candidates.append(_candidate(
                "persistent_warning",
                stage+":"+_digest(clean),
                60,
                "Remove validated release warnings from "+stage,
                source,
                ["warning_removed","stage_revalidated","full_regression_passed"],
            ))

    candidates.sort(key=lambda item:(-item["priority"],item["id"]))
    return {
        "version":VERSION,
        "status":"improvement_required" if candidates else "no_improvement_required",
        "candidates":candidates[:max_candidates],
    }


def next_candidate(assessment):
    if not isinstance(assessment,dict) or assessment.get("version")!=VERSION:
        raise ImprovementError("assessment invalid")
    candidates=assessment.get("candidates")
    if not isinstance(candidates,list):
        raise ImprovementError("assessment candidates invalid")
    return dict(candidates[0]) if candidates else None


def improvement_goal(candidate,*,max_attempts=8):
    if not isinstance(candidate,dict):
        raise ImprovementError("candidate invalid")
    required={"id","kind","priority","objective","source","required_evidence","evidence_fingerprint"}
    if set(candidate)!=required:
        raise ImprovementError("candidate malformed")
    evidence=candidate["required_evidence"]
    if not isinstance(evidence,list) or not evidence:
        raise ImprovementError("candidate evidence invalid")
    return new_goal(
        candidate["id"],
        candidate["objective"],
        [{"name":"proved_improvement","required_evidence":list(evidence)}],
        max_attempts=max_attempts,
    )

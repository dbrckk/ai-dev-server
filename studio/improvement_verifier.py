"""Fail-closed conversion of trusted project results into improvement evidence."""
from __future__ import annotations


class ImprovementVerificationError(ValueError):
    pass


def _full_regression(result):
    if not isinstance(result,dict) or result.get("status")!="complete":
        return False
    report=result.get("report")
    completion=report.get("completion") if isinstance(report,dict) else None
    return isinstance(completion,dict) and completion.get("finished") is True


def verify_improvement_result(candidate,result):
    if not isinstance(candidate,dict):
        raise ImprovementVerificationError("candidate invalid")
    kind=candidate.get("kind")
    source=candidate.get("source")
    if not isinstance(kind,str) or not isinstance(source,dict):
        raise ImprovementVerificationError("candidate metadata invalid")

    evidence={}
    if _full_regression(result):
        evidence["full_regression_passed"]=True

    verification=result.get("improvement_verification") if isinstance(result,dict) else None

    if kind=="repeated_failure":
        failure=source.get("failure")
        if (
            isinstance(failure,str) and
            isinstance(verification,dict) and
            verification.get("kind")=="repeated_failure" and
            verification.get("failure")==failure and
            verification.get("passed") is True and
            verification.get("targeted_test_passed") is True
        ):
            evidence["targeted_regression_passed"]=True

    elif kind=="capability_churn":
        capability=source.get("capability")
        if (
            isinstance(capability,str) and
            isinstance(verification,dict) and
            verification.get("kind")=="capability_churn" and
            verification.get("capability")==capability and
            verification.get("passed") is True and
            verification.get("preflight_passed") is True
        ):
            evidence["capability_preflight_passed"]=True

    elif kind=="persistent_warning":
        stage=source.get("stage")
        warnings=source.get("warnings")
        report=result.get("report") if isinstance(result,dict) else None
        release=report.get("release_evidence") if isinstance(report,dict) else None
        stage_evidence=release.get(stage) if isinstance(release,dict) and isinstance(stage,str) else None
        current=stage_evidence.get("warnings",[]) if isinstance(stage_evidence,dict) else None
        if (
            isinstance(stage_evidence,dict) and
            stage_evidence.get("passed") is True and
            isinstance(current,list) and
            isinstance(warnings,list) and
            not any(w in current for w in warnings)
        ):
            evidence["warning_removed"]=True
            evidence["stage_revalidated"]=True
    else:
        raise ImprovementVerificationError("unsupported improvement kind")

    return evidence

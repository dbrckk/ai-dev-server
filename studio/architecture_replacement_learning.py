"""Aggregate historical architecture replacement outcomes conservatively."""
from __future__ import annotations

import json
import time
from pathlib import Path

MIN_SAMPLES=5
CONFIDENCE_TARGET=20
REGIME_WINDOWS_DAYS=(30,90,180)
REGIME_MIN_SAMPLES=3
REGIME_DROP_THRESHOLD=0.20

def _wilson_lower(successes:int,samples:int,z:float=1.96)->float:
    if samples<=0: return 0.0
    p=successes/samples
    z2=z*z
    denom=1.0+z2/samples
    centre=p+z2/(2*samples)
    margin=z*((p*(1-p)/samples+z2/(4*samples*samples))**0.5)
    return max(0.0,min(1.0,(centre-margin)/denom))

def _rows(root:Path):
    candidates=[]
    direct=root/"architecture-replacement-outcome.json"
    if direct.is_file(): candidates.append(direct)
    candidates.extend(sorted(root.glob("*/architecture-replacement-outcome.json")))
    for path in candidates:
        try: value=json.loads(path.read_text(encoding="utf-8"))
        except (OSError,UnicodeError,json.JSONDecodeError): continue
        if isinstance(value,dict) and value.get("status")=="replacement_outcome_recorded":
            yield value

def summarize(root:Path|str="studio-output", now:float|None=None)->dict:
    root=Path(root)
    now=float(now) if isinstance(now,(int,float)) else time.time()
    stats={}
    raw_by_key={}
    outcomes=0
    for row in _rows(root):
        outcomes+=1
        current=row.get("current_repo"); replacement=row.get("replacement_repo")
        if not isinstance(current,str) or not isinstance(replacement,str): continue
        framework=row.get("framework") if isinstance(row.get("framework"),str) else None
        project_type=row.get("project_type") if isinstance(row.get("project_type"),str) else None
        primary_domain=row.get("primary_domain") if isinstance(row.get("primary_domain"),str) else None
        platform=row.get("platform") if isinstance(row.get("platform"),str) else None
        current_major=row.get("current_major_version")
        replacement_major=row.get("replacement_major_version")
        key=(current,replacement,framework,project_type,primary_domain,platform,current_major,replacement_major)
        item=stats.setdefault(key,{
            "current_repo":current,
            "replacement_repo":replacement,
            "framework":framework,
            "project_type":project_type,
            "primary_domain":primary_domain,
            "platform":platform,
            "current_major_version":current_major,
            "replacement_major_version":replacement_major,
            "samples":0,
            "successes":0,
            "regressions":0,
            "rollback_preparations":0,
            "rollbacks":0,
            "quality_total":0.0,
            "first_observed_at":None,
            "latest_observed_at":None,
        })
        raw_by_key.setdefault(key,[]).append(row)
        item["samples"]+=1
        item["successes"]+=int(row.get("successful") is True)
        item["regressions"]+=int(row.get("regressed") is True)
        item["rollback_preparations"]+=int(row.get("rollback_prepared") is True)
        item["rollbacks"]+=int(row.get("rolled_back") is True)
        q=row.get("quality_score")
        item["quality_total"]+=float(q) if isinstance(q,(int,float)) else 0.0
        ts=row.get("observed_at")
        if isinstance(ts,(int,float)):
            ts=float(ts)
            first=item["first_observed_at"]
            latest=item["latest_observed_at"]
            item["first_observed_at"]=ts if not isinstance(first,(int,float)) else min(float(first),ts)
            item["latest_observed_at"]=ts if not isinstance(latest,(int,float)) else max(float(latest),ts)

    rankings=[]
    for item in stats.values():
        n=item["samples"]; successes=item["successes"]
        success_rate=successes/n if n else 0.0
        posterior=(successes+1)/(n+2) if n>=0 else 0.5
        confidence=min(1.0,n/CONFIDENCE_TARGET) if n else 0.0
        regress_rate=item["regressions"]/n if n else 0.0
        rollback_preparation_rate=item["rollback_preparations"]/n if n else 0.0
        rollback_rate=item["rollbacks"]/n if n else 0.0
        mean_quality=item["quality_total"]/n if n else 0.0
        windows={}
        for days in REGIME_WINDOWS_DAYS:
            cutoff=now-days*86400.0
            recent=[
                row for row in raw_by_key.get((
                    item["current_repo"],item["replacement_repo"],item["framework"],
                    item["project_type"],item["primary_domain"],item["platform"],
                    item["current_major_version"],item["replacement_major_version"]
                ),[])
                if isinstance(row.get("observed_at"),(int,float)) and float(row["observed_at"])>=cutoff
            ]
            rn=len(recent)
            rs=sum(int(row.get("successful") is True) for row in recent)
            rr=sum(int(row.get("regressed") is True) for row in recent)
            windows[str(days)]={
                "samples":rn,
                "success_rate":round(rs/rn,4) if rn else None,
                "regression_rate":round(rr/rn,4) if rn else None,
                "wilson_lower_95":round(_wilson_lower(rs,rn),4) if rn else None,
            }
        comparable=[
            (int(days),window)
            for days,window in windows.items()
            if window["samples"]>=REGIME_MIN_SAMPLES and isinstance(window["success_rate"],(int,float))
        ]
        recent_window=min(comparable,key=lambda pair:pair[0]) if comparable else None
        recent_rate=recent_window[1]["success_rate"] if recent_window else None
        regime_drop=(success_rate-float(recent_rate)) if isinstance(recent_rate,(int,float)) else 0.0
        recent_regression=recent_window[1]["regression_rate"] if recent_window else None
        regime_shift=bool(
            recent_window
            and regime_drop>=REGIME_DROP_THRESHOLD
            and (
                float(recent_rate)<0.70
                or (isinstance(recent_regression,(int,float)) and float(recent_regression)>=0.25)
            )
        )
        rankings.append({
            **{k:item[k] for k in ("current_repo","replacement_repo","framework","project_type","primary_domain","platform","current_major_version","replacement_major_version","samples","successes","regressions","rollback_preparations","rollbacks","first_observed_at","latest_observed_at")},
            "success_rate":round(success_rate,4),
            "posterior_success_rate":round(posterior,4),
            "wilson_lower_95":round(_wilson_lower(successes,n),4),
            "evidence_confidence":round(confidence,4),
            "regression_rate":round(regress_rate,4),
            "rollback_preparation_rate":round(rollback_preparation_rate,4),
            "rollback_rate":round(rollback_rate,4),
            "mean_quality_score":round(mean_quality,3),
            "eligible_for_bias":n>=MIN_SAMPLES,
            "recent_windows":windows,
            "regime_shift":regime_shift,
            "regime_drop":round(regime_drop,4),
            "regime_window_days":recent_window[0] if recent_window else None,
            "regime_recent_success_rate":recent_rate,
        })
    rankings.sort(key=lambda x:(
        x["eligible_for_bias"],
        x["wilson_lower_95"],
        x["mean_quality_score"],
        -x["regression_rate"],
        -x["rollback_rate"],
        x["samples"],
    ),reverse=True)
    return {
        "version":4,
        "outcomes_observed":outcomes,
        "minimum_samples":MIN_SAMPLES,
        "confidence_target":CONFIDENCE_TARGET,
        "regime_windows_days":list(REGIME_WINDOWS_DAYS),
        "regime_min_samples":REGIME_MIN_SAMPLES,
        "regime_drop_threshold":REGIME_DROP_THRESHOLD,
        "advisory_only":True,
        "rankings":rankings[:200],
    }

"""Evidence-gated learning bridge for autonomous goal cycles."""
from __future__ import annotations
import hashlib,json
try:
    from .memory_bridge import remember_experience
    from .project_memory import query,reusable_for_project
except ImportError:
    from memory_bridge import remember_experience
    from project_memory import query,reusable_for_project

def _digest(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def context_for_goal(memory,project_id,tags=None,limit=20):
    if not isinstance(limit,int) or isinstance(limit,bool) or not 1<=limit<=100: raise ValueError("limit invalid")
    local=query(memory,project_id=project_id,tags=tags)
    reusable=reusable_for_project(memory,project_id,tags=tags)
    items=(local+reusable)[-limit:]
    return [{"id":x["id"],"kind":x["kind"],"summary":x["summary"],"tags":x["tags"],
             "evidence_sha256":_digest(x["evidence"]),"provenance":x["provenance"],
             "same_project":x["project_id"]==project_id} for x in items]

def learn_from_cycle(memory,project_id,goal_state,cycle_result,commit_sha):
    if not isinstance(goal_state,dict) or not isinstance(cycle_result,dict): raise ValueError("cycle evidence invalid")
    evidence=cycle_result.get("evidence")
    if not isinstance(evidence,dict) or not evidence: return memory
    if cycle_result.get("tests_passed") is not True: return memory
    if not isinstance(commit_sha,str) or len(commit_sha)!=40: raise ValueError("commit invalid")
    attempt=goal_state.get("attempt")
    goal_id=goal_state.get("goal_id")
    if not isinstance(attempt,int) or not isinstance(goal_id,str): raise ValueError("goal state invalid")
    summary=cycle_result.get("learning_summary")
    if not isinstance(summary,str) or not summary.strip(): return memory
    tags=cycle_result.get("learning_tags") or ["goal-cycle"]
    reusable=cycle_result.get("reusable_learning") is True
    proof={"tests_passed":True,"commit_sha":commit_sha,"evidence_sha256":_digest(evidence)}
    if reusable:
        if cycle_result.get("regression_suite_passed") is not True: return memory
        proof["regression_suite_passed"]=True
    return remember_experience(memory,project_id,entry_id=f"experience:{goal_id}:{attempt+1}:{commit_sha[:12]}",
        summary=summary[:4000],tags=tags,proof=proof,reusable=reusable,confidence=100 if reusable else 90)

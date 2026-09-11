"""Bounded execution of one active continuous-improvement goal at a time."""
from __future__ import annotations

from pathlib import Path

try:
    from .continuous_improvement import improvement_goal
    from .goal_engine import load as load_goal, save as save_goal
    from .goal_loop import run_goal
    from .improvement_backlog import load as load_backlog, prove, save as save_backlog
except ImportError:
    from continuous_improvement import improvement_goal
    from goal_engine import load as load_goal, save as save_goal
    from goal_loop import run_goal
    from improvement_backlog import load as load_backlog, prove, save as save_backlog


class ImprovementExecutionError(ValueError):
    pass


def _active(backlog):
    active=[item for item in backlog["items"] if item["status"]=="active"]
    if len(active)>1:
        raise ImprovementExecutionError("multiple active improvements")
    return active[0] if active else None


def run_active_improvement(
    backlog_path,
    goal_path,
    registry_path,
    execute_cycle,
    *,
    max_cycles=4,
):
    backlog_path=Path(backlog_path)
    goal_path=Path(goal_path)
    registry_path=Path(registry_path)
    backlog=load_backlog(backlog_path)
    item=_active(backlog)
    if item is None:
        return {
            "status":"idle",
            "candidate_id":None,
            "goal_status":None,
            "proved":False,
        }

    candidate=item["candidate"]
    candidate_id=candidate["id"]
    if goal_path.is_file():
        goal=load_goal(goal_path)
        if goal["goal_id"]!=candidate_id:
            raise ImprovementExecutionError("active improvement goal mismatch")
    else:
        goal=improvement_goal(candidate)
        save_goal(goal_path,goal)

    state=run_goal(
        goal_path,
        registry_path,
        execute_cycle,
        max_cycles=max_cycles,
    )
    status=state.get("status")
    if status!="complete":
        return {
            "status":"incomplete",
            "candidate_id":candidate_id,
            "goal_status":status,
            "proved":False,
        }

    required=candidate["required_evidence"]
    evidence=state.get("evidence")
    if not isinstance(evidence,dict):
        raise ImprovementExecutionError("completed improvement lacks evidence")
    proof={key:evidence[key] for key in required if key in evidence}
    if len(proof)!=len(required):
        raise ImprovementExecutionError("completed improvement proof incomplete")

    backlog=prove(backlog,candidate_id,proof)
    save_backlog(backlog_path,backlog)
    return {
        "status":"proved",
        "candidate_id":candidate_id,
        "goal_status":"complete",
        "proved":True,
        "proof_keys":sorted(proof),
    }

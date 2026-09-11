import json
from pathlib import Path
import pytest
from studio.goal_engine import GoalStateError,decide,finalize,load,new_goal,record_cycle,save

def goal(max_attempts=3):
    return new_goal("g1","Ship validated app",[
        {"name":"build","required_evidence":["build_sha"]},
        {"name":"qa","required_evidence":["qa_report"]},
    ],max_attempts=max_attempts)

def test_relaunch_until_required_evidence_exists():
    s=goal()
    assert decide(s)["decision"]=="relaunch"
    s=record_cycle(s,evidence={"build_sha":"abc"})
    assert decide(s)=={"decision":"relaunch","missing_evidence":["qa_report"],"next_action":"continue_goal"}

def test_complete_requires_all_evidence():
    s=record_cycle(goal(),evidence={"build_sha":"abc","qa_report":{"passed":True}})
    assert decide(s)["decision"]=="complete"
    assert finalize(s)["status"]=="complete"

def test_failure_never_counts_as_completion():
    s=record_cycle(goal(),failure="tests failed")
    assert decide(s)["decision"]=="relaunch"
    assert s["failures"]==["tests failed"]

def test_missing_capability_requests_adaptation():
    s=record_cycle(goal(),missing_capability="unity_android_qa")
    assert decide(s)["decision"]=="replan"
    assert decide(s)["next_action"]=="adapt:unity_android_qa"

def test_human_action_is_explicit_terminal_state():
    s=record_cycle(goal(),human_action="accept store declarations")
    assert decide(s)["decision"]=="human_action_required"
    assert finalize(s)["status"]=="human_action_required"

def test_attempt_budget_blocks_infinite_loop():
    s=record_cycle(goal(max_attempts=1),failure="still failing")
    assert decide(s)["decision"]=="blocked"
    assert decide(s)["next_action"]=="attempt_budget_exhausted"

def test_persistence_detects_tampering(tmp_path:Path):
    p=tmp_path/"goal.json"; s=goal(); save(p,s); assert load(p)==s
    value=json.loads(p.read_text()); value["objective"]="tampered"; p.write_text(json.dumps(value))
    with pytest.raises(GoalStateError,match="integrity"): load(p)

def test_terminal_state_is_immutable():
    s=finalize(record_cycle(goal(),evidence={"build_sha":"abc","qa_report":"ok"}))
    with pytest.raises(GoalStateError,match="immutable"): record_cycle(s,evidence={"x":"y"})

def test_false_evidence_rejected():
    with pytest.raises(GoalStateError,match="evidence invalid"): record_cycle(goal(),evidence={"build_sha":False})


def test_attempt_budget_cannot_be_overrun():
    s=record_cycle(goal(max_attempts=1),failure="failed")
    with pytest.raises(GoalStateError,match="attempt budget exhausted"):
        record_cycle(s,failure="again")

def test_resolve_capability_removes_pending_requirement():
    from studio.goal_engine import resolve_capability
    s=record_cycle(goal(),missing_capability="unity.qa")
    s=resolve_capability(s,"unity.qa",{"registry":"verified"})
    assert "unity.qa" not in s["missing_capabilities"]
    assert decide(s)["decision"]=="relaunch"

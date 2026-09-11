"""Persistent bounded autonomous goal loop."""
from __future__ import annotations
from pathlib import Path

try:
    from .capability_registry import has_capability,load as load_registry,register,save as save_registry
    from .goal_engine import decide,finalize,load as load_goal,record_cycle,resolve_capability,save as save_goal
except ImportError:
    from capability_registry import has_capability,load as load_registry,register,save as save_registry
    from goal_engine import decide,finalize,load as load_goal,record_cycle,resolve_capability,save as save_goal

def run_goal(goal_path,registry_path,execute_cycle,adapt_capability=None,*,max_cycles=100,context_provider=None,cycle_observer=None,execute_registered_capability=None):
    if not isinstance(max_cycles,int) or isinstance(max_cycles,bool) or not 1<=max_cycles<=1000:
        raise ValueError("max_cycles invalid")
    goal_path=Path(goal_path); registry_path=Path(registry_path)
    state=load_goal(goal_path); registry=load_registry(registry_path)
    for _ in range(max_cycles):
        decision=decide(state); action=decision["decision"]
        if action in {"complete","human_action_required","blocked"}:
            state=finalize(state); save_goal(goal_path,state); return state
        if action=="replan":
            capability=decision["next_action"].removeprefix("adapt:")
            if has_capability(registry,capability):
                item=registry["capabilities"][capability]
                if execute_registered_capability is None:
                    state=record_cycle(state,blocked_reason="registered capability has no runtime:"+capability)
                    save_goal(goal_path,state); continue
                result=execute_registered_capability(registry,capability,dict(state))
                if not isinstance(result,dict) or result.get("passed") is not True or not isinstance(result.get("evidence"),dict) or not result["evidence"]:
                    state=record_cycle(state,failure="registered capability execution unverified:"+capability)
                    save_goal(goal_path,state); continue
                evidence={"registry_provider":item["provider"],"registry_evidence":item["evidence"],"runtime_evidence":result["evidence"]}
                state=resolve_capability(state,capability,evidence)
                save_goal(goal_path,state); continue
            if adapt_capability is None:
                state=record_cycle(state,blocked_reason="no adapter for capability:"+capability)
                save_goal(goal_path,state); continue
            result=adapt_capability(capability,dict(state))
            if not isinstance(result,dict) or not result.get("provider") or not isinstance(result.get("evidence"),dict) or not result["evidence"]:
                state=record_cycle(state,failure="capability adaptation unverified:"+capability)
                save_goal(goal_path,state); continue
            registry=register(registry,capability,str(result["provider"]),result["evidence"])
            save_registry(registry_path,registry)
            state=resolve_capability(state,capability,result["evidence"])
            save_goal(goal_path,state); continue
        cycle_state=dict(state)
        if context_provider is not None:
            context=context_provider(dict(state))
            if not isinstance(context,list): raise ValueError("goal context invalid")
            cycle_state["learned_context"]=context
        result=execute_cycle(cycle_state)
        if not isinstance(result,dict):
            state=record_cycle(state,failure="cycle returned invalid result")
        elif result.get("yield_run") is True:
            state=record_cycle(state,evidence=result.get("evidence"),failure=result.get("failure"),
                missing_capability=result.get("missing_capability"),human_action=result.get("human_action"),
                blocked_reason=result.get("blocked_reason"),count_attempt=False)
            save_goal(goal_path,state)
            if cycle_observer is not None:
                cycle_observer(dict(state),result)
            return state
        else:
            state=record_cycle(state,evidence=result.get("evidence"),failure=result.get("failure"),
                missing_capability=result.get("missing_capability"),human_action=result.get("human_action"),
                blocked_reason=result.get("blocked_reason"))
        save_goal(goal_path,state)
        if cycle_observer is not None:
            cycle_observer(dict(state), result if isinstance(result,dict) else {})
    return state

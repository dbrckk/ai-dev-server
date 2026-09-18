"""Autonomous capability routing with ordered fallbacks and evidence."""
from __future__ import annotations
from pathlib import Path
import json
import os
from .adapters import AgentAdapter
from .codex import codex_invocation, parse_codex_usage
from .performance import bonus,eligible,load
from .registry import DEFAULT_REGISTRY
from .router import rank_agents
from routing_history import learned_weights, load as load_routing_history
from safe_rewrite_learning import summarize as summarize_safe_rewrite_learning
from contextual_routing_memory import load as load_contextual_routing_memory

def _safe_rewrite_summary()->dict:
    raw=os.environ.get("STUDIO_SAFE_REWRITE_LEARNING_PATH","")
    return summarize_safe_rewrite_learning(Path(raw)) if raw else {}


def _contextual_routing_state()->tuple[dict,list[tuple[str,float]]]:
    raw=os.environ.get("STUDIO_CONTEXTUAL_ROUTING_MEMORY_PATH","")
    data=load_contextual_routing_memory(Path(raw)) if raw else {}
    try:
        value=json.loads(os.environ.get("STUDIO_ROUTING_CONTEXTS_JSON","[]"))
    except json.JSONDecodeError:
        value=[]
    weighted=[]
    if isinstance(value,list):
        for item in value:
            if isinstance(item,list) and len(item)==2:
                try:
                    weighted.append((str(item[0]),float(item[1])))
                except (TypeError,ValueError):
                    pass
    return data,weighted


def _verification_seconds()->float:
    try:
        return max(0.0,float(os.environ.get("STUDIO_EXPECTED_VERIFICATION_SECONDS","0") or 0.0))
    except ValueError:
        return 0.0


def _agent_execution_seconds(perf:dict,role:str)->dict[str,float]:
    result={}
    for spec in DEFAULT_REGISTRY.all():
        row=perf.get(spec.name+":"+role)
        if isinstance(row,dict) and int(row.get("runs",0) or 0)>0:
            result[spec.name]=float(row.get("duration_total",0.0) or 0.0)/max(1,int(row.get("runs",0)))
    return result

def _opencode_runtime(prompt:str)->tuple[list[str],dict[str,str]]:
    model=os.environ.get("STUDIO_CODE_MODEL") or os.environ.get("STUDIO_MODEL","")
    base=os.environ.get("STUDIO_API_BASE","")
    key=os.environ.get("STUDIO_API_KEY","")
    env={"OPENCODE_DISABLE_MODELS_FETCH":"1"}
    argv=["opencode","run","--auto","--format","json"]
    if model and base and key:
        config={
            "$schema":"https://opencode.ai/config.json",
            "share":"disabled",
            "permission":{
                "*":"deny",
                "read":"allow",
                "edit":"allow",
                "glob":"allow",
                "grep":"allow",
                "lsp":"allow"
            },
            "provider":{
                "studio":{
                    "npm":"@ai-sdk/openai-compatible",
                    "name":"AI Dev Server provider",
                    "options":{"baseURL":base,"apiKey":"{env:OPENCODE_STUDIO_API_KEY}"},
                    "models":{model:{}},
                }
            },
        }
        env["OPENCODE_STUDIO_API_KEY"]=key
        env["OPENCODE_CONFIG_CONTENT"]=json.dumps(config,separators=(",",":"))
        argv.extend(["--model","studio/"+model])
    argv.append(prompt)
    return argv,env

def invocation_for(name:str,prompt:str)->tuple[list[str],dict[str,str]]|None:
    # Only invocation contracts verified against upstream CLIs are enabled.
    if name=="opencode":
        return _opencode_runtime(prompt)
    if name=="codex":
        return codex_invocation(prompt)
    if name=="hermes":
        return (["hermes","chat","--toolsets","file","-q",prompt],{"HERMES_YOLO_MODE":"1"})
    return None


def _run_evidence(run)->dict:
    evidence={"agent":run.agent,"returncode":run.returncode,
        "duration_seconds":run.duration_seconds,"stdout_tail":run.stdout_tail,"stderr_tail":run.stderr_tail}
    if run.agent=="codex":
        usage=parse_codex_usage(run.stdout_tail)
        if usage is not None:
            evidence["usage"]=usage
    return evidence


def execute(prompt:str,required:set[str],*,role:str,cwd:Path,memory_path:Path,timeout:int=1800)->dict:
    perf=load(memory_path)
    history_raw=os.environ.get("STUDIO_ROUTING_HISTORY_PATH","")
    history=load_routing_history(Path(history_raw)) if history_raw else []
    weights=learned_weights(history,kind="agent",role=role)
    reliability={spec.name:bonus(perf,spec.name,role) for spec in DEFAULT_REGISTRY.all()}
    contextual_routing,weighted_contexts=_contextual_routing_state()
    ranked=rank_agents(
        required,
        registry=DEFAULT_REGISTRY,
        prefer_free=True,
        long_task="long_task" in required,
        reliability=reliability,
        weights=weights,
        safe_rewrite_summary=_safe_rewrite_summary(),
        contextual_routing=contextual_routing,
        weighted_contexts=weighted_contexts,
        execution_seconds=_agent_execution_seconds(perf,role),
        verification_seconds=_verification_seconds(),
    )
    attempts=[]
    for decision in ranked:
        if not decision.agent.available(): continue
        if not eligible(perf,decision.agent.name,role):
            attempts.append({"agent":decision.agent.name,"status":"cooldown"})
            continue
        invocation=invocation_for(decision.agent.name,prompt)
        if invocation is None:
            attempts.append({"agent":decision.agent.name,"status":"unsupported_adapter"})
            continue
        try:
            argv,extra_env=invocation
            run=AgentAdapter(decision.agent).run(argv,cwd=cwd,timeout=timeout,extra_env=extra_env)
            ok=run.returncode==0
            evidence=_run_evidence(run)
            evidence["status"]="passed" if ok else "failed"
            attempts.append(evidence)
            if ok: return {"status":"passed","selected":run.agent,"attempts":attempts}
        except RuntimeError as exc:
            attempts.append({"agent":decision.agent.name,"status":"error","error":str(exc)[:1000]})
    return {"status":"unavailable","selected":None,"attempts":attempts}


def ranked_agent_names(required:set[str],*,role:str,memory_path:Path,limit:int=2,preferred:str|None=None)->list[str]:
    perf=load(memory_path)
    history_raw=os.environ.get("STUDIO_ROUTING_HISTORY_PATH","")
    history=load_routing_history(Path(history_raw)) if history_raw else []
    weights=learned_weights(history,kind="agent",role=role)
    reliability={spec.name:bonus(perf,spec.name,role) for spec in DEFAULT_REGISTRY.all()}
    ranked=rank_agents(
        required,
        registry=DEFAULT_REGISTRY,
        prefer_free=True,
        long_task="long_task" in required,
        reliability=reliability,
        weights=weights,
    )

    def usable(decision)->bool:
        return (
            decision.agent.available()
            and eligible(perf,decision.agent.name,role)
            and invocation_for(decision.agent.name,"probe") is not None
        )

    preferred_name=str(preferred or "").strip()
    if preferred_name=="auto":
        preferred_name=""

    names=[]
    if preferred_name:
        preferred_decision=next(
            (
                decision
                for decision in ranked
                if decision.agent.name==preferred_name and usable(decision)
            ),
            None,
        )
        if preferred_decision is not None:
            names.append(preferred_name)

    for decision in ranked:
        if len(names)>=limit:
            break
        if decision.agent.name in names or not usable(decision):
            continue
        names.append(decision.agent.name)
    return names

def execute_named(name:str,prompt:str,*,cwd:Path,timeout:int=1800)->dict:
    spec=DEFAULT_REGISTRY.get(name)
    if spec is None or not spec.available():
        return {"status":"unavailable","selected":None,"attempts":[{"agent":name,"status":"unavailable"}]}
    invocation=invocation_for(name,prompt)
    if invocation is None:
        return {"status":"unavailable","selected":None,"attempts":[{"agent":name,"status":"unsupported_adapter"}]}
    try:
        argv,extra_env=invocation
        run=AgentAdapter(spec).run(argv,cwd=cwd,timeout=timeout,extra_env=extra_env)
    except RuntimeError as exc:
        return {"status":"unavailable","selected":None,"attempts":[{"agent":name,"status":"error","error":str(exc)[:1000]}]}
    ok=run.returncode==0
    evidence=_run_evidence(run)
    evidence["status"]="passed" if ok else "failed"
    return {"status":"passed" if ok else "failed","selected":run.agent if ok else None,"attempts":[evidence]}


def routing_trace_for(name:str,required:set[str],*,role:str,memory_path:Path)->dict|None:
    perf=load(memory_path)
    history_raw=os.environ.get("STUDIO_ROUTING_HISTORY_PATH","")
    history=load_routing_history(Path(history_raw)) if history_raw else []
    weights=learned_weights(history,kind="agent",role=role)
    reliability={spec.name:bonus(perf,spec.name,role) for spec in DEFAULT_REGISTRY.all()}
    ranked=rank_agents(
        required,
        registry=DEFAULT_REGISTRY,
        prefer_free=True,
        long_task="long_task" in required,
        reliability=reliability,
        weights=weights,
    )
    decision=next((item for item in ranked if item.agent.name==name),None)
    return decision.trace if decision is not None else None

"""Autonomous capability routing with ordered fallbacks and evidence."""
from __future__ import annotations
from pathlib import Path
from .adapters import AgentAdapter
from .performance import bonus,load,record
from .registry import DEFAULT_REGISTRY
from .router import rank_agents

def argv_for(name:str,prompt:str)->list[str]|None:
    # Only invocation contracts verified by this project are enabled.
    if name=="opencode":
        return ["opencode","run","--format","json",prompt]
    return None

def execute(prompt:str,required:set[str],*,role:str,cwd:Path,memory_path:Path,timeout:int=1800)->dict:
    perf=load(memory_path)
    ranked=rank_agents(required,registry=DEFAULT_REGISTRY,prefer_free=True,long_task="long_task" in required)
    ranked.sort(key=lambda x:-(x.score+bonus(perf,x.agent.name,role)))
    attempts=[]
    for decision in ranked:
        if not decision.agent.available(): continue
        argv=argv_for(decision.agent.name,prompt)
        if argv is None:
            attempts.append({"agent":decision.agent.name,"status":"unsupported_adapter"})
            continue
        try:
            run=AgentAdapter(decision.agent).run(argv,cwd=cwd,timeout=timeout)
            ok=run.returncode==0
            record(memory_path,decision.agent.name,role,success=ok,duration=run.duration_seconds)
            evidence={"agent":run.agent,"status":"passed" if ok else "failed","returncode":run.returncode,
                "duration_seconds":run.duration_seconds,"stdout_tail":run.stdout_tail,"stderr_tail":run.stderr_tail}
            attempts.append(evidence)
            if ok: return {"status":"passed","selected":run.agent,"attempts":attempts}
        except RuntimeError as exc:
            attempts.append({"agent":decision.agent.name,"status":"error","error":str(exc)[:1000]})
    return {"status":"unavailable","selected":None,"attempts":attempts}

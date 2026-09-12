"""Autonomous capability routing with ordered fallbacks and evidence."""
from __future__ import annotations
from pathlib import Path
import json
import os
from .adapters import AgentAdapter
from .performance import bonus,eligible,load
from .registry import DEFAULT_REGISTRY
from .router import rank_agents

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
    if name=="hermes":
        return (["hermes","chat","--toolsets","file","-q",prompt],{"HERMES_YOLO_MODE":"1"})
    return None

def execute(prompt:str,required:set[str],*,role:str,cwd:Path,memory_path:Path,timeout:int=1800)->dict:
    perf=load(memory_path)
    ranked=rank_agents(required,registry=DEFAULT_REGISTRY,prefer_free=True,long_task="long_task" in required)
    ranked.sort(key=lambda x:-(x.score+bonus(perf,x.agent.name,role)))
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
            evidence={"agent":run.agent,"status":"passed" if ok else "failed","returncode":run.returncode,
                "duration_seconds":run.duration_seconds,"stdout_tail":run.stdout_tail,"stderr_tail":run.stderr_tail}
            attempts.append(evidence)
            if ok: return {"status":"passed","selected":run.agent,"attempts":attempts}
        except RuntimeError as exc:
            attempts.append({"agent":decision.agent.name,"status":"error","error":str(exc)[:1000]})
    return {"status":"unavailable","selected":None,"attempts":attempts}


def ranked_agent_names(required:set[str],*,role:str,memory_path:Path,limit:int=2)->list[str]:
    perf=load(memory_path)
    ranked=rank_agents(required,registry=DEFAULT_REGISTRY,prefer_free=True,long_task="long_task" in required)
    ranked.sort(key=lambda x:-(x.score+bonus(perf,x.agent.name,role)))
    names=[]
    for decision in ranked:
        if len(names)>=limit:
            break
        if not decision.agent.available() or not eligible(perf,decision.agent.name,role):
            continue
        if invocation_for(decision.agent.name,"probe") is None:
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
    evidence={"agent":run.agent,"status":"passed" if ok else "failed","returncode":run.returncode,
        "duration_seconds":run.duration_seconds,"stdout_tail":run.stdout_tail,"stderr_tail":run.stderr_tail}
    return {"status":"passed" if ok else "failed","selected":run.agent if ok else None,"attempts":[evidence]}

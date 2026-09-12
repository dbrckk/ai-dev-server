"""Autonomous capability routing with ordered fallbacks and evidence."""
from __future__ import annotations
from pathlib import Path
import json
import os
from .adapters import AgentAdapter
from .performance import bonus,load
from .registry import DEFAULT_REGISTRY
from .router import rank_agents

def _opencode_runtime(prompt:str)->tuple[list[str],dict[str,str]]:
    model=os.environ.get("STUDIO_CODE_MODEL") or os.environ.get("STUDIO_MODEL","")
    base=os.environ.get("STUDIO_API_BASE","")
    key=os.environ.get("STUDIO_API_KEY","")
    env={"OPENCODE_DISABLE_MODELS_FETCH":"1"}
    argv=["opencode","run","--format","json"]
    if model and base and key:
        config={
            "$schema":"https://opencode.ai/config.json",
            "share":"disabled",
            "provider":{
                "studio":{
                    "npm":"@ai-sdk/openai-compatible",
                    "name":"AI Dev Server provider",
                    "options":{"baseURL":"{env:STUDIO_API_BASE}","apiKey":"{env:STUDIO_API_KEY}"},
                    "models":{model:{}},
                }
            },
        }
        env["OPENCODE_CONFIG_CONTENT"]=json.dumps(config,separators=(",",":"))
        argv.extend(["--model","studio/"+model])
    argv.append(prompt)
    return argv,env

def invocation_for(name:str,prompt:str)->tuple[list[str],dict[str,str]]|None:
    # Only invocation contracts verified against upstream CLIs are enabled.
    if name=="opencode":
        return _opencode_runtime(prompt)
    return None

def execute(prompt:str,required:set[str],*,role:str,cwd:Path,memory_path:Path,timeout:int=1800)->dict:
    perf=load(memory_path)
    ranked=rank_agents(required,registry=DEFAULT_REGISTRY,prefer_free=True,long_task="long_task" in required)
    ranked.sort(key=lambda x:-(x.score+bonus(perf,x.agent.name,role)))
    attempts=[]
    for decision in ranked:
        if not decision.agent.available(): continue
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

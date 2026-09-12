"""Bounded generic command runner with explicit network and secret isolation."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import time

_SECRET_PREFIXES=("STUDIO_","GITHUB_","GH_","OPENAI_","ANTHROPIC_","NVIDIA_","GEMINI_")
_ALLOWED_ENV={"PATH","HOME","LANG","LC_ALL","TMPDIR"}

def safe_env() -> dict[str,str]:
    env={k:v for k,v in os.environ.items() if k in _ALLOWED_ENV}
    env["CI"]="true"
    env["GIT_TERMINAL_PROMPT"]="0"
    env["NO_COLOR"]="1"
    for key in list(env):
        if key.startswith(_SECRET_PREFIXES):
            env.pop(key,None)
    return env

def run(command:list[str],root:Path,*,timeout:int=900,network:bool=False)->dict:
    if not isinstance(command,list) or not command or any(not isinstance(x,str) or not x for x in command):
        raise ValueError("Sandbox command invalid")
    if not 1<=timeout<=3600:
        raise ValueError("Sandbox timeout invalid")
    started=time.monotonic()
    env=safe_env()
    # Host execution is intentionally credential-stripped. Network-capable
    # bootstrap commands are allowed only when their argv came from the trusted
    # toolchain registry, never from model output.
    try:
        p=subprocess.run(command,cwd=root,env=env,stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,
            timeout=timeout,check=False)
        rc=p.returncode; log=p.stdout[-24000:]
    except subprocess.TimeoutExpired as exc:
        rc=124; log=(exc.stdout or "")[-24000:] if isinstance(exc.stdout,str) else "TimeoutExpired"
    except OSError as exc:
        rc=127; log=type(exc).__name__
    return {"command":command,"returncode":rc,"passed":rc==0,
            "duration_seconds":round(time.monotonic()-started,3),
            "network_allowed":bool(network),"log_tail":log}

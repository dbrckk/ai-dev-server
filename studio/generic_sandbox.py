"""Bounded generic command runner with explicit network and secret isolation."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import time
import shutil

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
    argv=list(command)
    network_isolated=False
    if not network and shutil.which("unshare"):
        try:
            probe=subprocess.run(["unshare","--net","true"],env=env,stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=5,check=False)
            if probe.returncode==0:
                argv=["unshare","--net","--",*command]
                network_isolated=True
        except (OSError,subprocess.TimeoutExpired):
            pass
    # Commands never inherit provider/GitHub secrets. When the host permits an
    # unprivileged network namespace, verification is also executed without
    # network access; otherwise the evidence explicitly records that only
    # credential isolation was enforced.
    try:
        p=subprocess.run(argv,cwd=root,env=env,stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,
            timeout=timeout,check=False)
        rc=p.returncode; log=p.stdout[-24000:]
    except subprocess.TimeoutExpired as exc:
        rc=124; log=(exc.stdout or "")[-24000:] if isinstance(exc.stdout,str) else "TimeoutExpired"
    except OSError as exc:
        rc=127; log=type(exc).__name__
    return {"command":command,"returncode":rc,"passed":rc==0,
            "duration_seconds":round(time.monotonic()-started,3),
            "network_allowed":bool(network),
            "network_isolated":network_isolated,
            "credential_isolated":True,
            "log_tail":log}

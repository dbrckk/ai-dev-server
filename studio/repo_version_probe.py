"""Bounded GitHub semantic-version probe for replacement context."""
from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MAX_REPOS=8
TIMEOUT_SECONDS=4
SEMVER=re.compile(r"(?<!\d)v?(\d+)(?:\.\d+)?(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?")

def _major(value):
    if not isinstance(value,str):
        return None
    match=SEMVER.search(value.strip())
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None

def classify_release(value):
    if not isinstance(value,dict):
        return {"status":"unknown","major_version":None}
    tag=value.get("tag_name")
    major=_major(tag)
    return {
        "status":"known" if major is not None else "unknown",
        "tag_name":tag if isinstance(tag,str) else None,
        "major_version":major,
        "prerelease":value.get("prerelease") is True,
        "draft":value.get("draft") is True,
    }

def _fetch(repo,token):
    headers={
        "Accept":"application/vnd.github+json",
        "User-Agent":"ai-dev-server-version-probe",
    }
    if token:
        headers["Authorization"]="Bearer "+token
    req=Request("https://api.github.com/repos/"+repo+"/releases/latest",headers=headers)
    try:
        with urlopen(req,timeout=TIMEOUT_SECONDS) as response:
            value=json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return {"repo":repo,"status":"unknown","major_version":None,"reason":"http_"+str(exc.code)}
    except (URLError,TimeoutError,json.JSONDecodeError,UnicodeError) as exc:
        return {"repo":repo,"status":"unknown","major_version":None,"reason":type(exc).__name__}
    result=classify_release(value)
    result["repo"]=repo
    return result

def probe(repositories,token=None):
    unique=[]
    seen=set()
    for repo in repositories:
        if isinstance(repo,str) and "/" in repo and repo not in seen:
            seen.add(repo); unique.append(repo)
        if len(unique)>=MAX_REPOS:
            break
    token=token if token is not None else os.environ.get("GITHUB_TOKEN")
    if not unique:
        return {}
    out={}
    with ThreadPoolExecutor(max_workers=min(4,len(unique))) as pool:
        futures={pool.submit(_fetch,repo,token):repo for repo in unique}
        for future in as_completed(futures):
            repo=futures[future]
            try:
                out[repo]=future.result()
            except Exception as exc:
                out[repo]={"repo":repo,"status":"unknown","major_version":None,"reason":type(exc).__name__}
    return out

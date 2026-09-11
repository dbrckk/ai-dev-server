"""Persistent capability registry for studio adapters."""
from __future__ import annotations
import hashlib,json,os,tempfile
from pathlib import Path

VERSION=1
class CapabilityRegistryError(ValueError): pass

def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def _seal(v):
    x=dict(v); x.pop("registry_sha256",None)
    x["registry_sha256"]=hashlib.sha256(_canon(x)).hexdigest()
    return x

def new_registry():
    return _seal({"version":VERSION,"capabilities":{}})

def validate(registry):
    if not isinstance(registry,dict) or registry.get("version")!=VERSION or not isinstance(registry.get("capabilities"),dict):
        raise CapabilityRegistryError("registry invalid")
    digest=registry.get("registry_sha256")
    unsigned=dict(registry); unsigned.pop("registry_sha256",None)
    if not isinstance(digest,str) or hashlib.sha256(_canon(unsigned)).hexdigest()!=digest:
        raise CapabilityRegistryError("registry integrity failure")
    return registry

def register(registry,name,provider,evidence):
    validate(registry)
    if not isinstance(name,str) or not name.strip(): raise CapabilityRegistryError("name invalid")
    if not isinstance(provider,str) or not provider.strip(): raise CapabilityRegistryError("provider invalid")
    if not isinstance(evidence,dict) or not evidence: raise CapabilityRegistryError("evidence required")
    x={"version":VERSION,"capabilities":dict(registry["capabilities"])}
    x["capabilities"][name]={"provider":provider,"evidence":evidence}
    return _seal(x)

def has_capability(registry,name):
    validate(registry); return name in registry["capabilities"]

def save(path,registry):
    validate(registry); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(registry,f,sort_keys=True,ensure_ascii=False,indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        try: os.unlink(tmp)
        except FileNotFoundError: pass

def load(path):
    try: value=json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as e: raise CapabilityRegistryError("registry unreadable") from e
    return validate(value)

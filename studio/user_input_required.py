"""Safe user-input gate for genuinely external project prerequisites."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

_NAME_RE=re.compile(r"^[A-Z][A-Z0-9_]{2,127}$")
SECRET_NAME_RE=re.compile(
    r"\b([A-Z][A-Z0-9_]{2,}(?:API_KEY|TOKEN|SECRET|PASSWORD|ACCESS_KEY|PRIVATE_KEY))\b"
)


class UserInputRequiredError(ValueError):
    pass


def extract_secret_names(text: str) -> list[str]:
    if not isinstance(text,str):
        return []
    return sorted({
        match.group(1)
        for match in SECRET_NAME_RE.finditer(text)
        if _NAME_RE.fullmatch(match.group(1))
    })[:20]


def build(*, project_id: str, reason: str, required_env: list[str]) -> dict:
    if not isinstance(project_id,str) or not project_id.strip():
        raise UserInputRequiredError("user input project invalid")
    names=sorted({
        str(name).strip()
        for name in required_env
        if isinstance(name,str) and _NAME_RE.fullmatch(str(name).strip())
    })
    if not names:
        raise UserInputRequiredError("user input required_env invalid")
    return {
        "version":1,
        "status":"user_input_required",
        "project_id":project_id,
        "reason":str(reason or "external prerequisite required")[:1000],
        "required_env":names,
    }


def validate(value: dict) -> dict:
    if not isinstance(value,dict):
        raise UserInputRequiredError("user input state invalid")
    if value.get("version")!=1 or value.get("status")!="user_input_required":
        raise UserInputRequiredError("user input state version invalid")
    if not isinstance(value.get("project_id"),str) or not value["project_id"]:
        raise UserInputRequiredError("user input project invalid")
    names=value.get("required_env")
    if not isinstance(names,list) or not names:
        raise UserInputRequiredError("user input env list invalid")
    if any(not isinstance(name,str) or not _NAME_RE.fullmatch(name) for name in names):
        raise UserInputRequiredError("user input env name invalid")
    return value


def write(root: Path, value: dict) -> None:
    validate(value)
    root=Path(root)
    root.mkdir(parents=True,exist_ok=True)
    machine=root/"user-input-required.json"
    human=root/"USER_INPUT_REQUIRED.txt"
    machine.write_text(
        json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2)+"\n",
        encoding="utf-8",
    )
    human.write_text(
        "External input is required before autonomous work can continue.\\n\\n"
        + "Required environment/secret names:\n"
        + "".join(f"- {name}\n" for name in value["required_env"])
        + "\nReason:\n"
        + value["reason"]
        + "\n\nAdd the required value(s) to the configured secret/environment manager. "
          "Do not write secret values into these files. The next run will detect availability automatically.\n",
        encoding="utf-8",
    )


def load(path: Path) -> dict:
    try:
        value=json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        raise UserInputRequiredError("user input state unreadable") from exc
    return validate(value)


def missing_env(value: dict, environ: dict[str,str] | None = None) -> list[str]:
    validate(value)
    env=os.environ if environ is None else environ
    return [
        name for name in value["required_env"]
        if not isinstance(env.get(name),str) or not env.get(name)
    ]


def satisfied(value: dict, environ: dict[str,str] | None = None) -> bool:
    return not missing_env(value,environ)


def clear(root: Path) -> None:
    root=Path(root)
    for name in ("user-input-required.json","USER_INPUT_REQUIRED.txt"):
        try:
            (root/name).unlink()
        except FileNotFoundError:
            pass

"""Asset Forge routing bridge for premium visual production tasks."""
from __future__ import annotations

import re


VISUAL_TERMS = {
    "asset", "assets", "artwork", "sprite", "sprites", "texture", "textures",
    "icon", "icons", "logo", "ui", "graphic", "graphics", "visual", "visuals",
    "3d", "model", "models", "mesh", "meshes", "animation", "animations",
}
PREMIUM_TERMS = {"premium", "aaa", "professional", "production", "high quality", "polished"}


def should_route_to_asset_forge(task: dict) -> bool:
    if not isinstance(task, dict):
        return False
    text = " ".join(
        str(task.get(key) or "")
        for key in ("task", "objective", "instruction", "description", "title")
    ).lower()
    if not text.strip():
        return False
    tokens = set(re.findall(r"[a-z0-9]+", text))
    visual = bool(tokens & VISUAL_TERMS) or "pixel art" in text
    premium = any(term in text for term in PREMIUM_TERMS)
    explicit = task.get("requires_asset_forge") is True
    return explicit or (visual and premium)


def build_production_os_asset_dispatch(task: dict, *, project: str) -> dict:
    if not should_route_to_asset_forge(task):
        raise ValueError("task does not require asset-forge")
    asset_id = str(task.get("asset_id") or task.get("id") or "visual-asset").strip()
    asset_type = str(task.get("asset_type") or "icon").strip()
    target_format = str(task.get("format") or ("glb" if "3d" in str(task).lower() else "png")).strip().lower()
    instruction = str(
        task.get("instruction")
        or task.get("objective")
        or task.get("task")
        or task.get("description")
        or "Create a production-ready visual asset"
    ).strip()
    request_id = str(task.get("request_id") or f"{project}-{asset_id}").strip()
    engine = str(task.get("engine") or "").strip() or None

    args = [
        "production-os",
        "asset-forge-dispatch",
        "--request-id", request_id,
        "--project", project,
        "--asset-id", asset_id,
        "--asset-type", asset_type,
        "--instruction", instruction,
        "--format", target_format,
        "--backend", "auto",
    ]
    if engine:
        args.extend(["--engine", engine])

    return {
        "schema_version": "ai-dev-server/asset-forge-route/v1",
        "executor": "production-os",
        "capability": "asset-forge",
        "request_id": request_id,
        "project": project,
        "asset_id": asset_id,
        "command": args,
    }

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


def _infer_asset_shape(task: dict) -> tuple[str, str]:
    text = " ".join(str(task.get(key) or "") for key in ("task", "objective", "instruction", "description", "title")).lower()
    if "3d" in text or "mesh" in text or "model" in text:
        return "prop", "glb"
    if "sprite" in text or "pixel art" in text or "animation" in text:
        return "sprite-sheet", "png"
    if "texture" in text:
        return "texture", "png"
    if "logo" in text:
        return "logo", "svg"
    if "ui" in text:
        return "ui-vector", "svg"
    if "icon" in text:
        return "icon", "svg"
    return "icon", "png"


def build_production_os_asset_dispatch(
    task: dict,
    *,
    project: str,
    target_repository: str | None = None,
    target_worktree: str | None = None,
) -> dict:
    if not should_route_to_asset_forge(task):
        raise ValueError("task does not require asset-forge")
    inferred_type, inferred_format = _infer_asset_shape(task)
    asset_id = str(task.get("asset_id") or task.get("id") or "visual-asset").strip()
    asset_type = str(task.get("asset_type") or inferred_type).strip()
    target_format = str(task.get("format") or inferred_format).strip().lower()
    instruction = str(
        task.get("instruction")
        or task.get("objective")
        or task.get("task")
        or task.get("description")
        or "Create a production-ready visual asset"
    ).strip()
    request_id = str(task.get("request_id") or f"{project}-{asset_id}").strip()
    engine = str(task.get("engine") or "").strip() or None
    target_repository = str(task.get("target_repository") or target_repository or "").strip() or None
    target_worktree = str(task.get("target_worktree") or target_worktree or "").strip() or None
    default_root = "assets/art" if (engine or "").lower() in {"godot", "godot4", "godot-4", "libgdx"} else "assets/generated"
    target_path = str(task.get("target_path") or f"{default_root}/{asset_id}.{target_format}").strip()
    importance = str(task.get("importance") or ("primary" if any(term in instruction.lower() for term in PREMIUM_TERMS) else "secondary")).strip().lower()
    if importance not in {"primary", "secondary"}:
        raise ValueError("importance must be primary or secondary")

    args = [
        "production-os",
        "asset-forge-dispatch",
        "--request-id", request_id,
        "--project", project,
        "--asset-id", asset_id,
        "--asset-type", asset_type,
        "--instruction", instruction,
        "--format", target_format,
        "--importance", importance,
        "--backend", "auto",
    ]
    if engine:
        args.extend(["--engine", engine])
    if target_repository:
        args.extend(["--target-repository", target_repository])
    if target_path:
        args.extend(["--target-path", target_path])
    if target_worktree:
        args.extend(["--target-worktree", target_worktree])

    return {
        "schema_version": "ai-dev-server/asset-forge-route/v1",
        "executor": "production-os",
        "capability": "asset-forge",
        "request_id": request_id,
        "project": project,
        "asset_id": asset_id,
        "importance": importance,
        "target_repository": target_repository,
        "target_path": target_path,
        "command": args,
    }


def build_production_os_asset_batch(
    tasks: list[dict],
    *,
    project: str,
    target_repository: str | None = None,
    target_worktree: str | None = None,
) -> dict:
    routes = [
        build_production_os_asset_dispatch(
            task,
            project=project,
            target_repository=target_repository,
            target_worktree=target_worktree,
        )
        for task in tasks
        if should_route_to_asset_forge(task)
    ]
    if not routes:
        raise ValueError("batch contains no asset-forge tasks")

    items = []
    for task, route in zip(
        [task for task in tasks if should_route_to_asset_forge(task)],
        routes,
    ):
        inferred_type, inferred_format = _infer_asset_shape(task)
        asset_type = str(task.get("asset_type") or inferred_type).strip()
        target_format = str(task.get("format") or inferred_format).strip().lower()
        instruction = str(
            task.get("instruction")
            or task.get("objective")
            or task.get("task")
            or task.get("description")
            or "Create a production-ready visual asset"
        ).strip()
        engine = str(task.get("engine") or "").strip() or None
        source_mode = str(task.get("source_mode") or "generated").strip().lower()
        similarity_min = task.get("visual_similarity_min")
        similarity_retries = task.get("visual_similarity_retries")
        if similarity_min is None:
            similarity_min = 0.55 if route["importance"] == "primary" else 0.42
        if similarity_retries is None:
            similarity_retries = 2 if route["importance"] == "primary" else 1
        constraints = dict(task.get("constraints") or {}) if isinstance(task.get("constraints"), dict) else {}
        if target_format in {"png", "webp"}:
            constraints.setdefault("visualSimilarityMin", float(similarity_min))
            constraints.setdefault("visualSimilarityRetries", int(similarity_retries))

        request = {
            "schema": "asset-forge/production-request/v1",
            "requestId": route["request_id"],
            "instruction": instruction,
            "manifest": {
                "schema": "asset-forge/manifest/v1",
                "id": route["asset_id"],
                "project": project,
                "type": asset_type,
                "importance": route["importance"],
                "source": {
                    "mode": source_mode,
                    "uri": task.get("source_uri"),
                    "author": task.get("author"),
                },
                "license": {
                    "id": str(task.get("license_id") or "generated"),
                    "commercialUse": True,
                    "derivatives": True,
                    "attributionRequired": False,
                },
                "target": {
                    "format": target_format,
                    "engine": engine,
                },
                "constraints": constraints,
            },
        }
        if engine:
            request["delivery"] = {"engine": engine}
        raw_dependencies = task.get("depends_on")
        if raw_dependencies is None:
            implicit = (
                task.get("source_asset")
                or task.get("parent_asset")
                or task.get("variant_of")
                or task.get("animation_of")
                or task.get("atlas_of")
                or task.get("derived_from")
            )
            raw_dependencies = [implicit] if implicit else []
        elif isinstance(raw_dependencies, str):
            raw_dependencies = [raw_dependencies]
        if not isinstance(raw_dependencies, list):
            raise ValueError("asset dependency list must be an array")
        dependencies = [str(value).strip() for value in raw_dependencies if str(value).strip()]
        item = {
            "id": route["asset_id"],
            "depends_on": dependencies,
            "request": request,
            "target_path": route["target_path"],
        }
        if task.get("source_path"):
            item["source_path"] = str(task["source_path"])
        items.append(item)

    return {
        "schema_version": "ai-dev-server/asset-forge-batch-route/v1",
        "executor": "production-os",
        "capability": "asset-forge-batch",
        "project": project,
        "target_repository": target_repository,
        "target_worktree": target_worktree,
        "items": items,
        "routes": routes,
    }

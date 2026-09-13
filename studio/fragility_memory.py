"""Learn fragile files and modules from verified regression evidence."""
from __future__ import annotations

import json
from pathlib import Path

VERSION = 1
MAX_ROWS = 1000


def _zone(path: str) -> str:
    parts = [p for p in str(path).split("/") if p]
    if len(parts) <= 1:
        return "<root>"
    return "/".join(parts[:-1][:3])


def load(path: Path) -> dict:
    path = Path(path)
    if not path.is_file():
        return {"version": VERSION, "files": {}, "zones": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": VERSION, "files": {}, "zones": {}}
    if (
        not isinstance(value, dict)
        or value.get("version") != VERSION
        or not isinstance(value.get("files"), dict)
        or not isinstance(value.get("zones"), dict)
    ):
        return {"version": VERSION, "files": {}, "zones": {}}
    return value


def save(path: Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Bound retained history by keeping the riskiest entries.
    files = sorted(
        data.get("files", {}).items(),
        key=lambda item: (-float(item[1].get("risk", 0.0)), item[0]),
    )[:MAX_ROWS]
    zones = sorted(
        data.get("zones", {}).items(),
        key=lambda item: (-float(item[1].get("risk", 0.0)), item[0]),
    )[:MAX_ROWS]
    bounded = {"version": VERSION, "files": dict(files), "zones": dict(zones)}
    path.write_text(json.dumps(bounded, sort_keys=True, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _update(row: dict | None, *, regression: bool, safe: bool) -> dict:
    row = dict(row or {})
    regressions = int(row.get("regressions", 0)) + (1 if regression else 0)
    safe_changes = int(row.get("safe_changes", 0)) + (1 if safe else 0)
    observations = regressions + safe_changes
    # Beta-prior estimate avoids extreme risk from a single observation.
    risk = (regressions + 1.0) / (observations + 2.0)
    return {
        "regressions": regressions,
        "safe_changes": safe_changes,
        "observations": observations,
        "risk": round(risk, 4),
    }


def record(
    path: Path,
    *,
    culprit_files: list[str],
    safe_files: list[str],
) -> dict:
    data = load(path)
    files = data.setdefault("files", {})
    zones = data.setdefault("zones", {})

    for rel in sorted(set(culprit_files)):
        files[rel] = _update(files.get(rel), regression=True, safe=False)
        zone = _zone(rel)
        zones[zone] = _update(zones.get(zone), regression=True, safe=False)

    for rel in sorted(set(safe_files) - set(culprit_files)):
        files[rel] = _update(files.get(rel), regression=False, safe=True)
        zone = _zone(rel)
        zones[zone] = _update(zones.get(zone), regression=False, safe=True)

    save(path, data)
    return load(path)


def assess(data: dict, files: list[str] | None = None) -> dict:
    file_rows = data.get("files", {}) if isinstance(data, dict) else {}
    zone_rows = data.get("zones", {}) if isinstance(data, dict) else {}
    candidates = set(files or [])
    if not candidates:
        candidates.update(file_rows.keys())

    scored = []
    for rel in sorted(candidates):
        file_risk = float(file_rows.get(rel, {}).get("risk", 0.0))
        zone = _zone(rel)
        zone_risk = float(zone_rows.get(zone, {}).get("risk", 0.0))
        risk = max(file_risk, zone_risk)
        observations = max(
            int(file_rows.get(rel, {}).get("observations", 0)),
            int(zone_rows.get(zone, {}).get("observations", 0)),
        )
        if risk > 0:
            scored.append({
                "path": rel,
                "zone": zone,
                "risk": round(risk, 4),
                "observations": observations,
            })

    scored.sort(key=lambda x: (-x["risk"], -x["observations"], x["path"]))
    top = scored[:20]
    max_risk = top[0]["risk"] if top else 0.0

    if max_risk >= 0.75:
        level = "high"
        max_patch_files = 2
        extra_verification = True
    elif max_risk >= 0.55:
        level = "medium"
        max_patch_files = 4
        extra_verification = True
    else:
        level = "low"
        max_patch_files = 8
        extra_verification = False

    return {
        "level": level,
        "max_risk": max_risk,
        "max_patch_files": max_patch_files,
        "extra_verification": extra_verification,
        "fragile_paths": top,
    }

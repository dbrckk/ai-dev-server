"""Persistent learning for architecture-safe rewrite recovery."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

MAX_EVENTS = 500
MIN_SAMPLES = 5
MAX_PENALTY = 0.25
DECAY_HALF_LIFE_EVENTS = 20.0
MIN_EVENT_WEIGHT = 0.05
RECENT_WINDOW = 8


def _decay_weight(age: int) -> float:
    age = max(0, int(age))
    weight = 0.5 ** (age / DECAY_HALF_LIFE_EVENTS)
    return max(MIN_EVENT_WEIGHT, weight)


def _weighted_rate(rows: list[tuple[dict, float]], field: str) -> float:
    total = sum(weight for _, weight in rows)
    if total <= 0:
        return 0.0
    return sum(weight * int(event.get(field) is True) for event, weight in rows) / total


def _recent_success_streak(events: list[dict], field: str) -> int:
    streak = 0
    for event in reversed(events[-RECENT_WINDOW:]):
        if event.get(field) is True:
            streak += 1
        else:
            break
    return streak


def load(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": 1, "events": []}
    if not isinstance(value, dict) or value.get("schema") != 1:
        return {"schema": 1, "events": []}
    events = value.get("events")
    if not isinstance(events, list):
        events = []
    return {"schema": 1, "events": [x for x in events[-MAX_EVENTS:] if isinstance(x, dict)]}


def _save(path: Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def record_attempt(
    path: Path,
    *,
    event_id: str,
    engine: str,
    origin_kind: str,
    origin_name: str,
    rewrite_kind: str,
    rewrite_name: str,
    guard_passed: bool,
) -> dict:
    data = load(path)
    event = {
        "event_id": str(event_id)[:160],
        "engine": str(engine)[:40],
        "origin_kind": str(origin_kind)[:40],
        "origin_name": str(origin_name)[:200],
        "rewrite_kind": str(rewrite_kind)[:40],
        "rewrite_name": str(rewrite_name)[:200],
        "guard_passed": bool(guard_passed),
        "verification_passed": None,
        "review_passed": None,
        "completed": False,
        "sequence": len(data["events"]),
    }
    data["events"] = [x for x in data["events"] if x.get("event_id") != event["event_id"]]
    data["events"].append(event)
    data["events"] = data["events"][-MAX_EVENTS:]
    _save(path, data)
    return event


def finalize(
    path: Path,
    *,
    event_id: str,
    verification_passed: bool,
    review_passed: bool | None = None,
) -> dict | None:
    data = load(path)
    target = None
    for event in data["events"]:
        if event.get("event_id") == event_id:
            event["verification_passed"] = bool(verification_passed)
            event["review_passed"] = bool(review_passed) if review_passed is not None else None
            event["completed"] = True
            target = dict(event)
            break
    if target is not None:
        _save(path, data)
    return target


def summarize(path: Path) -> dict:
    events = load(path)["events"]
    completed = [e for e in events if e.get("completed") is True]
    newest_index = max(0, len(completed) - 1)

    def rows(kind_key: str, name_key: str) -> list[dict]:
        grouped = {}
        for index, event in enumerate(completed):
            name = event.get(name_key)
            kind = event.get(kind_key)
            if not isinstance(name, str) or not name:
                continue
            key = (str(kind or "unknown"), name)
            row = grouped.setdefault(key, {
                "kind": key[0],
                "name": name,
                "samples": 0,
                "guard_passes": 0,
                "verification_passes": 0,
                "review_passes": 0,
                "_weighted_events": [],
                "_events": [],
            })
            row["samples"] += 1
            row["guard_passes"] += int(event.get("guard_passed") is True)
            row["verification_passes"] += int(event.get("verification_passed") is True)
            row["review_passes"] += int(event.get("review_passed") is True)
            weight = _decay_weight(newest_index - index)
            row["_weighted_events"].append((event, weight))
            row["_events"].append(event)
        result = []
        for row in grouped.values():
            n = max(1, row["samples"])
            row["guard_pass_rate"] = round(row["guard_passes"] / n, 4)
            row["verification_pass_rate"] = round(row["verification_passes"] / n, 4)
            row["review_pass_rate"] = round(row["review_passes"] / n, 4)
            weighted = row.pop("_weighted_events")
            raw_events = row.pop("_events")
            row["decayed_guard_pass_rate"] = round(_weighted_rate(weighted, "guard_passed"), 4)
            row["decayed_verification_pass_rate"] = round(_weighted_rate(weighted, "verification_passed"), 4)
            row["decayed_review_pass_rate"] = round(_weighted_rate(weighted, "review_passed"), 4)
            row["effective_sample_weight"] = round(sum(weight for _, weight in weighted), 4)
            row["recent_verification_streak"] = _recent_success_streak(raw_events, "verification_passed")
            row["rehabilitating"] = row["recent_verification_streak"] >= 3
            row["eligible_for_routing_bias"] = row["samples"] >= MIN_SAMPLES
            result.append(row)
        result.sort(key=lambda x: (-x["verification_pass_rate"], -x["guard_pass_rate"], -x["samples"], x["name"]))
        return result

    return {
        "schema": 1,
        "events": len(events),
        "completed_events": len(completed),
        "origin_rankings": rows("origin_kind", "origin_name"),
        "rewrite_rankings": rows("rewrite_kind", "rewrite_name"),
        "policy": {
            "minimum_samples": MIN_SAMPLES,
            "max_penalty": MAX_PENALTY,
            "decay_half_life_events": DECAY_HALF_LIFE_EVENTS,
            "minimum_event_weight": MIN_EVENT_WEIGHT,
            "recent_window": RECENT_WINDOW,
        },
    }


def origin_violation_penalty(summary: dict, *, kind: str, name: str, role: str) -> float:
    """Bounded score-point penalty for repeatedly triggering architecture-safe recovery."""
    fraction = routing_penalty(summary, kind=kind, name=name, role=role)
    return round(fraction * 100.0, 4)


def rewrite_recovery_bonus(summary: dict, *, kind: str, name: str, role: str) -> float:
    """Conservative bonus for models/providers that repeatedly recover rejected patches."""
    if role != "implementation" or not isinstance(summary, dict):
        return 0.0
    rows = summary.get("rewrite_rankings")
    if not isinstance(rows, list):
        return 0.0
    for row in rows:
        if row.get("kind") != kind or row.get("name") != name:
            continue
        samples = row.get("samples")
        if not isinstance(samples, int) or samples < MIN_SAMPLES:
            return 0.0
        verify_rate = float(row.get("decayed_verification_pass_rate", row.get("verification_pass_rate", 0.0)))
        review_rate = float(row.get("decayed_review_pass_rate", row.get("review_pass_rate", 0.0)))
        quality = min(verify_rate, review_rate if row.get("review_passes", 0) else verify_rate)
        if quality <= 0.6:
            return 0.0
        # Smaller than the maximum violation penalty: recovery skill must not
        # make architecture violations strategically desirable.
        return round(min(10.0, (quality - 0.6) / 0.4 * 10.0), 4)
    return 0.0


def routing_penalty(summary: dict, *, kind: str, name: str, role: str) -> float:
    if role != "implementation" or not isinstance(summary, dict):
        return 0.0
    rows = summary.get("origin_rankings")
    if not isinstance(rows, list):
        return 0.0
    for row in rows:
        if row.get("kind") != kind or row.get("name") != name:
            continue
        samples = row.get("samples")
        if not isinstance(samples, int) or samples < MIN_SAMPLES:
            return 0.0
        verify_rate = float(row.get("decayed_verification_pass_rate", row.get("verification_pass_rate", 0.0)))
        if row.get("rehabilitating") is True:
            verify_rate = min(1.0, verify_rate + 0.15)
        # Penalize only repeatedly poor origins; never reward architecture violations.
        if verify_rate >= 0.6:
            return 0.0
        severity = min(1.0, (0.6 - verify_rate) / 0.6)
        return round(min(MAX_PENALTY, MAX_PENALTY * severity), 4)
    return 0.0

"""Deterministic bounded artwork capability.

Returns SVG assets only. It performs no network, filesystem, subprocess, or registry actions.
"""
from __future__ import annotations

import hashlib
import html
import json
import re

HEX_RE = re.compile(r"#[0-9a-fA-F]{6}")
MAX_TEXT = 120
MAX_ASSETS = 3


class ArtworkCapabilityError(ValueError):
    pass


def _color(value, fallback):
    if isinstance(value, str) and HEX_RE.fullmatch(value):
        return value.upper()
    return fallback


def _label(value):
    if not isinstance(value, str):
        return "APP"
    clean = " ".join(value.split()).strip()
    if not clean:
        return "APP"
    return clean[:MAX_TEXT]


def _palette(context):
    design = context.get("design")
    if not isinstance(design, dict):
        design = {}
    primary = _color(design.get("primary"), "#182030")
    accent = _color(design.get("accent"), "#5A64F6")
    return primary, accent


def _icon_svg(label, primary, accent):
    mark = html.escape(label[:2].upper())
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{primary}"/><stop offset="1" stop-color="{accent}"/>'
        '</linearGradient></defs>'
        '<rect width="512" height="512" rx="112" fill="url(#g)"/>'
        '<circle cx="256" cy="220" r="118" fill="#FFFFFF" fill-opacity=".16"/>'
        f'<text x="256" y="292" text-anchor="middle" font-family="sans-serif" font-size="132" font-weight="700" fill="#FFFFFF">{mark}</text>'
        '</svg>'
    )


def _feature_svg(label, primary, accent):
    safe = html.escape(label)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="500" viewBox="0 0 1024 500">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{primary}"/><stop offset="1" stop-color="{accent}"/>'
        '</linearGradient></defs>'
        '<rect width="1024" height="500" fill="url(#g)"/>'
        '<circle cx="820" cy="250" r="190" fill="#FFFFFF" fill-opacity=".10"/>'
        '<circle cx="850" cy="250" r="112" fill="#FFFFFF" fill-opacity=".12"/>'
        f'<text x="72" y="272" font-family="sans-serif" font-size="72" font-weight="700" fill="#FFFFFF">{safe}</text>'
        '</svg>'
    )


def run(context):
    if not isinstance(context, dict):
        raise ArtworkCapabilityError("context invalid")
    encoded = json.dumps(context, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(encoded) > 64_000:
        raise ArtworkCapabilityError("context too large")

    label = _label(context.get("label") or context.get("objective") or "APP")
    primary, accent = _palette(context)
    requested = context.get("assets", ["icon", "feature_graphic"])
    if not isinstance(requested, list) or not requested or len(requested) > MAX_ASSETS:
        raise ArtworkCapabilityError("assets request invalid")
    if any(item not in {"icon", "feature_graphic"} for item in requested):
        raise ArtworkCapabilityError("unsupported artwork asset")
    if len(set(requested)) != len(requested):
        raise ArtworkCapabilityError("duplicate artwork asset")

    assets = {}
    if "icon" in requested:
        svg = _icon_svg(label, primary, accent)
        assets["icon"] = {
            "format": "svg",
            "width": 512,
            "height": 512,
            "content": svg,
            "sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest(),
        }
    if "feature_graphic" in requested:
        svg = _feature_svg(label, primary, accent)
        assets["feature_graphic"] = {
            "format": "svg",
            "width": 1024,
            "height": 500,
            "content": svg,
            "sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest(),
        }

    return {
        "passed": True,
        "evidence": {
            "generator": "deterministic-svg-v1",
            "asset_count": len(assets),
            "primary": primary,
            "accent": accent,
        },
        "assets": assets,
    }

"""Provider-neutral artwork capability contract with deterministic fallback."""
from __future__ import annotations

import hashlib
from pathlib import Path

try:
    from .capability_registry import has_capability, validate as validate_registry
    from .store_package import decode_png
except ImportError:
    from capability_registry import has_capability, validate as validate_registry
    from store_package import decode_png

ARTWORK_CAPABILITY="store.artwork.generate"

REQUIREMENTS={
    "icon":{"width":512,"height":512},
    "feature_graphic":{"width":1024,"height":500},
}


class ArtworkError(ValueError):
    pass


def select_provider(registry):
    validate_registry(registry)
    if has_capability(registry,ARTWORK_CAPABILITY):
        item=registry["capabilities"][ARTWORK_CAPABILITY]
        return {
            "mode":"capability",
            "provider":item["provider"],
            "evidence":item["evidence"],
            "requires_local_validation":True,
        }
    return {
        "mode":"deterministic_fallback",
        "provider":"studio.store_package._brand_image",
        "evidence":{"trusted_builtin":True},
        "requires_local_validation":True,
    }


def validate_asset(path,kind):
    if kind not in REQUIREMENTS:
        raise ArtworkError("artwork kind invalid")
    path=Path(path)
    if not path.is_file():
        raise ArtworkError("artwork missing")
    try:
        width,height,_=decode_png(path)
    except (OSError,ValueError):
        raise ArtworkError("artwork png invalid") from None
    req=REQUIREMENTS[kind]
    if width!=req["width"] or height!=req["height"]:
        raise ArtworkError("artwork dimensions invalid")
    raw=path.read_bytes()
    if not raw:
        raise ArtworkError("artwork empty")
    return {
        "file":path.name,
        "kind":kind,
        "width":width,
        "height":height,
        "sha256":hashlib.sha256(raw).hexdigest(),
        "validated":True,
    }


def validate_artwork_set(icon_path,feature_path,*,provider_selection,visual_qa):
    if not isinstance(provider_selection,dict) or provider_selection.get("requires_local_validation") is not True:
        raise ArtworkError("provider selection invalid")
    if not isinstance(visual_qa,dict) or visual_qa.get("passed") is not True:
        raise ArtworkError("visual qa required")
    icon=validate_asset(icon_path,"icon")
    feature=validate_asset(feature_path,"feature_graphic")
    return {
        "passed":True,
        "provider":provider_selection["provider"],
        "provider_mode":provider_selection["mode"],
        "assets":{"icon":icon,"feature_graphic":feature},
        "visual_qa":visual_qa,
    }

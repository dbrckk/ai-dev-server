"""Provider-neutral artwork capability contract with deterministic fallback."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

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


SHA40_RE=re.compile(r"[0-9a-f]{40}")
SHA256_RE=re.compile(r"[0-9a-f]{64}")
ALLOWED_LICENSE_STATUS={"generated_original","project_owned","permissive_verified"}


def _provider_provenance(selection: dict) -> dict:
    mode=selection.get("mode")
    provider=selection.get("provider")
    evidence=selection.get("evidence")
    if mode=="deterministic_fallback" and provider=="studio.store_package._brand_image":
        return {
            "origin":"studio_generated",
            "external_sources":False,
            "license_status":"generated_original",
            "provider_identity":"trusted_builtin",
        }
    if (
        mode=="capability"
        and provider=="studio.capabilities.asset_artwork"
        and isinstance(evidence,dict)
        and evidence.get("source")=="promoted_factory_capability"
        and isinstance(evidence.get("candidate_sha"),str)
        and SHA40_RE.fullmatch(evidence["candidate_sha"])
    ):
        return {
            "origin":"studio_generated",
            "external_sources":False,
            "license_status":"generated_original",
            "provider_identity":evidence["candidate_sha"],
        }
    explicit=evidence.get("provenance") if isinstance(evidence,dict) else None
    if not isinstance(explicit,dict):
        raise ArtworkError("artwork provider provenance missing")
    required={"origin","external_sources","license_status","provider_identity"}
    if set(explicit)!=required:
        raise ArtworkError("artwork provider provenance invalid")
    origin=explicit.get("origin")
    external=explicit.get("external_sources")
    license_status=explicit.get("license_status")
    identity=explicit.get("provider_identity")
    if origin not in {"studio_generated","project_owned","verified_external"}:
        raise ArtworkError("artwork provenance origin invalid")
    if type(external) is not bool or license_status not in ALLOWED_LICENSE_STATUS:
        raise ArtworkError("artwork provenance license invalid")
    if not isinstance(identity,str) or not identity or len(identity)>200:
        raise ArtworkError("artwork provenance identity invalid")
    if external:
        if origin!="verified_external" or license_status!="permissive_verified" or not SHA256_RE.fullmatch(identity):
            raise ArtworkError("external artwork provenance insufficient")
    elif origin=="verified_external":
        raise ArtworkError("external artwork provenance inconsistent")
    return dict(explicit)


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



def builtin_visual_qa(icon_path,feature_path):
    metrics={}
    for kind,path in (("icon",Path(icon_path)),("feature_graphic",Path(feature_path))):
        try:
            width,height,pixels=decode_png(path)
        except (OSError,ValueError):
            raise ArtworkError("artwork visual decode failed") from None
        if not pixels:
            raise ArtworkError("artwork visual payload empty")
        sample_step=max(4,(len(pixels)//4//4096)*4)
        colors=set()
        luminance=[]
        for i in range(0,len(pixels),sample_step):
            if i+3>=len(pixels):
                break
            rgb=(pixels[i],pixels[i+1],pixels[i+2])
            colors.add(rgb)
            luminance.append((299*rgb[0]+587*rgb[1]+114*rgb[2])//1000)
            if len(colors)>256:
                break
        if len(colors)<8:
            raise ArtworkError("artwork visual diversity too low")
        if not luminance or max(luminance)-min(luminance)<24:
            raise ArtworkError("artwork visual contrast too low")
        metrics[kind]={
            "width":width,
            "height":height,
            "sampled_unique_colors":len(colors),
            "luminance_range":max(luminance)-min(luminance),
        }
    return {"passed":True,"checks":["png_decode","visual_diversity","contrast"],"metrics":metrics}

def validate_artwork_set(icon_path,feature_path,*,provider_selection,visual_qa):
    if not isinstance(provider_selection,dict) or provider_selection.get("requires_local_validation") is not True:
        raise ArtworkError("provider selection invalid")
    if not isinstance(visual_qa,dict) or visual_qa.get("passed") is not True:
        raise ArtworkError("visual qa required")
    provenance=_provider_provenance(provider_selection)
    icon=validate_asset(icon_path,"icon")
    feature=validate_asset(feature_path,"feature_graphic")
    return {
        "passed":True,
        "provider":provider_selection["provider"],
        "provider_mode":provider_selection["mode"],
        "provenance":provenance,
        "assets":{"icon":icon,"feature_graphic":feature},
        "visual_qa":visual_qa,
    }

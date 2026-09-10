"""Deterministic final review for a Godot Google Play release candidate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from core import StudioError

SHA_RE=re.compile(r'^[0-9a-f]{64}$')
REQUIRED_COVERAGE=(
    'android_export','device_qa','journeys_executed','visual_qa',
    'release_artifact','release_signed','store_metadata','privacy_qa','security_qa',
)

def _sha(v)->bool:
    return isinstance(v,str) and SHA_RE.fullmatch(v) is not None

def _verify_file(path:Path,digest:str,label:str)->None:
    if not _sha(digest): raise StudioError(label+' hash evidence invalid')
    if not path.is_file() or path.is_symlink(): raise StudioError(label+' artifact missing')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=digest: raise StudioError(label+' artifact hash mismatch')

def review(root:Path,out:Path,state:dict)->dict:
    if state.get('engine')!='godot' or state.get('status')!='godot_privacy_security_validated':
        raise StudioError('Godot final review requires validated privacy/security state')
    if state.get('blockers') not in ([],None):
        raise StudioError('Godot final review refuses unresolved blockers')
    coverage=state.get('coverage')
    if not isinstance(coverage,dict):
        raise StudioError('Godot final review coverage missing')
    missing=[key for key in REQUIRED_COVERAGE if coverage.get(key) is not True]
    if missing:
        raise StudioError('Godot final review missing coverage: '+','.join(missing))

    artifact=state.get('release_artifact'); store=state.get('store_metadata'); privacy=state.get('privacy_security')
    preflight=state.get('release_preflight'); visual=state.get('visual_qa')
    if not all(isinstance(x,dict) for x in (artifact,store,privacy,preflight,visual)):
        raise StudioError('Godot final review evidence bundle incomplete')
    if artifact.get('format')!='aab' or artifact.get('signing_scope')!='artifact_only' or artifact.get('project_code_had_signing_material') is not False:
        raise StudioError('Godot final review signing boundary invalid')
    if not _sha(artifact.get('certificate_sha256')):
        raise StudioError('Godot final review upload certificate evidence invalid')
    if int(preflight.get('target_api',0))<36 or int(artifact.get('target_api',0))<36:
        raise StudioError('Godot final review target API below required level')
    if artifact.get('package')!=preflight.get('package') or artifact.get('version_code')!=preflight.get('version_code') or artifact.get('version_name')!=preflight.get('version_name'):
        raise StudioError('Godot final review release identity mismatch')

    aab_hash=artifact.get('aab_sha256'); manifest_hash=store.get('manifest_sha256')
    if privacy.get('release_aab_sha256')!=aab_hash or privacy.get('store_manifest_sha256')!=manifest_hash:
        raise StudioError('Godot final review cross-stage hash binding mismatch')
    _verify_file(out/'app-release.aab',aab_hash,'Signed AAB')
    _verify_file(out/'play-store-godot'/'manifest.json',manifest_hash,'Play manifest')
    _verify_file(out/'privacy-godot'/'privacy-policy.md',privacy.get('policy_sha256'),'Privacy policy')
    _verify_file(out/'privacy-godot'/'data-safety.json',privacy.get('data_safety_sha256'),'Data Safety')

    shots=visual.get('screenshot_sha256')
    if not isinstance(shots,list) or len(shots)<1 or any(not _sha(x) for x in shots):
        raise StudioError('Godot final review visual evidence invalid')
    if int(store.get('screenshot_count',0))<2:
        raise StudioError('Godot final review Play screenshot evidence incomplete')
    data_safety=privacy.get('data_safety')
    if not isinstance(data_safety,dict) or data_safety.get('requires_human_legal_attestation') is not True:
        raise StudioError('Godot final review Data Safety attestation contract invalid')

    bundle={
        'release_aab_sha256':aab_hash,
        'certificate_sha256':artifact['certificate_sha256'],
        'store_manifest_sha256':manifest_hash,
        'privacy_policy_sha256':privacy['policy_sha256'],
        'data_safety_sha256':privacy['data_safety_sha256'],
        'package':artifact.get('package'),
        'version_code':artifact.get('version_code'),
        'version_name':artifact.get('version_name'),
        'target_api':artifact.get('target_api'),
        'screenshot_count':store.get('screenshot_count'),
    }
    bundle_sha=hashlib.sha256(json.dumps(bundle,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {
        'passed':True,
        'technical_store_ready':True,
        'release_bundle':bundle,
        'release_bundle_sha256':bundle_sha,
        'human_actions_required':[
            'developer_contact_email',
            'content_rating_declaration',
            'target_audience_declaration',
            'data_safety_legal_attestation',
            'play_console_submission',
        ],
        'published':False,
    }

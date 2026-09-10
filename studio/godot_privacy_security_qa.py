"""Trusted privacy and security audit for Godot Play releases."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from core import StudioError
from godot_store_metadata_qa import privacy_classification

SECRET_PATTERNS=(
    re.compile(r'gh[pousr]_[A-Za-z0-9_]{20,}'),
    re.compile(r'sk-[A-Za-z0-9_-]{20,}'),
    re.compile(r'nvapi-[A-Za-z0-9_-]{15,}'),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
)
DANGEROUS_MARKERS=('OS.execute(','OS.shell_open(','JavaScriptBridge','GDExtension')
CLEARTEXT_RE=re.compile(r'http://(?!schemas\.android\.com)[A-Za-z0-9.-]+(?::\d+)?(?:/[^\s"\']*)?')

def _sha(value)->bool:
    return isinstance(value,str) and re.fullmatch(r'[0-9a-f]{64}',value) is not None

def _source_files(root:Path)->list[Path]:
    files=[]
    for rel in ('project.godot','export_presets.cfg'):
        p=root/rel
        if p.is_file() and not p.is_symlink(): files.append(p)
    for folder in ('scripts','scenes','assets','docs'):
        base=root/folder
        if not base.exists(): continue
        for p in base.rglob('*'):
            if p.is_file() and not p.is_symlink() and p.stat().st_size<=500000 and p.suffix.lower() in {'.gd','.tscn','.tres','.cfg','.json','.md','.txt','.svg'}:
                files.append(p)
    return sorted(files)

def audit(root:Path,out:Path,state:dict)->dict:
    artifact=state.get('release_artifact') or {}; store=state.get('store_metadata') or {}
    aab_hash=artifact.get('aab_sha256'); manifest_hash=store.get('manifest_sha256')
    if not _sha(aab_hash) or not _sha(manifest_hash):
        raise StudioError('Godot privacy/security QA requires signed AAB and store manifest hashes')
    aab=out/'app-release.aab'; manifest=out/'play-store-godot'/'manifest.json'
    if not aab.is_file() or hashlib.sha256(aab.read_bytes()).hexdigest()!=aab_hash:
        raise StudioError('Signed AAB is missing or changed before privacy/security QA')
    if not manifest.is_file() or hashlib.sha256(manifest.read_bytes()).hexdigest()!=manifest_hash:
        raise StudioError('Play store manifest is missing or changed before privacy/security QA')
    chunks=[]; scanned=[]
    for p in _source_files(root):
        text=p.read_text(errors='replace'); chunks.append(text); scanned.append(p.relative_to(root).as_posix())
    source='\n'.join(chunks)
    secret_hits=sum(1 for pattern in SECRET_PATTERNS if pattern.search(source))
    dangerous=sorted(marker for marker in DANGEROUS_MARKERS if marker in source)
    cleartext=sorted(set(CLEARTEXT_RE.findall(source)))
    privacy=privacy_classification(root)
    blockers=[]
    if secret_hits: blockers.append('credential_like_material_detected')
    if dangerous: blockers.append('dangerous_runtime_bridge_requires_review')
    if cleartext: blockers.append('cleartext_network_endpoint_detected')
    if not privacy.get('can_derive_no_external_collection'): blockers.extend(privacy.get('blockers') or ['privacy_classification_incomplete'])
    policy_dir=out/'privacy-godot'; policy_dir.mkdir(parents=True,exist_ok=True)
    data_safety={
        'data_collected':False if privacy.get('can_derive_no_external_collection') else None,
        'data_shared':False if privacy.get('can_derive_no_external_collection') else None,
        'basis':'trusted_static_godot_audit',
        'requires_human_legal_attestation':True,
        'release_aab_sha256':aab_hash,
        'store_manifest_sha256':manifest_hash,
    }
    (policy_dir/'data-safety.json').write_text(json.dumps(data_safety,sort_keys=True,indent=2)+'\n')
    title=(store.get('listing') or {}).get('title') or 'Mobile App'
    policy=(f'# Privacy Policy for {title}\n\n'
            'This policy is generated from the exact audited release artifact and store manifest.\n\n'
            '## Data handling\n'
            + ('No external collection or sharing capability was detected by the trusted static Godot audit.\n'
               if privacy.get('can_derive_no_external_collection') else
               'Potential data-flow capabilities were detected and require verified classification before publication.\n')
            + '\n## Contact\nDeveloper contact information must be supplied from the verified Play Console account.\n')
    (policy_dir/'privacy-policy.md').write_text(policy)
    return {
        'passed':not blockers,
        'blockers':sorted(set(blockers)),
        'release_aab_sha256':aab_hash,
        'store_manifest_sha256':manifest_hash,
        'privacy':privacy,
        'data_safety':data_safety,
        'policy_sha256':hashlib.sha256((policy_dir/'privacy-policy.md').read_bytes()).hexdigest(),
        'data_safety_sha256':hashlib.sha256((policy_dir/'data-safety.json').read_bytes()).hexdigest(),
        'scanned_files':scanned,
        'dangerous_markers':dangerous,
        'cleartext_endpoints':cleartext,
        'secret_patterns_detected':secret_hits,
        'human_legal_attestation_required':True,
    }

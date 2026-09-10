"""Build fail-closed Google Play metadata from validated Godot evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from core import StudioError
from store_package import _brand_image, listing_from_state, store_screenshot

NETWORK_MARKERS = (
    'HTTPRequest', 'HTTPClient', 'WebSocketPeer', 'WebSocketMultiplayerPeer',
    'ENetMultiplayerPeer', 'TCPServer', 'StreamPeerTCP', 'PacketPeerUDP',
)
SENSITIVE_PERMISSIONS = (
    'ACCESS_FINE_LOCATION','ACCESS_COARSE_LOCATION','CAMERA','RECORD_AUDIO',
    'READ_CONTACTS','WRITE_CONTACTS','READ_CALENDAR','WRITE_CALENDAR',
    'READ_SMS','SEND_SMS','READ_PHONE_STATE','BLUETOOTH_CONNECT','POST_NOTIFICATIONS',
)

def _sha(value)->bool:
    return isinstance(value,str) and re.fullmatch(r'[0-9a-f]{64}',value) is not None

def _project_text(root:Path)->str:
    chunks=[]
    for rel in ('project.godot','export_presets.cfg'):
        p=root/rel
        if p.is_file() and not p.is_symlink() and p.stat().st_size<=300000:
            chunks.append(p.read_text(errors='replace'))
    for folder in ('scripts','scenes'):
        base=root/folder
        if not base.exists(): continue
        for p in base.rglob('*'):
            if p.is_file() and not p.is_symlink() and p.stat().st_size<=500000 and p.suffix in {'.gd','.tscn','.tres','.cfg','.json'}:
                chunks.append(p.read_text(errors='replace'))
    return '\n'.join(chunks)

def privacy_classification(root:Path)->dict:
    text=_project_text(root)
    network=sorted(marker for marker in NETWORK_MARKERS if marker in text)
    preset=root/'export_presets.cfg'
    custom=[]
    if preset.is_file():
        raw=preset.read_text(errors='replace')
        m=re.search(r'(?m)^permissions/custom_permissions=PackedStringArray\((.*)\)$',raw)
        if m:
            custom=sorted(set(re.findall(r'"([^"]+)"',m.group(1))))
    sensitive=sorted(p for p in custom if any(name in p for name in SENSITIVE_PERMISSIONS))
    safe=not network and not sensitive
    return {
        'network_markers':network,
        'custom_permissions':custom,
        'sensitive_permissions':sensitive,
        'can_derive_no_external_collection':safe,
        'requires_human_legal_attestation':True,
        'blockers':[] if safe else ['verified_data_flow_classification_required'],
    }

def _validated_screens(out:Path,state:dict)->list[Path]:
    visual=state.get('visual_qa') or {}
    expected=visual.get('screenshot_sha256')
    if not isinstance(expected,list) or not expected or any(not _sha(x) for x in expected):
        raise StudioError('Godot store metadata requires validated visual screenshot hashes')
    found=[]
    for p in sorted(out.glob('godot-visual-*.png')):
        if p.is_file() and not p.is_symlink():
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            if digest in expected and digest not in [x[0] for x in found]:
                found.append((digest,p))
    if [x[0] for x in found] != expected:
        by_hash={d:p for d,p in found}
        if not all(h in by_hash for h in expected):
            raise StudioError('Validated Godot visual screenshots are missing or changed')
        found=[(h,by_hash[h]) for h in expected]
    device=state.get('device_qa') or {}
    device_hash=device.get('screenshot_sha256')
    device_path=out/'godot-device.png'
    if len(found)<2 and _sha(device_hash) and device_path.is_file() and hashlib.sha256(device_path.read_bytes()).hexdigest()==device_hash:
        if device_hash not in {d for d,_ in found}: found.append((device_hash,device_path))
    if len(found)<2:
        raise StudioError('At least two distinct validated Android screenshots are required for Play metadata')
    return [p for _,p in found[:8]]

def build(req:dict,root:Path,out:Path,state:dict)->dict:
    artifact=state.get('release_artifact') or {}
    if not _sha(artifact.get('aab_sha256')) or artifact.get('format')!='aab':
        raise StudioError('Godot store metadata requires a validated signed AAB')
    listing=listing_from_state(req,state)
    store=out/'play-store-godot'; shots=store/'screenshots'/'phone'; shots.mkdir(parents=True,exist_ok=True)
    screen_evidence=[]
    for i,source in enumerate(_validated_screens(out,state),1):
        screen_evidence.append(store_screenshot(source,shots/f'{i:02d}.png'))
    icon=store/'icon-512.png'; feature=store/'feature-graphic-1024x500.png'
    icon.write_bytes(_brand_image(512,512,state.get('design',{}),False))
    feature.write_bytes(_brand_image(1024,500,state.get('design',{}),True))
    privacy=privacy_classification(root)
    listing_dir=store/'listing'/'en-US'; listing_dir.mkdir(parents=True,exist_ok=True)
    (listing_dir/'title.txt').write_text(listing['title']+'\n')
    (listing_dir/'short-description.txt').write_text(listing['short_description']+'\n')
    (listing_dir/'full-description.txt').write_text(listing['full_description']+'\n')
    manifest={
        'listing':listing,
        'release_aab_sha256':artifact['aab_sha256'],
        'screenshots':screen_evidence,
        'assets':{
            'icon':{'width':512,'height':512,'sha256':hashlib.sha256(icon.read_bytes()).hexdigest()},
            'feature_graphic':{'width':1024,'height':500,'sha256':hashlib.sha256(feature.read_bytes()).hexdigest()},
        },
        'privacy':privacy,
        'submission_fields_required':['developer_contact_email','content_rating','target_audience','data_safety_legal_attestation'],
    }
    path=store/'manifest.json'; path.write_text(json.dumps(manifest,sort_keys=True,ensure_ascii=False,indent=2)+'\n')
    return {
        'passed':True,
        'listing':listing,
        'screenshot_count':len(screen_evidence),
        'manifest_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'release_aab_sha256':artifact['aab_sha256'],
        'privacy':privacy,
        'assets':manifest['assets'],
        'human_submission_required':True,
    }

"""Derive privacy policy and Play Data Safety evidence from the generated app."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

NETWORK_MARKERS = (
    'HttpClient(', 'http://', 'https://', 'WebSocket(', 'Socket.connect(',
    'package:http/', 'package:dio/', 'Firebase', 'firebase_', 'supabase', 'graphql',
)
LOCAL_STORAGE_MARKERS = (
    'shared_preferences', 'hive', 'sqflite', 'isar', 'path_provider', 'File(', 'Directory(',
)
SENSITIVE_PERMISSION_DATA = {
    'android.permission.ACCESS_FINE_LOCATION': 'location',
    'android.permission.ACCESS_COARSE_LOCATION': 'location',
    'android.permission.CAMERA': 'photos_or_videos',
    'android.permission.RECORD_AUDIO': 'audio',
    'android.permission.READ_CONTACTS': 'contacts',
    'android.permission.WRITE_CONTACTS': 'contacts',
    'android.permission.READ_CALENDAR': 'calendar',
    'android.permission.WRITE_CALENDAR': 'calendar',
    'android.permission.READ_SMS': 'messages',
    'android.permission.SEND_SMS': 'messages',
    'android.permission.READ_PHONE_STATE': 'device_or_other_ids',
    'android.permission.BLUETOOTH_CONNECT': 'device_or_other_ids',
}


def _files(root: Path) -> list[Path]:
    allowed = []
    for folder in ('lib', 'android/app/src/main'):
        base = root / folder
        if not base.exists():
            continue
        for path in base.rglob('*'):
            if path.is_file() and not path.is_symlink() and path.stat().st_size <= 500000:
                allowed.append(path)
    return allowed


def _text(root: Path) -> str:
    chunks = []
    for path in _files(root):
        try:
            chunks.append(path.read_text(errors='replace'))
        except OSError:
            pass
    pubspec = root / 'pubspec.yaml'
    if pubspec.is_file():
        chunks.append(pubspec.read_text(errors='replace'))
    return '\n'.join(chunks)


def permissions(root: Path) -> list[str]:
    manifest = root / 'android/app/src/main/AndroidManifest.xml'
    if not manifest.is_file():
        return []
    return sorted(set(re.findall(r'<uses-permission[^>]+android:name=["\']([^"\']+)["\']', manifest.read_text(errors='replace'))))


def dependency_names(root: Path) -> list[str]:
    pubspec = root / 'pubspec.yaml'
    if not pubspec.is_file():
        return []
    names = []
    in_dependencies = False
    for raw in pubspec.read_text(errors='replace').splitlines():
        line = raw.rstrip()
        if re.match(r'^dependencies:\s*$', line):
            in_dependencies = True
            continue
        if in_dependencies and re.match(r'^[A-Za-z_][A-Za-z0-9_-]*:\s*$', line) and not line.startswith('  '):
            break
        if in_dependencies:
            match = re.match(r'^\s{2}([A-Za-z_][A-Za-z0-9_-]*):', line)
            if match and match.group(1) != 'flutter':
                names.append(match.group(1))
    return sorted(set(names))


def analyze(root: Path) -> dict:
    source = _text(root)
    perms = permissions(root)
    deps = dependency_names(root)
    network_markers = sorted(marker for marker in NETWORK_MARKERS if marker in source)
    local_markers = sorted(marker for marker in LOCAL_STORAGE_MARKERS if marker in source)
    sensitive = sorted(set(SENSITIVE_PERMISSION_DATA[p] for p in perms if p in SENSITIVE_PERMISSION_DATA))
    internet_permission = 'android.permission.INTERNET' in perms
    network_capable = internet_permission or bool(network_markers)
    local_storage = bool(local_markers)

    blockers = []
    if network_capable:
        blockers.append('network_capability_requires_verified_data_flow_classification')
    if sensitive:
        blockers.append('sensitive_permissions_require_verified_collection_purpose')

    return {
        'permissions': perms,
        'dependencies': deps,
        'network_capable': network_capable,
        'network_markers': network_markers,
        'local_storage_detected': local_storage,
        'local_storage_markers': local_markers,
        'sensitive_data_classes': sensitive,
        'can_assert_no_external_collection': not network_capable and not sensitive,
        'blockers': blockers,
    }


def build_data_safety(audit: dict) -> dict:
    if audit['can_assert_no_external_collection']:
        return {
            'status': 'derived',
            'data_collected': False,
            'data_shared': False,
            'basis': 'No network capability or sensitive permission detected by trusted static audit.',
            'local_processing_only': bool(audit['local_storage_detected']),
            'requires_human_legal_attestation': True,
        }
    return {
        'status': 'needs_verified_classification',
        'data_collected': None,
        'data_shared': None,
        'basis': 'Static evidence cannot safely classify all data flows.',
        'local_processing_only': None,
        'requires_human_legal_attestation': True,
        'blockers': list(audit['blockers']),
    }


def policy_text(app_title: str, audit: dict, data_safety: dict) -> str:
    sections = [
        f'# Privacy Policy for {app_title}',
        '',
        'This policy is generated from the application build and static privacy audit. It must remain consistent with the released binary and store declarations.',
        '',
        '## Data handling',
    ]
    if data_safety['status'] == 'derived':
        sections.append('The audited build does not contain detected network capability or sensitive Android permissions that would support external collection of personal data.')
        if audit['local_storage_detected']:
            sections.append('The application may store app state locally on the device. This local data is not detected as being transmitted externally by the audited build.')
    else:
        sections.append('The audited build contains capabilities that could involve personal-data processing. Collection and sharing cannot be truthfully classified from static evidence alone and must be verified before publication.')
    sections += [
        '',
        '## Android permissions',
        ', '.join(audit['permissions']) if audit['permissions'] else 'No explicit Android permissions were detected.',
        '',
        '## Third-party dependencies',
        ', '.join(audit['dependencies']) if audit['dependencies'] else 'No non-SDK Dart dependencies were detected in pubspec.yaml.',
        '',
        '## Contact',
        'The developer contact address must be supplied from the verified store account at submission time.',
    ]
    return '\n'.join(sections).strip() + '\n'


def build_privacy_package(root: Path, out: Path, state: dict) -> dict:
    audit = analyze(root)
    safety = build_data_safety(audit)
    title = state.get('release_evidence', {}).get('store_metadata', {}).get('listing', {}).get('title')
    if not isinstance(title, str) or not title.strip():
        title = 'Mobile App'
    folder = out / 'privacy'
    folder.mkdir(parents=True, exist_ok=True)
    policy = policy_text(title, audit, safety)
    (folder / 'privacy-policy.md').write_text(policy)
    manifest = {
        'audit': audit,
        'data_safety': safety,
        'external_submission_fields': ['developer_contact_email', 'legal_attestation'],
    }
    manifest_path = folder / 'data-safety.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    passed = safety['status'] == 'derived'
    return {
        'passed': passed,
        'audit': audit,
        'data_safety': safety,
        'policy_sha256': hashlib.sha256((folder / 'privacy-policy.md').read_bytes()).hexdigest(),
        'data_safety_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        'blockers': [] if passed else list(audit['blockers']),
    }

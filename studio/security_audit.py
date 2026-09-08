"""Trusted static security, dependency and provenance audit for generated apps."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

SECRET_PATTERNS = {
    'private_key': re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
    'github_token': re.compile(r'gh[pousr]_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+'),
    'openai_key': re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b'),
    'nvidia_key': re.compile(r'\bnvapi-[A-Za-z0-9_-]{15,}\b'),
}
DANGEROUS_PERMISSIONS = {
    'android.permission.READ_SMS', 'android.permission.SEND_SMS',
    'android.permission.READ_CALL_LOG', 'android.permission.WRITE_CALL_LOG',
    'android.permission.READ_PHONE_STATE', 'android.permission.MANAGE_EXTERNAL_STORAGE',
    'android.permission.SYSTEM_ALERT_WINDOW', 'android.permission.REQUEST_INSTALL_PACKAGES',
    'android.permission.PACKAGE_USAGE_STATS', 'android.permission.WRITE_SETTINGS',
    'android.permission.BIND_ACCESSIBILITY_SERVICE',
}
SENSITIVE_PERMISSIONS = {
    'android.permission.ACCESS_FINE_LOCATION', 'android.permission.ACCESS_COARSE_LOCATION',
    'android.permission.CAMERA', 'android.permission.RECORD_AUDIO',
    'android.permission.READ_CONTACTS', 'android.permission.WRITE_CONTACTS',
    'android.permission.READ_CALENDAR', 'android.permission.WRITE_CALENDAR',
    'android.permission.BLUETOOTH_CONNECT', 'android.permission.POST_NOTIFICATIONS',
} | DANGEROUS_PERMISSIONS
CLEAR_TEXT = re.compile(r'http://(?!schemas\.android\.com/)[^\s\"\'<>]+', re.I)


def _candidate_files(root: Path) -> list[Path]:
    files = []
    for rel in ('lib', 'android', 'ios', 'assets', 'docs'):
        base = root / rel
        if not base.exists():
            continue
        for path in base.rglob('*'):
            if (path.is_file() and not path.is_symlink() and path.stat().st_size <= 800000 and
                    not any(part in {'build', '.dart_tool', '.gradle'} for part in path.parts)):
                files.append(path)
    for rel in ('pubspec.yaml', 'pubspec.lock', 'analysis_options.yaml'):
        path = root / rel
        if path.is_file() and not path.is_symlink() and path.stat().st_size <= 800000:
            files.append(path)
    return sorted(set(files))


def _text_files(root: Path):
    for path in _candidate_files(root):
        try:
            yield path, path.read_text(errors='replace')
        except OSError:
            continue


def android_permissions(root: Path) -> list[str]:
    manifest = root / 'android/app/src/main/AndroidManifest.xml'
    if not manifest.is_file():
        return []
    return sorted(set(re.findall(r'<uses-permission[^>]+android:name=["\']([^"\']+)["\']',
                                 manifest.read_text(errors='replace'))))


def dependency_inventory(root: Path) -> list[dict]:
    lock = root / 'pubspec.lock'
    if not lock.is_file():
        return []
    packages = []
    current = None
    for raw in lock.read_text(errors='replace').splitlines():
        match = re.match(r'^  ([A-Za-z_][A-Za-z0-9_-]*):\s*$', raw)
        if match:
            if current:
                packages.append(current)
            current = {'name': match.group(1), 'version': None, 'source': None}
            continue
        if current:
            version = re.match(r'^    version:\s*["\']?([^"\']+)["\']?\s*$', raw)
            source = re.match(r'^    source:\s*([^\s]+)\s*$', raw)
            if version:
                current['version'] = version.group(1)
            elif source:
                current['source'] = source.group(1)
    if current:
        packages.append(current)
    return sorted(packages, key=lambda item: item['name'])


def dependency_risks(root: Path, dependencies: list[dict]) -> list[str]:
    pubspec = (root / 'pubspec.yaml').read_text(errors='replace') if (root / 'pubspec.yaml').is_file() else ''
    blockers = []
    if re.search(r'^\s{2,}[A-Za-z_][A-Za-z0-9_-]*:\s*\n\s+(git|path):', pubspec, re.M):
        blockers.append('unreviewed_git_or_path_dependency')
    for dep in dependencies:
        if not dep.get('version') and dep.get('source') not in ('sdk', None):
            blockers.append('dependency_without_locked_version:' + dep['name'])
    return sorted(set(blockers))


def scan(root: Path) -> dict:
    secrets = []
    cleartext_endpoints = []
    debug_flags = []
    executable_markers = []
    for path, text in _text_files(root):
        rel = path.relative_to(root).as_posix()
        for kind, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                secrets.append({'type': kind, 'path': rel})
        for endpoint in CLEAR_TEXT.findall(text):
            cleartext_endpoints.append({'path': rel, 'endpoint': endpoint[:180]})
        if 'android:debuggable="true"' in text:
            debug_flags.append({'path': rel, 'flag': 'android_debuggable_true'})
        if 'android:usesCleartextTraffic="true"' in text:
            debug_flags.append({'path': rel, 'flag': 'android_cleartext_traffic_enabled'})
        if re.search(r'Process\.run\(|Runtime\.getRuntime\(\)\.exec|/bin/sh|bash -c', text):
            executable_markers.append({'path': rel, 'marker': 'process_execution'})

    permissions = android_permissions(root)
    dangerous = sorted(p for p in permissions if p in DANGEROUS_PERMISSIONS)
    sensitive = sorted(p for p in permissions if p in SENSITIVE_PERMISSIONS)
    dependencies = dependency_inventory(root)
    dep_risks = dependency_risks(root, dependencies)

    blockers = []
    if secrets:
        blockers.append('credential_material_detected')
    if dangerous:
        blockers.append('dangerous_android_permissions_require_explicit_review')
    if cleartext_endpoints or any(item['flag'] == 'android_cleartext_traffic_enabled' for item in debug_flags):
        blockers.append('cleartext_network_traffic_detected')
    if any(item['flag'] == 'android_debuggable_true' for item in debug_flags):
        blockers.append('release_manifest_debuggable')
    if executable_markers:
        blockers.append('runtime_process_execution_detected')
    blockers.extend(dep_risks)

    return {
        'passed': not blockers,
        'blockers': sorted(set(blockers)),
        'secrets': secrets,
        'permissions': permissions,
        'sensitive_permissions': sensitive,
        'dangerous_permissions': dangerous,
        'cleartext_endpoints': cleartext_endpoints,
        'android_flags': debug_flags,
        'process_execution_markers': executable_markers,
        'dependencies': dependencies,
    }


def sbom(root: Path, audit: dict) -> dict:
    components = []
    for dep in audit['dependencies']:
        components.append({
            'type': 'library', 'name': dep['name'], 'version': dep.get('version'),
            'source': dep.get('source'), 'license_status': 'not_resolved_offline',
        })
    pubspec = root / 'pubspec.yaml'
    app_hash = hashlib.sha256(pubspec.read_bytes()).hexdigest() if pubspec.is_file() else None
    return {
        'format': 'studio-sbom-v1',
        'application_pubspec_sha256': app_hash,
        'components': components,
        'license_resolution': 'deferred_to_registry_or_cache_audit',
    }


def build_security_package(root: Path, out: Path) -> dict:
    audit = scan(root)
    bom = sbom(root, audit)
    folder = out / 'security'
    folder.mkdir(parents=True, exist_ok=True)
    audit_path = folder / 'audit.json'
    sbom_path = folder / 'sbom.json'
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    sbom_path.write_text(json.dumps(bom, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    return {
        'passed': audit['passed'],
        'blockers': audit['blockers'],
        'audit_sha256': hashlib.sha256(audit_path.read_bytes()).hexdigest(),
        'sbom_sha256': hashlib.sha256(sbom_path.read_bytes()).hexdigest(),
        'dependency_count': len(audit['dependencies']),
        'sensitive_permissions': audit['sensitive_permissions'],
        'dangerous_permissions': audit['dangerous_permissions'],
        'license_status': 'inventory_complete_resolution_deferred',
    }

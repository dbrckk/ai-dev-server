"""Classify generated app capabilities and derive mandatory QA profiles."""
from __future__ import annotations

from pathlib import Path
import re

PERMISSION_PROFILES = {
    'android.permission.CAMERA': 'native_qa',
    'android.permission.ACCESS_FINE_LOCATION': 'native_qa',
    'android.permission.ACCESS_COARSE_LOCATION': 'native_qa',
    'android.permission.BLUETOOTH_CONNECT': 'native_qa',
    'android.permission.BLUETOOTH_SCAN': 'native_qa',
    'android.permission.RECORD_AUDIO': 'native_qa',
    'android.permission.POST_NOTIFICATIONS': 'notification_qa',
}
DEPENDENCY_PROFILES = {
    'camera': 'native_qa',
    'geolocator': 'native_qa',
    'location': 'native_qa',
    'permission_handler': 'native_qa',
    'local_auth': 'native_qa',
    'flutter_blue_plus': 'native_qa',
    'firebase_messaging': 'notification_qa',
    'flutter_local_notifications': 'notification_qa',
    'in_app_purchase': 'billing_qa',
    'purchases_flutter': 'billing_qa',
    'webview_flutter': 'platform_view_qa',
    'google_maps_flutter': 'platform_view_qa',
    'video_player': 'platform_view_qa',
    'flame': 'performance_qa',
    'forge2d': 'performance_qa',
}
SOURCE_PROFILES = {
    'PlatformViewLink': 'platform_view_qa',
    'AndroidView(': 'platform_view_qa',
    'UiKitView(': 'platform_view_qa',
    'InAppPurchase': 'billing_qa',
    'FirebaseMessaging': 'notification_qa',
    'LocalNotifications': 'notification_qa',
    'GameWidget(': 'performance_qa',
    'FlameGame': 'performance_qa',
}
PROFILE_STAGE = {
    'performance_qa': 'performance_qa',
    'native_qa': 'native_qa',
    'notification_qa': 'notification_qa',
    'billing_qa': 'billing_qa',
    'platform_view_qa': 'platform_view_qa',
}


def _manifest_permissions(root: Path) -> list[str]:
    path = root / 'android/app/src/main/AndroidManifest.xml'
    if not path.is_file():
        return []
    text = path.read_text(errors='replace')
    return sorted(set(re.findall(r'<uses-permission[^>]+android:name=["\']([^"\']+)["\']', text)))


def _dependencies(root: Path) -> list[str]:
    path = root / 'pubspec.yaml'
    if not path.is_file():
        return []
    names = []
    in_deps = False
    for raw in path.read_text(errors='replace').splitlines():
        if re.match(r'^dependencies:\s*$', raw):
            in_deps = True
            continue
        if in_deps and raw and not raw.startswith(' '):
            break
        if in_deps:
            match = re.match(r'^\s{2}([A-Za-z_][A-Za-z0-9_-]*):', raw)
            if match and match.group(1) != 'flutter':
                names.append(match.group(1))
    return sorted(set(names))


def _source_text(root: Path) -> str:
    chunks = []
    lib = root / 'lib'
    if lib.exists():
        for path in sorted(lib.rglob('*.dart')):
            if path.is_file() and not path.is_symlink() and path.stat().st_size <= 500000:
                chunks.append(path.read_text(errors='replace'))
    return '\n'.join(chunks)


def classify(root: Path) -> dict:
    permissions = _manifest_permissions(root)
    dependencies = _dependencies(root)
    source = _source_text(root)
    profiles = {'standard'}
    reasons = []

    for permission in permissions:
        profile = PERMISSION_PROFILES.get(permission)
        if profile:
            profiles.add(profile)
            reasons.append({'profile': profile, 'source': 'permission', 'value': permission})
    for dependency in dependencies:
        profile = DEPENDENCY_PROFILES.get(dependency)
        if profile:
            profiles.add(profile)
            reasons.append({'profile': profile, 'source': 'dependency', 'value': dependency})
    for marker, profile in SOURCE_PROFILES.items():
        if marker in source:
            profiles.add(profile)
            reasons.append({'profile': profile, 'source': 'source_marker', 'value': marker})

    ordered = ['standard'] + sorted(p for p in profiles if p != 'standard')
    required_stages = [PROFILE_STAGE[p] for p in ordered if p in PROFILE_STAGE]
    return {
        'passed': True,
        'profiles': ordered,
        'required_qa_stages': required_stages,
        'permissions': permissions,
        'dependencies': dependencies,
        'reasons': reasons,
    }

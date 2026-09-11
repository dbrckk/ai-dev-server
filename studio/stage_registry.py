"""Trusted stage registry for bounded autonomous mobile completion."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re


@dataclass(frozen=True)
class Stage:
    name: str
    script: str
    deferred_status: str
    failed_status: str


STAGES = {
    'real_device': Stage('real_device', 'studio/device_stage.py', 'deferred_device', 'device_failed'),
    'capability_qa': Stage('capability_qa', 'studio/capability_stage.py', 'deferred_capability', 'capability_failed'),
    'performance_qa': Stage('performance_qa', 'studio/performance_stage.py', 'deferred_performance', 'performance_failed'),
    'native_qa': Stage('native_qa', 'studio/native_stage.py', 'deferred_native', 'native_failed'),
    'notification_qa': Stage('notification_qa', 'studio/notification_stage.py', 'deferred_notification', 'notification_failed'),
    'billing_qa': Stage('billing_qa', 'studio/billing_stage.py', 'deferred_billing', 'billing_failed'),
    'platform_view_qa': Stage('platform_view_qa', 'studio/platform_view_stage.py', 'deferred_platform_view', 'platform_view_failed'),
    'store_metadata': Stage('store_metadata', 'studio/store_stage.py', 'deferred_store', 'store_failed'),
    'artwork_qa': Stage('artwork_qa', 'studio/artwork_stage.py', 'deferred_artwork', 'artwork_failed'),
    'privacy_policy': Stage('privacy_policy', 'studio/privacy_stage.py', 'deferred_privacy', 'privacy_failed'),
    'security_scan': Stage('security_scan', 'studio/security_stage.py', 'deferred_security', 'security_failed'),
}

PROMOTED_REGISTRY = Path(__file__).resolve().parents[1] / 'control' / 'promoted_stages.json'


def _promoted_stage(name: str) -> Stage | None:
    if not re.fullmatch(r'[a-z][a-z0-9_]{2,48}_qa', name):
        return None
    if not PROMOTED_REGISTRY.exists():
        return None
    try:
        value = json.loads(PROMOTED_REGISTRY.read_text())
    except (OSError, json.JSONDecodeError):
        raise RuntimeError('Promoted-stage registry unreadable') from None
    if not isinstance(value, dict) or value.get('version') != 1 or not isinstance(value.get('stages'), dict):
        raise RuntimeError('Promoted-stage registry malformed')
    entry = value['stages'].get(name)
    if entry is None:
        return None
    if not isinstance(entry, dict) or set(entry) != {'script', 'candidate_id', 'baseline_sha', 'candidate_sha'}:
        raise RuntimeError('Promoted-stage entry malformed')
    expected_script = f"studio/{name[:-3]}_stage.py"
    if entry.get('script') != expected_script:
        raise RuntimeError('Promoted-stage script mismatch')
    if not isinstance(entry.get('candidate_id'), str) or not entry['candidate_id']:
        raise RuntimeError('Promoted-stage candidate identity missing')
    for key in ('baseline_sha', 'candidate_sha'):
        if not isinstance(entry.get(key), str) or not re.fullmatch(r'[0-9a-f]{40}', entry[key]):
            raise RuntimeError('Promoted-stage commit identity invalid')
    return Stage(name, expected_script, 'deferred_' + name[:-3], name[:-3] + '_failed')


def get_stage(name: str) -> Stage | None:
    return STAGES.get(name) or _promoted_stage(name)

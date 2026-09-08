"""Trusted stage registry for bounded autonomous mobile completion."""
from __future__ import annotations

from dataclasses import dataclass


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
    'store_metadata': Stage('store_metadata', 'studio/store_stage.py', 'deferred_store', 'store_failed'),
    'privacy_policy': Stage('privacy_policy', 'studio/privacy_stage.py', 'deferred_privacy', 'privacy_failed'),
    'security_scan': Stage('security_scan', 'studio/security_stage.py', 'deferred_security', 'security_failed'),
}


def get_stage(name: str) -> Stage | None:
    return STAGES.get(name)

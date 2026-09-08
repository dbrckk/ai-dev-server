"""Trusted Android QA for notification-capable Flutter apps."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from core import StudioError
from device_qa import package_name, run_command, start_emulator, wait_for_boot

POST_NOTIFICATIONS = 'android.permission.POST_NOTIFICATIONS'
CRASH_PATTERNS = ('FATAL EXCEPTION', 'AndroidRuntime: FATAL', 'ANR in ', 'Unhandled Exception')
NOTIFICATION_DEPENDENCIES = ('firebase_messaging', 'flutter_local_notifications')


def _serial(adb: str) -> str:
    explicit = os.environ.get('ANDROID_SERIAL')
    if explicit:
        return explicit
    devices = run_command([adb, 'devices'], timeout=30).stdout.splitlines()
    serials = [line.split()[0] for line in devices[1:] if '\tdevice' in line]
    if len(serials) != 1:
        raise StudioError('Notification QA requires exactly one Android target')
    return serials[0]


def _dependencies(root: Path) -> list[str]:
    pubspec = root / 'pubspec.yaml'
    if not pubspec.is_file():
        return []
    found = []
    in_dependencies = False
    for raw in pubspec.read_text(errors='replace').splitlines():
        if re.match(r'^dependencies:\s*$', raw):
            in_dependencies = True
            continue
        if in_dependencies and raw and not raw.startswith(' '):
            break
        if in_dependencies:
            match = re.match(r'^\s{2}([A-Za-z_][A-Za-z0-9_-]*):', raw)
            if match and match.group(1) != 'flutter':
                found.append(match.group(1))
    return sorted(set(found))


def _manifest_permissions(root: Path) -> list[str]:
    manifest = root / 'android/app/src/main/AndroidManifest.xml'
    if not manifest.is_file():
        return []
    return sorted(set(re.findall(
        r'<uses-permission[^>]+android:name=["\']([^"\']+)["\']',
        manifest.read_text(errors='replace'))))


def _launch(adb: str, serial: str, pkg: str) -> subprocess.CompletedProcess:
    return run_command([adb, '-s', serial, 'shell', 'monkey', '-p', pkg, '-c',
                        'android.intent.category.LAUNCHER', '1'], timeout=60)


def _crashes(adb: str, serial: str) -> list[str]:
    result = run_command([adb, '-s', serial, 'logcat', '-d', '-v', 'brief'], timeout=60)
    return [line for line in result.stdout.splitlines()
            if any(pattern in line for pattern in CRASH_PATTERNS)]


def _notification_dump(adb: str, serial: str) -> str:
    result = run_command([adb, '-s', serial, 'shell', 'dumpsys', 'notification', '--noredact'], timeout=60)
    return result.stdout if result.returncode == 0 else ''


def _count_package_notifications(text: str, pkg: str) -> int:
    if not text or not pkg:
        return 0
    # NotificationRecord lines consistently carry pkg=<application id>; count only the target app.
    return sum(1 for line in text.splitlines()
               if 'NotificationRecord' in line and re.search(r'\bpkg=' + re.escape(pkg) + r'(?:\s|$)', line))


def validate_notifications(root: Path, out: Path, adb: str = 'adb') -> dict:
    apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
    if not apk.is_file() or apk.stat().st_size < 1000:
        return {'passed': False, 'blockers': ['release_apk_missing']}
    if shutil.which(adb) is None:
        return {'passed': False, 'blockers': ['adb_unavailable']}

    emulator = None
    owned_emulator = False
    serial = None
    try:
        if run_command([adb, 'get-state'], timeout=10).returncode != 0:
            emulator = start_emulator()
            owned_emulator = True
        boot = wait_for_boot(adb)
        if not boot.get('passed'):
            return {'passed': False, 'blockers': ['emulator_boot_timeout']}
        serial = _serial(adb)
        pkg = package_name(root)
        install = run_command([adb, '-s', serial, 'install', '-r', '-t', str(apk)], timeout=180)
        if install.returncode:
            return {'passed': False, 'blockers': ['release_install_failed']}

        deps = _dependencies(root)
        declared = _manifest_permissions(root)
        capability_sources = {
            'post_notifications_permission': POST_NOTIFICATIONS in declared,
            'dependencies': [name for name in deps if name in NOTIFICATION_DEPENDENCIES],
        }
        blockers: list[str] = []
        states = []

        # Android 13+ notification permission path. Apps targeting older SDKs may not expose this permission;
        # dependency evidence still keeps observation requirements fail-closed.
        if POST_NOTIFICATIONS in declared:
            for state, verb in (('denied', 'revoke'), ('granted', 'grant')):
                run_command([adb, '-s', serial, 'logcat', '-c'], timeout=30)
                command = run_command([adb, '-s', serial, 'shell', 'pm', verb, pkg, POST_NOTIFICATIONS], timeout=30)
                launch = _launch(adb, serial, pkg)
                time.sleep(2)
                # Exercise background / resume because notification handling frequently crosses lifecycle states.
                run_command([adb, '-s', serial, 'shell', 'input', 'keyevent', '3'], timeout=30)
                time.sleep(1)
                resume = _launch(adb, serial, pkg)
                time.sleep(2)
                crash_lines = _crashes(adb, serial)
                states.append({
                    'state': state,
                    'permission_exit': command.returncode,
                    'launch_exit': launch.returncode,
                    'resume_exit': resume.returncode,
                    'crash_count': len(crash_lines),
                })
                if command.returncode:
                    blockers.append('notification_permission_state_control_failed:' + state)
                if launch.returncode or resume.returncode or crash_lines:
                    blockers.append('notification_lifecycle_unstable:' + state)

        # Observe only app-originated notifications. We deliberately do not use `cmd notification post`
        # because that would prove the shell can notify, not that the release APK can.
        before = _count_package_notifications(_notification_dump(adb, serial), pkg)
        run_command([adb, '-s', serial, 'shell', 'monkey', '-p', pkg,
                     '--throttle', '100', '--pct-syskeys', '0', '80'], timeout=120)
        run_command([adb, '-s', serial, 'shell', 'input', 'keyevent', '3'], timeout=30)
        time.sleep(5)
        after_dump = _notification_dump(adb, serial)
        after = _count_package_notifications(after_dump, pkg)
        observed = after > before or after > 0

        if _crashes(adb, serial):
            blockers.append('notification_runtime_crash_or_anr_detected')
        if not observed:
            blockers.append('no_app_originated_notification_observed')

        # Push delivery cannot be claimed without a trusted sender / credential. Local-notification apps can pass
        # when the release APK itself posts one; Firebase-only apps remain blocked rather than fabricating evidence.
        if 'firebase_messaging' in deps and not observed:
            blockers.append('external_push_delivery_not_exercised')

        payload = {
            'passed': not blockers,
            'environment': 'android_emulator',
            'package': pkg,
            'capability_sources': capability_sources,
            'permission_states': states,
            'background_resume_exercised': True,
            'notifications_before': before,
            'notifications_after': after,
            'app_originated_notification_observed': observed,
            'notification_tap_verified': False,
            'blockers': sorted(set(blockers)),
        }
        out.mkdir(parents=True, exist_ok=True)
        (out / 'notification-qa.json').write_text(json.dumps(payload, sort_keys=True, indent=2) + '\n')
        return payload
    finally:
        if owned_emulator and serial and shutil.which(adb):
            try:
                run_command([adb, '-s', serial, 'emu', 'kill'], timeout=20)
            except (OSError, subprocess.SubprocessError):
                pass
        if owned_emulator and emulator is not None:
            try:
                emulator.wait(timeout=20)
            except subprocess.TimeoutExpired:
                emulator.kill()

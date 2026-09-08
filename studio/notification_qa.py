"""Trusted Android QA for notification-capable Flutter apps."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

from core import StudioError
from device_qa import package_name, run_command, start_emulator, wait_for_boot

POST_NOTIFICATIONS = 'android.permission.POST_NOTIFICATIONS'
CRASH_PATTERNS = ('FATAL EXCEPTION', 'AndroidRuntime: FATAL', 'ANR in ', 'Unhandled Exception')
NOTIFICATION_DEPENDENCIES = ('firebase_messaging', 'flutter_local_notifications')
BOUNDS = re.compile(r'^\[(\d+),(\d+)\]\[(\d+),(\d+)\]$')


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
    return sum(1 for line in text.splitlines()
               if 'NotificationRecord' in line and re.search(r'\bpkg=' + re.escape(pkg) + r'(?:\s|$)', line))


def _apk_label(apk: Path) -> str | None:
    aapt = shutil.which('aapt')
    if not aapt:
        return None
    result = run_command([aapt, 'dump', 'badging', str(apk)], timeout=60)
    if result.returncode:
        return None
    match = re.search(r"application-label(?:-[^:]*)?:'([^']+)'", result.stdout)
    return match.group(1).strip() if match and match.group(1).strip() else None


def _tap_notification(adb: str, serial: str, label: str, pkg: str) -> dict:
    expand = run_command([adb, '-s', serial, 'shell', 'cmd', 'statusbar', 'expand-notifications'], timeout=30)
    if expand.returncode:
        return {'passed': False, 'blocker': 'notification_shade_expand_failed'}
    time.sleep(1)
    dump = run_command([adb, '-s', serial, 'shell', 'uiautomator', 'dump', '/sdcard/studio-notification.xml'], timeout=30)
    if dump.returncode:
        return {'passed': False, 'blocker': 'notification_ui_dump_failed'}
    xml = run_command([adb, '-s', serial, 'shell', 'cat', '/sdcard/studio-notification.xml'], timeout=30)
    if xml.returncode or not xml.stdout.strip():
        return {'passed': False, 'blocker': 'notification_ui_dump_unreadable'}
    try:
        root = ET.fromstring(xml.stdout[xml.stdout.find('<hierarchy'):])
    except (ET.ParseError, ValueError):
        return {'passed': False, 'blocker': 'notification_ui_dump_invalid'}

    parents = {child: parent for parent in root.iter() for child in parent}
    target = None
    for node in root.iter('node'):
        text = (node.attrib.get('text', '') + ' ' + node.attrib.get('content-desc', '')).strip()
        if label and label.lower() in text.lower():
            current = node
            while current is not None:
                if current.attrib.get('clickable') == 'true' and BOUNDS.match(current.attrib.get('bounds', '')):
                    target = current
                    break
                current = parents.get(current)
            if target is not None:
                break
    if target is None:
        return {'passed': False, 'blocker': 'notification_click_target_not_found', 'app_label': label}
    bounds = BOUNDS.match(target.attrib.get('bounds', ''))
    if bounds is None:
        return {'passed': False, 'blocker': 'notification_click_bounds_invalid'}
    x1, y1, x2, y2 = (int(value) for value in bounds.groups())
    tap = run_command([adb, '-s', serial, 'shell', 'input', 'tap', str((x1 + x2) // 2), str((y1 + y2) // 2)], timeout=30)
    time.sleep(2)
    focus = run_command([adb, '-s', serial, 'shell', 'dumpsys', 'window', 'windows'], timeout=60)
    foreground = focus.returncode == 0 and any(
        pkg in line for line in focus.stdout.splitlines()
        if 'mCurrentFocus' in line or 'mFocusedApp' in line
    )
    crashes = _crashes(adb, serial)
    return {
        'passed': tap.returncode == 0 and foreground and not crashes,
        'tap_exit': tap.returncode,
        'returned_to_app': foreground,
        'post_tap_crash_count': len(crashes),
        'app_label': label,
        'blocker': None if tap.returncode == 0 and foreground and not crashes else 'notification_tap_did_not_resume_stably',
    }


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
        if POST_NOTIFICATIONS in declared:
            for state, verb in (('denied', 'revoke'), ('granted', 'grant')):
                run_command([adb, '-s', serial, 'logcat', '-c'], timeout=30)
                command = run_command([adb, '-s', serial, 'shell', 'pm', verb, pkg, POST_NOTIFICATIONS], timeout=30)
                launch = _launch(adb, serial, pkg)
                time.sleep(2)
                run_command([adb, '-s', serial, 'shell', 'input', 'keyevent', '3'], timeout=30)
                time.sleep(1)
                resume = _launch(adb, serial, pkg)
                time.sleep(2)
                crash_lines = _crashes(adb, serial)
                states.append({'state': state, 'permission_exit': command.returncode,
                               'launch_exit': launch.returncode, 'resume_exit': resume.returncode,
                               'crash_count': len(crash_lines)})
                if command.returncode:
                    blockers.append('notification_permission_state_control_failed:' + state)
                if launch.returncode or resume.returncode or crash_lines:
                    blockers.append('notification_lifecycle_unstable:' + state)

        before = _count_package_notifications(_notification_dump(adb, serial), pkg)
        run_command([adb, '-s', serial, 'shell', 'monkey', '-p', pkg,
                     '--throttle', '100', '--pct-syskeys', '0', '80'], timeout=120)
        run_command([adb, '-s', serial, 'shell', 'input', 'keyevent', '3'], timeout=30)
        time.sleep(5)
        after = _count_package_notifications(_notification_dump(adb, serial), pkg)
        observed = after > before or after > 0
        if _crashes(adb, serial):
            blockers.append('notification_runtime_crash_or_anr_detected')
        if not observed:
            blockers.append('no_app_originated_notification_observed')

        tap_result = None
        if observed:
            label = _apk_label(apk)
            if not label:
                blockers.append('notification_app_label_unavailable')
            else:
                tap_result = _tap_notification(adb, serial, label, pkg)
                if not tap_result.get('passed'):
                    blockers.append(tap_result.get('blocker') or 'notification_tap_not_verified')
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
            'notification_tap_verified': bool(tap_result and tap_result.get('passed')),
            'notification_tap': tap_result,
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

"""Trusted Android QA for permission-driven/native-capability Flutter apps."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from core import StudioError
from device_qa import package_name, run_command, start_emulator, wait_for_boot

RUNTIME_PERMISSIONS = {
    'android.permission.CAMERA',
    'android.permission.ACCESS_FINE_LOCATION',
    'android.permission.ACCESS_COARSE_LOCATION',
    'android.permission.BLUETOOTH_CONNECT',
    'android.permission.BLUETOOTH_SCAN',
    'android.permission.RECORD_AUDIO',
}
CRASH_PATTERNS = ('FATAL EXCEPTION', 'AndroidRuntime: FATAL', 'ANR in ', 'Unhandled Exception')


def _serial(adb: str) -> str:
    explicit = os.environ.get('ANDROID_SERIAL')
    if explicit:
        return explicit
    devices = run_command([adb, 'devices'], timeout=30).stdout.splitlines()
    serials = [line.split()[0] for line in devices[1:] if '\tdevice' in line]
    if len(serials) != 1:
        raise StudioError('Native QA requires exactly one Android target')
    return serials[0]


def _declared_permissions(root: Path) -> list[str]:
    manifest = root / 'android/app/src/main/AndroidManifest.xml'
    if not manifest.is_file():
        return []
    import re
    text = manifest.read_text(errors='replace')
    return sorted(set(re.findall(r'<uses-permission[^>]+android:name=["\']([^"\']+)["\']', text)))


def _launch(adb: str, serial: str, pkg: str) -> subprocess.CompletedProcess:
    return run_command([adb, '-s', serial, 'shell', 'monkey', '-p', pkg, '-c',
                        'android.intent.category.LAUNCHER', '1'], timeout=60)


def _crashes(adb: str, serial: str) -> list[str]:
    result = run_command([adb, '-s', serial, 'logcat', '-d', '-v', 'brief'], timeout=60)
    return [line for line in result.stdout.splitlines()
            if any(pattern in line for pattern in CRASH_PATTERNS)]


def _exercise_permission(adb: str, serial: str, pkg: str, permission: str) -> dict:
    steps = []
    for state, command in (
        ('denied', [adb, '-s', serial, 'shell', 'pm', 'revoke', pkg, permission]),
        ('granted', [adb, '-s', serial, 'shell', 'pm', 'grant', pkg, permission]),
    ):
        run_command([adb, '-s', serial, 'logcat', '-c'], timeout=30)
        result = run_command(command, timeout=30)
        steps.append({'state': state, 'permission_command_exit': result.returncode,
                      'permission_command_output': result.stdout[-1000:]})
        if result.returncode:
            return {'passed': False, 'permission': permission, 'steps': steps,
                    'blocker': 'permission_state_control_failed'}
        run_command([adb, '-s', serial, 'shell', 'am', 'force-stop', pkg], timeout=30)
        launch = _launch(adb, serial, pkg)
        time.sleep(2)
        crash_lines = _crashes(adb, serial)
        steps[-1].update({'launch_exit': launch.returncode, 'crash_count': len(crash_lines)})
        if launch.returncode or crash_lines:
            return {'passed': False, 'permission': permission, 'steps': steps,
                    'blocker': 'app_unstable_for_' + state + '_permission_state'}
    return {'passed': True, 'permission': permission, 'steps': steps}


def validate_native(root: Path, out: Path, adb: str = 'adb') -> dict:
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

        declared = _declared_permissions(root)
        tested = [permission for permission in declared if permission in RUNTIME_PERMISSIONS]
        results = [_exercise_permission(adb, serial, pkg, permission) for permission in tested]
        blockers = [item['blocker'] + ':' + item['permission'] for item in results if not item['passed']]

        dependencies = (root / 'pubspec.yaml').read_text(errors='replace') if (root / 'pubspec.yaml').is_file() else ''
        biometric = 'local_auth:' in dependencies
        biometric_result = None
        if biometric:
            launch = _launch(adb, serial, pkg)
            finger = run_command([adb, '-s', serial, 'emu', 'finger', 'touch', '1'], timeout=30)
            biometric_result = {'launch_exit': launch.returncode, 'finger_command_exit': finger.returncode}
            if launch.returncode or finger.returncode:
                blockers.append('biometric_emulation_failed')

        if any(p in tested for p in ('android.permission.ACCESS_FINE_LOCATION', 'android.permission.ACCESS_COARSE_LOCATION')):
            geo = run_command([adb, '-s', serial, 'emu', 'geo', 'fix', '2.3522', '48.8566'], timeout=30)
            if geo.returncode:
                blockers.append('location_injection_failed')

        payload = {
            'passed': not blockers,
            'environment': 'android_emulator',
            'package': pkg,
            'declared_permissions': declared,
            'tested_permissions': tested,
            'permission_state_results': results,
            'biometric_emulated': biometric_result,
            'blockers': blockers,
        }
        out.mkdir(parents=True, exist_ok=True)
        (out / 'native-qa.json').write_text(json.dumps(payload, sort_keys=True, indent=2) + '\n')
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

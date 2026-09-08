"""Trusted Android emulator QA for validated release artifacts."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from core import StudioError, canonical

CRASH_PATTERNS = (
    'FATAL EXCEPTION',
    'AndroidRuntime: FATAL',
    'ANR in ',
    'Process: ',
)


def run_command(args: list[str], timeout: int = 120, check: bool = False) -> subprocess.CompletedProcess:
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, timeout=timeout)
    if check and result.returncode:
        raise StudioError('Device QA command failed: ' + ' '.join(args[:3]))
    return result


def wait_for_boot(adb: str = 'adb', timeout: int = 180) -> dict:
    start = time.monotonic()
    attempts = 0
    while time.monotonic() - start < timeout:
        attempts += 1
        state = run_command([adb, 'get-state'], timeout=15)
        if state.returncode == 0 and 'device' in state.stdout:
            boot = run_command([adb, 'shell', 'getprop', 'sys.boot_completed'], timeout=15)
            if boot.returncode == 0 and boot.stdout.strip() == '1':
                return {'passed': True, 'attempts': attempts}
        time.sleep(2)
    return {'passed': False, 'attempts': attempts}


def package_name(root: Path) -> str:
    manifest = root / 'android/app/src/main/AndroidManifest.xml'
    if not manifest.is_file():
        raise StudioError('Android manifest missing')
    text = manifest.read_text(errors='replace')
    match = re.search(r'package="([A-Za-z0-9_.]+)"', text)
    if match:
        return match.group(1)
    gradle = root / 'android/app/build.gradle.kts'
    if not gradle.is_file():
        gradle = root / 'android/app/build.gradle'
    if gradle.is_file():
        match = re.search(r'applicationId\s*[= ]\s*["\']([A-Za-z0-9_.]+)["\']', gradle.read_text(errors='replace'))
        if match:
            return match.group(1)
    raise StudioError('Unable to determine Android application id')


def validate_release_on_device(root: Path, out: Path, adb: str = 'adb') -> dict:
    """Install and launch the release APK on an already-running trusted emulator."""
    apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
    if not apk.is_file() or apk.stat().st_size < 1000:
        return {'passed': False, 'blockers': ['release_apk_missing'], 'logs': []}
    if shutil.which(adb) is None:
        return {'passed': False, 'blockers': ['adb_unavailable'], 'logs': []}

    boot = wait_for_boot(adb)
    if not boot['passed']:
        return {'passed': False, 'blockers': ['emulator_boot_timeout'], 'logs': [boot]}

    pkg = package_name(root)
    logs: list[dict] = []
    run_command([adb, 'logcat', '-c'], timeout=30)

    install = run_command([adb, 'install', '-r', '-t', str(apk)], timeout=180)
    logs.append({'command': ['adb', 'install'], 'exit_code': install.returncode,
                 'output': install.stdout[-4000:]})
    if install.returncode:
        return {'passed': False, 'blockers': ['release_install_failed'], 'logs': logs}

    launch = run_command([adb, 'shell', 'monkey', '-p', pkg, '-c',
                          'android.intent.category.LAUNCHER', '1'], timeout=60)
    logs.append({'command': ['adb', 'shell', 'monkey'], 'exit_code': launch.returncode,
                 'output': launch.stdout[-4000:]})
    if launch.returncode:
        return {'passed': False, 'blockers': ['release_launch_failed'], 'logs': logs}

    time.sleep(5)
    out.mkdir(parents=True, exist_ok=True)
    screenshot = out / 'device-release.png'
    with screenshot.open('wb') as handle:
        shot = subprocess.run([adb, 'exec-out', 'screencap', '-p'], stdout=handle,
                              stderr=subprocess.PIPE, timeout=60)
    if shot.returncode or not screenshot.is_file() or screenshot.stat().st_size < 1000:
        return {'passed': False, 'blockers': ['device_screenshot_failed'], 'logs': logs}

    logcat = run_command([adb, 'logcat', '-d', '-v', 'brief'], timeout=60)
    crash_lines = [line for line in logcat.stdout.splitlines()
                   if any(pattern in line for pattern in CRASH_PATTERNS)]
    logs.append({'command': ['adb', 'logcat', '-d'], 'exit_code': logcat.returncode,
                 'output': '\n'.join(crash_lines[-100:])})
    if crash_lines:
        return {'passed': False, 'blockers': ['runtime_crash_detected'], 'logs': logs}

    return {
        'passed': True,
        'package': pkg,
        'apk_sha256': hashlib.sha256(apk.read_bytes()).hexdigest(),
        'screenshot_sha256': hashlib.sha256(screenshot.read_bytes()).hexdigest(),
        'emulator_serial': os.environ.get('ANDROID_SERIAL', 'default'),
        'logs': logs,
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    result = validate_release_on_device(Path(args.work), Path(args.out))
    print(canonical(result))
    return 0 if result.get('passed') else 1


if __name__ == '__main__':
    raise SystemExit(main())

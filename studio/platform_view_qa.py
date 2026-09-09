"""Trusted runtime QA for Flutter platform views on Android release builds."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import time

from core import canonical
from device_qa import package_name, run_command, start_emulator, wait_for_boot

DEPENDENCIES = {
    'webview_flutter': ('android.webkit.WebView',),
    'video_player': ('android.view.SurfaceView', 'android.view.TextureView'),
    'google_maps_flutter': ('android.view.View', 'android.view.SurfaceView', 'android.view.TextureView'),
}
CRASH_PATTERNS = ('FATAL EXCEPTION', 'AndroidRuntime: FATAL', 'ANR in ', 'Unhandled Exception')


def _dependencies(root: Path) -> list[str]:
    path = root / 'pubspec.yaml'
    if not path.is_file():
        return []
    found: set[str] = set()
    for raw in path.read_text(errors='replace').splitlines():
        match = re.match(r'^\s{2}([A-Za-z0-9_]+):', raw)
        if match and match.group(1) in DEPENDENCIES:
            found.add(match.group(1))
    return sorted(found)


def _serial(adb: str) -> str | None:
    devices = run_command([adb, 'devices'], timeout=30).stdout.splitlines()
    serials = [line.split()[0] for line in devices[1:] if '\tdevice' in line]
    return serials[0] if len(serials) == 1 else None


def _ui_classes(xml: str) -> set[str]:
    return set(re.findall(r'class="([^"]+)"', xml))


def validate_platform_views(root: Path, out: Path, adb: str = 'adb') -> dict:
    apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
    deps = _dependencies(root)
    blockers: list[str] = []
    if not deps:
        blockers.append('platform_view_dependency_not_detected')
    if not apk.is_file() or apk.stat().st_size < 1000:
        blockers.append('release_apk_missing')
    if blockers:
        evidence = {'passed': False, 'dependencies': deps, 'blockers': blockers}
        out.mkdir(parents=True, exist_ok=True)
        (out / 'platform-view-qa.json').write_text(canonical(evidence))
        return evidence
    if shutil.which(adb) is None:
        evidence = {'passed': False, 'dependencies': deps, 'blockers': ['adb_unavailable']}
        out.mkdir(parents=True, exist_ok=True)
        (out / 'platform-view-qa.json').write_text(canonical(evidence))
        return evidence

    emulator = None
    owned = False
    serial = _serial(adb)
    try:
        if serial is None:
            emulator = start_emulator()
            owned = True
            boot = wait_for_boot(adb)
            if not boot.get('passed'):
                blockers.append('emulator_boot_timeout')
                return _write(out, deps, blockers)
            serial = _serial(adb)
        if not serial:
            blockers.append('ambiguous_android_target')
            return _write(out, deps, blockers)

        pkg = package_name(root)
        run_command([adb, '-s', serial, 'logcat', '-c'], timeout=30)
        install = run_command([adb, '-s', serial, 'install', '-r', '-t', str(apk)], timeout=180)
        if install.returncode:
            blockers.append('release_install_failed')
            return _write(out, deps, blockers, package=pkg, serial=serial)
        launch = run_command([adb, '-s', serial, 'shell', 'monkey', '-p', pkg, '-c', 'android.intent.category.LAUNCHER', '1'], timeout=60)
        if launch.returncode:
            blockers.append('release_launch_failed')
            return _write(out, deps, blockers, package=pkg, serial=serial)
        time.sleep(3)

        dump_cmd = [adb, '-s', serial, 'shell', 'uiautomator', 'dump', '/sdcard/window.xml']
        dumped = run_command(dump_cmd, timeout=60)
        xml = run_command([adb, '-s', serial, 'shell', 'cat', '/sdcard/window.xml'], timeout=30).stdout if dumped.returncode == 0 else ''
        classes = _ui_classes(xml)
        expected = sorted({c for dep in deps for c in DEPENDENCIES[dep]})
        observed = sorted(set(expected) & classes)
        if not observed:
            blockers.append('platform_view_not_observable_in_native_ui_tree')

        out.mkdir(parents=True, exist_ok=True)
        first = out / 'platform-view-foreground.png'
        with first.open('wb') as handle:
            shot = subprocess.run([adb, '-s', serial, 'exec-out', 'screencap', '-p'], stdout=handle, stderr=subprocess.PIPE, timeout=60)
        if shot.returncode or first.stat().st_size < 1000:
            blockers.append('platform_view_screenshot_failed')

        run_command([adb, '-s', serial, 'shell', 'input', 'keyevent', 'KEYCODE_HOME'], timeout=30)
        time.sleep(1)
        run_command([adb, '-s', serial, 'shell', 'monkey', '-p', pkg, '-c', 'android.intent.category.LAUNCHER', '1'], timeout=60)
        time.sleep(2)
        logcat = run_command([adb, '-s', serial, 'logcat', '-d', '-v', 'brief'], timeout=60)
        crash_lines = [line for line in logcat.stdout.splitlines() if any(p in line for p in CRASH_PATTERNS)]
        if crash_lines:
            blockers.append('platform_view_unstable_after_resume')

        evidence = {
            'passed': not blockers,
            'environment': 'android_emulator',
            'package': pkg,
            'device_serial': serial,
            'apk_sha256': hashlib.sha256(apk.read_bytes()).hexdigest(),
            'dependencies': deps,
            'expected_native_classes': expected,
            'observed_native_classes': observed,
            'foreground_render_evidence': first.name if first.is_file() else None,
            'background_resume_exercised': True,
            'crash_count': len(crash_lines),
            'blockers': blockers,
        }
        (out / 'platform-view-qa.json').write_text(canonical(evidence))
        return evidence
    finally:
        if owned and serial and shutil.which(adb):
            try:
                run_command([adb, '-s', serial, 'emu', 'kill'], timeout=20)
            except (OSError, subprocess.SubprocessError):
                pass
        if owned and emulator is not None:
            try:
                emulator.wait(timeout=20)
            except subprocess.TimeoutExpired:
                emulator.kill()


def _write(out: Path, deps: list[str], blockers: list[str], **extra) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    evidence = {'passed': False, 'dependencies': deps, 'blockers': blockers, **extra}
    (out / 'platform-view-qa.json').write_text(canonical(evidence))
    return evidence

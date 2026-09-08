"""Trusted Android performance QA for game/performance-sensitive Flutter apps."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from core import StudioError
from device_qa import package_name, run_command, start_emulator, wait_for_boot

FRAME_LIMIT_MS = float(os.environ.get('STUDIO_FRAME_LIMIT_MS', '16.7'))
JANK_RATIO_LIMIT = float(os.environ.get('STUDIO_JANK_RATIO_LIMIT', '0.15'))
MAX_FRAME_MS = float(os.environ.get('STUDIO_MAX_FRAME_MS', '80'))
SAMPLE_SECONDS = int(os.environ.get('STUDIO_PERF_SAMPLE_SECONDS', '20'))
CRASH_PATTERNS = ('FATAL EXCEPTION', 'AndroidRuntime: FATAL', 'ANR in ', 'Unhandled Exception')


def _serial(adb: str) -> str:
    explicit = os.environ.get('ANDROID_SERIAL')
    if explicit:
        return explicit
    devices = run_command([adb, 'devices'], timeout=30).stdout.splitlines()
    serials = [line.split()[0] for line in devices[1:] if '\tdevice' in line]
    if len(serials) != 1:
        raise StudioError('Performance QA requires exactly one Android target')
    return serials[0]


def _parse_gfxinfo(text: str) -> dict:
    frames = []
    in_profile = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('Draw') and 'Prepare' in stripped:
            in_profile = True
            continue
        if in_profile and not stripped:
            if frames:
                break
            continue
        if not in_profile:
            continue
        try:
            values = [float(value) for value in stripped.split(',')]
        except ValueError:
            continue
        if len(values) >= 4:
            frames.append(sum(values))
    if not frames:
        return {'frame_count': 0, 'janky_frames': None, 'jank_ratio': None,
                'p95_ms': None, 'max_ms': None}
    ordered = sorted(frames)
    p95 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    janky = sum(1 for value in frames if value > FRAME_LIMIT_MS)
    return {
        'frame_count': len(frames),
        'janky_frames': janky,
        'jank_ratio': round(janky / len(frames), 4),
        'p95_ms': round(p95, 3),
        'max_ms': round(max(frames), 3),
    }


def _exercise(adb: str, serial: str, pkg: str) -> list[dict]:
    actions = [
        [adb, '-s', serial, 'shell', 'input', 'tap', '540', '1200'],
        [adb, '-s', serial, 'shell', 'input', 'swipe', '540', '1500', '540', '500', '400'],
        [adb, '-s', serial, 'shell', 'input', 'keyevent', '3'],
        [adb, '-s', serial, 'shell', 'monkey', '-p', pkg, '-c', 'android.intent.category.LAUNCHER', '1'],
        [adb, '-s', serial, 'shell', 'input', 'keyevent', '26'],
        [adb, '-s', serial, 'shell', 'input', 'keyevent', '26'],
    ]
    logs = []
    for args in actions:
        result = run_command(args, timeout=30)
        logs.append({'command': args[4:] if len(args) > 4 else args,
                     'exit_code': result.returncode, 'output': result.stdout[-1000:]})
        time.sleep(1)
    return logs


def validate_performance(root: Path, out: Path, adb: str = 'adb') -> dict:
    apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
    if not apk.is_file() or apk.stat().st_size < 1000:
        return {'passed': False, 'blockers': ['release_apk_missing']}
    if shutil.which(adb) is None:
        return {'passed': False, 'blockers': ['adb_unavailable']}

    emulator = None
    owned_emulator = False
    serial = None
    logs = []
    try:
        if run_command([adb, 'get-state'], timeout=10).returncode != 0:
            emulator = start_emulator()
            owned_emulator = True
        boot = wait_for_boot(adb)
        if not boot.get('passed'):
            return {'passed': False, 'blockers': ['emulator_boot_timeout']}
        serial = _serial(adb)
        pkg = package_name(root)

        run_command([adb, '-s', serial, 'logcat', '-c'], timeout=30)
        install = run_command([adb, '-s', serial, 'install', '-r', '-t', str(apk)], timeout=180)
        if install.returncode:
            return {'passed': False, 'blockers': ['release_install_failed']}
        launch = run_command([adb, '-s', serial, 'shell', 'monkey', '-p', pkg, '-c',
                              'android.intent.category.LAUNCHER', '1'], timeout=60)
        if launch.returncode:
            return {'passed': False, 'blockers': ['release_launch_failed']}
        time.sleep(3)
        run_command([adb, '-s', serial, 'shell', 'dumpsys', 'gfxinfo', pkg, 'reset'], timeout=30)
        logs.extend(_exercise(adb, serial, pkg))

        monkey = run_command([adb, '-s', serial, 'shell', 'monkey', '-p', pkg,
                              '--throttle', '80', '--pct-syskeys', '0', '120'], timeout=120)
        logs.append({'command': ['monkey', '120'], 'exit_code': monkey.returncode,
                     'output': monkey.stdout[-2000:]})
        time.sleep(min(max(SAMPLE_SECONDS, 1), 30))

        gfx = run_command([adb, '-s', serial, 'shell', 'dumpsys', 'gfxinfo', pkg], timeout=60)
        metrics = _parse_gfxinfo(gfx.stdout)
        logcat = run_command([adb, '-s', serial, 'logcat', '-d', '-v', 'brief'], timeout=60)
        crashes = [line for line in logcat.stdout.splitlines()
                   if any(pattern in line for pattern in CRASH_PATTERNS)]

        blockers = []
        if monkey.returncode:
            blockers.append('interaction_stress_failed')
        if crashes:
            blockers.append('runtime_crash_or_anr_detected')
        if metrics['frame_count'] < 30:
            blockers.append('insufficient_frame_samples')
        elif metrics['jank_ratio'] is not None and metrics['jank_ratio'] > JANK_RATIO_LIMIT:
            blockers.append('excessive_jank')
        if metrics['max_ms'] is not None and metrics['max_ms'] > MAX_FRAME_MS:
            blockers.append('severe_frame_stall')

        out.mkdir(parents=True, exist_ok=True)
        payload = {
            'passed': not blockers,
            'environment': 'android_emulator',
            'package': pkg,
            'thresholds': {'target_frame_ms': FRAME_LIMIT_MS,
                           'max_jank_ratio': JANK_RATIO_LIMIT,
                           'max_frame_ms': MAX_FRAME_MS},
            'metrics': metrics,
            'pause_resume_exercised': True,
            'stress_events': 120,
            'crash_count': len(crashes),
            'blockers': blockers,
            'logs': logs,
        }
        (out / 'performance-qa.json').write_text(json.dumps(payload, sort_keys=True, indent=2) + '\n')
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

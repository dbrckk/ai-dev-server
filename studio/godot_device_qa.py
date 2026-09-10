"""Trusted Android-emulator smoke QA for a hashed Godot debug APK.

The APK must match the Android-export evidence before installation. The untrusted app
runs only inside an emulator; CI credentials are not forwarded to Android tooling.
This gate proves install/launch/no-crash/screenshot only. It never claims scripted
journeys or visual acceptance review.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from core import StudioError

SYSTEM_IMAGE = 'system-images;android-35;google_apis;x86_64'
AVD_NAME = 'studio-godot-qa'
CRASH_PATTERNS = ('FATAL EXCEPTION', 'AndroidRuntime: FATAL', 'ANR in ')
PACKAGE_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+$')


def _safe_env() -> dict[str, str]:
    allowed = ('PATH','HOME','ANDROID_HOME','ANDROID_SDK_ROOT','JAVA_HOME','TMPDIR')
    return {key: os.environ[key] for key in allowed if key in os.environ}


def _run(args: list[str], timeout: int = 120, input_text: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, input=input_text, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, timeout=timeout, env=_safe_env())


def package_name(root: Path) -> str:
    preset = root / 'export_presets.cfg'
    if not preset.is_file() or preset.is_symlink():
        raise StudioError('Godot export preset is missing')
    text = preset.read_text(errors='replace')
    values = re.findall(r'(?m)^package/unique_name="([^"]+)"$', text)
    if len(values) != 1 or not PACKAGE_RE.fullmatch(values[0]):
        raise StudioError('Godot Android package id is invalid or ambiguous')
    return values[0]


def _start_emulator() -> subprocess.Popen:
    required = ('sdkmanager','avdmanager','emulator','adb')
    missing = [name for name in required if shutil.which(name) is None]
    if missing:
        raise StudioError('Android emulator tooling unavailable: ' + ','.join(missing))
    installed = _run(['sdkmanager', SYSTEM_IMAGE], timeout=900)
    if installed.returncode:
        raise StudioError('Android system image installation failed')
    avd_dir = Path.home()/'.android/avd'/(AVD_NAME + '.avd')
    if not avd_dir.exists():
        created = _run(['avdmanager','create','avd','-n',AVD_NAME,'-k',SYSTEM_IMAGE,'--force'],
                       timeout=120,input_text='no\n')
        if created.returncode:
            raise StudioError('Android AVD creation failed')
    return subprocess.Popen(['emulator','-avd',AVD_NAME,'-no-window','-no-audio','-no-snapshot',
                             '-no-boot-anim','-gpu','swiftshader_indirect','-no-metrics'],
                            stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT,start_new_session=True,
                            env=_safe_env())


def _wait_for_boot(adb: str, timeout: int = 240) -> tuple[bool, str | None]:
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        devices = _run([adb,'devices'],timeout=15)
        serials = [line.split()[0] for line in devices.stdout.splitlines()[1:]
                   if '\tdevice' in line and line.split()[0].startswith('emulator-')]
        if len(serials) == 1:
            serial = serials[0]
            boot = _run([adb,'-s',serial,'shell','getprop','sys.boot_completed'],timeout=15)
            if boot.returncode == 0 and boot.stdout.strip() == '1':
                return True, serial
        time.sleep(2)
    return False, None


def validate_debug_apk(root: Path, apk: Path, expected_sha256: str, out: Path,
                       adb: str = 'adb', sleeper=time.sleep) -> dict:
    root = root.resolve(); apk = apk.resolve(); out = out.resolve()
    if not re.fullmatch(r'[0-9a-f]{64}', expected_sha256 or ''):
        raise StudioError('Godot device QA requires trusted APK SHA-256 evidence')
    if not apk.is_file() or apk.is_symlink() or apk.stat().st_size < 1000:
        return {'passed':False,'blockers':['debug_apk_missing'],'journeys_executed':False}
    actual = hashlib.sha256(apk.read_bytes()).hexdigest()
    if actual != expected_sha256:
        raise StudioError('Godot device QA APK hash does not match export evidence')
    if shutil.which(adb) is None:
        return {'passed':False,'blockers':['adb_unavailable'],'journeys_executed':False}
    pkg = package_name(root)
    emulator = None; serial = None
    try:
        existing = _run([adb,'devices'],timeout=20)
        serials = [line.split()[0] for line in existing.stdout.splitlines()[1:]
                   if '\tdevice' in line and line.split()[0].startswith('emulator-')]
        if len(serials) > 1:
            return {'passed':False,'blockers':['ambiguous_android_target'],'journeys_executed':False}
        if serials:
            serial = serials[0]
        else:
            emulator = _start_emulator()
            booted, serial = _wait_for_boot(adb)
            if not booted or not serial:
                return {'passed':False,'blockers':['emulator_boot_timeout'],'journeys_executed':False}
        logs = []
        _run([adb,'-s',serial,'logcat','-c'],timeout=30)
        # Keep the application offline during untrusted runtime smoke.
        _run([adb,'-s',serial,'shell','settings','put','global','airplane_mode_on','1'],timeout=30)
        _run([adb,'-s',serial,'shell','am','broadcast','-a','android.intent.action.AIRPLANE_MODE','--ez','state','true'],timeout=30)
        airplane = _run([adb,'-s',serial,'shell','settings','get','global','airplane_mode_on'],timeout=30)
        if airplane.returncode or airplane.stdout.strip() != '1':
            return {'passed':False,'blockers':['airplane_mode_unverified'],'journeys_executed':False}
        install = _run([adb,'-s',serial,'install','-r','-t',str(apk)],timeout=180)
        logs.append({'command':['adb','install'],'exit_code':install.returncode,'output':install.stdout[-4000:]})
        if install.returncode:
            return {'passed':False,'blockers':['debug_install_failed'],'logs':logs,'journeys_executed':False}
        launch = _run([adb,'-s',serial,'shell','monkey','-p',pkg,'-c','android.intent.category.LAUNCHER','1'],timeout=60)
        logs.append({'command':['adb','shell','monkey'],'exit_code':launch.returncode,'output':launch.stdout[-4000:]})
        if launch.returncode:
            return {'passed':False,'blockers':['debug_launch_failed'],'logs':logs,'journeys_executed':False}
        sleeper(5)
        out.mkdir(parents=True,exist_ok=True)
        screenshot = out/'godot-device.png'
        with screenshot.open('wb') as handle:
            shot = subprocess.run([adb,'-s',serial,'exec-out','screencap','-p'],stdout=handle,
                                  stderr=subprocess.PIPE,timeout=60,env=_safe_env())
        if shot.returncode or not screenshot.is_file() or screenshot.stat().st_size < 1000:
            return {'passed':False,'blockers':['device_screenshot_failed'],'logs':logs,'journeys_executed':False}
        logcat = _run([adb,'-s',serial,'logcat','-d','-v','brief'],timeout=60)
        crashes = [line for line in logcat.stdout.splitlines() if any(marker in line for marker in CRASH_PATTERNS)]
        logs.append({'command':['adb','logcat','-d'],'exit_code':logcat.returncode,'output':'\n'.join(crashes[-100:])})
        if crashes:
            return {'passed':False,'blockers':['runtime_crash_detected'],'logs':logs,'journeys_executed':False}
        return {'passed':True,'environment':'android_emulator','package':pkg,'apk_sha256':actual,
                'screenshot_sha256':hashlib.sha256(screenshot.read_bytes()).hexdigest(),
                'network':'airplane_mode','release_signed':False,'journeys_executed':False,
                'visual_reviewed':False,'logs':logs}
    finally:
        if emulator is not None and serial and shutil.which(adb):
            try: _run([adb,'-s',serial,'emu','kill'],timeout=20)
            except (OSError,subprocess.SubprocessError): pass
        if emulator is not None:
            try: emulator.wait(timeout=20)
            except subprocess.TimeoutExpired: emulator.kill()

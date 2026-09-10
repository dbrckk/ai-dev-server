"""Trusted Godot Android export gate.

Downloads the official Godot 4.7.2 export-template archive without credentials,
verifies its release SHA-256, extracts only the Android templates, and exports an
unsigned/debug APK from an ephemeral project copy. Source repositories are never
mounted into the container and no CI credentials are forwarded.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile

from core import IMAGE, StudioError
from godot_runtime import GODOT_VERSION, _copy_project, _host_env, _trusted_binary_hash

TEMPLATE_ASSET = 'Godot_v4.7.2-stable_export_templates.tpz'
TEMPLATE_URL = 'https://github.com/godotengine/godot/releases/download/4.7.2-stable/' + TEMPLATE_ASSET
TEMPLATE_SHA256 = 'f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011'
MAX_TEMPLATE_ARCHIVE_BYTES = 1_350_000_000
MAX_TEMPLATE_MEMBER_BYTES = 180_000_000
ANDROID_TEMPLATE_MEMBERS = {
    'templates/android_debug.apk': 'android_debug.apk',
    'templates/android_release.apk': 'android_release.apk',
}
EXPORT_ERROR_MARKERS = ('ERROR:', 'SCRIPT ERROR', 'Parse Error', 'Failed loading resource', 'Export failed')


def _archive_ok(path: Path) -> bool:
    return path.is_file() and path.stat().st_size <= MAX_TEMPLATE_ARCHIVE_BYTES and hashlib.sha256(path.read_bytes()).hexdigest() == TEMPLATE_SHA256


def _safe_member(info: zipfile.ZipInfo) -> bool:
    path = PurePosixPath(info.filename)
    return (not path.is_absolute() and '..' not in path.parts and '\\' not in info.filename
            and info.filename in ANDROID_TEMPLATE_MEMBERS and not info.is_dir()
            and info.file_size <= MAX_TEMPLATE_MEMBER_BYTES)


def install_android_templates(cache_dir: Path, opener=urllib.request.urlopen) -> Path:
    cache_dir = cache_dir.resolve(); cache_dir.mkdir(parents=True, exist_ok=True)
    archive = cache_dir / TEMPLATE_ASSET
    partial = cache_dir / (TEMPLATE_ASSET + '.part')
    target = cache_dir / 'android-templates'
    partial.unlink(missing_ok=True)
    try:
        if not _archive_ok(archive):
            archive.unlink(missing_ok=True)
            request = urllib.request.Request(TEMPLATE_URL, headers={'User-Agent':'ai-dev-server-godot-android-export'})
            with opener(request, timeout=90) as response, partial.open('wb') as out:
                total = 0; digest = hashlib.sha256()
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk: break
                    total += len(chunk)
                    if total > MAX_TEMPLATE_ARCHIVE_BYTES: raise StudioError('Godot template archive exceeded trusted size limit')
                    digest.update(chunk); out.write(chunk)
            if digest.hexdigest() != TEMPLATE_SHA256: raise StudioError('Godot template archive SHA-256 mismatch')
            partial.replace(archive)
        if not _archive_ok(archive): raise StudioError('Godot cached template archive is not trusted')
        staged = cache_dir / 'android-templates.new'
        shutil.rmtree(staged, ignore_errors=True); staged.mkdir()
        found = set()
        with zipfile.ZipFile(archive) as zf:
            infos = {i.filename:i for i in zf.infolist() if i.filename in ANDROID_TEMPLATE_MEMBERS}
            if set(infos) != set(ANDROID_TEMPLATE_MEMBERS) or any(not _safe_member(i) for i in infos.values()):
                raise StudioError('Godot Android template layout rejected')
            for member, output_name in ANDROID_TEMPLATE_MEMBERS.items():
                with zf.open(infos[member]) as src, (staged/output_name).open('wb') as dst: shutil.copyfileobj(src, dst)
                found.add(output_name)
        if found != set(ANDROID_TEMPLATE_MEMBERS.values()) or not _archive_ok(archive):
            raise StudioError('Godot Android templates failed integrity verification')
        shutil.rmtree(target, ignore_errors=True); staged.replace(target)
        return target
    finally:
        partial.unlink(missing_ok=True)


def _preset_name(export_presets: str) -> str:
    if not isinstance(export_presets, str) or len(export_presets) > 200_000:
        raise StudioError('Godot export presets are invalid')
    names = re.findall(r'(?m)^name="([^"]+)"$', export_presets)
    platforms = re.findall(r'(?m)^platform="([^"]+)"$', export_presets)
    if len(names) != len(platforms): raise StudioError('Godot export preset structure is invalid')
    android = [name for name, platform in zip(names, platforms) if platform == 'Android']
    if len(android) != 1: raise StudioError('Exactly one Android export preset is required')
    return android[0]


def export_debug_apk(project_root: Path, binary: Path, templates: Path, runner=subprocess.run, timeout=900, artifact_path: Path | None=None) -> dict:
    source = project_root.resolve(); binary = binary.resolve(); templates = templates.resolve()
    binary_hash = _trusted_binary_hash(binary)
    preset_path = source/'export_presets.cfg'
    if not preset_path.is_file() or preset_path.is_symlink(): raise StudioError('Godot Android export preset is missing')
    preset = _preset_name(preset_path.read_text())
    for name in ('android_debug.apk','android_release.apk'):
        p = templates/name
        if not p.is_file() or p.is_symlink() or p.stat().st_size > MAX_TEMPLATE_MEMBER_BYTES:
            raise StudioError('Godot Android export template is invalid')
    with tempfile.TemporaryDirectory(prefix='studio-godot-android-') as tmp:
        root = Path(tmp); project = root/'project'; home = root/'home'; output = root/'out'
        project.mkdir(); home.mkdir(); output.mkdir(); _copy_project(source, project)
        version_dir = home/'.local/share/godot/export_templates'/GODOT_VERSION.replace('-stable','.stable')
        version_dir.mkdir(parents=True)
        for name in ('android_debug.apk','android_release.apk'): shutil.copyfile(templates/name, version_dir/name)
        apk = output/'app-debug.apk'
        command = ['docker','run','--rm','--init','--cap-drop=ALL','--security-opt=no-new-privileges','--pids-limit=256','--memory=4g','--cpus=2','--network=none',
                   '--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=512m','-v',str(project)+':/project:rw','-v',str(home)+':/home/studio:rw',
                   '-v',str(output)+':/out:rw','-v',str(binary)+':/opt/godot:ro','-e','HOME=/home/studio','-w','/project',IMAGE,
                   '/opt/godot','--headless','--path','/project','--export-debug',preset,'/out/app-debug.apk']
        try: result = runner(command, env=_host_env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        except subprocess.TimeoutExpired: raise StudioError('Godot Android export timed out') from None
        text = result.stdout.decode(errors='replace')[-32000:] if isinstance(result.stdout,bytes) else str(result.stdout or '')[-32000:]
        passed = result.returncode == 0 and apk.is_file() and apk.stat().st_size > 0 and not any(m in text for m in EXPORT_ERROR_MARKERS)
        apk_hash = hashlib.sha256(apk.read_bytes()).hexdigest() if passed else None
        preserved = None
        if passed and artifact_path is not None:
            target = artifact_path.resolve(); target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(apk, target)
            if hashlib.sha256(target.read_bytes()).hexdigest() != apk_hash:
                target.unlink(missing_ok=True)
                raise StudioError('Preserved Godot APK hash mismatch')
            preserved = str(target)
        return {'passed':passed,'exit_code':result.returncode,'output':text,'preset':preset,'apk_sha256':apk_hash,
                'apk_artifact':preserved,'engine_version':GODOT_VERSION,'binary_sha256':binary_hash,'templates_sha256':TEMPLATE_SHA256,
                'network':'none','source_project':'not_mounted','release_signed':False}

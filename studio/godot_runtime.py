"""Pinned, credential-free Godot validation runtime.

Godot executes project scripts during import, so untrusted project code never runs on
the privileged CI host. The trusted host downloads the official editor asset without
credentials, verifies its release SHA-256, then executes it inside the already-pinned
studio container with networking disabled and the project mounted read-only.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile

from core import IMAGE, StudioError

GODOT_VERSION = '4.7.2-stable'
GODOT_ASSET = 'Godot_v4.7.2-stable_linux.x86_64.zip'
GODOT_BINARY = 'Godot_v4.7.2-stable_linux.x86_64'
GODOT_URL = 'https://github.com/godotengine/godot/releases/download/4.7.2-stable/' + GODOT_ASSET
GODOT_SHA256 = 'cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4'
MAX_ARCHIVE_BYTES = 90_000_000
MAX_BINARY_BYTES = 160_000_000
BLOCKING_MARKERS = ('SCRIPT ERROR', 'Parse Error', 'Cannot parse', 'Failed loading resource')


def _host_env():
    return {key: os.environ[key] for key in ('PATH', 'HOME') if key in os.environ}


def _safe_member(info: zipfile.ZipInfo) -> bool:
    path = PurePosixPath(info.filename)
    return (not path.is_absolute() and '..' not in path.parts and '\\' not in info.filename
            and info.filename == GODOT_BINARY and not info.is_dir())


def install(cache_dir: Path, opener=urllib.request.urlopen) -> Path:
    cache_dir = cache_dir.resolve(); cache_dir.mkdir(parents=True, exist_ok=True)
    binary = cache_dir / GODOT_BINARY
    digest_file = cache_dir / (GODOT_BINARY + '.sha256')
    if binary.is_file() and digest_file.is_file() and digest_file.read_text().strip() == GODOT_SHA256:
        if hashlib.sha256(binary.read_bytes()).hexdigest() == GODOT_SHA256:
            binary.chmod(0o755); return binary
        binary.unlink(missing_ok=True); digest_file.unlink(missing_ok=True)
    archive = cache_dir / GODOT_ASSET
    tmp = cache_dir / (GODOT_ASSET + '.part')
    tmp.unlink(missing_ok=True)
    try:
        request = urllib.request.Request(GODOT_URL, headers={'User-Agent': 'ai-dev-server-godot-runtime'})
        with opener(request, timeout=60) as response, tmp.open('wb') as out:
            total = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk: break
                total += len(chunk)
                if total > MAX_ARCHIVE_BYTES: raise StudioError('Godot archive exceeded trusted size limit')
                out.write(chunk)
        if hashlib.sha256(tmp.read_bytes()).hexdigest() != GODOT_SHA256:
            raise StudioError('Godot release archive SHA-256 mismatch')
        tmp.replace(archive)
        with zipfile.ZipFile(archive) as zf:
            members = zf.infolist()
            if len(members) != 1 or not _safe_member(members[0]) or members[0].file_size > MAX_BINARY_BYTES:
                raise StudioError('Godot release archive layout rejected')
            extracted = cache_dir / (GODOT_BINARY + '.new')
            extracted.unlink(missing_ok=True)
            with zf.open(members[0]) as src, extracted.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            extracted.replace(binary)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != GODOT_SHA256:
            raise StudioError('Godot verified archive changed during extraction')
        binary.chmod(0o755); digest_file.write_text(GODOT_SHA256 + '\n')
        archive.unlink(missing_ok=True)
        return binary
    finally:
        tmp.unlink(missing_ok=True)


def docker_command(project_root: Path, binary: Path, cache: Path) -> list[str]:
    project_root = project_root.resolve(); binary = binary.resolve(); cache = cache.resolve()
    if not project_root.is_dir() or not (project_root / 'project.godot').is_file():
        raise StudioError('Godot project root is invalid')
    if not binary.is_file() or hashlib.sha256(binary.read_bytes()).hexdigest() != GODOT_SHA256:
        raise StudioError('Godot binary is not trusted')
    cache.mkdir(parents=True, exist_ok=True)
    return ['docker','run','--rm','--init','--cap-drop=ALL','--security-opt=no-new-privileges',
            '--pids-limit=256','--memory=3g','--cpus=2','--network=none',
            '--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=256m',
            '-v',str(project_root)+':/project:ro',
            '-v',str(cache)+':/project/.godot:rw',
            '-v',str(binary)+':/opt/godot:ro',
            '-w','/project',IMAGE,'/opt/godot','--headless','--path','/project','--editor','--quit']


def validate(project_root: Path, binary: Path, runner=subprocess.run, timeout=600) -> dict:
    with tempfile.TemporaryDirectory(prefix='studio-godot-cache-') as tmp:
        command = docker_command(project_root, binary, Path(tmp))
        try:
            result = runner(command, env=_host_env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise StudioError('Godot validation timed out') from None
        output = result.stdout.decode(errors='replace')[-24000:] if isinstance(result.stdout, bytes) else str(result.stdout or '')[-24000:]
        blocked = result.returncode != 0 or any(marker in output for marker in BLOCKING_MARKERS)
        return {'passed': not blocked, 'exit_code': result.returncode, 'output': output,
                'network': 'none', 'project_mount': 'read_only', 'binary_sha256': GODOT_SHA256,
                'engine_version': GODOT_VERSION}

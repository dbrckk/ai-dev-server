"""Pinned, credential-free Godot validation runtime.

Godot executes project scripts during import, so untrusted project code never runs on
the privileged CI host. The trusted host downloads the official editor asset without
credentials, verifies its release SHA-256, then executes it inside the digest-pinned
studio container with networking disabled. The source project is never mounted into
the container: a bounded, symlink-free temporary copy is used instead.
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

GODOT_VERSION = '4.7.2-stable'
GODOT_ASSET = 'Godot_v4.7.2-stable_linux.x86_64.zip'
GODOT_BINARY = 'Godot_v4.7.2-stable_linux.x86_64'
GODOT_URL = 'https://github.com/godotengine/godot/releases/download/4.7.2-stable/' + GODOT_ASSET
GODOT_ARCHIVE_SHA256 = 'cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4'
MAX_ARCHIVE_BYTES = 90_000_000
MAX_BINARY_BYTES = 160_000_000
MAX_PROJECT_ENTRIES = 4000
MAX_PROJECT_BYTES = 160_000_000
BLOCKING_MARKERS = ('SCRIPT ERROR', 'Parse Error', 'Cannot parse', 'Failed loading resource')


def _host_env():
    return {key: os.environ[key] for key in ('PATH', 'HOME') if key in os.environ}


def _safe_member(info: zipfile.ZipInfo) -> bool:
    path = PurePosixPath(info.filename)
    return (not path.is_absolute() and '..' not in path.parts and '\\' not in info.filename
            and info.filename == GODOT_BINARY and not info.is_dir())


def _archive_ok(path: Path) -> bool:
    return path.is_file() and path.stat().st_size <= MAX_ARCHIVE_BYTES and hashlib.sha256(path.read_bytes()).hexdigest() == GODOT_ARCHIVE_SHA256


def install(cache_dir: Path, opener=urllib.request.urlopen) -> Path:
    cache_dir = cache_dir.resolve(); cache_dir.mkdir(parents=True, exist_ok=True)
    archive = cache_dir / GODOT_ASSET
    binary = cache_dir / GODOT_BINARY
    binary_digest = cache_dir / (GODOT_BINARY + '.sha256')
    tmp = cache_dir / (GODOT_ASSET + '.part')
    tmp.unlink(missing_ok=True)
    try:
        if not _archive_ok(archive):
            archive.unlink(missing_ok=True)
            request = urllib.request.Request(GODOT_URL, headers={'User-Agent': 'ai-dev-server-godot-runtime'})
            with opener(request, timeout=60) as response, tmp.open('wb') as out:
                total = 0
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk: break
                    total += len(chunk)
                    if total > MAX_ARCHIVE_BYTES: raise StudioError('Godot archive exceeded trusted size limit')
                    out.write(chunk)
            if hashlib.sha256(tmp.read_bytes()).hexdigest() != GODOT_ARCHIVE_SHA256:
                raise StudioError('Godot release archive SHA-256 mismatch')
            tmp.replace(archive)
        if not _archive_ok(archive):
            raise StudioError('Godot cached archive is not trusted')
        with zipfile.ZipFile(archive) as zf:
            members = zf.infolist()
            if len(members) != 1 or not _safe_member(members[0]) or members[0].file_size > MAX_BINARY_BYTES:
                raise StudioError('Godot release archive layout rejected')
            extracted = cache_dir / (GODOT_BINARY + '.new')
            extracted.unlink(missing_ok=True)
            with zf.open(members[0]) as src, extracted.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            extracted.replace(binary)
        if not _archive_ok(archive):
            raise StudioError('Godot verified archive changed during extraction')
        binary_hash = hashlib.sha256(binary.read_bytes()).hexdigest()
        binary.chmod(0o755); binary_digest.write_text(binary_hash + '\n')
        return binary
    finally:
        tmp.unlink(missing_ok=True)


def _trusted_binary_hash(binary: Path) -> str:
    digest_file = binary.with_name(binary.name + '.sha256')
    if not binary.is_file() or binary.is_symlink() or not digest_file.is_file() or digest_file.is_symlink():
        raise StudioError('Godot binary is not trusted')
    expected = digest_file.read_text().strip()
    if not re.fullmatch(r'[0-9a-f]{64}', expected):
        raise StudioError('Godot binary digest evidence is invalid')
    actual = hashlib.sha256(binary.read_bytes()).hexdigest()
    if actual != expected:
        raise StudioError('Godot binary changed after verified extraction')
    return actual


def _copy_project(source: Path, destination: Path) -> None:
    source = source.resolve(); destination = destination.resolve()
    if not source.is_dir() or not (source / 'project.godot').is_file():
        raise StudioError('Godot project root is invalid')
    entries = 0; total = 0
    for path in sorted(source.rglob('*')):
        entries += 1
        if entries > MAX_PROJECT_ENTRIES:
            raise StudioError('Godot project exceeds trusted entry limit')
        if path.is_symlink():
            raise StudioError('Godot project symlink rejected')
        rel = path.relative_to(source)
        target = destination / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if not path.is_file():
            raise StudioError('Godot project contains unsupported filesystem entry')
        size = path.stat().st_size; total += size
        if total > MAX_PROJECT_BYTES:
            raise StudioError('Godot project exceeds trusted byte limit')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def docker_command(sandbox_project: Path, binary: Path) -> list[str]:
    sandbox_project = sandbox_project.resolve(); binary = binary.resolve()
    if not sandbox_project.is_dir() or not (sandbox_project / 'project.godot').is_file():
        raise StudioError('Godot sandbox project is invalid')
    _trusted_binary_hash(binary)
    return ['docker','run','--rm','--init','--cap-drop=ALL','--security-opt=no-new-privileges',
            '--pids-limit=256','--memory=3g','--cpus=2','--network=none',
            '--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=256m',
            '-v',str(sandbox_project)+':/project:rw',
            '-v',str(binary)+':/opt/godot:ro',
            '-w','/project',IMAGE,'/opt/godot','--headless','--path','/project','--editor','--quit']


def validate(project_root: Path, binary: Path, runner=subprocess.run, timeout=600) -> dict:
    source = project_root.resolve(); binary = binary.resolve()
    binary_hash = _trusted_binary_hash(binary)
    with tempfile.TemporaryDirectory(prefix='studio-godot-project-') as tmp:
        sandbox_project = Path(tmp) / 'project'
        sandbox_project.mkdir()
        _copy_project(source, sandbox_project)
        command = docker_command(sandbox_project, binary)
        try:
            result = runner(command, env=_host_env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise StudioError('Godot validation timed out') from None
        output = result.stdout.decode(errors='replace')[-24000:] if isinstance(result.stdout, bytes) else str(result.stdout or '')[-24000:]
        blocked = result.returncode != 0 or any(marker in output for marker in BLOCKING_MARKERS)
        return {'passed': not blocked, 'exit_code': result.returncode, 'output': output,
                'network': 'none', 'source_project': 'not_mounted', 'sandbox_project': 'ephemeral_writable',
                'binary_sha256': binary_hash, 'archive_sha256': GODOT_ARCHIVE_SHA256,
                'engine_version': GODOT_VERSION}

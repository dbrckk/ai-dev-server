"""Read-only, pinned Jumpy baseline. No model calls or repository writes."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile

from core import StudioError, canonical

def config_check(c):
    fields = {'repository', 'baseline_commit', 'engine', 'engine_version', 'engine_sha256', 'mode'}
    if not isinstance(c, dict) or set(c) != fields:
        raise StudioError('Invalid existing-project manifest')
    if (c['repository'] != 'dbrckk/Jumpy' or c['engine'] != 'godot' or
        c['engine_version'] != '4.7.2' or c['mode'] != 'baseline_only'):
        raise StudioError('Only the reviewed Jumpy baseline is supported')
    for key, size in [('baseline_commit', 40), ('engine_sha256', 64)]:
        if not isinstance(c[key], str) or not re.fullmatch('[0-9a-f]{%d}' % size, c[key]):
            raise StudioError('Invalid immutable baseline identifier')
    return c

def verify_archive(data, digest):
    if hashlib.sha256(data).hexdigest() != digest:
        raise StudioError('Godot archive checksum mismatch')

def gate_ok(code, log, marker=None):
    return code == 0 and not re.search(
        r'SCRIPT ERROR|Parse Error|Cannot parse|Failed loading resource|ERROR:', log
    ) and (marker is None or marker in log)

def main():
    out = Path('studio-output/jumpy-baseline').resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = {'status': 'blocked', 'mode': 'baseline_only',
              'coverage': 'Headless import and eight gameplay invariants; no screenshots, APK or device test.',
              'repository_modified': False}
    try:
        c = config_check(json.loads(Path('control/existing-projects/jumpy.json').read_text()))
        report.update(repository=c['repository'], baseline_commit=c['baseline_commit'], engine_version=c['engine_version'])
        with tempfile.TemporaryDirectory(prefix='jumpy-baseline-') as tmp:
            root = Path(tmp)
            home = root / 'home'
            home.mkdir()
            # No inherited API keys, checkout SSH key, Git config, profile or user saves.
            env = {'PATH': os.environ['PATH'], 'HOME': str(home), 'XDG_DATA_HOME': str(home / 'data'),
                   'XDG_CONFIG_HOME': str(home / 'config'), 'LANG': 'C.UTF-8',
                   'GIT_TERMINAL_PROMPT': '0'}
            project = root / 'project'
            def run(args, timeout=180):
                p = subprocess.run(args, env=env, cwd=root, timeout=timeout,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                return p.returncode, p.stdout.decode(errors='replace')
            for args in [
                ['git', 'init', str(project)],
                ['git', '-C', str(project), 'remote', 'add', 'origin', 'https://github.com/dbrckk/Jumpy.git'],
                ['git', '-C', str(project), 'fetch', '--depth=1', 'origin', c['baseline_commit']],
                ['git', '-C', str(project), 'checkout', '--detach', 'FETCH_HEAD']]:
                code, log = run(args)
                if code:
                    raise StudioError('Pinned source checkout failed')
            code, head = run(['git', '-C', str(project), 'rev-parse', 'HEAD'])
            if code or head.strip() != c['baseline_commit']:
                raise StudioError('Unexpected baseline revision')
            shutil.rmtree(project / '.git')
            version = c['engine_version']
            name = f'Godot_v{version}-stable_linux.x86_64'
            url = f'https://github.com/godotengine/godot/releases/download/{version}-stable/{name}.zip'
            with urllib.request.urlopen(url, timeout=180) as response:
                data = response.read(200_000_001)
            if len(data) > 200_000_000:
                raise StudioError('Godot download exceeds size limit')
            verify_archive(data, c['engine_sha256'])
            archive = root / 'godot.zip'
            archive.write_bytes(data)
            with zipfile.ZipFile(archive) as z:
                info = z.getinfo(name)
                if info.file_size > 250_000_000:
                    raise StudioError('Godot binary exceeds size limit')
                binary = root / 'godot'
                binary.write_bytes(z.read(name))
            binary.chmod(0o700)
            for label, args, marker in [
                ('import', ['--headless', '--path', str(project), '--editor', '--quit'], None),
                ('gameplay', ['--headless', '--path', str(project), '--script', 'res://__studio_baseline.gd'], 'JUMPY_BASELINE_PASS')]:
                if label == 'gameplay':
                    shutil.copyfile(Path(__file__).with_name('jumpy_baseline.gd'), project / '__studio_baseline.gd')
                code, log = run([str(binary), *args])
                (out / (label + '.log')).write_text(log)
                if not gate_ok(code, log, marker):
                    raise StudioError('Jumpy ' + label + ' gate failed')
            report['status'] = 'baseline_passed'
    except (StudioError, OSError, ValueError, KeyError, zipfile.BadZipFile, subprocess.SubprocessError) as e:
        report['error'] = str(e) if isinstance(e, StudioError) else type(e).__name__
    (out / 'report.json').write_text(canonical(report))
    print(canonical(report))
    return 0 if report['status'] == 'baseline_passed' else 1

if __name__ == '__main__':
    raise SystemExit(main())

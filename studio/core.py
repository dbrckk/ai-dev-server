"""Bounded mobile studio. Standard library only; model output is data, never shell."""
from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import time
import uuid
import urllib.error
import urllib.request
from journeys import CONTRACT, encoded_journeys, validate_journeys

IMAGE = 'ghcr.io/cirruslabs/flutter:3.44.0@sha256:0a9de3b70b5b7b921a346eb2793e363dc22280849a4fd690d9dde99ce1c2b1b8'
ROLES = {
    'product': 'Senior mobile product lead: turn the brief into prioritized acceptance criteria, real user journeys, data model, scope, assumptions and external blockers. Never invent credentials or live services.',
    'design': 'Mobile art director: specify distinctive visual direction, exact color/type/spacing/radius/motion tokens, light/dark modes, accessible contrast, empty/loading/error states, small screens and large text. Prefer original vector/procedural visuals; record asset provenance. Use available SDK Roboto typography; do not promise missing custom fonts. No generic unfinished dashboard.',
    'implementation': 'Senior Flutter engineering team: implement the entire agreed app, real navigation, state, persistence when needed, error handling and meaningful widget/unit tests. Use lib/app.dart exposing const StudioApp({super.key}) and main.dart calling runApp(const StudioApp()). No placeholder buttons or fake backend success. Never weaken tests to hide defects. Use Flutter SDK packages only unless dependencies were explicitly approved in the brief. Do not add network permissions implicitly.',
    'tests': 'Senior Flutter QA engineer: read the supplied app source and acceptance journeys. Return real unit/widget tests covering primary actions, navigation and timer/state changes, using flutter_test and existing SDK dependencies. Every returned file must be under test/ and end in _test.dart. Do not change application source. Do not use vacuous assertions, skipped tests or mocked-away behavior. Tests must match the actual public APIs and widgets in the supplied source.',
    'review': 'Independent senior mobile reviewer: inspect implementation against every acceptance criterion, security, data durability, accessibility and maintainability. List concrete blocking defects, including absent features. Passing compilation alone is not completion.',
    'visual': 'Independent mobile visual QA: inspect the attached actual rendered screenshots against the design. Reject overflow, clipping, bad alignment, illegible text, low contrast, inconsistent spacing, generic unfinished visuals. Evaluate only screens actually shown. Never claim unseen interactions were tested.',
}

class StudioError(Exception):
    pass

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))

def request_check(data):
    if not isinstance(data, dict):
        raise StudioError('Request must be an object')
    required = {'id', 'target_repo', 'app_name', 'brief', 'enabled'}
    if set(data) - (required | {'max_rounds', 'max_calls', 'max_cycles'}) or not required <= set(data):
        raise StudioError('Invalid request fields')
    if not isinstance(data['enabled'], bool):
        raise StudioError('enabled must be boolean')
    for key, pattern in [('id', r'[a-z0-9][a-z0-9-]{0,47}'), ('target_repo', r'[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9][A-Za-z0-9_.-]*'), ('app_name', r'[a-z][a-z0-9_]{2,39}')]:
        if not isinstance(data[key], str) or not re.fullmatch(pattern, data[key]):
            raise StudioError('Invalid ' + key)
    if not isinstance(data['brief'], str) or not 20 <= len(data['brief']) <= 24000:
        raise StudioError('brief must contain 20..24000 characters')
    for key, default, maximum in [('max_rounds', 3, 6), ('max_calls', 12, 30), ('max_cycles', 5, 10)]:
        val = data.get(key, default)
        if type(val) is not int or not 1 <= val <= maximum:
            raise StudioError('Invalid ' + key)
        data[key] = val
    return data

def allowed(path):
    if not isinstance(path, str) or not path or '\\' in path or len(path) > 180:
        return False
    parts = path.split('/')
    if any(p in ('', '.', '..') or p.startswith('.') or p.startswith('__studio') for p in parts):
        return False
    return (path in ('pubspec.yaml', 'analysis_options.yaml', 'PROJECT_CONTEXT.md') or
            (parts[0] in ('lib', 'test') and path.endswith('.dart')) or
            (parts[0] == 'assets' and path.endswith(('.svg', '.json'))) or
            (parts[0] == 'docs' and path.endswith('.md')))

SECRET = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]+|nvapi-[A-Za-z0-9_-]{15,}|sk-[A-Za-z0-9_-]{20,}')

def patch_check(value):
    if not isinstance(value, dict) or set(value) != {'files'} or not isinstance(value['files'], list) or not 1 <= len(value['files']) <= 60:
        raise StudioError('Expected {files:[{path,content}]} with 1..60 files')
    seen, total = set(), 0
    for f in value['files']:
        if not isinstance(f, dict) or set(f) != {'path', 'content'} or not allowed(f['path']):
            raise StudioError('Patch path outside editable scope')
        if f['path'] in seen or not isinstance(f['content'], str) or '\x00' in f['content']:
            raise StudioError('Duplicate path or invalid content')
        seen.add(f['path'])
        total += len(f['content'].encode())
        if total > 600000 or SECRET.search(f['content']):
            raise StudioError('Patch too large or contains a credential pattern')
    return value['files']

def apply_patch(root, value):
    files = patch_check(value)
    for f in files:
        p = root / f['path']
        if not p.resolve().is_relative_to(root.resolve()) or any(x.is_symlink() for x in [p, *p.parents]):
            raise StudioError('Symlink or path escape')
    for f in files:
        p = root / f['path']
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f['content'])

def verdict(value):
    if (not isinstance(value, dict) or set(value) != {'passed', 'blockers'} or
        type(value['passed']) is not bool or not isinstance(value['blockers'], list) or
        any(not isinstance(x, str) or not x.strip() for x in value['blockers']) or
        value['passed'] == bool(value['blockers'])):
        raise StudioError('Invalid reviewer verdict')
    return value

class APIError(StudioError):
    def __init__(self, message, status=None):
        super().__init__(message); self.status = status

class API:
    def __init__(self, base, key=''):
        self.base, self.key = base.rstrip('/'), key
    def call(self, method, path, body=None, headers=None, timeout=90):
        url = self.base + path
        data = canonical(body).encode() if body is not None else None
        h = {'Accept': 'application/vnd.github+json', 'User-Agent': 'mobile-studio'}
        if self.key: h['Authorization'] = 'Bearer ' + self.key
        if data is not None: h['Content-Type'] = 'application/json'
        if headers: h.update(headers)
        req = urllib.request.Request(url, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            raise APIError('Remote API request failed', e.code) from None
        except (urllib.error.URLError, TimeoutError):
            raise APIError('Remote API unavailable') from None

class Model:
    def __init__(self, max_calls):
        self.max_calls=max_calls; self.calls=0; self.models_used={}; self.vision=os.environ.get('STUDIO_VISION_MODEL', '')
        self.base=os.environ.get('STUDIO_API_BASE','https://integrate.api.nvidia.com/v1').rstrip('/')
        self.key=os.environ.get('STUDIO_API_KEY',''); self.default=os.environ.get('STUDIO_MODEL','nvidia/nemotron-3-super-120b-a12b')
    def ask(self, role, payload, images=None):
        if not self.key: raise StudioError('Missing STUDIO_API_KEY')
        if self.calls >= self.max_calls: raise StudioError('Model call budget exhausted')
        self.calls += 1
        model = self.vision if images else self.default
        self.models_used[role] = model
        system = ROLES[role]
        content = [{'type':'text','text':payload}]
        if images:
            for p in images:
                content.append({'type':'image_url','image_url':{'url':'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()}})
        body={'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':content}], 'temperature':0.2,
              'response_format':{'type':'json_object'}}
        api=API(self.base,self.key)
        for attempt in range(3):
            try:
                result=api.call('POST','/chat/completions',body,timeout=180)
                break
            except APIError:
                if attempt == 2: raise
                time.sleep(2 ** attempt)
        try:
            text=result['choices'][0]['message']['content']
            parsed=json.loads(text)
            if role in ('review','visual'): return verdict(parsed)
            return parsed
        except (KeyError, IndexError, TypeError, ValueError):
            raise APIError('Provider returned invalid structured output') from None

class Sandbox:
    def __init__(self, root):
        self.root = root.resolve()
        self.native_files = {}
    def run(self, args, network=False, timeout=600):
        name = 'mobile-studio-' + uuid.uuid4().hex
        for p in [self.root, *self.root.rglob('*')]:
            if not p.is_symlink() and p.stat().st_uid == os.getuid():
                p.chmod(p.stat().st_mode | (0o777 if p.is_dir() else 0o666))
        cmd = ['docker', 'run', '--name', name, '--rm', '--init', '--cap-drop=ALL', '--security-opt=no-new-privileges',
               '--pids-limit=512', '--memory=6g', '--cpus=2', '--network=' + ('bridge' if network else 'none'),
               '-e', 'PUB_CACHE=/app/.studio-cache/pub', '-e', 'GRADLE_USER_HOME=/app/.studio-cache/gradle',
               '-v', str(self.root) + ':/app', '-w', '/app', IMAGE, 'bash', '-c',
               '"$@"; rc=$?; chmod -R a+rwX /app 2>/dev/null; exit $rc', '--'] + args
        run_id = os.environ.get('STUDIO_RUN_ID', '')
        if run_id:
            if not re.fullmatch(r'[0-9a-f]{32}', run_id):
                raise StudioError('Invalid sandbox run identifier')
            cmd[2:2] = ['--label', 'mobile-studio-run=' + run_id]
        env = {k: os.environ[k] for k in ('PATH', 'HOME', 'DOCKER_HOST') if k in os.environ}
        env.pop('DOCKER_HOST', None)
        try:
            r = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        except subprocess.TimeoutExpired:
            subprocess.run(['docker', 'rm', '-f', name], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
            raise StudioError('Sandbox command timed out') from None
        return r.returncode, r.stdout.decode(errors='replace')[-24000:]
    def create(self, name):
        rc, log = self.run(['flutter', 'create', '--no-pub', '--platforms=android,ios', '--project-name', name, '.'], network=True)
        if rc:
            raise StudioError('Flutter bootstrap failed: ' + log[-1000:])
        (self.root / 'test/widget_test.dart').unlink(missing_ok=True)
        self.native_files = {p.relative_to(self.root).as_posix(): p.read_bytes()
                             for folder in ('android', 'ios') for p in (self.root / folder).rglob('*')
                             if p.is_file() and not p.is_symlink() and p.name != 'local.properties'}
    def gates(self, name, journeys):
        probe = Path(__file__).with_name('visual_test.dart').read_text().replace('APP_NAME', name).replace('JOURNEYS_BASE64', encoded_journeys(journeys))
        import shutil
        shutil.rmtree(self.root / 'test/goldens', ignore_errors=True)
        (self.root / 'test').mkdir(exist_ok=True)
        (self.root / 'test/__studio_visual_test.dart').write_text(probe)
        (self.root / 'dart_test.yaml').write_text('tags:\n  studio-visual:\n')
        logs = []
        for args, network in [(['flutter', 'pub', 'get'], True),
                              (['flutter', 'analyze', '--no-pub'], False),
                              (['flutter', 'test', '--no-pub', '--exclude-tags=studio-visual'], False),
                              (['flutter', 'test', '--no-pub', '--update-goldens', 'test/__studio_visual_test.dart'], False),
                              (['flutter', 'build', 'apk', '--debug', '--no-pub'], True)]:
            print('Gate: ' + ' '.join(args), flush=True)
            rc, out = self.run(args, network=network, timeout=900)
            logs.append({'command': args, 'exit_code': rc, 'output': out})
            if rc:
                return False, logs
        for rel, original in self.native_files.items():
            p = self.root / rel
            if p.is_symlink() or not p.is_file() or p.read_bytes() != original:
                logs.append({'command': ['native-template-integrity'], 'exit_code': 1, 'output': 'Native template changed: ' + rel})
                return False, logs
        apk = self.root / 'build/app/outputs/flutter-apk/app-debug.apk'
        pngs = list((self.root / 'test/goldens').glob('*.png'))
        return apk.is_file() and apk.stat().st_size > 1000 and len(pngs) == 4 * (1 + len(journeys)), logs
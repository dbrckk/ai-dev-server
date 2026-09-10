"""GitHub brief -> bounded Flutter studio -> checkpoint branch and build artifacts."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import urllib.error

from journeys import validate_journeys
from core import API, APIError, Model, Sandbox, StudioError, allowed, apply_patch, canonical, request_check, verdict, SECRET
from project_context import write as write_project_context
from core import require_clean_patch_workspace

class GitHub(API):
    def __init__(self, repo):
        super().__init__('https://api.github.com', os.environ.get('STUDIO_GITHUB_TOKEN', ''))
        if not self.key:
            raise StudioError('Missing STUDIO_GITHUB_TOKEN with access to target repository')
        self.repo = '/repos/' + repo
    def get(self, path):
        return self.call('GET', self.repo + path)
    def restore(self, branch, root):
        metadata = self.get('')
        try:
            refs = self.get('/git/matching-refs/heads/' + branch)
        except APIError as e:
            if e.status != 409 or metadata.get('size', 0) != 0:
                raise
            initial = self.call('PUT', self.repo + '/contents/README.md', {
                'message': 'Initialize mobile studio target',
                'content': base64.b64encode(b'# Mobile app\n\nSources are generated in the studio branch.\n').decode()})
            return None, initial['commit']['sha']
        exact = [r for r in refs if r['ref'] == 'refs/heads/' + branch]
        if metadata.get('archived'):
            raise StudioError('Target repository is archived')
        if not exact:
            if metadata.get('size', 0) > 0:
                default = metadata['default_branch']
                tree = self.get('/git/trees/' + default + '?recursive=1')
                paths = {x['path'] for x in tree['tree'] if x['type'] == 'blob'}
                if paths - {'README.md', 'LICENSE', '.gitignore'}:
                    raise StudioError('Initial target must be empty or contain only README/LICENSE/.gitignore')
                return None, self.get('/branches/' + default)['commit']['sha']
            return None, None
        parent = exact[0]['object']['sha']
        tree = self.get('/git/trees/' + parent + '?recursive=1')
        if tree.get('truncated') or len(tree['tree']) > 1000:
            raise StudioError('Target tree exceeds supported size')
        state = None
        for item in tree['tree']:
            path = item['path']
            if item['type'] != 'blob' or not (allowed(path) or path in ('.studio/state.json', 'pubspec.lock')):
                continue
            if item.get('mode') != '100644' or item.get('size', 0) > 600000:
                raise StudioError('Unsupported target file')
            blob = self.get('/git/blobs/' + item['sha'])
            content = base64.b64decode(blob['content']).decode()
            if path == '.studio/state.json':
                state = json.loads(content)
            elif path == 'pubspec.lock':
                (root / path).write_text(content)
            else:
                apply_patch(root, {'files': [{'path': path, 'content': content}]})
        if state is None:
            raise StudioError('Existing studio branch has no checkpoint; refusing overwrite')
        return state, parent
    def publish(self, branch, parent, root, state):
        require_clean_patch_workspace(root)
        # Metadata is published too: validate it before any remote operation.
        try:
            state_json = json.dumps(state, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':'), allow_nan=False)
            state_json.encode('utf-8')
        except (TypeError, ValueError, RecursionError):
            raise StudioError('Checkpoint metadata is not valid JSON') from None
        if SECRET.search(state_json):
            raise StudioError('Checkpoint metadata contains a credential pattern')
        entries = []
        previous = {}
        if parent:
            previous = {x['path']: x.get('sha') for x in self.get('/git/trees/' + parent + '?recursive=1')['tree']}
        candidates = {}
        for p in sorted(root.rglob('*')):
            if not p.is_file() or p.is_symlink():
                continue
            rel = p.relative_to(root).as_posix()
            if any(x in ('build', '.dart_tool', '.studio-cache', '.gradle', 'goldens') for x in p.relative_to(root).parts):
                continue
            if rel.startswith('test/__studio') or rel.endswith(('local.properties', '.iml')):
                continue
            if not (allowed(rel) or rel in ('pubspec.lock', 'PROJECT_CONTEXT.md')):
                continue
            candidates[rel] = p.read_bytes()
        candidates.update(getattr(self, 'native_files', {}))
        for rel, content in sorted(candidates.items()):
            if len(content) > 1000000 or SECRET.search(content.decode(errors='ignore')):
                raise StudioError('Publication file rejected')
            sha = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
            if previous.get(rel) == sha:
                continue
            entry = {'path': rel, 'mode': '100755' if rel == 'android/gradlew' else '100644', 'type': 'blob'}
            try:
                entry['content'] = content.decode('utf-8')
            except UnicodeDecodeError:
                blob = self.call('POST', self.repo + '/git/blobs', {'encoding': 'base64', 'content': base64.b64encode(content).decode()})
                entry['sha'] = blob['sha']
            entries.append(entry)
        entries.append({'path': '.studio/state.json', 'mode': '100644', 'type': 'blob', 'content': state_json})
        data = {'tree': entries}
        if parent:
            data['base_tree'] = self.get('/git/commits/' + parent)['tree']['sha']
        tree = self.call('POST', self.repo + '/git/trees', data)
        commit = self.call('POST', self.repo + '/git/commits', {'message': 'Mobile studio: ' + state['status'], 'tree': tree['sha'], 'parents': [parent] if parent else []})
        refs = self.get('/git/matching-refs/heads/' + branch)
        exists = any(r['ref'] == 'refs/heads/' + branch for r in refs)
        if exists:
            self.call('PATCH', self.repo + '/git/refs/heads/' + branch, {'sha': commit['sha'], 'force': False})
        else:
            self.call('POST', self.repo + '/git/refs', {'ref': 'refs/heads/' + branch, 'sha': commit['sha']})
        return commit['sha']

def context(req, state, root):
    files = {p.relative_to(root).as_posix(): p.read_text() for p in sorted(root.rglob('*'))
             if p.is_file() and not p.is_symlink() and allowed(p.relative_to(root).as_posix())}
    return canonical({'request': req, 'product': state.get('product'), 'design': state.get('design'),
                      'previous_blockers': state.get('blockers', []), 'files': files})

def execute(req, root, out, github=None, model_factory=Model, sandbox_factory=Sandbox):
    def clear_preview_evidence(state):
        for key in ('apk_sha256', 'validation_contract', 'code_review', 'visual_review', 'visual_reviews'):
            state.pop(key, None)

    req = request_check(req)
    if not req['enabled']:
        return {'status': 'disabled'}
    if req['target_repo'].lower() == os.environ.get('GITHUB_REPOSITORY', '').lower():
        raise StudioError('Target must be separate from the control repository')
    github = github or GitHub(req['target_repo'])
    branch = 'studio/' + req['id']
    root.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise StudioError('Workspace must be fresh; resume uses the remote checkpoint')
    with tempfile.TemporaryDirectory() as saved:
        saved_root = Path(saved)
        state, parent = github.restore(branch, saved_root)
        fingerprint = hashlib.sha256(canonical({k: v for k, v in req.items() if k != 'enabled'}).encode()).hexdigest()
        if state and state.get('request_hash') != fingerprint:
            raise StudioError('Brief changed for existing id; use a new id and fresh target')
        state = state or {'request_hash': fingerprint, 'status': 'pending', 'cycles': 0, 'rounds': 0, 'blockers': []}
        if state['status'] == 'validated_preview' and state.get('validation_contract') != 2:
            state.update(status='validation_upgrade_required', blockers=['Acceptance-journey validation required for this older checkpoint.'])
        if state.get('product') and 'journeys' not in state['product']:
            state.pop('product')
        if state['status'] == 'validated_preview' or state['cycles'] >= req['max_cycles']:
            (out / 'report.json').write_text(canonical(state))
            return state
        clear_preview_evidence(state)
        model = model_factory(req['max_calls'])
        sandbox = sandbox_factory(root)
        sandbox.create(req['app_name'])
        github.native_files = getattr(sandbox, 'native_files', {})
        for p in saved_root.rglob('*'):
            if p.name == 'pubspec.lock':
                (root / 'pubspec.lock').write_bytes(p.read_bytes())
            elif p.is_file():
                apply_patch(root, {'files': [{'path': p.relative_to(saved_root).as_posix(), 'content': p.read_text()}]})
    state['cycles'] += 1

    def checkpoint(parent_sha):
        require_clean_patch_workspace(root)
        write_project_context(root, req, state)
        return github.publish(branch, parent_sha, root, state)

    try:
        for role in ('product', 'design'):
            if role not in state:
                result = model.ask(role, context(req, state, root))
                if role == 'product':
                    try:
                        validate_journeys(result.get('journeys'))
                    except ValueError as e:
                        raise StudioError(str(e)) from None
                state[role] = result
                state['status'] = role + '_complete'
                parent = checkpoint(parent)
        for _ in range(req['max_rounds']):
            state['rounds'] += 1
            clear_preview_evidence(state)
            patch = model.ask('implementation', context(req, state, root))
            apply_patch(root, patch)
            if not any(not p.name.startswith('__studio') for p in (root / 'test').rglob('*_test.dart')):
                qa_patch = model.ask('tests', context(req, state, root))
                apply_patch(root, qa_patch)
            if not any(not p.name.startswith('__studio') for p in (root / 'test').rglob('*_test.dart')):
                raise StudioError('QA must supply test/*_test.dart files')
            try:
                journeys = validate_journeys(state['product'].get('journeys'))
            except ValueError as e:
                raise StudioError(str(e)) from None
            passed, logs = sandbox.gates(req['app_name'], journeys)
            (out / 'validation.json').write_text(canonical(logs))
            state['status'] = 'repair_needed'
            if not passed:
                state['blockers'] = ['Validation failed: ' + canonical(logs[-1:])[-16000:]]
                parent = checkpoint(parent)
                continue
            state['validation_contract'] = 2
            review = verdict(model.ask('review', context(req, state, root)))
            state['code_review'] = review
            if not review['passed']:
                state['blockers'] = review['blockers']
                parent = checkpoint(parent)
                continue
            screenshots = sorted((root / 'test/goldens').glob('*.png'))
            if not model.vision:
                state.update(status='awaiting_visual_review', blockers=['Configure STUDIO_VISION_MODEL on a provider supporting image input.'])
                break
            visual = {'passed': True, 'blockers': []}
            state['visual_reviews'] = {}
            for screen in ['initial'] + [j['id'] for j in journeys]:
                batch = [p for p in screenshots if p.name.startswith(screen + '--')]
                if len(batch) != 4:
                    raise StudioError('Missing actual screenshots for ' + screen)
                result = verdict(model.ask('visual', canonical({'brief': req['brief'], 'design': state['design'],
                    'screen': screen, 'journeys': journeys}), batch))
                state['visual_reviews'][screen] = result
                visual['blockers'].extend(screen + ': ' + item for item in result['blockers'])
            visual['passed'] = not visual['blockers']
            state['visual_review'] = visual
            if not visual['passed']:
                state['blockers'] = visual['blockers']
                parent = checkpoint(parent)
                continue
            state.update(status='validated_preview', blockers=[])
            break
    except StudioError as e:
        state.update(status='blocked', blockers=[str(e)])
    # Publish only completed or explicitly handled failures. An unexpected fatal
    # error (especially failed patch rollback) leaves workspace integrity unknown.
    state['model_calls_this_cycle'] = model.calls
    state['models_used'] = getattr(model, 'models_used', {})
    state['limits'] = {'max_cycles': req['max_cycles'], 'max_calls_per_cycle': req['max_calls'], 'max_rounds_per_cycle': req['max_rounds']}
    state['release_status'] = 'not_store_ready'
    state['coverage'] = {'variants_per_path': 4, 'journeys': [j['id'] for j in state.get('product', {}).get('journeys', [])], 'scope': 'Initial screen and final screen of each declared journey; not all possible states or real-device testing.'}
    for p in (root / 'test/goldens').glob('*.png'):
        shutil.copyfile(p, out / p.name)
    apk = root / 'build/app/outputs/flutter-apk/app-debug.apk'
    if state['status'] in ('validated_preview', 'awaiting_visual_review') and apk.is_file():
        shutil.copyfile(apk, out / 'app-debug.apk')
        state['apk_sha256'] = hashlib.sha256(apk.read_bytes()).hexdigest()
    (out / 'report.json').write_text(canonical(state))
    sha = checkpoint(parent)
    state['checkpoint_commit'] = sha
    (out / 'report.json').write_text(canonical(state))
    return state

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('request')
    parser.add_argument('--work', default='/tmp/mobile-studio-app')
    parser.add_argument('--out', default='studio-output')
    args = parser.parse_args()
    try:
        provider = os.environ.get('STUDIO_CI_PROVIDER')
        if provider:
            from ci_provider import enabled
            if not enabled(provider):
                print('Generation inactive for this CI provider')
                return 0
        state = execute(json.loads(Path(args.request).read_text()), Path(args.work), Path(args.out))
        print(canonical({'status': state['status'], 'checkpoint_commit': state.get('checkpoint_commit')}))
        return 0 if state['status'] in ('disabled', 'validated_preview', 'awaiting_visual_review') else 1
    except (StudioError, ValueError, OSError) as e:
        Path(args.out).mkdir(parents=True, exist_ok=True)
        (Path(args.out) / 'error.json').write_text(canonical({'status': 'blocked', 'error': type(e).__name__, 'detail': str(e) if isinstance(e, StudioError) else 'Invalid configuration or local IO failure'}))
        print('Studio blocked; see error.json and existing checkpoint.', file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())

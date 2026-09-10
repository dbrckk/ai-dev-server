"""Resumable model-driven preview cycle for an existing Godot repository.

The runner checkpoints only to studio/<request-id>. It never updates the target default
branch and never claims Android export, device QA, visual QA or journey execution.
"""
from __future__ import annotations

import base64
import hashlib
from pathlib import Path

from core import StudioError, canonical, request_check, verdict
from engine_patch import SECRET, validate as validate_patch
from existing_project import ExistingProjectError, materialize, plan
from godot_model import GodotModel
from godot_session import GodotSandbox
from journeys import validate_journeys
from project_engine import editable, restorable

MAX_PUBLISH_FILE_BYTES = 1_000_000


def _safe_apply(root: Path, value: dict, role: str) -> None:
    files = validate_patch(value, 'godot', role)
    root = root.resolve(); targets = []
    for item in files:
        target = (root / item['path']).resolve()
        if not target.is_relative_to(root) or any(part.is_symlink() for part in [target, *target.parents] if part != root.parent):
            raise StudioError('Godot patch path escaped workspace or crossed symlink')
        targets.append((target, item['content']))
    for target, content in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)


def _context(req: dict, state: dict, root: Path) -> str:
    files = {}
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if editable(rel, 'godot'):
            files[rel] = path.read_text()
    return canonical({'engine':'godot','request':req,'product':state.get('product'),'design':state.get('design'),
                      'previous_blockers':state.get('blockers',[]),'files':files})


def _exact_branch_ref(github, branch: str):
    refs = github.get('/git/matching-refs/heads/' + branch)
    if not isinstance(refs, list):
        raise StudioError('Target branch lookup returned invalid data')
    exact = [item for item in refs if isinstance(item, dict) and item.get('ref') == 'refs/heads/' + branch]
    if len(exact) > 1:
        raise StudioError('Target branch lookup is ambiguous')
    return exact[0] if exact else None


def _restore(github, branch: str, root: Path) -> tuple[dict | None, str, bool]:
    metadata = github.get('')
    if not isinstance(metadata, dict) or metadata.get('archived'):
        raise StudioError('Target repository is unavailable or archived')
    branch_ref = _exact_branch_ref(github, branch)
    if branch_ref:
        parent = branch_ref.get('object', {}).get('sha')
        if not isinstance(parent, str) or len(parent) != 40:
            raise StudioError('Studio checkpoint branch has invalid head')
        source_ref = parent; existing_checkpoint = True
    else:
        default = metadata.get('default_branch')
        if not isinstance(default, str) or not default:
            raise StudioError('Existing Godot target requires a default branch')
        branch_info = github.get('/branches/' + default)
        parent = branch_info.get('commit', {}).get('sha') if isinstance(branch_info, dict) else None
        if not isinstance(parent, str) or len(parent) != 40:
            raise StudioError('Target default branch head is invalid')
        source_ref = parent; existing_checkpoint = False
    tree = github.get('/git/trees/' + source_ref + '?recursive=1')
    try:
        import_plan = plan(tree, expected_engine='godot')
        materialize(root, import_plan, lambda sha: github.get('/git/blobs/' + sha))
    except ExistingProjectError as exc:
        raise StudioError(str(exc)) from None
    state = None
    state_path = root / '.studio/state.json'
    if state_path.is_file():
        try:
            import json
            state = json.loads(state_path.read_text())
        except (OSError, ValueError):
            raise StudioError('Godot checkpoint state is invalid') from None
        state_path.unlink()
    if existing_checkpoint and not isinstance(state, dict):
        raise StudioError('Existing Godot studio branch has no checkpoint state')
    return state, parent, existing_checkpoint


def _publish(github, branch: str, parent: str, root: Path, state: dict) -> str:
    current = _exact_branch_ref(github, branch)
    if current:
        current_sha = current.get('object', {}).get('sha')
        if current_sha != parent:
            raise StudioError('Godot checkpoint branch moved during generation')
    entries = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if not restorable(rel, 'godot') or rel == '.studio/state.json':
            continue
        content = path.read_bytes()
        if len(content) > MAX_PUBLISH_FILE_BYTES or SECRET.search(content.decode(errors='ignore')):
            raise StudioError('Godot publication file rejected')
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            raise StudioError('Godot publication currently permits UTF-8 text only') from None
        entries.append({'path':rel,'mode':'100644','type':'blob','content':text})
    entries.append({'path':'.studio/state.json','mode':'100644','type':'blob','content':canonical(state)})
    base_tree = github.get('/git/commits/' + parent).get('tree', {}).get('sha')
    if not isinstance(base_tree, str) or len(base_tree) != 40:
        raise StudioError('Godot publication base tree is invalid')
    tree = github.call('POST', github.repo + '/git/trees', {'base_tree':base_tree,'tree':entries})
    tree_sha = tree.get('sha') if isinstance(tree, dict) else None
    if not isinstance(tree_sha, str) or len(tree_sha) != 40:
        raise StudioError('Godot publication tree creation failed')
    commit = github.call('POST', github.repo + '/git/commits', {'message':'Godot studio: ' + state['status'],'tree':tree_sha,'parents':[parent]})
    commit_sha = commit.get('sha') if isinstance(commit, dict) else None
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        raise StudioError('Godot publication commit creation failed')
    if current:
        github.call('PATCH', github.repo + '/git/refs/heads/' + branch, {'sha':commit_sha,'force':False})
    else:
        github.call('POST', github.repo + '/git/refs', {'ref':'refs/heads/' + branch,'sha':commit_sha})
    return commit_sha


def execute(req: dict, root: Path, out: Path, github, model_factory=GodotModel, sandbox_factory=GodotSandbox) -> dict:
    req = request_check(req)
    if not req['enabled']:
        return {'status':'disabled','engine':'godot'}
    root.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise StudioError('Workspace must be fresh; Godot resume uses remote checkpoint')
    branch = 'studio/' + req['id']
    state, parent, resumed = _restore(github, branch, root)
    fingerprint = hashlib.sha256(canonical({k:v for k,v in req.items() if k != 'enabled'}).encode()).hexdigest()
    if state and state.get('request_hash') != fingerprint:
        raise StudioError('Brief changed for existing Godot id; use a new id')
    state = state or {'request_hash':fingerprint,'status':'pending','engine':'godot','cycles':0,'rounds':0,'blockers':[]}
    if state.get('engine') != 'godot':
        raise StudioError('Checkpoint engine mismatch')
    if state['status'] == 'godot_preview_validated' or state['cycles'] >= req['max_cycles']:
        (out / 'report.json').write_text(canonical(state)); return state
    model = model_factory(req['max_calls']); sandbox = sandbox_factory(root); sandbox.create(req['app_name'])
    state['cycles'] += 1

    def checkpoint() -> None:
        nonlocal parent
        parent = _publish(github, branch, parent, root, state)

    try:
        for role in ('product','design'):
            if role not in state:
                result = model.ask(role, _context(req,state,root))
                if role == 'product':
                    try: validate_journeys(result.get('journeys'))
                    except ValueError as exc: raise StudioError(str(exc)) from None
                state[role] = result; state['status'] = role + '_complete'; checkpoint()
        for _ in range(req['max_rounds']):
            state['rounds'] += 1
            patch = model.ask('implementation', _context(req,state,root)); _safe_apply(root, patch, 'implementation')
            if not any(p.is_file() and not p.is_symlink() for p in (root / 'tests').rglob('*.gd')):
                qa = model.ask('tests', _context(req,state,root)); _safe_apply(root, qa, 'tests')
            if not any(p.is_file() and not p.is_symlink() for p in (root / 'tests').rglob('*.gd')):
                raise StudioError('Godot QA must supply tests/*.gd')
            try: journeys = validate_journeys(state['product'].get('journeys'))
            except ValueError as exc: raise StudioError(str(exc)) from None
            passed, logs = sandbox.gates(req['app_name'], journeys)
            (out / 'validation.json').write_text(canonical(logs))
            if not passed:
                state.update(status='repair_needed',blockers=['Godot headless validation failed: ' + canonical(logs[-1:])[-16000:]])
                checkpoint(); continue
            review = verdict(model.ask('review', _context(req,state,root))); state['code_review'] = review
            if not review['passed']:
                state.update(status='repair_needed',blockers=review['blockers']); checkpoint(); continue
            state.update(status='godot_preview_validated',blockers=[],validation_contract='godot-headless-v1')
            state['completion'] = {'finished':False,'next_stage':'godot_android_export_qa',
                                   'reason':'Headless Godot validation passed; Android export/device/visual journey evidence still required.'}
            break
    except StudioError as exc:
        state.update(status='blocked',blockers=[str(exc)])
    finally:
        state['model_calls_this_cycle'] = model.calls
        state['models_used'] = getattr(model,'models_used',{})
        state['release_status'] = 'not_store_ready'
        state['coverage'] = {'engine':'godot','headless_import':True,'journeys_executed':False,
                             'android_export':False,'device_qa':False,'visual_qa':False}
        (out / 'report.json').write_text(canonical(state))
        checkpoint(); state['checkpoint_commit'] = parent
        (out / 'report.json').write_text(canonical(state))
    return state

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
from core import API, APIError, Model, Sandbox, StudioError, allowed, apply_patch, canonical, request_check, verdict, SECRET, require_clean_patch_workspace
from project_context import write as write_project_context
from repair_planner import preview_plan
from repair_queue import complete_stage_tasks, enqueue, summarize
from project_budget import budget_status, can_spend, configure as configure_budget, record_calls
from idempotent_model import ask_value as checkpointed_ask
from atomic_file import write_text as atomic_write_text
from architecture_planner import write as write_architecture_plan
from architecture_outcome import write as write_architecture_outcome
from architecture_learning import write as write_architecture_learning, summarize as summarize_architecture_learning, root_for_output as architecture_learning_root
from architecture_replacement_learning import summarize as summarize_replacement_learning
from architecture_evaluator import write as write_architecture_evaluation
from architecture_benchmark import write as write_architecture_benchmark
from architecture_preflight import write as write_architecture_preflight
from architecture_change_guard import enforce as enforce_architecture_change_guard, ArchitectureChangeBlocked
from architecture_safe_rewrite import build_context as build_architecture_safe_rewrite_context
from capacity_status import snapshot as capacity_snapshot
from safe_rewrite_learning import (
    record_attempt as record_safe_rewrite_attempt,
    finalize as finalize_safe_rewrite,
    summarize as summarize_safe_rewrite_learning,
)

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
                branch_info = self.get('/branches/' + default)
                parent = branch_info['commit']['sha']
                tree = self.get('/git/trees/' + parent + '?recursive=1')
                if tree.get('truncated') or len(tree.get('tree', [])) > 2000:
                    raise StudioError('Target tree exceeds supported size')
                paths = {x['path'] for x in tree['tree'] if x.get('type') == 'blob'}
                bootstrap_only = paths <= {'README.md', 'LICENSE', '.gitignore'}
                existing_flutter = 'pubspec.yaml' in paths and any(
                    path.startswith('lib/') and path.endswith('.dart') for path in paths
                )
                if bootstrap_only:
                    return None, parent
                if not existing_flutter:
                    raise StudioError('Existing target is not a supported Flutter source repository')
                self.existing_project = True
                # Import only the trusted editable Flutter source surface. The default
                # branch remains the base tree, so unrelated/native files are preserved
                # on the studio branch rather than deleted.
                for item in tree['tree']:
                    path = item.get('path')
                    if item.get('type') != 'blob' or not isinstance(path, str):
                        continue
                    if not (allowed(path) or path == 'pubspec.lock'):
                        continue
                    if item.get('mode') != '100644' or item.get('size', 0) > 600000:
                        raise StudioError('Unsupported existing project source file')
                    blob = self.get('/git/blobs/' + item['sha'])
                    content = base64.b64decode(blob['content']).decode()
                    if path == 'pubspec.lock':
                        (root / path).write_text(content)
                    else:
                        apply_patch(root, {'files': [{'path': path, 'content': content}]})
                return None, parent
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
        try:
            state_json = json.dumps(state, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':'), allow_nan=False)
            state_json.encode('utf-8')
        except (TypeError, ValueError, UnicodeError, RecursionError):
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

def _load_architecture_replacement_work_orders(out: Path) -> dict:
    path = Path(out) / 'architecture-replacement-work-orders.json'
    if not path.is_file():
        return {'status': 'unavailable', 'work_orders': []}
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {'status': 'invalid', 'work_orders': []}
    if not isinstance(value, dict):
        return {'status': 'invalid', 'work_orders': []}
    work_orders = []
    for row in value.get('work_orders', [])[:4]:
        if not isinstance(row, dict):
            continue
        work_orders.append({
            'id': row.get('id'),
            'current_repo': row.get('current_repo'),
            'replacement_repo': row.get('replacement_repo'),
            'risk': row.get('risk'),
            'scope': row.get('scope'),
            'go_no_go': row.get('go_no_go'),
        })
    return {
        'status': value.get('status', 'planned'),
        'work_orders': work_orders,
        'advisory_only': True,
    }

def _load_architecture_replacement_plan(out: Path) -> dict:
    path = Path(out) / 'architecture-replacement-plan.json'
    if not path.is_file():
        return {'status': 'unavailable', 'replacement_plans': []}
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {'status': 'invalid', 'replacement_plans': []}
    if not isinstance(value, dict):
        return {'status': 'invalid', 'replacement_plans': []}
    plans = []
    for row in value.get('replacement_plans', [])[:8]:
        if not isinstance(row, dict):
            continue
        plans.append({
            'current_repo': row.get('current_repo'),
            'replacement_repo': row.get('replacement_repo'),
            'risk': row.get('risk'),
            'benchmark_delta': row.get('benchmark_delta'),
            'estimated_change_scope': row.get('estimated_change_scope'),
            'go_no_go': row.get('go_no_go'),
            'required_gates': row.get('required_gates', [])[:12],
        })
    return {
        'status': value.get('status', 'planned'),
        'replacement_plans': plans,
        'advisory_only': True,
    }

def _load_architecture_obsolescence(out: Path) -> dict:
    path = Path(out) / 'architecture-obsolescence.json'
    if not path.is_file():
        return {'status': 'unavailable', 'deprecation_candidates': []}
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {'status': 'invalid', 'deprecation_candidates': []}
    if not isinstance(value, dict):
        return {'status': 'invalid', 'deprecation_candidates': []}
    candidates = []
    for row in value.get('deprecation_candidates', [])[:8]:
        if not isinstance(row, dict):
            continue
        candidates.append({
            'repo': row.get('repo'),
            'replacement_candidate': row.get('replacement_candidate'),
            'drift_score': row.get('drift_score'),
            'benchmark_delta': row.get('benchmark_delta'),
            'maintenance_signal': row.get('maintenance_signal'),
            'reason': row.get('reason'),
        })
    return {
        'status': value.get('status', 'evaluated'),
        'deprecation_candidates': candidates,
        'advisory_only': True,
    }

def _load_architecture_benchmark(out: Path) -> dict:
    path = Path(out) / 'architecture-benchmark.json'
    if not path.is_file():
        return {'status': 'unavailable', 'migration_candidates': []}
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {'status': 'invalid', 'migration_candidates': []}
    if not isinstance(value, dict):
        return {'status': 'invalid', 'migration_candidates': []}
    candidates = []
    for row in value.get('migration_candidates', [])[:8]:
        if not isinstance(row, dict):
            continue
        candidates.append({
            'current_repo': row.get('current_repo'),
            'best_alternative': row.get('best_alternative'),
            'current_score': row.get('current_score'),
            'migration_reason': row.get('migration_reason'),
        })
    return {
        'status': value.get('status', 'benchmarked'),
        'evaluation_verdict': value.get('evaluation_verdict'),
        'migration_candidates': candidates,
        'advisory_only': True,
    }

def _load_star_recommendations(out: Path) -> dict:
    """Load bounded recommendation evidence as advisory data only."""
    path = Path(out) / 'star-recommendations.json'
    if not path.is_file():
        return {'status': 'unavailable', 'matches': []}
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {'status': 'invalid', 'matches': []}
    if not isinstance(value, dict):
        return {'status': 'invalid', 'matches': []}
    safe = []
    for row in value.get('matches', [])[:12]:
        if not isinstance(row, dict) or not isinstance(row.get('repo'), str):
            continue
        safe.append({
            'repo': row['repo'][:160],
            'score': row.get('score'),
            'quality_score': row.get('quality_score'),
            'tier': row.get('tier'),
            'domain': row.get('domain'),
            'capabilities': [str(x)[:80] for x in row.get('capabilities', [])[:16]],
            'best_for': [str(x)[:160] for x in row.get('best_for', [])[:8]],
            'avoid_when': [str(x)[:160] for x in row.get('avoid_when', [])[:8]],
            'alternatives': [str(x)[:160] for x in row.get('alternatives', [])[:8]],
            'complements': [str(x)[:160] for x in row.get('complements', [])[:8]],
        })
    return {
        'status': value.get('status', 'ok'),
        'phase': value.get('phase'),
        'source_format': value.get('source_format'),
        'matches': safe,
        'advisory_only': True,
    }

def context(req, state, root):
    files = {p.relative_to(root).as_posix(): p.read_text() for p in sorted(root.rglob('*'))
             if p.is_file() and not p.is_symlink() and allowed(p.relative_to(root).as_posix())}
    return canonical({'request': req, 'product': state.get('product'), 'design': state.get('design'),
                      'previous_blockers': state.get('blockers', []),
                      'technical_recommendations': state.get('technical_recommendations', {'status':'unavailable','matches':[]}),
                      'architecture_decision': state.get('architecture_decision', {'status':'unavailable','chosen':[]}),
                      'architecture_autonomy_policy': state.get('architecture_autonomy_policy', {}),
                      'architecture_preflight': state.get('architecture_preflight', {'status':'unavailable','verdict':'unknown'}),
                      'architecture_benchmark': state.get('architecture_benchmark', {'status':'unavailable','migration_candidates':[]}),
                      'architecture_obsolescence': state.get('architecture_obsolescence', {'status':'unavailable','deprecation_candidates':[]}),
                      'architecture_replacement_plan': state.get('architecture_replacement_plan', {'status':'unavailable','replacement_plans':[]}),
                      'architecture_replacement_work_orders': state.get('architecture_replacement_work_orders', {'status':'unavailable','work_orders':[]}),
                      'architecture_replacement_learning': state.get('architecture_replacement_learning', {'outcomes_observed':0,'rankings':[]}),
                      'architecture_drift_alerts': state.get('architecture_drift_alerts', []),
                      'files': files})

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
        configure_budget(state, req)
        state['publication_request'] = dict(req.get('play_publish', {'enabled': False, 'track': 'internal', 'commit': False}))
        if state['status'] == 'human_action_required' and state.get('validation_contract') == 2:
            state['status'] = 'validated_preview'
        if state['status'] == 'validated_preview' and state.get('validation_contract') != 2:
            state.update(status='validation_upgrade_required', blockers=['Acceptance-journey validation required for this older checkpoint.'])
        if state.get('product') and 'journeys' not in state['product']:
            state.pop('product')
        if state['status'] == 'validated_preview' or state['cycles'] >= req['max_cycles']:
            atomic_write_text(out / 'report.json', canonical(state))
            return state
        clear_preview_evidence(state)
        autonomy_dir = out / '.autonomy'
        autonomy_dir.mkdir(parents=True, exist_ok=True)
        os.environ['STUDIO_PROVIDER_COST_PATH'] = str(autonomy_dir / 'provider-cost.json')
        os.environ['STUDIO_PROVIDER_MONTHLY_QUOTA_PATH'] = str(autonomy_dir / 'provider-monthly-quota.json')
        max_api_cost = req.get('max_api_cost_usd')
        if isinstance(max_api_cost, (int, float)) and float(max_api_cost) > 0:
            os.environ['STUDIO_MAX_API_COST_USD'] = str(float(max_api_cost))
        else:
            os.environ.pop('STUDIO_MAX_API_COST_USD', None)
        state['budget_policy'] = {
            **state.get('budget_policy', {}),
            'max_api_cost_usd': float(max_api_cost) if isinstance(max_api_cost, (int, float)) and float(max_api_cost) > 0 else None,
            'unmetered_continues_after_paid_budget': True,
            'pooled_free_continues_after_paid_budget': True,
        }
        state['capacity_status'] = capacity_snapshot(
            autonomy_dir / 'provider-monthly-quota.json'
        )
        cycle_budget = min(req['max_calls'], max(0, budget_status(state)['model_calls_remaining']))
        if cycle_budget < 1:
            state.update(status='blocked', blockers=['Project model-call budget exhausted'])
            atomic_write_text(out / 'report.json', canonical(state))
            return state
        model = model_factory(cycle_budget)
        sandbox = sandbox_factory(root)
        sandbox.create(req['app_name'])
        github.native_files = getattr(sandbox, 'native_files', {})
        for p in saved_root.rglob('*'):
            if p.name == 'pubspec.lock':
                (root / 'pubspec.lock').write_bytes(p.read_bytes())
            elif p.is_file():
                apply_patch(root, {'files': [{'path': p.relative_to(saved_root).as_posix(), 'content': p.read_text()}]})
    safe_rewrite_learning_path = out / '.autonomy' / 'safe-rewrite-learning.json'
    state['technical_recommendations'] = _load_star_recommendations(out)
    historical_root = architecture_learning_root(out)
    historical_learning = summarize_architecture_learning(historical_root)
    replacement_learning = summarize_replacement_learning(historical_root)
    state['architecture_replacement_learning'] = {
        'outcomes_observed': replacement_learning.get('outcomes_observed',0),
        'rankings': replacement_learning.get('rankings',[])[:20],
        'advisory_only': True,
    }
    state['architecture_drift_alerts'] = historical_learning.get('drift_alerts', [])[:20]
    state['architecture_decision'] = write_architecture_plan(
        req,
        state['technical_recommendations'],
        out,
        learning=historical_learning,
        framework="flutter",
        publication_target="google-play",
    )
    state['architecture_autonomy_policy'] = state['architecture_decision'].get('autonomy_policy', {})
    state['architecture_preflight'] = write_architecture_preflight(
        state['architecture_decision'],
        state['technical_recommendations'],
        out,
    )
    state['architecture_autonomy_policy']['architecture_changes_allowed'] = bool(
        state['architecture_preflight'].get('architecture_changes_allowed')
    )
    state['cycles'] += 1

    def checkpoint(parent_sha):
        require_clean_patch_workspace(root)
        write_project_context(root, req, state)
        return github.publish(branch, parent_sha, root, state)

    try:
        for role in ('product', 'design'):
            if role not in state:
                result = checkpointed_ask(model, role, context(req, state, root), namespace='preview-' + role)
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
            implementation_context = context(req, state, root)
            patch = checkpointed_ask(model, 'implementation', implementation_context, namespace='preview-implementation')
            try:
                enforce_architecture_change_guard(
                    patch,
                    engine='flutter',
                    architecture_changes_allowed=bool(
                        state.get('architecture_autonomy_policy', {}).get('architecture_changes_allowed', True)
                    ),
                    root=root,
                )
            except ArchitectureChangeBlocked as exc:
                origin_identity = str(
                    getattr(model, 'providers_used', {}).get('implementation')
                    or getattr(model, 'models_used', {}).get('implementation')
                    or 'unknown'
                )
                event = {
                    'round': state['rounds'],
                    'role': 'implementation',
                    'status': 'blocked_architecture_change',
                    'detail': str(exc)[:2000],
                }
                state.setdefault('architecture_guard_events', []).append(event)
                rewrite_context = build_architecture_safe_rewrite_context(
                    implementation_context,
                    patch,
                    str(exc),
                    engine='flutter',
                )
                retry_patch = checkpointed_ask(
                    model,
                    'implementation',
                    rewrite_context,
                    namespace='preview-implementation-safe-rewrite',
                )
                try:
                    enforce_architecture_change_guard(
                        retry_patch,
                        engine='flutter',
                        architecture_changes_allowed=False,
                        root=root,
                    )
                except ArchitectureChangeBlocked as retry_exc:
                    event['safe_rewrite_status'] = 'blocked'
                    event['safe_rewrite_detail'] = str(retry_exc)[:2000]
                    state['status'] = 'architecture_review_hold'
                    state['blockers'] = [str(retry_exc)]
                    parent = checkpoint(parent)
                    continue
                patch = retry_patch
                event['safe_rewrite_status'] = 'accepted'
                event_id = f"{req['id']}:{state['rounds']}:flutter"
                origin_name = origin_identity
                rewrite_name = str(
                    getattr(model, 'providers_used', {}).get('implementation')
                    or getattr(model, 'models_used', {}).get('implementation')
                    or 'unknown'
                )
                record_safe_rewrite_attempt(
                    safe_rewrite_learning_path,
                    event_id=event_id,
                    engine='flutter',
                    origin_kind='provider',
                    origin_name=origin_name,
                    rewrite_kind='provider',
                    rewrite_name=rewrite_name,
                    guard_passed=True,
                )
                event['learning_event_id'] = event_id
                state['pending_safe_rewrite_event_id'] = event_id
                state['status'] = 'working'
                state['blockers'] = []
            apply_patch(root, patch)
            if not any(not p.name.startswith('__studio') for p in (root / 'test').rglob('*_test.dart')):
                qa_patch = checkpointed_ask(model, 'tests', context(req, state, root), namespace='preview-tests')
                enforce_architecture_change_guard(
                    qa_patch,
                    engine='flutter',
                    architecture_changes_allowed=bool(
                        state.get('architecture_autonomy_policy', {}).get('architecture_changes_allowed', True)
                    ),
                    root=root,
                )
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
                pending_safe_rewrite = state.pop('pending_safe_rewrite_event_id', None)
                if pending_safe_rewrite:
                    finalize_safe_rewrite(
                        safe_rewrite_learning_path,
                        event_id=pending_safe_rewrite,
                        verification_passed=False,
                        review_passed=None,
                    )
                    state['safe_rewrite_learning'] = summarize_safe_rewrite_learning(safe_rewrite_learning_path)
                state['blockers'] = ['Validation failed: ' + canonical(logs[-1:])[-16000:]]
                state['repair_plan'] = preview_plan('preview_validation', state['blockers'])
                enqueue(state, state['repair_plan'], estimated_model_calls=1)
                state['repair_queue_summary'] = summarize(state)
                parent = checkpoint(parent)
                continue
            state['validation_contract'] = 2
            review = verdict(checkpointed_ask(model, 'review', context(req, state, root), namespace='preview-review'))
            state['code_review'] = review
            if not review['passed']:
                pending_safe_rewrite = state.pop('pending_safe_rewrite_event_id', None)
                if pending_safe_rewrite:
                    finalize_safe_rewrite(
                        safe_rewrite_learning_path,
                        event_id=pending_safe_rewrite,
                        verification_passed=True,
                        review_passed=False,
                    )
                    state['safe_rewrite_learning'] = summarize_safe_rewrite_learning(safe_rewrite_learning_path)
                state['blockers'] = review['blockers']
                state['repair_plan'] = preview_plan('code_review', state['blockers'])
                enqueue(state, state['repair_plan'], estimated_model_calls=1)
                state['repair_queue_summary'] = summarize(state)
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
                result = verdict(checkpointed_ask(model, 'visual', canonical({'brief': req['brief'], 'design': state['design'],
                    'screen': screen, 'journeys': journeys}), batch, namespace='preview-visual'))
                state['visual_reviews'][screen] = result
                visual['blockers'].extend(screen + ': ' + item for item in result['blockers'])
            visual['passed'] = not visual['blockers']
            state['visual_review'] = visual
            if not visual['passed']:
                state['blockers'] = visual['blockers']
                state['repair_plan'] = preview_plan('visual_review', state['blockers'])
                enqueue(state, state['repair_plan'], estimated_model_calls=1)
                state['repair_queue_summary'] = summarize(state)
                parent = checkpoint(parent)
                continue
            pending_safe_rewrite = state.pop('pending_safe_rewrite_event_id', None)
            if pending_safe_rewrite:
                finalize_safe_rewrite(
                    safe_rewrite_learning_path,
                    event_id=pending_safe_rewrite,
                    verification_passed=True,
                    review_passed=True,
                )
                state['safe_rewrite_learning'] = summarize_safe_rewrite_learning(safe_rewrite_learning_path)
            state.update(status='validated_preview', blockers=[])
            state['repair_plan'] = preview_plan('preview', [])
            for completed_stage in ('preview_validation', 'code_review', 'visual_review'):
                complete_stage_tasks(state, completed_stage)
            state['repair_queue_summary'] = summarize(state)
            break
    except StudioError as e:
        state.update(status='blocked', blockers=[str(e)])

    effective_model_calls = max(0, int(model.calls) - int(getattr(model, 'checkpoint_replays', 0)))
    state['model_calls_this_cycle'] = effective_model_calls
    state['checkpoint_replays_this_cycle'] = int(getattr(model, 'checkpoint_replays', 0))
    record_calls(state, effective_model_calls)
    state['project_budget_status'] = budget_status(state)
    state['models_used'] = getattr(model, 'models_used', {})
    state['providers_used'] = getattr(model, 'providers_used', {})
    state['limits'] = {'max_cycles': req['max_cycles'], 'max_calls_per_cycle': req['max_calls'], 'max_rounds_per_cycle': req['max_rounds']}
    state['release_status'] = 'not_store_ready'
    state['coverage'] = {'variants_per_path': 4, 'journeys': [j['id'] for j in state.get('product', {}).get('journeys', [])], 'scope': 'Initial screen and final screen of each declared journey; not all possible states or real-device testing.'}
    for p in (root / 'test/goldens').glob('*.png'):
        shutil.copyfile(p, out / p.name)
    apk = root / 'build/app/outputs/flutter-apk/app-debug.apk'
    if state['status'] in ('validated_preview', 'awaiting_visual_review') and apk.is_file():
        shutil.copyfile(apk, out / 'app-debug.apk')
        state['apk_sha256'] = hashlib.sha256(apk.read_bytes()).hexdigest()
    state["architecture_evaluation"] = write_architecture_evaluation(
        state.get("architecture_decision", {}),
        state,
        out,
    )
    state["architecture_benchmark"] = write_architecture_benchmark(
        state.get("architecture_decision", {}),
        state.get("architecture_evaluation", {}),
        state.get("technical_recommendations", {}),
        out,
    )
    write_architecture_outcome(state, out)
    learning_root = architecture_learning_root(out)
    try:
        state["architecture_learning"] = write_architecture_learning(learning_root)
    except OSError:
        state["architecture_learning"] = {"status": "unavailable"}

    sha = checkpoint(parent)
    state['checkpoint_commit'] = sha
    atomic_write_text(out / 'report.json', canonical(state))
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
        atomic_write_text(Path(args.out) / 'error.json', canonical({'status': 'blocked', 'error': type(e).__name__, 'detail': str(e) if isinstance(e, StudioError) else 'Invalid configuration or local IO failure'}))
        print('Studio blocked; see error.json and existing checkpoint.', file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())

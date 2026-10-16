"""Resumable model-driven preview cycle for an existing Godot repository.

The runner checkpoints only to studio/<request-id>. It never updates the target default
branch and never claims Android export, device QA, visual QA or journey execution.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
from pathlib import Path

from core import StudioError, canonical, request_check, verdict
from atomic_file import write_text as atomic_write_text
from engine_patch import SECRET, validate as validate_patch
from existing_project import ExistingProjectError, materialize, plan
from godot_model import GodotModel
from godot_session import GodotSandbox
from journeys import validate_journeys
from project_engine import editable, restorable
from project_recommendations import recommend
from architecture_planner import write as write_architecture_plan
from architecture_learning import (
    summarize as summarize_architecture_learning,
    write as write_architecture_learning,
    root_for_output as architecture_learning_root,
)
from architecture_evaluator import write as write_architecture_evaluation
from architecture_benchmark import write as write_architecture_benchmark
from architecture_preflight import write as write_architecture_preflight
from architecture_change_guard import enforce as enforce_architecture_change_guard, ArchitectureChangeBlocked
from architecture_safe_rewrite import build_context as build_architecture_safe_rewrite_context
from safe_rewrite_learning import (
    record_attempt as record_safe_rewrite_attempt,
    finalize as finalize_safe_rewrite,
    summarize as summarize_safe_rewrite_learning,
)
from architecture_outcome import write as write_architecture_outcome

MAX_PUBLISH_FILE_BYTES = 1_000_000


def _safe_apply(
    root: Path,
    value: dict,
    role: str,
    *,
    architecture_changes_allowed: bool = True,
    excerpted_paths: tuple[str, ...] = (),
) -> None:
    # No full overwrite is safe when the model saw only selected excerpts.
    if isinstance(value, dict) and set(value) == {'files'} and excerpted_paths:
        if any(isinstance(item, dict) and item.get('path') in excerpted_paths
               for item in value.get('files', ())):
            raise StudioError('Godot excerpted source requires exact edits, not a full-file rewrite')
    # Aider-style small edits: validate before any write, then expand
    # uniquely matched on-disk snippets into the existing full-file safety
    # contract. Never trust excerpts or model-provided source as authority.
    if isinstance(value, dict) and set(value) == {'edits'}:
        edits = validate_patch(value, 'godot', role)
        root = root.resolve()
        expanded = []
        for item in edits:
            raw_target = root / item['path']
            cursor = raw_target
            while cursor != root:
                if cursor.is_symlink():
                    raise StudioError('Godot exact edit crossed symlink')
                cursor = cursor.parent
            target = raw_target.resolve()
            if not target.is_relative_to(root) or not target.is_file():
                raise StudioError('Godot exact edit requires an existing workspace file')
            try:
                if target.stat().st_size > 600_000:
                    raise StudioError('Godot exact edit source exceeds size limit')
                original = target.read_text(encoding='utf-8')
            except (OSError, UnicodeError):
                raise StudioError('Godot exact edit source is unreadable') from None
            if original.count(item['find']) != 1:
                raise StudioError('Godot exact edit expected exactly one source match')
            revised = original.replace(item['find'], item['replace'], 1)
            if revised == original or not revised:
                raise StudioError('Godot exact edit must preserve nonempty changed source')
            expanded.append({'path': item['path'], 'content': revised})
        value = {'files': expanded}
    enforce_architecture_change_guard(
        value,
        engine='godot',
        architecture_changes_allowed=architecture_changes_allowed,
        root=root,
    )
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


# Planning needs architecture and a representative source sample, not a full
# replay of every script. Implementation, QA and review still get exact files.
PLANNING_SOURCE_CHAR_BUDGET = 6_000
PLANNING_PER_FILE_CHAR_BUDGET = 3_500
PLANNING_FILE_PREVIEW_LIMIT = 6
PLANNING_MANIFEST_LIMIT = 48

# Large existing projects should be edited by exact source snippets, not
# regenerated wholesale. This budget is independent of model token counters.
COMPACT_SOURCE_THRESHOLD = 18_000
COMPACT_SOURCE_CHAR_BUDGET = 10_000
COMPACT_PER_FILE_CHAR_BUDGET = 7_000
COMPACT_SOURCE_FILE_LIMIT = 8


def _relevant_source_excerpt(source: str, brief: str, limit: int, *, planning: bool = False) -> str:
    if len(source) <= limit:
        return source
    # Prefer exact code identifiers explicitly mentioned in the task,
    # e.g. settings_open and _unhandled_input. Never synthesize source.
    identifiers = sorted(set(re.findall(r'[A-Za-z_][A-Za-z0-9_]{4,}', brief)),
                         key=lambda value: (-len(value), value))
    identifiers = [value.lower() for value in identifiers if '_' in value][:16]
    lines = source.splitlines(keepends=True)
    prefix = source[:min(1400, max(300, limit // 4))]
    chunks = [prefix]
    room = max(0, limit - len(prefix) - 120)
    anchors = []
    for i, line in enumerate(lines):
        lowered = line.lower()
        matching = [term for term in identifiers if term in lowered]
        if matching:
            score = 100 * len(matching) + sum(len(term) for term in matching)
            anchors.append((-score, i))
    # Without explicit identifiers, include representative function definitions.
    if not anchors:
        anchors = [(0, i) for i, line in enumerate(lines) if line.lstrip().startswith('func ')]
    seen = set()
    for _, index in sorted(anchors):
        start, end = max(0, index - 5), min(len(lines), index + 11)
        if any(i in seen for i in range(start, end)):
            continue
        chunk = ''.join(lines[start:end])
        if len(chunk) > room:
            continue
        chunks.append(chunk)
        seen.update(range(start, end))
        room -= len(chunk) + 42
        if room <= 0:
            break
    omitted = '[OMITTED SOURCE - planning excerpt only]' if planning else '[OMITTED SOURCE - EXACT EDITS ONLY]'
    truncated = '[TRUNCATED: planning excerpt only]' if planning else '[TRUNCATED SOURCE - EXACT EDITS ONLY]'
    return ('\n' + omitted + '\n').join(chunks)[:limit] + '\n' + truncated


def _review_evidence(patch: dict | None, root: Path) -> list[dict]:
    """Bounded, source-backed evidence of the accepted implementation patch.

    The model sees exact changed snippets plus the current source checksum,
    not a synthetic claim that the whole source has been independently read.
    All candidate patches pass _safe_apply before this helper is called.
    """
    if not isinstance(patch, dict):
        return []
    kind = 'edits' if set(patch) == {'edits'} else 'files' if set(patch) == {'files'} else ''
    entries = patch.get(kind) if kind else None
    if not isinstance(entries, list):
        return []
    result = []
    remaining = 9_000
    for item in entries[:12]:
        if not isinstance(item, dict):
            continue
        rel = item.get('path')
        if not isinstance(rel, str) or not editable(rel, 'godot'):
            continue
        source_path = root / rel
        if not source_path.is_file() or source_path.is_symlink():
            continue
        try:
            current = source_path.read_bytes()
        except OSError:
            continue
        row = {
            'path': rel,
            'current_source_sha256': hashlib.sha256(current).hexdigest(),
            'source_size_bytes': len(current),
            'change_kind': 'exact_edit' if kind == 'edits' else 'complete_file',
        }
        if kind == 'edits':
            before = item.get('find')
            after = item.get('replace')
            if not isinstance(before, str) or not isinstance(after, str):
                continue
            row['before'] = before[:min(2_500, remaining // 2)]
            row['after'] = after[:min(2_500, remaining // 2)]
            row['after_present_in_source'] = after.encode('utf-8') in current
            cost = len(row['before']) + len(row['after'])
        else:
            after = item.get('content')
            if not isinstance(after, str):
                continue
            row['source_excerpt'] = after[:min(3_000, remaining)]
            row['source_excerpt_truncated'] = len(after) > len(row['source_excerpt'])
            cost = len(row['source_excerpt'])
        result.append(row)
        remaining -= cost
        if remaining <= 0:
            break
    return result


def _context(req: dict, state: dict, root: Path, *, phase: str = 'implementation',
             review_patch: dict | None = None, validation_logs: list | None = None) -> str:
    paths = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if editable(rel, 'godot'):
            paths.append((rel, path))

    files = {}
    planning = phase in ('product', 'design')
    compact = (phase in ('implementation', 'tests', 'review') and
               sum(path.stat().st_size for _, path in paths) > COMPACT_SOURCE_THRESHOLD)
    excerpted_paths = []
    if planning:
        # Explicitly distinguish source *excerpts* from the full files used
        # to generate patches. Keeping this manifest lets the planner reason
        # about the actual project structure without consuming its code budget.
        def priority(item):
            rel = item[0]
            if rel == 'project.godot':
                return (0, rel)
            if rel == 'scripts/main.gd':
                return (1, rel)
            if rel.endswith('.tscn'):
                return (2, rel)
            if rel.endswith('.gd'):
                return (3, rel)
            return (4, rel)

        remaining = PLANNING_SOURCE_CHAR_BUDGET
        for rel, path in sorted(paths, key=priority):
            if not remaining or len(files) >= PLANNING_FILE_PREVIEW_LIMIT:
                break
            limit = min(PLANNING_PER_FILE_CHAR_BUDGET, remaining)
            # Retain task-relevant function bodies even when they occur far
            # below the beginning of a large gameplay script. These are
            # labelled partial excerpts, never authoritative full source.
            with path.open('r', encoding='utf-8') as source:
                sample = source.read()
            truncated = len(sample) > limit
            files[rel] = (
                _relevant_source_excerpt(sample, req.get('brief', ''), limit, planning=True)
                if truncated else sample
            )
            remaining -= min(limit, len(sample))
    elif compact:
        # Exact-match edits are revalidated on full trusted files at apply
        # time. Truncated input is NEVER permission to overwrite whole files.
        def source_priority(item):
            rel = item[0]
            return (0 if rel == 'scripts/main.gd' else
                    1 if rel == 'project.godot' else
                    2 if rel.endswith('.gd') else
                    3 if rel.endswith('.tscn') else 4, rel)

        remaining = COMPACT_SOURCE_CHAR_BUDGET
        for rel, path in sorted(paths, key=source_priority):
            if remaining <= 0 or len(files) >= COMPACT_SOURCE_FILE_LIMIT:
                excerpted_paths.append(rel)
                continue
            limit = min(COMPACT_PER_FILE_CHAR_BUDGET, remaining)
            source = path.read_text(encoding='utf-8')
            if len(source) > limit:
                files[rel] = _relevant_source_excerpt(source, req.get('brief', ''), limit)
                excerpted_paths.append(rel)
            else:
                files[rel] = source
            remaining -= min(len(source), limit)
    else:
        # Full source is retained for review and for small projects.
        for rel, path in paths:
            files[rel] = path.read_text()

    context = {
        'engine':'godot',
        'request':req,
        'product':state.get('product'),
        'design':state.get('design'),
        'previous_blockers':state.get('blockers',[]),
        'architecture_decision':state.get('architecture_decision', {'status':'unavailable','chosen':[]}),
        'architecture_autonomy_policy':state.get('architecture_autonomy_policy', {}),
        'architecture_preflight':state.get('architecture_preflight', {'status':'unavailable','verdict':'unknown'}),
        'architecture_benchmark':state.get('architecture_benchmark', {'status':'unavailable','migration_candidates':[]}),
        'files':files,
    }
    if planning:
        # The #36 canary spent 28,101 *input* tokens across only four
        # product-stage calls. Do not send full architecture telemetry,
        # entire request control data or verbose product deliverables to
        # preliminary planning. Preserve the complete trusted state for
        # implementation, QA, checkpoints and downstream validation.
        minimal_request = {
            key: req.get(key)
            for key in ('app_name', 'target_repo', 'brief')
            if req.get(key) is not None
        }
        compact_architecture = {
            'framework': 'godot',
            'architecture_changes_allowed': state.get(
                'architecture_autonomy_policy', {}
            ).get('architecture_changes_allowed'),
            'preflight_verdict': state.get('architecture_preflight', {}).get('verdict'),
        }
        lean = {
            'engine': 'godot',
            'phase': phase,
            'request': minimal_request,
            'architecture_constraints': compact_architecture,
            'files_mode': 'bounded_planning_excerpts_not_complete_source',
            'files': files,
            'editable_file_count': len(paths),
            'editable_file_manifest': [
                {'path': rel, 'size_bytes': path.stat().st_size}
                for rel, path in paths[:PLANNING_MANIFEST_LIMIT]
            ],
            'manifest_omitted_count': max(0, len(paths) - PLANNING_MANIFEST_LIMIT),
        }
        if phase == 'design':
            product = state.get('product')
            if isinstance(product, dict):
                criteria = product.get('acceptance_criteria')
                if not isinstance(criteria, list):
                    deliverable = product.get('deliverable')
                    criteria = deliverable.get('acceptance_criteria') if isinstance(deliverable, dict) else []
                if not isinstance(criteria, list):
                    criteria = []
                journeys = product.get('journeys')
                if not isinstance(journeys, list):
                    journeys = []
                compact_product = {
                    'acceptance_criteria': [
                        item[:180] for item in (criteria or [])[:4]
                        if isinstance(item, str)
                    ],
                    'journeys': [
                        {
                            'id': journey.get('id'),
                            'steps': journey.get('steps', [])[:4],
                        }
                        for journey in journeys[:3]
                        if isinstance(journey, dict)
                        and isinstance(journey.get('steps'), list)
                    ],
                }
                lean['product'] = compact_product
        return canonical(lean)
    if compact and phase in ('implementation', 'tests'):
        # Large-project code and QA prompts should NOT replay full architecture
        # telemetry or product/design narratives. These are checkpoint evidence
        # validated by trusted architecture guards, not source-edit authority.
        product = state.get('product')
        if not isinstance(product, dict):
            product = {}
        criteria = product.get('acceptance_criteria')
        if not isinstance(criteria, list):
            deliverable = product.get('deliverable')
            criteria = deliverable.get('acceptance_criteria') if isinstance(deliverable, dict) else []
        if not isinstance(criteria, list):
            criteria = []
        journeys = product.get('journeys')
        if not isinstance(journeys, list):
            journeys = []
        # Preserve EVERY journey step: these are the testable selectors the
        # implementation must honor. Only long prose summaries are trimmed.
        criteria = [str(value)[:240] for value in criteria[:8] if isinstance(value, str)]
        design = state.get('design')
        design_text = canonical(design) if isinstance(design, dict) else ''
        brief = str(req.get('brief') or '')
        blockers = state.get('blockers')
        blockers = blockers if isinstance(blockers, list) else []
        lean = {
            'engine': 'godot',
            'phase': phase,
            'request': {
                key: req[key] for key in ('app_name', 'target_repo', 'brief')
                if key in req
            },
            'architecture_constraints': {
                'architecture_changes_allowed': state.get(
                    'architecture_autonomy_policy', {}
                ).get('architecture_changes_allowed'),
                'preflight_verdict': state.get(
                    'architecture_preflight', {}
                ).get('verdict'),
            },
            'acceptance': {
                'criteria': criteria,
                'journeys': journeys,
            },
            'design_guidance_excerpt': design_text[:1_000],
            'design_excerpt_truncated': len(design_text) > 1_000,
            'previous_blockers': [
                value[:200] for value in blockers[:3]
                if isinstance(value, str)
            ],
            'files': files,
            'files_mode': 'bounded_exact_match_source_excerpts',
            'excerpted_paths': excerpted_paths,
            'editable_file_count': len(paths),
            'editable_file_manifest': [
                {'path': rel, 'size_bytes': path.stat().st_size}
                for rel, path in paths[:PLANNING_MANIFEST_LIMIT]
            ],
            'manifest_omitted_count': max(0, len(paths) - PLANNING_MANIFEST_LIMIT),
        }
        if phase == 'tests':
            # QA sees just the trusted accepted code change, not the complete
            # generation history or unchecked model explanation.
            evidence = _review_evidence(review_patch, root)
            lean['accepted_change_evidence'] = [
                {key: (value[:850] if isinstance(value, str) else value)
                 for key, value in row.items()
                 if key in ('path', 'change_kind', 'before', 'after',
                            'source_excerpt', 'current_source_sha256')}
                for row in evidence[:2]
            ]
            lean['qa_scope'] = (
                'Return a complete tests/*.gd file covering the supplied '
                'accepted code change. Do not modify production files.'
            )
        return canonical(lean)
    if compact:
        context['files_mode'] = (
            'bounded_review_source_excerpts' if phase == 'review'
            else 'bounded_exact_match_source_excerpts'
        )
        context['excerpted_paths'] = excerpted_paths
        context['editable_file_manifest'] = [
            {'path': rel, 'size_bytes': path.stat().st_size}
            for rel, path in paths[:PLANNING_MANIFEST_LIMIT]
        ]
        context['manifest_omitted_count'] = max(0, len(paths) - PLANNING_MANIFEST_LIMIT)
    if phase == 'review' and compact:
        context['accepted_change_evidence'] = _review_evidence(review_patch, root)
        if validation_logs is not None:
            report = canonical(validation_logs)
            context['trusted_validation_excerpt'] = report[:2_000]
            context['validation_excerpt_truncated'] = len(report) > 2_000
        context['review_scope'] = (
            'Review the accepted changed snippets, surrounding authentic source excerpts '
            'and trusted headless validation. This is bounded review input, not complete project source. '
            'Reject suspicious or insufficient evidence; never claim full-file inspection.'
        )
    return canonical(context)

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
    state['publication_request'] = dict(req.get('play_publish', {'enabled':False,'track':'internal','commit':False}))
    if state.get('engine') != 'godot':
        raise StudioError('Checkpoint engine mismatch')
    state['target_repo'] = req['target_repo']
    if resumed:
        # The restored branch head is the authoritative committed checkpoint.
        # Stored state precedes its publication, so it may lack this SHA.
        state['checkpoint_commit'] = parent
    if state['status'] != 'godot_preview_validated' and state['cycles'] >= req['max_cycles']:
        state.update(status='blocked', preview_cycle_budget_exhausted=True)
        state['completion'] = {'finished': False, 'next_stage': 'godot_preview_cycle_budget_exhausted'}
    if state['status'] == 'godot_preview_validated' or state.get('preview_cycle_budget_exhausted') is True:
        atomic_write_text(out / 'report.json', canonical(state)); return state

    architecture_recommendations = recommend(
        'planning',
        out,
        context_text=req.get('brief'),
    )
    architecture_root = architecture_learning_root(out)
    historical_learning = summarize_architecture_learning(architecture_root)
    safe_rewrite_learning_path = out / '.autonomy' / 'safe-rewrite-learning.json'
    state['architecture_recommendations'] = architecture_recommendations
    state['architecture_decision'] = write_architecture_plan(
        req,
        architecture_recommendations,
        out,
        learning=historical_learning,
        framework='godot',
        publication_target='google-play',
    )
    state['architecture_autonomy_policy'] = state['architecture_decision'].get('autonomy_policy', {})
    state['architecture_preflight'] = write_architecture_preflight(
        state['architecture_decision'],
        architecture_recommendations,
        out,
    )
    state['architecture_autonomy_policy']['architecture_changes_allowed'] = bool(
        state['architecture_preflight'].get('architecture_changes_allowed')
    )

    model = model_factory(req['max_calls']); sandbox = sandbox_factory(root); sandbox.create(req['app_name'])
    state['cycles'] += 1

    def checkpoint() -> None:
        nonlocal parent
        parent = _publish(github, branch, parent, root, state)

    try:
        for role in ('product','design'):
            if role not in state:
                result = model.ask(role, _context(req,state,root,phase=role))
                if role == 'product':
                    try: validate_journeys(result.get('journeys'))
                    except ValueError as exc: raise StudioError(str(exc)) from None
                state[role] = result; state['status'] = role + '_complete'; checkpoint()
        for _ in range(req['max_rounds']):
            state['rounds'] += 1
            implementation_context = _context(req,state,root)
            excerpted_paths = tuple(json.loads(implementation_context).get('excerpted_paths', ()))
            patch = model.ask('implementation', implementation_context)
            try:
                _safe_apply(
                    root,
                    patch,
                    'implementation',
                    architecture_changes_allowed=bool(
                        state.get('architecture_autonomy_policy', {}).get('architecture_changes_allowed', True)
                    ),
                    excerpted_paths=excerpted_paths,
                )
            except ArchitectureChangeBlocked as exc:
                event = {
                    'round': state['rounds'],
                    'role': 'implementation',
                    'status': 'blocked_architecture_change',
                    'detail': str(exc)[:2000],
                }
                state.setdefault('architecture_guard_events', []).append(event)
                retry_patch = model.ask(
                    'implementation',
                    build_architecture_safe_rewrite_context(
                        implementation_context,
                        patch,
                        str(exc),
                        engine='godot',
                    ),
                )
                try:
                    _safe_apply(
                        root,
                        retry_patch,
                        'implementation',
                        architecture_changes_allowed=False,
                        excerpted_paths=excerpted_paths,
                    )
                except ArchitectureChangeBlocked as retry_exc:
                    event['safe_rewrite_status'] = 'blocked'
                    event['safe_rewrite_detail'] = str(retry_exc)[:2000]
                    state.update(status='architecture_review_hold', blockers=[str(retry_exc)])
                    checkpoint()
                    continue
                patch = retry_patch
                event['safe_rewrite_status'] = 'accepted'
                event_id = f"{req['id']}:{state['rounds']}:godot"
                model_name = str(getattr(model, 'models_used', {}).get('implementation') or 'unknown')
                record_safe_rewrite_attempt(
                    safe_rewrite_learning_path,
                    event_id=event_id,
                    engine='godot',
                    origin_kind='model',
                    origin_name=model_name,
                    rewrite_kind='model',
                    rewrite_name=model_name,
                    guard_passed=True,
                )
                event['learning_event_id'] = event_id
                state['pending_safe_rewrite_event_id'] = event_id
                state.update(status='working', blockers=[])
            if not any(p.is_file() and not p.is_symlink() for p in (root / 'tests').rglob('*.gd')):
                qa = model.ask('tests', _context(req,state,root,phase='tests',review_patch=patch)); _safe_apply(
                    root,
                    qa,
                    'tests',
                    architecture_changes_allowed=bool(
                        state.get('architecture_autonomy_policy', {}).get('architecture_changes_allowed', True)
                    ),
                )
            if not any(p.is_file() and not p.is_symlink() for p in (root / 'tests').rglob('*.gd')):
                raise StudioError('Godot QA must supply tests/*.gd')
            try: journeys = validate_journeys(state['product'].get('journeys'))
            except ValueError as exc: raise StudioError(str(exc)) from None
            passed, logs = sandbox.gates(req['app_name'], journeys)
            atomic_write_text(out / 'validation.json', canonical(logs))
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
                state.update(status='repair_needed',blockers=['Godot headless validation failed: ' + canonical(logs[-1:])[-16000:]])
                checkpoint(); continue
            review_context = _context(req, state, root, phase='review', review_patch=patch, validation_logs=logs)
            review = verdict(model.ask('review', review_context)); state['code_review'] = review
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
                state.update(status='repair_needed',blockers=review['blockers']); checkpoint(); continue
            pending_safe_rewrite = state.pop('pending_safe_rewrite_event_id', None)
            if pending_safe_rewrite:
                finalize_safe_rewrite(
                    safe_rewrite_learning_path,
                    event_id=pending_safe_rewrite,
                    verification_passed=True,
                    review_passed=True,
                )
                state['safe_rewrite_learning'] = summarize_safe_rewrite_learning(safe_rewrite_learning_path)
            state.update(status='godot_preview_validated',blockers=[],validation_contract='godot-headless-v1')
            state['completion'] = {'finished':False,'next_stage':'godot_android_export_qa',
                                   'reason':'Headless Godot validation passed; Android export/device/visual journey evidence still required.'}
            break
    except StudioError as exc:
        state.update(status='blocked',blockers=[str(exc)])
    finally:
        state['model_calls_this_cycle'] = model.calls
        state['checkpoint_replays_this_cycle'] = 0
        state['models_used'] = getattr(model,'models_used',{})
        state['release_status'] = 'not_store_ready'
        state['coverage'] = {'engine':'godot','headless_import':True,'journeys_executed':False,
                             'android_export':False,'device_qa':False,'visual_qa':False}
        state['architecture_evaluation'] = write_architecture_evaluation(
            state.get('architecture_decision', {}),
            state,
            out,
        )
        state['architecture_benchmark'] = write_architecture_benchmark(
            state.get('architecture_decision', {}),
            state.get('architecture_evaluation', {}),
            state.get('architecture_recommendations', {}),
            out,
        )
        write_architecture_outcome(state, out)
        try:
            state['architecture_learning'] = write_architecture_learning(architecture_root)
        except OSError:
            state['architecture_learning'] = {'status':'unavailable'}

        atomic_write_text(out / 'report.json', canonical(state))
        checkpoint(); state['checkpoint_commit'] = parent
        atomic_write_text(out / 'report.json', canonical(state))
    return state

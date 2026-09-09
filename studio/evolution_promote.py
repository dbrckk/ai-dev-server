"""Trusted publication step for an approved autonomous factory evolution.

This module runs only after isolated benchmark approval. It never executes candidate
code. It reconstructs the exact validated candidate on the pinned baseline, applies
one deterministic trusted registry insertion, creates an `evolution/<candidate>`
branch and opens a PR. It never writes directly to main and refuses stale baselines.
"""
from __future__ import annotations

import base64
import os
import re

from core import API, StudioError
from evolution_candidate import expected_paths


class PromotionError(StudioError):
    pass


class ControlGitHub(API):
    def __init__(self, repository: str, token: str | None = None):
        if not isinstance(repository, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise PromotionError('Control repository invalid')
        super().__init__('https://api.github.com', token if token is not None else os.environ.get('STUDIO_GITHUB_TOKEN', ''))
        if not self.key:
            raise PromotionError('Missing STUDIO_GITHUB_TOKEN for trusted promotion')
        self.repo = '/repos/' + repository

    def get(self, path: str):
        return self.call('GET', self.repo + path)

    def post(self, path: str, data: dict):
        return self.call('POST', self.repo + path, data)


def _approved(work_order: dict, validated_candidate: dict, promotion: dict) -> tuple[str, str, str]:
    if not isinstance(work_order, dict) or work_order.get('status') != 'candidate_planned':
        raise PromotionError('Promotion requires planned work order')
    if not isinstance(validated_candidate, dict) or validated_candidate.get('status') != 'candidate_validated':
        raise PromotionError('Promotion requires validated candidate')
    if not isinstance(promotion, dict) or promotion.get('status') != 'promotion_approved' or promotion.get('promotion_decision') != 'approve':
        raise PromotionError('Promotion decision is not approved')
    candidate_id = work_order.get('candidate_id')
    baseline = work_order.get('baseline_sha')
    gap = (work_order.get('primary_gap') or {}).get('value')
    if not isinstance(candidate_id, str) or validated_candidate.get('candidate_id') != candidate_id or promotion.get('candidate_id') != candidate_id:
        raise PromotionError('Promotion candidate identity mismatch')
    if not isinstance(baseline, str) or not re.fullmatch(r'[0-9a-f]{40}', baseline) or promotion.get('baseline_sha') != baseline:
        raise PromotionError('Promotion baseline identity mismatch')
    if not isinstance(gap, str) or validated_candidate.get('gap') != gap or promotion.get('gap') != gap:
        raise PromotionError('Promotion gap identity mismatch')
    branch = work_order.get('candidate_branch')
    expected_branch = 'evolution/' + candidate_id
    if branch != expected_branch or validated_candidate.get('candidate_branch') != expected_branch:
        raise PromotionError('Promotion branch identity mismatch')
    return baseline, gap, expected_branch


def registry_update(content: str, gap: str) -> str:
    if not isinstance(content, str) or not re.fullmatch(r'[a-z][a-z0-9_]{2,48}_qa', gap):
        raise PromotionError('Registry promotion input invalid')
    if f"'{gap}': Stage(" in content:
        raise PromotionError('Stage is already registered')
    marker = '}\n\n\ndef get_stage'
    if content.count(marker) != 1 or 'STAGES = {\n' not in content:
        raise PromotionError('Trusted stage registry shape changed; re-review required')
    base = gap[:-3]
    line = f"    '{gap}': Stage('{gap}', 'studio/{base}_stage.py', 'deferred_{base}', '{base}_failed'),\n"
    index = content.index(marker)
    return content[:index] + line + content[index:]


def _registry_at(github: ControlGitHub, baseline: str) -> tuple[str, str]:
    commit = github.get('/git/commits/' + baseline)
    tree_sha = commit.get('tree', {}).get('sha')
    if not isinstance(tree_sha, str):
        raise PromotionError('Baseline tree unavailable')
    tree = github.get('/git/trees/' + tree_sha + '?recursive=1')
    if tree.get('truncated'):
        raise PromotionError('Baseline tree truncated')
    entries = [item for item in tree.get('tree', []) if item.get('path') == 'studio/stage_registry.py' and item.get('type') == 'blob']
    if len(entries) != 1:
        raise PromotionError('Trusted stage registry missing')
    blob = github.get('/git/blobs/' + entries[0]['sha'])
    try:
        content = base64.b64decode(blob['content']).decode('utf-8')
    except (KeyError, ValueError, UnicodeError):
        raise PromotionError('Trusted stage registry blob invalid') from None
    return tree_sha, content


def publish(work_order: dict, validated_candidate: dict, promotion: dict,
            repository: str | None = None, github: ControlGitHub | None = None) -> dict:
    baseline, gap, branch = _approved(work_order, validated_candidate, promotion)
    repository = repository or os.environ.get('GITHUB_REPOSITORY', '')
    github = github or ControlGitHub(repository)

    metadata = github.get('')
    if metadata.get('default_branch') != 'main' or metadata.get('archived'):
        raise PromotionError('Control repository must be active with main as default branch')
    current_main = github.get('/branches/main').get('commit', {}).get('sha')
    if current_main != baseline:
        raise PromotionError('Promotion baseline is stale; rebenchmark against current main')

    expected = set(expected_paths(gap).values())
    files = validated_candidate.get('files')
    if not isinstance(files, list) or {item.get('path') for item in files if isinstance(item, dict)} != expected:
        raise PromotionError('Validated candidate file set changed')

    refs = github.get('/git/matching-refs/heads/' + branch)
    if any(item.get('ref') == 'refs/heads/' + branch for item in refs if isinstance(item, dict)):
        raise PromotionError('Evolution branch already exists; refusing overwrite')

    base_tree, registry = _registry_at(github, baseline)
    promoted_registry = registry_update(registry, gap)
    tree_entries = [
        {'path': item['path'], 'mode': '100644', 'type': 'blob', 'content': item['content']}
        for item in sorted(files, key=lambda item: item['path'])
    ]
    tree_entries.append({'path': 'studio/stage_registry.py', 'mode': '100644', 'type': 'blob', 'content': promoted_registry})
    tree = github.post('/git/trees', {'base_tree': base_tree, 'tree': tree_entries})
    commit = github.post('/git/commits', {
        'message': 'Promote validated factory capability: ' + gap,
        'tree': tree['sha'],
        'parents': [baseline],
    })
    promoted_sha = commit.get('sha')
    if not isinstance(promoted_sha, str) or not re.fullmatch(r'[0-9a-f]{40}', promoted_sha):
        raise PromotionError('GitHub returned invalid promotion commit')
    github.post('/git/refs', {'ref': 'refs/heads/' + branch, 'sha': promoted_sha})
    pr = github.post('/pulls', {
        'title': 'Promote autonomous factory capability: ' + gap,
        'head': branch,
        'base': 'main',
        'body': (
            'Autonomous evolution candidate approved by the trusted isolated benchmark.\n\n'
            'Candidate: `' + str(work_order.get('candidate_id')) + '`\n'
            'Tested baseline: `' + baseline + '`\n'
            'Tested candidate commit: `' + str(promotion.get('candidate_sha')) + '`\n'
            'Rollback ref: `' + baseline + '`\n\n'
            'This PR adds only the validated capability files plus the deterministic trusted stage-registry entry. '
            'Normal repository CI must pass again before merge.'
        ),
    })
    number = pr.get('number')
    if type(number) is not int or number < 1:
        raise PromotionError('GitHub did not create a promotion PR')
    return {
        'version': 1,
        'status': 'promotion_pr_opened',
        'candidate_id': work_order.get('candidate_id'),
        'gap': gap,
        'branch': branch,
        'baseline_sha': baseline,
        'rollback_ref': baseline,
        'tested_candidate_sha': promotion.get('candidate_sha'),
        'promotion_commit_sha': promoted_sha,
        'pull_request': number,
        'direct_main_write': False,
        'requires_fresh_ci_before_merge': True,
    }

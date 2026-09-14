"""Trusted PROJECT_CONTEXT.md generator for every factory-managed app."""
from __future__ import annotations

from datetime import date
from pathlib import Path

FILE = 'PROJECT_CONTEXT.md'


def _clean_list(value):
    if not isinstance(value, list):
        return []
    return [x.strip() for x in value if isinstance(x, str) and x.strip()]


def _bullets(items, fallback):
    return '\n'.join('- ' + item for item in items) if items else '- ' + fallback


def render(req: dict, state: dict) -> str:
    product = state.get('product') if isinstance(state.get('product'), dict) else {}
    completion = state.get('completion') if isinstance(state.get('completion'), dict) else {}
    evidence = state.get('release_evidence') if isinstance(state.get('release_evidence'), dict) else {}
    capability = evidence.get('capability_qa') if isinstance(evidence.get('capability_qa'), dict) else {}
    journeys = product.get('journeys') if isinstance(product.get('journeys'), list) else []
    journey_ids = [j.get('id') for j in journeys if isinstance(j, dict) and isinstance(j.get('id'), str)]
    acceptance = _clean_list(product.get('acceptance_criteria'))
    assumptions = _clean_list(product.get('assumptions'))
    blockers = _clean_list(completion.get('blockers')) or _clean_list(state.get('blockers'))
    profiles = _clean_list(capability.get('profiles'))
    required = _clean_list(completion.get('required_stages'))
    next_stage = completion.get('next_stage')
    status = state.get('status', 'unknown')
    architecture = state.get('architecture_decision') if isinstance(state.get('architecture_decision'), dict) else {}
    chosen_arch = architecture.get('chosen') if isinstance(architecture.get('chosen'), list) else []
    chosen_repos = [x.get('repo') for x in chosen_arch if isinstance(x, dict) and isinstance(x.get('repo'), str)]
    architecture_eval = state.get('architecture_evaluation') if isinstance(state.get('architecture_evaluation'), dict) else {}
    architecture_verdict = architecture_eval.get('verdict') if isinstance(architecture_eval.get('verdict'), str) else 'not evaluated'
    architecture_benchmark = state.get('architecture_benchmark') if isinstance(state.get('architecture_benchmark'), dict) else {}
    migration_candidates = architecture_benchmark.get('migration_candidates') if isinstance(architecture_benchmark.get('migration_candidates'), list) else []
    migration_repos = [x.get('best_alternative') for x in migration_candidates if isinstance(x, dict) and isinstance(x.get('best_alternative'), str)]
    drift_alerts = state.get('architecture_drift_alerts') if isinstance(state.get('architecture_drift_alerts'), list) else []
    obsolescence = state.get('architecture_obsolescence') if isinstance(state.get('architecture_obsolescence'), dict) else {}
    deprecations = obsolescence.get('deprecation_candidates') if isinstance(obsolescence.get('deprecation_candidates'), list) else []
    deprecation_lines = []
    for item in deprecations[:8]:
        if not isinstance(item, dict) or not isinstance(item.get('repo'), str):
            continue
        replacement = item.get('replacement_candidate')
        suffix = f" -> {replacement}" if isinstance(replacement, str) and replacement else ""
        deprecation_lines.append(f"{item['repo']}{suffix}")
    drift_lines = []
    for item in drift_alerts[:10]:
        if not isinstance(item, dict):
            continue
        if item.get('type') == 'repository' and isinstance(item.get('repo'), str):
            drift_lines.append(f"{item['repo']}: degraded (score={item.get('score')})")
        elif item.get('type') == 'stack' and isinstance(item.get('repos'), list):
            repos = ', '.join(str(x) for x in item.get('repos', [])[:6])
            drift_lines.append(f"{repos}: stack degraded (score={item.get('score')})")

    immediate = (
        f'Execute and validate `{next_stage}`.'
        if isinstance(next_stage, str) and next_stage
        else ('Verify remaining external Play Store/legal prerequisites.' if completion.get('finished')
              else 'Derive and execute the next trusted completion stage.')
    )

    return f'''# {req.get('app_name', 'Mobile app')} — Project Context

> **Read this file first when resuming this project in another ChatGPT conversation or agent session.**
> This is a trusted handoff generated from the factory state. `.studio/state.json` remains the machine authority.

## What this application is

{req.get('brief', '').strip()}

## Product goals and acceptance

{_bullets(acceptance, 'Acceptance criteria have not yet been generated.')}

### Executable user journeys

{_bullets(journey_ids, 'No trusted acceptance journey is recorded yet.')}

## Current scope and architecture

- Stack: Flutter mobile application.
- Primary publication target: Google Play.
- Factory request id: `{req.get('id', 'unknown')}`
- Target repository: `{req.get('target_repo', 'unknown')}`
- Current studio status: `{status}`
- Capability profiles: {', '.join(profiles) if profiles else 'not classified yet'}

### Architecture decision

{_bullets(chosen_repos, 'No architecture recommendation has been selected.')}

Architecture evaluation: `{architecture_verdict}`

Potential migration candidates:

{_bullets(migration_repos, 'No benchmark-backed migration candidate is currently recommended.')}

### Architecture drift alerts

{_bullets(drift_lines, 'No statistically supported architecture degradation is currently detected.')}

### Deprecation candidates

{_bullets(deprecation_lines, 'No evidence-backed deprecation candidate is currently identified.')}

## Current validation / release evidence

Required stages:

{_bullets(required, 'Release stages have not yet been derived.')}

Recorded evidence:

{_bullets(sorted(evidence), 'No release evidence is recorded yet.')}

Next required stage: `{next_stage if isinstance(next_stage, str) and next_stage else 'none / not derived'}`

Do not infer completion from a preview, successful compilation, or this prose file. Completion requires the trusted evidence contract.

## Known blockers, risks and technical debt

{_bullets(blockers, 'No trusted blocker is currently recorded. Future/external requirements may still exist.')}

## Key assumptions / decisions to preserve

{_bullets(assumptions, 'No product assumptions are currently recorded.')}

- Never replace real behavior with placeholders or fake-success paths.
- Never weaken tests, accessibility, privacy, security or completion gates to obtain a green result.
- Missing capabilities must go through the factory adaptation process rather than being silently skipped.

## Immediate next objective

{immediate}

## Near-term roadmap

1. Complete every dynamically required implementation, QA and release stage.
2. Repair functional, visual, accessibility, performance, privacy and security defects discovered by evidence.
3. Produce professional store assets, metadata and consistent privacy/Data Safety material.
4. Validate the actual release artifact on appropriate runtime/device environments.
5. Continue until the machine completion contract passes or a genuinely irreducible external prerequisite is identified.

## Long-term / final objective

Deliver a fully functional, highly polished, maintainable and professionally presented application ready for Google Play publication. The factory owns autonomous iteration and capability adaptation; human intervention is reserved for genuinely external legal, identity, payment or credential actions that cannot safely be automated.

## Resume instructions for a future ChatGPT/agent

1. Read this file and `.studio/state.json` first.
2. Inspect current repository state, CI and evidence rather than trusting an old conversation summary.
3. Preserve the product brief and non-negotiable quality gates.
4. Continue from the immediate next objective by doing implementation work, not only planning.
5. Refresh this file after every material checkpoint.

Last generated: {date.today().isoformat()}
'''


def write(root: Path, req: dict, state: dict) -> Path:
    path = root / FILE
    path.write_text(render(req, state))
    return path

"""Trusted durable handoff document for every factory-managed application."""
from __future__ import annotations

from datetime import date
from pathlib import Path

FILE = 'PROJECT_CONTEXT.md'


def _lines(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [x.strip() for x in value if isinstance(x, str) and x.strip()]


def _bullets(items: list[str], fallback: str) -> str:
    return '\n'.join('- ' + x for x in items) if items else '- ' + fallback


def render(req: dict, state: dict) -> str:
    product = state.get('product', {}) if isinstance(state.get('product'), dict) else {}
    design = state.get('design', {}) if isinstance(state.get('design'), dict) else {}
    completion = state.get('completion', {}) if isinstance(state.get('completion'), dict) else {}
    evidence = state.get('release_evidence', {}) if isinstance(state.get('release_evidence'), dict) else {}
    capability = evidence.get('capability_qa', {}) if isinstance(evidence.get('capability_qa'), dict) else {}
    blockers = _lines(completion.get('blockers'))
    profiles = _lines(capability.get('profiles'))
    stages = _lines(completion.get('required_stages'))
    next_stage = completion.get('next_stage')
    status = state.get('status', 'unknown')
    acceptance = _lines(product.get('acceptance_criteria'))
    assumptions = _lines(product.get('assumptions'))
    journeys = product.get('journeys') if isinstance(product.get('journeys'), list) else []
    journey_ids = [j.get('id') for j in journeys if isinstance(j, dict) and isinstance(j.get('id'), str)]

    return f'''# {req.get("app_name", "Mobile app")} — Project Context

> **Read this file first when resuming this project in another ChatGPT conversation or agent session.**
> This file is generated from trusted studio state. Update it whenever the project materially changes.

## Product summary

{req.get('brief', '').strip()}

## Product goals and acceptance

{_bullets(acceptance, 'Acceptance criteria have not yet been generated.')}

### Executable journeys

{_bullets(journey_ids, 'No trusted acceptance journey is recorded yet.')}

## Current implementation / architecture

- Platform: Flutter mobile application targeting Android and iOS templates; Play Store release is the primary publication target.
- Factory request id: `{req.get('id', 'unknown')}`
- Target repository: `{req.get('target_repo', 'unknown')}`
- Current studio status: `{status}`
- Capability profiles: {', '.join(profiles) if profiles else 'not classified yet'}
- Design specification present: {'yes' if design else 'no'}

## Current validation and release status

Required release/QA stages:

{_bullets(stages, 'Release stages have not yet been derived.')}

Next required stage: `{next_stage if isinstance(next_stage, str) and next_stage else 'none / not derived'}`

Recorded evidence stages:

{_bullets(sorted(evidence), 'No release evidence has been recorded yet.')}

**Do not infer completion from compilation or preview.** The authoritative completion contract is the trusted studio state and its required evidence.

## Known blockers / risks

{_bullets(blockers, 'No trusted completion blocker is currently recorded. This does not mean all future/external requirements are resolved.')}

## Assumptions and decisions to preserve

{_bullets(assumptions, 'No product assumptions are recorded yet.')}

- Do not replace real behavior with placeholders or fake-success paths.
- Do not weaken tests, accessibility, privacy, security or completion gates to obtain a passing build.
- New capabilities required by this app must be validated through the factory adaptation/evolution process rather than silently skipped.

## Immediate next objective

{'Execute and validate `' + next_stage + '`.' if isinstance(next_stage, str) and next_stage else ('Project satisfies the current machine completion contract; verify any external Play Store/legal submission prerequisites.' if completion.get('finished') else 'Derive the next trusted completion stage and continue autonomously.')}

## Near-term roadmap

1. Complete every dynamically required QA/release stage.
2. Repair any discovered functional, visual, accessibility, performance, privacy or security defect.
3. Produce professional Play Store artifacts and consistent privacy/Data Safety evidence.
4. Validate the release artifact, not only debug/preview behavior.
5. Continue until the trusted completion contract is satisfied or an irreducible external prerequisite is explicitly identified.

## Long-term / final objective

Deliver this application as a fully functional, polished, maintainable and professionally presented mobile product ready for Google Play publication. The factory owns autonomous iteration and capability adaptation; human intervention is reserved for genuinely external legal, identity, payment or credential actions that cannot safely be automated.

## Resume instructions for a future ChatGPT/agent

1. Read this file and `.studio/state.json` first.
2. Inspect the current branch/commit, CI and release evidence rather than trusting an old conversation summary.
3. Preserve the product brief and non-negotiable quality gates.
4. Continue from the immediate next objective; do implementation work, not only planning.
5. Refresh this file after every material milestone or change of next objective.

Last generated: {date.today().isoformat()}
'''


def write(root: Path, req: dict, state: dict) -> Path:
    path = root / FILE
    path.write_text(render(req, state))
    return path

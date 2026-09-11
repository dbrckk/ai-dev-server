"""Godot-specific model adapter that preserves the generic model budget and transport."""
from __future__ import annotations

import json

from core import Model, ProtocolError, StudioError
from engine_patch import PatchPolicyError, validate as validate_patch
from journeys import validate_journeys

GODOT_ROLE = {
    'product': (
        'Senior Godot mobile game product lead: turn the brief and existing project into prioritized acceptance criteria, '
        'gameplay journeys, data/state requirements, scope and blockers. Every journey key is a stable Godot runtime selector: '
        'it MUST be the exact Node.name of one unique runtime node. Prefer Button/LineEdit/TextEdit/ScrollContainer controls for '
        'interactions and never claim journeys were executed before trusted runtime evidence exists.'
    ),
    'design': (
        'Senior Godot mobile game art director: define a distinctive visual direction, layout, typography, feedback, motion, '
        'accessibility and responsive behavior using assets/resources that can be represented safely in the existing Godot project. '
        'Do not assume unavailable proprietary assets.'
    ),
    'implementation': (
        'Senior Godot 4.7 mobile game engineering team: modify the existing Godot project in GDScript/resources. '
        'Preserve working behavior, implement the requested scope completely, keep code deterministic where practical, '
        'and never add credentials or pretend external services exist. Implement every acceptance-journey key as the exact '
        'Node.name of one unique runtime node. Interactive journey nodes must use the matching Godot Control type; never fake '
        'selectors only for tests. Runtime node names are part of the acceptance contract.'
    ),
    'tests': (
        'Senior Godot 4.7 QA engineer: add concrete GDScript tests under tests/. Test real project behavior and regressions; '
        'do not weaken production code, skip tests, or replace behavior with vacuous mocks.'
    ),
}
PATCH_SCHEMA = (
    'Editable implementation scope: project.godot, export_presets.cfg, scripts/**, scenes/**, assets/**, tests/**, docs/** '
    'using only the trusted text extensions. QA role may write only tests/*.gd (including subdirectories). '
    'Return ONLY JSON {"files":[{"path":"scripts/main.gd","content":"full file"}]}.'
)
PRODUCT_SCHEMA = (
    'Return ONLY a JSON object with your detailed deliverable and a journeys field. journeys must contain 1..6 objects with '
    'exactly id and steps; each journey needs 2..12 steps, at least one interaction and one assertion. Supported actions are '
    'tap(key), enter_text(key,value), scroll(key,dy), expect_text(value), expect_absent(value), expect_key(key). '
    'For Godot, every key is the exact case-sensitive Node.name of one unique runtime node, encoded as a lower-case slug; '
    'implementation must assign that Node.name explicitly. These journeys are specifications only until trusted runtime execution.'
)
DESIGN_SCHEMA = 'Return ONLY a JSON object containing the complete Godot-oriented design specification.'


class GodotModel(Model):
    def ask(self, role, context, screenshots=()):
        from learning_context import augment
        context = augment(context)
        if role not in GODOT_ROLE:
            return super().ask(role, context, screenshots)
        if screenshots:
            raise StudioError('Godot source generation does not accept screenshots')
        error = 'unknown structured-output error'
        for attempt in range(2):
            try:
                value = self._ask_godot(role, context)
                if role in ('implementation', 'tests'):
                    validate_patch(value, 'godot', role)
                elif role == 'product':
                    validate_journeys(value.get('journeys'))
                return value
            except (ProtocolError, PatchPolicyError, ValueError) as exc:
                error = str(exc)
            if attempt or self.calls >= self.limit:
                raise StudioError('Structured response rejected: ' + error) from None
            context += '\nYour previous response violated this schema rule: ' + error + '. Return corrected complete JSON only.'
        raise StudioError('Protocol repair exhausted')

    def _ask_godot(self, role: str, context: str) -> dict:
        if self.calls >= self.limit:
            raise StudioError('Model call budget exhausted; checkpoint retained')
        if len(context.encode()) > 500000:
            raise StudioError('Context exceeds configured safety limit')
        self.calls += 1
        selected_model = self.code_model if role in ('implementation', 'tests') else self.model
        self.models_used[role] = selected_model
        schema = PATCH_SCHEMA if role in ('implementation', 'tests') else PRODUCT_SCHEMA if role == 'product' else DESIGN_SCHEMA
        params = {
            'model': selected_model,
            'stream': False,
            'max_tokens': 16000 if role == 'implementation' else 8192,
            'messages': [
                {'role': 'system', 'content': GODOT_ROLE[role] + '\n' + schema},
                {'role': 'user', 'content': context},
            ],
        }
        if self.api.base == 'https://integrate.api.nvidia.com/v1' and selected_model.startswith('nvidia/nemotron-3-'):
            params.update(chat_template_kwargs={'enable_thinking': True}, reasoning_budget=2048)
        response = self.api.call('POST', '/chat/completions', params)
        try:
            if not isinstance(response, dict) or not isinstance(response.get('choices'), list) or not response['choices']:
                raise ProtocolError('Provider returned invalid completion envelope')
            choice = response['choices'][0]
            if not isinstance(choice, dict) or not isinstance(choice.get('message'), dict):
                raise ProtocolError('Provider returned invalid completion choice')
            if choice.get('finish_reason') == 'length':
                raise ProtocolError('Model response truncated')
            raw = choice['message'].get('content')
            if not isinstance(raw, str) or not raw.strip():
                raise ProtocolError('Provider returned empty text content')
            raw = raw.strip()
            if raw.startswith('```'):
                raw = raw.split('\n', 1)[1].rsplit('```', 1)[0]
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError()
            return value
        except (KeyError, IndexError, TypeError, ValueError):
            raise ProtocolError('Provider returned invalid structured output') from None
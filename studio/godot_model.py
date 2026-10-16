"""Godot-specific model adapter that preserves the generic model budget and transport."""
from __future__ import annotations

import json
import os
from pathlib import Path
import time

import core
from core import Model, ProtocolError, StudioError
from engine_patch import PatchPolicyError, validate as validate_patch
from journeys import validate_journeys
from provider_health import eligible as provider_eligible, record_failure as record_provider_failure, record_success as record_provider_success
from provider_metrics import record as record_provider_latency
from provider_router import budget_eligible, candidates_for

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
    'using only trusted text extensions. For modifications to EXISTING files, strongly prefer concise exact-match edits: '
    'return ONLY JSON {"edits":[{"path":"scripts/main.gd","find":"exact unique existing snippet","replace":"modified snippet"}]}. '
    'The find text must occur exactly once in the existing file; include enough surrounding lines for uniqueness. '
    'Never use line numbers, wildcards or invented context. Preserve all code not explicitly changed. '
    'Do NOT echo an entire existing file for a small change, because free model output quota is limited. '
    'If adding a NEW file or a full rewrite is essential, alternatively return ONLY JSON '
    '{"files":[{"path":"scripts/main.gd","content":"full file"}]}. Never mix files and edits. '
    'QA role may write only tests/*.gd and MUST use files, not edits.'
)
# The QA role must NOT see the implementation's exact-edit preference.
# Canary #37 spent two QA calls returning disallowed edit envelopes.
TESTS_SCHEMA = (
    'Godot QA: return ONLY JSON {"files":[{"path":"tests/main_test.gd",'
    '"content":"complete GDScript test source"}]}. '
    'Only NEW or full-source tests/*.gd entries are allowed; never return edits, '
    'summaries, explanation, markdown, wrappers or implementation source. '
    'Write a focused executable regression for the requested behavior and '
    'preserve the production game. The accepted envelope has exactly one top-level key: files.'
)

PRODUCT_SCHEMA = (
    'Return ONLY a JSON object with your detailed deliverable and a journeys field. journeys must contain 1..6 objects with '
    'exactly id and steps; each journey needs 2..12 steps, at least one interaction and one assertion. '
    'Journey ids must be unique lower-case slugs starting with a-z, followed only by a-z, 0-9, hyphen or underscore '
    '(max 40 characters); initial is reserved. Prefer short ids such as settings_guard. '
    'Every step MUST be a JSON object; never use string shorthand such as action(key). Supported step objects are exactly: '
    '{"action":"tap","key":"play_button"}, {"action":"enter_text","key":"name_input","value":"Player"}, '
    '{"action":"scroll","key":"settings_list","dy":-300}, {"action":"expect_text","value":"Score"}, '
    '{"action":"expect_absent","value":"Error"}, {"action":"expect_key","key":"timer_running"}. '
    'Keys must start with a-z and contain only a-z, 0-9, hyphen or underscore (max 60 characters). '
    'Text values must be strings of 1..160 characters. Scroll dy must be a nonzero number between -1000 and 1000. '
    'For Godot, every key is the exact case-sensitive Node.name of one unique runtime node, encoded as a lower-case slug; '
    'implementation must assign that Node.name explicitly. These journeys are specifications only until trusted runtime execution. '
    'Keep the deliverable compact: prioritize the requested gameplay bug, use one or two journeys unless more are required, and avoid repeating repository source. '
    'Output should use no more than 900 tokens: at most four brief acceptance criteria and minimal journeys; '
    'do not invent lengthy nested design documents, layout inventories or full source.'
)
DESIGN_SCHEMA = ('Return ONLY a concise JSON object for the requested Godot change with direction, layout, feedback, '
    'motion, accessibility and responsive behavior. Keep the answer focused on this specific change, avoid redundant '
    'full-game inventories and source excerpts, and target no more than 900 output tokens.')


class GodotModel(Model):
    def ask(self, role, context, screenshots=()):
        from learning_context import augment
        # Keep validated memories, but prioritize the current source and
        # preserve the remaining free quota for actual GDScript output.
        # This cap affects injected memory only, never project files.
        if role in ('product', 'design'):
            context = augment(context, max_items=2, max_chars=1400)
        elif role in ('implementation', 'tests', 'review'):
            context = augment(context, max_items=4, max_chars=2800)
        else:
            context = augment(context)
        if role not in GODOT_ROLE:
            return super().ask(role, context, screenshots)
        if screenshots:
            raise StudioError('Godot source generation does not accept screenshots')
        error = 'unknown structured-output error'
        invalid_response_provider = None
        for attempt in range(2):
            try:
                value = self._ask_godot(
                    role, context, avoid_response_provider=invalid_response_provider,
                )
                if role in ('implementation', 'tests'):
                    validate_patch(value, 'godot', role)
                elif role == 'product':
                    validate_journeys(value.get('journeys'))
                return value
            except (ProtocolError, PatchPolicyError, ValueError) as exc:
                error = str(exc)
                # Invalid JSON, product journeys or patch envelopes may be provider-specific.
                # Use the one bounded repair on a different eligible provider
                # where available; never bypass its quota/routing limits.
                # Truncations and policy errors remain on the same provider.
                if (
                    isinstance(exc, ProtocolError) and error != 'Model response truncated'
                ) or (
                    role == 'product' and isinstance(exc, ValueError)
                ) or (
                    isinstance(exc, PatchPolicyError)
                    and error in (
                        'Expected patch envelope',
                        'Exact edits permitted only for Godot implementation',
                    )
                ):
                    invalid_response_provider = self.providers_used.get(role)
            if attempt or self.calls >= self.limit:
                raise StudioError('Structured response rejected: ' + error) from None
            if (
                error == 'Model response truncated'
                and role == 'implementation'
                and '"files_mode":"bounded_exact_match_source_excerpts"' in context
            ):
                # A large project was supplied as trusted source excerpts.
                # Its full files cannot be reconstructed from that prompt.
                # Demand a single small exact replacement, not a full rewrite.
                context += (
                    '\nYour previous compact Godot edit was truncated. '
                    'Return ONLY JSON {"edits":[{"path":"scripts/main.gd",'
                    '"find":"exact unique existing snippet",'
                    '"replace":"minimal changed snippet"}]}. '
                    'Use at most one or two short exact edits; no complete source files, '
                    'no commentary, no code fences and no invented context.'
                )
            elif error == 'Model response truncated' and role in ('implementation', 'tests'):
                context += (
                    '\nYour previous response hit the output limit. Return complete JSON with at most two files '
                    'and at most 20,000 characters of combined file content. Include full contents for each '
                    'file; prioritize the smallest self-contained change. Further files can follow in later rounds.'
                )
            elif error == 'Model response truncated' and role in ('product', 'design'):
                context += (
                    '\nYour previous JSON was truncated by the provider output limit. '
                    'Do NOT repeat the long plan. Return ONLY a minimal valid complete JSON '
                    'with at most 700 output tokens for product or 450 for design. '
                    'For product use one journey with two or three steps, one interaction '
                    'and one assertion; use at most three brief acceptance criteria. '
                    'Every action value must be a nonempty string under 80 characters. '
                    'For design return a few short keys and no deep nested objects.'
                )
            elif error == 'Expected patch envelope' and role in ('implementation', 'tests'):
                context += (
                    '\nThe previous JSON was not a patch envelope. Return exactly one top-level key, '
                    'with no summary, explanation, markdown, wrapper or acceptance criteria. '
                    + ('For this existing-source change use {"edits":[{"path":"scripts/main.gd",'
                       '"find":"exact unique existing snippet","replace":"modified snippet"}]}. '
                       'Do not mix files and edits; preserve the supplied source outside the exact replacement.'
                       if role == 'implementation' else
                       'Use {"files":[{"path":"tests/main_test.gd","content":"complete GDScript test source"}]}. '
                       'The QA role may write only tests/*.gd; exact edits are not allowed.')
                )
            elif role == 'tests' and error == 'Exact edits permitted only for Godot implementation':
                context += (
                    '\\nThe previous QA answer used implementation-only exact edits. '
                    'Return ONLY JSON {"files":[{"path":"tests/main_test.gd",'
                    '"content":"complete focused GDScript regression test"}]}. '
                    'The only top-level key must be files. Never use edits, '
                    'summary, or production scripts for QA.'
                )
            elif role == 'product' and error == 'Invalid step text':
                context += (
                    '\nRepair ONLY the invalid journey value fields. Each value must '
                    'be a nonempty string of 1..160 characters, ideally under 80, '
                    'not null, an array or a long descriptive paragraph. '
                    'Return the complete concise JSON with the original valid steps preserved.'
                )
            else:
                context += '\nYour previous response violated this schema rule: ' + error + '. Return corrected complete JSON only.'
        raise StudioError('Protocol repair exhausted')

    def _ask_godot(
        self, role: str, context: str, *, avoid_response_provider: str | None = None,
    ) -> dict:
        if self.calls >= self.limit:
            raise StudioError('Model call budget exhausted; checkpoint retained')
        if len(context.encode()) > 500000:
            raise StudioError('Context exceeds configured safety limit')
        self.calls += 1

        provider_candidates = tuple(
            provider
            for provider in candidates_for(role, screenshots=False, providers=self.providers)
            if provider.name not in self.avoid_providers
        )
        health_raw = os.environ.get('STUDIO_PROVIDER_HEALTH_PATH', '')
        metrics_raw = os.environ.get('STUDIO_PROVIDER_METRICS_PATH', '')
        cost_raw = os.environ.get('STUDIO_PROVIDER_COST_PATH', '')
        quota_raw = os.environ.get('STUDIO_PROVIDER_MONTHLY_QUOTA_PATH', '')
        health_path = Path(health_raw) if health_raw else None
        metrics_path = Path(metrics_raw) if metrics_raw else None
        cost_path = Path(cost_raw) if cost_raw else None
        quota_path = Path(quota_raw) if quota_raw else None

        if health_path is not None:
            provider_candidates = tuple(
                provider for provider in provider_candidates
                if provider_eligible(health_path, provider.name)
            )

        from provider_cost import estimate_call_cost, load as load_provider_cost, record as record_provider_cost
        from provider_monthly_quota import load as load_provider_monthly_quota, quota_status as provider_quota_status, record as record_provider_monthly_quota

        provider_costs = load_provider_cost(cost_path) if cost_path is not None else {}
        spent_api_cost_usd = sum(
            max(0.0, float(row.get('total_cost_usd', 0.0) or 0.0))
            for row in provider_costs.values()
            if isinstance(row, dict)
        )
        try:
            max_api_cost_usd = float(os.environ.get('STUDIO_MAX_API_COST_USD', '0') or 0.0)
        except ValueError:
            max_api_cost_usd = 0.0
        provider_candidates = budget_eligible(
            provider_candidates,
            max_api_cost_usd=max_api_cost_usd,
            spent_api_cost_usd=spent_api_cost_usd,
        )
        quota_data = load_provider_monthly_quota(quota_path) if quota_path is not None else {'schema': 1, 'months': {}}
        provider_candidates = tuple(
            provider
            for provider in provider_candidates
            if (
                provider.monthly_token_quota <= 0
                or not provider_quota_status(
                    quota_data,
                    provider.name,
                    provider.monthly_token_quota,
                )['exhausted']
            )
        )
        if not provider_candidates:
            raise StudioError(
                'No healthy provider remains for this role; paid budget or pooled token quota may be exhausted'
            )
        # Retry provider malformed output with a different eligible provider,
        # but do not strand a single-provider installation or bypass budgets.
        if avoid_response_provider and len(provider_candidates) > 1:
            alternatives = tuple(
                provider for provider in provider_candidates
                if provider.name != avoid_response_provider
            )
            if alternatives:
                provider_candidates = alternatives

        self.routing_portfolio[role] = {
            'candidates': [
                {
                    'provider': provider.name,
                    'model': provider.model_for(role, False),
                    'priority': provider.priority,
                }
                for provider in provider_candidates[:6]
            ],
            'independent_from_implementation': False,
        }

        schema = PATCH_SCHEMA if role == 'implementation' else TESTS_SCHEMA if role == 'tests' else PRODUCT_SCHEMA if role == 'product' else DESIGN_SCHEMA
        system_content = GODOT_ROLE[role] + '\n' + schema
        response = None
        selected_provider = None
        selected_model = ''
        elapsed = 0.0
        last_error = None
        primary_provider = self.providers[0] if self.providers else None
        compact_source = 'bounded_exact_match_source_excerpts' in context

        for provider in provider_candidates:
            selected_model = provider.model_for(role, False)
            api = self.api if primary_provider is not None and provider == primary_provider else core.API(provider.base, provider.key)
            params = {
                'model': selected_model,
                'stream': False,
                'max_tokens': (
                    3072 if role == 'product' else 1536 if role == 'design' else
                    4096 if compact_source and role == 'implementation' else
                    3072 if compact_source and role == 'tests' else
                    16000 if role == 'implementation' else 8192
                ),
                'messages': [
                    {'role': 'system', 'content': system_content},
                    {'role': 'user', 'content': context},
                ],
            }
            if api.base == 'https://integrate.api.nvidia.com/v1':
                params['response_format'] = {'type': 'json_object'}
            if api.base == 'https://integrate.api.nvidia.com/v1' and selected_model.startswith('nvidia/nemotron-3-'):
                params.update(
                    chat_template_kwargs={'enable_thinking': True},
                    reasoning_budget=(512 if role in ('product', 'design') or (compact_source and role == 'tests')
                                      else 1024 if compact_source and role == 'implementation' else 2048),
                )
            print('Model role: ' + role + '; provider: ' + provider.name + '; model: ' + selected_model, flush=True)
            from native_model_usage import call as accounted_call, NativeAccountingError
            started = time.monotonic()
            try:
                # The capacity ledger may leave only a tiny output fragment.
                # Sending it would spend free-provider quota on truncated JSON.
                # Enforce a conservative minimum after prompt headroom, without
                # granting additional tokens or changing the requested ceiling.
                output_floor = (
                    768 if role == 'product' else
                    640 if role == 'design' else
                    1536 if compact_source and role == 'implementation' else
                    896 if compact_source and role == 'tests' else
                    3072 if role == 'implementation' else
                    1024
                )
                response = accounted_call(
                    api, params, provider.name,
                    minimum_output_tokens=output_floor,
                )
            except NativeAccountingError:
                raise
            except StudioError as exc:
                elapsed = time.monotonic() - started
                if metrics_path is not None:
                    record_provider_latency(metrics_path, provider.name, role, elapsed)
                if health_path is not None:
                    record_provider_failure(health_path, provider.name)
                last_error = exc
                continue
            elapsed = time.monotonic() - started
            if metrics_path is not None:
                record_provider_latency(metrics_path, provider.name, role, elapsed)
            selected_provider = provider
            self.models_used[role] = selected_model
            self.providers_used[role] = provider.name
            self.routing_portfolio[role]['selected'] = {
                'provider': provider.name,
                'model': selected_model,
                'priority': provider.priority,
            }
            usage = response.get('usage') if isinstance(response, dict) else None
            if isinstance(usage, dict):
                try:
                    prompt_tokens = int(usage.get('prompt_tokens', 0) or 0)
                    completion_tokens = int(usage.get('completion_tokens', 0) or 0)
                except (TypeError, ValueError):
                    prompt_tokens = completion_tokens = 0
                if cost_path is not None:
                    call_cost = (
                        0.0
                        if provider.unmetered or provider.monthly_token_quota > 0
                        else estimate_call_cost(
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            input_cost_per_million=provider.input_cost_per_million,
                            output_cost_per_million=provider.output_cost_per_million,
                        )
                    )
                    record_provider_cost(cost_path, provider.name, role, call_cost)
                if quota_path is not None and provider.monthly_token_quota > 0:
                    record_provider_monthly_quota(
                        quota_path,
                        provider.name,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                    )
            break

        if selected_provider is None:
            if isinstance(last_error, core.APIError):
                raise StudioError('All configured providers failed; last HTTP status ' + str(last_error.status)) from None
            raise StudioError('All configured providers are unavailable') from None

        try:
            if not isinstance(response, dict) or not isinstance(response.get('choices'), list) or not response['choices']:
                raise ProtocolError('Provider returned invalid completion envelope')
            choice = response['choices'][0]
            if not isinstance(choice, dict) or not isinstance(choice.get('message'), dict):
                raise ProtocolError('Provider returned invalid completion choice')
            if choice.get('finish_reason') == 'length':
                raise ProtocolError('Model response truncated')
            if choice.get('finish_reason') not in (None, 'stop'):
                raise ProtocolError('Model response did not complete normally')
            raw = choice['message'].get('content')
            if not isinstance(raw, str) or not raw.strip():
                raise ProtocolError('Provider returned empty text content')
            raw = raw.strip()
            if raw.startswith('```'):
                raw = raw.split('\n', 1)[1].rsplit('```', 1)[0]
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError()
            if health_path is not None:
                record_provider_success(health_path, selected_provider.name)
            return value
        except ProtocolError:
            if health_path is not None:
                record_provider_failure(health_path, selected_provider.name)
            raise
        except (KeyError, IndexError, TypeError, ValueError):
            if health_path is not None:
                record_provider_failure(health_path, selected_provider.name)
            raise ProtocolError('Provider returned invalid structured output') from None

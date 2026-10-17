"""Execution-local native inference accounting and shared project admission.

Only counters and provider/model identifiers are retained, never prompts or replies.
Unknown usage consumes the reservation estimate; reported usage replaces it.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

from atomic_file import write_text
from capacity_ledger import consumed_tokens, load_active, reserved_tokens, reserve, settle
from capacity_runtime import project_envelope
from core import StudioError, APIError
from file_lock import exclusive


class NativeAccountingError(StudioError):
    pass


class NativeCapacityError(NativeAccountingError):
    pass


def _path():
    raw = os.environ.get('STUDIO_NATIVE_MODEL_USAGE_PATH', '')
    return Path(raw) if raw else None


def _empty():
    return {'schema': 1, 'capacity_exhausted': False, 'usage': {
        'input_tokens': 0, 'cached_input_tokens': 0, 'output_tokens': 0,
        'reasoning_tokens': 0, 'total_tokens': 0, 'reported_tokens': 0,
        'runs': 0, 'estimated_calls': 0, 'agents': {}, 'models': {},
    }}


def _load(path):
    if not path.exists():
        return _empty()
    try:
        value = json.loads(path.read_text())
        usage = value['usage']
        valid = (value.get('schema') == 1 and isinstance(usage, dict)
                 and type(value.get('capacity_exhausted')) is bool
                 and isinstance(usage.get('agents'), dict) and isinstance(usage.get('models'), dict)
                 and all(type(usage.get(k)) is int and usage[k] >= 0
                         for k in _empty()['usage'] if k not in ('agents', 'models')))
        valid = valid and all(isinstance(k, str) and type(v) is int and v >= 0
                              for name in ('agents', 'models') for k, v in usage[name].items())
        if not valid:
            raise ValueError()
        return value
    except (OSError, ValueError, KeyError, TypeError):
        raise NativeAccountingError('Native usage checkpoint missing or invalid') from None


def snapshot(path=None):
    path = Path(path) if path else _path()
    if path is None or not path.exists():
        return None
    with exclusive(path):
        value = _load(path)
    usage = dict(value['usage'])
    usage['api_calls'] = usage['runs']
    usage['accounting_mode'] = 'estimated' if usage['estimated_calls'] else 'reported'
    providers = list(usage['agents'])
    models = list(usage['models'])
    if providers:
        usage['provider'] = providers[0] if len(providers) == 1 else 'multiple'
    if models:
        usage['model'] = models[0] if len(models) == 1 else 'multiple'
    return {**value, 'usage': usage}


def _save(path, value):
    try:
        write_text(path, json.dumps(value, sort_keys=True) + '\n', encoding='utf-8')
    except OSError:
        raise NativeAccountingError('Native usage checkpoint unavailable') from None


def _reported(response):
    usage = response.get('usage') if isinstance(response, dict) else None
    if not isinstance(usage, dict):
        return None
    components = [usage.get(key, 0) for key in
                  ('prompt_tokens', 'input_tokens', 'completion_tokens', 'output_tokens')]
    if any(type(x) is not int or x < 0 for x in components):
        return None
    incoming = max(components[:2])
    outgoing = max(components[2:])
    total = usage.get('total_tokens', incoming + outgoing)
    if type(total) is not int or total <= 0 or total < incoming + outgoing:
        return None
    prompt_details = usage.get('prompt_tokens_details')
    completion_details = usage.get('completion_tokens_details')
    cached = prompt_details.get('cached_tokens', 0) if isinstance(prompt_details, dict) else 0
    reasoning = completion_details.get('reasoning_tokens', 0) if isinstance(completion_details, dict) else 0
    if (type(cached) is not int or not 0 <= cached <= incoming
            or type(reasoning) is not int or not 0 <= reasoning <= outgoing):
        return None
    return {'input_tokens': incoming, 'output_tokens': outgoing, 'total_tokens': total,
            'cached_input_tokens': cached, 'reasoning_tokens': reasoning}


def call(api, params, provider, *, capacity_reserved=False, estimated_tokens=None,
         timeout_seconds=None, minimum_output_tokens=1, future_stage_reserve_tokens=0):
    # Caller-specified floor is an admission check, not an extra quota grant.
    # Do not submit a completion that cannot possibly fit a useful response.
    if type(minimum_output_tokens) is not int or minimum_output_tokens < 1:
        raise ValueError('minimum_output_tokens must be a positive integer')
    if (type(future_stage_reserve_tokens) is not int
            or not 0 <= future_stage_reserve_tokens <= 1_000_000):
        raise ValueError('future_stage_reserve_tokens must be a bounded non-negative integer')
    transport = {} if timeout_seconds is None else {'timeout_seconds': timeout_seconds}
    if getattr(type(api), 'supports_bounded_retries', False) is True:
        transport['max_attempts'] = 1
    path = _path()
    if path is None:
        return api.call('POST', '/chat/completions', params, **transport)
    with exclusive(path):
        _save(path, _load(path))  # Verify storage before submitting inference.
    payload = dict(params)
    prompt_estimate = max(1, (len(json.dumps(payload.get('messages', []), ensure_ascii=False)) + 3)//4)
    # Character-count token estimates are not exact for source code or JSON.
    # Reserve conservative prompt headroom before enforcing a project cap;
    # actual provider usage still replaces the reservation at settlement.
    prompt_allowance = prompt_estimate + max(128, (prompt_estimate + 4)//5)
    output_limit = int(payload['max_tokens'])
    reservation = None
    ledger_path = None
    plan_raw = os.environ.get('STUDIO_CAPACITY_PLAN_PATH', '')
    project_id = os.environ.get('STUDIO_PROJECT_ID', '')
    if plan_raw and not capacity_reserved:
        envelope = project_envelope(plan_raw, project_id)
        ledger_raw = os.environ.get('STUDIO_CAPACITY_LEDGER_PATH', '')
        if envelope is None or not ledger_raw or not project_id:
            raise NativeAccountingError('Configured native project capacity plan missing or invalid')
        ledger_path = Path(ledger_raw)
        with exclusive(ledger_path):
            if ledger_path.exists():
                try:
                    saved = json.loads(ledger_path.read_text())
                    if (saved.get('schema') != 1 or not isinstance(saved.get('consumed'), dict)
                            or not isinstance(saved.get('reservations'), dict)):
                        raise ValueError()
                    for key, count in saved['consumed'].items():
                        if (not isinstance(key, str) or '::' not in key
                                or any(not part for part in key.split('::', 1))
                                or type(count) is not int or count < 0):
                            raise ValueError()
                    for key, row in saved['reservations'].items():
                        if (not isinstance(key, str) or not isinstance(row, dict)
                                or any(not isinstance(row.get(k), str) or not row[k]
                                       for k in ('project_id', 'provider'))
                                or type(row.get('reserved_tokens')) is not int
                                or row['reserved_tokens'] < 0
                                or any(type(row.get(k)) not in (int, float)
                                       or not math.isfinite(row[k]) or row[k] < 0
                                       for k in ('created_at', 'expires_at'))):
                            raise ValueError()
                except (OSError, ValueError, TypeError, AttributeError):
                    raise NativeAccountingError('Configured native capacity ledger invalid') from None
            active = load_active(ledger_path)
        remaining = envelope - consumed_tokens(active, project_id=project_id) - reserved_tokens(active, project_id=project_id)
        # This is a planning-stage admission guard, not a second charge or
        # additional token quota. Keep a bounded slice of the existing
        # project envelope available for subsequent source implementation.
        # Settlement accounts only the current call's actual/estimated usage.
        unguarded_output_limit = min(output_limit, remaining - prompt_allowance)
        output_limit = min(
            output_limit,
            remaining - prompt_allowance - future_stage_reserve_tokens,
        )
        if output_limit >= minimum_output_tokens:
            reservation = reserve(ledger_path, project_id=project_id, provider='native:'+provider,
                estimated_tokens=prompt_allowance+output_limit, provider_remaining_tokens=None,
                project_envelope_tokens=envelope)
        if output_limit < minimum_output_tokens or reservation.get('admitted') is not True:
            with exclusive(path):
                value = _load(path); value['capacity_exhausted'] = True; _save(path, value)
            reason = (
                'project_future_stage_reserve'
                if (future_stage_reserve_tokens and output_limit < minimum_output_tokens
                    and unguarded_output_limit >= minimum_output_tokens)
                else 'project_envelope_exhausted'
            )
            raise NativeCapacityError(reason)
    payload['max_tokens'] = output_limit
    if 'reasoning_budget' in payload:
        payload['reasoning_budget'] = min(int(payload['reasoning_budget']), output_limit)
    estimate = prompt_estimate + output_limit if estimated_tokens is None else max(1, int(estimated_tokens))
    try:
        with exclusive(path):
            value = _load(path); usage = value['usage']
            usage['runs'] += 1; usage['estimated_calls'] += 1; usage['total_tokens'] += estimate
            usage['agents'][provider] = int(usage['agents'].get(provider, 0)) + 1
            name = str(payload.get('model') or 'unknown')
            usage['models'][name] = int(usage['models'].get(name, 0)) + 1
            _save(path, value)
    except Exception:
        if reservation is not None:
            settle(ledger_path, reservation['reservation_id'], actual_tokens=0)
        raise
    try:
        response = None
        reported = None
        definitively_rejected = False
        try:
            # One POST per accounted submission. Provider fallback is separately
            # reserved; opaque transport retries must not bypass admission.
            response = api.call('POST', '/chat/completions', payload, **transport)
            reported = _reported(response)
            return response
        except APIError as exc:
            # A rejection of the initial POST cannot have generated tokens.
            # Polling an accepted 202 response, transport timeouts and 5xx
            # failures remain conservatively charged: usage is unknown.
            definitively_rejected = (
                exc.status in {400, 401, 403, 404, 422, 429}
                and not exc.pending_accepted
            )
            raise
        finally:
            actual = (
                reported['total_tokens'] if reported is not None else
                0 if definitively_rejected else estimate
            )
            if reservation is not None:
                settle(ledger_path, reservation['reservation_id'], actual_tokens=actual)
            if reported is not None:
                with exclusive(path):
                    value = _load(path); usage = value['usage']
                    usage['total_tokens'] += actual - estimate
                    usage['estimated_calls'] -= 1
                    usage['reported_tokens'] += actual
                    for key in ('input_tokens','output_tokens','cached_input_tokens','reasoning_tokens'):
                        usage[key] += reported[key]
                    _save(path, value)
            elif definitively_rejected:
                with exclusive(path):
                    value = _load(path); usage = value['usage']
                    usage['total_tokens'] -= estimate
                    usage['estimated_calls'] -= 1
                    _save(path, value)
    except NativeAccountingError as exc:
        exc.inference_submitted = True
        raise

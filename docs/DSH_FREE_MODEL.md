# Optional DSH free-model gateway

[Ebony-Vinyl/dsh-our-free-model](https://github.com/Ebony-Vinyl/dsh-our-free-model)
is a DSH plugin with an authenticated local OpenAI-compatible gateway. It can
be used through the existing provider router; no plugin installation, automatic
updates, or credentials from that repository are required inside this worker.

## Qualification (2026-10-20)

Reviewed upstream README and `src/kilo.js` at
[`5923ebef0f55578ca21bb5555b7ba5adb51aef21`](https://github.com/Ebony-Vinyl/dsh-our-free-model/tree/5923ebef0f55578ca21bb5555b7ba5adb51aef21).
A read-only request to the [Kilo gateway catalog](https://api.kilo.ai/api/gateway/models)
returned 401 catalog entries, of which 18 declared `isFree: true`. This was a
catalog lookup, not an inference or uptime qualification. No generation was sent.
The catalog warns that free-pool prompts may be logged and used for training.
Use only deliberately selected public, nonsensitive tasks with this lane.

The plugin is a client of external services, not additional self-hosted model
capacity. Free availability, model IDs, regional access and quotas can change.
Do not register it as unlimited capacity or import a guessed monthly allowance.
Desktop-only EAC access is separate and does not establish Actions worker access.

## Connect an existing local gateway

1. In DSH, enable **Settings → Our Free Model → Local forward**. Copy the actual
   bound base URL and create its gateway key. The port can change if occupied.
2. Run DSH and this worker on the same machine/network namespace. `127.0.0.1`
   on a hosted GitHub runner does not reach a gateway on your desktop.
3. Put the key in `DSH_GATEWAY_KEY` in the worker environment (never in JSON,
   source files, logs or command-line arguments). Set `DSH_GATEWAY_BASE` to the
   copied URL ending in `/v1`. List models without generating tokens:

   ```bash
   python - <<'PY'
   import os, sys
   sys.path.insert(0, 'studio')
   from core import API
   key = os.environ['DSH_GATEWAY_KEY']
   if not key.strip():
       raise SystemExit('DSH_GATEWAY_KEY is empty')
   result = API(os.environ['DSH_GATEWAY_BASE'], key).call(
       'GET', '/models', timeout_seconds=15, max_attempts=1)
   for item in result.get('data', []):
       print(item['id'])
   PY
   ```

4. Select an exact currently advertised model whose upstream pricing is free;
   the local catalog also contains paid/BYOK lanes. Add a provider object to
   your existing `STUDIO_PROVIDERS_JSON` array, replacing the example URL and
   model ID with those verified above:

   ```json
   {
     "name": "dsh-local-free",
     "base": "http://127.0.0.1:18899/v1",
     "key_env": "DSH_GATEWAY_KEY",
     "model": "EXACT_ADVERTISED_FREE_MODEL_ID",
     "code_model": "EXACT_ADVERTISED_FREE_MODEL_ID",
     "priority": 40,
     "free_preferred": true,
     "unmetered": false,
     "monthly_token_quota": 0
   }
   ```

`free_preferred` is a routing preference, not a price guarantee. Explicit
`unmetered: false` is essential because a loopback address normally represents
local inference. A zero monthly quota means no verified quota is declared; it
must not be used to override existing capacity/budget gates. Missing declared
keys now exclude the provider, including loopback gateways. Intentionally
keyless local servers continue to omit `key_env`.

Before enabling real work, qualify structured JSON output and a bounded public
source task with the selected model. Existing retry/cooldown, budget, validation,
commit and review checks still apply. This integration has been checked through
real authenticated loopback HTTP with a diagnostic server; a running DSH host
and model-authored delivery have not been verified here.

## Optional direct anonymous gateway

The router also accepts `"anonymous": true` for an explicitly configured
public gateway. This is opt-in, requires HTTPS for remote endpoints, and cannot
be combined with `key_env`. Existing authenticated and keyless local providers
retain their previous configuration. No default production provider is added.

For public, nonsensitive experiments only, a currently advertised Kilo free
model can be configured without installing a DSH host:

```json
{
  "name": "kilo-public-free",
  "base": "https://api.kilo.ai/api/gateway",
  "anonymous": true,
  "model": "kilo-auto/free",
  "code_model": "kilo-auto/free",
  "priority": 40,
  "free_preferred": true,
  "unmetered": false,
  "monthly_token_quota": 0
}
```

Add the object to an explicitly chosen `STUDIO_PROVIDERS_JSON` array. Confirm
`isFree: true` and zero prompt/completion prices from the live catalog before
use; the router's `anonymous` flag is authentication configuration, not a pricing
verifier. It does not bypass capacity reservations, cooldowns or budget checks.
Do not send credentials, private repositories or private tool output to this lane.

### Bounded live observation, 2026-10-20

Two requests sent only a synthetic JSON echo instruction, without credentials
or project content, after checking the live catalog's free flag and prices:

- At `max_tokens=128`, the service returned empty content: 128 completion tokens,
  including 123 reasoning tokens. HTTP success alone was not usable output.
- At `max_tokens=512`, it returned the requested JSON, `finish_reason=stop`,
  190 completion tokens including 174 reasoning tokens.
- Both responses identified `stealth/glyph-cluster` behind `kilo-auto/free` and
  reported `market_cost=0`. The underlying model identity was not independently
  verified; automatic routing may change.

The configured anonymous provider also successfully fetched the real catalog
through the worker's existing API transport. This proves a bounded request and
catalog path, not tool-use reliability, coding quality, durable capacity, or a
hosted worker-to-PR delivery. No deployment variables were changed.

## Independent hosted free-code smoke (synthetic data only)

The read-only-scope GitHub Actions workflow
[`public-free-code-smoke.yml`](../.github/workflows/public-free-code-smoke.yml)
checks the live `kilo-auto/free` entry is still marked `isFree: true`
with exactly zero prompt and completion catalog prices **before** making
any generation request. It then makes **at most one** public synthetic
Python-code request with a 512-completion-token ceiling and no API key,
private file, source snippet, repository credential, or operator token.

The resulting code is **never executed**. It is checked with the existing
restricted AST-based `increment(value)` semantic verifier, and only
redacted counters/status are retained in the `public-free-code-smoke`
workflow artifact. Catalog uncertainty, transport errors, insufficient
model output, or nonzero reported costs fail closed. Cost evidence includes top-level and
`usage` cost/market-cost fields plus upstream cost details; every present field
must be numeric zero. Missing costs remain explicitly unreported. Trigger on
changes to the probe/workflow or via manual GitHub Actions dispatch;
there is **no scheduled consumption**.

A passing check only demonstrates a small anonymous model-authored
source response on GitHub Actions at that point in time. It is **not**
authorization to transmit private projects, a promise of sustainable
capacity, or proof that Production-OS produced a target-branch commit,
draft PR, and independent build. Those separate delivery gates still
apply.

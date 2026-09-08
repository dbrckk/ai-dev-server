# Autonomous mobile factory: completion contract

The control plane must never equate a successful debug preview with a finished application.

## User contract

The intended interaction is one brief from ChatGPT. After dispatch, the factory owns planning, design, implementation, original/provenance-tracked graphics, tests, repair, build, release QA and continued improvement. It should request human intervention only for irreducibly external actions such as accepting legal agreements, creating store identities, payment, or credentials that cannot safely be generated.

## Completion ladder

1. **Product** — acceptance criteria and executable user journeys exist.
2. **Design** — visual tokens, accessibility, responsive states and asset requirements exist.
3. **Implementation** — no placeholders or fake-success paths; tests exercise real behavior.
4. **Validation** — static analysis, tests, journey screenshots and build gates pass.
5. **Independent review** — code and visual reviewers pass on actual evidence.
6. **Release build** — reproducible release artifact is built and hashed.
7. **Device QA** — declared critical journeys pass on a real Android device/emulator release build.
8. **Release package** — store metadata, screenshots, icon/feature graphics and privacy disclosures are generated and validated.
9. **Security/privacy** — dependency/source/security checks and declared permissions/data behavior pass.
10. **Finished** — all required evidence above is present. Store submission itself is a separate external action when credentials/legal acceptance are unavailable.

`studio/completion.py` is the machine-readable guardrail for this ladder. Missing evidence is work to schedule, never a reason to claim completion.

## Continuous evolution

Continuous improvement must remain evidence-driven and reversible. The factory may propose and test improvements indefinitely, but must not silently weaken tests, quality gates, security boundaries or the definition of done. Changes to the factory itself should use an isolated branch, pass its own regression suite, and merge only when measured quality is non-regressing.

## Next implementation milestones

- Wire completion evidence into the orchestrator and queue unfinished stages automatically.
- Produce signed/release-capable Android App Bundles without exposing signing material to model context.
- Add emulator/device journey execution against release artifacts.
- Add an asset/art-direction pipeline with provenance manifests and automated visual consistency checks.
- Generate store listing copy, screenshots, icon/feature graphics and privacy/data-safety drafts from verified app behavior.
- Add security/dependency/license/permission gates.
- Add an autonomous evaluator that benchmarks factory changes against fixed reference briefs before promotion.

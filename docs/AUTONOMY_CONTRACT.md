# Autonomous mobile factory: completion contract

The control plane must never equate a successful debug preview with a finished application.

## User contract

The intended interaction is one brief from ChatGPT. After dispatch, the factory owns planning, design, implementation, original/provenance-tracked graphics, tests, repair, build, release QA and continued improvement. It should request human intervention only for irreducibly external actions such as accepting legal agreements, creating store identities, payment, or credentials that cannot safely be generated.

The long-term interface is deliberately narrow: a ChatGPT conversation supplies the target repository and high-level product brief. The factory is responsible for translating that brief into all required technical work, adapting its own capability set when the project exposes a gap, and returning verifiable release/store evidence rather than asking the user to operate the development toolchain.

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

## Autonomous adaptation lifecycle

A project must not be rejected merely because the current factory lacks a specialized executor. It must also never be called complete when such an executor is missing. Unsupported work enters `adaptation_required` and produces `evolution-request.json`.

The evolution loop is:

1. **Detect the gap** from actual project evidence: capability, permission, dependency, platform behavior, store rule or failed trusted gate.
2. **Research resources** with preference for official platform documentation, maintained SDK/package metadata, trusted runtime environments and reviewed open-source references.
3. **Design a candidate capability** on an isolated factory branch. Unreviewed external source code is never executed with factory credentials.
4. **Add trusted tests and measurable evidence** specific to the new capability.
5. **Benchmark the candidate** against the existing regression suite, real Flutter smoke test and fixed reference projects.
6. **Promote only non-regressing candidates** that preserve security boundaries and the definition of done.
7. **Keep rollback possible** so a later regression can revert the factory capability without corrupting application repositories.
8. **Resume the blocked project** using the newly promoted capability and continue until completion or the next evidence-backed gap.

The factory may add tools, SDKs, packages, emulators, device services, model providers or other resources when justified by a project, but new resources are capabilities to verify—not reasons to bypass a quality gate.

## Continuous evolution

Continuous improvement must remain evidence-driven and reversible. The factory may propose and test improvements indefinitely, but must not silently weaken tests, quality gates, security boundaries or the definition of done. Changes to the factory itself should use an isolated branch, pass its own regression suite, and merge only when measured quality is non-regressing.

## Play Store destination

The target deliverable is not merely a compilable APK. The factory should converge on a Play-ready release: current Android target requirements, release AAB, signing/upload-key workflow that never exposes private key material to model context, device/capability QA, professional store media, truthful Data Safety/privacy declarations, security/dependency/license evidence, and automated submission when an authorized Play account and required legal attestations are available.

Account creation, identity verification, accepting legal terms, payment, mandatory tester participation and credentials controlled by external services remain explicit external dependencies rather than fabricated completion evidence.

## Next implementation milestones

- Turn `evolution-request.json` into a bounded resource-research and candidate-generation workflow.
- Add a fixed benchmark suite of diverse reference app briefs and an autonomous promotion evaluator.
- Add a ChatGPT-facing dispatch contract that creates/updates a project request without manual repository editing.
- Produce signed/release-capable Android App Bundles without exposing signing material to model context.
- Verify current Google Play target-SDK and publication-policy requirements as trusted release gates.
- Complete billing, platform-view and other dynamically discovered QA executors.
- Add an asset/art-direction pipeline with provenance manifests and automated visual consistency checks.
- Expand privacy/data-flow classification so networked applications can pass on verified evidence instead of remaining conservatively blocked.
- Automate Play Console submission when credentials and legal/account prerequisites are present.

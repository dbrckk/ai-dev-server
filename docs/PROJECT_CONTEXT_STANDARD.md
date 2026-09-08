# PROJECT_CONTEXT.md Standard

Every repository created or substantially managed by the autonomous factory MUST have a root `PROJECT_CONTEXT.md` designed for cross-conversation handoff.

## Required sections

- **Purpose** — what the app/project does, target users, core value.
- **Current scope** — implemented and explicitly planned product behavior.
- **Architecture and constraints** — stack, important components, external services, platform constraints and invariants.
- **Evidence/status** — current build, test, QA and release state. Never convert assumptions into evidence.
- **Blockers/risks/debt** — unresolved technical, product, privacy, security, store or external issues.
- **Immediate objective** — the next concrete unit of work.
- **Near-term roadmap** — ordered meaningful milestones.
- **Final objective** — the intended finished state of the product.
- **Decisions to preserve** — choices a future agent must not accidentally undo.
- **Handoff metadata** — last meaningful update date and useful commit/PR identifiers.

## Lifecycle

1. Create the file as soon as the factory has enough product context to initialize a repository.
2. Treat the file as trusted handoff metadata; application-generation models must not be allowed to silently rewrite the quality contract or claim unverified completion.
3. Refresh it after material milestones, architecture changes, newly discovered blockers, release-stage transitions, or changes to the immediate objective.
4. Include it in remote checkpoints so a new ChatGPT conversation can recover without relying on chat memory.
5. Before substantial work, an agent resuming a repository should read this file and then verify volatile facts such as current branch, CI and open PRs against GitHub.

## Safety and quality rules

- Never store secrets, tokens, private keys or sensitive credentials in the context file.
- Never mark a stage complete without the corresponding trusted evidence.
- Never use the context file to bypass `.studio/state.json`, completion gates or CI.
- Keep historical detail concise; preserve decisions and current state rather than an exhaustive changelog.
- The final objective must remain explicit so short-term optimizations cannot silently redefine the product.

## Factory requirement

A factory-managed project missing `PROJECT_CONTEXT.md` should eventually be treated as a recoverable handoff defect: generate/reconstruct the file from trusted request/state/repository evidence, validate it, checkpoint it, then continue. This requirement applies to newly generated projects and existing projects brought under factory management.

# Autonomous project ownership

## Mission

AI Dev Server is intended to take ownership of a new project or an existing supported project and continue working without routine human intervention until the machine definition of done is satisfied.

The normal lifecycle is:

1. inspect the target repository and persisted project state;
2. understand the objective and existing implementation;
3. for new Android apps or major redesigns, complete the [REA competitor/reference research intake](APP_REFERENCE_REA.md) with official source evidence and explicit unavailability status before implementation planning;
4. consult the curated star-list for reusable tools/repositories;
5. plan the next concrete work;
6. implement;
7. run tests, builds, reviews and runtime/visual checks;
8. repair failures and regressions;
9. adapt the factory when a missing capability is discovered;
10. persist checkpoints and memory;
11. repeat automatically until completion.

A failed test, model failure, provider quota, implementation error or missing internal capability is **not** a reason to ask the user to take over. The system should retry, reroute, repair, research or adapt when it can do so safely.

## Only valid reason to stop for the user

Human intervention is reserved for genuinely external prerequisites that the worker cannot safely perform itself, for example:

- adding an API key or token to a secret manager;
- identity/KYC or payment actions;
- accepting legal agreements;
- store-console actions requiring the account owner;
- external approval that cannot be delegated.

When this happens the worker creates:

- `USER_INPUT_REQUIRED.txt` — concise instructions for the user;
- `user-input-required.json` — machine-readable state.

Secrets must never be written into either file. The file asks the user to add the secret to GitHub Actions/environment secrets under the required name. Once supplied, the worker resumes from its persisted checkpoint.

## Existing projects

Existing supported repositories are detected from their files. Work should occur on the studio/project branch and preserve the default branch until validation is complete. Existing source is treated as the starting point, not discarded.

Current specialized engines are Flutter and Godot. The orchestration layer is intentionally engine-neutral so additional project types can be added as adapters rather than creating separate autonomous systems.

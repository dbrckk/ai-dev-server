# Generic autonomous project engine

The generic engine is the fallback for repositories that are not handled by a specialized engine such as Flutter or Godot.

## Autonomous loop

Each cycle follows the same evidence-driven pattern:

1. restore the latest project checkpoint;
2. inspect the repository;
3. use the portfolio scan and persistent engineering memory;
4. plan concrete work;
5. implement a bounded text patch;
6. discover and run trusted verification commands;
7. review the objective against actual verification evidence;
8. checkpoint the work on the studio branch;
9. continue until the objective is verified complete.

The worker does not stop merely because an implementation attempt or test fails. The next round receives the previous verification evidence and repairs the project accordingly.

## Portfolio research

Before project execution, AI Dev Server lists the repositories owned by the target owner. It ranks all repositories using the target name, brief, metadata, language and topics. The strongest candidates are then deep-profiled using their repository tree and README.

This research is advisory. Code from another repository is never executed automatically. Similar projects are injected into the planning context so the worker can reuse proven architecture and avoid rebuilding existing work from zero.

## Verification support

The current trusted verifier automatically detects common stacks including:

- Node/npm
- Python
- Go
- Rust
- Maven/JVM
- Gradle
- .NET

Verification runs with a stripped environment that does not expose GitHub/provider secrets.

If a project has no supported verifier, the project cannot be declared complete merely from model judgment. Future capability adaptation should add an appropriate verifier or the implementation should add a testable project structure.

## Continuous learning

Verified generic cycles are written to persistent project memory only when:

- a real verifier passed;
- the project checkpoint was persisted to Git;
- the evidence is structurally valid.

Those experiences are marked reusable and can inform future projects. Current project evidence always overrides prior memory.


## Adaptive verifier synthesis

If the built-in verifier does not recognize the stack, the generic engine does not stop. It asks the configured model to synthesize a **declarative verifier recipe** from:

- repository files;
- locally available trusted toolchains;
- the project brief;
- previous verification evidence;
- validated engineering memory from earlier projects.

The recipe is constrained to argument-vector commands. Shell command strings, remote installers, deployment/publishing operations, secret access and arbitrary executables are rejected. The recipe is saved as `generic-verifier.json`, executed, and its result feeds the next work/analyse cycle.

A verifier recipe becomes reusable learning only after a real verification passes and the corresponding project checkpoint is persisted to Git. Future projects can then reuse that validated experience.

## Resuming after required user input

A missing secret is the exceptional pause path and is triggered only from explicit trusted failure evidence: the verification log must both state that an external secret/environment prerequisite is required and name the required environment variable.

The generic engine then:

1. rejects publication of the failing round and restores the pre-round editable workspace when available;
2. writes `USER_INPUT_REQUIRED.txt` with human-readable instructions containing secret **names only**;
3. writes `user-input-required.json` with the project id, reason and required environment-variable names;
4. returns `user_input_required` instead of looping through providers or implementation strategies.

No secret value is written to either file.

On the next run, the engine checks those exact environment-variable names **before model/bootstrap work**. If any remain unavailable, it exits again without consuming model work. Once all are present, both user-input files are cleared and autonomous work resumes from the persisted checkpoint/DAG task.

The read-only status command also exposes this state:

```bash
python studio/project_status.py /path/to/project-output --compact
```


## Read-only project status

The persisted autonomous state can be inspected without starting a model, verifier, or implementation round:

```bash
python studio/project_status.py /path/to/project-output
```

For scripts/mobile terminals:

```bash
python studio/project_status.py /path/to/project-output --compact
```

The JSON view includes:

- objective DAG counts and next task;
- stalled/confidence blockers;
- latest round verification summary;
- task/release confidence;
- semantic task count;
- task proof count and sealed release proof metadata.

The command is read-only and never mutates project state.

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

A missing secret remains the exceptional pause path. The project produces `USER_INPUT_REQUIRED.txt` and stays schedulable. Scheduled runs check whether the specifically requested secret is now available. Once it appears, the persisted goal is reactivated automatically and work resumes from the previous checkpoint.

# Capacity Work-Conserving V3 Design

## Scope

Make finite token allocation work-conserving on the current V3 scheduler while preserving all existing safety and routing semantics.

The change applies only to finite capacity. Unmetered providers continue to remove token-envelope constraints. Provider ordering, adaptive routing scores, circuit-breaker exclusion, capacity-pressure weighting, efficiency weighting, stagnation caps, pause semantics and critical classification remain unchanged.

## Required behavior

1. Ordinary projects may consume at most the ordinary pool (`finite_capacity - critical_reserve`). Reserved capacity must never be granted to ordinary work.
2. If an ordinary project reaches its request/stagnation cap, unused ordinary capacity is redistributed among other eligible ordinary projects instead of being stranded.
3. Critical work receives the critical reserve first, then may consume ordinary capacity that ordinary projects did not use.
4. Paused projects receive zero capacity and do not participate in redistribution.
5. No project may exceed its effective envelope cap: `min(requested_tokens, stagnation_cap)`.
6. Allocation remains deterministic and weighted by the existing `_weight()` function.
7. Internal scheduler-only fields must not leak into the public report.
8. `summary.allocated_tokens` must equal the sum of project envelopes and must never exceed finite capacity when no unmetered provider is available.

## Architecture

Add one pure helper, `_weighted_work_conserving(projects, capacity)`, that repeatedly distributes remaining finite capacity across uncapped eligible projects according to the existing weight function until either capacity is exhausted or all projects hit their caps.

`allocate()` computes every project's effective cap once. It then performs three deterministic passes: ordinary pool allocation, critical reserve allocation, and critical use of unused ordinary capacity. Public report construction stays unchanged except for consuming the computed envelopes and stripping private scratch fields.

## Failure and safety properties

- A zero/negative capacity argument returns zero allocations.
- A zero stagnation multiplier still yields a zero effective cap.
- A paused project never receives redistributed capacity.
- Critical reserve remains isolated from ordinary work.
- No model/provider runtime behavior changes; this is a deterministic scheduler-only change.

## Verification

Add regression tests for:

- peer cap redistribution with full finite utilization;
- reserve isolation for ordinary projects;
- critical consumption of otherwise-unused ordinary capacity;
- pause/stagnation caps under redistribution;
- total allocation never exceeding finite capacity.

Run the targeted scheduler test module first, then the repository's required GitHub Actions gates before merge.

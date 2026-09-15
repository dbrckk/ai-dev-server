# Capacity Work-Conserving V3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make finite project scheduling fully work-conserving without weakening critical reserve, pause, stagnation, or provider-routing policies.

**Architecture:** Add one deterministic weighted redistribution helper and use it in three finite-capacity passes: ordinary pool, critical reserve, then critical access to unused ordinary capacity. Keep unmetered behavior and provider ordering untouched.

**Tech Stack:** Python 3, `unittest`, existing GitHub Actions validation suite.

**Spec:** `docs/superpowers/specs/2026-09-15-capacity-work-conserving-v3-design.md`

## Global Constraints

- Do not change provider tier ordering or adaptive routing-score formulas.
- Ordinary projects must never consume critical reserve.
- Critical projects may consume only unused ordinary capacity beyond their reserved share.
- Never exceed the effective per-project cap or total finite capacity.
- Preserve pause and stagnation semantics.
- Use TDD: observe RED before implementation and GREEN afterward.

---

### Task 1: Lock the work-conserving contract with regression tests

**Files:**
- Modify: `tests/test_capacity_scheduler.py`

**Interfaces:**
- Consumes: `allocate(projects, providers, *, critical_reserve_ratio, exploration_strength)`
- Produces: regression expectations for redistribution, reserve isolation, critical borrowing, and global finite-capacity conservation.

- [ ] **Step 1: Add failing peer-cap redistribution test**

```python
def test_finite_capacity_is_work_conserving_when_peer_hits_cap(self):
    providers = [ProviderCapacity("free", 1000, unmetered=False)]
    report = allocate([
        {"id": "small", "requested_tokens": 100, "priority": 100},
        {"id": "large", "requested_tokens": 1000, "priority": 1},
    ], providers, critical_reserve_ratio=0.0)
    by_id = {row["id"]: row for row in report["projects"]}
    self.assertEqual(by_id["small"]["token_envelope"], 100)
    self.assertEqual(by_id["large"]["token_envelope"], 900)
    self.assertEqual(report["summary"]["allocated_tokens"], 1000)
```

- [ ] **Step 2: Add failing critical-reserve isolation and borrowing tests**

```python
def test_reserved_capacity_is_not_spent_by_ordinary_projects(self):
    providers = [ProviderCapacity("free", 1000, unmetered=False)]
    report = allocate([
        {"id": "ordinary", "requested_tokens": 1000, "priority": 100},
    ], providers, critical_reserve_ratio=0.2)
    self.assertEqual(report["projects"][0]["token_envelope"], 800)


def test_critical_project_can_consume_unused_ordinary_pool(self):
    providers = [ProviderCapacity("free", 1000, unmetered=False)]
    report = allocate([
        {"id": "critical", "requested_tokens": 1000, "priority": 50, "phase": "verification"},
    ], providers, critical_reserve_ratio=0.2)
    self.assertEqual(report["projects"][0]["token_envelope"], 1000)
```

- [ ] **Step 3: Add finite-cap conservation test with caps and pauses**

```python
def test_work_conserving_allocation_respects_pause_caps_and_total_capacity(self):
    providers = [ProviderCapacity("free", 1000, unmetered=False)]
    report = allocate([
        {"id": "paused", "requested_tokens": 900, "priority": 100, "capacity_paused": True},
        {"id": "capped", "requested_tokens": 500, "priority": 90, "stagnation_multiplier": 0.2},
        {"id": "runner", "requested_tokens": 1000, "priority": 10},
    ], providers, critical_reserve_ratio=0.0)
    by_id = {row["id"]: row for row in report["projects"]}
    self.assertEqual(by_id["paused"]["token_envelope"], 0)
    self.assertEqual(by_id["capped"]["token_envelope"], 100)
    self.assertEqual(by_id["runner"]["token_envelope"], 900)
    self.assertLessEqual(report["summary"]["allocated_tokens"], 1000)
```

- [ ] **Step 4: Run the targeted test module and confirm RED**

Run: `python -m unittest tests.test_capacity_scheduler -v`
Expected: the new work-conserving assertions fail while pre-existing tests remain green.

- [ ] **Step 5: Commit the tests-only state**

```bash
git add tests/test_capacity_scheduler.py
git commit -m "test: lock work-conserving capacity contract"
```

### Task 2: Implement deterministic work-conserving redistribution

**Files:**
- Modify: `studio/capacity_scheduler.py`

**Interfaces:**
- Produces: `_weighted_work_conserving(projects: list[dict], capacity: int) -> dict[str, int]`
- Consumes: existing `_weight(project)` and private `_max_envelope` scratch key.

- [ ] **Step 1: Add the pure redistribution helper**

```python
def _weighted_work_conserving(projects: list[dict], capacity: int) -> dict[str, int]:
    remaining = max(0, int(capacity))
    allocations = {project["id"]: 0 for project in projects}
    pending = [
        project for project in projects
        if not project.get("capacity_paused") and int(project.get("_max_envelope", 0)) > 0
    ]
    while remaining > 0 and pending:
        total_weight = sum(_weight(project) for project in pending) or 1.0
        progressed = 0
        for project in list(pending):
            project_id = project["id"]
            cap = int(project["_max_envelope"])
            room = max(0, cap - allocations[project_id])
            if room == 0:
                pending.remove(project)
                continue
            share = max(1, int(remaining * (_weight(project) / total_weight)))
            grant = min(room, share, remaining)
            allocations[project_id] += grant
            remaining -= grant
            progressed += grant
            if allocations[project_id] >= cap:
                pending.remove(project)
            if remaining <= 0:
                break
        if progressed == 0:
            break
    return allocations
```

- [ ] **Step 2: Compute effective caps before allocation**

For each cleaned project, set private `_max_envelope = min(requested_tokens, stagnation_cap)` before finite allocation.

- [ ] **Step 3: Allocate ordinary pool, critical reserve, then unused ordinary capacity to critical work**

Use `_weighted_work_conserving()` for each pass, subtracting the already-granted critical reserve from critical caps before the borrowing pass.

- [ ] **Step 4: Strip private scratch fields from public report rows**

Construct each report row with:

```python
**{key: value for key, value in project.items() if not key.startswith("_")}
```

- [ ] **Step 5: Run targeted tests and confirm GREEN**

Run: `python -m unittest tests.test_capacity_scheduler -v`
Expected: PASS.

- [ ] **Step 6: Run repository validation through GitHub Actions**

Expected: all required PR-triggered gates succeed before merge.

- [ ] **Step 7: Commit implementation**

```bash
git add studio/capacity_scheduler.py
git commit -m "feat: make finite capacity allocation work-conserving"
```

"""Phase-level execution quota planning and bounded reallocation."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseQuotas:
    planning: int
    implementation: int
    verification: int
    fallback: int
    review: int

    def as_dict(self) -> dict:
        return {
            "planning": self.planning,
            "implementation": self.implementation,
            "verification": self.verification,
            "fallback": self.fallback,
            "review": self.review,
        }

    @property
    def total(self) -> int:
        return self.planning + self.implementation + self.verification + self.fallback + self.review


def allocate(
    *,
    available_seconds: float | None,
    verification_reserve_seconds: int,
    difficulty_band: str,
) -> PhaseQuotas:
    if available_seconds is None:
        total = max(900, verification_reserve_seconds + 480)
    else:
        total = max(180, int(available_seconds))
    verify = max(60, min(total // 2, int(verification_reserve_seconds)))
    remaining = max(0, total - verify)

    if difficulty_band in {"high", "very_high"}:
        planning_share, implementation_share, fallback_share, review_share = 0.12, 0.55, 0.20, 0.13
    elif difficulty_band == "medium":
        planning_share, implementation_share, fallback_share, review_share = 0.10, 0.58, 0.17, 0.15
    else:
        planning_share, implementation_share, fallback_share, review_share = 0.08, 0.62, 0.12, 0.18

    planning = max(30, int(remaining * planning_share))
    implementation = max(60, int(remaining * implementation_share))
    fallback = max(30, int(remaining * fallback_share))
    review = max(30, remaining - planning - implementation - fallback)

    overflow = planning + implementation + fallback + review + verify - total
    if overflow > 0:
        reducible = max(0, implementation - 60)
        take = min(reducible, overflow)
        implementation -= take
        overflow -= take
    if overflow > 0:
        reducible = max(0, fallback - 30)
        take = min(reducible, overflow)
        fallback -= take
        overflow -= take
    if overflow > 0:
        reducible = max(0, review - 30)
        take = min(reducible, overflow)
        review -= take
        overflow -= take
    if overflow > 0:
        planning = max(30, planning - overflow)

    return PhaseQuotas(planning, implementation, verify, fallback, review)


def reallocate_unused(quotas: PhaseQuotas, *, phase: str, unused_seconds: int) -> PhaseQuotas:
    unused = max(0, int(unused_seconds))
    if unused == 0:
        return quotas
    values = quotas.as_dict()
    if phase not in values:
        raise ValueError("unknown phase")
    values[phase] = max(0, values[phase] - unused)
    targets = {
        "planning": ("implementation", "verification"),
        "implementation": ("verification", "fallback"),
        "verification": ("review", "fallback"),
        "fallback": ("verification", "review"),
        "review": ("verification", "fallback"),
    }[phase]
    first = unused * 2 // 3
    second = unused - first
    values[targets[0]] += first
    values[targets[1]] += second
    return PhaseQuotas(**values)

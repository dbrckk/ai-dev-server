"""Predictive difficulty and verification-reserve estimator.

The estimator is intentionally deterministic and bounded. It does not execute
code or inspect secrets; callers pass aggregate repository and verification
signals only.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DifficultyEstimate:
    score: float
    band: str
    verification_reserve_seconds: int
    recommended_work_passes: int
    recommended_agent_limit: int

    def as_dict(self) -> dict:
        return {
            "score": round(self.score, 3),
            "band": self.band,
            "verification_reserve_seconds": self.verification_reserve_seconds,
            "recommended_work_passes": self.recommended_work_passes,
            "recommended_agent_limit": self.recommended_agent_limit,
        }


def estimate(
    *,
    file_count: int,
    source_bytes: int,
    previous_failures: int,
    verification_seconds: float | None,
    bootstrap_passed: bool,
) -> DifficultyEstimate:
    if type(file_count) is not int or file_count < 0:
        raise ValueError("file_count invalid")
    if type(source_bytes) is not int or source_bytes < 0:
        raise ValueError("source_bytes invalid")
    if type(previous_failures) is not int or previous_failures < 0:
        raise ValueError("previous_failures invalid")

    verify = 0.0 if verification_seconds is None else max(0.0, float(verification_seconds))
    score = 0.0
    score += min(30.0, file_count / 8.0)
    score += min(25.0, source_bytes / 120_000.0)
    score += min(25.0, previous_failures * 5.0)
    score += min(15.0, verify / 20.0)
    if not bootstrap_passed:
        score += 15.0
    score = max(0.0, min(100.0, score))

    if score < 25.0:
        band = "low"
        reserve = max(90, int(verify * 1.5))
        passes = 1
        agents = 1
    elif score < 55.0:
        band = "medium"
        reserve = max(120, int(verify * 1.75))
        passes = 2
        agents = 1
    elif score < 80.0:
        band = "high"
        reserve = max(180, int(verify * 2.0))
        passes = 2
        agents = 2
    else:
        band = "very_high"
        reserve = max(240, int(verify * 2.5))
        passes = 2
        agents = 2

    return DifficultyEstimate(
        score=score,
        band=band,
        verification_reserve_seconds=min(900, reserve),
        recommended_work_passes=passes,
        recommended_agent_limit=agents,
    )


def can_start_generation(*, remaining_seconds: float | None, reserve_seconds: int, minimum_generation_seconds: int = 90) -> bool:
    if remaining_seconds is None:
        return True
    remaining = max(0.0, float(remaining_seconds))
    if type(reserve_seconds) is not int or reserve_seconds < 0:
        raise ValueError("reserve_seconds invalid")
    if type(minimum_generation_seconds) is not int or minimum_generation_seconds < 1:
        raise ValueError("minimum_generation_seconds invalid")
    return remaining >= reserve_seconds + minimum_generation_seconds

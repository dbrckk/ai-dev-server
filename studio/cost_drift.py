"""Phase cost drift detection for autonomous execution."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CostDriftDetector:
    elevated_ratio: float = 1.5
    severe_ratio: float = 2.0
    samples: list[dict] = field(default_factory=list)

    def record(self, *, phase: str, expected_seconds: float, observed_seconds: float, baseline: dict | None = None) -> dict:
        expected = max(1.0, float(expected_seconds))
        observed = max(0.0, float(observed_seconds))
        ratio = observed / expected
        source = "fixed_ratio"
        normalized_deviation = None
        if isinstance(baseline, dict):
            mean = max(1.0, float(baseline.get("ema_seconds", 0.0)))
            deviation = max(1.0, float(baseline.get("ema_abs_deviation", 0.0)))
            normalized_deviation = (observed - mean) / deviation
            source = "historical"
            if normalized_deviation >= 4.0:
                level = "severe"
            elif normalized_deviation >= 2.5:
                level = "elevated"
            else:
                level = "normal"
        elif ratio >= self.severe_ratio:
            level = "severe"
        elif ratio >= self.elevated_ratio:
            level = "elevated"
        else:
            level = "normal"
        sample = {
            "phase": phase,
            "expected_seconds": round(expected, 3),
            "observed_seconds": round(observed, 3),
            "ratio": round(ratio, 3),
            "level": level,
            "source": source,
        }
        if normalized_deviation is not None:
            sample["normalized_deviation"] = round(normalized_deviation, 3)
        self.samples.append(sample)
        return sample

    def decision(self) -> dict:
        severe = [x for x in self.samples if x["level"] == "severe"]
        elevated = [x for x in self.samples if x["level"] == "elevated"]
        if len(severe) >= 2:
            return {
                "action": "stop",
                "reason": "multiple phases exceeded predicted cost by at least 2x",
            }
        if severe:
            return {
                "action": "replan",
                "reason": severe[-1]["phase"] + " exceeded predicted cost by at least 2x",
            }
        if len(elevated) >= 2:
            return {
                "action": "reduce_exploration",
                "reason": "multiple phases exceeded predicted cost by at least 1.5x",
            }
        if elevated:
            return {
                "action": "reduce_exploration",
                "reason": elevated[-1]["phase"] + " exceeded predicted cost by at least 1.5x",
            }
        return {"action": "continue", "reason": "observed phase costs remain within prediction"}

    def exploration_multiplier(self) -> float:
        action = self.decision()["action"]
        if action == "reduce_exploration":
            return 0.5
        if action in {"replan", "stop"}:
            return 0.0
        return 1.0

    def snapshot(self) -> dict:
        return {
            "samples": list(self.samples[-20:]),
            "decision": self.decision(),
            "exploration_multiplier": self.exploration_multiplier(),
        }

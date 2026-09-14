"""Dynamic multi-model portfolio policy."""
from __future__ import annotations

from dataclasses import dataclass

PORTFOLIO_ROLES = (
    "product",
    "design",
    "implementation",
    "tests",
    "review",
    "visual",
    "security_fix",
    "release_fix",
)

INDEPENDENT_ROLES = {"review", "visual"}


@dataclass(frozen=True)
class PortfolioChoice:
    role: str
    provider: str
    model: str
    score: float
    independent_from: str | None = None

    def as_dict(self) -> dict:
        return {
            "role": self.role,
            "provider": self.provider,
            "model": self.model,
            "score": round(float(self.score), 4),
            "independent_from": self.independent_from,
        }


def choose(
    ranked_by_role: dict[str, list[dict]],
    *,
    implementation_provider: str | None = None,
    implementation_model: str | None = None,
) -> dict:
    choices = {}
    for role in PORTFOLIO_ROLES:
        rows = ranked_by_role.get(role)
        if not isinstance(rows, list) or not rows:
            continue

        selected = None
        if role in INDEPENDENT_ROLES and (implementation_provider or implementation_model):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                if implementation_provider and row.get("provider") == implementation_provider:
                    continue
                if implementation_model and row.get("model") == implementation_model:
                    continue
                selected = row
                break

        if selected is None:
            selected = next((row for row in rows if isinstance(row, dict)), None)
        if selected is None:
            continue

        choices[role] = PortfolioChoice(
            role=role,
            provider=str(selected.get("provider") or ""),
            model=str(selected.get("model") or ""),
            score=float(selected.get("score", 0.0) or 0.0),
            independent_from=(
                implementation_provider
                if role in INDEPENDENT_ROLES and implementation_provider
                else None
            ),
        ).as_dict()

    return {
        "roles": choices,
        "implementation_identity": {
            "provider": implementation_provider,
            "model": implementation_model,
        },
    }

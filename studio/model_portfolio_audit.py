"""Audit diversity and independence of a multi-model portfolio."""
from __future__ import annotations


def _identity(row: dict | None) -> tuple[str, str] | None:
    if not isinstance(row, dict):
        return None
    provider = row.get("provider")
    model = row.get("model")
    if not isinstance(provider, str) or not provider:
        return None
    if not isinstance(model, str) or not model:
        return None
    return provider, model


def audit(selections: dict) -> dict:
    if not isinstance(selections, dict):
        return {
            "roles_observed": 0,
            "unique_providers": 0,
            "unique_models": 0,
            "review_independent": None,
            "diversity_ratio": 0.0,
        }

    identities = {}
    for role, row in selections.items():
        identity = _identity(row)
        if identity is not None:
            identities[str(role)] = identity

    providers = {provider for provider, _ in identities.values()}
    models = {model for _, model in identities.values()}
    role_count = len(identities)
    diversity_ratio = (
        len(set(identities.values())) / role_count
        if role_count
        else 0.0
    )

    impl = identities.get("implementation")
    review = identities.get("review")
    review_independent = None
    if impl is not None and review is not None:
        review_independent = (
            impl[0] != review[0]
            and impl[1] != review[1]
        )

    return {
        "roles_observed": role_count,
        "unique_providers": len(providers),
        "unique_models": len(models),
        "review_independent": review_independent,
        "diversity_ratio": round(diversity_ratio, 4),
        "identities": {
            role: {"provider": provider, "model": model}
            for role, (provider, model) in sorted(identities.items())
        },
    }

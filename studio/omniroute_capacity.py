"""Read-only adapter for OmniRoute live free-tier capacity summary.

The scheduler treats OmniRoute as a single pooled free-capacity provider. Public
catalog totals are useful telemetry, but schedulable capacity is trusted only
when OmniRoute returns authenticated usage fields (usedThisMonth and remaining).
Anonymous summaries therefore fail closed to zero available tokens.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SUMMARY_PATH = "/api/free-tier/summary"


class OmniRouteCapacityError(ValueError):
    """Raised when OmniRoute capacity cannot be fetched or validated."""


def _nonnegative_int(value, *, field: str, nullable: bool = False) -> int | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise OmniRouteCapacityError(f"{field} must be a non-negative integer")
    if value < 0:
        raise OmniRouteCapacityError(f"{field} must be a non-negative integer")
    return value


def _optional_text(value, *, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise OmniRouteCapacityError(f"{field} must be a string or null")
    return value


@dataclass(frozen=True)
class OmniRouteCapacitySnapshot:
    steady_recurring_tokens: int
    used_this_month: int | None
    remaining_tokens: int | None
    catalog_updated_at: str | None = None
    catalog_source: str | None = None

    @property
    def authenticated_usage(self) -> bool:
        return self.used_this_month is not None and self.remaining_tokens is not None

    def provider_row(self, name: str = "omniroute") -> dict:
        """Return a row accepted by capacity_scheduler.provider_capacities.

        Extra telemetry fields are deliberately retained for callers that persist
        the row before normalization. capacity_scheduler ignores unknown fields,
        so this stays backward compatible.
        """
        provider_name = str(name or "").strip()
        if not provider_name:
            raise OmniRouteCapacityError("provider name must not be empty")
        return {
            "name": provider_name,
            "available_tokens": self.remaining_tokens if self.authenticated_usage else 0,
            "unmetered": False,
            "free_preferred": True,
            "paid": False,
            "source": "omniroute-free-tier",
            "authenticated_usage": self.authenticated_usage,
            "steady_recurring_tokens": self.steady_recurring_tokens,
            "used_this_month": self.used_this_month,
            "remaining_tokens": self.remaining_tokens,
            "catalog_updated_at": self.catalog_updated_at,
            "catalog_source": self.catalog_source,
        }


def parse_summary(payload: dict) -> OmniRouteCapacitySnapshot:
    """Validate an OmniRoute /api/free-tier/summary response."""
    if not isinstance(payload, dict):
        raise OmniRouteCapacityError("summary payload must be a JSON object")

    steady = _nonnegative_int(
        payload.get("steadyRecurringTokens"),
        field="steadyRecurringTokens",
    )
    used = _nonnegative_int(
        payload.get("usedThisMonth"),
        field="usedThisMonth",
        nullable=True,
    )
    remaining = _nonnegative_int(
        payload.get("remaining"),
        field="remaining",
        nullable=True,
    )

    if (used is None) != (remaining is None):
        raise OmniRouteCapacityError(
            "usedThisMonth and remaining must both be present or both be null"
        )

    return OmniRouteCapacitySnapshot(
        steady_recurring_tokens=steady,
        used_this_month=used,
        remaining_tokens=remaining,
        catalog_updated_at=_optional_text(
            payload.get("catalogUpdatedAt"),
            field="catalogUpdatedAt",
        ),
        catalog_source=_optional_text(
            payload.get("catalogSource"),
            field="catalogSource",
        ),
    )


def _summary_url(base_url: str) -> str:
    value = str(base_url or "").strip()
    if not value:
        raise OmniRouteCapacityError("OmniRoute base URL must not be empty")
    value = value.rstrip("/")
    if value.endswith(SUMMARY_PATH):
        return value
    if value.endswith("/v1"):
        value = value[:-3].rstrip("/")
    return value + SUMMARY_PATH


def fetch_summary(
    base_url: str,
    *,
    api_key: str | None = None,
    timeout: float = 5.0,
    opener: Callable = urlopen,
) -> OmniRouteCapacitySnapshot:
    """Fetch and validate live OmniRoute free-tier capacity.

    api_key is sent only as a Bearer header and is never included in errors.
    The injectable opener keeps networking out of unit tests.
    """
    try:
        timeout_value = float(timeout)
    except (TypeError, ValueError) as exc:
        raise OmniRouteCapacityError("timeout must be a positive number") from exc
    if timeout_value <= 0:
        raise OmniRouteCapacityError("timeout must be a positive number")

    headers = {"Accept": "application/json"}
    token = str(api_key or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(_summary_url(base_url), headers=headers, method="GET")
    try:
        with opener(request, timeout=timeout_value) as response:
            raw = response.read()
    except (HTTPError, URLError, OSError) as exc:
        raise OmniRouteCapacityError(
            f"failed to fetch OmniRoute capacity: {exc.__class__.__name__}"
        ) from exc

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError) as exc:
        raise OmniRouteCapacityError("OmniRoute returned invalid JSON") from exc
    return parse_summary(payload)

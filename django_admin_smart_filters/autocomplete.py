"""Server-side autocomplete request parsing and paginated search."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from django_admin_smart_filters.contracts import FilterSpec
from django_admin_smart_filters.validation import validate_filter_spec

MIN_AUTOCOMPLETE_QUERY_LENGTH = 2
DEFAULT_AUTOCOMPLETE_PAGE_SIZE = 20
MAX_AUTOCOMPLETE_PAGE_SIZE = 50


@dataclass(frozen=True)
class AutocompleteRequest:
    """Validated autocomplete request inputs."""

    spec: FilterSpec
    query: str
    page: int
    limit: int
    state: Mapping[str, Any]


@dataclass(frozen=True)
class AutocompleteResultPage:
    """Paginated autocomplete results."""

    results: list[dict[str, str]]
    page: int
    limit: int
    has_next: bool


def parse_autocomplete_request(
    spec: FilterSpec,
    params: Mapping[str, Any],
    *,
    state: Mapping[str, Any] | None = None,
) -> AutocompleteRequest:
    """Parse and validate one autocomplete request from query parameters."""

    validate_filter_spec(spec)
    if spec.filter_kind != "autocomplete":
        raise ValueError(
            f"Invalid autocomplete spec '{spec.field_name}': filter kind must be 'autocomplete'."
        )

    requested_field = str(params.get("field", "")).strip()
    if requested_field and requested_field not in {spec.field_name, spec.param_name}:
        raise ValueError(
            f"Invalid autocomplete field '{requested_field}'. Expected '{spec.field_name}' or '{spec.param_name}'."
        )

    query = str(params.get("query", "")).strip()
    page = _parse_positive_int(params.get("page"), "page", default=1)
    requested_limit = _parse_positive_int(
        params.get("limit"), "limit", default=DEFAULT_AUTOCOMPLETE_PAGE_SIZE
    )
    limit = min(requested_limit, MAX_AUTOCOMPLETE_PAGE_SIZE)

    return AutocompleteRequest(
        spec=spec,
        query=query,
        page=page,
        limit=limit,
        state=dict(state or {}),
    )


def search_autocomplete_options(
    queryset: Any, request: AutocompleteRequest
) -> AutocompleteResultPage:
    """Run server-side autocomplete search with deterministic pagination."""

    if len(request.query) < MIN_AUTOCOMPLETE_QUERY_LENGTH:
        return AutocompleteResultPage(
            results=[], page=request.page, limit=request.limit, has_next=False
        )

    field_name = request.spec.field_name
    ordered = (
        queryset.filter(**{f"{field_name}__icontains": request.query})
        .order_by(field_name, "pk")
        .values_list("pk", field_name)
    )

    offset = (request.page - 1) * request.limit
    window = list(ordered[offset : offset + request.limit + 1])
    has_next = len(window) > request.limit
    visible = window[: request.limit]

    results = [
        {
            "id": str(pk),
            "value": str(pk),
            "label": str(label),
        }
        for pk, label in visible
    ]

    return AutocompleteResultPage(
        results=results, page=request.page, limit=request.limit, has_next=has_next
    )


def _parse_positive_int(raw: Any, field_name: str, *, default: int) -> int:
    if raw in {None, ""}:
        return default

    try:
        value = int(str(raw))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: expected a positive integer.") from exc

    if value < 1:
        raise ValueError(f"Invalid {field_name}: expected a value >= 1.")

    return value


__all__ = [
    "AutocompleteRequest",
    "AutocompleteResultPage",
    "DEFAULT_AUTOCOMPLETE_PAGE_SIZE",
    "MAX_AUTOCOMPLETE_PAGE_SIZE",
    "MIN_AUTOCOMPLETE_QUERY_LENGTH",
    "parse_autocomplete_request",
    "search_autocomplete_options",
]

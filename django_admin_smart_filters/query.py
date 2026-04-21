"""Filter-kind aware queryset application helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date
from typing import Any

from django_admin_smart_filters.contracts import FilterSpec
from django_admin_smart_filters.validation import validate_filter_spec

TRUE_VALUES = {"1", "true", "t", "yes", "y", "on"}
FALSE_VALUES = {"0", "false", "f", "no", "n", "off"}


def apply_filter_value(queryset: Any, spec: FilterSpec, value: Any) -> Any:
    """Apply one normalized filter value to a queryset-like object."""

    validate_filter_spec(spec)
    normalized = _normalize_for_kind(spec.filter_kind, value, spec.param_name)

    if normalized is None:
        return queryset

    filtered = _apply_base_filter(queryset, spec, normalized)
    if spec.query_hook is not None:
        return spec.query_hook(filtered, normalized, spec)

    return filtered


def apply_filter_state(
    queryset: Any, specs: Iterable[FilterSpec], state: Mapping[str, Any]
) -> Any:
    """Apply all known state values to a queryset deterministically by spec order."""

    current = queryset
    for spec in specs:
        validate_filter_spec(spec)
        if spec.param_name not in state:
            continue
        current = apply_filter_value(current, spec, state[spec.param_name])
    return current


def _apply_base_filter(queryset: Any, spec: FilterSpec, normalized: Any) -> Any:
    field_name = spec.field_name

    if spec.filter_kind in {"dropdown", "boolean_toggle"}:
        return queryset.filter(**{field_name: normalized})

    if spec.filter_kind == "multi_select":
        return queryset.filter(**{f"{field_name}__in": normalized})

    if spec.filter_kind == "date_range":
        current = queryset
        start = normalized.get("start")
        end = normalized.get("end")
        if start is not None:
            current = current.filter(**{f"{field_name}__gte": start.isoformat()})
        if end is not None:
            current = current.filter(**{f"{field_name}__lte": end.isoformat()})
        return current

    if spec.filter_kind == "numeric_range":
        current = queryset
        minimum = normalized.get("min")
        maximum = normalized.get("max")
        if minimum is not None:
            current = current.filter(**{f"{field_name}__gte": minimum})
        if maximum is not None:
            current = current.filter(**{f"{field_name}__lte": maximum})
        return current

    return queryset.filter(**{field_name: normalized})


def _normalize_for_kind(filter_kind: str, value: Any, param_name: str) -> Any:
    if filter_kind == "dropdown":
        return _normalize_single_value(value)

    if filter_kind == "multi_select":
        return _normalize_multi_select(value)

    if filter_kind == "date_range":
        return _normalize_date_range(value, param_name)

    if filter_kind == "numeric_range":
        return _normalize_numeric_range(value, param_name)

    if filter_kind == "boolean_toggle":
        return _normalize_boolean(value, param_name)

    return _normalize_single_value(value)


def _normalize_single_value(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _normalize_multi_select(value: Any) -> list[str] | None:
    if value is None:
        return None

    if isinstance(value, str):
        candidates: list[Any] = [part for part in value.split(",")]
    elif isinstance(value, Iterable):
        candidates = list(value)
    else:
        candidates = [value]

    normalized = [str(item).strip() for item in candidates if str(item).strip()]
    return normalized or None


def _normalize_date_range(value: Any, param_name: str) -> dict[str, date | None] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"Invalid date range for '{param_name}'.")

    start_raw = _first_non_empty(value.get("start"), value.get("min"))
    end_raw = _first_non_empty(value.get("end"), value.get("max"))

    if start_raw is None and end_raw is None:
        return None

    try:
        start = date.fromisoformat(start_raw) if start_raw is not None else None
        end = date.fromisoformat(end_raw) if end_raw is not None else None
    except ValueError as exc:
        raise ValueError(f"Invalid date range for '{param_name}'.") from exc

    return {"start": start, "end": end}


def _normalize_numeric_range(
    value: Any, param_name: str
) -> dict[str, float | None] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"Invalid numeric range for '{param_name}'.")

    minimum_raw = _first_non_empty(value.get("min"), value.get("start"))
    maximum_raw = _first_non_empty(value.get("max"), value.get("end"))

    if minimum_raw is None and maximum_raw is None:
        return None

    try:
        minimum = float(minimum_raw) if minimum_raw is not None else None
        maximum = float(maximum_raw) if maximum_raw is not None else None
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid numeric range for '{param_name}'.") from exc

    return {"min": minimum, "max": maximum}


def _normalize_boolean(value: Any, param_name: str) -> bool:
    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in TRUE_VALUES:
        return True
    if text in FALSE_VALUES:
        return False
    raise ValueError(f"Invalid boolean value for '{param_name}': {value!r}.")


def _first_non_empty(*values: object) -> str | None:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


__all__ = ["apply_filter_value", "apply_filter_state"]

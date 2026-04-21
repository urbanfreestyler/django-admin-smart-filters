"""URL-driven filter state parsing and serialization."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from django.http import QueryDict

from django_admin_smart_filters.contracts import FilterSpec
from django_admin_smart_filters.validation import validate_filter_spec

TRUE_VALUES = {"1", "true", "t", "yes", "y", "on"}
FALSE_VALUES = {"0", "false", "f", "no", "n", "off"}


def parse_filter_state(
    specs: Iterable[FilterSpec], querydict: QueryDict
) -> dict[str, Any]:
    """Parse deterministic filter state from query parameters."""

    normalized_specs = _validated_specs(specs)
    parsed: dict[str, Any] = {}

    for spec in normalized_specs:
        value = _parse_spec_value(spec, querydict)
        if value is not None:
            parsed[spec.param_name] = value

    return parsed


def serialize_filter_state(
    specs: Iterable[FilterSpec], state: Mapping[str, Any]
) -> QueryDict:
    """Serialize normalized filter state into deterministic query parameters."""

    normalized_specs = _validated_specs(specs)
    query = QueryDict("", mutable=True)

    for spec in normalized_specs:
        if spec.param_name not in state:
            continue

        value = state[spec.param_name]

        if spec.filter_kind == "multi_select":
            items = [str(item) for item in value if str(item).strip()]
            if items:
                query.setlist(spec.param_name, items)
            continue

        if spec.filter_kind == "date_range":
            if not isinstance(value, Mapping):
                continue
            start = value.get("start")
            end = value.get("end")
            if start:
                query[f"{spec.param_name}_start"] = str(start)
            if end:
                query[f"{spec.param_name}_end"] = str(end)
            continue

        if spec.filter_kind == "numeric_range":
            if not isinstance(value, Mapping):
                continue
            minimum = value.get("min")
            maximum = value.get("max")
            if minimum is not None and str(minimum).strip() != "":
                query[f"{spec.param_name}_min"] = str(minimum)
            if maximum is not None and str(maximum).strip() != "":
                query[f"{spec.param_name}_max"] = str(maximum)
            continue

        if spec.filter_kind == "boolean_toggle":
            query[spec.param_name] = "true" if bool(value) else "false"
            continue

        if value is not None and str(value).strip() != "":
            query[spec.param_name] = str(value)

    return query


def _validated_specs(specs: Iterable[FilterSpec]) -> list[FilterSpec]:
    normalized_specs = list(specs)
    for spec in normalized_specs:
        validate_filter_spec(spec)
    return normalized_specs


def _parse_spec_value(spec: FilterSpec, querydict: QueryDict) -> Any:
    if spec.filter_kind == "dropdown":
        return _parse_single_value(querydict, spec.param_name)

    if spec.filter_kind == "multi_select":
        return _parse_multiselect(querydict, spec.param_name)

    if spec.filter_kind == "date_range":
        return _parse_date_range(querydict, spec.param_name)

    if spec.filter_kind == "numeric_range":
        return _parse_numeric_range(querydict, spec.param_name)

    if spec.filter_kind == "boolean_toggle":
        return _parse_boolean(querydict, spec.param_name)

    return _parse_single_value(querydict, spec.param_name)


def _parse_single_value(querydict: QueryDict, param_name: str) -> str | None:
    raw = querydict.get(param_name)
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def _parse_multiselect(querydict: QueryDict, param_name: str) -> list[str] | None:
    raw_values = querydict.getlist(param_name)
    values: list[str] = []

    for raw in raw_values:
        parts = str(raw).split(",")
        for part in parts:
            value = part.strip()
            if value:
                values.append(value)

    return values or None


def _parse_boolean(querydict: QueryDict, param_name: str) -> bool | None:
    raw = querydict.get(param_name)
    if raw is None:
        return None

    value = str(raw).strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False

    raise ValueError(f"Invalid boolean value for '{param_name}': {raw!r}.")


def _parse_date_range(
    querydict: QueryDict, param_name: str
) -> dict[str, str | None] | None:
    start = _first_non_empty(
        querydict.get(f"{param_name}_start"),
        querydict.get(f"{param_name}_min"),
    )
    end = _first_non_empty(
        querydict.get(f"{param_name}_end"),
        querydict.get(f"{param_name}_max"),
    )

    if start is None and end is None:
        return None

    return {"start": start, "end": end}


def _parse_numeric_range(
    querydict: QueryDict, param_name: str
) -> dict[str, float | None] | None:
    minimum_raw = _first_non_empty(
        querydict.get(f"{param_name}_min"),
        querydict.get(f"{param_name}_start"),
    )
    maximum_raw = _first_non_empty(
        querydict.get(f"{param_name}_max"),
        querydict.get(f"{param_name}_end"),
    )

    if minimum_raw is None and maximum_raw is None:
        return None

    try:
        minimum = float(minimum_raw) if minimum_raw is not None else None
        maximum = float(maximum_raw) if maximum_raw is not None else None
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid numeric range for '{param_name}'.") from exc

    return {"min": minimum, "max": maximum}


def _first_non_empty(*values: object) -> str | None:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


__all__ = ["parse_filter_state", "serialize_filter_state"]

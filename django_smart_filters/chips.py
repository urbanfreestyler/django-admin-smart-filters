"""Active filter chip view-model and URL action helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from django.http import QueryDict

from django_smart_filters.contracts import FilterSpec


def build_active_filter_chips(
    filter_specs: Iterable[FilterSpec],
    filter_state: Mapping[str, Any],
    field_labels: Mapping[str, str] | None = None,
) -> list[dict[str, Any]]:
    labels = field_labels or {}
    chips: list[dict[str, Any]] = []

    for spec in filter_specs:
        value = filter_state.get(spec.param_name)
        if value is None:
            continue

        title = labels.get(spec.field_name) or spec.field_name.replace("_", " ").title()
        chips.extend(_chips_for_spec(spec, title, value))

    return chips


def build_remove_one_url(current_query: QueryDict, target_chip: Mapping[str, Any]) -> str:
    action = target_chip.get("remove_action")
    if not isinstance(action, Mapping):
        return _querydict_to_querystring(current_query)

    query = current_query.copy()
    mode = action.get("mode")
    param = str(action.get("param", ""))

    if mode == "single":
        query.pop(param, None)
    elif mode == "remove_value":
        target_value = str(action.get("value", ""))
        remaining = [item for item in query.getlist(param) if str(item) != target_value]
        if remaining:
            query.setlist(param, remaining)
        else:
            query.pop(param, None)
    elif mode == "range":
        for key in action.get("keys", []):
            query.pop(str(key), None)

    return _querydict_to_querystring(query)


def build_reset_all_url(current_query: QueryDict, managed_params: Iterable[str]) -> str:
    query = current_query.copy()
    for param in managed_params:
        query.pop(param, None)
        query.pop(f"{param}_start", None)
        query.pop(f"{param}_end", None)
        query.pop(f"{param}_min", None)
        query.pop(f"{param}_max", None)

    return _querydict_to_querystring(query)


def _chips_for_spec(spec: FilterSpec, title: str, value: Any) -> list[dict[str, Any]]:
    if spec.filter_kind == "multi_select":
        return [
            {
                "field_name": spec.field_name,
                "param_name": spec.param_name,
                "label": f"{title}: {item}",
                "remove_action": {"mode": "remove_value", "param": spec.param_name, "value": str(item)},
            }
            for item in value
            if str(item).strip()
        ]

    if spec.filter_kind in {"date_range", "numeric_range"} and isinstance(value, Mapping):
        if spec.filter_kind == "date_range":
            start = value.get("start")
            end = value.get("end")
            summary = _range_summary(start, end)
            keys = [f"{spec.param_name}_start", f"{spec.param_name}_end", f"{spec.param_name}_min", f"{spec.param_name}_max"]
        else:
            minimum = value.get("min")
            maximum = value.get("max")
            summary = _range_summary(minimum, maximum)
            keys = [f"{spec.param_name}_min", f"{spec.param_name}_max", f"{spec.param_name}_start", f"{spec.param_name}_end"]

        return [
            {
                "field_name": spec.field_name,
                "param_name": spec.param_name,
                "label": f"{title}: {summary}",
                "remove_action": {"mode": "range", "keys": keys},
            }
        ]

    text = str(value)
    return [
        {
            "field_name": spec.field_name,
            "param_name": spec.param_name,
            "label": f"{title}: {text}",
            "remove_action": {"mode": "single", "param": spec.param_name},
        }
    ]


def _range_summary(start: object, end: object) -> str:
    if start is not None and end is not None:
        return f"{start} to {end}"
    if start is not None:
        return f"from {start}"
    if end is not None:
        return f"to {end}"
    return "(empty)"


def _querydict_to_querystring(query: QueryDict) -> str:
    pairs = sorted(query.lists(), key=lambda item: item[0])
    encoded = QueryDict("", mutable=True)
    for key, values in pairs:
        for value in sorted(str(v) for v in values):
            encoded.appendlist(key, value)
    text = encoded.urlencode()
    return f"?{text}" if text else ""


__all__ = [
    "build_active_filter_chips",
    "build_remove_one_url",
    "build_reset_all_url",
]

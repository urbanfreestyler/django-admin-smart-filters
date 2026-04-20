from __future__ import annotations

import pytest
from django.conf import settings
from django.http import QueryDict

from django_smart_filters.builder import Filter
from django_smart_filters.declarations import ClassFilterDeclaration, normalize_class_declaration
from django_smart_filters.state import parse_filter_state, serialize_filter_state


if not settings.configured:
    settings.configure(DEFAULT_CHARSET="utf-8")


def _specs():
    return [
        Filter.field("status").dropdown().to_spec(),
        Filter.field("category").multi_select().to_spec(),
        Filter.field("created").date_range().to_spec(),
        Filter.field("score").numeric_range().to_spec(),
        Filter.field("active").boolean_toggle().to_spec(),
    ]


def test_parse_dropdown_and_boolean_toggle_from_single_value_params() -> None:
    query = QueryDict("status=open&active=true")

    state = parse_filter_state(_specs(), query)

    assert state["status"] == "open"
    assert state["active"] is True


def test_parse_multiselect_from_repeated_and_csv_values_stable_order() -> None:
    query = QueryDict("category__in=beta&category__in=alpha,gamma")

    state = parse_filter_state(_specs(), query)

    assert state["category__in"] == ["beta", "alpha", "gamma"]


def test_parse_date_and_numeric_ranges_from_explicit_keys() -> None:
    query = QueryDict(
        "created_start=2026-01-01&created_end=2026-01-31&score_min=10&score_max=20"
    )

    state = parse_filter_state(_specs(), query)

    assert state["created"] == {"start": "2026-01-01", "end": "2026-01-31"}
    assert state["score"] == {"min": 10.0, "max": 20.0}


def test_parse_range_supports_min_max_for_dates_and_start_end_for_numeric() -> None:
    query = QueryDict(
        "created_min=2026-02-01&created_max=2026-02-03&score_start=1.5&score_end=2.5"
    )

    state = parse_filter_state(_specs(), query)

    assert state["created"] == {"start": "2026-02-01", "end": "2026-02-03"}
    assert state["score"] == {"min": 1.5, "max": 2.5}


def test_serialize_then_parse_roundtrip_is_equivalent() -> None:
    specs = _specs()
    original_state = {
        "status": "queued",
        "category__in": ["foo", "bar"],
        "created": {"start": "2026-03-01", "end": "2026-03-10"},
        "score": {"min": 3.5, "max": 9},
        "active": False,
    }

    serialized = serialize_filter_state(specs, original_state)
    reparsed = parse_filter_state(specs, serialized)

    assert reparsed == {
        "status": "queued",
        "category__in": ["foo", "bar"],
        "created": {"start": "2026-03-01", "end": "2026-03-10"},
        "score": {"min": 3.5, "max": 9.0},
        "active": False,
    }


def test_unknown_params_are_ignored_without_mutating_known_state() -> None:
    query = QueryDict("status=open&unknown=hack&score_min=1")

    state = parse_filter_state(_specs(), query)

    assert state == {"status": "open", "score": {"min": 1.0, "max": None}}


def test_malformed_numeric_range_raises_deterministic_error() -> None:
    query = QueryDict("score_min=not-a-number")

    with pytest.raises(ValueError, match="Invalid numeric range"):
        parse_filter_state(_specs(), query)


def test_parse_filter_state_validates_incoming_specs() -> None:
    invalid_spec = normalize_class_declaration(
        ClassFilterDeclaration(field_name="status", filter_kind="dropdown")
    )
    invalid_spec = type(invalid_spec)(
        field_name=invalid_spec.field_name,
        alias=invalid_spec.alias,
        filter_kind="not_supported",
        query_hook=invalid_spec.query_hook,
        widget_hook=invalid_spec.widget_hook,
        param_name=invalid_spec.param_name,
    )

    with pytest.raises(ValueError, match="Unsupported filter_kind"):
        parse_filter_state([invalid_spec], QueryDict("status=open"))

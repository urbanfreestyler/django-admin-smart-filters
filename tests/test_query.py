from __future__ import annotations

import pytest

from django_admin_smart_filters.builder import Filter
from django_admin_smart_filters.contracts import FilterSpec
from django_admin_smart_filters.query import apply_filter_state, apply_filter_value


class RecordingQuerySet:
    def __init__(self, calls: list[dict[str, object]] | None = None) -> None:
        self.calls = calls or []

    def filter(self, **kwargs: object) -> "RecordingQuerySet":
        return RecordingQuerySet(self.calls + [kwargs])


def _specs() -> list[FilterSpec]:
    return [
        Filter.field("status").dropdown().to_spec(),
        Filter.field("category").multi_select().to_spec(),
        Filter.field("created").date_range().to_spec(),
        Filter.field("score").numeric_range().to_spec(),
        Filter.field("active").boolean_toggle().to_spec(),
    ]


def test_dropdown_applies_equality_lookup() -> None:
    queryset = RecordingQuerySet()
    spec = Filter.field("status").dropdown().to_spec()

    updated = apply_filter_value(queryset, spec, "open")

    assert updated.calls == [{"status": "open"}]


def test_multiselect_applies_in_lookup() -> None:
    queryset = RecordingQuerySet()
    spec = Filter.field("category").multi_select().to_spec()

    updated = apply_filter_value(queryset, spec, ["a", "b"])

    assert updated.calls == [{"category__in": ["a", "b"]}]


def test_date_and_numeric_ranges_apply_only_present_bounds() -> None:
    queryset = RecordingQuerySet()
    date_spec = Filter.field("created").date_range().to_spec()
    numeric_spec = Filter.field("score").numeric_range().to_spec()

    updated = apply_filter_value(
        queryset, date_spec, {"start": "2026-01-01", "end": None}
    )
    updated = apply_filter_value(updated, numeric_spec, {"min": None, "max": 20})

    assert updated.calls == [{"created__gte": "2026-01-01"}, {"score__lte": 20.0}]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (True, True),
        (False, False),
        ("true", True),
        ("false", False),
        ("1", True),
        ("0", False),
    ],
)
def test_boolean_toggle_maps_true_false_consistently(
    raw: object, expected: bool
) -> None:
    queryset = RecordingQuerySet()
    spec = Filter.field("active").boolean_toggle().to_spec()

    updated = apply_filter_value(queryset, spec, raw)

    assert updated.calls == [{"active": expected}]


def test_mixed_filter_state_composes_deterministically() -> None:
    queryset = RecordingQuerySet()
    specs = _specs()
    state = {
        "status": "open",
        "category__in": ["a", "b"],
        "created": {"start": "2026-01-01", "end": "2026-01-31"},
        "score": {"min": 10, "max": 20},
        "active": "true",
    }

    updated = apply_filter_state(queryset, specs, state)

    assert updated.calls == [
        {"status": "open"},
        {"category__in": ["a", "b"]},
        {"created__gte": "2026-01-01"},
        {"created__lte": "2026-01-31"},
        {"score__gte": 10.0},
        {"score__lte": 20.0},
        {"active": True},
    ]


def test_query_hook_runs_after_base_normalization() -> None:
    observed: dict[str, object] = {}

    def query_hook(
        queryset: RecordingQuerySet, value: object, spec: FilterSpec
    ) -> RecordingQuerySet:
        observed["value"] = value
        observed["calls_before_hook"] = list(queryset.calls)
        observed["field"] = spec.field_name
        return queryset.filter(hooked=True)

    spec = FilterSpec(
        field_name="active",
        alias=None,
        filter_kind="boolean_toggle",
        query_hook=query_hook,
        widget_hook=None,
        param_name="active",
        component_key=None,
    )

    updated = apply_filter_value(RecordingQuerySet(), spec, "true")

    assert observed["value"] is True
    assert observed["calls_before_hook"] == [{"active": True}]
    assert observed["field"] == "active"
    assert updated.calls == [{"active": True}, {"hooked": True}]


def test_invalid_boolean_value_raises_error() -> None:
    queryset = RecordingQuerySet()
    spec = Filter.field("active").boolean_toggle().to_spec()

    with pytest.raises(ValueError, match="Invalid boolean value"):
        apply_filter_value(queryset, spec, "definitely")

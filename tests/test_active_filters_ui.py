from __future__ import annotations

from urllib.parse import parse_qsl

import pytest
from django.http import QueryDict

from django_admin_smart_filters.builder import Filter
from django_admin_smart_filters.state import parse_filter_state

from django_admin_smart_filters.chips import (
    build_active_filter_chips,
    build_remove_one_url,
    build_reset_all_url,
)


def _specs():
    return [
        Filter.field("status").dropdown().to_spec(),
        Filter.field("category").multi_select().to_spec(),
        Filter.field("created").date_range().to_spec(),
        Filter.field("score").numeric_range().to_spec(),
        Filter.field("active").boolean_toggle().to_spec(),
    ]


def _pairs(url: str) -> list[tuple[str, str]]:
    return parse_qsl(url.lstrip("?"), keep_blank_values=True)


def test_chip_labels_are_human_readable_and_param_keys_are_hidden() -> None:
    specs = _specs()
    state = parse_filter_state(
        specs,
        QueryDict(
            "status=open&category__in=alpha&category__in=beta&score_min=10&score_max=20"
        ),
    )

    chips = build_active_filter_chips(
        specs,
        state,
        {
            "status": "Status",
            "category": "Category",
            "score": "Score",
        },
    )

    labels = [chip["label"] for chip in chips]
    assert labels == [
        "Status: open",
        "Category: alpha",
        "Category: beta",
        "Score: 10.0 to 20.0",
    ]
    assert all("__" not in label for label in labels)
    assert all("_min" not in label and "_max" not in label for label in labels)


def test_remove_one_url_drops_target_chip_only_and_preserves_other_criteria() -> None:
    specs = _specs()
    query = QueryDict("status=open&category__in=alpha&category__in=beta&page=3")
    state = parse_filter_state(specs, query)
    chips = build_active_filter_chips(
        specs, state, {"status": "Status", "category": "Category"}
    )

    target = next(chip for chip in chips if chip["label"] == "Category: alpha")
    remove_url = build_remove_one_url(query, target)

    pairs = _pairs(remove_url)
    assert ("status", "open") in pairs
    assert ("category__in", "beta") in pairs
    assert ("page", "3") in pairs
    assert ("category__in", "alpha") not in pairs


def test_remove_one_flow_rebuilds_chip_state_without_targeted_chip() -> None:
    specs = _specs()
    labels = {"status": "Status", "category": "Category"}
    initial_query = QueryDict("status=open&category__in=alpha&category__in=beta")
    initial_state = parse_filter_state(specs, initial_query)
    initial_chips = build_active_filter_chips(specs, initial_state, labels)

    target = next(chip for chip in initial_chips if chip["label"] == "Category: alpha")
    next_state = parse_filter_state(
        specs, QueryDict(build_remove_one_url(initial_query, target).lstrip("?"))
    )
    next_chips = build_active_filter_chips(specs, next_state, labels)

    assert [chip["label"] for chip in next_chips] == ["Status: open", "Category: beta"]


def test_reset_all_url_removes_managed_filter_params_only() -> None:
    specs = _specs()
    managed_params = [spec.param_name for spec in specs]
    query = QueryDict("status=open&score_min=10&score_max=20&page=2&o=-created")

    reset_url = build_reset_all_url(query, managed_params)
    pairs = _pairs(reset_url)

    assert ("status", "open") not in pairs
    assert ("score_min", "10") not in pairs
    assert ("score_max", "20") not in pairs
    assert ("page", "2") in pairs
    assert ("o", "-created") in pairs


def test_reset_all_flow_results_in_no_active_chips() -> None:
    specs = _specs()
    managed_params = [spec.param_name for spec in specs]
    labels = {"status": "Status", "category": "Category", "score": "Score"}
    initial_query = QueryDict("status=open&category__in=alpha&score_min=10")

    reset_state = parse_filter_state(
        specs,
        QueryDict(build_reset_all_url(initial_query, managed_params).lstrip("?")),
    )

    assert build_active_filter_chips(specs, reset_state, labels) == []


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        (
            "status=open&category__in=beta&category__in=alpha&page=3",
            [
                ("category__in", "alpha"),
                ("page", "3"),
                ("status", "open"),
            ],
        ),
        (
            "page=3&status=open&category__in=alpha&category__in=beta",
            [
                ("category__in", "alpha"),
                ("page", "3"),
                ("status", "open"),
            ],
        ),
    ],
)
def test_remove_one_url_is_deterministic_for_mixed_filters(
    query: str, expected: list[tuple[str, str]]
) -> None:
    specs = _specs()
    querydict = QueryDict(query)
    state = parse_filter_state(specs, querydict)
    chips = build_active_filter_chips(
        specs, state, {"status": "Status", "category": "Category"}
    )

    target = next(chip for chip in chips if chip["label"] == "Category: beta")
    assert _pairs(build_remove_one_url(querydict, target)) == expected

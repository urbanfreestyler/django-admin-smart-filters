from __future__ import annotations

import pytest

from django_admin_smart_filters.autocomplete import (
    DEFAULT_AUTOCOMPLETE_PAGE_SIZE,
    MAX_AUTOCOMPLETE_PAGE_SIZE,
    MIN_AUTOCOMPLETE_QUERY_LENGTH,
    parse_autocomplete_request,
    search_autocomplete_options,
)
from django_admin_smart_filters.builder import Filter


class RecordingValuesList:
    def __init__(
        self, rows: list[tuple[int, str]], calls: list[tuple[str, object]]
    ) -> None:
        self._rows = rows
        self.calls = calls

    def __getitem__(self, item):
        self.calls.append(("slice", item))
        return self._rows[item]


class RecordingAutocompleteQuerySet:
    def __init__(
        self,
        rows: list[tuple[int, str]],
        *,
        calls: list[tuple[str, object]] | None = None,
    ) -> None:
        self._rows = rows
        self.calls = calls or []

    def filter(self, **kwargs: object) -> "RecordingAutocompleteQuerySet":
        self.calls.append(("filter", kwargs))
        key, value = next(iter(kwargs.items()))
        term = str(value).lower()
        filtered = [row for row in self._rows if term in row[1].lower()]
        return RecordingAutocompleteQuerySet(filtered, calls=self.calls)

    def order_by(self, *fields: str) -> "RecordingAutocompleteQuerySet":
        self.calls.append(("order_by", fields))
        assert fields[-1] == "pk"
        sorted_rows = sorted(self._rows, key=lambda row: (row[1], row[0]))
        return RecordingAutocompleteQuerySet(sorted_rows, calls=self.calls)

    def values_list(self, *fields: str) -> RecordingValuesList:
        self.calls.append(("values_list", fields))
        return RecordingValuesList(self._rows, calls=self.calls)


def _spec():
    return Filter.field("category").autocomplete().to_spec()


def test_parse_autocomplete_request_applies_defaults_and_caps_limit() -> None:
    spec = _spec()

    request = parse_autocomplete_request(spec, {"query": "alpha"})
    capped = parse_autocomplete_request(spec, {"query": "alpha", "limit": "999"})

    assert request.query == "alpha"
    assert request.page == 1
    assert request.limit == DEFAULT_AUTOCOMPLETE_PAGE_SIZE
    assert capped.limit == MAX_AUTOCOMPLETE_PAGE_SIZE


def test_parse_autocomplete_request_fails_fast_for_invalid_params() -> None:
    spec = _spec()

    with pytest.raises(ValueError, match="Invalid page"):
        parse_autocomplete_request(spec, {"query": "alpha", "page": "0"})

    with pytest.raises(ValueError, match="Invalid limit"):
        parse_autocomplete_request(spec, {"query": "alpha", "limit": "nope"})

    with pytest.raises(ValueError, match="Invalid autocomplete field"):
        parse_autocomplete_request(spec, {"query": "alpha", "field": "status"})


def test_parse_autocomplete_request_rejects_non_autocomplete_spec() -> None:
    spec = Filter.field("status").dropdown().to_spec()

    with pytest.raises(ValueError, match="Invalid autocomplete spec"):
        parse_autocomplete_request(spec, {"query": "open"})


def test_search_autocomplete_options_short_query_returns_empty_without_scan() -> None:
    rows = [(1, "Alpha"), (2, "Beta")]
    queryset = RecordingAutocompleteQuerySet(rows)
    request = parse_autocomplete_request(_spec(), {"query": "a"})

    page = search_autocomplete_options(queryset, request)

    assert len(request.query) < MIN_AUTOCOMPLETE_QUERY_LENGTH
    assert page.results == []
    assert page.has_next is False
    assert queryset.calls == []


def test_search_autocomplete_options_returns_minimal_payload_shape() -> None:
    rows = [(9, "Alpha")]
    queryset = RecordingAutocompleteQuerySet(rows)
    request = parse_autocomplete_request(_spec(), {"query": "alp"})

    page = search_autocomplete_options(queryset, request)

    assert page.results == [{"id": "9", "value": "9", "label": "Alpha"}]
    assert set(page.results[0].keys()) == {"id", "value", "label"}


def test_search_autocomplete_options_paginates_deterministically_by_label_then_pk() -> (
    None
):
    rows = [
        (4, "Beta"),
        (2, "Alpha"),
        (1, "Alpha"),
        (8, "Gamma"),
        (3, "Beta"),
    ]
    queryset = RecordingAutocompleteQuerySet(rows)

    page1_request = parse_autocomplete_request(
        _spec(), {"query": "a", "page": "1", "limit": "2"}
    )
    page2_request = parse_autocomplete_request(
        _spec(), {"query": "a", "page": "2", "limit": "2"}
    )

    # Use valid query length while still matching all rows.
    page1_request = parse_autocomplete_request(
        _spec(), {"query": "Al", "page": "1", "limit": "2"}
    )
    page2_request = parse_autocomplete_request(
        _spec(), {"query": "Al", "page": "2", "limit": "2"}
    )

    page1 = search_autocomplete_options(queryset, page1_request)
    page2 = search_autocomplete_options(queryset, page2_request)

    assert page1.results == [
        {"id": "1", "value": "1", "label": "Alpha"},
        {"id": "2", "value": "2", "label": "Alpha"},
    ]
    assert page1.has_next is False
    assert page2.results == []
    assert page2.has_next is False


def test_search_autocomplete_options_pagination_has_next_and_offset_slice() -> None:
    rows = [(1, "Alpha"), (2, "Alpine"), (3, "Alto")]
    queryset = RecordingAutocompleteQuerySet(rows)

    request = parse_autocomplete_request(
        _spec(), {"query": "Al", "page": "1", "limit": "2"}
    )
    page = search_autocomplete_options(queryset, request)

    assert page.page == 1
    assert page.limit == 2
    assert page.has_next is True

    # Ensure server-side flow used filter/order/values/slice.
    call_names = [name for name, _ in queryset.calls]
    assert call_names == ["filter", "order_by", "values_list", "slice"]

from __future__ import annotations

import json
from pathlib import Path

import django
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.test import RequestFactory

from django_smart_filters.admin import SmartFilterAdminMixin
from django_smart_filters.builder import Filter


if not settings.configured:
    settings.configure(
        SECRET_KEY="test-key",
        DEFAULT_CHARSET="utf-8",
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        MIDDLEWARE=[],
        ROOT_URLCONF=__name__,
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "DIRS": [
                    str(Path(__file__).resolve().parents[1] / "django_smart_filters" / "templates")
                ],
            }
        ],
    )


django.setup()


class AutocompleteAdminTestModel(models.Model):
    status = models.CharField(max_length=50)
    category = models.CharField(max_length=50)

    class Meta:
        app_label = "tests"


class InMemoryQuerySet:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows

    def filter(self, **kwargs: object) -> "InMemoryQuerySet":
        rows = self._rows
        for key, value in kwargs.items():
            if key.endswith("__icontains"):
                field = key[: -len("__icontains")]
                needle = str(value).lower()
                rows = [row for row in rows if needle in str(row[field]).lower()]
            elif key.endswith("__in"):
                field = key[: -len("__in")]
                allowed = {str(item) for item in value}  # type: ignore[arg-type]
                rows = [row for row in rows if str(row[field]) in allowed]
            else:
                rows = [row for row in rows if row[key] == value]
        return InMemoryQuerySet(rows)

    def order_by(self, *fields: str) -> "InMemoryQuerySet":
        ordered = list(self._rows)
        for field in reversed(fields):
            descending = field.startswith("-")
            key = field[1:] if descending else field
            ordered.sort(key=lambda row: row[key], reverse=descending)
        return InMemoryQuerySet(ordered)

    def values_list(self, *fields: str):
        return [tuple(row[field] for field in fields) for row in self._rows]


class _BaseSmartAdmin(admin.ModelAdmin):
    dataset = [
        {"pk": 1, "status": "open", "category": "Alpha"},
        {"pk": 2, "status": "open", "category": "Alpine"},
        {"pk": 3, "status": "closed", "category": "Alpha"},
        {"pk": 4, "status": "open", "category": "Beta"},
    ]

    def get_smart_filter_base_queryset(self, request):
        return InMemoryQuerySet(self.dataset)


class EndpointAdmin(SmartFilterAdminMixin, _BaseSmartAdmin):
    smart_filters = [
        Filter.field("status").dropdown(),
        Filter.field("category").autocomplete(),
    ]


def _make_admin() -> EndpointAdmin:
    return EndpointAdmin(AutocompleteAdminTestModel, AdminSite())


def _payload(response):
    return json.loads(response.content.decode("utf-8"))


def test_autocomplete_endpoint_returns_paginated_results() -> None:
    admin_instance = _make_admin()
    request = RequestFactory().get(
        "/admin/tests/autocompleteadmintestmodel/smart-filters/autocomplete/",
        data={"field": "category", "query": "Al", "page": "1", "limit": "1"},
    )

    response = admin_instance.smart_filter_autocomplete_view(request)
    payload = _payload(response)

    assert response.status_code == 200
    assert set(payload.keys()) == {"results", "pagination"}
    assert payload["pagination"] == {"page": 1, "limit": 1, "has_next": True}


def test_autocomplete_endpoint_result_payload_is_minimal_shape() -> None:
    admin_instance = _make_admin()
    request = RequestFactory().get(
        "/admin/tests/autocompleteadmintestmodel/smart-filters/autocomplete/",
        data={"field": "category", "query": "Al", "page": "1", "limit": "5"},
    )

    response = admin_instance.smart_filter_autocomplete_view(request)
    payload = _payload(response)

    assert payload["results"]
    assert all(set(item.keys()) == {"id", "value", "label"} for item in payload["results"])


def test_autocomplete_endpoint_applies_server_side_text_filter() -> None:
    admin_instance = _make_admin()
    request = RequestFactory().get(
        "/admin/tests/autocompleteadmintestmodel/smart-filters/autocomplete/",
        data={"field": "category", "query": "Be", "page": "1", "limit": "5"},
    )

    response = admin_instance.smart_filter_autocomplete_view(request)
    payload = _payload(response)

    assert [item["label"] for item in payload["results"]] == ["Beta"]


def test_autocomplete_endpoint_honors_existing_filter_state_composition() -> None:
    admin_instance = _make_admin()
    request = RequestFactory().get(
        "/admin/tests/autocompleteadmintestmodel/smart-filters/autocomplete/",
        data={
            "field": "category",
            "query": "Al",
            "status": "open",
            "page": "1",
            "limit": "5",
        },
    )

    response = admin_instance.smart_filter_autocomplete_view(request)
    payload = _payload(response)

    # closed + Alpha (pk=3) is excluded by active status=open context
    assert [item["id"] for item in payload["results"]] == ["1", "2"]


def test_autocomplete_endpoint_rejects_unknown_or_non_autocomplete_fields() -> None:
    admin_instance = _make_admin()

    unknown = RequestFactory().get(
        "/admin/tests/autocompleteadmintestmodel/smart-filters/autocomplete/",
        data={"field": "missing", "query": "Al"},
    )
    unknown_response = admin_instance.smart_filter_autocomplete_view(unknown)
    assert unknown_response.status_code == 400
    assert "invalid" in _payload(unknown_response)["error"].lower()

    non_autocomplete = RequestFactory().get(
        "/admin/tests/autocompleteadmintestmodel/smart-filters/autocomplete/",
        data={"field": "status", "query": "op"},
    )
    non_autocomplete_response = admin_instance.smart_filter_autocomplete_view(non_autocomplete)
    assert non_autocomplete_response.status_code == 400
    assert "invalid" in _payload(non_autocomplete_response)["error"].lower()


def test_autocomplete_endpoint_rejects_invalid_paging_params() -> None:
    admin_instance = _make_admin()
    request = RequestFactory().get(
        "/admin/tests/autocompleteadmintestmodel/smart-filters/autocomplete/",
        data={"field": "category", "query": "Al", "page": "0"},
    )

    response = admin_instance.smart_filter_autocomplete_view(request)

    assert response.status_code == 400
    assert "invalid" in _payload(response)["error"].lower()


def test_get_urls_registers_smart_filter_autocomplete_route() -> None:
    admin_instance = _make_admin()

    urls = admin_instance.get_urls()
    names = {pattern.name for pattern in urls}

    assert "tests_autocompleteadmintestmodel_smart_filters_autocomplete" in names

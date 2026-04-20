from __future__ import annotations

from pathlib import Path

import django
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.template.loader import render_to_string
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


class UiAdminTestModel(models.Model):
    status = models.CharField(max_length=50)
    category = models.CharField(max_length=50)

    class Meta:
        app_label = "tests"


class _BaseSmartAdmin(admin.ModelAdmin):
    def get_smart_filter_base_queryset(self, request):
        class _EmptyQuerySet:
            def filter(self, **kwargs):
                return self

            def order_by(self, *args):
                return self

            def values_list(self, *args):
                return []

        return _EmptyQuerySet()

    def changelist_view(self, request, extra_context=None):
        return extra_context or {}


class UiAdmin(SmartFilterAdminMixin, _BaseSmartAdmin):
    smart_filters = [
        Filter.field("status").dropdown(),
        Filter.field("category").autocomplete(),
    ]


def _make_admin() -> UiAdmin:
    return UiAdmin(UiAdminTestModel, AdminSite())


def test_autocomplete_control_is_lazy_loaded() -> None:
    admin_instance = _make_admin()
    request = RequestFactory().get("/admin/tests/uiadmintestmodel/")

    context = admin_instance.changelist_view(request)
    control = next(item for item in context["filter_controls"] if item["kind"] == "autocomplete")

    assert control["endpoint_url"].endswith("/smart-filters/autocomplete/")
    assert control["page_size"] == 20
    assert control["min_query_length"] == 2
    assert control["options"] == []


def test_autocomplete_control_template_contains_metadata_without_preloaded_options() -> None:
    html = render_to_string(
        "admin/django_smart_filters/autocomplete_control.html",
        {
            "control": {
                "field_name": "category",
                "param_name": "category",
                "endpoint_url": "/admin/tests/uiadmintestmodel/smart-filters/autocomplete/",
                "min_query_length": 2,
                "page_size": 20,
                "value": "",
                "selected_label": "",
            }
        },
    )

    assert "data-autocomplete-url=\"/admin/tests/uiadmintestmodel/smart-filters/autocomplete/\"" in html
    assert "data-page-size=\"20\"" in html
    assert "<option" not in html


def test_autocomplete_control_js_defines_debounce_and_stale_guard() -> None:
    js = (Path(__file__).resolve().parents[1] / "django_smart_filters" / "static" / "django_smart_filters" / "autocomplete.js").read_text()

    assert "const DEBOUNCE_MS = 250" in js
    assert "function createDebouncer" in js
    assert "function createStaleGuard" in js
    assert "staleGuard.isCurrent" in js


def test_stale_response_is_ignored() -> None:
    js = (Path(__file__).resolve().parents[1] / "django_smart_filters" / "static" / "django_smart_filters" / "autocomplete.js").read_text()

    assert "if (!staleGuard.isCurrent(token))" in js
    assert "return { stale: true }" in js


def test_autocomplete_js_fetches_paginated_results_and_supports_load_more() -> None:
    js = (Path(__file__).resolve().parents[1] / "django_smart_filters" / "static" / "django_smart_filters" / "autocomplete.js").read_text()

    assert "params.set(\"page\", String(page))" in js
    assert "params.set(\"limit\", String(pageSize))" in js
    assert "requestPage(currentQuery, currentPage + 1, true)" in js

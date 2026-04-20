from __future__ import annotations

from pathlib import Path

import django
import pytest
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.test import RequestFactory

from django_smart_filters.builder import Filter
from django_smart_filters.declarations import DropdownFilter


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


class AdminFilterTestModel(models.Model):
    status = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    created = models.DateField(null=True)
    score = models.FloatField(null=True)
    active = models.BooleanField(default=False)

    class Meta:
        app_label = "tests"


class RecordingQuerySet:
    def __init__(self, calls: list[dict[str, object]] | None = None) -> None:
        self.calls = calls or []

    def filter(self, **kwargs: object) -> "RecordingQuerySet":
        return RecordingQuerySet(self.calls + [kwargs])


class _BaseSmartAdmin(admin.ModelAdmin):
    def get_smart_filter_base_queryset(self, request):
        return RecordingQuerySet()


def _admin_class(declarations):
    from django_smart_filters.admin import SmartFilterAdminMixin

    class TestAdmin(SmartFilterAdminMixin, _BaseSmartAdmin):
        smart_filters = declarations

    return TestAdmin


def _make_admin(declarations):
    admin_class = _admin_class(declarations)
    return admin_class(AdminFilterTestModel, AdminSite())


def _all_filter_declarations():
    return [
        DropdownFilter("status"),
        Filter.field("category").multi_select(),
        Filter.field("created").date_range(),
        Filter.field("score").numeric_range(),
        Filter.field("active").boolean_toggle(),
    ]


@pytest.mark.parametrize(
    ("data", "expected_calls"),
    [
        ({"status": "open"}, [{"status": "open"}]),
        ({"category__in": ["a", "b"]}, [{"category__in": ["a", "b"]}]),
        (
            {"created_start": "2026-01-01", "created_end": "2026-01-31"},
            [{"created__gte": "2026-01-01"}, {"created__lte": "2026-01-31"}],
        ),
        ({"score_min": "10", "score_max": "20"}, [{"score__gte": 10.0}, {"score__lte": 20.0}]),
        ({"active": "true"}, [{"active": True}]),
    ],
)
def test_each_built_in_kind_filters_queryset_from_get_params(data, expected_calls) -> None:
    admin_instance = _make_admin(_all_filter_declarations())
    request = RequestFactory().get("/admin/tests/adminfiltertestmodel/", data=data)

    queryset = admin_instance.get_queryset(request)

    assert queryset.calls == expected_calls


def test_class_style_and_fluent_declarations_share_normalization_path() -> None:
    class_style_admin = _make_admin([
        DropdownFilter("status"),
        DropdownFilter("category", alias="cat"),
    ])
    fluent_admin = _make_admin([
        Filter.field("status").dropdown(),
        Filter.field("category").as_alias("cat").dropdown(),
    ])

    class_specs = class_style_admin.get_smart_filter_specs()
    fluent_specs = fluent_admin.get_smart_filter_specs()

    assert class_specs == fluent_specs


def test_default_admin_usage_requires_no_changelist_replacement() -> None:
    admin_instance = _make_admin(_all_filter_declarations())

    assert admin_instance.change_list_template is None

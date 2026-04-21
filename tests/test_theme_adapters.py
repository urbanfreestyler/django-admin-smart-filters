from __future__ import annotations

import django
from pathlib import Path
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.test import RequestFactory

from django_admin_smart_filters.builder import Filter
from django_admin_smart_filters.theme import ThemeAdapter, resolve_theme_adapter

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
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
        MIDDLEWARE=[],
        ROOT_URLCONF=__name__,
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "DIRS": [
                    str(
                        Path(__file__).resolve().parents[1]
                        / "django_admin_smart_filters"
                        / "templates"
                    )
                ],
            }
        ],
    )

django.setup()


class ThemeAdminFilterModel(models.Model):
    status = models.CharField(max_length=50)

    class Meta:
        app_label = "tests"


class _BaseSmartAdmin(admin.ModelAdmin):
    def get_smart_filter_base_queryset(self, request):
        class _RecordingQuerySet:
            def filter(self, **kwargs):
                return self

        return _RecordingQuerySet()

    def changelist_view(self, request, extra_context=None):
        return extra_context or {}


class CustomThemeAdapter(ThemeAdapter):
    pass


def _make_admin(*, adapter: ThemeAdapter | None = None):
    from django_admin_smart_filters.admin import SmartFilterAdminMixin

    class TestAdmin(SmartFilterAdminMixin, _BaseSmartAdmin):
        smart_filters = [Filter.field("status").dropdown()]
        smart_filter_theme_adapter = adapter

    return TestAdmin(ThemeAdminFilterModel, AdminSite())


def test_default_adapter_resolves_when_none_configured() -> None:
    resolved = resolve_theme_adapter(None)

    assert resolved.name == "default"
    assert resolved.controls_template.endswith("theme/default/filter_controls.html")
    assert resolved.active_bar_template.endswith(
        "theme/default/active_filters_bar.html"
    )


def test_custom_adapter_can_define_alternate_template_paths() -> None:
    adapter = CustomThemeAdapter(
        name="acme",
        controls_template="admin/django_admin_smart_filters/filter_controls.html",
        active_bar_template="admin/django_admin_smart_filters/active_filters_bar.html",
    )

    resolved = resolve_theme_adapter(adapter)

    assert resolved is adapter
    assert resolved.name == "acme"


def test_changelist_context_uses_adapter_selected_templates() -> None:
    adapter = CustomThemeAdapter(
        name="acme",
        controls_template="admin/django_admin_smart_filters/filter_controls.html",
        active_bar_template="admin/django_admin_smart_filters/active_filters_bar.html",
    )
    admin_instance = _make_admin(adapter=adapter)
    request = RequestFactory().get("/admin/tests/themeadminfiltermodel/")

    context = admin_instance.changelist_view(request)

    assert context["smart_filter_theme_adapter"] == "acme"
    assert context["smart_filter_controls_template"] == adapter.controls_template
    assert context["smart_filter_active_bar_template"] == adapter.active_bar_template

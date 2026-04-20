"""Default Django admin integration for declared smart filters."""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.urls import path

from django_smart_filters.autocomplete import (
    DEFAULT_AUTOCOMPLETE_PAGE_SIZE,
    MIN_AUTOCOMPLETE_QUERY_LENGTH,
    parse_autocomplete_request,
    search_autocomplete_options,
)
from django_smart_filters.chips import (
    build_active_filter_chips,
    build_remove_one_url,
    build_reset_all_url,
)
from django_smart_filters.declarations import normalize_declarations
from django_smart_filters.query import apply_filter_state
from django_smart_filters.state import parse_filter_state
from django_smart_filters.theme import ThemeAdapter, resolve_theme_adapter


class SmartFilterAdminMixin:
    """Additive changelist integration for declarative smart filters."""

    smart_filters: list[object] = []
    smart_filter_controls_template = "admin/django_smart_filters/filter_controls.html"
    smart_filter_active_bar_template = "admin/django_smart_filters/active_filters_bar.html"
    smart_filter_theme_adapter: ThemeAdapter | None = None

    def get_smart_filter_declarations(self) -> list[object]:
        return list(getattr(self, "smart_filters", []) or [])

    def get_smart_filter_specs(self):
        return normalize_declarations(self.get_smart_filter_declarations())

    def get_smart_filter_state(self, request: HttpRequest) -> dict[str, Any]:
        specs = self.get_smart_filter_specs()
        return parse_filter_state(specs, request.GET)

    def get_smart_filter_base_queryset(self, request: HttpRequest):
        base_method = getattr(super(), "get_smart_filter_base_queryset", None)
        if callable(base_method):
            return base_method(request)
        return super().get_queryset(request)

    def get_queryset(self, request: HttpRequest):
        queryset = self.get_smart_filter_base_queryset(request)
        specs = self.get_smart_filter_specs()
        state = parse_filter_state(specs, request.GET)
        return apply_filter_state(queryset, specs, state)

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name

        smart_urls = [
            path(
                "smart-filters/autocomplete/",
                self.admin_site.admin_view(self.smart_filter_autocomplete_view),
                name="%s_%s_smart_filters_autocomplete" % info,
            )
        ]
        return smart_urls + urls

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, Any] | None = None):
        theme_adapter = self.get_smart_filter_theme_adapter()
        specs = self.get_smart_filter_specs()
        state = parse_filter_state(specs, request.GET)
        controls = self._build_filter_controls(specs, state, request)
        labels = {spec.field_name: spec.field_name.replace("_", " ").title() for spec in specs}
        chips = build_active_filter_chips(specs, state, labels)
        for chip in chips:
            chip["remove_url"] = build_remove_one_url(request.GET, chip)
        managed_params = [spec.param_name for spec in specs]
        reset_all_url = build_reset_all_url(request.GET, managed_params)

        context = dict(extra_context or {})
        context["smart_filter_controls_template"] = theme_adapter.controls_template
        context["smart_filter_active_bar_template"] = theme_adapter.active_bar_template
        context["smart_filter_theme_adapter"] = theme_adapter.name
        context["filter_controls"] = controls
        context["smart_filter_state"] = state
        context["active_filter_chips"] = chips
        context["reset_all_url"] = reset_all_url
        context["smart_filter_controls_html"] = self.render_smart_filter_controls(controls, theme_adapter=theme_adapter)
        context["smart_filter_active_bar_html"] = self.render_smart_filter_active_bar(
            chips,
            reset_all_url,
            theme_adapter=theme_adapter,
        )

        return super().changelist_view(request, extra_context=context)

    def smart_filter_autocomplete_view(self, request: HttpRequest) -> JsonResponse:
        specs = self.get_smart_filter_specs()
        field_selector = str(request.GET.get("field", "")).strip()

        target_spec = self._resolve_autocomplete_spec(specs, field_selector)
        if target_spec is None:
            return JsonResponse({"error": f"invalid autocomplete field: {field_selector or '(missing)'}"}, status=400)

        state = parse_filter_state(specs, request.GET)
        scoped_state = {k: v for k, v in state.items() if k != target_spec.param_name}

        try:
            autocomplete_request = parse_autocomplete_request(target_spec, request.GET, state=scoped_state)
        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=400)

        queryset = self.get_smart_filter_base_queryset(request)
        if scoped_state:
            queryset = apply_filter_state(queryset, specs, scoped_state)

        page = search_autocomplete_options(queryset, autocomplete_request)

        return JsonResponse(
            {
                "results": page.results,
                "pagination": {
                    "page": page.page,
                    "limit": page.limit,
                    "has_next": page.has_next,
                },
            }
        )

    def get_smart_filter_theme_adapter(self) -> ThemeAdapter:
        configured = getattr(self, "smart_filter_theme_adapter", None)
        return resolve_theme_adapter(configured)

    def render_smart_filter_controls(
        self,
        controls: list[dict[str, Any]],
        *,
        theme_adapter: ThemeAdapter | None = None,
    ) -> str:
        adapter = resolve_theme_adapter(theme_adapter or self.get_smart_filter_theme_adapter())
        return render_to_string(adapter.controls_template, {"filter_controls": controls})

    def render_smart_filter_active_bar(
        self,
        chips: list[dict[str, Any]],
        reset_all_url: str,
        *,
        theme_adapter: ThemeAdapter | None = None,
    ) -> str:
        adapter = resolve_theme_adapter(theme_adapter or self.get_smart_filter_theme_adapter())
        return render_to_string(
            adapter.active_bar_template,
            {
                "active_filter_chips": chips,
                "reset_all_url": reset_all_url,
            },
        )

    def _build_filter_controls(
        self,
        specs,
        state: dict[str, Any],
        request: HttpRequest | None = None,
    ) -> list[dict[str, Any]]:
        controls: list[dict[str, Any]] = []
        autocomplete_url = self._autocomplete_endpoint_url(request)

        for spec in specs:
            value = state.get(spec.param_name)
            control = {
                "field_name": spec.field_name,
                "label": spec.field_name.replace("_", " ").title(),
                "kind": spec.filter_kind,
                "param_name": spec.param_name,
                "value": value,
                "options": self._control_options(spec.filter_kind, value),
            }

            if spec.filter_kind == "autocomplete":
                control.update(
                    {
                        "endpoint_url": autocomplete_url,
                        "min_query_length": MIN_AUTOCOMPLETE_QUERY_LENGTH,
                        "page_size": DEFAULT_AUTOCOMPLETE_PAGE_SIZE,
                        "selected_label": str(value) if value is not None else "",
                    }
                )

            controls.append(control)

        return controls

    def _control_options(self, filter_kind: str, value: Any) -> list[dict[str, str]]:
        if filter_kind == "boolean_toggle":
            return [
                {"value": "true", "label": "Yes"},
                {"value": "false", "label": "No"},
            ]

        if filter_kind == "multi_select":
            if not isinstance(value, list):
                return []
            return [{"value": str(item), "label": str(item)} for item in value]

        if filter_kind == "dropdown":
            if value is None:
                return []
            text = str(value)
            return [{"value": text, "label": text}]

        return []

    def _resolve_autocomplete_spec(self, specs, field_selector: str):
        if not field_selector:
            return None

        for spec in specs:
            if spec.filter_kind != "autocomplete":
                continue
            if field_selector in {spec.field_name, spec.param_name}:
                return spec

        return None

    def _autocomplete_endpoint_url(self, request: HttpRequest | None) -> str:
        if request is None:
            return "smart-filters/autocomplete/"

        base = request.path.rstrip("/")
        return f"{base}/smart-filters/autocomplete/"


__all__ = ["SmartFilterAdminMixin"]

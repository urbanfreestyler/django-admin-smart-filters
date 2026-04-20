"""Default Django admin integration for declared smart filters."""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from django.template.loader import render_to_string

from django_smart_filters.chips import (
    build_active_filter_chips,
    build_remove_one_url,
    build_reset_all_url,
)
from django_smart_filters.declarations import normalize_declarations
from django_smart_filters.query import apply_filter_state
from django_smart_filters.state import parse_filter_state


class SmartFilterAdminMixin:
    """Additive changelist integration for declarative smart filters."""

    smart_filters: list[object] = []
    smart_filter_controls_template = "admin/django_smart_filters/filter_controls.html"
    smart_filter_active_bar_template = "admin/django_smart_filters/active_filters_bar.html"

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

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, Any] | None = None):
        specs = self.get_smart_filter_specs()
        state = parse_filter_state(specs, request.GET)
        controls = self._build_filter_controls(specs, state)
        labels = {spec.field_name: spec.field_name.replace("_", " ").title() for spec in specs}
        chips = build_active_filter_chips(specs, state, labels)
        for chip in chips:
            chip["remove_url"] = build_remove_one_url(request.GET, chip)
        managed_params = [spec.param_name for spec in specs]
        reset_all_url = build_reset_all_url(request.GET, managed_params)

        context = dict(extra_context or {})
        context["smart_filter_controls_template"] = self.smart_filter_controls_template
        context["smart_filter_active_bar_template"] = self.smart_filter_active_bar_template
        context["filter_controls"] = controls
        context["smart_filter_state"] = state
        context["active_filter_chips"] = chips
        context["reset_all_url"] = reset_all_url
        context["smart_filter_controls_html"] = self.render_smart_filter_controls(controls)
        context["smart_filter_active_bar_html"] = self.render_smart_filter_active_bar(chips, reset_all_url)

        return super().changelist_view(request, extra_context=context)

    def render_smart_filter_controls(self, controls: list[dict[str, Any]]) -> str:
        return render_to_string(self.smart_filter_controls_template, {"filter_controls": controls})

    def render_smart_filter_active_bar(self, chips: list[dict[str, Any]], reset_all_url: str) -> str:
        return render_to_string(
            self.smart_filter_active_bar_template,
            {
                "active_filter_chips": chips,
                "reset_all_url": reset_all_url,
            },
        )

    def _build_filter_controls(self, specs, state: dict[str, Any]) -> list[dict[str, Any]]:
        controls: list[dict[str, Any]] = []
        for spec in specs:
            value = state.get(spec.param_name)
            controls.append(
                {
                    "field_name": spec.field_name,
                    "label": spec.field_name.replace("_", " ").title(),
                    "kind": spec.filter_kind,
                    "param_name": spec.param_name,
                    "value": value,
                    "options": self._control_options(spec.filter_kind, value),
                }
            )
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


__all__ = ["SmartFilterAdminMixin"]

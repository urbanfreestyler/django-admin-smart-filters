from __future__ import annotations

import pytest

from django_smart_filters.builder import Filter
from django_smart_filters.contracts import FilterComponent, FilterSpec
from django_smart_filters.declarations import ClassFilterDeclaration, normalize_class_declaration
from django_smart_filters.registry import (
    clear_filter_component_registry,
    register_filter_component,
    resolve_filter_component,
)


class DemoComponent(FilterComponent):
    key = "demo"
    filter_kind = "dropdown"


def test_register_component_and_resolve_returns_same_class() -> None:
    clear_filter_component_registry()

    register_filter_component("demo", DemoComponent)

    resolved = resolve_filter_component("demo")
    assert resolved is DemoComponent


def test_duplicate_component_registration_fails_fast() -> None:
    clear_filter_component_registry()
    register_filter_component("demo", DemoComponent)

    with pytest.raises(ValueError, match="already registered"):
        register_filter_component("demo", DemoComponent)


def test_unknown_component_key_in_normalization_raises_actionable_error() -> None:
    clear_filter_component_registry()

    declaration = ClassFilterDeclaration(
        field_name="status",
        filter_kind="dropdown",
        component_key="missing",
    )

    with pytest.raises(ValueError, match="Unknown filter component 'missing'"):
        normalize_class_declaration(declaration)


def test_fluent_builder_hooks_preserved_in_normalized_spec() -> None:
    def query_hook(queryset: object, value: object, spec: FilterSpec) -> object:
        return queryset

    def widget_hook(widget_context: dict[str, object], spec: FilterSpec) -> dict[str, object]:
        return widget_context

    spec = (
        Filter.field("status")
        .dropdown()
        .with_query_hook(query_hook)
        .with_widget_hook(widget_hook)
        .to_spec()
    )

    assert spec.query_hook is query_hook
    assert spec.widget_hook is widget_hook

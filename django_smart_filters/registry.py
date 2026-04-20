"""Registry for custom filter component contracts."""

from __future__ import annotations

from django_smart_filters.contracts import FilterComponent

_COMPONENT_REGISTRY: dict[str, type[FilterComponent]] = {}


def register_filter_component(key: str, component: type[FilterComponent]) -> None:
    """Register a custom component class under a unique key."""

    normalized_key = str(key).strip()
    if not normalized_key:
        raise ValueError("Invalid component key: expected a non-empty string.")

    if normalized_key in _COMPONENT_REGISTRY:
        raise ValueError(f"Filter component '{normalized_key}' is already registered.")

    _COMPONENT_REGISTRY[normalized_key] = component


def resolve_filter_component(key: str) -> type[FilterComponent]:
    """Resolve a component class by key, failing fast when unknown."""

    normalized_key = str(key).strip()
    component = _COMPONENT_REGISTRY.get(normalized_key)
    if component is None:
        raise ValueError(
            "Unknown filter component "
            f"'{normalized_key}'. Register it with register_filter_component(...)."
        )
    return component


def clear_filter_component_registry() -> None:
    """Clear all registered components (test helper)."""

    _COMPONENT_REGISTRY.clear()


__all__ = [
    "register_filter_component",
    "resolve_filter_component",
    "clear_filter_component_registry",
]

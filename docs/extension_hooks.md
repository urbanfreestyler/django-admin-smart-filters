# Extension Hooks

Use extension hooks to register custom filter components and attach query/widget behavior without patching core internals.

## Public Imports

```python
# docs:extension-public-imports
from django_smart_filters import (
    FilterComponent,
    register_filter_component,
    resolve_filter_component,
)
from django_smart_filters.builder import Filter
from django_smart_filters.declarations import ClassFilterDeclaration
```

## Register a Custom Component

```python
# docs:component-registration
from django_smart_filters import (
    FilterComponent,
    register_filter_component,
    resolve_filter_component,
)


class StatusBadgeComponent(FilterComponent):
    key = "status_badge"
    filter_kind = "dropdown"


register_filter_component("status_badge", StatusBadgeComponent)
resolved_component = resolve_filter_component("status_badge")
```

## Attach Query and Widget Hooks

Class-style declaration:

```python
from django_smart_filters.declarations import ClassFilterDeclaration


def only_open(queryset, value, spec):
    if value == "open":
        return queryset.filter(is_archived=False)
    return queryset


def add_widget_hint(widget_context, spec):
    enriched = dict(widget_context)
    enriched["placeholder"] = f"Filter by {spec.field_name}"
    return enriched


status_filter = ClassFilterDeclaration(
    field_name="status",
    filter_kind="dropdown",
    component_key="status_badge",
    query_hook=only_open,
    widget_hook=add_widget_hint,
)
```

Fluent declaration:

```python
from django_smart_filters.builder import Filter


status_filter = (
    Filter.field("status")
    .dropdown()
    .with_component("status_badge")
    .with_query_hook(only_open)
    .with_widget_hook(add_widget_hint)
)
```

## Failure Semantics

- Unknown `component_key` values fail fast during declaration normalization.
- Duplicate registrations for the same key raise `ValueError`.
- Hooks are optional and preserve default behavior when omitted.

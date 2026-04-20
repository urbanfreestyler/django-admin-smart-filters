# Examples

## End-to-End v1 Example

```python
from django.contrib import admin

from django_smart_filters import FilterComponent, register_filter_component
from django_smart_filters.admin import SmartFilterAdminMixin
from django_smart_filters.builder import Filter
from django_smart_filters.theme import ThemeAdapter


class StatusBadgeComponent(FilterComponent):
    key = "status_badge"
    filter_kind = "dropdown"


register_filter_component("status_badge", StatusBadgeComponent)


def active_only(queryset, value, spec):
    if value == "active":
        return queryset.filter(is_archived=False)
    return queryset


def widget_hint(context, spec):
    data = dict(context)
    data["placeholder"] = "Search status"
    return data


class OrderAdmin(SmartFilterAdminMixin, admin.ModelAdmin):
    smart_filter_theme_adapter = ThemeAdapter(
        name="acme",
        controls_template="admin/django_smart_filters/filter_controls.html",
        active_bar_template="admin/django_smart_filters/active_filters_bar.html",
    )

    smart_filters = [
        Filter.field("status")
        .dropdown()
        .with_component("status_badge")
        .with_query_hook(active_only)
        .with_widget_hook(widget_hint),
        Filter.field("assignee").autocomplete(),
        Filter.field("created").date_range(),
    ]
```

This combines built-in filters, a custom component key, extension hooks, and an adapter override while keeping core query/state behavior unchanged.

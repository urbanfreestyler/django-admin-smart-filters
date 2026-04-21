# Theme Adapters

Theme adapters decouple rendering templates from query/state logic so you can support non-default admin themes safely.

## Adapter Contract

`ThemeAdapter` defines:

- `name`: adapter identifier used in context.
- `controls_template`: template used by `render_smart_filter_controls()`.
- `active_bar_template`: template used by `render_smart_filter_active_bar()`.
- `class_map`: optional class mapping for theme-specific class names.

## Configure an Adapter

```python
# docs:theme-adapter-config
from django.contrib import admin

from django_admin_smart_filters.admin import SmartFilterAdminMixin
from django_admin_smart_filters.theme import ThemeAdapter


adapter = ThemeAdapter(
    name="acme",
    controls_template="admin/django_admin_smart_filters/filter_controls.html",
    active_bar_template="admin/django_admin_smart_filters/active_filters_bar.html",
)


class ProductAdmin(SmartFilterAdminMixin, admin.ModelAdmin):
    smart_filter_theme_adapter = adapter
```

## Template Path Structure

Default adapter template paths:

- `admin/django_admin_smart_filters/theme/default/filter_controls.html`
- `admin/django_admin_smart_filters/theme/default/active_filters_bar.html`

Filesystem location for package defaults:

- `templates/admin/django_admin_smart_filters/theme/default/filter_controls.html`
- `templates/admin/django_admin_smart_filters/theme/default/active_filters_bar.html`

Backward-compatible wrapper templates remain at:

- `admin/django_admin_smart_filters/filter_controls.html`
- `admin/django_admin_smart_filters/active_filters_bar.html`

If no adapter is configured, `resolve_theme_adapter(None)` uses the default adapter.

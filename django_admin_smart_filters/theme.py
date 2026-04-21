"""Theme adapter contracts and resolver utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class ThemeAdapter:
    """Rendering contract for smart filter templates."""

    name: str
    controls_template: str
    active_bar_template: str
    class_map: Mapping[str, str] = field(default_factory=dict)


DEFAULT_THEME_ADAPTER = ThemeAdapter(
    name="default",
    controls_template="admin/django_admin_smart_filters/theme/default/filter_controls.html",
    active_bar_template="admin/django_admin_smart_filters/theme/default/active_filters_bar.html",
)


def resolve_theme_adapter(adapter: ThemeAdapter | None) -> ThemeAdapter:
    """Resolve configured theme adapter, defaulting safely."""

    if adapter is None:
        return DEFAULT_THEME_ADAPTER
    return adapter


__all__ = ["ThemeAdapter", "DEFAULT_THEME_ADAPTER", "resolve_theme_adapter"]

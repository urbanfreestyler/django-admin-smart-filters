"""Core declaration contracts for Django Smart Filters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Mapping, Protocol


class QueryHook(Protocol):
    """Hook for custom queryset application behavior."""

    def __call__(self, queryset: Any, value: Any, spec: "FilterSpec") -> Any:
        ...


class WidgetHook(Protocol):
    """Hook for custom widget context behavior."""

    def __call__(self, widget_context: Mapping[str, Any], spec: "FilterSpec") -> Mapping[str, Any]:
        ...


class FilterComponent:
    """Base contract for custom filter component extensions."""

    key: ClassVar[str]
    filter_kind: ClassVar[str] = "dropdown"


@dataclass(frozen=True)
class FilterSpec:
    """Normalized internal filter declaration contract."""

    field_name: str
    alias: str | None
    filter_kind: str
    query_hook: QueryHook | None
    widget_hook: WidgetHook | None
    param_name: str
    component_key: str | None = None

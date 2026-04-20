"""Fluent declaration builder API."""

from __future__ import annotations

from dataclasses import dataclass

from django_smart_filters.contracts import FilterSpec, QueryHook, WidgetHook
from django_smart_filters.declarations import normalize_builder_declaration


@dataclass(frozen=True)
class BuilderFilterDeclaration:
    field_name: str
    filter_kind: str
    alias: str | None = None
    query_hook: QueryHook | None = None
    widget_hook: WidgetHook | None = None

    def to_spec(self) -> FilterSpec:
        return normalize_builder_declaration(self)


@dataclass(frozen=True)
class _FilterFieldBuilder:
    field_name: str
    alias: str | None = None

    def as_alias(self, alias: str) -> "_FilterFieldBuilder":
        return _FilterFieldBuilder(field_name=self.field_name, alias=alias)

    def _kind(self, filter_kind: str) -> BuilderFilterDeclaration:
        return BuilderFilterDeclaration(
            field_name=self.field_name,
            alias=self.alias,
            filter_kind=filter_kind,
        )

    def dropdown(self) -> BuilderFilterDeclaration:
        return self._kind("dropdown")

    def autocomplete(self) -> BuilderFilterDeclaration:
        return self._kind("autocomplete")

    def multi_select(self) -> BuilderFilterDeclaration:
        return self._kind("multi_select")

    def date_range(self) -> BuilderFilterDeclaration:
        return self._kind("date_range")

    def numeric_range(self) -> BuilderFilterDeclaration:
        return self._kind("numeric_range")

    def boolean_toggle(self) -> BuilderFilterDeclaration:
        return self._kind("boolean_toggle")


class Filter:
    """Entrypoint for fluent declaration style."""

    @staticmethod
    def field(field_name: str) -> _FilterFieldBuilder:
        return _FilterFieldBuilder(field_name=field_name)

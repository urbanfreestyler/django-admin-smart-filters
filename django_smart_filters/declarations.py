"""Class-style declarations and normalization path."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from django_smart_filters.contracts import FilterSpec, QueryHook, WidgetHook
from django_smart_filters.params import resolve_param_name
from django_smart_filters.validation import FilterValidationError, validate_filter_spec


@dataclass(frozen=True)
class ClassFilterDeclaration:
    field_name: str
    filter_kind: str
    alias: str | None = None
    query_hook: QueryHook | None = None
    widget_hook: WidgetHook | None = None


def DropdownFilter(field_name: str, *, alias: str | None = None) -> ClassFilterDeclaration:
    return ClassFilterDeclaration(field_name=field_name, filter_kind="dropdown", alias=alias)


def _is_multivalue(kind: str) -> bool:
    return kind in {"multi_select"}


def normalize_class_declaration(declaration: ClassFilterDeclaration) -> FilterSpec:
    spec = FilterSpec(
        field_name=declaration.field_name,
        alias=declaration.alias,
        filter_kind=declaration.filter_kind,
        query_hook=declaration.query_hook,
        widget_hook=declaration.widget_hook,
        param_name=resolve_param_name(
            declaration.field_name,
            alias=declaration.alias,
            multivalue=_is_multivalue(declaration.filter_kind),
        ),
    )
    validate_filter_spec(spec)
    return spec


def normalize_builder_declaration(declaration: "BuilderFilterDeclaration") -> FilterSpec:
    class_declaration = ClassFilterDeclaration(
        field_name=declaration.field_name,
        filter_kind=declaration.filter_kind,
        alias=declaration.alias,
        query_hook=declaration.query_hook,
        widget_hook=declaration.widget_hook,
    )
    return normalize_class_declaration(class_declaration)


def normalize_declarations(declarations: Iterable[object]) -> list[FilterSpec]:
    specs: list[FilterSpec] = []

    for declaration in declarations:
        if hasattr(declaration, "to_spec"):
            spec = declaration.to_spec()
        else:
            spec = normalize_class_declaration(declaration)
        specs.append(spec)
    _validate_param_collisions(specs)
    return specs


def _validate_param_collisions(specs: Sequence[FilterSpec]) -> None:
    seen: dict[str, str] = {}
    for spec in specs:
        if spec.param_name in seen:
            previous = seen[spec.param_name]
            raise FilterValidationError(
                "Parameter name collision for "
                f"'{spec.param_name}' between fields '{previous}' and '{spec.field_name}'. "
                "Set a unique alias on one declaration to resolve the conflict."
            )
        seen[spec.param_name] = spec.field_name

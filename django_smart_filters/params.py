"""Parameter naming helpers for deterministic filter query keys."""

from __future__ import annotations


def resolve_param_name(field_name: str, *, alias: str | None = None, multivalue: bool = False) -> str:
    """Resolve deterministic query parameter name.

    Alias takes precedence over derived names.
    """

    if alias:
        return alias

    return f"{field_name}__in" if multivalue else field_name

"""Validation utilities for normalized filter specs."""

from __future__ import annotations

from django_smart_filters.contracts import FilterSpec

SUPPORTED_FILTER_KINDS = {
    "dropdown",
    "autocomplete",
    "multi_select",
    "date_range",
    "numeric_range",
    "boolean_toggle",
}


class FilterValidationError(ValueError):
    """Raised when a declaration cannot be normalized safely."""


def validate_filter_spec(spec: FilterSpec) -> None:
    """Validate one normalized filter spec."""

    if spec.field_name is None or not str(spec.field_name).strip():
        raise FilterValidationError(
            "Invalid field_name value: empty. Provide a non-empty field name like 'status'."
        )

    if spec.filter_kind not in SUPPORTED_FILTER_KINDS:
        supported = ", ".join(sorted(SUPPORTED_FILTER_KINDS))
        raise FilterValidationError(
            f"Unsupported filter_kind '{spec.filter_kind}'. Supported kinds: {supported}."
        )

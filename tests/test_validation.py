import pytest

from django_smart_filters.declarations import (
    ClassFilterDeclaration,
    DropdownFilter,
    normalize_class_declaration,
    normalize_declarations,
)
from django_smart_filters.validation import FilterValidationError


def test_invalid_field_name_raises_at_normalization_time() -> None:
    with pytest.raises(FilterValidationError, match="non-empty field name"):
        normalize_class_declaration(DropdownFilter(""))

    with pytest.raises(FilterValidationError, match="non-empty field name"):
        normalize_class_declaration(ClassFilterDeclaration(field_name=None, filter_kind="dropdown"))  # type: ignore[arg-type]


def test_duplicate_resolved_param_names_raise_collision_error() -> None:
    declarations = [
        DropdownFilter("status"),
        DropdownFilter("state", alias="status"),
    ]

    with pytest.raises(FilterValidationError, match="collision"):
        normalize_declarations(declarations)


def test_unsupported_filter_kind_message_includes_invalid_and_supported_values() -> None:
    with pytest.raises(FilterValidationError, match="Unsupported filter_kind 'unknown_kind'") as exc_info:
        normalize_class_declaration(
            ClassFilterDeclaration(field_name="status", filter_kind="unknown_kind")
        )

    message = str(exc_info.value)
    assert "Supported kinds:" in message
    assert "dropdown" in message

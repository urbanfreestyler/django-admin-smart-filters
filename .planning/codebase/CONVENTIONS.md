# Coding Conventions

**Analysis Date:** 2026-04-20

## Naming Patterns

**Files:**
- Use `snake_case.py` module names for library code and tests, for example `django_smart_filters/query.py`, `django_smart_filters/validation.py`, and `tests/test_autocomplete_admin_endpoint.py`.

**Functions:**
- Use `snake_case` for functions and methods, including private helpers prefixed with `_`, for example `apply_filter_state` in `django_smart_filters/query.py`, `_parse_numeric_range` in `django_smart_filters/state.py`, and `_autocomplete_endpoint_url` in `django_smart_filters/admin.py`.

**Variables:**
- Use `snake_case` locals and parameters (`field_selector`, `normalized_specs`, `expected_calls`) across `django_smart_filters/admin.py` and `tests/test_admin_filters.py`.
- Use `UPPER_CASE` for module constants, such as `MIN_AUTOCOMPLETE_QUERY_LENGTH` in `django_smart_filters/autocomplete.py` and `SUPPORTED_FILTER_KINDS` in `django_smart_filters/validation.py`.

**Types:**
- Use PascalCase for classes and dataclasses, for example `FilterSpec` in `django_smart_filters/contracts.py`, `AutocompleteRequest` in `django_smart_filters/autocomplete.py`, and `ClassFilterDeclaration` in `django_smart_filters/declarations.py`.
- Use Protocol contracts for callable hooks (`QueryHook`, `WidgetHook`) in `django_smart_filters/contracts.py`.

## Code Style

**Formatting:**
- Tool used: Not detected (no formatter config file found at repository root; `pyproject.toml`, `ruff.toml`, `setup.cfg`, and `.editorconfig` are not present).
- Apply the existing style observed in source files under `django_smart_filters/` and `tests/`:
  - Type annotations on public functions and many internals (for example `parse_filter_state` in `django_smart_filters/state.py`).
  - Double-quoted strings and concise module docstrings (`django_smart_filters/query.py`, `django_smart_filters/chips.py`).
  - Blank-line grouped imports and line wrapping style consistent with Black-compatible formatting (`django_smart_filters/admin.py`, `tests/test_autocomplete_admin_endpoint.py`).

**Linting:**
- Tool used: Not detected (no lint config such as `.ruff.toml`, `pyproject.toml`, `.flake8`, or `pylintrc` found).
- Enforce type-friendly patterns already present in code:
  - Narrow exception types (`except (TypeError, ValueError) as exc`) in `django_smart_filters/query.py` and `django_smart_filters/state.py`.
  - Explicit `__all__` module exports in `django_smart_filters/__init__.py`, `django_smart_filters/query.py`, `django_smart_filters/state.py`, and `django_smart_filters/autocomplete.py`.

## Import Organization

**Order:**
1. Future imports (`from __future__ import annotations`) in modules like `django_smart_filters/query.py` and `django_smart_filters/admin.py`.
2. Standard library imports (`dataclasses`, `typing`, `collections.abc`, `datetime`) as seen in `django_smart_filters/contracts.py` and `django_smart_filters/autocomplete.py`.
3. Django and third-party imports (`django.http`, `django.template.loader`, `pytest`) in `django_smart_filters/admin.py` and `tests/test_query.py`.
4. Local package imports (`from django_smart_filters...`) in all package modules and tests.

**Path Aliases:**
- Not used. Imports use explicit absolute package paths like `from django_smart_filters.state import parse_filter_state` in `django_smart_filters/admin.py`.

## Error Handling

**Patterns:**
- Raise explicit validation exceptions with actionable messages:
  - `FilterValidationError` for contract/declaration failures in `django_smart_filters/validation.py` and `django_smart_filters/declarations.py`.
  - `ValueError` for invalid runtime input parsing in `django_smart_filters/query.py`, `django_smart_filters/state.py`, and `django_smart_filters/autocomplete.py`.
- Preserve exception causes using `raise ... from exc` when converting parse errors (`django_smart_filters/query.py`, `django_smart_filters/state.py`, `django_smart_filters/autocomplete.py`).
- In HTTP boundary code, convert parsing errors into structured 400 responses instead of uncaught exceptions (`smart_filter_autocomplete_view` in `django_smart_filters/admin.py`).

## Logging

**Framework:** console

**Patterns:**
- No active logging calls are present in `django_smart_filters/*.py` or `tests/*.py`.
- Use deterministic return values and explicit errors rather than log-driven control flow, following patterns in `django_smart_filters/query.py` and `django_smart_filters/state.py`.

## Comments

**When to Comment:**
- Keep comments sparse; prefer clear naming and small functions.
- Use short intent comments only where context is non-obvious, as in `tests/test_autocomplete_admin_endpoint.py` (the status-scoping expectation comment) and `tests/test_autocomplete.py` (server-side flow assertions).

**JSDoc/TSDoc:**
- Not applicable for Python modules.
- Use Python docstrings on modules/classes/functions for API intent, for example `django_smart_filters/admin.py`, `django_smart_filters/contracts.py`, and `django_smart_filters/autocomplete.py`.

## Function Design

**Size:**
- Keep public orchestration functions compact and delegate to private helpers, following `parse_filter_state` + `_parse_*` helpers in `django_smart_filters/state.py` and `apply_filter_value` + `_normalize_*` helpers in `django_smart_filters/query.py`.

**Parameters:**
- Use explicit typed parameters and keyword-only arguments where option clarity matters, for example `resolve_param_name(..., *, alias: str | None = None, multivalue: bool = False)` in `django_smart_filters/params.py` and `parse_autocomplete_request(..., *, state: Mapping[str, Any] | None = None)` in `django_smart_filters/autocomplete.py`.

**Return Values:**
- Return normalized, deterministic structures (`dict[str, Any]`, `QueryDict`, dataclasses) rather than mixed shapes, as in `django_smart_filters/state.py`, `django_smart_filters/chips.py`, and `django_smart_filters/autocomplete.py`.
- Use `None` to represent “no usable filter input” during normalization paths (`_normalize_single_value`, `_normalize_multi_select` in `django_smart_filters/query.py`).

## Module Design

**Exports:**
- Define stable public symbols via `__all__` where modules expose API surfaces, as in `django_smart_filters/__init__.py`, `django_smart_filters/query.py`, `django_smart_filters/state.py`, `django_smart_filters/chips.py`, and `django_smart_filters/autocomplete.py`.

**Barrel Files:**
- Use a minimal barrel at `django_smart_filters/__init__.py` to expose contracts (`FilterSpec`, `QueryHook`, `WidgetHook`) without re-exporting implementation modules.

---

*Convention analysis: 2026-04-20*

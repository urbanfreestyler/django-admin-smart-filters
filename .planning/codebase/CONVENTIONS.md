# Coding Conventions

**Analysis Date:** 2026-04-21

## Naming Patterns

**Files:**
- Use `snake_case.py` for Python modules in `django_smart_filters/` and tests in `tests/` (examples: `django_smart_filters/validation.py`, `tests/test_admin_filters.py`).
- Use `snake_case.html` for Django templates in `django_smart_filters/templates/admin/django_smart_filters/` (examples: `autocomplete_control.html`, `active_filters_bar.html`).
- Use `snake_case.js` for static JavaScript assets in `django_smart_filters/static/django_smart_filters/` (example: `autocomplete.js`).

**Functions:**
- Use `snake_case` for public and internal Python functions (examples: `parse_filter_state` in `django_smart_filters/state.py`, `_normalize_numeric_range` in `django_smart_filters/query.py`).
- Use `_leading_underscore` for module-private helpers (examples: `_parse_spec_value` in `django_smart_filters/state.py`, `_validate_param_collisions` in `django_smart_filters/declarations.py`).
- Use descriptive action-first names for behaviors (examples: `apply_filter_state`, `register_filter_component`, `resolve_theme_adapter`).

**Variables:**
- Use `snake_case` for local variables and constants in Python (examples: `field_selector`, `target_spec` in `django_smart_filters/admin.py`).
- Use `UPPER_SNAKE_CASE` for module constants (examples: `MIN_AUTOCOMPLETE_QUERY_LENGTH` in `django_smart_filters/autocomplete.py`, `SUPPORTED_FILTER_KINDS` in `django_smart_filters/validation.py`).

**Types:**
- Use PascalCase for classes and dataclasses (examples: `FilterSpec` in `django_smart_filters/contracts.py`, `ThemeAdapter` in `django_smart_filters/theme.py`).
- Use Protocol types for extension hooks (examples: `QueryHook`, `WidgetHook` in `django_smart_filters/contracts.py`).

## Code Style

**Formatting:**
- Tool used: Not detected in repository config files (`pyproject.toml`, `setup.cfg`, `tox.ini`, `pytest.ini` not present).
- Apply existing in-code style from `django_smart_filters/*.py`: typed signatures, explicit return annotations in tests and core modules, and short module-level docstrings.
- Use `from __future__ import annotations` in Python modules and tests (examples: `django_smart_filters/admin.py`, `tests/test_query.py`).

**Linting:**
- Tool used: Not detected in repository config files.
- Follow strict typing and clear branch structure already used across `django_smart_filters/` modules.
- Raise actionable exceptions with user-facing messages in validation paths (examples in `django_smart_filters/validation.py`, `django_smart_filters/autocomplete.py`).

## Import Organization

**Order:**
1. `__future__` imports first (example: `django_smart_filters/query.py`).
2. Standard library imports next (`collections.abc`, `datetime`, `typing` in `django_smart_filters/query.py`).
3. Django imports next when needed (`django.http` in `django_smart_filters/state.py`).
4. Local package imports last (`django_smart_filters.contracts`, `django_smart_filters.validation`).

**Path Aliases:**
- Not used. Import with explicit package paths such as `from django_smart_filters.builder import Filter` in `tests/test_declarations.py`.

## Error Handling

**Patterns:**
- Validate early and fail fast (`validate_filter_spec(spec)` at entry points in `django_smart_filters/query.py` and `django_smart_filters/state.py`).
- Raise `ValueError`/`FilterValidationError` with deterministic messages for invalid user inputs (examples: `_parse_positive_int` in `django_smart_filters/autocomplete.py`, `validate_filter_spec` in `django_smart_filters/validation.py`).
- Convert internal exceptions to HTTP 400 JSON responses at admin boundaries (example: `smart_filter_autocomplete_view` in `django_smart_filters/admin.py`).

## Logging

**Framework:** console (none detected in codebase)

**Patterns:**
- No logging calls detected in `django_smart_filters/*.py`.
- For new code, preserve current convention: return deterministic errors instead of adding ad-hoc logging.

## Comments

**When to Comment:**
- Prefer docstrings over inline comments for module/class/function intent (examples across `django_smart_filters/contracts.py`, `django_smart_filters/chips.py`).
- Use inline comments in tests only to clarify scenario intent (example line comment in `tests/test_autocomplete_admin_endpoint.py`).

**JSDoc/TSDoc:**
- Not applicable for Python modules.
- JavaScript file `django_smart_filters/static/django_smart_filters/autocomplete.js` uses no JSDoc; keep functions self-descriptive with clear naming.

## Function Design

**Size:**
- Keep orchestration in top-level functions/methods and move detailed parsing/normalization to helpers (pattern in `django_smart_filters/state.py` and `django_smart_filters/query.py`).

**Parameters:**
- Prefer typed, explicit parameters and keyword-only args for optional context (example: `parse_autocomplete_request(..., *, state=None)` in `django_smart_filters/autocomplete.py`).
- Use `Mapping`/`Iterable` abstractions for input collections (examples in `django_smart_filters/chips.py`, `django_smart_filters/state.py`).

**Return Values:**
- Return normalized domain values (dict/list/bool/None) for parser helpers (examples: `_parse_numeric_range` in `django_smart_filters/state.py`).
- Return immutable dataclasses for structured responses where shape matters (examples: `AutocompleteRequest`, `AutocompleteResultPage` in `django_smart_filters/autocomplete.py`).

## Module Design

**Exports:**
- Define explicit `__all__` in public modules to constrain API surface (examples: `django_smart_filters/__init__.py`, `django_smart_filters/autocomplete.py`, `django_smart_filters/registry.py`).

**Barrel Files:**
- Use `django_smart_filters/__init__.py` as the package barrel for stable public imports (`FilterSpec`, `register_filter_component`, `resolve_filter_component`).

---

*Convention analysis: 2026-04-21*

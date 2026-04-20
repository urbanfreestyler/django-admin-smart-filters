# Architecture

**Analysis Date:** 2026-04-20

## Pattern Overview

**Overall:** Layered Django admin mixin with a functional core for declaration normalization, URL state parsing, queryset application, and UI rendering.

**Key Characteristics:**
- Use `SmartFilterAdminMixin` in `django_smart_filters/admin.py` as the single integration point with `ModelAdmin` lifecycle methods (`get_queryset`, `changelist_view`, `get_urls`).
- Keep filter logic in pure-ish functions (`django_smart_filters/declarations.py`, `django_smart_filters/state.py`, `django_smart_filters/query.py`, `django_smart_filters/chips.py`) so behavior is deterministic and testable without DB-heavy setup.
- Drive all behavior from normalized `FilterSpec` contracts defined in `django_smart_filters/contracts.py`.

## Layers

**Public API Layer:**
- Purpose: Expose stable top-level contracts to consumers.
- Location: `django_smart_filters/__init__.py`
- Contains: Re-exports (`FilterSpec`, `QueryHook`, `WidgetHook`).
- Depends on: `django_smart_filters/contracts.py`.
- Used by: External adopters and tests importing package-level symbols.

**Declaration & Validation Layer:**
- Purpose: Convert class-style/fluent declarations into validated, collision-safe specs.
- Location: `django_smart_filters/declarations.py`, `django_smart_filters/builder.py`, `django_smart_filters/params.py`, `django_smart_filters/validation.py`, `django_smart_filters/contracts.py`
- Contains: `ClassFilterDeclaration`, `BuilderFilterDeclaration`, `Filter.field(...)` builder, param naming, `validate_filter_spec`, `FilterValidationError`.
- Depends on: Dataclasses/typing plus internal contracts.
- Used by: `django_smart_filters/admin.py` (`get_smart_filter_specs`) and unit tests in `tests/test_declarations.py`, `tests/test_validation.py`.

**State & Query Execution Layer:**
- Purpose: Parse GET params to normalized state and apply that state to querysets by filter kind.
- Location: `django_smart_filters/state.py`, `django_smart_filters/query.py`
- Contains: `parse_filter_state`, `serialize_filter_state`, `apply_filter_value`, `apply_filter_state`.
- Depends on: `FilterSpec` + validation from `django_smart_filters/validation.py`; Django `QueryDict` in `state.py`.
- Used by: `SmartFilterAdminMixin` in `django_smart_filters/admin.py`; tests in `tests/test_state.py`, `tests/test_query.py`.

**Admin Integration Layer:**
- Purpose: Plug smart filters into Django admin change list and expose autocomplete endpoint.
- Location: `django_smart_filters/admin.py`
- Contains: `SmartFilterAdminMixin` and helper methods for controls/chips/endpoint URLs.
- Depends on: Declarations, state, query, chips, autocomplete modules.
- Used by: Downstream `ModelAdmin` subclasses (demonstrated in `tests/test_admin_filters.py`, `tests/test_autocomplete_admin_endpoint.py`, `tests/test_autocomplete_ui.py`).

**UI Rendering & Frontend Behavior Layer:**
- Purpose: Render filter controls and active chips, then progressively enhance autocomplete in browser.
- Location: `django_smart_filters/templates/admin/django_smart_filters/*.html`, `django_smart_filters/static/django_smart_filters/autocomplete.js`
- Contains: Control templates, chip templates, active-bar template, JS runtime with debounce/stale-response guard.
- Depends on: Control/chip context produced in `django_smart_filters/admin.py`.
- Used by: `render_smart_filter_controls` and `render_smart_filter_active_bar` in `django_smart_filters/admin.py`.

## Data Flow

**Changelist Filtering Flow:**

1. `SmartFilterAdminMixin.get_smart_filter_specs()` in `django_smart_filters/admin.py` normalizes declarations via `normalize_declarations(...)` in `django_smart_filters/declarations.py`.
2. `parse_filter_state(...)` in `django_smart_filters/state.py` reads `request.GET` into deterministic state keyed by `FilterSpec.param_name`.
3. `apply_filter_state(...)` in `django_smart_filters/query.py` applies each filter in declaration order to queryset.
4. `SmartFilterAdminMixin.changelist_view(...)` in `django_smart_filters/admin.py` builds control dictionaries and chip dictionaries, then renders HTML snippets via templates in `django_smart_filters/templates/admin/django_smart_filters/`.
5. Returned context is merged into admin changelist extra context; default admin template remains in use (`change_list_template is None` validated in `tests/test_admin_filters.py`).

**Autocomplete Endpoint Flow:**

1. `SmartFilterAdminMixin.get_urls()` in `django_smart_filters/admin.py` registers `smart-filters/autocomplete/` under admin route namespace.
2. Browser JS in `django_smart_filters/static/django_smart_filters/autocomplete.js` issues GET requests with `field`, `query`, `page`, and `limit`.
3. `smart_filter_autocomplete_view(...)` in `django_smart_filters/admin.py` resolves target spec, parses request with `parse_autocomplete_request(...)` in `django_smart_filters/autocomplete.py`, and excludes the active target field from scoped state.
4. Base queryset is narrowed by remaining active filters via `apply_filter_state(...)` in `django_smart_filters/query.py`.
5. `search_autocomplete_options(...)` in `django_smart_filters/autocomplete.py` returns paginated payload (`results`, `pagination`) consumed by JS.

**State Management:**
- Use URL query parameters as the source of truth (`request.GET`) in `django_smart_filters/state.py` and `django_smart_filters/admin.py`.
- Keep canonical parameter naming through `resolve_param_name(...)` in `django_smart_filters/params.py`.
- Preserve deterministic ordering and query-string rebuilding in `build_remove_one_url(...)` / `_querydict_to_querystring(...)` in `django_smart_filters/chips.py`.

## Key Abstractions

**FilterSpec Contract:**
- Purpose: Canonical representation of one filter declaration.
- Examples: `django_smart_filters/contracts.py`, constructed in `django_smart_filters/declarations.py` and `django_smart_filters/builder.py`.
- Pattern: Immutable dataclass boundary (`@dataclass(frozen=True)`) passed across all modules.

**Declaration APIs (Class + Fluent):**
- Purpose: Provide two authoring styles that converge to identical specs.
- Examples: `DropdownFilter(...)` in `django_smart_filters/declarations.py`, `Filter.field(...).dropdown()` in `django_smart_filters/builder.py`.
- Pattern: Adapter normalization path (`normalize_class_declaration` and `normalize_builder_declaration`) validated in `tests/test_declarations.py`.

**SmartFilterAdminMixin:**
- Purpose: Non-invasive admin extension with queryset, context, and endpoint hooks.
- Examples: `django_smart_filters/admin.py`.
- Pattern: Mixin composition with overridable hooks (`get_smart_filter_declarations`, `get_smart_filter_base_queryset`, template path attributes).

## Entry Points

**Admin Mixin Entry Point:**
- Location: `django_smart_filters/admin.py` (`SmartFilterAdminMixin`).
- Triggers: Django admin calls `get_queryset`, `changelist_view`, `get_urls` on registered `ModelAdmin`.
- Responsibilities: Normalize declarations, parse URL state, filter queryset, build UI context, register autocomplete route, serve autocomplete JSON.

**Declaration Authoring Entry Points:**
- Location: `django_smart_filters/declarations.py` (`DropdownFilter`), `django_smart_filters/builder.py` (`Filter.field`).
- Triggers: Developer configures `smart_filters` list in `ModelAdmin` subclass.
- Responsibilities: Produce declarations that normalize into valid `FilterSpec` objects.

**Package API Entry Point:**
- Location: `django_smart_filters/__init__.py`.
- Triggers: Consumer imports package-level contracts.
- Responsibilities: Provide stable top-level exports.

## Error Handling

**Strategy:** Fail fast at declaration normalization and request parsing boundaries; return structured HTTP 400 for invalid autocomplete requests.

**Patterns:**
- Raise `FilterValidationError` from `django_smart_filters/validation.py` during spec validation in normalization path (`django_smart_filters/declarations.py`).
- Raise `ValueError` for malformed runtime values in `django_smart_filters/state.py`, `django_smart_filters/query.py`, and `django_smart_filters/autocomplete.py`; convert to JSON 400 in `smart_filter_autocomplete_view(...)` in `django_smart_filters/admin.py`.

## Cross-Cutting Concerns

**Logging:** Not detected in `django_smart_filters/*.py`; add logging at admin boundary (`django_smart_filters/admin.py`) when introducing operational diagnostics.
**Validation:** Centralized through `validate_filter_spec(...)` in `django_smart_filters/validation.py` and reused in `django_smart_filters/declarations.py`, `django_smart_filters/state.py`, `django_smart_filters/query.py`, `django_smart_filters/autocomplete.py`.
**Authentication:** Delegate endpoint protection to Django admin wrapper in `get_urls()` via `self.admin_site.admin_view(...)` in `django_smart_filters/admin.py`.

---

*Architecture analysis: 2026-04-20*

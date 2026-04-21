# Architecture

**Analysis Date:** 2026-04-21

## Pattern Overview

**Overall:** Layered Django admin extension library with declarative configuration and adapter-based rendering.

**Key Characteristics:**
- Keep Django admin as the orchestration surface by extending `ModelAdmin` through `SmartFilterAdminMixin` in `django_smart_filters/admin.py`.
- Normalize all declaration styles into one internal contract (`FilterSpec`) before any state/query processing in `django_smart_filters/declarations.py` and `django_smart_filters/contracts.py`.
- Isolate UI rendering behind template adapter resolution so query/state behavior remains unchanged across themes in `django_smart_filters/theme.py`.

## Layers

**Public API Layer:**
- Purpose: Expose stable extension and registry surface for consumers.
- Location: `django_smart_filters/__init__.py`
- Contains: Re-exported contracts and registry functions (`FilterComponent`, `FilterSpec`, hooks, register/resolve/clear).
- Depends on: `django_smart_filters/contracts.py`, `django_smart_filters/registry.py`
- Used by: App/admin code and docs snippets in `docs/extension_hooks.md`, `docs/examples.md`

**Declaration & Contract Layer:**
- Purpose: Define and validate filter declarations before runtime.
- Location: `django_smart_filters/contracts.py`, `django_smart_filters/declarations.py`, `django_smart_filters/builder.py`, `django_smart_filters/params.py`, `django_smart_filters/validation.py`, `django_smart_filters/registry.py`
- Contains: Dataclass contracts (`FilterSpec`, declaration objects), fluent builder API, parameter naming rules, validation, component registry.
- Depends on: Pure Python dataclasses/protocols and internal validation/registry modules.
- Used by: `django_smart_filters/admin.py`, `django_smart_filters/query.py`, `django_smart_filters/state.py`

**Query/State Execution Layer:**
- Purpose: Parse URL state and apply deterministic queryset filtering.
- Location: `django_smart_filters/state.py`, `django_smart_filters/query.py`, `django_smart_filters/autocomplete.py`, `django_smart_filters/chips.py`
- Contains: QueryDict parsing/serialization, kind-specific filter normalization and lookup mapping, paginated autocomplete search, active chip/reset URL mechanics.
- Depends on: `FilterSpec` contract and validation.
- Used by: `SmartFilterAdminMixin` request handlers in `django_smart_filters/admin.py`

**Admin Integration Layer:**
- Purpose: Plug smart filters into Django admin changelist and custom endpoint lifecycle.
- Location: `django_smart_filters/admin.py`
- Contains: `get_queryset()` override, `changelist_view()` context assembly, autocomplete route/view registration, control view-model construction.
- Depends on: Declaration, state, query, autocomplete, chips, and theme layers.
- Used by: Consumer `ModelAdmin` classes that mix in `SmartFilterAdminMixin` (see patterns in `tests/test_admin_filters.py`).

**Presentation Adapter Layer:**
- Purpose: Render controls/active bars through adapter-selected templates and frontend behavior.
- Location: `django_smart_filters/theme.py`, `django_smart_filters/templates/admin/django_smart_filters/theme/default/*.html`, wrapper templates in `django_smart_filters/templates/admin/django_smart_filters/*.html`, JS in `django_smart_filters/static/django_smart_filters/autocomplete.js`
- Contains: `ThemeAdapter` contract, default template mapping, control fragments, chip rendering, autocomplete runtime.
- Depends on: Context produced by `SmartFilterAdminMixin`.
- Used by: Django template loader during changelist rendering.

## Data Flow

**Changelist Query Filtering Flow:**

1. `SmartFilterAdminMixin.get_queryset()` in `django_smart_filters/admin.py` obtains base queryset via `get_smart_filter_base_queryset()`.
2. Declarations are normalized to `FilterSpec` objects with `normalize_declarations()` in `django_smart_filters/declarations.py`.
3. URL parameters are parsed into typed state with `parse_filter_state()` in `django_smart_filters/state.py`.
4. Filter state is applied deterministically by spec order with `apply_filter_state()` in `django_smart_filters/query.py`.

**Changelist UI Context Flow:**

1. `SmartFilterAdminMixin.changelist_view()` in `django_smart_filters/admin.py` resolves adapter (`resolve_theme_adapter()`) and state (`parse_filter_state()`).
2. `_build_filter_controls()` builds per-filter control models, including autocomplete metadata (`endpoint_url`, `min_query_length`, `page_size`).
3. `build_active_filter_chips()` / `build_remove_one_url()` / `build_reset_all_url()` in `django_smart_filters/chips.py` generate active filter UX actions.
4. `render_smart_filter_controls()` and `render_smart_filter_active_bar()` render adapter templates and inject HTML into changelist context.

**Autocomplete Endpoint Flow:**

1. `get_urls()` in `django_smart_filters/admin.py` registers `smart-filters/autocomplete/` under model admin routes.
2. `smart_filter_autocomplete_view()` resolves target autocomplete spec and rejects unknown/non-autocomplete fields with HTTP 400 JSON.
3. Existing non-target state is parsed and applied (`parse_filter_state()` + `apply_filter_state()`) to scope autocomplete results.
4. `parse_autocomplete_request()` validates query/page/limit in `django_smart_filters/autocomplete.py`, then `search_autocomplete_options()` returns paginated `{results, pagination}` payload.

**State Management:**
- Use URL as canonical state store through `parse_filter_state()` and `serialize_filter_state()` in `django_smart_filters/state.py`.
- Keep ordering deterministic by iterating normalized specs, then serializing query params in stable sorted order for chip URLs in `django_smart_filters/chips.py`.

## Key Abstractions

**Normalized Filter Contract (`FilterSpec`):**
- Purpose: Single internal representation for every filter declaration style.
- Examples: `django_smart_filters/contracts.py`, usage in `django_smart_filters/query.py`, `django_smart_filters/state.py`, `django_smart_filters/admin.py`
- Pattern: Normalize early, validate once, consume everywhere.

**Declaration Styles (Class + Fluent):**
- Purpose: Provide ergonomic authoring while preserving one normalization path.
- Examples: `ClassFilterDeclaration` / `DropdownFilter` in `django_smart_filters/declarations.py`; fluent `Filter.field(...).<kind>()` in `django_smart_filters/builder.py`
- Pattern: Route both styles through `normalize_class_declaration()` / `normalize_builder_declaration()` and then `normalize_declarations()`.

**Theme Adapter Contract (`ThemeAdapter`):**
- Purpose: Separate template selection from filter semantics.
- Examples: `django_smart_filters/theme.py`, defaults at `django_smart_filters/templates/admin/django_smart_filters/theme/default/*.html`
- Pattern: Resolve adapter at runtime and render by template path, not hardcoded HTML.

**Component Registry (`FilterComponent` + registry funcs):**
- Purpose: Allow custom component key registration with fail-fast resolution.
- Examples: `django_smart_filters/contracts.py`, `django_smart_filters/registry.py`, extension docs in `docs/extension_hooks.md`
- Pattern: Register once by key, resolve during declaration normalization, reject duplicates/unknown keys immediately.

## Entry Points

**Django Admin Runtime Entry Point:**
- Location: `django_smart_filters/admin.py` (`SmartFilterAdminMixin`)
- Triggers: Django admin changelist request and admin URL dispatch.
- Responsibilities: Build specs/state, apply queryset filtering, add smart filter context/HTML, register and serve autocomplete endpoint.

**Declaration Authoring Entry Points:**
- Location: `django_smart_filters/declarations.py` (`DropdownFilter`, `ClassFilterDeclaration`) and `django_smart_filters/builder.py` (`Filter.field`)
- Triggers: Consumer admin class configuration (`smart_filters = [...]`).
- Responsibilities: Capture declaration intent and normalize to `FilterSpec`.

**Extension Registration Entry Point:**
- Location: `django_smart_filters/registry.py` and re-exports in `django_smart_filters/__init__.py`
- Triggers: App startup or module import where custom components are registered.
- Responsibilities: Register, resolve, and clear component mappings.

## Error Handling

**Strategy:** Fail fast during normalization/validation and return explicit API errors for HTTP endpoints.

**Patterns:**
- Raise `FilterValidationError` for invalid declarations or unsupported kinds in `django_smart_filters/validation.py` and declaration normalization in `django_smart_filters/declarations.py`.
- Raise `ValueError` for malformed runtime values (boolean/numeric/date/autocomplete paging) in `django_smart_filters/state.py`, `django_smart_filters/query.py`, and `django_smart_filters/autocomplete.py`.
- Convert endpoint-level validation failures to structured `JsonResponse(..., status=400)` in `smart_filter_autocomplete_view()` in `django_smart_filters/admin.py`.

## Cross-Cutting Concerns

**Logging:** No dedicated logging layer detected in `django_smart_filters/*.py`.
**Validation:** Centralized spec validation in `django_smart_filters/validation.py`, plus request/value validation in `django_smart_filters/state.py` and `django_smart_filters/autocomplete.py`.
**Authentication:** Endpoint access is wrapped with `self.admin_site.admin_view(...)` in `django_smart_filters/admin.py`, relying on Django admin auth/permissions.

---

*Architecture analysis: 2026-04-21*

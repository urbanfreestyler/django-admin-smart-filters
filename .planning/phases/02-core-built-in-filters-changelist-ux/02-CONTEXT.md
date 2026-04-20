# Phase 2: Core Built-in Filters & Changelist UX - Context

**Gathered:** 2026-04-20 (auto mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers production-ready built-in filter types for Django Admin changelist UX in default admin: dropdown, multi-select, date-range, numeric-range, and boolean-toggle filters, plus visible active-filter state, clear/reset actions, and stable URL query-state behavior. It focuses on default Django Admin integration and user interaction quality; async autocomplete scale behavior and theme adapter expansion remain in later phases.

</domain>

<decisions>
## Implementation Decisions

### Built-in Filter Behavior
- **D-01:** Implement all Phase 2 filter kinds as first-class declarations wired from the shared `FilterSpec` contract: `dropdown`, `multi_select`, `date_range`, `numeric_range`, and `boolean_toggle`.
- **D-02:** Keep each filter kind mapped to deterministic query-parameter behavior built on Phase 1 naming rules, preserving mixed-filter composition predictability.
- **D-03:** Apply validation and normalization at declaration processing time (fail-fast), not lazily during queryset execution.

### Active Filter Visibility (Tags/Chips)
- **D-04:** Show active filters as compact chips above the changelist result area with one chip per active criterion.
- **D-05:** Chip labels should use human-readable field title + selected value/range summary, not raw query key names.

### Clear and Reset UX
- **D-06:** Provide both per-chip remove actions and a global "Reset all filters" control on the same visible bar as active chips.
- **D-07:** Removing one chip only clears that specific criterion and preserves all other active criteria.

### URL State and Shareability
- **D-08:** Treat URL query parameters as source-of-truth for filter state, so browser refresh/back/forward and share links preserve exact filter selections.
- **D-09:** Keep parameter schema stable and deterministic; avoid ephemeral client-only state for selected filters.

### Default Admin Integration
- **D-10:** Prioritize default Django Admin template/block integration for this phase with no custom admin replacement or incompatible rendering model.
- **D-11:** Place filter controls and active-state UI using additive template customization patterns that preserve standard changelist behavior.

### OpenCode's Discretion
- Visual styling details for chips/toggles/range controls in default admin, as long as clarity and consistency are maintained.
- Exact helper/module decomposition for rendering utilities and URL-state helpers.
- Minor copy text for empty-active-filter state and reset affordances.

</decisions>

<specifics>
## Specific Ideas

- Preserve Django-admin-native interaction flow: selecting filters should feel like a better changelist, not a separate UI framework.
- Keep active-state UI highly legible for admins handling many records and multiple filter criteria.
- Use the existing `Filter.field(...).{kind}()` fluent path and class-style path as equal inputs to the same normalized behavior.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirement mapping
- `.planning/ROADMAP.md` — Phase 2 goal, requirement set, and UX success criteria.
- `.planning/REQUIREMENTS.md` — FILT-01, FILT-03, FILT-04, FILT-05, FILT-06, THEM-01, UX-01, UX-02, UX-03 definitions.

### Prior locked decisions to preserve
- `.planning/phases/01-declarative-filter-api-foundation/01-CONTEXT.md` — locked API/validation/param decisions carried forward into UI behavior.

### Existing implementation baseline
- `django_smart_filters/contracts.py` — shared normalized `FilterSpec` contract and hooks.
- `django_smart_filters/declarations.py` — normalization flow and collision handling.
- `django_smart_filters/builder.py` — fluent declaration entrypoints for all filter kinds used in this phase.
- `django_smart_filters/params.py` — deterministic query parameter derivation semantics.
- `django_smart_filters/validation.py` — fail-fast validation rules.
- `tests/test_declarations.py` — current normalization/parity expectations to preserve while adding changelist UX.

### Product intent and constraints
- `.planning/PROJECT.md` — core value and constraints (Django-native, performance-safe, theme-compatible scope).
- `docs/project_description.md` — MVP intent for filter types and UX behavior.
- `AGENTS.md` — project-level workflow and implementation constraints.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `FilterSpec` contract already defines the normalized shape for filter behavior (`django_smart_filters/contracts.py`).
- Class and fluent declaration normalization already converge through shared path (`django_smart_filters/declarations.py`, `django_smart_filters/builder.py`).
- Deterministic/alias-aware parameter naming helper exists and should remain canonical (`django_smart_filters/params.py`).

### Established Patterns
- All declarations are validated at normalization time via fail-fast `FilterValidationError` flow (`django_smart_filters/validation.py`).
- Existing tests assert class/fluent parity and ordered mixed declarations; Phase 2 should extend, not replace, this behavior (`tests/test_declarations.py`).

### Integration Points
- Phase 2 should extend declaration outputs into default-admin changelist rendering and interaction components while preserving current normalization contracts.
- New UX/state modules should consume `FilterSpec` and parameter helpers directly so Phase 3 async filtering can build on the same state model.

</code_context>

<deferred>
## Deferred Ideas

- Async autocomplete performance/debounce/pagination concerns remain primarily in Phase 3 scope.
- Theme adapter expansion beyond default admin support remains in Phase 4 scope.

None otherwise — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-core-built-in-filters-changelist-ux*
*Context gathered: 2026-04-20*

# Phase 3: Async Autocomplete & Scale Performance - Context

**Gathered:** 2026-04-20 (auto mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers async autocomplete filtering for high-cardinality datasets with server-side search, pagination, debounced request behavior, and lazy option loading performance safeguards. It extends the existing filter/state/admin pipeline from Phases 1-2 without expanding into broader theme adapter work or extension SDK concerns.

</domain>

<decisions>
## Implementation Decisions

### Async Endpoint Contract
- **D-01:** Implement autocomplete as server-side endpoints wired to declared filter specs, not client-side preloaded options.
- **D-02:** Use deterministic request/response contract keyed by existing `FilterSpec` and normalized param behavior from earlier phases.
- **D-03:** Restrict returned options to the minimum shape required for selection (stable id/value + display label), with no unrelated payload expansion.

### Search Semantics and Query Behavior
- **D-04:** Execute search on the server for each autocomplete request using declared field/filter context and current query text.
- **D-05:** Require minimum query length before costly lookup execution to reduce unnecessary high-cardinality scans.
- **D-06:** Preserve existing active filter state composition so autocomplete selections combine predictably with other filters.

### Pagination and Scale Control
- **D-07:** Enforce paginated option responses with explicit page/limit semantics and deterministic ordering for stable browsing.
- **D-08:** Use conservative page-size defaults to protect response latency and DB load; avoid unbounded result windows.
- **D-09:** Ensure lazy loading of options end-to-end (load on demand, not at changelist render time).

### Debounce and Request Churn Handling
- **D-10:** Apply debounced autocomplete querying at the integration layer so rapid typing does not trigger one request per keystroke.
- **D-11:** Ignore or supersede stale in-flight responses when newer query input exists, so UI state tracks latest intent.

### Performance and Safety Guardrails
- **D-12:** Keep memory usage bounded by processing only requested page slices and avoiding full choice-list materialization.
- **D-13:** Validate autocomplete request parameters with fail-fast behavior consistent with prior declaration/state validation patterns.
- **D-14:** Keep implementation Django-admin-native and additive, with no SPA framework coupling or custom admin replacement.

### OpenCode's Discretion
- Exact debounce interval and default page size values, as long as they are documented and conservative for high-cardinality admin usage.
- Internal module split between endpoint handlers, search adapters, and response serializers.
- Minor endpoint naming details while preserving consistent deterministic contracts.

</decisions>

<specifics>
## Specific Ideas

- Build async autocomplete on top of the existing `SmartFilterAdminMixin` and state/query foundations so behavior remains consistent with existing filter UX.
- Keep UX responsive for admins by reducing needless query churn and making pagination predictable.
- Preserve deterministic URLs and mixed-filter composition as autocomplete joins existing filter controls.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` — Phase 3 goal, success criteria, and dependency boundary.
- `.planning/REQUIREMENTS.md` — FILT-02, PERF-01, PERF-02, PERF-03, PERF-04 requirement definitions.

### Prior locked decisions to preserve
- `.planning/phases/01-declarative-filter-api-foundation/01-CONTEXT.md` — declaration, validation, deterministic param decisions.
- `.planning/phases/02-core-built-in-filters-changelist-ux/02-CONTEXT.md` — URL-source-of-truth state, additive admin integration, clear/reset UX expectations.

### Existing implementation baseline
- `django_smart_filters/contracts.py` — normalized `FilterSpec` and hook contracts.
- `django_smart_filters/declarations.py` — declaration normalization and collision handling.
- `django_smart_filters/state.py` — deterministic parse/serialize state behavior to compose with autocomplete.
- `django_smart_filters/query.py` — filter-kind queryset application path to preserve mixed composition.
- `django_smart_filters/admin.py` — current default-admin integration seam for filter controls/state context.
- `django_smart_filters/chips.py` — active-state URL operations that must remain compatible.
- `tests/test_state.py` — state determinism and validation expectations.
- `tests/test_query.py` — query application behavior expectations.
- `tests/test_admin_filters.py` — additive admin integration expectations.
- `tests/test_active_filters_ui.py` — deterministic URL/chip behavior expectations.

### Product and project constraints
- `.planning/PROJECT.md` — core value and constraints (Django-native, performance, compatibility scope).
- `docs/project_description.md` — original async autocomplete and pagination goals.
- `AGENTS.md` — project workflow and implementation constraints.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `FilterSpec` + declaration normalization pipeline already supports an `autocomplete` filter kind in fluent declarations (`builder.py`, `declarations.py`).
- `SmartFilterAdminMixin` already centralizes changelist state parsing and queryset application (`admin.py`).
- `parse_filter_state` and `apply_filter_state` provide deterministic backbone for composing autocomplete with existing filters (`state.py`, `query.py`).

### Established Patterns
- Fail-fast validation is consistently applied before behavior execution (`validation.py`, declaration/state/query paths).
- Default admin integration is additive via templates/context, not replacement (`admin.py`, template files).
- Deterministic ordering and URL-state semantics are tested and expected by current suite.

### Integration Points
- Phase 3 should add async endpoint + request handling that plugs into existing admin integration layer.
- Autocomplete responses should align with existing state/param conventions so selected values flow through current query pipeline.
- Performance controls (debounce/pagination/lazy loading) should be implemented without breaking existing Phase 2 control/chip workflows.

</code_context>

<deferred>
## Deferred Ideas

- Broader theme adapter expansion and non-default theme compatibility hardening remain Phase 4 scope.
- Extension-SDK hardening and broader custom filter platform concerns remain later-phase scope.

None otherwise — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-async-autocomplete-scale-performance*
*Context gathered: 2026-04-20*

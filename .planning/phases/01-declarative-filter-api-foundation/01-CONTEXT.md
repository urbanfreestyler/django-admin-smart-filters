# Phase 1: Declarative Filter API Foundation - Context

**Gathered:** 2026-04-20 (auto mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase defines a stable, `list_filter`-compatible API contract so developers can declare smart admin filters with minimal boilerplate. It covers declaration ergonomics, configuration validation, and core extension seams for filter definitions. It does not include full async autocomplete behavior, full theme adapter implementation, or broader UX features from later phases.

</domain>

<decisions>
## Implementation Decisions

### API Declaration Style
- **D-01:** Support both class-style declarations and fluent builder declarations in v1 API surface, with a shared internal normalized spec.
- **D-02:** Keep Django-native `list_filter` compatibility as the primary contract, so adoption requires no admin paradigm change.

### Configuration and Validation Contract
- **D-03:** Use fail-fast validation for invalid filter definitions at startup/import-time where possible, with clear actionable errors.
- **D-04:** Use deterministic query parameter naming derived from field identity, with optional explicit aliases when needed.

### Filter Spec and Extensibility Foundation
- **D-05:** Standardize on a base filter component contract that supports query application and option behavior through explicit hooks.
- **D-06:** Keep extension hooks practical and bounded in this phase (query logic and widget behavior hooks only), deferring broader plugin concerns.

### OpenCode's Discretion
- Exact package/module layout for API internals.
- Naming of internal helper classes/functions that are not part of public API.
- Error message wording style, as long as messages remain specific and actionable.

</decisions>

<specifics>
## Specific Ideas

- Keep the external API readable enough that a `ModelAdmin` class shows filter intent in one quick scan.
- Preserve compatibility with existing Django Admin habits rather than introducing a new conceptual model.
- Normalize both declaration styles into one internal representation so planner/executor can avoid duplicated logic paths.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirement mapping
- `.planning/ROADMAP.md` — Phase 1 goal, dependency boundaries, and success criteria.
- `.planning/REQUIREMENTS.md` — API-01 and API-02 requirement definitions and traceability expectations.

### Product intent and constraints
- `.planning/PROJECT.md` — Core value, constraints, and key project decisions that shape API design.
- `docs/project_description.md` — Original project framing, MVP scope, and declarative API examples.
- `AGENTS.md` — Current generated project guidance and GSD workflow constraints.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- No implementation source files exist yet; this phase will establish first reusable API primitives.

### Established Patterns
- Planning artifacts establish a Django-native architecture and phase sequencing: API foundation first, then UX/autocomplete/theme depth.
- Compatibility and performance constraints are already fixed at project level and must shape API boundaries now.

### Integration Points
- Phase 1 outputs should become the contract consumed by later filter-type phases (Phase 2 filter UIs and Phase 3 async autocomplete).
- API contracts must integrate with Django Admin `list_filter` semantics and remain extensible for adapter/theme work in Phase 4.

</code_context>

<deferred>
## Deferred Ideas

- Advanced query-language semantics beyond current requirement scope — Phase 4+ consideration.
- Rich UX concerns (chips presentation, per-filter visuals) beyond API foundation — covered in later phases.

None otherwise — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-declarative-filter-api-foundation*
*Context gathered: 2026-04-20*

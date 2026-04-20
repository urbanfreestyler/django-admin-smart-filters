# ROADMAP: Django Smart Filters

## Phases

- [x] **Phase 1: Declarative Filter API Foundation** - Developers can define smart admin filters with a stable, list_filter-compatible contract. (completed 2026-04-20)
- [x] **Phase 2: Core Built-in Filters & Changelist UX** - Users can apply and manage common filters in default Django Admin with reliable URL-based state. (completed 2026-04-20)
- [ ] **Phase 3: Async Autocomplete & Scale Performance** - Users can filter high-cardinality datasets through responsive, server-driven autocomplete.
- [ ] **Phase 4: Theme Adapters, Extension Hooks & Docs** - Developers can adapt rendering, extend filter behavior, and ship custom filters using documented extension points.

## Phase Details

### Phase 1: Declarative Filter API Foundation
**Goal**: Developers can configure smart admin filters with minimal boilerplate through a stable API contract compatible with Django Admin patterns.
**Depends on**: Nothing (first phase)
**Requirements**: API-01, API-02
**Success Criteria** (what must be TRUE):
  1. Developer can declare a smart filter in `list_filter` without replacing standard Django Admin usage patterns.
  2. Developer can configure equivalent filter behavior using either class-based declaration or fluent builder style.
  3. Developer can mix multiple declared filters in one changelist and the resulting query parameters remain predictable.
**Plans**: 1 plans

Plans:
- [ ] 01-01-PLAN.md — Define normalized declarative filter API contract with class/fluent parity and fail-fast validation.

### Phase 2: Core Built-in Filters & Changelist UX
**Goal**: Admin users can filter records with core built-in filter types and manage filter state clearly in the default Django Admin interface.
**Depends on**: Phase 1
**Requirements**: FILT-01, FILT-03, FILT-04, FILT-05, FILT-06, THEM-01, UX-01, UX-02, UX-03
**Success Criteria** (what must be TRUE):
  1. User can apply dropdown, multi-select, date-range, numeric-range, and boolean-toggle filters from the changelist and see filtered results immediately.
  2. User can always see which filters are active via visible tags/chips in the interface.
  3. User can clear one active filter or reset all filters in one action without manual URL editing.
  4. User can copy/share a filtered changelist URL and another user can open it to the same filter state.
  5. Developer can use all implemented v1 filter types in default Django Admin without custom integration glue.
**Plans**: 3 plans
 
Plans:
- [x] 02-01-PLAN.md — Build tested deterministic URL-state parsing/serialization and query application core for all Phase 2 filter kinds.
- [x] 02-02-PLAN.md — Integrate core built-in filter controls into default Django Admin changelist using additive templates.
- [x] 02-03-PLAN.md — Implement active-filter chips with per-chip clear and global reset-all actions tied to stable URL state.
**UI hint**: yes

### Phase 3: Async Autocomplete & Scale Performance
**Goal**: Admin users can filter very large related datasets through fast async autocomplete backed by server-side search and pagination.
**Depends on**: Phase 1
**Requirements**: FILT-02, PERF-01, PERF-02, PERF-03, PERF-04
**Success Criteria** (what must be TRUE):
  1. User can type into an autocomplete filter and receive matching options from server-side search results.
  2. User can continue loading/browsing more autocomplete matches through paginated option retrieval.
  3. User experiences smooth autocomplete interaction under normal typing because requests are debounced.
  4. User can open pages with high-cardinality filters without long stalls caused by loading full option sets up front.
**Plans**: 3 plans

Plans:
- [ ] 03-01-PLAN.md — Build and test the backend autocomplete contract (validated request parsing, server-side search, deterministic pagination, minimal payload).
- [ ] 03-02-PLAN.md — Expose autocomplete through SmartFilterAdminMixin endpoint wiring with paginated JSON responses and fail-fast guards.
- [ ] 03-03-PLAN.md — Implement admin autocomplete control + debounced client runtime with stale-response protection and lazy option loading.
**UI hint**: yes

### Phase 4: Theme Adapters, Extension Hooks & Docs
**Goal**: Developers can adapt filter rendering for custom admin themes, build custom filter components, and follow official docs to implement core flows.
**Depends on**: Phase 2, Phase 3
**Requirements**: THEM-02, THEM-03, EXT-01, EXT-02, DOC-01
**Success Criteria** (what must be TRUE):
  1. Developer can plug in a theme adapter so filter rendering works in a non-default admin theme without rewriting filter query logic.
  2. Developer can override filter templates through a documented override structure that avoids hardcoded theme assumptions.
  3. Developer can implement a custom filter type by extending the base `FilterComponent` abstraction and registering it in the framework.
  4. Developer can customize filter query behavior and widget behavior through documented pluggable hooks.
  5. Developer can implement all core v1 filter flows by following official copyable documentation examples.
**Plans**: TBD
**UI hint**: yes

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Declarative Filter API Foundation | 1/1 | Complete    | 2026-04-20 |
| 2. Core Built-in Filters & Changelist UX | 3/3 | Complete    | 2026-04-20 |
| 3. Async Autocomplete & Scale Performance | 0/3 | Not started | - |
| 4. Theme Adapters, Extension Hooks & Docs | 0/TBD | Not started | - |

## Requirement Coverage Map

| Requirement | Phase |
|-------------|-------|
| API-01 | Phase 1 |
| API-02 | Phase 1 |
| FILT-01 | Phase 2 |
| FILT-02 | Phase 3 |
| FILT-03 | Phase 2 |
| FILT-04 | Phase 2 |
| FILT-05 | Phase 2 |
| FILT-06 | Phase 2 |
| PERF-01 | Phase 3 |
| PERF-02 | Phase 3 |
| PERF-03 | Phase 3 |
| PERF-04 | Phase 3 |
| THEM-01 | Phase 2 |
| THEM-02 | Phase 4 |
| THEM-03 | Phase 4 |
| UX-01 | Phase 2 |
| UX-02 | Phase 2 |
| UX-03 | Phase 2 |
| EXT-01 | Phase 4 |
| EXT-02 | Phase 4 |
| DOC-01 | Phase 4 |

**Coverage:** 21/21 v1 requirements mapped (100%).

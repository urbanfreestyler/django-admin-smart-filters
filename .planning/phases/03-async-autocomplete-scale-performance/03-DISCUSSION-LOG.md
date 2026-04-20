# Phase 3: Async Autocomplete & Scale Performance - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-20
**Phase:** 03-async-autocomplete-scale-performance
**Areas discussed:** Endpoint contract, search semantics, pagination strategy, debounce behavior, performance guardrails
**Mode:** auto

---

## Endpoint contract

| Option | Description | Selected |
|--------|-------------|----------|
| Server-side autocomplete endpoints | Fetch matching options on demand from backend | ✓ |
| Client-preloaded option lists | Load full options in browser upfront | |
| Hybrid prefetch + fallback | Partial preload plus backend expansion | |

**Auto choice:** Server-side autocomplete endpoints (recommended default in auto mode)
**Notes:** Aligns with high-cardinality and memory constraints.

---

## Search semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Server-side query-driven matching | Search executes on backend per request term | ✓ |
| Browser-side local filtering | Filter previously fetched local option lists | |
| Mixed server/local model | Local first then backend fallback | |

**Auto choice:** Server-side query-driven matching (recommended default in auto mode)
**Notes:** Keeps result relevance and scale behavior consistent for large datasets.

---

## Pagination strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Strict paginated responses | Deterministic page/limit with stable ordering | ✓ |
| Unbounded result batches | Return all matches for each query | |
| Adaptive mixed sizing | Dynamic window sizes by query | |

**Auto choice:** Strict paginated responses (recommended default in auto mode)
**Notes:** Necessary for predictable performance and browseability.

---

## Debounce behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Debounced request dispatch | Coalesce rapid keystrokes and drop stale responses | ✓ |
| Request per keystroke | Fire one backend request for each input change | |
| Manual trigger search | Only query on explicit user action | |

**Auto choice:** Debounced request dispatch (recommended default in auto mode)
**Notes:** Directly satisfies PERF-03 while keeping UX responsive.

---

## Performance guardrails

| Option | Description | Selected |
|--------|-------------|----------|
| Lazy loading with bounded pages | Load options on demand; avoid full list materialization | ✓ |
| Eager loading with caching | Preload large option sets into process/browser cache | |
| Batch sync approach | Periodic bulk sync of options for local querying | |

**Auto choice:** Lazy loading with bounded pages (recommended default in auto mode)
**Notes:** Aligns with PERF-04 and existing project constraints.

---

## OpenCode's Discretion

- Exact debounce interval and default page size values.
- Internal endpoint/helper module boundaries.

## Deferred Ideas

- Non-default theme adapter expansion (Phase 4).
- Extension platform hardening beyond current async scope.

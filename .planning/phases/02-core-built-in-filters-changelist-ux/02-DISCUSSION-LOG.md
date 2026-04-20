# Phase 2: Core Built-in Filters & Changelist UX - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-20
**Phase:** 02-core-built-in-filters-changelist-ux
**Areas discussed:** Built-in filter behavior, Active filter visibility, Clear/reset interactions, URL state model, Default admin integration
**Mode:** auto

---

## Built-in filter behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Implement full Phase 2 filter set | dropdown + multi-select + date-range + numeric-range + boolean-toggle | ✓ |
| Ship partial subset first | Defer one or more filter kinds | |
| Prototype stubs only | UX scaffolding before behavior completeness | |

**Auto choice:** Implement full Phase 2 filter set (recommended default in auto mode)
**Notes:** Aligns directly with Phase 2 requirement mapping and roadmap success criteria.

---

## Active filter visibility

| Option | Description | Selected |
|--------|-------------|----------|
| Chips bar above results | One chip per active filter with human-readable labels | ✓ |
| Sidebar-only indicators | Keep all active-state indicators in existing sidebar area | |
| Summary text block | Single sentence summary without removable chips | |

**Auto choice:** Chips bar above results (recommended default in auto mode)
**Notes:** Best supports UX-01 and clear visibility for multi-filter admin workflows.

---

## Clear/reset interactions

| Option | Description | Selected |
|--------|-------------|----------|
| Per-chip remove + global reset | Clear one criterion or reset all in one click | ✓ |
| Global reset only | Remove all filters, no per-filter actions | |
| Per-filter controls only | No single global reset action | |

**Auto choice:** Per-chip remove + global reset (recommended default in auto mode)
**Notes:** Directly satisfies UX-02 while preserving composed filter sessions.

---

## URL state model

| Option | Description | Selected |
|--------|-------------|----------|
| URL as source of truth | Filter state fully represented in deterministic query params | ✓ |
| Hybrid URL + client state | URL carries some state, JS store carries rest | |
| Client state dominant | URL is secondary serialization only | |

**Auto choice:** URL as source of truth (recommended default in auto mode)
**Notes:** Preserves UX-03 shareability/back-forward consistency and carries Phase 1 deterministic naming forward.

---

## Default admin integration

| Option | Description | Selected |
|--------|-------------|----------|
| Additive default-admin integration | Template/block customizations that preserve native changelist behavior | ✓ |
| Heavy custom admin surface | Replace major changelist structures for full bespoke UX | |
| Separate UI package first | Build detached frontend package before default admin parity | |

**Auto choice:** Additive default-admin integration (recommended default in auto mode)
**Notes:** Aligns with THEM-01 and project constraints around Django-native architecture.

---

## OpenCode's Discretion

- Exact style details for chips, spacing, and control labels.
- Internal file/module partitioning for rendering and state helpers.

## Deferred Ideas

- Async autocomplete interaction/performance specifics (Phase 3).
- Broader theme adapter expansion (Phase 4).

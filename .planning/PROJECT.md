# Django Smart Filters

## What This Is

Django Smart Filters is a reusable filtering framework for Django Admin that improves filter usability for large and complex datasets. It provides pluggable filter components and theme-compatible rendering so teams can use richer filtering UIs without being locked into a specific frontend approach. It is built for Django developers who rely on admin workflows and need better filter discoverability, performance, and customization.

## Core Value

Django admins can quickly find the records they need through fast, extensible, and theme-compatible filters, even at high data scale.

## Requirements

### Validated

- ✓ Provide a declarative API to define admin filters with minimal boilerplate — validated in Phase 1
- ✓ Deliver core built-in changelist filters and UX in default Django Admin (dropdown, multi-select, date range, numeric range, boolean toggle, active chips, clear/reset, URL-persistent state) — validated in Phase 2

### Active

- [ ] Ship production-ready async autocomplete filters for Django Admin
- [ ] Support high-cardinality fields with server-side search and pagination
- [ ] Ensure compatibility with default Django Admin and an adapter pattern for custom themes
- [ ] Document extension points for custom filter types and widgets

### Out of Scope

- Full React/Vue frontend rewrite for admin filters — not needed for MVP and adds unnecessary complexity
- Analytics dashboard functionality — separate problem from admin filtering UX
- Overly abstract plugin meta-framework — prioritize practical extension hooks first

## Context

- Django's built-in `list_filter` works for simple cases but degrades with high-cardinality relations and limited UX controls.
- The project is intended as a library-style enhancement for Django Admin, not a full admin replacement.
- The idea emphasizes a UI-agnostic architecture: backend filter logic, lightweight frontend behavior, and adapter-based theming.
- Initial implementation focus is MVP-level: dropdown + autocomplete, default admin support, and clear docs/examples.

## Constraints

- **Tech stack**: Django-native architecture extending `SimpleListFilter` — must integrate cleanly with standard admin patterns.
- **Performance**: Large datasets must be handled via lazy loading, server-side filtering, and pagination — avoid loading huge choice lists into memory.
- **Compatibility**: No hardcoded assumptions tied to a single admin theme — adapters/templates must support theme variance.
- **Scope**: MVP prioritizes core filter usability and extensibility over broad feature surface.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Build as a Django Admin extension library (not standalone app) | Fits target user workflow and lowers adoption cost | - Pending |
| Prioritize async autocomplete in MVP | High-cardinality filtering is the biggest current pain point | - Pending |
| Use adapter-based theme compatibility | Preserves UI flexibility across default and custom admin themes | - Pending |
| Keep frontend layer lightweight and framework-agnostic | Reduces dependencies and integration friction for Django projects | - Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-20 after Phase 2 completion*

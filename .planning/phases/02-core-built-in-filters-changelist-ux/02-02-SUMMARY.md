---
phase: 02-core-built-in-filters-changelist-ux
plan: 02
subsystem: ui
tags: [django, admin, filters, changelist, templates]
requires:
  - phase: 02-core-built-in-filters-changelist-ux
    provides: deterministic URL/state parsing and queryset dispatch from Plan 02-01
provides:
  - default-admin smart filter integration mixin wired to parse_filter_state/apply_filter_state
  - additive filter control templates for dropdown, multi_select, date_range, numeric_range, and boolean_toggle
  - integration tests validating built-in kind behavior and additive changelist context contracts
affects: [phase-2-active-filter-chips, phase-4-theme-adapters]
tech-stack:
  added: []
  patterns:
    - additive changelist integration via extra_context without replacing Django admin core flow
    - declaration-driven controls contract using normalized FilterSpec values
key-files:
  created:
    - django_smart_filters/admin.py
    - django_smart_filters/templates/admin/django_smart_filters/filter_controls.html
    - django_smart_filters/templates/admin/django_smart_filters/active_filters_bar.html
    - tests/test_admin_filters.py
  modified:
    - django_smart_filters/admin.py
    - django_smart_filters/templates/admin/django_smart_filters/filter_controls.html
    - tests/test_admin_filters.py
key-decisions:
  - "Integrate through a SmartFilterAdminMixin that augments get_queryset/changelist_view rather than replacing Django changelist architecture."
  - "Render control and active-bar templates through additive context contracts to keep theme-compatible and Django-template-native behavior."
  - "Use only declared FilterSpec params via parse_filter_state so unknown GET keys are ignored before queryset mutation."
patterns-established:
  - "Admin integration pattern: get_smart_filter_base_queryset + apply_filter_state for composable queryset behavior."
  - "Template contract pattern: filter_controls list with kind/param/value/options for renderer portability."
requirements-completed: [FILT-01, FILT-03, FILT-04, FILT-05, FILT-06, THEM-01]
duration: 6 min
completed: 2026-04-20
---

# Phase 2 Plan 02: Default-Admin Built-in Filter Controls Summary

**Shipped additive Django Admin changelist integration that renders and applies all five built-in smart filter kinds through normalized declarations and template-native controls.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-20T16:44:52+05:00
- **Completed:** 2026-04-20T16:50:08+05:00
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added `SmartFilterAdminMixin` in `django_smart_filters/admin.py` to bridge declared filters into default admin queryset and changelist context, using `parse_filter_state` and `apply_filter_state`.
- Added additive templates for built-in controls and active-filter bar placeholders:
  - `filter_controls.html` for dropdown/multi-select/date/numeric/boolean controls
  - `active_filters_bar.html` for active-state summary/reset hook
- Added integration coverage in `tests/test_admin_filters.py` for all five filter kinds, class/fluent parity, and additive context contracts.

## task Commits

Each task was committed atomically:

1. **task 1: add default-admin integration bridge for declared filters**
   - `ae1e3fa` (test, RED)
   - `0d5fcac` (feat, GREEN)
2. **task 2: render built-in filter controls with additive changelist templates**
   - `88c04ed` (feat)
   - `ed227e0` (fix, Rule 1 follow-up within task scope)

## Files Created/Modified

- `django_smart_filters/admin.py` - Default-admin integration mixin and additive changelist context/rendering helpers.
- `django_smart_filters/templates/admin/django_smart_filters/filter_controls.html` - Built-in control rendering for five in-scope kinds.
- `django_smart_filters/templates/admin/django_smart_filters/active_filters_bar.html` - Active-filter bar/reset integration hook for subsequent chip work.
- `tests/test_admin_filters.py` - Integration tests for filter application and template context coverage.

## Decisions Made

- Preserved Django admin permission and changelist flow by integrating through `get_queryset`/`changelist_view` overrides only, avoiding admin replacement.
- Kept template rendering framework-agnostic and theme-neutral (Django templates + autoescape, no SPA or theme-specific assumptions).
- Standardized control context fields (`field_name`, `label`, `kind`, `param_name`, `value`, `options`) to support later UI evolution without changing backend state contracts.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Base queryset hook was bypassed in mixin queryset path**
- **Found during:** task 1
- **Issue:** `get_smart_filter_base_queryset` fallback called `super().get_queryset` directly, bypassing test-provided base hook behavior in composed admins.
- **Fix:** Added `super().get_smart_filter_base_queryset` detection path before default fallback, preserving additive composition and expected base queryset sourcing.
- **Files modified:** `django_smart_filters/admin.py`
- **Verification:** `python -m pytest tests/test_admin_filters.py -x`
- **Committed in:** `0d5fcac`

**2. [Rule 1 - Bug] Dropdown/multi-select controls were rendered as free text inputs**
- **Found during:** task 2
- **Issue:** Initial template used text inputs for dropdown and multi-select, violating built-in control semantics required by plan scope.
- **Fix:** Added options context in `admin.py` and switched template rendering to semantic `<select>` / `<select multiple>` controls.
- **Files modified:** `django_smart_filters/admin.py`, `django_smart_filters/templates/admin/django_smart_filters/filter_controls.html`
- **Verification:** `python -m pytest tests/test_admin_filters.py -x`
- **Committed in:** `ed227e0`

---

**Total deviations:** 2 auto-fixed (2 bug)
**Impact on plan:** Both fixes were correctness/semantics fixes within planned scope; no architectural drift and no scope creep.

## Issues Encountered

None.

## Authentication Gates

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Default-admin built-in controls are wired and verified across all five kinds.
- Active-filter bar hook exists; ready for plan 02-03 chip rendering and per-chip clear/reset behavior.

## Self-Check: PASSED

- FOUND: `.planning/phases/02-core-built-in-filters-changelist-ux/02-02-SUMMARY.md`
- FOUND commit: `ae1e3fa`
- FOUND commit: `0d5fcac`
- FOUND commit: `88c04ed`
- FOUND commit: `ed227e0`

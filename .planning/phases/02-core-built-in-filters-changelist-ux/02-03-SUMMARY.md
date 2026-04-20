---
phase: 02-core-built-in-filters-changelist-ux
plan: 03
subsystem: ui
tags: [django-admin, filters, chips, url-state]

# Dependency graph
requires:
  - phase: 02-core-built-in-filters-changelist-ux
    provides: deterministic state parsing/query application and additive changelist control rendering
provides:
  - Active-filter chip view models with deterministic remove/reset URL builders
  - Changelist active-filter bar rendering with per-chip remove actions and reset-all control
  - Tests proving chip labels, remove-one/reset-all behavior, and URL-state persistence
affects: [phase-03-autocomplete, phase-04-theme-adapters, admin-ux]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Deterministic URL canonicalization by sorted query keys/values for filter actions
    - One chip per active criterion derived from parsed FilterSpec-driven state

key-files:
  created:
    - django_smart_filters/chips.py
    - django_smart_filters/templates/admin/django_smart_filters/chip.html
    - tests/test_active_filters_ui.py
  modified:
    - django_smart_filters/admin.py
    - django_smart_filters/templates/admin/django_smart_filters/active_filters_bar.html
    - tests/test_admin_filters.py

key-decisions:
  - "Keep chip ordering deterministic by iterating FilterSpec order and sorting query output in URL builders."
  - "Use additive admin context fields (`active_filter_chips`, `reset_all_url`) instead of replacing changelist behavior."

patterns-established:
  - "URL as source of truth: remove/reset actions are pure GET links over managed params."
  - "Chip rendering remains Django-template-native and autoescaped."

requirements-completed: [UX-01, UX-02, UX-03, THEM-01]

# Metrics
duration: 3 min
completed: 2026-04-20
---

# Phase 2 Plan 3: Active-filter chips with deterministic clear/reset actions Summary

**Active filter chips now render human-readable criteria with deterministic remove-one and reset-all URLs that preserve shareable changelist state.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-20T12:00:32Z
- **Completed:** 2026-04-20T12:03:40Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Added `django_smart_filters/chips.py` with chip view-model generation and deterministic remove/reset URL builders.
- Wired chip and reset context into `SmartFilterAdminMixin` and rendered active chips via reusable `chip.html` partial.
- Added/expanded tests validating label readability, remove-one preservation, reset-all behavior, and stable URL-state reconstruction.

## Task Commits

Each task was committed atomically:

1. **task 1 (TDD RED): chip/URL behavior tests** - `ab5984d` (test)
2. **task 1 (TDD GREEN): chip model + URL builders** - `59e58c7` (feat)
3. **task 2: render active-filter bar + controls** - `6fcf01d` (feat)

## Files Created/Modified
- `django_smart_filters/chips.py` - Active chip generation and deterministic remove/reset query builders.
- `django_smart_filters/templates/admin/django_smart_filters/chip.html` - Reusable escaped chip markup with remove link.
- `django_smart_filters/templates/admin/django_smart_filters/active_filters_bar.html` - Visible chip list + reset-all control.
- `django_smart_filters/admin.py` - Admin context wiring for chips and reset URL plus active bar rendering.
- `tests/test_active_filters_ui.py` - New tests for label format, remove-one/reset-all flows, deterministic URLs.
- `tests/test_admin_filters.py` - Integration checks for chip context and rendered active bar controls.

## Decisions Made
- Kept chip data generation independent in `chips.py` so rendering remains template/theme adaptable.
- Canonicalized generated querystrings for deterministic URL output and reproducible chip-state links.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Removed ad-hoc Django settings initialization from new test module**
- **Found during:** task 2 verification
- **Issue:** `tests/test_active_filters_ui.py` configured Django settings early, which prevented admin template directories from being available in combined test runs.
- **Fix:** Removed local `settings.configure(...)` from the new test module to preserve suite-level test settings behavior.
- **Files modified:** `tests/test_active_filters_ui.py`
- **Verification:** `PYTHONPATH=. pytest tests/test_active_filters_ui.py tests/test_admin_filters.py -x` passes.
- **Committed in:** `6fcf01d`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Fix was required for reliable verification and did not expand scope.

## Issues Encountered
- Local pytest execution required `PYTHONPATH=.` so package imports resolve in this workspace environment.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Active filter visibility and clear/reset UX are complete on default admin integration.
- Ready for downstream async/filter-scale and theme-adapter phases that consume stable chip/action contracts.

## Self-Check: PASSED

- FOUND: `.planning/phases/02-core-built-in-filters-changelist-ux/02-03-SUMMARY.md`
- FOUND commits: `ab5984d`, `59e58c7`, `6fcf01d`

---
*Phase: 02-core-built-in-filters-changelist-ux*
*Completed: 2026-04-20*

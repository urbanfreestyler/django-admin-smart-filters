---
status: partial
phase: 02-core-built-in-filters-changelist-ux
source: [02-VERIFICATION.md]
started: 2026-04-20T12:40:00Z
updated: 2026-04-20T12:40:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Render changelist with all five filter kinds in real Django Admin UI
expected: Dropdown, multi-select, date-range, numeric-range, and boolean-toggle controls are visible, labeled clearly, and usable without template breakage.
result: [pending]

### 2. Use per-chip remove action and Reset all filters action from browser
expected: Removing one chip clears only that criterion, reset clears all managed filters, and unrelated params (e.g., pagination/sort) are preserved appropriately.
result: [pending]

### 3. Share a filtered changelist URL between sessions/users
expected: Opening the shared URL reproduces the same active chips and filtered result set.
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps

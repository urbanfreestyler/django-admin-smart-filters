---
phase: 04-theme-adapters-extension-hooks-docs
plan: 01
subsystem: extension-contracts
tags: [extensions, registry, hooks, declarations]
requirements_completed: [EXT-01, EXT-02]
---

# Phase 4 Plan 1 Summary

Implemented extension contracts and registry wiring in:
- `django_smart_filters/contracts.py`
- `django_smart_filters/registry.py`
- `django_smart_filters/declarations.py`
- `django_smart_filters/builder.py`
- `django_smart_filters/__init__.py`
- `tests/test_extension_registry.py`
- `tests/test_declarations.py`

## Delivered
- Added `FilterComponent` base contract and `FilterSpec.component_key` extension metadata.
- Added component registry API:
  - `register_filter_component(...)`
  - `resolve_filter_component(...)`
  - `clear_filter_component_registry(...)`
- Added fail-fast component-key resolution in declaration normalization with actionable errors for unknown keys.
- Added fluent hook extension methods:
  - `with_query_hook(...)`
  - `with_widget_hook(...)`
  - `with_component(...)`
- Exported extension primitives from package root for stable public usage.

## Verification
- `python -m pytest tests/test_extension_registry.py tests/test_declarations.py -x` ✅

## Notes
- Extension behavior remains additive: existing declarations continue to normalize unchanged when no component key/hooks are provided.

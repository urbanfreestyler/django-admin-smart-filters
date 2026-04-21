# Codebase Concerns

**Analysis Date:** 2026-04-21

## Tech Debt

**Extension hooks are defined but not executed in UI rendering path:**
- Issue: `widget_hook` is part of normalized declarations/contracts but control rendering does not invoke it, so extension points exist in API but are not applied at runtime.
- Files: `django_smart_filters/contracts.py`, `django_smart_filters/declarations.py`, `django_smart_filters/builder.py`, `django_smart_filters/admin.py`
- Impact: Integrators can configure widget hooks and see no effect, creating contract drift between docs/API and behavior.
- Fix approach: Apply `spec.widget_hook` inside `SmartFilterAdminMixin._build_filter_controls()` before appending each control, and add focused tests in `tests/test_admin_filters.py`.

**Component registry currently changes filter kind only:**
- Issue: `component_key` resolves to a class and only reads `filter_kind`; no additional component behavior is invoked during query, state, or rendering.
- Files: `django_smart_filters/registry.py`, `django_smart_filters/declarations.py`, `django_smart_filters/admin.py`, `docs/extension_hooks.md`
- Impact: Custom components appear supported but currently provide limited runtime extensibility.
- Fix approach: Define and enforce a richer component contract (render/query hooks or control factory), then call it in `django_smart_filters/admin.py`.

## Known Bugs

**Autocomplete requests from UI do not include active filter context:**
- Symptoms: Autocomplete endpoint can compose with existing filters when params are present, but browser requests send only `field/query/page/limit` so server-side scoped filtering is skipped.
- Files: `django_smart_filters/static/django_smart_filters/autocomplete.js`, `django_smart_filters/admin.py`, `tests/test_autocomplete_admin_endpoint.py`
- Trigger: Use an admin changelist with one active filter and type in autocomplete; JS request omits active query params.
- Workaround: Build endpoint URLs that include existing query params, or patch JS to append current URL/search params to each autocomplete request.

**Autocomplete selected value label degrades to raw value on reload:**
- Symptoms: Selected autocomplete text can show PK/string value instead of human label after page reload.
- Files: `django_smart_filters/admin.py`, `django_smart_filters/templates/admin/django_smart_filters/autocomplete_control.html`
- Trigger: Load changelist with pre-existing autocomplete param; `selected_label` is set from raw value in `_build_filter_controls()`.
- Workaround: Resolve and inject display label server-side for selected value, or fetch label on control init in `autocomplete.js`.

## Security Considerations

**Executable documentation snippets in tests:**
- Risk: `exec()` runs Python snippets extracted from docs; malicious snippet changes could execute arbitrary code in CI/test environments.
- Files: `tests/test_docs_examples.py`, `docs/extension_hooks.md`, `docs/theme_adapters.md`
- Current mitigation: Snippets are sourced from in-repo docs and executed in controlled test namespace.
- Recommendations: Restrict snippet execution to an allowlisted AST subset or run in sandboxed subprocess for docs validation.

## Performance Bottlenecks

**Autocomplete search uses broad `icontains` scan without explicit index strategy:**
- Problem: `field__icontains` can become expensive on large datasets.
- Files: `django_smart_filters/autocomplete.py`
- Cause: Search applies `queryset.filter(**{f"{field_name}__icontains": query})` and sorts by field + PK; large cardinality can drive full/large scans.
- Improvement path: Add documented indexed-search guidance (trigram/functional indexes per DB), configurable lookup strategy, and optional custom query hook for autocomplete.

**Repeated declaration normalization per request path:**
- Problem: Specs are normalized repeatedly in `get_queryset`, `changelist_view`, and autocomplete endpoint.
- Files: `django_smart_filters/admin.py`, `django_smart_filters/declarations.py`
- Cause: `get_smart_filter_specs()` recomputes from declarations each call.
- Improvement path: Cache normalized specs per admin class instance/request lifecycle and invalidate only when declarations change.

## Fragile Areas

**Global mutable component registry state:**
- Files: `django_smart_filters/registry.py`, `tests/test_extension_registry.py`
- Why fragile: Registry is process-global and mutable; tests must manually clear state, and runtime order of registrations can affect behavior.
- Safe modification: Keep startup-only registration discipline and isolate tests with explicit `clear_filter_component_registry()` in setup/teardown.
- Test coverage: Registration and duplicate handling are tested in `tests/test_extension_registry.py`, but concurrent registration semantics are not tested.

**State parsing/normalization split across multiple modules:**
- Files: `django_smart_filters/state.py`, `django_smart_filters/query.py`, `django_smart_filters/admin.py`
- Why fragile: Similar coercion rules are implemented in multiple places (e.g., boolean/range handling), increasing risk of drift.
- Safe modification: Centralize normalization primitives and ensure both parse and apply paths share the same conversion functions.
- Test coverage: Good unit coverage exists in `tests/test_state.py` and `tests/test_query.py`, but cross-module invariants are not enforced by a single contract test.

## Scaling Limits

**Autocomplete endpoint request amplification under rapid typing:**
- Current capacity: Debounce is fixed at 250ms client-side with one request per debounce cycle.
- Limit: Large admin user concurrency can generate high endpoint traffic because no server-side caching/throttling is implemented.
- Scaling path: Add per-user throttling, short-lived result caching for repeated query prefixes, and configurable debounce in `django_smart_filters/static/django_smart_filters/autocomplete.js` and endpoint policy in `django_smart_filters/admin.py`.

## Dependencies at Risk

**No dependency risk hotspots detected in current repository snapshot:**
- Risk: Not detected.
- Impact: Not applicable.
- Migration plan: Not applicable.

## Missing Critical Features

**Widget hook behavior is not wired into rendered controls:**
- Problem: Public extension contract advertises widget customization, but runtime control building does not invoke widget hooks.
- Blocks: Theme/component authors cannot reliably customize control context through documented extension path.

## Test Coverage Gaps

**No test asserts widget_hook affects rendered control context:**
- What's not tested: End-to-end widget hook application from declaration → control context → template output.
- Files: `tests/test_extension_registry.py`, `tests/test_admin_filters.py`, `django_smart_filters/admin.py`
- Risk: Regressions or missing implementation can ship while tests still pass.
- Priority: High

**No browser-level integration tests for autocomplete network behavior:**
- What's not tested: Real DOM/network behavior that includes existing URL filter params in autocomplete requests.
- Files: `tests/test_autocomplete_ui.py`, `django_smart_filters/static/django_smart_filters/autocomplete.js`
- Risk: Request composition issues can pass unit tests but fail in production UI flows.
- Priority: Medium

---

*Concerns audit: 2026-04-21*

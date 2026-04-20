# Codebase Concerns

**Analysis Date:** 2026-04-20

## Tech Debt

**Autocomplete contract is coupled to `pk` and same-field labels:**
- Issue: `search_autocomplete_options()` always emits `{"id": pk, "value": pk, "label": field_name}` while `apply_filter_value()` applies `field_name=<selected value>`. This coupling assumes selected values should always be `pk`, but base filtering for `autocomplete` currently uses plain field equality.
- Files: `django_smart_filters/autocomplete.py`, `django_smart_filters/query.py`, `django_smart_filters/admin.py`
- Impact: Autocomplete can produce mismatched filtering semantics for non-FK text fields, and can produce low-quality labels for relational fields where `field_name` is not user-facing text.
- Fix approach: Introduce explicit autocomplete spec metadata for `search_lookup`, `value_field`, and `label_field`; use those for both endpoint payload and queryset application so selected value and applied filter lookup are aligned.

**Repeated normalization constants and helpers across modules:**
- Issue: Boolean token sets and range parsing helpers are duplicated across state parsing and query application.
- Files: `django_smart_filters/state.py`, `django_smart_filters/query.py`
- Impact: Behavior drift risk when adding/editing accepted boolean/range formats in one module but not the other.
- Fix approach: Centralize shared parsing/normalization utilities in one module and import from both parser and query layers.

**No packaging/install metadata committed:**
- Issue: Repository root does not contain package metadata (`pyproject.toml`, `setup.cfg`, `setup.py`) or dependency lock/constraints files.
- Files: project root (`C:\Projects\django-admin-smart-filters`)
- Impact: Installation, publishing, and reproducible local/CI setup are fragile and rely on implicit environment state.
- Fix approach: Add `pyproject.toml` with build-system and project metadata, define test/dev extras, and document canonical setup commands.

## Known Bugs

**`pytest` command fails import collection unless run as module:**
- Symptoms: `pytest -q` fails with `ModuleNotFoundError: No module named 'django_smart_filters'` during collection, while `python -m pytest -q` succeeds.
- Files: project root invocation context; test imports in `tests/test_admin_filters.py`, `tests/test_autocomplete.py`, `tests/test_state.py` (and other `tests/*.py`)
- Trigger: Running tests using the `pytest` console script in the current Windows environment.
- Workaround: Run tests with `python -m pytest` until path configuration is standardized via packaging/test config.

## Security Considerations

**Autocomplete endpoint has no explicit request throttling:**
- Risk: Authenticated admin users can generate high request volume against `smart_filter_autocomplete_view()`.
- Files: `django_smart_filters/admin.py`, `django_smart_filters/static/django_smart_filters/autocomplete.js`
- Current mitigation: Debounce in client runtime (`DEBOUNCE_MS = 250`) and minimum query length (`MIN_AUTOCOMPLETE_QUERY_LENGTH = 2`).
- Recommendations: Add optional server-side rate limiting/throttling hooks for autocomplete endpoint usage in high-traffic admin deployments.

**Client silently swallows fetch/response errors:**
- Risk: Endpoint failures are suppressed client-side, reducing operator visibility and increasing time-to-diagnosis.
- Files: `django_smart_filters/static/django_smart_filters/autocomplete.js`
- Current mitigation: Stale-response guard prevents outdated responses from being applied.
- Recommendations: Surface non-2xx/network errors in UI and optionally emit structured console diagnostics for admin debugging.

## Performance Bottlenecks

**Autocomplete query uses `icontains` + ordered pagination on each request:**
- Problem: `field__icontains` searches with deterministic `order_by(field, pk)` can become expensive at scale without proper DB indexing/search strategy.
- Files: `django_smart_filters/autocomplete.py`
- Cause: Broad substring search plus sorting for each query page.
- Improvement path: Provide pluggable search strategy (`istartswith`, trigram/full-text where available), enforce indexed fields, and add optional hard query timeout/limit policies.

**Spec normalization recomputed repeatedly per request path:**
- Problem: `normalize_declarations()` is called from multiple request lifecycle methods (`get_queryset`, `changelist_view`, autocomplete view).
- Files: `django_smart_filters/admin.py`, `django_smart_filters/declarations.py`
- Cause: No per-request caching of normalized specs/state.
- Improvement path: Cache normalized specs/state on `request` during the request lifecycle to avoid repeated normalization and validation work.

## Fragile Areas

**Admin mixin combines endpoint, rendering, control-building, and query-state composition in one class:**
- Files: `django_smart_filters/admin.py`
- Why fragile: `SmartFilterAdminMixin` currently owns URL wiring, endpoint behavior, state parsing, control view-model generation, and template rendering, increasing change blast radius.
- Safe modification: Extract endpoint handler, control-building, and rendering into dedicated helpers with narrow unit tests before adding new filter kinds.
- Test coverage: Behavior tests exist in `tests/test_admin_filters.py` and `tests/test_autocomplete_admin_endpoint.py`, but mutation-heavy refactors remain high-risk due to centralized class responsibilities.

**Template/JS contract depends on stringly-typed data attributes:**
- Files: `django_smart_filters/templates/admin/django_smart_filters/autocomplete_control.html`, `django_smart_filters/static/django_smart_filters/autocomplete.js`
- Why fragile: Runtime relies on exact CSS class and `data-*` keys; small template changes can silently break JS behavior.
- Safe modification: Keep a versioned runtime contract and add assertion tests that validate required attributes/classes are present in rendered HTML.
- Test coverage: Static-string assertions in `tests/test_autocomplete_ui.py` cover key markers but do not run browser-level interaction tests.

## Scaling Limits

**Autocomplete endpoint scales with live query load and lacks backend guardrails:**
- Current capacity: Not measured in repository; no benchmark artifacts detected.
- Limit: High concurrent admin typing sessions can increase DB query pressure because each page/search call hits DB-style filtering.
- Scaling path: Add server-side throttling, configurable minimum term length/page size, and benchmark-based limits for endpoint throughput.

## Dependencies at Risk

**Django runtime dependency is implicit, not pinned in project metadata:**
- Risk: Environment drift can change admin/template behavior and test outcomes unexpectedly.
- Impact: Reproducibility and compatibility checks are harder across machines/CI.
- Migration plan: Commit `pyproject.toml` with explicit Django version ranges and add CI matrix constraints.

## Missing Critical Features

**Theme adapter layer is not implemented in runtime code:**
- Problem: Project roadmap and docs call for theme adapters, but code paths currently target default admin templates only.
- Blocks: Confident support for non-default admin themes and controlled extension points for theme-specific rendering.

**Published extension contract docs for custom filter components are not present in code/docs:**
- Problem: Runtime exposes `query_hook`/`widget_hook`, but there is no complete developer guide for custom filter type implementation flow.
- Blocks: Third-party extension development and predictable adoption for custom filter modules.

## Test Coverage Gaps

**No end-to-end browser tests for autocomplete interaction path:**
- What's not tested: Real DOM event behavior, async fetch timing, and stale response handling in a browser environment.
- Files: runtime in `django_smart_filters/static/django_smart_filters/autocomplete.js`; related tests in `tests/test_autocomplete_ui.py`
- Risk: UI regressions can pass unit/static tests but fail in real admin pages.
- Priority: High

**Autocomplete selection-to-query application semantics are not validated:**
- What's not tested: Whether selected autocomplete `value` maps correctly to queryset filtering for realistic Django model fields/relations.
- Files: `django_smart_filters/autocomplete.py`, `django_smart_filters/query.py`, `django_smart_filters/admin.py`, tests in `tests/test_autocomplete_admin_endpoint.py`
- Risk: Users can select visible options yet get incorrect or empty filtered results.
- Priority: High

**No performance/benchmark tests for high-cardinality autocomplete:**
- What's not tested: Response time and query efficiency under large datasets and concurrent requests.
- Files: `django_smart_filters/autocomplete.py`, `django_smart_filters/admin.py`
- Risk: Performance regressions are detected late in production-like usage.
- Priority: Medium

---

*Concerns audit: 2026-04-20*

# Project Research Summary

**Project:** django-admin-enhanced-filters
**Domain:** Django admin filtering framework library (async autocomplete + theme adapters)
**Researched:** 2026-04-20
**Confidence:** HIGH

## Executive Summary

This project is a Django-admin-native filtering library, not a replacement admin UI. The research converges on a backend-first architecture that extends `ModelAdmin`/`list_filter` with a declarative filter spec system, then layers progressive enhancement (async autocomplete, compact widgets) on top of server-rendered admin pages. Experts in this space avoid SPA rewrites and instead use Django’s existing extension seams: `SimpleListFilter`, `get_urls()`, admin template overrides, and admin-compatible JS.

The recommended approach is to ship a strong v1 core: declarative list-filter-compatible API, dropdown + async autocomplete + range filters, permission-safe server-side search/pagination, and a stable UI contract with a default Django admin adapter. Theme support should be adapter-driven (default admin first, then optional Jazzmin/Grappelli adapters), with query logic isolated from presentation to avoid long-term coupling.

The main risks are permission leaks in autocomplete endpoints, performance collapse on high-cardinality datasets (unindexed `icontains`, paginator `count()`, facet query explosion), and brittle theme/JS coupling. Mitigation is clear: centralized auth/query services, strict parameter schema validation, benchmark budgets, opt-in facets, immutable request-time configuration patterns, and a compatibility QA matrix (light/dark + at least one non-default theme).

## Key Findings

### Recommended Stack

Research strongly supports a modern but conservative baseline: Django 5.2 LTS as minimum contract, validated against Django 6.0.x in CI, running on Python 3.12–3.14. Runtime dependencies should stay minimal (`Django`, `asgiref`), while quality/tooling is handled with `pytest` + `pytest-django`, `ruff`, `mypy` + `django-stubs`, `pre-commit`, and `hatchling` packaging.

This stack minimizes breakage risk for an OSS library and keeps focus on admin integration quality instead of framework churn.

**Core technologies:**
- **Python 3.12+**: runtime baseline — aligns with Django 6.0 support and modern typing/performance.
- **Django 5.2 LTS (+ test 6.0.x)**: admin extension surface — stable support window plus forward-compat confidence.
- **Django admin built-ins (Select2/templates/hooks)**: async UX foundation — reuse official admin behavior instead of duplicating with SPA/external widget stacks.
- **asgiref 3.11+**: sync/async boundary safety — supports safe async endpoint integration.

### Expected Features

The MVP is clear and focused: adoption requires drop-in `list_filter` compatibility and safe/high-performance handling of large related datasets. Differentiation comes from a unified API and theme adapter architecture, not from replacing admin itself.

**Must have (table stakes):**
- Declarative `list_filter`-compatible API.
- Async autocomplete for FK/M2M with server-side search/pagination.
- Permission-safe option loading and stable querystring state.
- Dropdown/compact filters and date/numeric range filters.
- Default admin renderer plus explicit adapter contract.

**Should have (competitive):**
- Unified builders (`dropdown`, `autocomplete`, `range`) under one API style.
- Theme adapter layer (default + optional custom themes).
- Performance guardrails (debounce, limits, query hints, timeout/error states).
- Extension SDK and optional facet/count controls with budgets.
- Saved filter presets (querystring-based) after core validation.

**Defer (v2+):**
- Advanced query language / nested boolean “mega builder”.
- Cross-model compound filtering workflows.

### Architecture Approach

Architecture research recommends strict separation of concerns: `AdminIntegration` (ModelAdmin seam), `FilterRegistry` + `FilterEngine` (query semantics), `UIContract` + `ThemeAdapter` (presentation boundary), and `AsyncEndpoint` + lightweight `FrontendController` (high-cardinality option delivery). The URL querystring remains the single source of truth for filter state. Build order should be dependency-driven: core filter domain first, then admin wiring, then UI contract/default adapter, then async autocomplete, then additional themes and performance hardening.

**Major components:**
1. **Admin integration layer** — bridges declarative filter specs into Django admin lifecycle (`list_filter`, `get_urls`, media/hooks).
2. **Filter domain engine** — validates params and compiles filter specs into deterministic ORM/Q operations.
3. **Presentation contract + theme adapters** — renders consistent filter UI across default admin and optional skins.
4. **Async options endpoint** — permission-scoped, paginated option search for large relations.

### Critical Pitfalls

1. **Misusing `autocomplete_fields` as changelist filter solution** — create a dedicated changelist filter abstraction early.
2. **Missing auth/search boundaries in async endpoints** — require searchable config and centralize request-scoped permission filtering.
3. **Unindexed `icontains` on large datasets** — constrain search fields, add custom search hooks, and enforce latency budgets.
4. **Facet/count and paginator query explosions** — keep facets opt-in, add per-filter controls, and provide large-table paginator strategies.
5. **Theme/JS coupling and admin integration drift** — rely on admin conventions (`django.jQuery`, `block.super`), adapter hooks, and compatibility QA matrix.

## Implications for Roadmap

Based on combined research, the roadmap should follow a dependency-first sequence that protects API stability and reduces rework.

### Phase 1: Core Filter Domain & API Contract
**Rationale:** Everything else depends on a stable filter abstraction and parameter/query contract.
**Delivers:** Declarative filter specs, registry, param schema validation, compiler/engine, conflict validation (widget precedence), core tests.
**Addresses:** Declarative API table stake; foundation for dropdown/autocomplete/range.
**Avoids:** `autocomplete_fields` abstraction mistakes, ad-hoc params, mutable hook drift.

### Phase 2: Admin Integration + Secure Async Data Plane
**Rationale:** Validate real Django admin lifecycle integration and permission-safe data retrieval early.
**Delivers:** `ModelAdmin` mixin integration, URL hooks, autocomplete JSON endpoint, role-based auth tests, initial frontend controller with debounced requests.
**Addresses:** Async autocomplete + server-side search/pagination + permission-safe filtering.
**Avoids:** auth leaks, endpoint inconsistency, JS/admin convention breakage.

### Phase 3: UI Contract, Default Adapter, and v1 UX Completeness
**Rationale:** Stabilize rendering boundary before broad theme expansion.
**Delivers:** UI contract, default admin templates, dropdown + range widgets, querystring persistence guarantees, adapter extension example.
**Addresses:** Dropdown/range table stakes and default admin renderer requirement.
**Avoids:** theme-coupled query logic, brittle CSS/selectors, missing loading/empty/error states.

### Phase 4: Performance Guardrails & Optional Facets
**Rationale:** After end-to-end behavior exists, optimize where real bottlenecks emerge.
**Delivers:** Benchmark fixtures, indexed search guidance, optional paginator strategy, facet/count budget toggles, query-count regression tests.
**Addresses:** Performance differentiator and P2 facet controls.
**Avoids:** unindexed search collapse, `count()` bottlenecks, facet query explosion.

### Phase 5: Theme Expansion, Compatibility QA, and v1.x Enhancements
**Rationale:** Extend safely once core contract and perf profile are stable.
**Delivers:** Additional adapters (e.g., Jazzmin/Grappelli optional), compatibility matrix tests, saved presets, extension SDK hardening.
**Addresses:** Differentiators and post-validation features.
**Avoids:** adapter lock-in, recurring theme regressions, unstable extension surface.

### Phase Ordering Rationale

- Core query semantics and contract precede admin/UI layers to avoid repeated rewrites.
- Security and async endpoint correctness come before richer UX/theming because leaks/perf failures are high severity.
- Theme breadth is intentionally delayed until default-admin parity and contract stability are proven.
- Performance hardening is inserted before broad adapter rollout to prevent scaling surprises across consumers.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4:** DB-specific optimization strategy (index types, paginator alternatives, facet query budgeting across Postgres/MySQL/SQLite).
- **Phase 5:** Theme adapter nuances for third-party skins and long-term compatibility policy.
- **Phase 5:** Preset governance model (team/user scope, permissions, migration strategy) if included beyond simple querystring snapshots.

Phases with standard patterns (can usually skip extra research):
- **Phase 1:** Declarative filter specs, request param validation, and ORM compiler patterns are well-established.
- **Phase 2:** Django admin integration seams (`list_filter`, `get_urls`, media) and permission testing patterns are well documented.
- **Phase 3 (default adapter only):** Server-rendered templates + progressive enhancement follows standard Django admin conventions.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Primarily validated against official Django/Python compatibility docs and current package metadata. |
| Features | MEDIUM | Table stakes are clear, but competitor landscape has mixed maintenance quality and varying release cadence. |
| Architecture | HIGH | Strong convergence with official admin extension points and well-known separation-of-concerns patterns. |
| Pitfalls | HIGH | Risks are directly documented in Django admin behavior and repeatedly observed in comparable packages. |

**Overall confidence:** HIGH (with feature-prioritization uncertainty concentrated in post-MVP differentiators).

### Gaps to Address

- **Theme adapter contract depth:** Define minimum stable adapter API and versioning policy before adding multiple third-party theme adapters.
- **Performance SLO baselines:** Establish explicit P95 latency/query-count targets and realistic fixture sizes during planning.
- **Facet defaults:** Decide default OFF/ON policy and per-filter thresholds based on benchmark evidence.
- **Preset scope/security:** Confirm whether presets are user-only, team-shared, or both, and map to permission model.
- **Forward-compat cadence:** Define policy for Django minor/major compatibility (especially upcoming 6.1+) and deprecation windows.

## Sources

### Primary (HIGH confidence)
- Django official docs (admin/filter APIs, JS customization, async, template overrides):  
  https://docs.djangoproject.com/en/6.0/ref/contrib/admin/  
  https://docs.djangoproject.com/en/6.0/ref/contrib/admin/filters/  
  https://docs.djangoproject.com/en/6.0/ref/contrib/admin/javascript/  
  https://docs.djangoproject.com/en/6.0/topics/async/  
  https://docs.djangoproject.com/en/stable/howto/overriding-templates/
- Django release/support and Python compatibility references:  
  https://www.djangoproject.com/download/  
  https://docs.djangoproject.com/en/6.0/faq/install/#what-python-version-can-i-use-with-django
- Packaging and PyPI metadata references:  
  https://packaging.python.org/en/latest/guides/writing-pyproject-toml/  
  https://pypi.org/pypi/Django/json  
  https://pypi.org/pypi/asgiref/json  
  https://pypi.org/pypi/pytest/json  
  https://pypi.org/pypi/pytest-django/json  
  https://pypi.org/pypi/ruff/json  
  https://pypi.org/pypi/mypy/json  
  https://pypi.org/pypi/django-stubs/json

### Secondary (MEDIUM confidence)
- Competitive package ecosystem signals:  
  https://github.com/silentsokolov/django-admin-rangefilter  
  https://github.com/farhan0581/django-admin-autocomplete-filter  
  https://github.com/thomst/django-more-admin-filters  
  https://github.com/saxix/django-adminfilters  
  https://pypi.org/project/django-adminfilters/  
  https://github.com/ivelum/djangoql
- Theme ecosystem references:  
  https://django-jazzmin.readthedocs.io/  
  https://django-grappelli.readthedocs.io/en/latest/

### Tertiary (LOW confidence)
- Older/stale package activity used as directional UX evidence (not implementation authority):  
  https://github.com/mrts/django-admin-list-filter-dropdown
- Select2 troubleshooting guidance (external but relevant to widget behavior):  
  https://select2.org/troubleshooting/common-problems

---
*Research completed: 2026-04-20*
*Ready for roadmap: yes*

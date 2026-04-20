# Pitfalls Research

**Domain:** Django admin filtering library (async autocomplete + theme compatibility)
**Researched:** 2026-04-20
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Treating `autocomplete_fields` as a drop-in for changelist filters

**What goes wrong:**
Teams assume Django’s built-in `ModelAdmin.autocomplete_fields` solves async filtering in `list_filter`. It does not map directly to custom sidebar filters, so implementation gets hacked late and API design collapses.

**Why it happens:**
`autocomplete_fields` is well-documented and convenient, but it targets relation form widgets, while changelist filters are a separate API (`list_filter`, `SimpleListFilter`, `FieldListFilter`).

**How to avoid:**
- Define your own filter abstraction explicitly for changelist context (parameter parsing + queryset application + widget rendering).
- Keep a clear contract: filter UI component ↔ query param schema ↔ queryset transformer.
- Document that form autocomplete and changelist filter autocomplete are distinct integration points.

**Warning signs:**
- Team tries to wire `autocomplete_fields` into `list_filter` directly.
- Filter prototype works in change form but not in changelist sidebar.
- Query params become ad-hoc and inconsistent between filters.

**Phase to address:**
Phase 1 (API/design foundation).

---

### Pitfall 2: Missing `search_fields` and permission boundaries for autocomplete endpoints

**What goes wrong:**
Autocomplete fails, returns poor results, or leaks object visibility across admin users.

**Why it happens:**
Django autocomplete requires `search_fields` on the related admin and enforces permission checks. Custom filter endpoints often skip equivalent checks.

**How to avoid:**
- Require searchable field configuration in your filter declaration.
- Centralize request-scoped queryset authorization (`request.user` + model/object visibility).
- Add tests for staff roles with different permissions.

**Warning signs:**
- 403/empty results for valid users.
- Users can discover object labels they should not see.
- Search behavior differs per model with no explicit config.

**Phase to address:**
Phase 2 (server query + auth layer).

---

### Pitfall 3: Unindexed `icontains` search on high-cardinality fields

**What goes wrong:**
Autocomplete and filter search become slow under realistic data volume.

**Why it happens:**
Django admin default search behavior uses `icontains` across `search_fields`; when fields aren’t indexed, query cost explodes.

**How to avoid:**
- Restrict default search fields to indexed columns.
- Support custom search backends (`get_search_results()`-style hook) for large tables.
- Add performance budgets (e.g., P95 response target for autocomplete).

**Warning signs:**
- Query plans show sequential scans on large tables.
- Latency spikes once dataset crosses early thresholds.
- DB CPU rises during typeahead usage.

**Phase to address:**
Phase 2 (query engine) and Phase 4 (scale hardening).

---

### Pitfall 4: Expensive ordering + paginator `count()` on large datasets

**What goes wrong:**
Every filter interaction triggers expensive sort/count operations, creating multi-second admin delays.

**Why it happens:**
Admin ordering can force costly sorts, and default paginator performs `count()`; both become painful at scale.

**How to avoid:**
- Use predictable indexed ordering defaults.
- Provide optional paginator strategy for large tables.
- Add benchmark fixtures with realistic row counts.

**Warning signs:**
- Slow queries include sort on non-indexed columns.
- `COUNT(*)` dominates request time.
- “Works in dev, unusable in production” reports from ops users.

**Phase to address:**
Phase 4 (performance/scalability).

---

### Pitfall 5: Query explosion from facets and filter choice generation

**What goes wrong:**
Enabling richer filter UX (counts/facets/many related choices) unexpectedly multiplies DB queries.

**Why it happens:**
Django notes that facet counts increase queries with number of filters. Custom filter libraries often add extra count/metadata queries per control.

**How to avoid:**
- Keep facets opt-in, not always-on.
- Cache cheap metadata per request when possible.
- Expose per-filter toggles for count badges.

**Warning signs:**
- Query count scales linearly with number of visible filters.
- Changelist loads are much slower when facets are enabled.
- APM traces show many small repetitive count queries.

**Phase to address:**
Phase 3 (UX features) and Phase 4 (perf guardrails).

---

### Pitfall 6: Widget conflict matrix ignored (`formfield_overrides` vs relation widgets)

**What goes wrong:**
Custom widgets silently fail or render inconsistently when fields are also in `raw_id_fields`, `radio_fields`, or `autocomplete_fields`.

**Why it happens:**
Django relation widget selection has explicit precedence rules; many libraries ignore those rules and assume widget override always wins.

**How to avoid:**
- Validate configuration conflicts at startup.
- Emit explicit errors when incompatible options are combined.
- Document precedence in extension API.

**Warning signs:**
- Widget appears in one admin screen and not another.
- CSS/JS loads but control type remains default.
- Support issues around “override not applied.”

**Phase to address:**
Phase 1 (config model) and Phase 2 (adapter implementation).

---

### Pitfall 7: JavaScript integration that bypasses admin conventions

**What goes wrong:**
Autocomplete/filter JS works in isolation but breaks in admin pages, especially with third-party admin themes.

**Why it happens:**
Django admin uses namespaced `django.jQuery`; widgets depending on jQuery need `admin/js/jquery.init.js`; template overrides that omit `{{ block.super }}` break core admin scripts.

**How to avoid:**
- Provide a single asset-loading strategy compatible with admin media API.
- Use `django.jQuery` by default in admin context.
- In docs/examples, always include `{{ block.super }}` in overridden admin blocks.

**Warning signs:**
- “`$` is undefined” or duplicate jQuery conflicts.
- Filter UI disappears only in customized admin templates.
- Regressions after enabling a custom admin theme/app.

**Phase to address:**
Phase 2 (frontend behavior layer) and Phase 5 (compatibility QA).

---

### Pitfall 8: Theme coupling via hardcoded CSS/selectors

**What goes wrong:**
Controls look correct in stock admin but break in dark mode or in theme adapters (spacing, contrast, dropdown alignment).

**Why it happens:**
Library CSS is authored against one DOM/CSS assumption instead of Django’s variable-based theming and template extension points.

**How to avoid:**
- Build styling tokens around Django admin CSS variables.
- Test both light/dark mode and at least one non-default admin skin.
- Ship adapter hooks for class names/templates instead of hardcoding selectors.

**Warning signs:**
- Low contrast in dark mode.
- Dropdown widths/positions wrong in themed admins.
- Frequent CSS hotfixes per consumer project.

**Phase to address:**
Phase 3 (theming/adapters) and Phase 5 (cross-theme verification).

---

### Pitfall 9: Shared mutable state in dynamic admin hooks

**What goes wrong:**
Filter behavior changes across requests/users (duplicate fields, drifting config, nondeterministic UI).

**Why it happens:**
Code mutates class-level lists/tuples in request-time hooks (`get_*` methods), causing cumulative side effects.

**How to avoid:**
- Treat class attributes as immutable.
- Return copied structures from dynamic hooks.
- Add regression tests for repeated requests with mixed user roles.

**Warning signs:**
- Duplicate filters/options appear after several requests.
- Behavior differs between first and subsequent page loads.
- Issues only reproducible on long-running processes.

**Phase to address:**
Phase 2 (hook implementation discipline).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcode query param names per widget | Fast prototype | Breaking changes when adding composite filters | Only in throwaway spike |
| Inline JS/CSS in templates | Quick visual demo | Theme incompatibility and hard maintenance | Never for library release |
| Global jQuery assumptions (`$`) | Reuse old snippets | Conflicts with admin namespace and plugins | Never in admin package |
| Always-on facet/count queries | Rich UI quickly | DB query explosion on large datasets | Only behind explicit feature flag |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Django admin media | Loading scripts manually in random templates | Use `ModelAdmin`/widget media consistently and include required admin init assets |
| Select2 behavior | Assuming dropdown placement always correct | Keep dropdown anchoring configurable in adapters; test in constrained containers/modals |
| Admin theme overrides | Replacing base blocks without `block.super` | Preserve parent block content and layer custom assets/styles on top |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Unindexed `icontains` autocomplete | Slow typing feedback, DB CPU spikes | Indexed search fields + custom search backend hook | Usually noticeable at 100k+ rows |
| Default paginator `count()` on huge tables | Long TTFB even before data renders | Optional large-table paginator/count strategy | Usually noticeable at 1M+ rows |
| Always-on facets across many filters | Sudden rise in query count | Make facets opt-in per filter/admin | Noticeable with 6+ filters on large datasets |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Returning autocomplete data without request-scoped permission filters | Unauthorized data disclosure | Enforce model/object visibility checks in one shared query service |
| Exposing sensitive fields in search labels/results | Information leakage via typeahead | Explicitly whitelist display/search fields |
| Trusting client-provided filter params without validation | Unexpected queryset broadening and info exposure | Strict parameter schema + server-side coercion |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Autocomplete with no loading/error states | Users think filter is broken | Add loading, empty, and retry states |
| Inconsistent filter param persistence | Users lose context after edits | Preserve and normalize query params across changelist actions |
| One-size-fits-all filter widgets | Poor usability on high-cardinality fields | Adaptive widget selection (choices vs async autocomplete) |

## "Looks Done But Isn't" Checklist

- [ ] **Async autocomplete:** Works with permission-restricted staff users, not just superuser.
- [ ] **Performance:** P95 latency tested with realistic high-cardinality data.
- [ ] **Theme compatibility:** Verified in light + dark mode and at least one non-default admin theme.
- [ ] **Filter persistence:** Query params survive add/edit/delete round-trips correctly.
- [ ] **JS resilience:** No duplicate jQuery, no `$` global dependency, no missing `block.super` regressions.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong abstraction (`autocomplete_fields` misuse) | HIGH | Introduce dedicated filter abstraction; ship migration layer for old API |
| Query performance collapse | MEDIUM-HIGH | Add indexes, narrow search fields, custom search backend, optional paginator strategy |
| Theme breakage across consumers | MEDIUM | Move to tokenized CSS vars and adapter templates; add visual regression tests |
| Permission leak in autocomplete | HIGH | Patch endpoint checks immediately, rotate logs/review access, add role-based tests |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| `autocomplete_fields` misuse for changelist | Phase 1 | API docs and tests show separate changelist filter abstraction |
| Missing search/auth boundaries | Phase 2 | Role-based endpoint tests + forbidden-object probes |
| Unindexed search/perf collapse | Phase 2 & 4 | Benchmark suite with large fixtures passes latency budget |
| Expensive ordering/paginator count | Phase 4 | Query plans + APM traces show acceptable cost |
| Facet/query explosion | Phase 3 & 4 | Query-count regression tests with facets on/off |
| Widget conflict matrix | Phase 1 & 2 | Startup config validation catches incompatible settings |
| JS/admin integration drift | Phase 2 & 5 | End-to-end tests in stock + themed admin environments |
| Theme coupling | Phase 3 & 5 | Visual QA matrix (light/dark/custom theme) |
| Shared mutable hook state | Phase 2 | Repeated-request tests remain deterministic |

## Sources

- Django admin reference (5.2): `autocomplete_fields`, `search_fields`, `get_search_results`, paginator/order/facets/theming/media/jQuery — https://docs.djangoproject.com/en/5.2/ref/contrib/admin/ (**HIGH**)
- Django admin list filters (5.2): filter API surface and customization points — https://docs.djangoproject.com/en/5.2/ref/contrib/admin/filters/ (**HIGH**)
- Django admin JavaScript customization guidance (block inheritance and `block.super`) — https://docs.djangoproject.com/en/5.2/ref/contrib/admin/javascript/ (**HIGH**)
- Select2 troubleshooting (dropdown attachment issues in constrained containers) — https://select2.org/troubleshooting/common-problems (**MEDIUM**, external to Django but relevant to Select2-based widgets)

---
*Pitfalls research for: Django admin filtering library*
*Researched: 2026-04-20*

# Feature Research

**Domain:** Django admin filtering framework (library)
**Researched:** 2026-04-20
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Declarative `list_filter`-compatible API | Django admin users expect drop-in integration without replacing admin architecture | LOW | Must support `SimpleListFilter`/`FieldListFilter` patterns and standard querystring behavior. |
| Async autocomplete filter for FK/M2M | Official Django admin already uses async Select2 for `autocomplete_fields`; users expect similar behavior for list filters on large relations | MEDIUM | Must use server-side search endpoint + permissions + `search_fields` integration. |
| Server-side search + pagination for high-cardinality choices | Large datasets make static option lists unusable; ecosystem packages highlight this as core pain | MEDIUM | Return small pages, include term search, cap page size, avoid loading all choices into memory. |
| Dropdown/compact filter UI for long choice lists | Widely adopted by dropdown-focused packages because default sidebar becomes unwieldy | LOW | Should work for choices, related fields, and plain values with clear “All” reset. |
| Date and numeric range filters | Common operational/admin workflow; mature package support indicates baseline demand | MEDIUM | Include presets where possible (today, last 7 days, this month) but keep logic server-side. |
| Multi-filter coexistence + stable URL state | Admin users share links and expect back/forward browser behavior | LOW | Preserve selected filters in query params; ensure filters compose predictably. |
| Permission-safe filtering | Official admin docs emphasize object permissions around autocomplete/search data | MEDIUM | Never leak unavailable related objects in suggestions or counts. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Theme adapter layer (default admin + custom themes) | Most libraries focus on default admin only; adapter abstraction enables broad adoption | HIGH | Keep filter logic backend-first; render via adapter templates/components per theme. |
| Unified filter builders (dropdown/autocomplete/range) with one API style | Reduces cognitive overhead vs mixing unrelated third-party filter styles | MEDIUM | Example: `Filter.dropdown(...)`, `Filter.autocomplete(...)`, `Filter.range(...)`. |
| Performance guardrails built in | Prevents common production regressions on big tables | HIGH | Add safe defaults: debounced requests, query limits, optional `select_related` hints, timeout/error UX. |
| Extension SDK for custom filter types | Moves library from “set of widgets” to “platform” | MEDIUM | Publish stable hooks: queryset transformation, option provider, template slot, JS behavior hook. |
| Facet/count integration with budget controls | Gives users context (“how many”) while controlling query explosion | HIGH | Integrate with Django facets model; allow OFF/ON/ALWAYS per filter with thresholds. |
| Saved filter presets (team-level, optional) | Frequent admin workflows become one-click operations | MEDIUM | Keep optional and conservative; save querystring presets, not arbitrary unsafe query DSL by default. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Full React/Vue rewrite of admin filtering | “Modern UX” appeal | Breaks Django admin upgrade path, raises integration/support cost, conflicts with project scope | Keep progressive enhancement JS + server-rendered templates + adapter layer |
| “One mega filter builder” with arbitrary nested boolean logic in MVP | Power-user flexibility | High complexity, hard-to-debug queries, permission/performance risk | Ship composable simple filters first; defer advanced query language as optional integration |
| Client-side preload of all filter choices | Feels fast on tiny datasets | Collapses on high-cardinality data; memory/network spikes | Strict server-side search/pagination |
| Auto-generate rich filters for every model field | Fast setup demo | Produces noisy/slow UI and poor relevance | Explicit, declarative filter selection with sane defaults |
| Deep coupling to one admin skin | Faster first release | Vendor lock-in and fragile CSS/DOM assumptions | Adapter contracts + per-theme templates |

## Feature Dependencies

```text
Declarative API
    └──requires──> list_filter-compatible backend contracts

Autocomplete filter
    └──requires──> server-side search endpoint
                        └──requires──> permission-safe queryset + pagination

Range filters (date/number)
    └──enhances──> table-stakes filtering completeness

Theme adapter layer
    └──requires──> backend/frontend separation

Saved presets
    └──requires──> stable URL/querystring state

Facet/count integration
    └──requires──> query-budget controls

Arbitrary query language
    └──conflicts──> MVP simplicity/performance goals
```

### Dependency Notes

- **Autocomplete requires server-side search endpoint:** Without endpoint + pagination, high-cardinality fields regress to unusable dropdowns.
- **Server-side search requires permission-safe queryset:** Suggestion leaks are a hard blocker in admin contexts.
- **Theme adapter requires backend/frontend separation:** If filter logic is template-bound, multi-theme support becomes brittle.
- **Saved presets require stable querystring contract:** Presets should serialize existing URL filters, not invent a second state model.
- **Facet counts require budget controls:** Count queries scale with filter count and can degrade changelist performance.

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [ ] Declarative, `list_filter`-compatible API — core adoption path for Django teams.
- [ ] Dropdown filter + async autocomplete filter — covers low and high cardinality primary use cases.
- [ ] Server-side search/pagination + permission-safe option loading — required for scale and safety.
- [ ] Date/numeric range filters — high-frequency admin workflow support.
- [ ] Default Django admin renderer + adapter contract (at least one extension example) — validates theme-agnostic direction.

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] Facet/count toggles with performance thresholds — add once real workload profiles are observed.
- [ ] Filter preset save/share — add after teams validate repeated filter workflows.
- [ ] Extension SDK hardening (typed hooks, compatibility policy) — add once first external extensions appear.

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] Optional advanced query language integration (e.g., DjangoQL-style mode) — powerful, but not core MVP.
- [ ] Cross-model compound filter workflows — defer due to complexity and authorization edge cases.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Declarative API + list_filter compatibility | HIGH | LOW | P1 |
| Async autocomplete + server-side search/pagination | HIGH | MEDIUM | P1 |
| Date/numeric range filters | HIGH | MEDIUM | P1 |
| Theme adapter contract + default renderer | HIGH | MEDIUM | P1 |
| Facet/count controls | MEDIUM | HIGH | P2 |
| Saved filter presets | MEDIUM | MEDIUM | P2 |
| Advanced query language mode | MEDIUM | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Competitor A | Competitor B | Our Approach |
|---------|--------------|--------------|--------------|
| Dropdown filters | `django-admin-list-filter-dropdown` (simple, stable concept, but stale releases) | `django-more-admin-filters` (dropdown + multiselect variants, actively maintained) | First-class dropdown in unified API, modern Django compatibility focus |
| Autocomplete list filters | `django-admin-autocomplete-filter` (focused package, older release cadence) | `django-adminfilters` (broad filter catalog incl. autocomplete) | Make autocomplete a core table-stakes path, with explicit performance + permission guarantees |
| Range filters | `django-admin-rangefilter` (popular and active) | `django-adminfilters` (number/date variants) | Native range builders integrated with same API surface as dropdown/autocomplete |
| Advanced filtering/query DSL | `djangoql` (powerful search language) | `django-adminfilters` (lookup/querystring filters) | Keep optional/integrated later; avoid making complex DSL mandatory for MVP |

## Sources

- Django official docs — `ModelAdmin` list filters, autocomplete, facets, and performance notes (HIGH): https://docs.djangoproject.com/en/6.0/ref/contrib/admin/ and https://docs.djangoproject.com/en/6.0/ref/contrib/admin/filters/
- `django-admin-rangefilter` repository + release recency (MEDIUM): https://github.com/silentsokolov/django-admin-rangefilter
- `django-admin-autocomplete-filter` repository (MEDIUM): https://github.com/farhan0581/django-admin-autocomplete-filter
- `django-more-admin-filters` repository + Django 6.0 support claim (MEDIUM): https://github.com/thomst/django-more-admin-filters
- `django-adminfilters` repository + PyPI metadata/release history (MEDIUM): https://github.com/saxix/django-adminfilters and https://pypi.org/project/django-adminfilters/
- `django-admin-list-filter-dropdown` repository (LOW-MEDIUM; older activity, still useful as UX signal): https://github.com/mrts/django-admin-list-filter-dropdown
- `djangoql` repository (MEDIUM): https://github.com/ivelum/djangoql

---
*Feature research for: Django admin filtering framework*
*Researched: 2026-04-20*

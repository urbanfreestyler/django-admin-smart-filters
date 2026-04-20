# Architecture Research

**Domain:** Django admin filtering framework (library)
**Researched:** 2026-04-20
**Confidence:** HIGH

## Standard Architecture

### System Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                        Django Admin Integration Layer                        │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐   ┌──────────────────────┐   ┌──────────────────┐  │
│  │ ModelAdmin Mixin    │   │ Filter Registration  │   │ URL Hooking      │  │
│  │ (list_filter bridge)│   │ (declarative API)    │   │ (get_urls)       │  │
│  └──────────┬──────────┘   └──────────┬───────────┘   └────────┬─────────┘  │
│             │                         │                         │            │
├─────────────┴─────────────────────────┴─────────────────────────┴────────────┤
│                    Filter Engine + Presentation Contract                      │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────────────┐  │
│  │ Filter Spec      │  │ Query Compiler   │  │ UI Context Builder         │  │
│  │ (what filter is) │  │ (spec -> Q/ORM)  │  │ (widget config + state)    │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────────────┬─────────────┘  │
│           │                     │                           │                │
├───────────┴─────────────────────┴───────────────────────────┴────────────────┤
│               Delivery Layer (Templates, JS, Async Endpoints)                │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌────────────────────┐  ┌──────────────────────────┐  │
│  │ Theme Adapter    │  │ Widget Templates   │  │ Autocomplete Endpoint    │  │
│  │ (layout contract)│  │ (HTML fragments)   │  │ (permissioned JSON)      │  │
│  └────────┬─────────┘  └─────────┬──────────┘  └─────────────┬────────────┘  │
│           │                      │                           │                │
├───────────┴──────────────────────┴───────────────────────────┴────────────────┤
│                         Data + Infrastructure Layer                            │
│                  Django ORM / DB indexes / optional cache                      │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| `AdminIntegration` | Attach framework to `ModelAdmin`, map declarative filter definitions into admin lifecycle | `ModelAdmin` mixin + `list_filter` bridge + `get_urls()` extension |
| `FilterRegistry` | Source of truth for enabled filters, parameter names, widget type, query strategy | Python registry objects keyed by parameter name |
| `FilterEngine` | Parse request params, validate values, apply to queryset deterministically | `SimpleListFilter`/custom classes + service layer producing `Q` objects |
| `UIContract` | Build normalized render context independent of specific theme HTML | Dataclass/dict contract shared by templates/adapters |
| `ThemeAdapter` | Map UI contract into concrete template partials, CSS classes, and JS hooks per theme | Adapter interface (`render_filter`, `container_classes`, `assets`) |
| `AsyncEndpoint` | Handle autocomplete/search/pagination for high-cardinality fields with permission checks | Admin-scoped JSON view registered via `ModelAdmin.get_urls()` |
| `FrontendController` | Progressive enhancement: bind inputs, debounce search, sync URL params | Lightweight vanilla JS module loaded through admin Media |

## Recommended Project Structure

```text
django_smart_filters/
├── __init__.py                    # Public exports
├── apps.py                        # Django app config
├── admin/
│   ├── mixins.py                  # SmartFilterAdminMixin for ModelAdmin
│   ├── changelist.py              # Optional ChangeList integration helpers
│   └── urls.py                    # URL helpers for async endpoints
├── filters/
│   ├── specs.py                   # Declarative filter specs
│   ├── registry.py                # Registration/discovery
│   ├── params.py                  # Querystring parsing + validation
│   ├── compiler.py                # Spec -> ORM/Q translation
│   └── builtins/
│       ├── dropdown.py            # Dropdown backend behavior
│       └── autocomplete.py        # Autocomplete backend behavior
├── endpoints/
│   ├── views.py                   # JSON endpoints for async options
│   ├── schema.py                  # Response shape helpers
│   └── permissions.py             # Admin permission/visibility guards
├── ui/
│   ├── contracts.py               # Theme-agnostic render context
│   ├── templates/
│   │   └── django_smart_filters/  # Default template partials
│   └── static/django_smart_filters/
│       └── filters.js             # Progressive enhancement controller
├── themes/
│   ├── base.py                    # Adapter interface
│   ├── default_admin.py           # Default Django admin adapter
│   └── registry.py                # Adapter selection logic
└── tests/
    ├── test_filters_engine.py
    ├── test_endpoints.py
    ├── test_theme_adapters.py
    └── test_admin_integration.py
```

### Structure Rationale

- **`filters/`:** Keeps business logic (query semantics) separate from rendering and HTTP details.
- **`ui/` + `themes/`:** Enforces a clean contract so theme differences do not leak into filter/query logic.
- **`endpoints/`:** Isolates async concerns (pagination, permission checks, response shape) from page rendering.
- **`admin/`:** Single integration seam with Django admin hooks (`list_filter`, `Media`, `get_urls`).

## Architectural Patterns

### Pattern 1: Declarative Filter Spec + Compiled Query Strategy

**What:** Define filters as metadata/spec objects, then compile into queryset operations.
**When to use:** Always; this is the core extensibility mechanism.
**Trade-offs:** Slightly more abstraction up front, but prevents ad-hoc query logic spread across templates and views.

**Example:**
```python
from dataclasses import dataclass

@dataclass
class FilterSpec:
    name: str
    param: str
    widget: str          # "dropdown" | "autocomplete"
    lookup: str          # e.g. "status", "author__id"

def apply_filter(qs, spec: FilterSpec, raw_value: str):
    if not raw_value:
        return qs
    return qs.filter(**{spec.lookup: raw_value})
```

### Pattern 2: Theme Adapter Boundary

**What:** Keep a stable UI contract and let adapters translate to theme-specific templates/CSS hooks.
**When to use:** Required once supporting both default admin and custom themes.
**Trade-offs:** More files, but avoids hardcoded assumptions and reduces rewrite risk.

**Example:**
```python
class BaseThemeAdapter:
    name = "base"

    def filter_template(self, widget_type: str) -> str:
        raise NotImplementedError

class DefaultAdminAdapter(BaseThemeAdapter):
    name = "django_admin"

    def filter_template(self, widget_type: str) -> str:
        return f"django_smart_filters/default/{widget_type}.html"
```

### Pattern 3: Progressive Enhancement for Async Widgets

**What:** Server renders initial filter shell; JS adds async behavior for autocomplete.
**When to use:** High-cardinality fields where static choices are too large.
**Trade-offs:** Requires endpoint + JS coordination, but keeps admin functional without SPA complexity.

## Data Flow

### Request Flow

```text
[Admin changelist request]
    ↓
[ModelAdmin + SmartFilterAdminMixin]
    ↓
[FilterRegistry loads specs]
    ↓
[Params parser validates querystring]
    ↓
[FilterEngine applies queryset filters]
    ↓
[UIContract builder prepares widget context]
    ↓
[ThemeAdapter selects template fragments]
    ↓
[Django template renders sidebar + assets]
```

### Async Autocomplete Flow

```text
[User types in autocomplete widget]
    ↓ (debounced JS)
[GET /admin/.../smart-filter-options/?q=...&page=...]
    ↓
[Endpoint permission + filter visibility checks]
    ↓
[Backend search + pagination query]
    ↓
[JSON options payload]
    ↓
[Widget updates options list and hidden value]
    ↓
[Form submit -> changelist URL params updated]
```

### State Management

```text
URL querystring = source of truth
    ↓
Server parses params -> queryset + selected UI state
    ↓
Templates render selected filter values
    ↓
JS only mutates query params / fetches options (no separate app state store)
```

### Key Data Flows

1. **Filter application flow:** URL params -> validated filter values -> queryset constraints -> result list.
2. **Filter options flow:** User search term -> async endpoint -> paginated option set -> widget display.
3. **Theme rendering flow:** UI contract -> adapter -> theme-specific templates/classes.

## Component Boundaries (Who Talks to What)

| Component | Talks To | Communication | Rule |
|-----------|----------|---------------|------|
| `ModelAdmin` mixin | `FilterRegistry`, `FilterEngine`, `ThemeAdapter` | Python method calls | `ModelAdmin` never contains filter query logic directly |
| `FilterEngine` | Django ORM only | QuerySet/Q operations | No template or theme concerns inside engine |
| `ThemeAdapter` | `UIContract`, Django templates | Context + template name | No database access inside adapter |
| `FrontendController` | `AsyncEndpoint` | HTTP JSON | No direct access to queryset logic |
| `AsyncEndpoint` | `FilterRegistry`, ORM, permission checks | Python + ORM + JSON response | Must enforce admin permissions and scoped data |

## Suggested Build Order (Dependency-Driven)

1. **Core filter domain (specs, params, compiler, engine)**
   - Dependency base for everything else.
   - Deliverables: deterministic queryset filtering + tests.

2. **Admin integration seam (`ModelAdmin` mixin + registration)**
   - Wires engine into real admin changelist lifecycle.
   - Deliverables: dropdown filter working end-to-end without async.

3. **UI contract + default theme adapter + templates**
   - Stabilizes rendering boundary before adding multiple themes.
   - Deliverables: default Django admin rendering parity.

4. **Async endpoint + frontend controller (autocomplete)**
   - Depends on established registry + permission model + UI contract.
   - Deliverables: high-cardinality autocomplete with pagination.

5. **Additional theme adapters + adapter test matrix**
   - Safe to add once contract is stable.
   - Deliverables: adapter compatibility layer and docs.

6. **Performance hardening (indexes, caching, benchmark fixtures)**
   - Last, after usage patterns are known.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k admin users | Monolithic Django app, no cache required, focus on correct query logic |
| 1k-100k records per filtered model | Add DB indexes on filtered/search fields; optimize queryset/select_related |
| 100k+ to 1M+ records | Strictly async option loading, aggressive pagination, optional caching for hot option lookups |

### Scaling Priorities

1. **First bottleneck: option loading for high-cardinality fields** — fix with async autocomplete + server-side search.
2. **Second bottleneck: expensive facet/count/filter combinations** — reduce expensive counts and optimize DB indexes/query plans.

## Anti-Patterns

### Anti-Pattern 1: Query logic embedded in templates/widgets

**What people do:** Put filtering decisions in template tags or JS conditionals.
**Why it's wrong:** Duplicates logic, breaks testability, and causes behavior drift across themes.
**Do this instead:** Centralize all query semantics in `FilterEngine`.

### Anti-Pattern 2: Eagerly loading full choice lists

**What people do:** Render all filter options server-side for large relations.
**Why it's wrong:** Slow pages, memory blowups, poor UX.
**Do this instead:** Use async autocomplete endpoints with pagination.

### Anti-Pattern 3: Bypassing admin permission checks in async endpoints

**What people do:** Expose raw JSON search endpoint without admin-scoped permissions.
**Why it's wrong:** Potential data disclosure.
**Do this instead:** Reuse admin permission gates and model-level visibility checks in endpoint layer.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Database (PostgreSQL/MySQL/SQLite) | Django ORM queries from `FilterEngine` and endpoints | Indexes on filter/search columns are critical at scale |
| Optional cache (Redis/local-memory) | Cache hot autocomplete result pages | Optional; add only after measuring hotspot latency |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `admin ↔ filters` | Direct Python API | Keeps admin hook code thin and declarative |
| `filters ↔ ui` | UI contract object | Prevents theme coupling to query logic |
| `ui ↔ themes` | Adapter interface | Enables default admin + custom theme support |
| `frontend ↔ endpoints` | JSON HTTP | Stable schema required for backward compatibility |

## Sources

- Django admin list filters (official): https://docs.djangoproject.com/en/stable/ref/contrib/admin/filters/
- Django `ModelAdmin` reference (`list_filter`, `autocomplete_fields`, `get_urls`, `search_fields`, `show_facets`): https://docs.djangoproject.com/en/stable/ref/contrib/admin/
- Django admin JavaScript customization: https://docs.djangoproject.com/en/stable/ref/contrib/admin/javascript/
- Django template override strategy: https://docs.djangoproject.com/en/stable/howto/overriding-templates/

---
*Architecture research for: Django Smart Filters*
*Researched: 2026-04-20*

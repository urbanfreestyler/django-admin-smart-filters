# Architecture & Technical Reference: Django Smart Filters

This document serves as the definitive architecture and technical reference for the **Django Smart Filters** package. It provides a deeper look into the systemic boundaries, component lifecycle, frontend integration, and design decisions.

---

## 1. Executive Summary

Django Smart Filters is designed to enhance the filtering capabilities of the default Django admin out of the box while maintaining absolute UI-agnosticism. By replacing the default synchronous `list_filter` with declarative, API-supported smart filters, it provides better handling for high-cardinality fields via asynchronous endpoints (e.g., Autocomplete) and a robust client-side presentation (Chips and dedicated UI controls).

The architecture is layered strictly between:
1. **Declaration**: Describing the intent through fluent builders or explicit classes.
2. **State Management**: Parsing requested filters deterministically from raw URLs.
3. **Query Application**: Translating state properties into Django ORM equivalents safely.
4. **Presentation**: Using dynamically resolved `ThemeAdapter` components to remain agnostic toward Jazzmin, Grappelli, or standard Django stylesheets.

---

## 2. Architecture Overview

```mermaid
graph TD
    A[User Request (GET)] --> B[SmartFilterAdminMixin];
    
    subgraph Initialization
    B --> C[Fetch Filter Declarations];
    C --> D[Normalize to FilterSpecs];
    end
    
    subgraph State Management
    D --> E[parse_filter_state];
    E --> F[Generate Deterministic State Dictionary];
    end
    
    subgraph Query Execution
    F --> G[apply_filter_state];
    G --> H[Map kind to Field Lookups];
    H --> I[Apply to Base Queryset];
    end
    
    subgraph Presentation
    F --> J[Build Filter Controls Context];
    F --> K[Build Active Chips Context];
    J -.-> L[ThemeAdapter resolve_template];
    K -.-> L;
    L --> M[Render HTML fragment for changelist view];
    end

    I --> N[Final Queryset for Changelist];
    M --> N;
    
    subgraph Frontend Actions
    O[Client Autocomplete Input] --> P[smart_filter_autocomplete_view];
    P --> Q[search_autocomplete_options];
    Q --> R[JSON Response pageable choices];
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px;
    style N fill:#9f9,stroke:#333,stroke-width:2px;
    style P fill:#ccf,stroke:#333;
```

---

## 3. Core Layer Definitions

### 3.1. `SmartFilterAdminMixin` (`admin.py`)
The primary adoption seam for Django application logic. Appending this mixin to a `ModelAdmin` overrides the critical endpoints (`changelist_view`, `get_queryset`, `get_urls`) to integrate the smart filtering stack.

- **`get_queryset()`**: Hijacked to read parsed state mapped to generated `FilterSpecs` and delegates ORM modifications to the internal `query.py` module before the default processing resumes.
- **`changelist_view()`**: Re-computes active state and configurations to dispatch required context arrays (`filter_controls`, `active_filter_chips`) down into overriden template layouts.
- **Autocomplete View**: Patches the routing to introduce a dedicated `smart-filters/autocomplete/` endpoint resolving paged `JsonResponse` items for UI fetching.

### 3.2. Declarations (`declarations.py` & `builder.py`)
Rather than relying on static definitions inside strings, the package utilizes an abstract `ClassFilterDeclaration` which handles the declaration mapping (query hooks, specific aliases relative to field names, etc). 

- **Fluent API**: An alternative pattern exposed via `builder.py` (`Filter.field("foo").dropdown().with_query_hook(...)`) providing dynamic composability, simplifying repetitive boilerplate code.

### 3.3. State Parsing and Validation (`state.py`)
Because Django passes query state solely via URL `GET` arguments, `django_admin_smart_filters` relies upon a normalization phase converting `QueryDict` properties into typed programmatic constructs depending on the component's `filter_kind`.
- **Booleans**: Parsed against known truthy (`1`, `true`, `yes`) mappings.
- **Ranges (Numeric & Date)**: Intercepts scoped `_start`/`_end` and `_min`/`_max` postfix rules for mapping fields gracefully without collisions.
- **Multivalue Array Elements**: Decouples comma-separated attributes or multiple repeated instances (`foo=a&foo=b`).

### 3.4. Query Execution (`query.py`)
Responsible for executing the parsed values against native ORM `QuerySet` commands natively supported by Django architectures.
- Built-ins automatically generate standard commands (`__gte`, `__lte`, `__in`).
- Can be overridden using `QueryHook` callables attached to specific specs in declaration time for distinct join scenarios spanning relations.

---

## 4. Customizing UI Extensibility (Theme Compatibility)

The package operates entirely UI-Agnostically through `ThemeAdapter` constructs inside `theme.py`.

### 4.1. The `ThemeAdapter` Interface
`ModelAdmin.smart_filter_theme_adapter` points to an explicit theme implementation. During template rendering, fragments are not resolved arbitrarily but fetched strictly via the adapter.
For instance, a `ThemeAdapter` designates where `controls_template` and `active_bar_template` should originate. 

> [!NOTE]
> This decouples the core logic of query filtering from breaking visually when the user switches to alternate administrative packages like `Jazzmin`, `Grappelli`, or Custom Frontend Apps.

---

## 5. Extensibility Hooks

The core constraints have been intentionally kept minimal to ensure straightforward customization.

### 5.1. Component Registry (`registry.py`)
While `dropdown`, `boolean_toggle` and `autocomplete` are supported out-of-the-box, proprietary component kinds can be enforced by defining a `FilterComponent` implementation and registering it globally:
```python
from django_admin_smart_filters import register_filter_component, FilterComponent

class GeometryRadiusComponent(FilterComponent):
    key = "geom_radius"
    filter_kind = "numeric_range"

register_filter_component("geom_radius", GeometryRadiusComponent)
```

### 5.2. Functional Hooks (`contracts.py`)
- `QueryHook`: A programmatic escape hatch avoiding subclasses when business logic needs unique query mapping behavior.
- `WidgetHook`: Permits customized frontend layout mapping or custom state transmission specifically down onto the HTML element.

---

## 6. Design Rationales & Architectural Decisions

Why was this package structured this way rather than extending existing capabilities?

1. **Circumventing `SimpleListFilter` Limitations**
   Django's default choice lists aggressively process synchronously over SQL `COUNT` functions. Building our own state pipeline enables asynchronous endpoints (bypassing initialization locking entirely for millions of records).
   
2. **URL as the Single Source of Truth**
   The architecture heavily relies on URL `params.py` string mappings to propagate active chips and shareable search parameters. By intercepting URL mapping independently from default list filters, Smart Filters avoids recursive query execution loop vulnerabilities.

3. **Progressive Frontend Enhancements**
   Instead of demanding integration via Webpack/Node compilation, all provided presentation features load gracefully mapped under simple Data-Attribute tags inside Django templates to prioritize seamless backwards compatibility out of the box.

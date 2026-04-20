# Django Smart Filters

A flexible, extensible, and theme-compatible filtering system for Django Admin.

---

## Overview

Django’s built-in `list_filter` is effective for simple use cases but breaks down with:

- High-cardinality fields (e.g., hundreds of related objects)
- Poor UX for selection and discovery
- Limited customization options
- Incompatibility with modern admin themes

**Django Smart Filters** addresses these limitations by providing a pluggable, UI-agnostic filtering framework that enhances both developer experience and admin usability.

---

## Goals

- Improve usability of Django admin filters
- Support multiple UI paradigms (dropdowns, autocomplete, etc.)
- Handle large datasets efficiently
- Remain compatible with different admin themes
- Provide a clean, declarative API
- Be extensible for custom filter types

---

## Key Features

### 1. Multiple Filter UI Types

Supports different rendering strategies depending on the data:

- Dropdown filters (for medium-sized datasets)
- Autocomplete filters (for large datasets / foreign keys)
- Multi-select filters (checkboxes or tag-based)
- Date range filters
- Numeric range filters
- Boolean toggles

---

### 2. Autocomplete (Async) Filters

Designed for high-cardinality relationships:

- AJAX-powered search
- Server-side filtering
- Pagination support
- Debounced queries
- Minimal memory footprint

---

### 3. Theme Compatibility

Works across different Django admin themes:

- Default Django Admin
- Extensible adapter system for custom themes
- Clean template override structure
- No hardcoded UI assumptions

---

### 4. Declarative API

Simple and expressive configuration:

```python
class ProductAdmin(admin.ModelAdmin):
    list_filter = [
        DropdownFilter("category"),
        AutocompleteFilter("brand"),
        MultiSelectFilter("status"),
        DateRangeFilter("created_at"),
    ]
````

Alternative fluent API:

```python
list_filter = [
    Filter.field("category").dropdown(),
    Filter.field("brand").autocomplete(),
]
```

---

### 5. High-Performance Handling

* Lazy loading of filter options
* Queryset-based filtering
* Optional caching layer
* Avoids loading full choice lists into memory

---

### 6. Improved UX

* Clean filter UI components
* Active filters displayed as tags/chips
* Easy reset/clear functionality
* Consistent URL query parameter handling

---

### 7. Extensibility

Developers can create custom filters:

* Base `FilterComponent` class
* Custom query logic hooks
* Pluggable widgets
* Reusable filter definitions

---

## Architecture

### 1. Backend Layer

* Extends Django’s `SimpleListFilter`
* Handles filtering logic
* Provides API endpoints for async filters

---

### 2. UI Layer

* Template fragments for each filter type
* Lightweight JavaScript for interactivity
* Framework-agnostic (optionally Alpine.js)

---

### 3. Adapter Layer

* Theme-specific rendering adapters
* Allows compatibility with multiple admin UIs
* Easily extendable for third-party themes

---

## Example: Autocomplete Filter

```python
class BrandFilter(AutocompleteFilter):
    title = "Brand"
    field_name = "brand"
    search_fields = ["name__icontains"]
```

---

## MVP Scope

Initial release will include:

* Dropdown filter
* Autocomplete filter (core feature)
* Default Django admin support
* Basic theme adapter structure
* Documentation with examples

---

## Non-Goals (for MVP)

* Full frontend frameworks (React/Vue)
* Complex analytics dashboards
* Overly abstract plugin systems

---

## Why This Project

* Django admin is widely used but under-optimized
* Filtering UX is a common pain point
* Existing libraries are limited or inflexible
* Modern admin themes need better integration support

---

## Roadmap

### Phase 1 (MVP)

* Core filter classes
* Dropdown + autocomplete
* Documentation

### Phase 2

* Multi-select filters
* Range filters
* Theme adapters

### Phase 3

* Advanced UX (chips, saved filters)
* Performance optimizations
* Community extensions

---

## Naming Ideas

* django-smart-filters
* django-admin-filters-plus
* django-adaptive-filters

---

## Contribution

Contributions are welcome:

* New filter types
* Theme adapters
* Performance improvements
* Documentation enhancements

---

## License

MIT License (recommended)


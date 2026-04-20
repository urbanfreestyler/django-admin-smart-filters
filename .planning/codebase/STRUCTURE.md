# Codebase Structure

**Analysis Date:** 2026-04-20

## Directory Layout

```text
django-admin-smart-filters/
├── django_smart_filters/                        # Library package: declarations, query/state engine, admin mixin, templates/static
│   ├── static/django_smart_filters/             # Browser assets for smart filter UX (`autocomplete.js`)
│   └── templates/admin/django_smart_filters/    # Django admin template fragments for controls and active chips
├── tests/                                       # Pytest suite covering declarations, state/query logic, admin integration, UI payloads
├── docs/                                        # Project-level descriptive documentation
├── .planning/                                   # Planning artifacts; generated codebase mapping docs live in `.planning/codebase/`
├── AGENTS.md                                    # Agent workflow constraints and project context
└── .gitignore                                   # Ignore rules (`__pycache__/`, `*.pyc`, `.idea/`, `.venv/`)
```

## Directory Purposes

**django_smart_filters/:**
- Purpose: Keep all runtime package code for smart filtering.
- Contains: Core contracts and normalization (`contracts.py`, `declarations.py`, `builder.py`, `validation.py`, `params.py`), runtime execution (`state.py`, `query.py`, `autocomplete.py`, `chips.py`), Django admin integration (`admin.py`), templates/static assets.
- Key files: `django_smart_filters/admin.py`, `django_smart_filters/query.py`, `django_smart_filters/state.py`, `django_smart_filters/autocomplete.py`, `django_smart_filters/contracts.py`.

**django_smart_filters/templates/admin/django_smart_filters/:**
- Purpose: Render smart filter controls and active-filter bar.
- Contains: `filter_controls.html`, `autocomplete_control.html`, `active_filters_bar.html`, `chip.html`.
- Key files: `django_smart_filters/templates/admin/django_smart_filters/filter_controls.html`, `django_smart_filters/templates/admin/django_smart_filters/autocomplete_control.html`.

**django_smart_filters/static/django_smart_filters/:**
- Purpose: Ship client-side progressive enhancement code for autocomplete behavior.
- Contains: `autocomplete.js`.
- Key files: `django_smart_filters/static/django_smart_filters/autocomplete.js`.

**tests/:**
- Purpose: Verify behavior of every core module and admin integration path.
- Contains: Focused test modules by concern (`test_declarations.py`, `test_validation.py`, `test_state.py`, `test_query.py`, `test_autocomplete.py`, `test_admin_filters.py`, `test_autocomplete_admin_endpoint.py`, `test_autocomplete_ui.py`, `test_active_filters_ui.py`).
- Key files: `tests/test_admin_filters.py`, `tests/test_autocomplete_admin_endpoint.py`, `tests/test_state.py`, `tests/test_query.py`.

**docs/:**
- Purpose: Human-readable project description and goals.
- Contains: `project_description.md`.
- Key files: `docs/project_description.md`.

**.planning/:**
- Purpose: Planning and orchestration artifacts for GSD workflow.
- Contains: `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, phase docs, `research/`, and output docs under `.planning/codebase/`.
- Key files: `.planning/PROJECT.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`.

## Key File Locations

**Entry Points:**
- `django_smart_filters/admin.py`: Main runtime entrypoint via `SmartFilterAdminMixin` for Django admin integration.
- `django_smart_filters/builder.py`: Fluent declaration entrypoint `Filter.field(...)`.
- `django_smart_filters/declarations.py`: Class-style declaration entrypoint `DropdownFilter(...)` and normalization helpers.
- `django_smart_filters/__init__.py`: Public package export surface.

**Configuration:**
- `AGENTS.md`: Repository-level workflow and constraints for automated coding agents.
- `.gitignore`: Workspace ignore policy.
- Django test settings are configured inline in integration test modules: `tests/test_admin_filters.py`, `tests/test_autocomplete_admin_endpoint.py`, `tests/test_autocomplete_ui.py`.

**Core Logic:**
- `django_smart_filters/contracts.py`: `FilterSpec`, `QueryHook`, `WidgetHook` contracts.
- `django_smart_filters/validation.py`: Supported filter kinds and spec validation.
- `django_smart_filters/params.py`: Deterministic URL parameter naming.
- `django_smart_filters/state.py`: Parse/serialize filter state to/from `QueryDict`.
- `django_smart_filters/query.py`: Apply normalized state to queryset.
- `django_smart_filters/autocomplete.py`: Parse autocomplete request + paginated search.
- `django_smart_filters/chips.py`: Build active chip view models and removal/reset URLs.

**Testing:**
- `tests/test_declarations.py`: Declaration equivalence and normalization expectations.
- `tests/test_validation.py`: Validation errors and collision handling.
- `tests/test_state.py`: Query string parsing/serialization invariants.
- `tests/test_query.py`: Queryset application by filter kind and query hook behavior.
- `tests/test_autocomplete.py`: Autocomplete request parsing and pagination semantics.
- `tests/test_admin_filters.py`: Mixin changelist context and queryset integration.
- `tests/test_autocomplete_admin_endpoint.py`: Endpoint behavior and URL registration.
- `tests/test_autocomplete_ui.py`: Template/JS expectations for lazy autocomplete UI.
- `tests/test_active_filters_ui.py`: Chip labels and remove/reset URL determinism.

## Naming Conventions

**Files:**
- Python modules use snake_case: `django_smart_filters/autocomplete.py`, `django_smart_filters/test_state.py` style under `tests/`.
- Tests use `test_*.py`: `tests/test_query.py`, `tests/test_autocomplete_admin_endpoint.py`.
- Template fragments use snake_case `.html`: `active_filters_bar.html`, `filter_controls.html`.

**Directories:**
- Package and nested static/template directories use snake_case and Django conventions: `django_smart_filters/`, `django_smart_filters/static/django_smart_filters/`, `django_smart_filters/templates/admin/django_smart_filters/`.

## Where to Add New Code

**New Feature:**
- Primary code: add domain logic in `django_smart_filters/` near existing concern module (state/query/autocomplete/chips/declarations).
- Admin wiring: extend `django_smart_filters/admin.py` only for orchestration/hook points.
- Tests: add/extend focused module under `tests/test_<concern>.py`; add integration coverage in `tests/test_admin_filters.py` or `tests/test_autocomplete_admin_endpoint.py` when behavior touches admin lifecycle.

**New Component/Module:**
- Implementation: add new Python module in `django_smart_filters/` with snake_case filename and export through explicit imports where needed.
- UI fragment: place templates in `django_smart_filters/templates/admin/django_smart_filters/` and static assets in `django_smart_filters/static/django_smart_filters/`.

**Utilities:**
- Shared helpers: colocate by concern in existing modules (`params.py` for param naming, `validation.py` for schema checks, `chips.py` for URL/chip helpers). Add a dedicated module under `django_smart_filters/` only when the helper does not fit existing concern boundaries.

## Special Directories

**`django_smart_filters/__pycache__/`:**
- Purpose: Python bytecode cache.
- Generated: Yes.
- Committed: No (ignored by `.gitignore`).

**`tests/__pycache__/`:**
- Purpose: Python bytecode cache for test modules.
- Generated: Yes.
- Committed: No (ignored by `.gitignore`).

**`.venv/`:**
- Purpose: Local virtual environment.
- Generated: Yes.
- Committed: No (ignored by `.gitignore`).

**`.planning/codebase/`:**
- Purpose: Generated architecture/structure/quality/stack mapping docs consumed by GSD planning/execution commands.
- Generated: Yes.
- Committed: Yes (planning artifacts directory is tracked in repository structure).

---

*Structure analysis: 2026-04-20*

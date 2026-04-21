# Codebase Structure

**Analysis Date:** 2026-04-21

## Directory Layout

```text
django-admin-enhanced-filters/
├── django_smart_filters/         # Library package: contracts, admin mixin, state/query logic
│   ├── static/django_smart_filters/    # Frontend runtime assets (autocomplete JS)
│   └── templates/admin/django_smart_filters/  # Template fragments and theme adapter templates
├── tests/                        # Unit/integration-style tests for all modules and docs snippets
├── docs/                         # Usage and extension documentation
├── .planning/                    # GSD planning artifacts and generated codebase maps
├── AGENTS.md                     # Agent workflow/project guidance
└── .gitignore                    # Git ignore rules
```

## Directory Purposes

**`django_smart_filters/`:**
- Purpose: Source package implementing smart filter contracts, normalization, query/state processing, admin integration, and theme adapter support.
- Contains: Python modules (`admin.py`, `query.py`, `state.py`, `autocomplete.py`, `theme.py`, etc.), Django templates, static JS.
- Key files: `django_smart_filters/admin.py`, `django_smart_filters/declarations.py`, `django_smart_filters/query.py`, `django_smart_filters/state.py`, `django_smart_filters/theme.py`

**`django_smart_filters/templates/admin/django_smart_filters/`:**
- Purpose: Render smart filter controls and active-filter chips in Django admin changelist.
- Contains: Wrapper templates (`filter_controls.html`, `active_filters_bar.html`), reusable partials (`chip.html`, `autocomplete_control.html`), default theme templates under `theme/default/`.
- Key files: `django_smart_filters/templates/admin/django_smart_filters/theme/default/filter_controls.html`, `django_smart_filters/templates/admin/django_smart_filters/theme/default/active_filters_bar.html`

**`django_smart_filters/static/django_smart_filters/`:**
- Purpose: Progressive enhancement runtime for autocomplete behavior.
- Contains: Plain JavaScript module for debounce, stale-response guard, async pagination.
- Key files: `django_smart_filters/static/django_smart_filters/autocomplete.js`

**`tests/`:**
- Purpose: Verify declarations, state/query semantics, admin integration, autocomplete endpoint/UI, adapters, docs examples.
- Contains: `test_*.py` modules with in-memory query fakes and RequestFactory-based admin tests.
- Key files: `tests/test_admin_filters.py`, `tests/test_autocomplete_admin_endpoint.py`, `tests/test_query.py`, `tests/test_state.py`, `tests/test_docs_examples.py`

**`docs/`:**
- Purpose: Consumer-facing examples and extension contracts.
- Contains: Markdown guides for project description, extension hooks, adapters, and examples.
- Key files: `docs/extension_hooks.md`, `docs/theme_adapters.md`, `docs/examples.md`

**`.planning/`:**
- Purpose: Planning/research/phase execution artifacts and generated mapping docs.
- Contains: `PROJECT.md`, `ROADMAP.md`, `STATE.md`, `research/`, `phases/`, `codebase/`.
- Key files: `.planning/PROJECT.md`, `.planning/research/STACK.md`, `.planning/codebase/ARCHITECTURE.md`

## Key File Locations

**Entry Points:**
- `django_smart_filters/admin.py`: Runtime integration entry for Django admin via `SmartFilterAdminMixin`.
- `django_smart_filters/__init__.py`: Public package exports for contracts and extension registry APIs.
- `django_smart_filters/builder.py`: Fluent declaration entry (`Filter.field`).
- `django_smart_filters/declarations.py`: Class-style declaration entry and normalization.

**Configuration:**
- `AGENTS.md`: Agent behavior and GSD workflow rules.
- `.planning/config.json`: Planning configuration metadata.
- Not detected: `pyproject.toml`, `setup.py`, `pytest.ini`, `tox.ini` in repository root.

**Core Logic:**
- `django_smart_filters/contracts.py`: Core protocols/contracts (`FilterSpec`, hooks, component base).
- `django_smart_filters/validation.py`: Spec validation and supported kind enforcement.
- `django_smart_filters/query.py`: Queryset application for each filter kind.
- `django_smart_filters/state.py`: URL query parsing and serialization.
- `django_smart_filters/autocomplete.py`: Autocomplete request validation and search pagination.
- `django_smart_filters/chips.py`: Active chip generation and URL mutation helpers.
- `django_smart_filters/theme.py`: Adapter contract/default resolution.
- `django_smart_filters/registry.py`: Component extension registration and resolution.

**Testing:**
- `tests/test_declarations.py`: Declaration normalization and equivalence tests.
- `tests/test_validation.py`: Validation failure coverage.
- `tests/test_query.py`: Kind-aware queryset filtering behavior.
- `tests/test_state.py`: QueryDict parse/serialize behavior.
- `tests/test_admin_filters.py`: Changelist integration and context coverage.
- `tests/test_autocomplete_admin_endpoint.py`: JSON endpoint behavior and route registration.
- `tests/test_autocomplete_ui.py`: Template/JS metadata and client behavior assertions.
- `tests/test_theme_adapters.py`: Adapter resolution and template selection.
- `tests/test_extension_registry.py`: Registry behavior and hook persistence.
- `tests/test_docs_examples.py`: Executable docs snippet checks.

## Naming Conventions

**Files:**
- `snake_case.py` for source and tests: `django_smart_filters/autocomplete.py`, `tests/test_active_filters_ui.py`.
- Test modules use `test_<area>.py`: `tests/test_theme_adapters.py`.
- Template fragments use `snake_case.html`: `django_smart_filters/templates/admin/django_smart_filters/autocomplete_control.html`.

**Directories:**
- Python package and directories use lowercase with underscores where needed: `django_smart_filters/`.
- Django template hierarchy follows admin namespace path: `templates/admin/django_smart_filters/theme/default/`.
- Static files are namespaced by package: `static/django_smart_filters/`.

## Where to Add New Code

**New Feature:**
- Primary code: Add domain logic under `django_smart_filters/` by concern (e.g., new query behavior in `django_smart_filters/query.py` or new module like `django_smart_filters/<feature>.py`).
- Tests: Add corresponding `tests/test_<feature>.py` with focused unit behavior and admin integration coverage where applicable.

**New Component/Module:**
- Implementation: Define extension contracts/components in `django_smart_filters/contracts.py` or dedicated module; register/resolve behavior in `django_smart_filters/registry.py`; normalize usage in `django_smart_filters/declarations.py`.

**Utilities:**
- Shared helpers: Place reusable, pure helper logic in focused modules under `django_smart_filters/` (pattern examples: `django_smart_filters/params.py`, `django_smart_filters/validation.py`).

## Special Directories

**`django_smart_filters/templates/`:**
- Purpose: Django template fragments for admin rendering and theme adapters.
- Generated: No
- Committed: Yes

**`django_smart_filters/static/`:**
- Purpose: Browser-side runtime assets used by templates.
- Generated: No
- Committed: Yes

**`tests/__pycache__/`:**
- Purpose: Python bytecode cache from local test execution.
- Generated: Yes
- Committed: No (ignored workspace artifact)

**`.planning/codebase/`:**
- Purpose: Generated codebase mapping documents consumed by GSD planner/executor.
- Generated: Yes
- Committed: Yes

---

*Structure analysis: 2026-04-21*

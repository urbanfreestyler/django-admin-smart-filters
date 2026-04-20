# Technology Stack

**Analysis Date:** 2026-04-20

## Languages

**Primary:**
- Python 3.x (exact runtime version not pinned in repo) - Library and tests in `django_smart_filters/*.py` and `tests/*.py`

**Secondary:**
- HTML (Django templates) - Admin UI rendering in `django_smart_filters/templates/admin/django_smart_filters/*.html`
- JavaScript (vanilla browser JS) - Client autocomplete behavior in `django_smart_filters/static/django_smart_filters/autocomplete.js`

## Runtime

**Environment:**
- Python + Django runtime (project is a reusable Django package; no standalone server entrypoint detected)

**Package Manager:**
- pip/setuptools workflow implied by Python package layout
- Version: Not detected
- Lockfile: missing (no `requirements*.txt`, `pyproject.toml`, `Pipfile`, or lockfile detected at repo root)

## Frameworks

**Core:**
- Django (version not pinned in repository manifests) - Admin integration and HTTP/templating APIs used in `django_smart_filters/admin.py`

**Testing:**
- pytest (imported in `tests/test_query.py`, `tests/test_validation.py`, `tests/test_active_filters_ui.py`)
- Django test utilities (`RequestFactory`, `QueryDict`) used in `tests/test_admin_filters.py`, `tests/test_autocomplete_admin_endpoint.py`, `tests/test_state.py`

**Build/Dev:**
- Not detected (no linter/formatter/build config files such as `pyproject.toml`, `setup.cfg`, `tox.ini`, `noxfile`, or CI config detected)

## Key Dependencies

**Critical:**
- `django` - Core admin mixin contract, URL routing, templates, request/response objects in `django_smart_filters/admin.py`
- Python stdlib (`dataclasses`, `typing`, `collections.abc`, `datetime`) - Data modeling and normalization logic in `django_smart_filters/autocomplete.py`, `django_smart_filters/query.py`, `django_smart_filters/declarations.py`

**Infrastructure:**
- Browser Fetch API - Autocomplete HTTP calls in `django_smart_filters/static/django_smart_filters/autocomplete.js`
- Django staticfiles/template loaders - Template and JS asset wiring in `django_smart_filters/templates/admin/django_smart_filters/filter_controls.html`

## Configuration

**Environment:**
- Runtime env var contract: Not detected (no `os.environ`/`getenv` usage in library code)
- Test-only Django settings are defined inline via `settings.configure(...)` in `tests/test_admin_filters.py`, `tests/test_autocomplete_ui.py`, and `tests/test_autocomplete_admin_endpoint.py`

**Build:**
- Build metadata/config files: Not detected (`pyproject.toml`, `setup.py`, `setup.cfg`, and requirements files are absent)
- Local repo ignores virtualenv and IDE artifacts via `.gitignore`

## Platform Requirements

**Development:**
- Python environment with Django and pytest installed (imports required by `django_smart_filters/*.py` and `tests/*.py`)
- Browser-capable Django admin page for JS-enhanced autocomplete from `django_smart_filters/static/django_smart_filters/autocomplete.js`

**Production:**
- Django Admin integration target (mixin intended for `ModelAdmin` subclasses in `django_smart_filters/admin.py`)
- Database backend provided by host Django project (this repo itself only configures in-memory SQLite inside tests)

---

*Stack analysis: 2026-04-20*

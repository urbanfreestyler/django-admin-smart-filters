# Technology Stack

**Analysis Date:** 2026-04-21

## Languages

**Primary:**
- Python (version not pinned in repo) - library runtime and core implementation in `django_smart_filters/*.py`.

**Secondary:**
- JavaScript (vanilla browser JS; version not pinned) - progressive enhancement for autocomplete in `django_smart_filters/static/django_smart_filters/autocomplete.js`.
- Django template language - admin UI rendering in `django_smart_filters/templates/admin/django_smart_filters/**/*.html`.

## Runtime

**Environment:**
- Python runtime (exact version not detected; no `pyproject.toml`, `requirements*.txt`, or `setup.py` present).
- Browser runtime for admin JS behavior in `django_smart_filters/static/django_smart_filters/autocomplete.js`.

**Package Manager:**
- Not detected (no `pyproject.toml`/Poetry/Pipenv/requirements manifest committed).
- Lockfile: missing (not detected).

## Frameworks

**Core:**
- Django (version not pinned in repository manifests) - admin integration via `SmartFilterAdminMixin` in `django_smart_filters/admin.py` and HTTP/template primitives (`django.http`, `django.template.loader`, `django.urls`).

**Testing:**
- pytest (imported and used in multiple tests, e.g., `tests/test_query.py`, `tests/test_autocomplete.py`, `tests/test_admin_filters.py`).
- Django test utilities (`RequestFactory`, `AdminSite`) used for integration-style tests in `tests/test_admin_filters.py` and `tests/test_autocomplete_admin_endpoint.py`.

**Build/Dev:**
- Not detected (no lint/type/build config files such as `ruff.toml`, `mypy.ini`, `tox.ini`, `.pre-commit-config.yaml`, or CI workflow files found).

## Key Dependencies

**Critical:**
- `django` - core platform dependency for admin extensibility and request/response handling; directly imported in `django_smart_filters/admin.py` and test modules under `tests/`.

**Infrastructure:**
- `pytest` - testing runner patterns and assertions used across `tests/*.py`.
- Python stdlib modules (`dataclasses`, `typing`, `collections.abc`, `datetime`) - foundational internal contracts and normalization logic in `django_smart_filters/contracts.py`, `django_smart_filters/theme.py`, `django_smart_filters/query.py`.

## Configuration

**Environment:**
- Production/runtime environment configuration file is not detected in repository root (no committed `.env*` files found).
- Test-local Django settings are configured inline via `settings.configure(...)` in `tests/test_admin_filters.py`, `tests/test_autocomplete_admin_endpoint.py`, `tests/test_autocomplete_ui.py`, and `tests/test_theme_adapters.py`.
- Required test settings pattern includes `INSTALLED_APPS`, `DATABASES` (SQLite in-memory), `ROOT_URLCONF`, and `TEMPLATES` in those test files.

**Build:**
- Build configuration files not detected (`pyproject.toml`, `setup.cfg`, `setup.py`, `tox.ini`, GitHub Actions workflow files all absent).

## Platform Requirements

**Development:**
- Use a Python environment with Django and pytest installed to run and validate modules in `django_smart_filters/` and `tests/`.
- Ensure Django template/static loading works for package templates and assets under `django_smart_filters/templates/` and `django_smart_filters/static/`.

**Production:**
- Deployment target is Django Admin within a Django application; this repository provides a reusable package layer (`django_smart_filters/`) rather than a standalone deployed service.

---

*Stack analysis: 2026-04-21*

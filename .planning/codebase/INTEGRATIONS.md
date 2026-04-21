# External Integrations

**Analysis Date:** 2026-04-21

## APIs & External Services

**Third-party APIs:**
- Not detected in runtime package code under `django_smart_filters/*.py`.
  - SDK/Client: Not applicable
  - Auth: Not applicable

**Internal HTTP endpoint (library-provided):**
- Django admin autocomplete JSON endpoint - used by package frontend script to fetch server-side options.
  - Server implementation: `django_smart_filters/admin.py` (`smart_filter_autocomplete_view`, `get_urls` route `smart-filters/autocomplete/`)
  - Client caller: `django_smart_filters/static/django_smart_filters/autocomplete.js` (`fetch(endpoint + "?" + params.toString())`)
  - Auth: inherited from `self.admin_site.admin_view(...)` wrapping in `django_smart_filters/admin.py`.

## Data Storage

**Databases:**
- Host application database via Django ORM queryset passed into mixin methods (no dedicated DB client in this package).
  - Connection: Not configured inside package code; delegated to host Django project settings.
  - Client: Django ORM queryset API usage in `django_smart_filters/query.py` and `django_smart_filters/autocomplete.py`.

**File Storage:**
- Local package static/templates only (`django_smart_filters/static/`, `django_smart_filters/templates/`); no external object storage integration detected.

**Caching:**
- None detected in current codebase (no cache backend calls in `django_smart_filters/*.py`).

## Authentication & Identity

**Auth Provider:**
- Django Admin authentication/authorization from consuming project.
  - Implementation: endpoint protection through Django admin wrapper `self.admin_site.admin_view(...)` in `django_smart_filters/admin.py`.

## Monitoring & Observability

**Error Tracking:**
- None detected (no Sentry/third-party error SDK imports in `django_smart_filters/*.py` or `tests/*.py`).

**Logs:**
- No explicit logging framework usage detected in package modules (`django_smart_filters/*.py`).

## CI/CD & Deployment

**Hosting:**
- Not applicable for standalone service hosting; library is intended to run inside a host Django admin application (`django_smart_filters/admin.py`, docs in `docs/project_description.md`).

**CI Pipeline:**
- Not detected (no `.github/workflows/*`, `tox.ini`, or other CI config files found).

## Environment Configuration

**Required env vars:**
- Not detected at package level (no `os.environ` usage in `django_smart_filters/*.py`).
- Test-only inline settings are used instead of env vars in `tests/test_admin_filters.py`, `tests/test_autocomplete_admin_endpoint.py`, `tests/test_autocomplete_ui.py`, and `tests/test_theme_adapters.py`.

**Secrets location:**
- Not detected in repository configuration files.
- `.env` files not detected in repository root scan.

## Webhooks & Callbacks

**Incoming:**
- None (no webhook receiver endpoints detected).

**Outgoing:**
- None to third-party systems.
- Browser-to-server callback flow exists only within host admin: client JS calls package endpoint (`django_smart_filters/static/django_smart_filters/autocomplete.js` → `django_smart_filters/admin.py`).

---

*Integration audit: 2026-04-21*

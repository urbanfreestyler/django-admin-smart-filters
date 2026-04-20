# External Integrations

**Analysis Date:** 2026-04-20

## APIs & External Services

**Internal HTTP endpoint (Django Admin):**
- Smart filter autocomplete endpoint - Serves paginated autocomplete results for admin filters
  - Implementation: `SmartFilterAdminMixin.smart_filter_autocomplete_view` in `django_smart_filters/admin.py`
  - Route registration: `get_urls()` adds `smart-filters/autocomplete/` in `django_smart_filters/admin.py`
  - Client: browser Fetch API in `django_smart_filters/static/django_smart_filters/autocomplete.js`
  - Auth: Django admin view wrapping via `self.admin_site.admin_view(...)` in `django_smart_filters/admin.py`

**Third-party external APIs:**
- Not detected (no Stripe/Supabase/AWS/HTTP SDK imports in `django_smart_filters/*.py`)

## Data Storage

**Databases:**
- Host Django project database (library applies queryset filters but does not own DB connections)
  - Connection: configured by consuming Django app (env var names not defined in this repository)
  - ORM/client: Django ORM querysets via `.filter()`, `.order_by()`, `.values_list()` in `django_smart_filters/query.py` and `django_smart_filters/autocomplete.py`

- Test database only: SQLite in-memory in `tests/test_admin_filters.py`, `tests/test_autocomplete_ui.py`, `tests/test_autocomplete_admin_endpoint.py`
  - Connection setting: `DATABASES["default"]` with `ENGINE="django.db.backends.sqlite3"` and `NAME=":memory:"`

**File Storage:**
- Local package static/templates only (`django_smart_filters/static/...`, `django_smart_filters/templates/...`)
- External object/file storage service: None detected

**Caching:**
- None detected (no Redis/memcached/cache backend integration code detected)

## Authentication & Identity

**Auth Provider:**
- Django Admin authentication/authorization context
  - Implementation: autocomplete endpoint is protected by `self.admin_site.admin_view(...)` in `django_smart_filters/admin.py`

## Monitoring & Observability

**Error Tracking:**
- None detected (no Sentry or external error SDK usage)

**Logs:**
- None detected (no logging framework usage in library files)

## CI/CD & Deployment

**Hosting:**
- Not applicable for standalone service; package is designed to be embedded in a host Django project

**CI Pipeline:**
- Not detected (no GitHub Actions/workflow files or other CI configs present)

## Environment Configuration

**Required env vars:**
- Not detected in repository code (no `os.environ`/`getenv` references)

**Secrets location:**
- No secrets files detected in repository root during analysis
- `.env` files: Not detected

## Webhooks & Callbacks

**Incoming:**
- None detected (no webhook receiver endpoints)

**Outgoing:**
- Browser-side GET requests from admin autocomplete control to same-site Django endpoint in `django_smart_filters/static/django_smart_filters/autocomplete.js`
- External callback/webhook emission: None detected

---

*Integration audit: 2026-04-20*

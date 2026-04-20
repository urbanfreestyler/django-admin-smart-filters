# Stack Research

**Domain:** Django Admin filtering framework library (async autocomplete + theme adapters)
**Researched:** 2026-04-20
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| Python | 3.12+ (target 3.12–3.14) | Runtime baseline for library + CI matrix | Django 6.0 supports Python 3.12–3.14; modern typing/perf and clean baseline for new package work. | HIGH |
| Django | 5.2 LTS baseline + test on 6.0.4 | Admin integration surface (`ModelAdmin`, `SimpleListFilter`, `autocomplete_fields`, templates) | 5.2 is LTS for long support; 6.0.4 is current latest stable. Build API against 5.2 contracts, verify forward-compat on 6.0. | HIGH |
| Django Admin built-ins (Select2 + admin templates) | bundled with Django 5.2/6.0 | Async autocomplete UX + extension points | `autocomplete_fields` already provides async Select2 behavior and permission checks. Overriding admin templates/blocks gives stable extension seam for theme adapters. | HIGH |
| asgiref | 3.11.1 | Safe sync/async boundary for endpoints and future async internals | Django’s official async adapter layer (`sync_to_async`, `async_to_sync`) avoids unsafe ORM usage in async contexts. | HIGH |

### Supporting Libraries

| Library | Version | Purpose | When to Use | Confidence |
|---------|---------|---------|-------------|------------|
| pytest | 9.0.3 | Core test runner | Always; base for unit + integration tests. | HIGH |
| pytest-django | 4.12.0 | Django-aware testing helpers | Always for admin integration tests and request/response fixtures. | HIGH |
| ruff | 0.15.11 | Lint + format in one fast tool | Always; replace Flake8/isort/Black stack for lower CI/tooling overhead. | HIGH |
| mypy | 1.20.1 | Static typing checks for library API stability | Use for public API and adapter contracts. | HIGH |
| django-stubs | 6.0.3 | Accurate Django typing + mypy plugin | Use with mypy for `ModelAdmin`/ORM typing precision. | HIGH |
| pre-commit | 4.5.1 | Local quality gate automation | Always; enforce ruff/mypy/pytest checks before commit. | HIGH |
| hatchling | 1.29.0 | Modern PEP 517 build backend for publishing | Use for packaging to PyPI with `pyproject.toml`; minimal, modern default. | HIGH |

### Development Tools

| Tool | Purpose | Notes | Confidence |
|------|---------|-------|------------|
| tox (or nox) | Multi-version test matrix | Run Django 5.2 + 6.0 and Python 3.12/3.13/3.14 in CI. | MEDIUM |
| GitHub Actions | CI for tests/lint/type checks | Standard for OSS Python libs; run matrix + wheel/sdist checks. | MEDIUM |

## Installation

```bash
# Runtime (library + Django admin integration)
pip install "Django>=5.2,<6.1" "asgiref>=3.11,<4"

# Dev/test/quality tooling
pip install -U pytest==9.0.3 pytest-django==4.12.0 ruff==0.15.11 mypy==1.20.1 "django-stubs[compatible-mypy]==6.0.3" pre-commit==4.5.1 hatchling==1.29.0
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Built-in Django admin Select2 autocomplete | `django-select2` | Use only if you need Select2 in non-admin app views too. For admin-only library, built-in is simpler and avoids duplicate JS stack. |
| Ruff-only lint/format | Black + isort + Flake8(+plugins) | Use legacy stack only if contributor base already standardized and migration cost is too high. |
| Hatchling | Setuptools | Use setuptools when you need legacy/plugin behaviors not supported by hatchling. |
| Theme adapter abstraction in your package | Hard-coding one admin skin (e.g., Jazzmin-first) | Only if product scope is intentionally single-theme and you accept lock-in. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Django < 5.2 | Unsupported/near-EOL baselines increase compatibility burden with little value for a greenfield library. | 5.2 LTS minimum, test 6.0 current stable. |
| Hard dependency on `django-select2` for admin autocomplete | Django admin already ships async Select2 for `autocomplete_fields`; external dependency duplicates capability and increases breakage risk. | Use native `autocomplete_fields` + custom admin JSON endpoints where needed. |
| Frontend SPA stack (React/Vue) for admin filters | Violates project constraint (lightweight, framework-agnostic), increases install and maintenance complexity for a library. | Progressive enhancement with small vanilla JS modules via admin Media/templates. |
| Theme-specific logic mixed into filter/query code | Causes rewrite risk when adding Jazzmin/Grappelli/default-admin support. | Adapter layer that maps one UI contract to per-theme templates/classes. |
| Grappelli as primary compatibility target | Current docs indicate Grappelli 4.0.3 is Django 5.x-oriented; not best primary baseline if you want smooth 6.0 path. | Default Django admin as canonical baseline; ship Grappelli adapter as optional. |

## Stack Patterns by Variant

**If you want maximum long-term stability (recommended default):**
- Use Django 5.2 LTS as minimum supported version.
- Run compatibility tests on 5.2 and 6.0.
- Keep runtime deps minimal (`Django`, `asgiref`) and put theme adapters behind optional extras.

**If you need broad theme support early (Jazzmin/Grappelli):**
- Keep a strict adapter interface (`render`, `assets`, `class map`).
- Add adapters incrementally as extras (`[jazzmin]`, `[grappelli]`) rather than core dependency.
- Treat default Django admin templates as canonical behavior and test oracle.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Django 5.2.x | Python 3.10–3.14 | LTS line; safest baseline for external package adoption. |
| Django 6.0.4 | Python 3.12–3.14 | Current stable feature line; validate forward compatibility in CI. |
| pytest-django 4.12.0 | Django 4.2/5.1/5.2/6.0 (per classifiers) | Good fit for dual-track Django support. |
| django-stubs 6.0.3 | Django 5.0/5.1/5.2/6.0 (per classifiers) | Use `compatible-mypy` extra to reduce plugin/version drift. |

## Sources

- https://www.djangoproject.com/download/ — verified current releases and support windows (HIGH)
- https://docs.djangoproject.com/en/6.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.autocomplete_fields — verified built-in async Select2 autocomplete behavior (HIGH)
- https://docs.djangoproject.com/en/6.0/ref/contrib/admin/filters/ — verified `SimpleListFilter` and filter extension mechanisms (HIGH)
- https://docs.djangoproject.com/en/6.0/ref/contrib/admin/javascript/ — verified admin JS customization extension points (HIGH)
- https://docs.djangoproject.com/en/6.0/topics/async/ — verified async boundaries and ORM caveats (HIGH)
- https://docs.djangoproject.com/en/6.0/faq/install/#what-python-version-can-i-use-with-django — verified Python compatibility matrix (HIGH)
- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ — verified modern `pyproject.toml`/build backend guidance (HIGH)
- https://pypi.org/pypi/Django/json — verified latest Django package version (HIGH)
- https://pypi.org/pypi/asgiref/json — verified asgiref latest version (HIGH)
- https://pypi.org/pypi/pytest/json — verified pytest latest version (HIGH)
- https://pypi.org/pypi/pytest-django/json — verified pytest-django latest version + classifiers (HIGH)
- https://pypi.org/pypi/ruff/json — verified ruff latest version (HIGH)
- https://pypi.org/pypi/mypy/json — verified mypy latest version (HIGH)
- https://pypi.org/pypi/django-stubs/json — verified django-stubs latest version + classifiers (HIGH)
- https://pypi.org/pypi/pre-commit/json — verified pre-commit latest version (HIGH)
- https://pypi.org/pypi/hatchling/json — verified hatchling latest version (HIGH)
- https://django-jazzmin.readthedocs.io/ and https://pypi.org/pypi/django-jazzmin/json — theme ecosystem reference (MEDIUM)
- https://django-grappelli.readthedocs.io/en/latest/ and https://pypi.org/pypi/django-grappelli/json — theme ecosystem reference + compatibility caveat (MEDIUM)

---
*Stack research for: Django Smart Filters (stack dimension)*
*Researched: 2026-04-20*

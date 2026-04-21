# Stack Research

**Domain:** Release-readiness stack for a Django Admin library package
**Researched:** 2026-04-21
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12+ (target CI: 3.12–3.14) | Packaging/build/test runtime baseline | Matches current Django 6.0 Python support and keeps release tooling modern and well-supported. |
| Django | 5.2 LTS minimum, test on 6.0.4 | Compatibility contract for your library | 5.2 gives stable long-support baseline; validating on 6.0 proves forward compatibility before first public release. |
| Hatchling (build backend) | 1.29.0 | Build backend in `pyproject.toml` (`[build-system]`) | Minimal PEP 517 backend, strong default for pure-Python libraries, and supports modern metadata flow. |
| PyPA build (build frontend) | 1.4.3 | Generate `sdist` and `wheel` artifacts (`python -m build`) | Officially recommended frontend in packaging docs; backend-agnostic and simple for CI. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| twine | 6.2.0 | Distribution checks and optional manual upload (`twine check`, `twine upload`) | Use `twine check --strict dist/*` in release CI even if publishing is automated via GitHub Action. |
| check-wheel-contents | 0.6.3 | Validate wheel content correctness | Use before publish to catch packaging mistakes (tests/docs accidentally included, invalid top-level entries, etc.). |
| towncrier | 25.8.0 | Changelog/release-notes generation from fragment files | Use for first public release to establish consistent, auditable changelog workflow. |
| validate-pyproject | 0.25 | Validate `pyproject.toml` metadata/schema | Run in CI to fail fast on malformed metadata before build/upload steps. |
| readme-renderer | 44.0 | Validate README rendering assumptions | Optional but useful if your README is complex and you want explicit pre-publish rendering validation. |
| pytest | 9.0.3 | Test runner for release gate | Always run as part of release pipeline. |
| pytest-django | 4.12.0 | Django-aware tests | Always for admin integration behavior checks. |
| ruff | 0.15.11 | Lint + format gate | Always in first-release quality gates. |
| mypy | 1.20.1 | Type gate for public API stability | Recommended for exported filter APIs and extension hooks. |
| django-stubs | 6.0.3 | Django typing support for mypy | Use with mypy to avoid false positives and improve confidence in typed public APIs. |
| pre-commit | 4.5.1 | Local reproducible checks | Use to ensure contributors run same lint/type/test checks as CI. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| GitHub Actions | CI quality gates + release orchestration | Split into “verify” workflow (PR/push) and “publish” workflow (tag push). |
| pypa/gh-action-pypi-publish (`release/v1`) | Trusted Publishing to PyPI/TestPyPI | Prefer OIDC Trusted Publishing over long-lived API tokens. |
| tox | 4.53.0 | Single command for local+CI matrix parity | Useful if you want predictable env orchestration across Python/Django matrix; optional but pragmatic for OSS libs. |

## Installation

```bash
# Runtime baseline (library support matrix)
pip install "Django>=5.2,<6.1" "asgiref>=3.11,<4"

# Packaging + release tooling
pip install -U hatchling==1.29.0 build==1.4.3 twine==6.2.0 check-wheel-contents==0.6.3 towncrier==25.8.0 validate-pyproject==0.25 readme-renderer==44.0

# Quality gates
pip install -U pytest==9.0.3 pytest-django==4.12.0 ruff==0.15.11 mypy==1.20.1 "django-stubs[compatible-mypy]==6.0.3" pre-commit==4.5.1 tox==4.53.0
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Hatchling + `python -m build` | Setuptools backend | Use setuptools if you need legacy setuptools-specific behavior/plugins already in your repo. |
| GitHub OIDC Trusted Publishing (`gh-action-pypi-publish`) | Twine upload in CI with API token secrets | Use Twine CI upload only if your target index cannot use Trusted Publishing. |
| Towncrier fragment-based changelog | Manual `CHANGELOG.md` editing | Use manual changelog only if maintainer team is very small and release cadence is low. |
| check-wheel-contents | Only smoke-install artifacts | Smoke install alone can miss malformed wheel structure/content errors; use-only-smoke-check is acceptable for very small internal packages. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Poetry/PDM/Hatch CLI migration for this milestone | Adds workflow churn not required for first release; scope is release readiness, not toolchain migration. | Keep existing workflow + add minimal packaging/release tools above. |
| `python setup.py sdist bdist_wheel` legacy build path | Deprecated/legacy pattern; bypasses modern isolated build assumptions. | `python -m build` with `pyproject.toml`. |
| Long-lived PyPI API tokens in repo secrets (when GitHub OIDC available) | Higher secret leakage risk and operational overhead. | Trusted Publishing via `pypa/gh-action-pypi-publish`. |
| Semantic-release automation for first release | Premature complexity for a first public cut; requires commit-discipline/process changes. | Explicit version bump + Towncrier-generated changelog + tagged release. |
| cibuildwheel right now | Your library is Django/pure-Python; no binary wheels needed for first release. | Build universal wheel + sdist via `python -m build`. |

## Stack Patterns by Variant

**If you want the leanest first-release process (recommended):**
- `hatchling + build + twine(check) + check-wheel-contents + towncrier`
- GitHub Actions for verify/publish, Trusted Publishing to TestPyPI/PyPI
- Explicit manual version bump in `pyproject.toml` + release tag

**If you need stricter enterprise gates from day one:**
- Add `validate-pyproject` and required branch checks
- Require TestPyPI publish + install/import smoke job before PyPI publish approval
- Keep `twine check --strict` and wheel-content checks mandatory

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Django 5.2.x | Python 3.10–3.14 | Release baseline target remains 5.2+ for broad adoption. |
| Django 6.0.4 | Python 3.12–3.14 | Validate forward compatibility in CI matrix before public release. |
| pytest-django 4.12.0 | Django 4.2/5.1/5.2/6.0 (classifiers) | Confirms suitability for your target matrix. |
| django-stubs 6.0.3 | Django 5.0/5.1/5.2/6.0 (classifiers) | Good fit for type-gating public Django integration APIs. |

## Release Integration Points (first-release scope)

1. **`pyproject.toml`**
   - Add `[build-system]` with `hatchling`.
   - Ensure complete `[project]` metadata: name, version, description, readme, requires-python, license/license-files, classifiers, URLs.
2. **Artifact validation step**
   - `python -m build`
   - `twine check --strict dist/*`
   - `check-wheel-contents dist/*.whl`
   - clean venv install/import smoke test from wheel.
3. **Changelog/release notes**
   - Add Towncrier fragments and render changelog at release cut.
4. **CI quality gate**
   - Required: `ruff`, `mypy`, `pytest`, packaging validation, artifact validation.
5. **Publishing workflow**
   - Use GitHub Actions + `pypa/gh-action-pypi-publish@release/v1` with Trusted Publishing.
   - TestPyPI first; PyPI publish on signed/tagged release flow.

## Sources

- https://packaging.python.org/en/latest/tutorials/packaging-projects/ — official build/upload flow (`build`, `twine`, sdist+wheel) (HIGH)
- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ — current `pyproject.toml`/`[build-system]` and metadata guidance (HIGH)
- https://packaging.python.org/en/latest/specifications/core-metadata/ — current core metadata spec (v2.5) and deprecations (HIGH)
- https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/ — Trusted Publishing workflow guidance (HIGH)
- https://twine.readthedocs.io/en/stable/ — `twine check`/upload behavior and CLI options (HIGH)
- https://pypi.org/pypi/hatchling/json — latest hatchling version (HIGH)
- https://pypi.org/pypi/build/json — latest build version (HIGH)
- https://pypi.org/pypi/twine/json — latest twine version (HIGH)
- https://pypi.org/pypi/towncrier/json — latest towncrier version (HIGH)
- https://pypi.org/pypi/check-wheel-contents/json — latest check-wheel-contents version (HIGH)
- https://pypi.org/pypi/validate-pyproject/json — latest validate-pyproject version (HIGH)
- https://pypi.org/pypi/readme-renderer/json — latest readme-renderer version (HIGH)
- https://pypi.org/pypi/pytest/json — latest pytest version (HIGH)
- https://pypi.org/pypi/pytest-django/json — latest pytest-django version (HIGH)
- https://pypi.org/pypi/ruff/json — latest ruff version (HIGH)
- https://pypi.org/pypi/mypy/json — latest mypy version (HIGH)
- https://pypi.org/pypi/django-stubs/json — latest django-stubs version (HIGH)
- https://pypi.org/pypi/pre-commit/json — latest pre-commit version (HIGH)
- https://pypi.org/pypi/tox/json — latest tox version (HIGH)

---
*Stack research for: Django Smart Filters (release-readiness stack)*
*Researched: 2026-04-21*

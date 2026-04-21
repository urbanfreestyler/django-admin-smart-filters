# Architecture Research

**Domain:** Django reusable admin library release-readiness architecture
**Researched:** 2026-04-21
**Confidence:** HIGH

## Standard Architecture

### System Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                        Source & Runtime Layer                               │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────┐  ┌──────────────────────┐  ┌───────────────────┐ │
│  │ django_admin_* package│  │ templates/static      │  │ docs examples     │ │
│  │ (public API + logic)  │  │ (packaged assets)     │  │ (import snippets) │ │
│  └────────────┬──────────┘  └────────────┬─────────┘  └─────────┬─────────┘ │
│               │                          │                      │           │
├───────────────┴──────────────────────────┴──────────────────────┴───────────┤
│                         Packaging & Metadata Layer                            │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────────┐ │
│  │ pyproject.toml      │  │ README/CHANGELOG    │  │ MANIFEST/build config│ │
│  │ (build + metadata)  │  │ (PyPI rendering)    │  │ (template/static incl)| │
│  └────────────┬────────┘  └────────────┬────────┘  └───────────┬──────────┘ │
│               │                        │                        │           │
├───────────────┴────────────────────────┴────────────────────────┴───────────┤
│                        Verification & Delivery Layer                          │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐ │
│  │ local quality gates │  │ CI matrix + artifacts│  │ publish workflow     │ │
│  │ (ruff/mypy/pytest)  │  │ (wheel/sdist checks) │  │ (trusted publisher)  │ │
│  └─────────────────────┘  └──────────────────────┘  └──────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Runtime package (`django_admin_smart_filters/`) | Stable import/runtime API and admin integration behavior | Existing modules (`admin.py`, `declarations.py`, `query.py`, etc.) plus packaged templates/static |
| Packaging metadata | Define install/build identity and compatibility | `pyproject.toml` (`[build-system]`, `[project]`, dependencies, classifiers, URLs) |
| Distribution file selection | Ensure templates/static/docs/license are included in sdist/wheel correctly | Build backend include rules (`tool.hatch.build...`) and optional `MANIFEST.in` fallback |
| Docs surface | PyPI-facing install/usage and release history | Root `README.md`, `CHANGELOG.md`, `docs/` references |
| Quality gate runner | Prevent shipping broken/undocumented artifacts | Pre-commit + CI steps for `ruff`, `mypy`, `pytest`, docs snippet compile/exec tests |
| Artifact validation | Verify installability and importability of built files (not just source tree) | `python -m build`, `twine check dist/*`, clean-venv `pip install dist/*.whl` smoke imports |
| Release automation | Publish only verified artifacts with minimal credential risk | GitHub Actions + PyPI Trusted Publisher (`pypa/gh-action-pypi-publish`) |

## Recommended Project Structure

```text
django-admin-enhanced-filters/
├── django_admin_smart_filters/              # Runtime package (already exists)
│   ├── static/django_admin_smart_filters/   # JS assets (must ship in wheel)
│   └── templates/admin/django_admin_smart_filters/
├── tests/                                   # Unit/integration/docs tests (already exists)
├── docs/                                    # User docs (already exists)
├── pyproject.toml                           # NEW: canonical build + metadata config
├── README.md                                # NEW: PyPI long description entry point
├── CHANGELOG.md                             # NEW: release notes and version history
├── LICENSE                                  # NEW: explicit OSS licensing for redistribution
├── .pre-commit-config.yaml                  # NEW: reproducible local quality gate
├── .github/workflows/
│   ├── ci.yml                               # NEW: matrix test/lint/type + build verify
│   └── publish.yml                          # NEW: trusted publish from tags/releases
└── .gitignore                               # MOD: ignore build/release artifacts (dist/, build/, *.egg-info/)
```

### Structure Rationale

- **Keep runtime package unchanged as release unit**: architecture already cleanly layered; release prep should add packaging/verification around it, not refactor internals.
- **Make `pyproject.toml` the single source of release truth**: dependencies, Python/Django compatibility, package data inclusion, and tool config should converge there.
- **Separate CI (`ci.yml`) from publish (`publish.yml`)**: prevents accidental releases and enforces “build once, publish verified artifact.”

## Architectural Patterns

### Pattern 1: Build-from-Artifact, not Build-from-Source-Assumption

**What:** Validate the produced wheel/sdist in a clean environment.
**When to use:** Always before first public release and for every tagged release.
**Trade-offs:** Slightly slower pipeline, much lower risk of missing files or broken metadata.

**Example:**
```bash
python -m build
python -m twine check dist/*
python -m pip install --force-reinstall dist/*.whl
python -c "import django_admin_smart_filters as pkg; print(pkg.__all__)"
```

### Pattern 2: Source Name / Distribution Name Contract

**What:** Explicitly manage the rename boundary: distribution name on PyPI vs import package path.
**When to use:** Required now due to in-progress namespace rename noted in project context.
**Trade-offs:** Needs explicit docs/tests, but avoids user-facing import confusion.

**Example:**
```toml
[project]
name = "django-admin-smart-filters"  # distribution name

# tests/docs must consistently import:
# from django_admin_smart_filters import ...
```

### Pattern 3: Dual Gate Pipeline (Quality Gate + Release Gate)

**What:** CI runs full checks on pushes/PRs; publish runs only from immutable release refs and only after build job success.
**When to use:** Standard for package reliability and supply-chain hygiene.
**Trade-offs:** More workflow files, but clearer operational safety.

## Data Flow

### Request Flow (Release Prep Capability Flow)

```text
[Code/docs change]
    ↓
[Local gate: pre-commit + pytest]
    ↓
[CI gate: lint/type/test matrix]
    ↓
[Build artifacts: sdist + wheel]
    ↓
[Artifact validation: twine check + install/import smoke]
    ↓
[Tag/release event]
    ↓
[Trusted publisher uploads already-verified artifacts]
```

### State Management

```text
pyproject.toml = canonical package state
    ↓
CI reads same config for lint/type/test/build
    ↓
dist/* artifacts represent release state
    ↓
CHANGELOG.md + Git tag represent public version state
```

### Key Data Flows

1. **Metadata flow:** `pyproject.toml` -> wheel/sdist metadata -> PyPI project page fields.
2. **Asset inclusion flow:** `django_admin_smart_filters/templates|static` -> build backend inclusion -> import/runtime render correctness.
3. **Docs correctness flow:** docs snippets -> `tests/test_docs_examples.py` -> release docs confidence.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1 maintainer, early releases | Single CI workflow + manual release tags is sufficient |
| Multiple maintainers, regular patch releases | Enforce required checks, protected release tags, and Trusted Publishing only |
| High adoption / frequent releases | Add stricter matrix (Django 5.2 + 6.0, Python 3.12–3.14), changelog automation, and release candidate TestPyPI lane |

### Scaling Priorities

1. **First bottleneck:** namespace/metadata drift (`django_smart_filters` vs `django_admin_smart_filters`) across docs/planning/release files.
2. **Second bottleneck:** missing packaged non-Python assets (templates/static) only discovered post-release.

## Anti-Patterns

### Anti-Pattern 1: “Tests pass in repo, therefore release is safe”

**What people do:** Run `pytest` only, skip build/install validation.
**Why it's wrong:** Does not verify wheel/sdist completeness or metadata rendering.
**Do this instead:** Add explicit artifact validation stage (`build`, `twine check`, clean install/import smoke).

### Anti-Pattern 2: Publishing with long-lived API token in CI secrets

**What people do:** Store account-wide token indefinitely in CI.
**Why it's wrong:** Larger blast radius if compromised.
**Do this instead:** Use PyPI Trusted Publisher (OIDC) with short-lived minted upload tokens.

### Anti-Pattern 3: Mixing release files into runtime module decisions

**What people do:** Refactor runtime internals while adding packaging/CI in same milestone.
**Why it's wrong:** Expands risk surface and delays release.
**Do this instead:** Keep this milestone architectural scope to packaging + gates + docs + artifact verification.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| GitHub Actions | CI + artifact build + gated publish jobs | Use separate `ci.yml` and `publish.yml` with publish depending on build artifacts |
| PyPI/TestPyPI | Twine/gh-action upload target | Prefer Trusted Publishing over static API tokens |
| Packaging toolchain (`build`, `twine`) | CLI validation in CI and local release scripts | `twine check` catches README rendering errors early |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `pyproject.toml` ↔ runtime package dir | package include config + import path | Must explicitly include templates/static to avoid runtime template failures |
| `docs/` ↔ `tests/test_docs_examples.py` | executable snippet validation | Existing test file is a strong release-readiness gate; keep it in CI |
| `requirements-dev.txt` ↔ CI steps | dev dependency installation | Maintain alignment; avoid duplicated divergent tool pins |
| Namespace rename context ↔ docs/planning files | text references/import examples | Update stale `django_smart_filters` references before release to prevent onboarding errors |

## New vs Modified Components (Release Prep)

### New files/components

- `pyproject.toml` (build system + project metadata + tool config)
- `README.md` (PyPI long description entry)
- `CHANGELOG.md` (versioned release history)
- `LICENSE` (redistribution/legal requirement)
- `.pre-commit-config.yaml` (local gate automation)
- `.github/workflows/ci.yml` (quality + artifact validation)
- `.github/workflows/publish.yml` (trusted publish)

### Modified existing files/components

- `.gitignore` -> add `dist/`, `build/`, `*.egg-info/`, `.mypy_cache/`, `.ruff_cache/`
- `requirements-dev.txt` -> add `build`, `twine` (and optional `tox`/`nox` if used)
- `docs/project_description.md` + docs examples -> ensure package name/import paths and install instructions reflect release name
- `.planning/codebase/*.md` where stale `django_smart_filters` naming appears (to avoid internal drift)
- `django_admin_smart_filters/__init__.py` (only if version export strategy is adopted)

## Suggested Build Order (Dependency-Driven)

1. **Stabilize naming contract (import vs distribution) + docs alignment**
   - Fixes highest confusion risk before any metadata is frozen.

2. **Add `pyproject.toml` with complete metadata + package data rules**
   - Foundation for all subsequent CI/build work.

3. **Add release docs surface (`README.md`, `CHANGELOG.md`, `LICENSE`)**
   - Required for valid, user-facing artifacts and PyPI rendering.

4. **Add local and CI quality gates (`pre-commit`, `ci.yml`)**
   - Must pass before publish automation is enabled.

5. **Add artifact validation stage (`build` + `twine check` + smoke install/import)**
   - Ensures generated artifacts are truly releasable.

6. **Add publish workflow with Trusted Publisher (`publish.yml`)**
   - Final step after all quality and artifact checks are proven green.

7. **Run dry-run release to TestPyPI (optional but recommended)**
   - Final confidence step before first public PyPI release.

## Sources

- Python Packaging User Guide — writing `pyproject.toml`: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ (HIGH)
- Python Packaging User Guide — packaging projects/tutorial (`python -m build`, dist flow): https://packaging.python.org/en/latest/tutorials/packaging-projects/ (HIGH)
- Python Packaging User Guide — GitHub Actions publishing guide (trusted publishing patterns): https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/ (HIGH)
- GitHub Docs — building/testing Python workflows and matrix patterns: https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python (HIGH)
- Twine docs (`twine check`, upload behavior): https://twine.readthedocs.io/en/stable/ (HIGH)
- PyPI help — API tokens and trusted publisher recommendation: https://pypi.org/help/#apitoken (HIGH)
- PyPI Docs — Trusted Publishers model and short-lived tokens: https://docs.pypi.org/trusted-publishers/ (HIGH)
- Django docs — reusable app packaging expectations including templates/static handling and `MANIFEST.in` context: https://docs.djangoproject.com/en/6.0/intro/reusable-apps/ (HIGH)
- Repository evidence (`.planning/PROJECT.md`, `.planning/codebase/*`, `requirements-dev.txt`, `tests/test_docs_examples.py`) (HIGH)

---
*Architecture research for: Django Smart Filters release readiness*
*Researched: 2026-04-21*

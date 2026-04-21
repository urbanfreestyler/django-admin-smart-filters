# Feature Research

**Domain:** Python package release-readiness milestone (existing Django admin library)
**Researched:** 2026-04-21
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features maintainers and early adopters expect before a first public PyPI release.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Complete `pyproject.toml` metadata (name/version/description/readme/license/requires-python/dependencies/URLs/classifiers) | PyPI package pages and installers depend on valid metadata; missing metadata makes package look incomplete or fail policy checks | MEDIUM | Align distribution name with import package rename (`django_admin_smart_filters`) and ensure metadata fields are PEP 621/core-metadata compliant. |
| Build both `sdist` and wheel (`python -m build`) | PyPA guidance expects both archives for normal releases; users expect fast wheel installs with sdist fallback | LOW | Must verify both artifacts are generated on clean environment. |
| Artifact validation gates (`twine check`, install/import smoke test) | First release failures are often metadata/README/rendering/import-path mistakes | LOW | `twine check` validates long description; smoke test should install built wheel and import public package entrypoints. |
| Reproducible quality gate (tests + lint + typing in CI) | Consumers expect baseline stability from v1 packages, not “works on maintainer machine” releases | MEDIUM | Gate on existing project checks: pytest, ruff, mypy/django-stubs (if enabled in stack). |
| TestPyPI dry run before production publish | Standard safe first-release workflow to catch upload/auth/index issues without polluting real PyPI | LOW | Upload to TestPyPI, then verify install from TestPyPI index. |
| Secure publishing path (Trusted Publishing or scoped API token) | PyPI ecosystem now treats token hygiene as baseline release practice | MEDIUM | Prefer Trusted Publishing (OIDC short-lived creds) over long-lived secrets in CI. |
| Release docs bundle (install/quickstart/changelog/release notes) | First-time adopters need immediate “can I install and use this?” confidence | MEDIUM | Changelog + “what’s stable in v1.1” should reflect release-readiness scope (no net-new filter features). |

### Differentiators (Competitive Advantage)

Release features that go beyond minimum “can upload package” behavior.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Automated tag-driven release workflow (build once, publish artifacts) | Eliminates manual release drift and makes releases repeatable/auditable | MEDIUM | GitHub Actions pattern: build job -> artifact store -> publish jobs. |
| Trusted Publishing + environment approvals | Strong security posture for OSS package consumers and maintainers | MEDIUM | PyPI OIDC tokens are short-lived; add manual approval on production `pypi` environment. |
| Release readiness checklist command/doc in repo | Reduces maintainer cognitive load and onboarding friction | LOW | One command path for local “preflight”: clean build, checks, smoke test, TestPyPI upload. |
| Post-upload verification script (fresh venv install + example import) | Quickly detects broken distribution metadata/import path after publish | LOW | Especially useful during package namespace rename transition. |
| Compatibility badge matrix (Python/Django support) in README | Improves trust and discoverability for Django teams evaluating package fit | LOW | Should match tested matrix from CI, not aspirational claims. |

### Anti-Features (Commonly Requested, Often Problematic)

Scope that looks useful but usually harms first-release success.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Shipping net-new filter capabilities in release-readiness milestone | “Make launch bigger/more exciting” | Mixes product work with packaging risk; delays release and complicates regression triage | Freeze feature surface; ship reliability/packaging milestone only |
| Custom release CLI/orchestration framework | “One tool to do everything” | Over-engineering for first release; adds maintenance burden before proving need | Use standard PyPA tools (`build`, `twine`) + lightweight scripts |
| Long-lived PyPI tokens in repo secrets as default | Quick setup convenience | Higher compromise blast radius than OIDC trusted publishing | Prefer Trusted Publishing; fallback to scoped tokens only if needed |
| Multi-index publish complexity on day one (mirrors/private registries/extra repos) | “Future-proofing” | Adds failure modes unrelated to initial public release goal | Start with TestPyPI + PyPI only, then expand |
| “Auto-fix metadata” at release time | Reduce manual edits | Hidden mutation during release makes provenance harder and can ship unexpected metadata | Keep metadata explicit in VCS; release pipeline verifies, not rewrites |

## Feature Dependencies

```text
Existing stable library behavior (v1.0 phases complete)
    └──requires──> release-readiness scope freeze

Package namespace rename finalization (`django_admin_smart_filters`)
    └──requires──> metadata + import-path alignment
                        └──requires──> install/import smoke tests

Build artifacts (`sdist` + wheel)
    └──requires──> valid `pyproject.toml`
                        └──requires──> `twine check` + TestPyPI upload

Production publish
    └──requires──> CI quality gates passing
    └──requires──> secure auth path (Trusted Publishing preferred)

Release documentation
    └──requires──> final package name/version + validated install commands
```

### Dependency Notes

- **Scope freeze before packaging:** if feature work continues during release hardening, failures become hard to attribute.
- **Rename alignment is critical:** distribution name, import package, docs examples, and smoke tests must all agree.
- **CI gates precede publishing:** publishing without deterministic tests/lint/type checks turns PyPI into test environment.
- **TestPyPI precedes PyPI:** catches auth and metadata rendering issues with low risk.
- **Docs depend on tested commands:** installation snippets must be copied from verified flows, not assumptions.

## MVP Definition

### Launch With (v1.1 release-readiness milestone)

- [ ] Finalized `pyproject.toml` metadata and version baseline — essential for valid distribution identity.
- [ ] Deterministic build of `sdist` + wheel — required for distribution delivery.
- [ ] `twine check` + clean-venv install/import smoke test — essential release safety net.
- [ ] CI gate for tests/lint/type checks — baseline quality contract for first public package.
- [ ] TestPyPI rehearsal + production publishing path docs — de-risk first PyPI publish.
- [ ] Release notes/changelog/install docs updated for renamed package namespace — reduce adopter confusion.

### Add After Validation (v1.x)

- [ ] Fully automated tag->publish workflow with environment approvals — add after first manual/semimanual release succeeds.
- [ ] Signed provenance/attestation enhancements beyond defaults — add once baseline release pipeline is stable.
- [ ] Automated release-note generation from conventional commits/labels — optimize once cadence increases.

### Future Consideration (v2+)

- [ ] Multi-registry publication strategy (private mirrors/internal index) — only after clear enterprise demand.
- [ ] Advanced supply-chain hardening expansions (beyond Trusted Publishing defaults) — phase in with maintainer capacity.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Valid package metadata (`pyproject.toml`) | HIGH | MEDIUM | P1 |
| Build + artifact validation (`sdist`/wheel + `twine check`) | HIGH | LOW | P1 |
| CI quality gates for release | HIGH | MEDIUM | P1 |
| TestPyPI rehearsal + smoke install | HIGH | LOW | P1 |
| Secure publish auth (Trusted Publishing) | HIGH | MEDIUM | P1 |
| Automated tag-driven publish workflow | MEDIUM | MEDIUM | P2 |
| Release checklist automation | MEDIUM | LOW | P2 |
| Multi-index publishing support | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor/Standard Practice Analysis

| Release Practice | Typical Ecosystem Baseline | Our Approach |
|------------------|----------------------------|--------------|
| Metadata declaration | PEP 621 `pyproject.toml` with complete project metadata | Enforce complete static metadata, aligned with rename and Django support policy |
| Build/publish tooling | `python -m build` + `twine`/PyPI publish action | Keep standard PyPA toolchain; avoid custom release framework |
| Pre-production validation | TestPyPI upload + install verification | Mandatory rehearsal before first real PyPI release |
| CI publishing auth | Trusted Publishing increasingly recommended | Prefer OIDC trusted publishing with approvals for production release |

## Sources

- PyPA tutorial: packaging projects (build artifacts, upload/test flow) (HIGH): https://packaging.python.org/en/latest/tutorials/packaging-projects/
- PyPA guide: writing `pyproject.toml` / PEP 621 metadata fields (HIGH): https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- PyPA guide: using TestPyPI (HIGH): https://packaging.python.org/en/latest/guides/using-testpypi/
- PyPA guide: publishing with GitHub Actions + trusted publishing workflow (HIGH): https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
- PyPI docs: trusted publishers / OIDC security model (HIGH): https://docs.pypi.org/trusted-publishers/
- Twine docs (`twine check`, upload behavior, security rationale) (HIGH): https://twine.readthedocs.io/en/stable/
- PyPA core metadata specification (v2.5, Sept 2025) (HIGH): https://packaging.python.org/en/latest/specifications/core-metadata/

---
*Feature research for: first package release readiness milestone*
*Researched: 2026-04-21*

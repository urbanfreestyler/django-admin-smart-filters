# Pitfalls Research

**Domain:** First-release readiness for a Django reusable package (existing codebase, packaging + publication integration)
**Researched:** 2026-04-21
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Distribution name and import package drift during namespace rename

**What goes wrong:**
Package uploads as one name, docs reference another, and users cannot import after install (`pip install` succeeds but `import ...` fails or docs are wrong).

**Why it happens:**
Teams conflate distribution name (PyPI project) with import package name, especially during late rename work.

**How to avoid:**
- Freeze naming decisions before artifact build: distribution name, import path, and app label.
- Add release smoke test that does: fresh venv install from wheel + `python -c "import django_admin_smart_filters"`.
- Update install docs and examples from the same source of truth.

**Warning signs:**
- README says one install command but tests import a different module.
- Package name appears in multiple variants (`-`, `_`, old namespace) across docs/config.
- Rename PRs touch code/docs but not release checks.

**Phase to address:**
Phase 1 (packaging metadata baseline) and Phase 2 (artifact validation).

---

### Pitfall 2: Templates/static files missing from wheel/sdist

**What goes wrong:**
Library works from repo checkout but installed package has missing admin templates/JS/CSS, causing runtime template-not-found or broken UI behavior.

**Why it happens:**
Python module files are included, but package data rules are incomplete/misconfigured.

**How to avoid:**
- Explicitly configure package data inclusion for `templates/` and `static/`.
- Test both built artifacts (`sdist`, `wheel`), not just editable install.
- Add CI assertion that artifact file list contains expected template/static paths.

**Warning signs:**
- UI tests pass locally but fail after `pip install dist/*.whl`.
- `TemplateDoesNotExist` appears only in installed-package tests.
- Dist artifact size unexpectedly small after packaging changes.

**Phase to address:**
Phase 2 (build and artifact integrity).

---

### Pitfall 3: Editable install masks packaging defects

**What goes wrong:**
Release is shipped with missing files or bad metadata because validation only used `pip install -e .`.

**Why it happens:**
Editable mode reads directly from working tree and can hide distribution packaging errors.

**How to avoid:**
- Make wheel/sdist install smoke checks mandatory in CI.
- Run smoke tests in clean environment without source tree on `PYTHONPATH`.
- Gate release on built-artifact tests only.

**Warning signs:**
- Team repeatedly says “works in editable mode.”
- No test stage that installs from `dist/` files.
- Bugs reproduced only by downstream users, not maintainers.

**Phase to address:**
Phase 2 (artifact validation) and Phase 3 (CI quality gates).

---

### Pitfall 4: Incomplete or misleading core metadata

**What goes wrong:**
Users install incompatible versions or cannot evaluate project quality because `requires-python`, classifiers, project URLs, or license/readme metadata are wrong.

**Why it happens:**
Metadata is treated as “form-filling” instead of an install/runtime contract.

**How to avoid:**
- Validate `[project]` metadata fields as part of release checklist.
- Align `requires-python` with tested matrix and documented support policy.
- Ensure `readme` renders and URLs are valid.

**Warning signs:**
- CI matrix and `requires-python` disagree.
- Missing/placeholder project URLs.
- PyPI page rendering issues after test upload.

**Phase to address:**
Phase 1 (metadata baseline) and Phase 4 (publication rehearsal).

---

### Pitfall 5: Version source ambiguity (multiple truths)

**What goes wrong:**
Tag, changelog, package metadata, and module `__version__` disagree; wrong version gets published or tagged.

**Why it happens:**
No single-source version policy before first release automation.

**How to avoid:**
- Declare one version authority (static in `pyproject.toml` or controlled dynamic source).
- Add CI guard that version in artifacts matches release tag intent.
- Include pre-release check for changelog/version coherence.

**Warning signs:**
- Release PR includes manual updates in 2–4 places.
- Maintainers ask “which version is canonical?”
- Built filename version differs from release notes draft.

**Phase to address:**
Phase 1 (versioning baseline) and Phase 3 (release gate automation).

---

### Pitfall 6: Runtime dependency leakage from dev environment

**What goes wrong:**
Package imports pass in development but fail for users because transitive dev-only dependencies were never declared in runtime dependencies.

**Why it happens:**
Local env contains extra packages from test/lint tooling; release artifacts are never tested in minimal env.

**How to avoid:**
- Separate runtime vs dev dependencies strictly.
- Smoke-test import and minimal usage in fresh env with only installed artifact dependencies.
- Add negative test to ensure optional features fail with clear message unless extras installed.

**Warning signs:**
- `ModuleNotFoundError` reported by users for packages not in runtime deps.
- Requirements files differ from declared package dependencies.
- Tests only run in one pre-loaded dev container.

**Phase to address:**
Phase 2 (artifact smoke tests) and Phase 3 (CI matrix hardening).

---

### Pitfall 7: Build isolation and reproducibility not enforced

**What goes wrong:**
Release builds pass on maintainer machine but fail in CI or for downstream rebuilds due to undeclared build requirements or environment-sensitive outputs.

**Why it happens:**
Build backend/tooling assumptions are implicit; reproducibility controls are not tested.

**How to avoid:**
- Use standards-compliant isolated builds (`python -m build`) in CI.
- Keep `[build-system]` explicit and minimal.
- Rebuild artifacts in clean runner and compare expected structure/checks.

**Warning signs:**
- “Works on my machine” build failures.
- Missing build dependency errors in CI only.
- Artifact contents vary unexpectedly between runs.

**Phase to address:**
Phase 2 (build pipeline) and Phase 3 (CI reproducibility checks).

---

### Pitfall 8: Upload credentials and release auth model are insecure

**What goes wrong:**
Long-lived PyPI tokens are over-scoped, leaked, or manually pasted; compromise risk is high for first automation setup.

**Why it happens:**
Teams optimize for speed and skip trusted publishing/OIDC setup.

**How to avoid:**
- Prefer PyPI Trusted Publishing (OIDC) for CI release jobs.
- If tokens are temporarily required, scope minimally and rotate.
- Prohibit token use in local scripts/docs examples.

**Warning signs:**
- Tokens stored in plaintext docs or repository secrets with broad scope.
- Manual maintainer uploads as default path.
- No documented auth rotation/revocation process.

**Phase to address:**
Phase 4 (publication security and auth).

---

### Pitfall 9: No TestPyPI rehearsal, then immutable release collision

**What goes wrong:**
First upload fails late (bad metadata, broken README, existing file/version conflicts). Team burns release number and scrambles.

**Why it happens:**
PyPI release immutability constraints not rehearsed with full artifact flow.

**How to avoid:**
- Run full dry-run on TestPyPI before production publish.
- Add `twine check` and artifact install verification before upload.
- Treat version number as immutable once publish job starts.

**Warning signs:**
- First real PyPI publish is first time upload flow is executed.
- No documented fallback when upload partially fails.
- Release checklist has no TestPyPI step.

**Phase to address:**
Phase 4 (publication rehearsal).

---

### Pitfall 10: Missing post-release correction path (yank policy)

**What goes wrong:**
Broken release remains active too long because maintainers have no agreed response (yank, follow-up patch, communication plan).

**Why it happens:**
Teams plan happy-path release only, not failure containment.

**How to avoid:**
- Define explicit incident runbook: detect → decide yank → patch release.
- Document yanking criteria (broken/uninstallable/security).
- Add communication template for release notes/issues.

**Warning signs:**
- Maintainers debate process during incident.
- No one knows who can yank releases.
- Broken version remains current for hours/days.

**Phase to address:**
Phase 5 (release operations + post-release governance).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| “We’ll package files later” (no explicit data-file rules) | Faster milestone close | Installed package breaks in production | Never for release milestone |
| Manual one-off release commands | Fast first publish | Non-reproducible process, bus-factor risk | Only for internal pre-release smoke |
| Reusing broad personal API token in CI | Easy setup | High account/project compromise blast radius | Never; migrate to trusted publishing |
| Skipping TestPyPI rehearsal | Saves one step | First real publish becomes integration test | Never for first public release |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Build backend (`pyproject.toml`) | Undeclared/implicit build requirements | Keep `[build-system]` explicit and validated in isolated CI builds |
| Django reusable app packaging | Forgetting to include templates/static in artifacts | Add explicit package-data rules and artifact-content checks |
| PyPI upload | Direct production upload without `twine check`/dry-run | Use TestPyPI rehearsal + metadata rendering check + install smoke tests |
| CI release auth | Long-lived API token secrets | Use Trusted Publishing (OIDC) and short-lived credentials |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Full test suite only after upload step | Slow feedback, late failures | Reorder pipeline: lint/type/test/build/check before publish | Any project; painful on first release |
| Rebuilding environment per job without cache strategy | Long release pipeline timeouts | Use deterministic lock/constraints + CI caching policy | Moderate-to-large CI matrices |
| Re-running heavyweight integration tests for docs-only release PRs | Release prep drags | Use path-based CI job selection while preserving release gate jobs | As repo/test surface grows |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Storing PyPI token in plaintext or shell history | Account/package takeover | Use CI secret store + non-interactive upload flow or OIDC trusted publishing |
| Over-scoped credentials across multiple projects | Cross-project blast radius | Scope creds to project/repository and rotate on schedule |
| Missing 2FA/recovery setup for maintainers | Maintainer lockout or account hijack risk | Enforce maintainer account hygiene and backup owner policy |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Sparse install docs for reusable app | New users fail first setup | Publish explicit install + `INSTALLED_APPS` + minimal integration snippet |
| Changelog not aligned with release contents | Users cannot assess upgrade risk | Keep changelog section tied to artifact version before publish |
| Hidden compatibility policy | Consumers choose unsupported Python/Django combos | Put support matrix in README and classifiers/requires-python |

## "Looks Done But Isn't" Checklist

- [ ] **Metadata complete:** `name`, `version`, `requires-python`, license, URLs, classifiers align with tested policy.
- [ ] **Artifact integrity:** wheel and sdist both contain Python modules + templates + static assets.
- [ ] **Install smoke checks:** clean venv install from wheel and sdist, then import and minimal admin integration pass.
- [ ] **Upload rehearsal:** `twine check` passes and TestPyPI dry-run has been validated.
- [ ] **Auth hardening:** trusted publishing configured (or temporary scoped token plan documented).
- [ ] **Recovery path:** yank/patch process documented with owners and triggers.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Missing package data in release | HIGH | Yank broken release, patch file-inclusion config, rebuild, republish with new version |
| Name/import mismatch | HIGH | Update docs + metadata + import path shims if needed, cut corrective release |
| Bad metadata/readme on PyPI | MEDIUM | Fix metadata source, verify with `twine check`, publish next patch release |
| Credential exposure | HIGH | Revoke credential immediately, rotate secrets, audit recent uploads, migrate to OIDC |
| Broken compatibility declaration | MEDIUM-HIGH | Correct `requires-python`/classifiers, publish fixed release, note incompatibility in changelog |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Name/import drift | Phase 1 + 2 | Install/import smoke tests from built artifacts pass |
| Missing templates/static in artifacts | Phase 2 | Artifact file-list assertions + runtime template load tests pass |
| Editable-install masking defects | Phase 2 + 3 | CI gates install from wheel/sdist only for release checks |
| Incomplete metadata | Phase 1 + 4 | Metadata checklist + `twine check` + TestPyPI rendering verification |
| Version source ambiguity | Phase 1 + 3 | Version consistency checks across tag/artifact/changelog pass |
| Runtime dependency leakage | Phase 2 + 3 | Fresh-env smoke tests pass with only declared runtime deps |
| Non-reproducible builds | Phase 2 + 3 | Isolated `python -m build` in CI is deterministic and green |
| Insecure upload auth | Phase 4 | Trusted publishing workflow succeeds without long-lived token |
| No publish rehearsal | Phase 4 | TestPyPI dry-run and install verification completed before prod publish |
| No yank runbook | Phase 5 | Incident drill/checklist exists and ownership assigned |

## Sources

- Python Packaging User Guide — Packaging projects tutorial (build/upload/install flow): https://packaging.python.org/en/latest/tutorials/packaging-projects/ (**HIGH**)
- Python Packaging User Guide — Writing `pyproject.toml` (metadata/build-system requirements): https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ (**HIGH**)
- Python Packaging spec — Names and normalization (distribution naming behavior): https://packaging.python.org/en/latest/specifications/name-normalization/ (**HIGH**)
- Django docs — Reusable app packaging guidance (including static/templates packaging concerns): https://docs.djangoproject.com/en/6.0/intro/reusable-apps/ (**HIGH**)
- PyPA build docs (isolated, standards-compliant build frontend behavior): https://build.pypa.io/en/latest/ (**HIGH**)
- Twine docs (`twine check`, upload workflow, non-interactive CI options): https://twine.readthedocs.io/en/latest/ (**HIGH**)
- PyPI docs — Trusted Publishers (OIDC model and security properties): https://docs.pypi.org/trusted-publishers/ (**HIGH**)
- PyPI docs — Yanking releases (non-destructive rollback path): https://docs.pypi.org/project-management/yanking/ (**HIGH**)
- PyPI docs — Project metadata presentation/verification semantics: https://docs.pypi.org/project_metadata/ (**MEDIUM**; display-focused but relevant to release metadata quality)
- Setuptools data files guide (common file inclusion failure modes): https://setuptools.pypa.io/en/latest/userguide/datafiles.html (**HIGH**)
- Hatch build configuration (file-selection and build config pitfalls if hatchling is used): https://hatch.pypa.io/latest/config/build/ (**MEDIUM**; backend-specific)

---
*Pitfalls research for: Django Smart Filters release-readiness milestone*
*Researched: 2026-04-21*

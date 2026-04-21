# Testing Patterns

**Analysis Date:** 2026-04-21

## Test Framework

**Runner:**
- pytest (version not pinned in repository files)
- Config: Not detected (`pytest.ini`, `pyproject.toml`, `setup.cfg`, `tox.ini` absent in project root)

**Assertion Library:**
- Native `assert` statements via pytest in `tests/*.py`

**Run Commands:**
```bash
python -m pytest tests                       # Run all tests
python -m pytest tests -x                    # Stop on first failure
python -m pytest tests -q                    # Quiet output
```

## Test File Organization

**Location:**
- Separate test directory: `tests/`

**Naming:**
- Files use `test_*.py` (examples: `tests/test_query.py`, `tests/test_autocomplete_admin_endpoint.py`)
- Test functions use `test_*` naming with behavior-focused descriptions.

**Structure:**
```
tests/
├── test_declarations.py
├── test_validation.py
├── test_state.py
├── test_query.py
├── test_admin_filters.py
├── test_autocomplete.py
├── test_autocomplete_admin_endpoint.py
├── test_autocomplete_ui.py
├── test_theme_adapters.py
├── test_extension_registry.py
└── test_docs_examples.py
```

## Test Structure

**Suite Organization:**
```python
def _specs():
    return [
        Filter.field("status").dropdown().to_spec(),
        Filter.field("category").multi_select().to_spec(),
    ]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("true", True), ("false", False)],
)
def test_boolean_toggle_maps_true_false_consistently(raw, expected):
    queryset = RecordingQuerySet()
    spec = Filter.field("active").boolean_toggle().to_spec()
    updated = apply_filter_value(queryset, spec, raw)
    assert updated.calls == [{"active": expected}]
```

**Patterns:**
- Setup pattern: helper builders/factories inside test modules (`_make_admin`, `_specs`, `_all_filter_declarations`) in `tests/test_admin_filters.py`, `tests/test_state.py`.
- Teardown pattern: explicit registry cleanup when global state is touched (`clear_filter_component_registry()` in `tests/test_extension_registry.py` and `tests/test_docs_examples.py`).
- Assertion pattern: full-structure equality assertions for deterministic behavior (`queryset.calls == [...]` in `tests/test_query.py`; payload key-set checks in `tests/test_autocomplete_admin_endpoint.py`).

## Mocking

**Framework:**
- Custom in-memory fakes/stubs (no `unittest.mock`/`pytest-mock` usage detected)

**Patterns:**
```python
class RecordingQuerySet:
    def __init__(self, calls=None):
        self.calls = calls or []

    def filter(self, **kwargs):
        return RecordingQuerySet(self.calls + [kwargs])
```

```python
class InMemoryQuerySet:
    def filter(self, **kwargs):
        ...
    def order_by(self, *fields):
        ...
    def values_list(self, *fields):
        ...
```

**What to Mock:**
- QuerySet behavior via lightweight doubles (`RecordingQuerySet` in `tests/test_query.py`, `InMemoryQuerySet` in `tests/test_autocomplete_admin_endpoint.py`).
- Admin superclass seams via local base admin classes (`_BaseSmartAdmin` in `tests/test_admin_filters.py`, `tests/test_theme_adapters.py`).

**What NOT to Mock:**
- Core normalization/validation functions (`parse_filter_state`, `apply_filter_state`, `normalize_declarations`) are tested directly.
- Template rendering is exercised with real `render_to_string` calls in `tests/test_autocomplete_ui.py`.

## Fixtures and Factories

**Test Data:**
```python
dataset = [
    {"pk": 1, "status": "open", "category": "Alpha"},
    {"pk": 2, "status": "open", "category": "Alpine"},
    {"pk": 3, "status": "closed", "category": "Alpha"},
]
```

**Location:**
- Inline per-module fixtures/helpers in each `tests/test_*.py` file.
- No shared `tests/conftest.py` detected.

## Coverage

**Requirements:** None enforced (no coverage config or threshold files detected)

**View Coverage:**
```bash
Not configured in repository (no coverage tool config detected)
```

## Test Types

**Unit Tests:**
- Pure-function and normalization tests in `tests/test_state.py`, `tests/test_query.py`, `tests/test_validation.py`, `tests/test_declarations.py`.

**Integration Tests:**
- Django admin integration with `RequestFactory`, `ModelAdmin`, template rendering, and JSON responses in `tests/test_admin_filters.py`, `tests/test_autocomplete_admin_endpoint.py`, `tests/test_theme_adapters.py`, `tests/test_autocomplete_ui.py`.

**E2E Tests:**
- Not used (no browser automation framework detected).

## Common Patterns

**Async Testing:**
```python
# No async test functions detected; autocomplete UI behavior is validated
# via deterministic string/assertion checks in JS and HTML output.
```

**Error Testing:**
```python
with pytest.raises(ValueError, match="Invalid page"):
    parse_autocomplete_request(spec, {"query": "alpha", "page": "0"})
```

---

*Testing analysis: 2026-04-21*

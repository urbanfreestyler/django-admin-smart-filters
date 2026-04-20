# Testing Patterns

**Analysis Date:** 2026-04-20

## Test Framework

**Runner:**
- `pytest` (version pinned in environment cache artifacts as `pytest-9.0.3` via files like `tests/__pycache__/test_query.cpython-312-pytest-9.0.3.pyc`)
- Config: Not detected (`pytest.ini`, `pyproject.toml`, `tox.ini`, and `conftest.py` are not present at `C:\Projects\django-admin-smart-filters`)

**Assertion Library:**
- Built-in `pytest` assertions and exception matching (`assert ...`, `pytest.raises(...)`) in `tests/test_query.py` and `tests/test_validation.py`.

**Run Commands:**
```bash
pytest                      # Run all tests from repository root
pytest -k autocomplete      # Run focused subset by keyword
pytest --maxfail=1 -q       # Fast local feedback
```

## Test File Organization

**Location:**
- Use separate test directory pattern: all tests live under `tests/`.
- Library code under test lives under `django_smart_filters/`.

**Naming:**
- Use `test_*.py` module naming, for example `tests/test_state.py`, `tests/test_admin_filters.py`, and `tests/test_autocomplete_ui.py`.
- Use test function names in `test_<behavior>_<expected_result>` style, for example `test_parse_multiselect_from_repeated_and_csv_values_stable_order` in `tests/test_state.py`.

**Structure:**
```
tests/
  test_declarations.py
  test_validation.py
  test_state.py
  test_query.py
  test_admin_filters.py
  test_active_filters_ui.py
  test_autocomplete.py
  test_autocomplete_admin_endpoint.py
  test_autocomplete_ui.py
```

## Test Structure

**Suite Organization:**
```python
# Pattern from `tests/test_query.py`
class RecordingQuerySet:
    def filter(self, **kwargs: object) -> "RecordingQuerySet":
        ...

def _specs() -> list[FilterSpec]:
    return [
        Filter.field("status").dropdown().to_spec(),
        Filter.field("category").multi_select().to_spec(),
    ]

def test_dropdown_applies_equality_lookup() -> None:
    queryset = RecordingQuerySet()
    spec = Filter.field("status").dropdown().to_spec()
    updated = apply_filter_value(queryset, spec, "open")
    assert updated.calls == [{"status": "open"}]
```

**Patterns:**
- Setup pattern:
  - Use local lightweight fakes/stubs inside each module (`RecordingQuerySet` in `tests/test_query.py`, `InMemoryQuerySet` in `tests/test_autocomplete_admin_endpoint.py`).
  - Build common filter specs through helper functions (`_specs` in `tests/test_state.py`, `_all_filter_declarations` in `tests/test_admin_filters.py`).
- Teardown pattern:
  - No explicit teardown fixtures; tests rely on function isolation and immutable/local data.
- Assertion pattern:
  - Assert exact deterministic structures (lists of filter calls, JSON payload keys, query param pairs) rather than partial truthiness, e.g. `tests/test_active_filters_ui.py` and `tests/test_autocomplete_admin_endpoint.py`.

## Mocking

**Framework:**
- No dedicated mocking library detected (no `unittest.mock` or external mock helpers used).

**Patterns:**
```python
# Pattern from `tests/test_autocomplete_admin_endpoint.py`
class InMemoryQuerySet:
    def filter(self, **kwargs: object) -> "InMemoryQuerySet":
        ...

    def order_by(self, *fields: str) -> "InMemoryQuerySet":
        ...

    def values_list(self, *fields: str):
        return [tuple(row[field] for field in fields) for row in self._rows]

class EndpointAdmin(SmartFilterAdminMixin, _BaseSmartAdmin):
    smart_filters = [
        Filter.field("status").dropdown(),
        Filter.field("category").autocomplete(),
    ]
```

**What to Mock:**
- Mock queryset behavior with small in-memory classes for deterministic filter/search behavior (`tests/test_query.py`, `tests/test_autocomplete.py`, `tests/test_autocomplete_admin_endpoint.py`).
- Mock admin request context using `RequestFactory` for `get_queryset`, `changelist_view`, and custom endpoint tests (`tests/test_admin_filters.py`, `tests/test_autocomplete_admin_endpoint.py`).

**What NOT to Mock:**
- Do not mock normalization/parsing functions under test; pass raw inputs and assert normalized output (`tests/test_state.py`, `tests/test_query.py`).
- Do not mock template rendering for UI payload contract checks; render real templates via `render_to_string` (`tests/test_autocomplete_ui.py`).

## Fixtures and Factories

**Test Data:**
```python
# Pattern from `tests/test_admin_filters.py`
@pytest.mark.parametrize(
    ("data", "expected_calls"),
    [
        ({"status": "open"}, [{"status": "open"}]),
        ({"active": "true"}, [{"active": True}]),
    ],
)
def test_each_built_in_kind_filters_queryset_from_get_params(data, expected_calls) -> None:
    ...
```

**Location:**
- Inline module helpers and local factories are used instead of shared fixture files:
  - `_make_admin` in `tests/test_admin_filters.py` and `tests/test_autocomplete_admin_endpoint.py`
  - `_pairs` in `tests/test_active_filters_ui.py`
  - `_spec` in `tests/test_autocomplete.py`

## Coverage

**Requirements:**
- None enforced (no coverage configuration file detected and no coverage threshold config detected).

**View Coverage:**
```bash
pytest --cov=django_smart_filters --cov-report=term-missing
```

## Test Types

**Unit Tests:**
- Pure-function normalization/validation/state/query tests dominate (`tests/test_validation.py`, `tests/test_declarations.py`, `tests/test_state.py`, `tests/test_query.py`, `tests/test_autocomplete.py`).

**Integration Tests:**
- Django admin integration tests instantiate `ModelAdmin` subclasses and drive requests with `RequestFactory` (`tests/test_admin_filters.py`, `tests/test_autocomplete_admin_endpoint.py`, `tests/test_autocomplete_ui.py`).

**E2E Tests:**
- Not used (no browser automation framework files detected).

## Common Patterns

**Async Testing:**
```python
# Current pattern is synchronous endpoint/function testing
response = admin_instance.smart_filter_autocomplete_view(request)
payload = json.loads(response.content.decode("utf-8"))
assert response.status_code == 200
```
Used in `tests/test_autocomplete_admin_endpoint.py`; no async test runner markers are present.

**Error Testing:**
```python
# Pattern from `tests/test_validation.py`
with pytest.raises(FilterValidationError, match="collision"):
    normalize_declarations(declarations)

# Pattern from `tests/test_query.py`
with pytest.raises(ValueError, match="Invalid boolean value"):
    apply_filter_value(queryset, spec, "definitely")
```

---

*Testing analysis: 2026-04-20*

from django_smart_filters.builder import Filter
from django_smart_filters.contracts import FilterSpec
from django_smart_filters.declarations import DropdownFilter, normalize_class_declaration, normalize_declarations
from django_smart_filters.params import resolve_param_name


def test_param_name_deterministic_and_alias_override() -> None:
    assert resolve_param_name("status") == "status"
    assert resolve_param_name("status", multivalue=True) == "status__in"
    assert resolve_param_name("status", alias="state") == "state"
    assert resolve_param_name("status", alias="state", multivalue=True) == "state"


def test_class_style_declaration_normalizes_to_filter_spec() -> None:
    spec = normalize_class_declaration(DropdownFilter("status"))

    assert isinstance(spec, FilterSpec)
    assert spec.field_name == "status"
    assert spec.filter_kind == "dropdown"
    assert spec.param_name == "status"


def test_fluent_declaration_normalizes_to_equivalent_filter_spec() -> None:
    class_spec = normalize_class_declaration(DropdownFilter("status"))
    fluent_spec = Filter.field("status").dropdown().to_spec()

    assert fluent_spec == class_spec


def test_mixed_declarations_preserve_order_and_remain_list_filter_friendly() -> None:
    declarations = [
        DropdownFilter("status"),
        Filter.field("category").autocomplete(),
        Filter.field("active").boolean_toggle(),
    ]

    specs = normalize_declarations(declarations)

    assert [spec.field_name for spec in specs] == ["status", "category", "active"]
    assert [spec.filter_kind for spec in specs] == ["dropdown", "autocomplete", "boolean_toggle"]

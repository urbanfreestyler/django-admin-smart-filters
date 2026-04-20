from django_smart_filters.params import resolve_param_name


def test_param_name_deterministic_and_alias_override() -> None:
    assert resolve_param_name("status") == "status"
    assert resolve_param_name("status", multivalue=True) == "status__in"
    assert resolve_param_name("status", alias="state") == "state"
    assert resolve_param_name("status", alias="state", multivalue=True) == "state"

from __future__ import annotations

import re
from pathlib import Path

from django_admin_smart_filters.registry import clear_filter_component_registry


def _docs_root() -> Path:
    return Path(__file__).resolve().parents[1] / "docs"


def _extract_python_block(doc_path: Path, marker: str) -> str:
    content = doc_path.read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", content, flags=re.DOTALL)
    for block in blocks:
        if marker in block:
            return block
    raise AssertionError(f"No python snippet marked '{marker}' in {doc_path}")


def test_extension_docs_public_import_snippet_compiles() -> None:
    snippet = _extract_python_block(
        _docs_root() / "extension_hooks.md",
        "docs:extension-public-imports",
    )

    compile(snippet, "extension_hooks.md", "exec")


def test_custom_component_registration_snippet_executes() -> None:
    clear_filter_component_registry()
    snippet = _extract_python_block(
        _docs_root() / "extension_hooks.md",
        "docs:component-registration",
    )

    namespace: dict[str, object] = {}
    exec(snippet, namespace)

    resolved = namespace.get("resolved_component")
    assert resolved is not None
    assert getattr(resolved, "key", None) == "status_badge"


def test_theme_adapter_snippet_uses_valid_template_contract_paths() -> None:
    docs_path = _docs_root() / "theme_adapters.md"
    content = docs_path.read_text(encoding="utf-8")
    assert "templates/admin/django_admin_smart_filters/theme/default/" in content

    snippet = _extract_python_block(docs_path, "docs:theme-adapter-config")
    namespace: dict[str, object] = {}
    exec(snippet, namespace)

    adapter = namespace.get("adapter")
    assert adapter is not None
    assert str(getattr(adapter, "controls_template", "")).startswith(
        "admin/django_admin_smart_filters/"
    )
    assert str(getattr(adapter, "active_bar_template", "")).startswith(
        "admin/django_admin_smart_filters/"
    )

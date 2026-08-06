"""Static guard: propensity.py must NOT reference any FORBIDDEN_FIELDS name.

This is the canonical fair-housing enforcement in code. If a future contributor
adds a forbidden field reference (even via .attr lookup or a string literal in a
dictionary key), this test fails loudly.
"""
import ast
import pathlib

from scripts.criteria import FORBIDDEN_FIELDS


_PROPENSITY_PATH = pathlib.Path(__file__).parent.parent / "scripts" / "propensity.py"


def _collect_names_and_attrs(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            names.add(node.value)
        elif isinstance(node, ast.keyword) and node.arg:
            names.add(node.arg)
    return names


def test_propensity_source_references_no_forbidden_fields():
    src = _PROPENSITY_PATH.read_text()
    tree = ast.parse(src)
    names = _collect_names_and_attrs(tree)
    leak = names & FORBIDDEN_FIELDS
    assert not leak, (
        f"propensity.py references protected-class fields: {sorted(leak)}. "
        f"Fair-housing rule: scoring must not touch any of {sorted(FORBIDDEN_FIELDS)}."
    )


def test_propensity_module_does_not_import_any_forbidden_module_name():
    # Defensive: also fail if anyone imports a module named for a protected class.
    src = _PROPENSITY_PATH.read_text()
    tree = ast.parse(src)
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.name.split(".")[-1])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_names.add(node.module.split(".")[-1])
            for alias in node.names:
                imported_names.add(alias.name)
    leak = imported_names & FORBIDDEN_FIELDS
    assert not leak, f"propensity.py imports protected-class name: {sorted(leak)}"

"""Generate compact repository outlines from source files.

The outline intentionally emits structure only: file paths, imports, classes,
functions, async functions, and method signatures. Function bodies are omitted
so the output can be safely used as compressed exploration context.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Iterable, Sequence


SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "_archived",
    "node_modules",
    "venv",
}


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Return a compact function or async-function signature."""
    args = ast.unparse(node.args)
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {node.name}({args}){returns}"


def import_line(node: ast.Import | ast.ImportFrom) -> str:
    """Return a compact import statement for an import AST node."""
    if isinstance(node, ast.Import):
        names = ", ".join(alias.name for alias in node.names)
        return f"import {names}"

    module = "." * node.level + (node.module or "")
    names = ", ".join(alias.name for alias in node.names)
    return f"from {module} import {names}"


def should_skip(path: Path) -> bool:
    """Return true when any path part is an ignored directory."""
    return any(part in SKIP_DIRS for part in path.parts)


def relative_display_path(path: Path) -> str:
    """Return a stable display path, relative to cwd when possible."""
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def depth_from_root(path: Path, root: Path) -> int:
    """Return file depth relative to the root, counting the file as depth 1."""
    return len(path.relative_to(root).parts)


def iter_files(
    roots: Sequence[Path],
    max_depth: int | None,
    include_non_python: bool,
) -> Iterable[tuple[Path, Path]]:
    """Yield ``(root, file)`` pairs in deterministic order."""
    for root in roots:
        root = root.resolve()
        if root.is_file():
            if include_non_python or root.suffix == ".py":
                yield root.parent, root
            continue

        for path in sorted(root.rglob("*")):
            if path.is_dir() or should_skip(path):
                continue
            if max_depth is not None and depth_from_root(path, root) > max_depth:
                continue
            if include_non_python or path.suffix == ".py":
                yield root, path


def outline_python(path: Path) -> list[str]:
    """Return outline lines for a Python source file."""
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError as exc:
        return [f"  ! syntax error: {exc.msg}"]

    lines: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            lines.append(f"  {import_line(node)}")
        elif isinstance(node, ast.ClassDef):
            lines.append(f"  class {node.name}")
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    lines.append(f"    {signature(child)}")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            lines.append(f"  {signature(node)}")
    return lines


def generate_outline(
    roots: Sequence[Path],
    max_depth: int | None = None,
    include_non_python: bool = False,
) -> str:
    """Generate a compact outline for the given roots."""
    output: list[str] = []
    for root, path in iter_files(roots, max_depth, include_non_python):
        output.append(relative_display_path(path))
        if path.suffix == ".py":
            output.extend(outline_python(path))
    return "\n".join(output)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--max-depth", type=int, default=None)
    parser.add_argument(
        "--include-non-python",
        action="store_true",
        help="Include non-Python files as path-only outline entries.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the outline CLI."""
    args = build_parser().parse_args(argv)
    print(generate_outline(
        roots=args.roots,
        max_depth=args.max_depth,
        include_non_python=args.include_non_python,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())

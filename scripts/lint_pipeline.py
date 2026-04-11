"""Pipeline lint — enforces ADR-0002 (stdlib-only) and ADR-0008 (no LLM in pipeline).

Scans every pipeline Python file and checks that:
  1. Every import resolves to a Python stdlib module (sys.stdlib_module_names)
  2. No import mentions a known LLM client (anthropic, openai, claude, llm, ...)
  3. No raw string literal in the file references an LLM API endpoint

Scope:
  - scripts/build_index_*.py  (primary pipeline scripts)
  - src/indices/**/*.py       (any future per-index helper modules)

Exit code:
  0 if clean, 1 if any violation found.

Run:
  python3 scripts/lint_pipeline.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

STDLIB = sys.stdlib_module_names

FORBIDDEN_LLM_MODULES = {
    "anthropic",
    "openai",
    "claude",
    "claude_client",
    "llm",
    "cohere",
    "google.generativeai",
    "vertexai",
    "huggingface_hub",
    "replicate",
    "ollama",
}

FORBIDDEN_URL_PATTERNS = [
    r"api\.anthropic\.com",
    r"api\.openai\.com",
    r"api\.cohere\.ai",
    r"generativelanguage\.googleapis\.com",
    r"api\.replicate\.com",
    r"huggingface\.co/api/inference",
]

SCAN_GLOBS = [
    "scripts/build_index_*.py",
    "src/indices/**/*.py",
]


def top_level(module_name: str) -> str:
    """Return the top-level package name (e.g. 'xml.etree.ElementTree' -> 'xml')."""
    return module_name.split(".", 1)[0]


def scan_file(path: Path) -> list[str]:
    """Return list of violations (as human-readable strings)."""
    src = path.read_text(encoding="utf-8")
    violations: list[str] = []

    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        return [f"{path.relative_to(REPO_ROOT)}: syntax error: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = top_level(alias.name)
                if top in FORBIDDEN_LLM_MODULES or alias.name in FORBIDDEN_LLM_MODULES:
                    violations.append(
                        f"{path.relative_to(REPO_ROOT)}:{node.lineno}  "
                        f"LLM module import '{alias.name}' violates ADR-0008"
                    )
                    continue
                if top not in STDLIB:
                    violations.append(
                        f"{path.relative_to(REPO_ROOT)}:{node.lineno}  "
                        f"non-stdlib import '{alias.name}' violates ADR-0002"
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                # relative import (from . import x) — always allowed
                continue
            top = top_level(node.module)
            if top in FORBIDDEN_LLM_MODULES or node.module in FORBIDDEN_LLM_MODULES:
                violations.append(
                    f"{path.relative_to(REPO_ROOT)}:{node.lineno}  "
                    f"LLM module import 'from {node.module}' violates ADR-0008"
                )
                continue
            if top not in STDLIB:
                violations.append(
                    f"{path.relative_to(REPO_ROOT)}:{node.lineno}  "
                    f"non-stdlib import 'from {node.module}' violates ADR-0002"
                )

    # URL literal check: grep for known LLM API hostnames
    for pattern in FORBIDDEN_URL_PATTERNS:
        for m in re.finditer(pattern, src):
            line_num = src.count("\n", 0, m.start()) + 1
            violations.append(
                f"{path.relative_to(REPO_ROOT)}:{line_num}  "
                f"LLM API URL literal '{m.group(0)}' violates ADR-0008"
            )

    return violations


def main() -> int:
    files: list[Path] = []
    for pattern in SCAN_GLOBS:
        files.extend(sorted(REPO_ROOT.glob(pattern)))

    if not files:
        print("  (no pipeline files matched — nothing to lint)", file=sys.stderr)
        return 0

    total_violations = 0
    for f in files:
        violations = scan_file(f)
        for v in violations:
            print(f"  {v}")
            total_violations += 1

    print()
    if total_violations:
        print(f"FAIL  {total_violations} violation(s) across {len(files)} pipeline file(s)", file=sys.stderr)
        print(f"      Enforces ADR-0002 (stdlib only) and ADR-0008 (no LLM in pipeline)", file=sys.stderr)
        return 1
    print(f"PASS  lint_pipeline: scanned {len(files)} pipeline file(s), zero violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())

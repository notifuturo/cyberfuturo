"""Index lint — enforces ADR-0007 (versioned methodology) and BR-11 (kill criterion).

For every published index under data/indices/, checks that:
  1. A methodology markdown file exists at src/indices/<slug>/methodology.md
  2. The methodology contains required sections
  3. The methodology has a visible version (vX.Y) and a changelog entry
  4. The methodology declares kill / deprecation criteria (BR-11)
  5. A matching HTML methodology page exists under site/methodology/

Exit code:
  0 if clean, 1 if any published index is non-compliant.

Run:
  python3 scripts/lint_indices.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_METHOD_SECTIONS = [
    "what this measures",
    "what this does not measure",
    "exact query",
    "pipeline",
    "outputs",
    "known limitations",
    "changelog",
    "how to reproduce",
    "deprecation criteria",  # BR-11
]


def scan_index(slug: str) -> list[str]:
    problems: list[str] = []
    method_md = REPO_ROOT / "src" / "indices" / slug / "methodology.md"
    method_html = REPO_ROOT / "site" / "methodology" / f"{slug}.html"
    csv_path = REPO_ROOT / "data" / "indices" / f"{slug}.csv"
    svg_path = REPO_ROOT / "data" / "indices" / f"{slug}.svg"

    # 1. Methodology doc must exist
    if not method_md.exists():
        problems.append(f"{slug}: missing methodology at {method_md.relative_to(REPO_ROOT)}")
        return problems

    text = method_md.read_text(encoding="utf-8").lower()

    # 2. Required sections
    for section in REQUIRED_METHOD_SECTIONS:
        if section not in text:
            problems.append(
                f"{slug}: methodology missing '{section}' section — "
                f"violates {'BR-11' if 'deprecation' in section else 'ADR-0007'}"
            )

    # 3. Version tag
    if not re.search(r"\bv\d+\.\d+\b", text):
        problems.append(f"{slug}: methodology has no visible version tag (e.g. v0.1) — violates ADR-0007")

    # 4. Matching HTML methodology page
    if not method_html.exists():
        problems.append(
            f"{slug}: missing public methodology page at {method_html.relative_to(REPO_ROOT)} — "
            f"violates BR-04 (traceability)"
        )

    # 5. Canonical CSV and SVG present
    if not csv_path.exists():
        problems.append(f"{slug}: missing canonical CSV at {csv_path.relative_to(REPO_ROOT)}")
    if not svg_path.exists():
        problems.append(f"{slug}: missing canonical SVG at {svg_path.relative_to(REPO_ROOT)}")

    return problems


def main() -> int:
    indices_dir = REPO_ROOT / "data" / "indices"
    if not indices_dir.exists():
        print("  (no data/indices/ directory — nothing to lint)", file=sys.stderr)
        return 0

    slugs: set[str] = set()
    for path in indices_dir.iterdir():
        if path.suffix in (".csv", ".svg"):
            slugs.add(path.stem)

    if not slugs:
        print("  (no indices found — nothing to lint)", file=sys.stderr)
        return 0

    total_problems = 0
    for slug in sorted(slugs):
        problems = scan_index(slug)
        for p in problems:
            print(f"  {p}")
            total_problems += 1

    print()
    if total_problems:
        print(f"FAIL  {total_problems} problem(s) across {len(slugs)} index/indices", file=sys.stderr)
        print(f"      Enforces ADR-0007 (versioned methodology) and BR-11 (kill criterion)", file=sys.stderr)
        return 1
    print(f"PASS  lint_indices: scanned {len(slugs)} index/indices, all compliant")
    return 0


if __name__ == "__main__":
    sys.exit(main())

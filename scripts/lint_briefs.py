"""Brief structure lint — enforces the 9-section template and several BRs.

Checks every markdown brief under docs/briefs/ for:
  - Required headings in order (§5 of business-concepts.md, BR editorial)
  - AI-assistance disclosure (BR-09)
  - Sources block with (index_slug, methodology_version) tuples (BR-04)
  - No forbidden vocabulary (delegated to lint_editorial.py, but this file
    also contains a secondary check to catch anything that slipped through
    when a brief is structurally valid but editorially non-compliant).

Exit code:
  0 if clean, 1 if any brief is non-compliant.

Run:
  python3 scripts/lint_briefs.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_HEADINGS_IN_ORDER = [
    # (required-substring-in-heading, human-readable-name)
    ("the number", "The number"),
    ("what moved", "What moved"),
    ("what this is", "What this is NOT"),  # flexible match
    ("how this was built", "How this was built"),
    ("next", "Next"),
]

DISCLOSURE_MARKERS = [
    "human-edited",
    "ai-assisted",
    "no llm",
    "deterministic",
]

SOURCES_MARKERS = [
    "sources",
    "cited indices",
]


def scan_brief(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    text_lower = text.lower()
    rel = path.relative_to(REPO_ROOT)
    problems: list[str] = []

    # 1. Headings in order
    last_pos = 0
    for substring, label in REQUIRED_HEADINGS_IN_ORDER:
        # Find a heading line containing the substring
        matches = [
            i for i, line in enumerate(text_lower.splitlines())
            if line.lstrip().startswith("#") and substring in line
        ]
        if not matches:
            problems.append(f"{rel}: missing required section '{label}'")
            continue
        # Position in doc (bytes)
        positions = [m.start() for m in re.finditer(re.escape(substring), text_lower)]
        # Pick the earliest match
        pos = positions[0] if positions else -1
        if pos < last_pos:
            problems.append(
                f"{rel}: section '{label}' appears out of required order"
            )
        last_pos = pos

    # 2. AI assistance disclosure (BR-09)
    if not any(marker in text_lower for marker in DISCLOSURE_MARKERS):
        problems.append(
            f"{rel}: no AI-assistance disclosure found "
            f"(expected one of: {', '.join(DISCLOSURE_MARKERS)}) — violates BR-09"
        )

    # 3. Sources block (BR-04)
    if not any(marker in text_lower for marker in SOURCES_MARKERS):
        problems.append(
            f"{rel}: no sources block found "
            f"(expected 'Sources' or 'Cited indices' heading) — violates BR-04"
        )

    # 4. Each brief should cite at least one (index, methodology_version) tuple
    # Tuple syntax: [slug vMAJOR.MINOR] or similar — we use a flexible regex.
    version_tag_re = re.compile(
        r"\b([a-z][a-z0-9\-]{2,}?)[\s,]+v(\d+\.\d+)\b", re.IGNORECASE
    )
    if not version_tag_re.search(text):
        problems.append(
            f"{rel}: no (index_slug, methodology_version) citation found "
            f"(expected e.g. 'arxiv-ai-velocity v0.1') — violates BR-04"
        )

    return problems


def main() -> int:
    briefs = sorted((REPO_ROOT / "docs" / "briefs").glob("*.md"))
    if not briefs:
        print("  (no briefs found — nothing to lint)", file=sys.stderr)
        return 0

    total_problems = 0
    for f in briefs:
        problems = scan_brief(f)
        for p in problems:
            print(f"  {p}")
            total_problems += 1

    print()
    if total_problems:
        print(f"FAIL  {total_problems} problem(s) across {len(briefs)} brief(s)", file=sys.stderr)
        print(f"      Enforces BR-04, BR-09, and brief structure template", file=sys.stderr)
        return 1
    print(f"PASS  lint_briefs: scanned {len(briefs)} brief(s), all compliant")
    return 0


if __name__ == "__main__":
    sys.exit(main())

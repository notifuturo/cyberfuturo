"""Editorial lint — enforces BR-01 (no forecasts) vocabulary rules.

Scans briefs, HTML pages, and the markdown sources for forbidden words that
contradict the measurement-only publication stance (ADR-0001).

Scope of scan (files):
  - docs/briefs/*.md        (editorial sources)
  - site/index.html
  - site/issues/*.html
  - site/methodology/*.html
  - site/rules.html, site/about.html, site/privacy.html, site/methodology.html

Scope of exclusion (content):
  - Text inside HTML comments
  - Text inside <code>...</code>, <pre>...</pre>, and markdown code fences
  - Text inside headers that explicitly delimit negation ("What this is NOT",
    "What CyberFuturo is not") — that section is allowed to *quote* forbidden
    words in order to reject them. We track this by skipping lines inside a
    "### Not-a-forecast escape hatch" block delimited by
    <!-- lint:allow-forbidden start --> / <!-- lint:allow-forbidden end -->
    in HTML, or the same comment syntax in markdown.

Exit code:
  0 if clean, 1 if any forbidden occurrences are found.

Run:
  python3 scripts/lint_editorial.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

FORBIDDEN_WORDS = [
    # Forecasting vocabulary per business-concepts.md §2
    r"\bforecast(s|ed|ing)?\b",
    r"\bpredict(s|ed|ion|ions|ive|ing)?\b",
    r"\bwill\s+be\b",
    r"\bexpected\s+to\b",
    r"\bprojected\s+to\b",
    r"\bon\s+track\s+to\b",
    r"\blikely\s+to\s+reach\b",
    r"\bset\s+to\s+(reach|hit|cross)\b",
]

SCAN_GLOBS = [
    "docs/briefs/*.md",
    "site/*.html",
    "site/issues/*.html",
    "site/methodology/*.html",
]

ALLOW_OPEN = "<!-- lint:allow-forbidden start -->"
ALLOW_CLOSE = "<!-- lint:allow-forbidden end -->"

HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
HTML_CODE_RE = re.compile(r"<(code|pre)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
MD_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
MD_INLINE_CODE_RE = re.compile(r"`[^`]+`")


def strip_protected(text: str) -> str:
    """Remove code blocks and comments so we don't flag quoted examples."""
    text = HTML_CODE_RE.sub("", text)
    text = MD_FENCE_RE.sub("", text)
    text = MD_INLINE_CODE_RE.sub("", text)
    return text


def strip_allow_blocks(text: str) -> str:
    """Remove regions explicitly marked as allowed to contain forbidden words."""
    out: list[str] = []
    in_allow = False
    for line in text.splitlines(keepends=True):
        if ALLOW_OPEN in line:
            in_allow = True
            continue
        if ALLOW_CLOSE in line:
            in_allow = False
            continue
        if not in_allow:
            out.append(line)
    return "".join(out)


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    """Return list of (line_number, matched_text, full_line) for each hit."""
    raw = path.read_text(encoding="utf-8")
    # Strip allow-blocks first (they may contain HTML comments we want to preserve
    # the semantics of), then strip code and HTML comments.
    cleaned = strip_allow_blocks(raw)
    cleaned = HTML_COMMENT_RE.sub("", cleaned)
    cleaned = strip_protected(cleaned)

    hits: list[tuple[int, str, str]] = []
    for pattern in FORBIDDEN_WORDS:
        for m in re.finditer(pattern, cleaned, flags=re.IGNORECASE):
            # Map cleaned offset back to a line number by counting newlines in
            # the cleaned text (we report against cleaned lines; good enough to
            # locate the issue).
            line_num = cleaned.count("\n", 0, m.start()) + 1
            line_text = cleaned.splitlines()[line_num - 1].strip() if line_num - 1 < len(cleaned.splitlines()) else ""
            hits.append((line_num, m.group(0), line_text))
    return hits


def main() -> int:
    files: list[Path] = []
    for pattern in SCAN_GLOBS:
        files.extend(sorted(REPO_ROOT.glob(pattern)))

    if not files:
        print("  (no files matched scan globs — nothing to lint)", file=sys.stderr)
        return 0

    total_hits = 0
    files_with_hits: list[Path] = []
    for f in files:
        hits = scan_file(f)
        if hits:
            files_with_hits.append(f)
            for line, match, context in hits:
                rel = f.relative_to(REPO_ROOT)
                print(f"  {rel}:{line}  FORBIDDEN '{match}'  -- {context[:120]}")
                total_hits += 1

    print()
    if total_hits:
        print(f"FAIL  {total_hits} forbidden occurrence(s) across {len(files_with_hits)} file(s)", file=sys.stderr)
        print(f"      Enforces BR-01 (no forecasts) / ADR-0001", file=sys.stderr)
        return 1
    print(f"PASS  lint_editorial: scanned {len(files)} files, zero forbidden words")
    return 0


if __name__ == "__main__":
    sys.exit(main())

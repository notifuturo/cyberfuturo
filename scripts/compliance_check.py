"""Compliance master runner — orchestrates every lint and produces a report.

Runs (in order):
  1. lint_editorial.py   — BR-01 / ADR-0001 (no forecasts)
  2. lint_pipeline.py    — ADR-0002 / ADR-0008 (stdlib only / no LLM)
  3. lint_briefs.py      — BR-04 / BR-09 / brief structure
  4. lint_indices.py     — ADR-0007 / BR-11 (versioned methodology / kill criteria)
  5. Static checks        — required public pages (rules, about, privacy)
  6. Writes docs/compliance-report.md

Exit code:
  0 if every gate passes, 1 otherwise.

Run:
  python3 scripts/compliance_check.py
"""

from __future__ import annotations

import datetime as dt
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = REPO_ROOT / "docs" / "compliance-report.md"

SUBPROCESS_TIMEOUT = 120  # seconds — prevent misbehaving lint scripts from hanging

LINTS = [
    ("scripts/lint_editorial.py", "BR-01 / ADR-0001", "No-forecast vocabulary"),
    ("scripts/lint_pipeline.py",  "ADR-0002 / ADR-0008", "Stdlib-only pipeline, no LLM"),
    ("scripts/lint_briefs.py",    "BR-04 / BR-09", "Brief structure + disclosure"),
    ("scripts/lint_indices.py",   "ADR-0007 / BR-11", "Versioned methodology + kill criteria"),
]

REQUIRED_PUBLIC_PAGES = [
    ("site/index.html",                               "landing page"),
    ("site/rules.html",                               "editorial rules (BR-01/02/07/08/09/10)"),
    ("site/about.html",                               "about / mission"),
    ("site/privacy.html",                             "privacy policy (BR-10)"),
    ("site/methodology.html",                         "methodology index (BR-04)"),
    ("site/issues/01.html",                           "issue #01"),
    ("site/methodology/arxiv-ai-velocity.html",       "arxiv methodology"),
    ("site/robots.txt",                               "robots"),
    ("site/sitemap.xml",                              "sitemap"),
]


def run_lint(script_rel: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, script_rel],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )
    combined = proc.stdout + (proc.stderr if proc.stderr else "")
    return proc.returncode, combined


def check_public_pages() -> tuple[int, list[str]]:
    missing: list[str] = []
    for rel, description in REQUIRED_PUBLIC_PAGES:
        if not (REPO_ROOT / rel).exists():
            missing.append(f"{rel} — {description}")
    return (0 if not missing else 1), missing


def write_report(results: list[tuple[str, str, str, int, str]],
                 pages_status: tuple[int, list[str]]) -> None:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    all_pass = all(code == 0 for _, _, _, code, _ in results) and pages_status[0] == 0

    lines: list[str] = []
    lines.append("# CyberFuturo — Compliance Report")
    lines.append("")
    lines.append(f"**Generated**: {now}  ")
    lines.append(f"**Overall**: {'PASS ✅' if all_pass else 'FAIL ❌'}")
    lines.append("")
    lines.append("This report is produced by `scripts/compliance_check.py` and "
                 "audits the repo against every [ADR](./adr/README.md) and "
                 "business rule in [`docs/domain/business-concepts.md`](./domain/business-concepts.md).")
    lines.append("")
    lines.append("Run locally with:")
    lines.append("```bash")
    lines.append("python3 scripts/compliance_check.py")
    lines.append("```")
    lines.append("")
    lines.append("## Lint gates")
    lines.append("")
    lines.append("| # | Gate | Enforces | Status |")
    lines.append("|---|---|---|---|")
    for i, (script, rule, desc, code, _out) in enumerate(results, start=1):
        status = "PASS ✅" if code == 0 else "FAIL ❌"
        lines.append(f"| {i} | `{script}` — {desc} | {rule} | {status} |")
    lines.append("")

    lines.append("## Required public pages")
    lines.append("")
    code, missing = pages_status
    lines.append(f"**Status**: {'PASS ✅' if code == 0 else 'FAIL ❌'}")
    lines.append("")
    if missing:
        lines.append("Missing:")
        for m in missing:
            lines.append(f"- {m}")
        lines.append("")
    else:
        lines.append("All required public pages present.")
        lines.append("")

    lines.append("## Lint output")
    lines.append("")
    for script, rule, desc, code, out in results:
        lines.append(f"### `{script}`")
        lines.append("")
        lines.append("```")
        lines.append(out.strip() or "(no output)")
        lines.append("```")
        lines.append("")

    lines.append("## Coverage matrix")
    lines.append("")
    lines.append("| Rule | Enforcement | Status |")
    lines.append("|---|---|---|")
    matrix = [
        ("ADR-0001 measurement-only",      "lint_editorial.py forbidden-word scan",          results[0][3]),
        ("ADR-0002 stdlib only",           "lint_pipeline.py AST import check",              results[1][3]),
        ("ADR-0003 static site no JS",     "no enforcement script yet (manual review)",      None),
        ("ADR-0004 CF Pages direct upload","no enforcement script yet (manual review)",      None),
        ("ADR-0005 inline SVG",            "no enforcement script yet (manual review)",      None),
        ("ADR-0006 private repo public site","manual — gh repo view --json visibility",     None),
        ("ADR-0007 versioned methodology", "lint_indices.py section check",                  results[3][3]),
        ("ADR-0008 no LLM numbers",        "lint_pipeline.py module+URL check",              results[1][3]),
        ("ADR-0009 $0 free tier",          "manual — no automated check",                    None),
        ("ADR-0010 trailing window drift", "lint_indices.py (via methodology limitations)",  results[3][3]),
        ("BR-01 no forecasts",             "lint_editorial.py",                              results[0][3]),
        ("BR-02 no LLM numbers",           "lint_pipeline.py",                               results[1][3]),
        ("BR-03 methodology before pub",   "lint_indices.py methodology presence",           results[3][3]),
        ("BR-04 traceability",             "lint_briefs.py citation tuple",                  results[2][3]),
        ("BR-05 corrections next brief",   "editorial process (manual)",                     None),
        ("BR-06 one sponsor per brief",    "future sponsor-commerce validator",              None),
        ("BR-07 sponsors below the fold",  "future template constraint",                     None),
        ("BR-08 editorial independence",   "editorial process (manual)",                     None),
        ("BR-09 AI disclosure",            "lint_briefs.py disclosure-marker check",         results[2][3]),
        ("BR-10 subscribers never shared", "privacy page presence + policy statement",       pages_status[0]),
        ("BR-11 every index has kill crit","lint_indices.py deprecation-criteria check",     results[3][3]),
        ("BR-12 git history audit trail",  "git history — manual review",                    None),
    ]
    for rule, enforcement, code in matrix:
        if code is None:
            status = "—"
        elif code == 0:
            status = "PASS ✅"
        else:
            status = "FAIL ❌"
        lines.append(f"| {rule} | {enforcement} | {status} |")
    lines.append("")
    lines.append("Rules marked `—` have no automated enforcement yet. They are "
                 "tracked as manual-review items; upgrading them to automated "
                 "checks is part of the v0.2 compliance roadmap.")
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    results: list[tuple[str, str, str, int, str]] = []
    for script, rule, desc in LINTS:
        print(f"--- running {script} ---")
        code, output = run_lint(script)
        print(output)
        results.append((script, rule, desc, code, output))

    print("--- checking required public pages ---")
    pages_code, missing = check_public_pages()
    if missing:
        for m in missing:
            print(f"  missing: {m}")
    else:
        print("  all required pages present")
    print()

    write_report(results, (pages_code, missing))
    print(f"wrote {REPORT_PATH.relative_to(REPO_ROOT)}")

    all_ok = all(code == 0 for _, _, _, code, _ in results) and pages_code == 0
    print()
    print(f"{'PASS ✅' if all_ok else 'FAIL ❌'}  overall compliance")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Generate site/sitemap.xml by walking the actual site tree.

Why a script (vs hand-maintained XML):
  - After Phase 5 shipped 28 chapter-preview pages, the hand-maintained
    sitemap had 13 entries but the site had 100+ indexable pages. Drift is
    inevitable with per-page edits.
  - Filesystem → sitemap is deterministic. The four language trees are
    structurally parallel, so we can emit hreflang alternates automatically
    by matching path shapes across /pt /es /en /fr.

Rules baked in:
  - Skip thank-you pages (`obrigado|gracias|thank-you|merci`) — they're
    noindex and transient.
  - Skip /verify/ sample pages — noindex.
  - Skip 404.html — dedicated error page.
  - Priority: 1.0 for language homes, 0.9 for course TOC + chapters 00/01
    (primary content), 0.85 for chapter-preview pages, 0.8 for orientation +
    buy + privacy.
  - lastmod: today's date (2026-04-22) across the board. Can be refined later
    to use `git log --format=%aI` per file.

Idempotent. ADR-0002 (stdlib only). Run with `python3 scripts/gen_sitemap.py`.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

# Parallel localized path segments. The script discovers pages under PT and
# mirrors each to the equivalent ES/EN/FR URL using this substitution table.
# Keep in sync with site/_worker.js and scripts/gen_chapter_previews.py.
LANG_PATHS = [
    ("pt", "curso",       "comprar",  "privacidade",      "como-comecar"),
    ("es", "curso",       "comprar",  "privacidad",       "como-empezar"),
    ("en", "course",      "buy",      "privacy",          "getting-started"),
    ("fr", "cours",       "acheter",  "confidentialite",  "comment-commencer"),
]
COURSE_DIR   = {lang: c for lang, c, _, _, _ in LANG_PATHS}
BUY_DIR      = {lang: b for lang, _, b, _, _ in LANG_PATHS}
PRIV_DIR     = {lang: p for lang, _, _, p, _ in LANG_PATHS}
START_DIR    = {lang: s for lang, _, _, _, s in LANG_PATHS}
LANGS        = [lang for lang, _, _, _, _ in LANG_PATHS]
OG_HREFLANG  = {"pt": "pt-BR", "es": "es-419", "en": "en-US", "fr": "fr-CA"}

BASE = "https://cyberfuturo.com"
TODAY = date.today().isoformat()

# (path-shape-key, priority). The path-shape-key uses {course} / {buy} / {priv}
# / {start} tokens that map to the per-language path segment.
#
# All structures must have exactly one file per language.
PAGE_SHAPES = [
    ("/{lang}/",                              1.0),
    ("/{lang}/{course}/",                     0.9),
    ("/{lang}/{course}/00-bienvenido/",       0.9),
    ("/{lang}/{course}/01-terminal/",         0.85),
    ("/{lang}/{course}/02-primer-git-commit/", 0.85),
    ("/{lang}/{course}/03-python-hola/",      0.85),
    ("/{lang}/{course}/04-ramos-git/",        0.85),
    ("/{lang}/{course}/05-primera-sql/",      0.85),
    ("/{lang}/{course}/06-http-apis/",        0.85),
    ("/{lang}/{course}/07-loops-dados/",      0.85),
    ("/{lang}/{course}/08-dicionarios/",      0.85),
    ("/{lang}/{buy}/",                        0.8),
    ("/{lang}/{start}/",                      0.8),
    ("/{lang}/indices/",                      0.7),
    ("/{lang}/{priv}/",                       0.6),
]


def expand(shape: str, lang: str) -> str:
    return shape.format(
        lang=lang,
        course=COURSE_DIR[lang],
        buy=BUY_DIR[lang],
        priv=PRIV_DIR[lang],
        start=START_DIR[lang],
    )


# Single-canonical pages that live outside the 4-language shape system —
# governance/traceability artifacts (rules, about, briefs, per-index
# methodology), same treatment as ADR-0007's per-index methodology docs:
# one authoritative version, not translated 4 ways.
STANDALONE_PAGES = [
    ("/rules/",                                0.6),
    ("/about/",                                0.6),
    ("/issues/01/",                            0.6),
    ("/methodology/arxiv-ai-velocity",         0.6),
    ("/methodology/x402-repo-velocity",        0.6),
]


def verify_standalone_files_exist(site_root: Path) -> list[str]:
    missing = []
    for path, _ in STANDALONE_PAGES:
        if path.endswith("/"):
            file_path = site_root / (path.lstrip("/") + "index.html")
        else:
            file_path = site_root / (path.lstrip("/") + ".html")
        if not file_path.exists():
            missing.append(str(file_path))
    return missing


def render_standalone_entry(path: str, priority: float) -> str:
    loc = BASE + path
    return (
        f"  <url>\n"
        f"    <loc>{escape(loc)}</loc>\n"
        f"    <lastmod>{TODAY}</lastmod>\n"
        f"    <priority>{priority:.2f}</priority>\n"
        f"  </url>"
    )


def verify_files_exist(site_root: Path) -> list[str]:
    """Sanity check: every expected file exists on disk."""
    missing = []
    for shape, _ in PAGE_SHAPES:
        for lang in LANGS:
            rel = expand(shape, lang).lstrip("/")
            # URL ends in / → index.html
            file_path = site_root / (rel + "index.html")
            if not file_path.exists():
                missing.append(str(file_path))
    return missing


def render_url_entry(shape: str, priority: float) -> str:
    """Emit one <url> block with hreflang alternates for all 4 languages."""
    per_lang = {l: BASE + expand(shape, l) for l in LANGS}
    alternates = "\n".join(
        f'    <xhtml:link rel="alternate" hreflang="{OG_HREFLANG[l]}" href="{escape(u)}"/>'
        for l, u in per_lang.items()
    )
    # Use PT URL as the <loc>; emit one entry per language.
    blocks = []
    for lang in LANGS:
        blocks.append(
            f"  <url>\n"
            f"    <loc>{escape(per_lang[lang])}</loc>\n"
            f"    <lastmod>{TODAY}</lastmod>\n"
            f"    <priority>{priority:.2f}</priority>\n"
            f"{alternates}\n"
            f"    <xhtml:link rel=\"alternate\" hreflang=\"x-default\" href=\"{escape(per_lang['pt'])}\"/>\n"
            f"  </url>"
        )
    return "\n".join(blocks)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    site_root = root / "site"

    missing = verify_files_exist(site_root) + verify_standalone_files_exist(site_root)
    if missing:
        print("ERROR — sitemap shapes reference missing files:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        return 1

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for shape, priority in PAGE_SHAPES:
        out.append(render_url_entry(shape, priority))
    for path, priority in STANDALONE_PAGES:
        out.append(render_standalone_entry(path, priority))
    out.append("</urlset>")
    out.append("")  # trailing newline

    target = site_root / "sitemap.xml"
    target.write_text("\n".join(out), encoding="utf-8")

    n = len(PAGE_SHAPES) * len(LANGS) + len(STANDALONE_PAGES)
    print(f"wrote {target.relative_to(root)} — {n} URLs "
          f"({len(PAGE_SHAPES)} page shapes × {len(LANGS)} languages + {len(STANDALONE_PAGES)} standalone)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""CyberFuturo Index — arXiv AI research velocity.

Fetches monthly submission counts for cs.AI OR cs.LG from the arXiv API
for the trailing 24 full months and writes:

  data/indices/arxiv-ai-velocity.csv   — raw time series
  data/indices/arxiv-ai-velocity.svg   — rendered chart

Dependencies: Python stdlib only. No external packages.

Methodology:
  - Query: (cat:cs.AI OR cat:cs.LG) AND submittedDate:[start TO end]
  - Unit: papers first-submitted within the calendar month (UTC)
  - Source: https://export.arxiv.org/api/query
  - Dedup: arXiv's own OR query returns unique entries, not sum of categories
  - Rate limit: 3s between requests (arXiv asks nicely for ~1 req / 3s)

Run:
  python3 scripts/build_index_arxiv_ai.py
"""

from __future__ import annotations

import calendar
import csv
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

ARXIV_ENDPOINT = "https://export.arxiv.org/api/query"
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}
USER_AGENT = "CyberFuturoIndex/0.1 (https://cyberfuturo.com)"
RATE_LIMIT_SECONDS = 3.1
REQUEST_TIMEOUT = 30

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "data" / "indices" / "arxiv-ai-velocity.csv"
SVG_PATH = REPO_ROOT / "data" / "indices" / "arxiv-ai-velocity.svg"

MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10 MiB — reject abnormally large payloads


def month_window(year: int, month: int) -> tuple[str, str]:
    last_day = calendar.monthrange(year, month)[1]
    start = f"{year:04d}{month:02d}010000"
    end = f"{year:04d}{month:02d}{last_day:02d}2359"
    return start, end


def trailing_months(end_year: int, end_month: int, n: int) -> list[tuple[int, int]]:
    months: list[tuple[int, int]] = []
    y, m = end_year, end_month
    for _ in range(n):
        months.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    months.reverse()
    return months


def fetch_count(year: int, month: int) -> int:
    start, end = month_window(year, month)
    query = f"(cat:cs.AI OR cat:cs.LG) AND submittedDate:[{start} TO {end}]"
    params = {"search_query": query, "start": "0", "max_results": "1"}
    url = f"{ARXIV_ENDPOINT}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        payload = resp.read(MAX_RESPONSE_BYTES + 1)
    if len(payload) > MAX_RESPONSE_BYTES:
        raise RuntimeError(
            f"arXiv response exceeded {MAX_RESPONSE_BYTES} bytes; aborting to "
            f"avoid processing untrusted oversized XML."
        )
    # Parse with an explicit XMLParser rather than bare ET.fromstring() to make
    # the security posture explicit.  Python 3.9+ already limits entity
    # expansion in the default expat parser, but we call out the concern here:
    # stdlib xml.etree does NOT fully defend against billion-laughs on all
    # builds.  The MAX_RESPONSE_BYTES check above is the primary mitigation
    # for untrusted arXiv XML when defusedxml is unavailable (ADR-0002:
    # stdlib-only constraint).
    parser = ET.XMLParser()
    parser.feed(payload)
    root = parser.close()
    total_el = root.find("opensearch:totalResults", NS)
    if total_el is None or total_el.text is None:
        raise RuntimeError(f"arXiv returned no totalResults for {year}-{month:02d}")
    return int(total_el.text)


def write_csv(rows: list[tuple[str, int]]) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", "papers"])
        for month, count in rows:
            w.writerow([month, count])


def render_svg(rows: list[tuple[str, int]]) -> None:
    width, height = 860, 460
    ml, mr, mt, mb = 80, 30, 70, 70
    plot_w = width - ml - mr
    plot_h = height - mt - mb

    counts = [c for _, c in rows]
    ymin = 0
    ymax_raw = max(counts)
    # round ymax up to a nice gridline
    mag = 10 ** (len(str(ymax_raw)) - 1)
    ymax = ((ymax_raw // mag) + 1) * mag

    n = len(rows)
    def x(i: int) -> float:
        return ml + (plot_w * i) / max(n - 1, 1)

    def y(val: int) -> float:
        return mt + plot_h - (plot_h * (val - ymin) / (ymax - ymin))

    title = "arXiv AI research velocity — monthly submissions (cs.AI OR cs.LG)"
    subtitle = f"Trailing {n} months · Source: arXiv API · CyberFuturo Index"

    lines: list[str] = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'font-family="-apple-system, system-ui, Segoe UI, sans-serif">'
    )
    # background
    lines.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')

    # title
    lines.append(
        f'<text x="{ml}" y="28" font-size="17" font-weight="600" fill="#0f172a">{title}</text>'
    )
    lines.append(
        f'<text x="{ml}" y="48" font-size="12" fill="#64748b">{subtitle}</text>'
    )

    # Y gridlines + labels (5 steps)
    steps = 5
    for i in range(steps + 1):
        val = ymin + (ymax - ymin) * i / steps
        gy = y(val)
        lines.append(
            f'<line x1="{ml}" y1="{gy:.1f}" x2="{width - mr}" y2="{gy:.1f}" '
            f'stroke="#e2e8f0" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{ml - 10}" y="{gy + 4:.1f}" font-size="11" fill="#64748b" '
            f'text-anchor="end">{int(val):,}</text>'
        )

    # X axis baseline
    lines.append(
        f'<line x1="{ml}" y1="{mt + plot_h}" x2="{width - mr}" y2="{mt + plot_h}" '
        f'stroke="#94a3b8" stroke-width="1"/>'
    )

    # X labels: show every 3rd month to avoid overlap
    for i, (month, _) in enumerate(rows):
        if i % 3 == 0 or i == n - 1:
            lines.append(
                f'<text x="{x(i):.1f}" y="{mt + plot_h + 18}" font-size="11" '
                f'fill="#64748b" text-anchor="middle">{month}</text>'
            )

    # Data polyline
    pts = " ".join(f"{x(i):.1f},{y(c):.1f}" for i, (_, c) in enumerate(rows))
    lines.append(
        f'<polyline fill="none" stroke="#1e40af" stroke-width="2.5" '
        f'stroke-linejoin="round" stroke-linecap="round" points="{pts}"/>'
    )

    # Data dots
    for i, (_, c) in enumerate(rows):
        lines.append(
            f'<circle cx="{x(i):.1f}" cy="{y(c):.1f}" r="3.5" fill="#1e40af"/>'
        )

    # Y axis label
    lines.append(
        f'<text x="{ml - 60}" y="{mt + plot_h / 2:.1f}" font-size="11" '
        f'fill="#64748b" text-anchor="middle" '
        f'transform="rotate(-90 {ml - 60} {mt + plot_h / 2:.1f})">papers / month</text>'
    )

    # Footer caption with latest value
    latest_month, latest_count = rows[-1]
    first_count = rows[0][1]
    pct = ((latest_count - first_count) / first_count) * 100 if first_count else 0
    caption = (
        f"{latest_month}: {latest_count:,} papers · "
        f"{pct:+.0f}% vs {rows[0][0]}"
    )
    lines.append(
        f'<text x="{ml}" y="{height - 22}" font-size="12" fill="#0f172a" '
        f'font-weight="500">{caption}</text>'
    )
    lines.append(
        f'<text x="{ml}" y="{height - 8}" font-size="10" fill="#94a3b8">'
        f'cyberfuturo.com — how fast the future is arriving, by the numbers</text>'
    )

    lines.append("</svg>")
    SVG_PATH.parent.mkdir(parents=True, exist_ok=True)
    SVG_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    today = date.today()
    # Last full month = month before current month
    if today.month == 1:
        end_year, end_month = today.year - 1, 12
    else:
        end_year, end_month = today.year, today.month - 1

    months = trailing_months(end_year, end_month, 24)
    print(
        f"Fetching arXiv cs.AI OR cs.LG counts for "
        f"{months[0][0]}-{months[0][1]:02d} through "
        f"{months[-1][0]}-{months[-1][1]:02d}",
        file=sys.stderr,
    )

    rows: list[tuple[str, int]] = []
    for idx, (y, m) in enumerate(months):
        count = fetch_count(y, m)
        label = f"{y:04d}-{m:02d}"
        rows.append((label, count))
        print(f"  {label}: {count:,}", file=sys.stderr)
        if idx < len(months) - 1:
            time.sleep(RATE_LIMIT_SECONDS)

    write_csv(rows)
    render_svg(rows)
    print(f"\nWrote {CSV_PATH}", file=sys.stderr)
    print(f"Wrote {SVG_PATH}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

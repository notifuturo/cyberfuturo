"""CyberFuturo Index — x402 repository velocity.

Fetches monthly counts of new, non-fork GitHub repositories matching
"x402" in name, description, or topics for the trailing 24 full months
and writes:

  data/indices/x402-repo-velocity.csv   — raw time series
  data/indices/x402-repo-velocity.svg   — rendered chart

Dependencies: Python stdlib only. No external packages.

Methodology:
  - Query: x402 in:name,description,topics created:{start}..{end} fork:false
  - Unit: repositories first created within the calendar month (UTC)
  - Source: https://api.github.com/search/repositories
  - Auth: GITHUB_TOKEN env var if set (CI supplies this automatically via
    the built-in Actions token; raises the search rate limit from 10 to 30
    requests/min). Unauthenticated works too, just slower.
  - Rate limit: 3.1s between requests (mirrors the arXiv pipeline's
    politeness margin; comfortably under both the authenticated and
    unauthenticated GitHub search limits)

Run:
  python3 scripts/build_index_x402_repos.py
"""

from __future__ import annotations

import calendar
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _svg_chart import render_svg as _render_svg  # noqa: E402

GITHUB_SEARCH_ENDPOINT = "https://api.github.com/search/repositories"
USER_AGENT = "CyberFuturoIndex/0.1 (https://cyberfuturo.com)"
RATE_LIMIT_SECONDS = 3.1
REQUEST_TIMEOUT = 30

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "data" / "indices" / "x402-repo-velocity.csv"
SVG_PATH = REPO_ROOT / "data" / "indices" / "x402-repo-velocity.svg"

MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10 MiB — reject abnormally large payloads


def month_window(year: int, month: int) -> tuple[str, str]:
    last_day = calendar.monthrange(year, month)[1]
    start = f"{year:04d}-{month:02d}-01"
    end = f"{year:04d}-{month:02d}-{last_day:02d}"
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
    query = f"x402 in:name,description,topics created:{start}..{end} fork:false"
    params = {"q": query, "per_page": "1"}
    url = f"{GITHUB_SEARCH_ENDPOINT}?{urllib.parse.urlencode(params)}"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        payload = resp.read(MAX_RESPONSE_BYTES + 1)
    if len(payload) > MAX_RESPONSE_BYTES:
        raise RuntimeError(
            f"GitHub search response exceeded {MAX_RESPONSE_BYTES} bytes; aborting to "
            f"avoid processing an untrusted oversized payload."
        )
    data = json.loads(payload)
    if "total_count" not in data:
        raise RuntimeError(f"GitHub search returned no total_count for {year}-{month:02d}: {data}")
    return int(data["total_count"])


def write_csv(rows: list[tuple[str, int]]) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["month", "repos"])
        for month, count in rows:
            w.writerow([month, count])


def render_svg(rows: list[tuple[str, int]]) -> None:
    _render_svg(
        rows,
        SVG_PATH,
        title="x402 repository velocity — new repos/month (name, description, or topic)",
        source_label="GitHub Search API",
        unit_label="new repos / month",
    )


def main() -> int:
    today = date.today()
    if today.month == 1:
        end_year, end_month = today.year - 1, 12
    else:
        end_year, end_month = today.year, today.month - 1

    months = trailing_months(end_year, end_month, 24)
    print(
        f"Fetching GitHub x402-repo counts for "
        f"{months[0][0]}-{months[0][1]:02d} through "
        f"{months[-1][0]}-{months[-1][1]:02d}",
        file=sys.stderr,
    )
    if not os.environ.get("GITHUB_TOKEN"):
        print("  (no GITHUB_TOKEN set — running unauthenticated, 10 req/min search limit)", file=sys.stderr)

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

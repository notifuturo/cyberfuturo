"""Shared inline-SVG line-chart renderer for CyberFuturo indices.

Extracted from the arXiv AI velocity pipeline (v0.1) when the second index
(x402 repo velocity) needed the identical chart shape. Every CyberFuturo
index renders the same way: a 24-point (or N-point) monthly time series,
one line, one caption with the latest value and pct-change since the first
point. Keeping this in one place means a chart-styling change updates every
index at once instead of drifting between per-index copies.

Python stdlib only (ADR-0002). No behavior change from the original
inline version in build_index_arxiv_ai.py — ported verbatim.
"""

from __future__ import annotations

from pathlib import Path


def render_svg(rows: list[tuple[str, int]], svg_path: Path, title: str, source_label: str, unit_label: str) -> None:
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

    subtitle = f"Trailing {n} months · Source: {source_label} · CyberFuturo Index"

    lines: list[str] = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'font-family="-apple-system, system-ui, Segoe UI, sans-serif">'
    )
    lines.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')

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

    pts = " ".join(f"{x(i):.1f},{y(c):.1f}" for i, (_, c) in enumerate(rows))
    lines.append(
        f'<polyline fill="none" stroke="#1e40af" stroke-width="2.5" '
        f'stroke-linejoin="round" stroke-linecap="round" points="{pts}"/>'
    )

    for i, (_, c) in enumerate(rows):
        lines.append(
            f'<circle cx="{x(i):.1f}" cy="{y(c):.1f}" r="3.5" fill="#1e40af"/>'
        )

    lines.append(
        f'<text x="{ml - 60}" y="{mt + plot_h / 2:.1f}" font-size="11" '
        f'fill="#64748b" text-anchor="middle" '
        f'transform="rotate(-90 {ml - 60} {mt + plot_h / 2:.1f})">{unit_label}</text>'
    )

    latest_month, latest_count = rows[-1]
    first_count = rows[0][1]
    if first_count:
        pct = ((latest_count - first_count) / first_count) * 100
        caption = f"{latest_month}: {latest_count:,} · {pct:+.0f}% vs {rows[0][0]}"
    else:
        # A 0 → N change has no defined percentage — showing "+0%" would
        # misread as "no change" when the truth is the opposite. State the
        # raw endpoints instead of fabricating a ratio.
        caption = f"{latest_month}: {latest_count:,} · {rows[0][0]} was {first_count:,}"
    lines.append(
        f'<text x="{ml}" y="{height - 22}" font-size="12" fill="#0f172a" '
        f'font-weight="500">{caption}</text>'
    )
    lines.append(
        f'<text x="{ml}" y="{height - 8}" font-size="10" fill="#94a3b8">'
        f'cyberfuturo.com — how fast the future is arriving, by the numbers</text>'
    )

    lines.append("</svg>")
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text("\n".join(lines), encoding="utf-8")

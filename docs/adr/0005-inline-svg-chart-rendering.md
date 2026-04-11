# ADR-0005: In-pipeline SVG chart rendering

- **Status**: Accepted
- **Date**: 2026-04-11

## Context

Every CyberFuturo index produces a chart. Charts are embedded in briefs, on the landing page, and in emails. We needed to decide how the chart is rendered.

Options considered (in order of increasing framework dependency):

1. **Pipeline-emitted SVG** (strings produced by the Python ingestion script)
2. **matplotlib.savefig()** to PNG or SVG
3. **Plotly / Vega-Lite** rendered statically via their Python APIs
4. **Client-side JavaScript charts** (Observable Plot, ECharts, D3)
5. **External chart-as-a-service** (QuickChart, Image-charts)

Each layer adds a dependency surface that contradicts ADR-0002 (stdlib only) and introduces reproducibility risk over multi-year timelines.

We also looked at what chart features we actually need for a measurement-first publication (ADR-0001):

- Line chart with data points
- X axis (month labels)
- Y axis with gridlines
- Title and subtitle
- Source attribution
- One optional highlight or annotation

That's all. We do not need: interactive tooltips, zoom, pan, multi-axis, animation, color palettes, legends with 10+ series, or 3D.

## Decision

**Charts are rendered as SVG strings directly in the Python pipeline, using only stdlib.** No chart library. No client-side JS.

The renderer function lives next to the data-fetch function in the same script. It takes the CSV rows and produces an SVG file. That's the entire dependency chain: `str.format` → `svg` → `cp to site/data/`.

See `scripts/build_index_arxiv_ai.py::render_svg()` for the reference implementation (~70 lines).

## Consequences

### Positive
- **Charts are text.** Diffable in git. `git log -p data/indices/*.svg` shows exactly how the chart changed between runs.
- **Perfectly reproducible.** Two machines running the same script against the same data produce byte-identical SVG output. No font rendering variability, no anti-aliasing differences, no matplotlib backend drift.
- **One HTTP request per chart.** SVG is inlined once, cached by Cloudflare, loads in a single round trip.
- **Infinitely scalable.** SVG is resolution-independent. No "@2x" / retina variants to maintain.
- **Embeddable everywhere.** SVG works in browsers, email clients that support SVG, Markdown viewers, GitHub, LinkedIn, Notion, and PDF exports.
- **Accessible.** We can add `<title>`, `<desc>`, and ARIA attributes for screen readers directly in the string template.

### Negative
- **Every chart type is hand-coded.** A new chart shape (stacked bar, scatter, heatmap) means writing a new `render_*()` function. At v0.1 scale (3-5 indices, mostly line charts) this is fine. If we grow to 30+ indices of varied shapes we will re-evaluate.
- **No hover tooltips.** Readers can't click on a data point to see the exact value. Acceptable tradeoff: we list the latest value in the caption and the full series is a one-click CSV download.
- **Requires thinking about layout math.** Margins, axis scaling, gridlines — all manual. The reference renderer contains that math and can be copied for new charts.

### Neutral
- **No color palette system yet.** We use one accent color (`#1e40af`) for the first index and will formalize a small palette (~6 colors) if a brief ever compares multiple indices on one chart.

## Non-goals

- Interactive exploration. Readers who want to drill into the time series download the CSV.
- Animation. Static charts are a feature, not a limitation — they preserve the "measurement" mental model.
- Styling parity with Bloomberg / FT. We aim for functional clarity, not editorial design-system polish.

## Alternatives considered

- **matplotlib** — rejected per ADR-0002 (dependency), and font/backend variability hurts reproducibility.
- **Plotly (static export)** — rejected; adds kaleido binary dep and a full JS runtime for what we need.
- **Vega-Lite / Altair** — interesting spec-based approach, but the renderer still depends on a JS runtime or Java.
- **ECharts / D3 (client-side)** — rejected per ADR-0003 (no JavaScript).
- **QuickChart.io / image-charts.com** — rejected. Introduces a runtime dep on a third-party service that could disappear, adds latency, and leaks our queries to a vendor.
- **Pre-rendered PNGs from a local headless browser** — rejected as engineering overkill and reproducibility risk.

## Related ADRs

- [ADR-0002 — Python stdlib-only pipeline](./0002-python-stdlib-only-pipeline.md) — the constraint this ADR operationalizes for charts
- [ADR-0003 — Static site, no JS framework](./0003-static-site-no-js-framework.md) — the site context the chart lives in

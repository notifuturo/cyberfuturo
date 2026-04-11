# ADR-0002: Python stdlib-only ingestion pipeline (v0.1)

- **Status**: Accepted (for v0.1 and v0.2)
- **Date**: 2026-04-11

## Context

The ingestion layer needs to:

1. Pull data from public APIs (arXiv, NIST NVD, GitHub Advisory, SEC EDGAR, FRED, etc.)
2. Parse JSON, XML, CSV
3. Compute basic statistics (sums, averages, YoY)
4. Render line charts
5. Write CSV and SVG outputs
6. Run in GitHub Actions on a monthly cron

The obvious default stack is `requests + pandas + matplotlib`. But that stack has real costs at our scale:

- **Supply chain surface**: three top-level deps → ~150 transitive deps → hundreds of annual updates → regular security advisories → need for Dependabot, lockfiles, and CI policy
- **Reproducibility decay**: numpy/pandas major-version migrations have historically broken reproducibility of old scripts. CyberFuturo's *entire value proposition* is reproducibility over multi-year timelines — we cannot afford silent dep-induced drift in our data.
- **CI cold-start time**: `pip install pandas matplotlib` on every cron run is 30+ seconds of wall time. Caching works but is one more thing to maintain.
- **Chart render variability**: matplotlib depends on system fonts, backends, and rendering pipelines. Two different machines can produce visually different outputs from identical input.

## Decision

**The CyberFuturo ingestion and rendering pipeline uses only Python 3.11+ stdlib. No third-party packages.**

Modules in use: `urllib`, `xml.etree.ElementTree`, `csv`, `datetime`, `calendar`, `pathlib`, `time`, `sys`. That's all.

This applies to v0.1 and v0.2. We will re-evaluate for v0.3+ if and only if a specific index genuinely cannot be built in stdlib.

## Consequences

### Positive
- **Zero supply chain risk.** There is no `requirements.txt`, no `pip install`, no lockfile. `python3 scripts/build_index_arxiv_ai.py` is the entire dependency story.
- **Reproducible across decades.** Python stdlib is extraordinarily stable. A script that runs today will almost certainly run unchanged in 2036.
- **Small, readable scripts.** Forces us to write the ~20 lines of code pandas would hide behind a one-liner. Those 20 lines are auditable.
- **Fast CI cold-start.** GitHub Actions Python setup takes ~5s. No package install step.
- **Charts as text.** SVG rendered from string concatenation is git-diffable. We can see exactly what changed between two runs.

### Negative
- **More code per feature.** A monthly GROUP BY in pandas is three lines; in stdlib it's a `defaultdict` loop. We accept this.
- **Charts look less fancy.** No gradients, no animations, no interactive tooltips. Our charts are deliberately minimal anyway (ADR-0005).
- **Limits some advanced analysis.** Statistical methods like STL decomposition, ARIMA, kernel density estimation require third-party libs. We're a measurement publication, not a forecasting one (ADR-0001), so most of this would violate our principles anyway.

### Neutral
- The one script we've written so far (`scripts/build_index_arxiv_ai.py`) is 185 lines and handles fetch + parse + transform + chart + CSV output. That's a reasonable upper bound on per-index complexity.

## Alternatives considered

- **`requests + pandas + matplotlib`.** Rejected for the reasons above.
- **`httpx + polars + plotnine`.** Rejected. Newer stack, same underlying problems.
- **Node.js (TypeScript + fetch + vega-lite).** Rejected. Adds a second language ecosystem, and vega-lite charts depend on JavaScript render. We want pipeline output to be static SVG text.
- **Rust.** Rejected as over-engineering for ~200 lines per index.
- **Go.** Rejected for the same reason; also, XML and CSV handling in Python stdlib is more ergonomic.

## Enforcement

- `scripts/` contains only stdlib imports. Any PR that adds a third-party import must also add a new ADR superseding this one.
- CI will eventually run `python3 -c "import ast; ..."` to enforce stdlib-only imports at PR time (v0.2).

## Related ADRs

- [ADR-0005 — In-pipeline SVG chart rendering](./0005-inline-svg-chart-rendering.md) is a direct consequence of this decision.

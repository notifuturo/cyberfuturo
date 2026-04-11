# CyberFuturo #01 — AI research velocity

*2026-04-11 · ~4-minute read*

**Cited indices**: `arxiv-ai-velocity v0.1`
**Data**: [`arxiv-ai-velocity.csv`](../../data/indices/arxiv-ai-velocity.csv) · [Methodology](../../src/indices/arxiv-ai-velocity/methodology.md)
**Editorial mode**: human-edited, AI-assisted prose · deterministic pipeline · no LLM touched the numbers

---

## The number

**7,406** — new AI/ML papers submitted to arXiv in **March 2026** [`arxiv-ai-velocity v0.1`].

The highest monthly value in our 24-month tracking window, and **+79%** over April 2024 (4,130).

![arXiv AI research velocity, trailing 24 months](../../data/indices/arxiv-ai-velocity.svg)

## What moved

Three observations the headline number does not convey on its own.

### 1. The YoY rate is ~28%, not 79%

The two-year doubling is compounding, not acceleration. Trailing-12 vs prior-12:

- April 2025 → March 2026: **6,529 papers/month average**
- April 2024 → March 2025: **5,119 papers/month average**
- **+27.5% year-over-year**

Faster than global GDP, faster than cloud-compute spend, faster than almost any macro indicator — and meaningfully below the "exponential takeoff" framing common in press coverage.

### 2. Volatility is structural

Compare August 2024 (3,981) with May 2025 (7,886) — a near 2× swing within a single year. arXiv submissions cluster around conference deadlines (NeurIPS, ICML, ICLR, CVPR). A single month's count moves more from seasonal deadline clustering than from any underlying shift in the field. Read the 6-month moving average or the YoY rate, not individual months, to infer direction.

### 3. Q1 2026 is the highest-volume Q1 in the window

- January: 6,502
- February: 7,284
- March: 7,406
- **Q1 2026 average: 7,064 papers/month**
- Q1 2025 average: 5,524
- **+27.9% Q1-over-Q1**

The acceleration rate is holding, not decelerating, as of the most recent month we can measure.

## What this is not

This is one data point from one source. It does not measure paper quality, reproducibility, novelty, industrial vs. academic distribution, or whether the research matters. It is a raw volumetric indicator of AI/ML research submission velocity on arXiv, counted by first-submission date.

Any claim that goes beyond that — capability scaling, model quality, "AI is speeding up / slowing down" as a civilizational pattern — is interpretation layered on top of this number, not the number itself. If you see such a claim citing this index, treat the claim as opinion, not as measurement.

## How this was built

Every index in CyberFuturo is deterministic: a documented query against a public API, run on a schedule, stored as CSV, rendered to SVG. No LLM generated any number in this brief. No outputs were estimated, interpolated, or rounded by a language model.

Editorial prose (the words you are reading) was **drafted with AI assistance and human-edited**. The numbers and chart were not. The full rules governing this split are documented in [our editorial rules](https://cyberfuturo.pages.dev/rules).

- Full source: [`scripts/build_index_arxiv_ai.py`](https://github.com/notifuturo/cyberfuturo/blob/main/scripts/build_index_arxiv_ai.py)
- Methodology and known limitations: [`arxiv-ai-velocity v0.1` methodology](../../src/indices/arxiv-ai-velocity/methodology.md)

## Next

The next brief cites two more indices already in development: **global compute capex** and **battery $/kWh**. Both follow the same pipeline pattern as this one — public source, deterministic query, versioned methodology, CSV and SVG outputs, no LLM-generated numbers.

If you want to follow along, subscribe below. If you spot a methodology problem, reply to this email or open an issue on the repo. Corrections appear in the next brief with a changelog entry.

---

## Sources

| Claim | Index | Version | Source |
|---|---|---|---|
| 7,406 papers in March 2026 | `arxiv-ai-velocity` | v0.1 | [arXiv API](https://export.arxiv.org/api/query) |
| 4,130 papers in April 2024 | `arxiv-ai-velocity` | v0.1 | [arXiv API](https://export.arxiv.org/api/query) |
| 5,119 prior-12 avg · 6,529 trailing-12 avg · +27.5% YoY | `arxiv-ai-velocity` | v0.1 | computed from [canonical CSV](../../data/indices/arxiv-ai-velocity.csv) |
| Q1 2026 avg 7,064 · Q1 2025 avg 5,524 · +27.9% | `arxiv-ai-velocity` | v0.1 | computed from [canonical CSV](../../data/indices/arxiv-ai-velocity.csv) |
| August 2024: 3,981 · May 2025: 7,886 | `arxiv-ai-velocity` | v0.1 | [canonical CSV](../../data/indices/arxiv-ai-velocity.csv) |

Every number above is traceable in three clicks: this brief → canonical CSV → arXiv API query documented in methodology.

---

*CyberFuturo — how fast the future is arriving, by the numbers.*

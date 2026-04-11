# Index: arXiv AI research velocity

- **Slug**: `arxiv-ai-velocity`
- **Current version**: `v0.1`
- **Unit**: papers submitted per calendar month (UTC)
- **Cadence**: monthly, refreshed on the 2nd of each month
- **Window**: trailing 24 calendar months
- **Source**: [arXiv API](https://export.arxiv.org/api/query)
- **License**: arXiv metadata is public; this derived index is released under CC-BY-4.0
- **Active as of**: 2026-04-11

---

## What this measures

The count of distinct papers first submitted to arXiv within a given calendar month whose primary or secondary category is either `cs.AI` (Artificial Intelligence) or `cs.LG` (Machine Learning).

Read it as: a raw velocity signal for the AI/ML research surface area — how many new papers are being produced per month.

## What this does not measure

- Paper quality, novelty, or reproducibility
- Citation impact
- Whether research is original or derivative
- Industrial vs. academic output
- Geographic distribution
- Duplicate, withdrawn, or replaced papers (v0.1 — see Known limitations)

If you want any of those, combine this index with other sources. On its own it is a volumetric indicator, nothing more.

## Exact query

For each calendar month in the trailing 24-month window:

```
(cat:cs.AI OR cat:cs.LG) AND submittedDate:[YYYYMMDD0000 TO YYYYMMDDHHMM2359]
```

Evaluated against `https://export.arxiv.org/api/query`. Count is read from the `opensearch:totalResults` element of the returned Atom XML response.

**Deduplication**: arXiv's search backend returns unique entries for OR queries across categories. A paper cross-listed in both `cs.AI` and `cs.LG` is counted once per query.

**Rate limit**: 3.1 seconds between requests (arXiv polite-use guidance).

## Pipeline

Source: [`scripts/build_index_arxiv_ai.py`](../../../scripts/build_index_arxiv_ai.py)

```
arXiv API → XML parse → monthly counts → CSV → SVG
```

Implementation: Python 3.11+ stdlib only. No third-party dependencies. Roughly 185 lines of code. Fully reproducible from a clean Python environment in ~75 seconds.

## Outputs

| File | Purpose | Overwritten each run? |
|---|---|---|
| `data/indices/arxiv-ai-velocity.csv` | Canonical time series | Yes |
| `data/indices/arxiv-ai-velocity.svg` | Rendered line chart | Yes |
| `site/data/arxiv-ai-velocity.csv` | Public mirror for site | Yes |
| `site/data/arxiv-ai-velocity.svg` | Public mirror for site | Yes |

Git history preserves every past state — that is the audit trail for any brief that cited a specific value at publication time.

## Output schema

Canonical CSV: `data/indices/arxiv-ai-velocity.csv`

| Column | Type | Example | Constraint |
|---|---|---|---|
| `month` | string (`YYYY-MM`) | `2026-03` | Always a valid calendar month in the trailing 24-month window |
| `papers` | integer | `7406` | ≥ 0; derived from `opensearch:totalResults` as a non-negative integer |

File-level invariants:
- Header row is exactly `month,papers`
- Rows are sorted chronologically ascending
- Exactly 24 data rows
- Values are UTF-8 encoded, LF line endings, no BOM

## Known limitations (v0.1)

1. **No resubmission handling.** arXiv `submittedDate` refers to first submission; papers replaced or updated within a month may or may not recount depending on arXiv index behavior. Future work: verify against a second query method.
2. **No withdrawal filter.** Papers later withdrawn are still counted in the month they were first submitted. This is the correct behavior for a velocity signal but worth stating.
3. **No seasonality adjustment.** The raw series shows conference-deadline clustering (NeurIPS, ICML, ICLR, CVPR). A seasonally adjusted variant is planned for v0.2.
4. **Category overlap with non-AI fields.** `cs.LG` includes some papers that are ML-method applied to non-AI domains. We accept this noise as part of the definition.
5. **Single-point-in-time snapshots.** arXiv backfills corrections and reclassifications. See [ADR-0010](../../../docs/adr/0010-trailing-window-time-series.md).
6. **Timezone**: arXiv UTC. No adjustment.

## Changelog

- **v0.1 — 2026-04-11** — Initial release. 24-month trailing window, monthly cadence, stdlib-only pipeline, SVG rendering. First cited by [CyberFuturo Issue #01](../../../docs/briefs/issue-01.md).

Methodology changes bump the version and append here. Historical CSV values are preserved in git so briefs citing older versions remain verifiable.

## How to reproduce

```bash
git clone https://github.com/notifuturo/cyberfuturo
cd cyberfuturo
python3 scripts/build_index_arxiv_ai.py
# Writes data/indices/arxiv-ai-velocity.{csv,svg}
# Takes ~75 seconds (24 requests at 3.1s rate limit)
```

Zero third-party packages. No API keys. No environment variables.

## Deprecation criteria

Per business rule BR-11, every index has pre-committed conditions for deprecation, renaming, or retirement.

This index is deprecated when **any one** of the following becomes true:

1. **Source deprecation** — arXiv removes or rate-limits the public `/api/query` endpoint, or requires authentication that blocks free-tier usage
2. **Source drift beyond tolerance** — consecutive weekly re-snapshots (planned v0.2) show >3% drift on month values older than 12 months, indicating backfill behavior that breaks the trailing-window assumption
3. **Category restructuring** — arXiv reorganizes the `cs.AI` / `cs.LG` hierarchy in a way that makes a single query no longer meaningful (e.g. a new `cs.AGI` category that absorbs a significant fraction of submissions)
4. **Measurement becomes unrepresentative** — if AI/ML research shifts away from arXiv to a successor preprint server, and the arXiv count no longer reflects the broader phenomenon the index claims to measure
5. **Replaced by a better version** — a v2.x index with the same slug and stricter methodology (e.g. seasonally adjusted + dedup against replacement papers) can supersede v0.x

Deprecation process:

- Publish a final snapshot at the deprecation moment, versioned and frozen
- Announce in the next brief with explicit reasoning
- Move the CSV/SVG to `data/indices/archived/<slug>/` and keep forever
- Strike through the index on the methodology index page with a link to the final snapshot and the announcement brief
- Leave the methodology document in place with a "deprecated on [date], superseded by [new-slug]" banner at the top

The index is never silently removed. Every deprecation is logged in the changelog of this document.

## Contact

Methodology errors, data disputes, or reproducibility problems: open an issue on the repo or reply to any brief that cites this index. Corrections are published in the next brief with a changelog entry.

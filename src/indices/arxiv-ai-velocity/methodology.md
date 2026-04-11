# Index: arXiv AI Research Velocity

**Slug**: `arxiv-ai-velocity`
**Unit**: papers submitted per calendar month (UTC)
**Cadence**: monthly, refreshed on the 2nd of each month (measuring the previous full month)
**Coverage**: trailing 24 calendar months
**Source**: [arXiv API](https://export.arxiv.org/api/query)
**License**: arXiv metadata is public. This derived index is released under CC-BY-4.0.

---

## What this measures

The number of distinct papers first submitted to arXiv within a given calendar month whose primary or secondary category is either `cs.AI` (Artificial Intelligence) or `cs.LG` (Machine Learning).

**Read it as**: a raw velocity signal for the AI/ML research surface area — how many new papers are being produced per month. Nothing more.

---

## What this does NOT measure

- Paper *quality*, novelty, or reproducibility
- Citation impact
- Whether the research is original or iterative
- Industrial vs. academic output
- Geographic distribution
- Duplicate / withdrawn / replaced papers (v1 only — see "Known limitations")

If you want any of those, combine this index with other sources. On its own it's a volumetric indicator.

---

## Exact query

```
(cat:cs.AI OR cat:cs.LG) AND submittedDate:[YYYYMMDD0000 TO YYYYMMDDHHMM2359]
```

Evaluated via the arXiv public API at `https://export.arxiv.org/api/query`, one request per calendar month. The total count is read from the `opensearch:totalResults` element of the Atom response.

**Dedup**: arXiv's search backend returns unique entries for OR queries across categories. Papers cross-listed in both `cs.AI` and `cs.LG` are counted once per query.

**Rate limit**: 3.1 seconds between requests to respect arXiv's polite-use guidance.

---

## Pipeline (v0.1)

```
arXiv API  →  XML parse (stdlib)  →  monthly counts  →  CSV  →  SVG
```

Source: [`scripts/build_index_arxiv_ai.py`](../../../scripts/build_index_arxiv_ai.py)

The script uses only Python stdlib (urllib, xml.etree, csv). No third-party dependencies. Fully reproducible from a clean Python 3.11+ environment.

---

## Outputs

| File | Purpose |
|---|---|
| `data/indices/arxiv-ai-velocity.csv` | Canonical time series (`month,papers`) |
| `data/indices/arxiv-ai-velocity.svg` | Rendered line chart for embed |

Both files are overwritten on each run. Past versions live in git history — that's the audit trail.

---

## Known limitations (v0.1)

1. **No resubmission handling.** arXiv allows `submittedDate` to refer to first submission, but papers replaced/updated within a month may or may not recount depending on arXiv index behavior. Future work: verify against a second query method.
2. **No withdrawal filter.** Papers later withdrawn are still counted in the month they were first submitted. This is the correct behavior for a velocity signal but worth stating.
3. **No seasonality adjustment.** The raw series shows clear conference-deadline clustering (NeurIPS, ICML, ICLR, CVPR). A seasonally adjusted variant is planned for v0.2.
4. **Category overlap with non-AI fields.** `cs.LG` includes some papers that are machine-learning-method but applied to non-AI domains (physics, biology). We accept this noise as part of the definition.
5. **Single-point-in-time snapshots.** arXiv backfills corrections and reclassifications. A paper's category assignment can change. We do not currently re-fetch historical months, so older values may drift very slightly from arXiv's current totals. Planned for v0.2: weekly re-snapshot of the full window.
6. **Timezone.** Submission dates are in arXiv's UTC. No adjustment.

---

## Changelog

**v0.1 — 2026-04-11** — Initial release. 24-month trailing window, monthly cadence, stdlib-only pipeline, SVG rendering. First published as [CyberFuturo Issue #01](../../../docs/briefs/issue-01.md).

Methodology changes will be appended here with a version bump. Historical CSV values will be preserved in git so older briefs remain verifiable against the numbers they cited.

---

## How to reproduce

```bash
cd /path/to/cyberfuturo
python3 scripts/build_index_arxiv_ai.py
# Writes data/indices/arxiv-ai-velocity.{csv,svg}
# Takes ~75 seconds (24 requests at 3.1s rate limit)
```

No environment variables, no API keys, no external packages.

---

## Contact

If you find a methodology error, open an issue or reply to any CyberFuturo brief that cites this index. Corrections are published in the next issue with a changelog entry.

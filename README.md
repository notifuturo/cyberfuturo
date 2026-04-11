# CyberFuturo

**How fast the future is arriving, by the numbers.**

A small, rigorously defined set of indices tracking leading indicators across AI, compute, and energy — built from public data, reproducible methodology, no forecasts.

- 🌐 Site: [cyberfuturo.com](https://cyberfuturo.com) *(pending DNS cutover)*
- 📊 Live index: [arXiv AI research velocity](./docs/briefs/issue-01.md)
- 📁 Data: [`data/indices/`](./data/indices/)
- 🧮 Methodology: [`src/indices/`](./src/indices/)

---

## What this is

CyberFuturo publishes deterministic, documented, reproducible indices built from free public data. Every index has:

- A **documented query** against a public API
- A **methodology page** listing exactly what it measures and what it doesn't
- **Raw CSV** output so readers can verify or re-analyze
- A **version number** — methodology changes bump the version and log a changelog entry

We do not forecast. We do not interpret heavily. We publish measurements.

## Repo layout

```
cyberfuturo/
├── scripts/                    # Ingestion + transform scripts (stdlib-only Python)
│   └── build_index_arxiv_ai.py
├── data/
│   └── indices/
│       ├── arxiv-ai-velocity.csv
│       └── arxiv-ai-velocity.svg
├── src/
│   └── indices/
│       └── arxiv-ai-velocity/
│           └── methodology.md
├── site/                       # Static site, deployed to Cloudflare Pages
│   ├── index.html
│   ├── issues/01.html
│   ├── methodology/arxiv-ai-velocity.html
│   ├── data/                   # Chart + CSV (mirrored from data/indices/)
│   └── styles.css
├── docs/
│   ├── briefs/issue-01.md      # Markdown source of issue #01
│   └── deploy.md               # How to deploy the site
└── .github/workflows/
    └── refresh-arxiv.yml       # Monthly auto-refresh of the arXiv index
```

## Reproducing the arXiv index

Zero dependencies beyond Python 3.11+ stdlib:

```bash
python3 scripts/build_index_arxiv_ai.py
# Takes ~75 seconds (24 requests at 3.1s rate limit).
# Writes data/indices/arxiv-ai-velocity.{csv,svg}
```

See [`src/indices/arxiv-ai-velocity/methodology.md`](./src/indices/arxiv-ai-velocity/methodology.md) for the exact query and known limitations.

## Roadmap

- **v0.1** ✅ — Release: arXiv AI research velocity
- **v0.2** — Global compute capex (quarterly, from public filings)
- **v0.3** — Battery $/kWh (annual)
- **v0.4** — Seasonally-adjusted arXiv variant
- **v0.5** — Historical snapshot re-fetch + changelog-diffed values

## License

- **Code**: MIT
- **Derived indices (CSV, SVG)**: CC-BY-4.0 — attribution required if republished
- **Upstream data** (arXiv metadata, etc.): governed by the upstream source license

## Contact

Methodology errors, data disputes, or feature requests → open an issue on this repo.

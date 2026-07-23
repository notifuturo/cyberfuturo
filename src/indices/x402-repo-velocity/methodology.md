# Index: x402 repository velocity

- **Slug**: `x402-repo-velocity`
- **Current version**: `v0.1`
- **Unit**: new GitHub repositories created per calendar month (UTC)
- **Cadence**: monthly, refreshed on the 2nd of each month
- **Window**: trailing 24 calendar months
- **Source**: [GitHub Search API](https://docs.github.com/en/rest/search/search#search-repositories)
- **License**: repository metadata is public; this derived index is released under CC-BY-4.0
- **Active as of**: 2026-07-23

---

## What this measures

The count of non-fork GitHub repositories, first created within a given calendar month, whose name, description, or topics contain the string `x402` (the open payment-standard protocol built on HTTP 402, used for AI-agent and API micropayments).

Read it as: a raw velocity signal for how many new, independent projects are being started around the x402 ecosystem per month — tooling, facilitators, SDKs, demos, integrations.

## What this does not measure

- Actual x402 payment/transaction volume, or dollar value settled on-chain
- Code quality, project maturity, or whether a repo is maintained after creation
- Deduplication of near-identical demo/tutorial repos (each still counts once)
- Non-GitHub activity (GitLab, self-hosted git, private repos)
- Repos that mention x402 without it appearing in name/description/topics (e.g. buried in README body text only)
- Forks (explicitly excluded — a fork is not a new independent project)

We chose repository-creation velocity specifically **because** no clean public API exists for x402 transaction volume: the protocol is deployed via many independent, self-hostable facilitators (Coinbase's, Cloudflare's, and community-run ones) with no single shared settlement contract, so no single on-chain address represents "x402 usage." See [Known limitations](#known-limitations-v01) #1 for the full reasoning. If you want transaction-volume data, this index is not that — combine with other sources, or treat any such claim about this index as a misreading.

## Exact query

For each calendar month in the trailing 24-month window:

```
x402 in:name,description,topics created:{YYYY-MM-01}..{YYYY-MM-DD} fork:false
```

Evaluated against `https://api.github.com/search/repositories`. Count is read from the `total_count` field of the returned JSON response.

**Deduplication**: none needed — a repository has exactly one creation date, so it can only ever fall into one monthly bucket.

**Rate limit**: 3.1 seconds between requests. GitHub's search endpoint allows 10 req/min unauthenticated, 30 req/min with a token; either comfortably covers 24 monthly requests at this pace.

## Pipeline

Source: [`scripts/build_index_x402_repos.py`](../../../scripts/build_index_x402_repos.py)

```
GitHub Search API → JSON parse → monthly counts → CSV → SVG
```

Implementation: Python 3.11+ stdlib only. No third-party dependencies. Shares its chart renderer with the arXiv index via [`scripts/_svg_chart.py`](../../../scripts/_svg_chart.py) (extracted when this became the second index using the same chart shape — ADR-0007's "template for everything that follows" in practice). Fully reproducible from a clean Python environment in ~75 seconds; faster and higher-rate-limited with a `GITHUB_TOKEN` in the environment (CI supplies this automatically via the Actions built-in token — no setup, no account creation required).

## Outputs

| File | Purpose | Overwritten each run? |
|---|---|---|
| `data/indices/x402-repo-velocity.csv` | Canonical time series | Yes |
| `data/indices/x402-repo-velocity.svg` | Rendered line chart | Yes |
| `site/data/x402-repo-velocity.csv` | Public mirror for site | Yes |
| `site/data/x402-repo-velocity.svg` | Public mirror for site | Yes |

Git history preserves every past state — the audit trail for any brief that cites a specific value at publication time.

## Output schema

Canonical CSV: `data/indices/x402-repo-velocity.csv`

| Column | Type | Example | Constraint |
|---|---|---|---|
| `month` | string (`YYYY-MM`) | `2026-06` | Always a valid calendar month in the trailing 24-month window |
| `repos` | integer | `996` | ≥ 0; derived from `total_count` as a non-negative integer |

File-level invariants:
- Header row is exactly `month,repos`
- Rows are sorted chronologically ascending
- Exactly 24 data rows
- Values are UTF-8 encoded, LF line endings, no BOM

## Known limitations (v0.1)

1. **This is an ecosystem-activity proxy, not a usage/volume metric — by design, not by accident.** We evaluated tracking on-chain settlement volume through a specific facilitator (Coinbase's, on Base) and rejected it: x402 has no single shared settlement contract, facilitators are independently self-hostable, and any one facilitator's volume would systematically undercount the ecosystem while being published under a name ("x402 adoption") that implies the whole thing. Repository-creation count avoids that mislabeling at the cost of measuring a less direct signal.
2. **Text-match noise.** `in:name,description,topics` is a substring/keyword match, not a curated allowlist — a small number of matches may be unrelated projects that happen to mention "x402," or duplicate demo/tutorial repos from onboarding events. We accept this noise as part of the definition, same posture as the arXiv index's `cs.LG` category-overlap limitation.
3. **No repo-quality or survivorship filter.** An abandoned repo created and never touched again still counts in its creation month forever. This measures *starting* activity, not *sustained* activity.
4. **GitHub-only.** Misses GitLab, Codeberg, self-hosted git, and private repositories entirely.
5. **Search index lag.** GitHub's search index can lag live repository creation by up to a few minutes; irrelevant at monthly granularity but noted for completeness.
6. **Timezone**: GitHub's `created:` date filter operates on UTC dates. No adjustment.

## Changelog

- **v0.1 — 2026-07-23** — Initial release. 24-month trailing window, monthly cadence, stdlib-only pipeline sharing the arXiv index's chart renderer, no LLM-generated numbers. First index chosen specifically after rejecting an on-chain-volume approach for methodology-honesty reasons (see Known limitation #1).

Methodology changes bump the version and append here. Historical CSV values are preserved in git so briefs citing older versions remain verifiable.

## How to reproduce

```bash
git clone https://github.com/notifuturo/cyberfuturo
cd cyberfuturo
python3 scripts/build_index_x402_repos.py
# Writes data/indices/x402-repo-velocity.{csv,svg}
# Takes ~75 seconds unauthenticated (24 requests at 3.1s rate limit).
# Optionally: export GITHUB_TOKEN=$(gh auth token) first to use the
# authenticated 30 req/min search limit instead of 10 req/min.
```

Zero required third-party packages. No required API keys — `GITHUB_TOKEN` is optional and only raises the rate ceiling.

## Deprecation criteria

Per business rule BR-11, every index has pre-committed conditions for deprecation, renaming, or retirement.

This index is deprecated when **any one** of the following becomes true:

1. **Source deprecation** — GitHub removes or materially restricts the public repository search endpoint for unauthenticated/low-volume use.
2. **Query saturation** — "x402" stops being a specific-enough term (e.g. it becomes a common word/product name unrelated to the protocol) such that the match rate is dominated by false positives, judged by a manual sample review showing >20% off-topic matches in a given month.
3. **A real usage-volume alternative appears** — if x402 governance (the Linux Foundation project) or a neutral third party ever publishes a documented, reproducible transaction-volume API, that becomes a stronger index and this one is superseded or demoted to a secondary signal.
4. **The protocol is abandoned or superseded** — if x402 adoption visibly collapses or a successor standard replaces it industry-wide.
5. **Replaced by a better version** — a v2.x index with the same slug and stricter methodology (e.g. weighted by repo activity, not just creation) can supersede v0.x.

Deprecation process:

- Publish a final snapshot at the deprecation moment, versioned and frozen
- Announce in the next brief with explicit reasoning
- Move the CSV/SVG to `data/indices/archived/<slug>/` and keep forever
- Strike through the index on the methodology index page with a link to the final snapshot and the announcement brief
- Leave the methodology document in place with a "deprecated on [date], superseded by [new-slug]" banner at the top

The index is never silently removed. Every deprecation is logged in the changelog of this document.

## Contact

Methodology errors, data disputes, or reproducibility problems: open an issue on the repo or reply to any brief that cites this index. Corrections are published in the next brief with a changelog entry.

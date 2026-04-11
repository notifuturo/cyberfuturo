# Architecture Decision Records

This directory contains the architectural decisions made for CyberFuturo, using a light [MADR-inspired](https://adr.github.io/madr/) format. Each file documents one decision, its context, and its tradeoffs.

## Format conventions

Every ADR contains:

- **Status** — `Proposed`, `Accepted`, `Deprecated`, or `Superseded by ADR-xxxx`
- **Date** — when the decision was recorded (not necessarily when it was first made)
- **Context** — what problem we faced and what constraints shaped the decision
- **Decision** — what we chose
- **Consequences** — the positive, negative, and neutral fallout
- **Alternatives considered** — options that were rejected and why

ADRs are **append-only**. When a decision changes, write a new ADR that supersedes the old one. Never rewrite history.

## Current ADRs

| # | Title | Status | Date |
|---|---|---|---|
| [0001](./0001-measurement-only-publication.md) | Measurement-only publication (no forecasts) | Accepted | 2026-04-11 |
| [0002](./0002-python-stdlib-only-pipeline.md) | Python stdlib-only ingestion pipeline (v0.1) | Accepted | 2026-04-11 |
| [0003](./0003-static-site-no-js-framework.md) | Static site with no JavaScript framework | Accepted | 2026-04-11 |
| [0004](./0004-cloudflare-pages-direct-upload.md) | Cloudflare Pages via direct-upload deploy | Accepted | 2026-04-11 |
| [0005](./0005-inline-svg-chart-rendering.md) | In-pipeline SVG chart rendering | Accepted | 2026-04-11 |
| [0006](./0006-private-repo-public-site.md) | Private repo, public site | Accepted | 2026-04-11 |
| [0007](./0007-versioned-methodology-artifact.md) | Versioned per-index methodology as first-class artifact | Accepted | 2026-04-11 |
| [0008](./0008-llms-never-generate-numbers.md) | LLMs never generate numbers | Accepted | 2026-04-11 |
| [0009](./0009-free-tier-only-infrastructure.md) | $0 / free-tier-only infrastructure constraint | Accepted | 2026-04-11 |
| [0010](./0010-trailing-window-time-series.md) | Trailing-window time series, accept backfill drift (v0.1) | Accepted | 2026-04-11 |

## Decision themes

These ten ADRs cluster around three big commitments that define the project:

1. **Credibility discipline** — ADRs 0001, 0007, 0008. No forecasts, every number versioned, LLMs never fabricate. Together these are the product moat.
2. **Radical simplicity** — ADRs 0002, 0003, 0005. Stdlib-only Python, no JS framework, charts as text. Zero dependency rot over multi-year timelines.
3. **$0 operability** — ADRs 0004, 0006, 0009. Free-tier hosts, private repo, direct upload. The project runs indefinitely without revenue.

ADR-0010 is the one explicit "we're aware this is imperfect" decision — we accept minor backfill drift in v0.1 because the alternative is too expensive for the value it adds. This is the canonical shape of a good ADR: naming a tradeoff instead of pretending it doesn't exist.

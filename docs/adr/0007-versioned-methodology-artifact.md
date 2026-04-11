# ADR-0007: Versioned per-index methodology as first-class artifact

- **Status**: Accepted
- **Date**: 2026-04-11

## Context

A measurement-first publication (ADR-0001) is only as credible as the methodology behind the measurements. The failure mode we most want to avoid is **silent drift** — where the query, the filter, or the source changes and old published numbers quietly become non-reproducible, but the publication doesn't disclose the change.

Every serious data publication deals with this somehow. Options:

1. **No formal methodology** — most indie newsletters
2. **A single global "Methods" page** — most academic papers and some financial publications
3. **Per-index methodology docs** — government statistics (BLS, ONS, Eurostat), Our World in Data, FRED
4. **Versioned methodology linked to each published data point** — rare; mostly scientific data releases

For CyberFuturo, options (1) and (2) fail the specific problem we have: different indices from different sources have different corner cases, different update cadences, and different known limitations. A global methods page would either be vague (useless) or a 20-page catch-all (unreadable).

## Decision

**Every CyberFuturo index has a versioned per-index methodology document, treated as a first-class artifact with its own lifecycle.**

Concretely:

- Each index `<slug>` has a file at `src/indices/<slug>/methodology.md`
- Each index is assigned a semver-like version number (`v0.1`, `v0.2`, etc.)
- The methodology document includes:
  - **What this measures** (positive definition)
  - **What this does NOT measure** (negative definition — often longer than the positive)
  - **Exact query** (reproducible by a reader)
  - **Pipeline** (source file, language, dep inventory)
  - **Outputs** (file paths and schemas)
  - **Known limitations** (every known gap, explicitly stated, numbered)
  - **Changelog** (append-only version history)
  - **How to reproduce** (exact commands a reader can run)
  - **Contact** (how to report a methodology error)

- **Methodology version changes are governance events.** A version bump requires:
  1. A changelog entry describing what changed and why
  2. A new row in the published data (old rows stay valid under the previous version)
  3. A note in the next published brief disclosing the version bump
  4. Optionally, a comparison chart showing old-method vs new-method values for the overlap window

- **Historical data is preserved in git** so briefs that cited v0.1 numbers remain verifiable forever against the exact CSV as of publication time.

## Consequences

### Positive
- **Auditability.** A skeptical reader in 2030 can clone the repo, read `src/indices/arxiv-ai-velocity/methodology.md`, run the documented command, and verify the March 2026 number the Issue #01 brief cited.
- **Corrections are visible and honest.** When we find a bug, the changelog entry documents the bug, the fix, and the value delta. This is a feature, not an embarrassment — it's how trust compounds.
- **Methodology changes force deliberation.** Because every bump is a named event, the cost of changing the query is high enough to prevent casual edits.
- **New indices have a template.** The first methodology doc (arxiv-ai-velocity) is the structural template for everything that follows. Consistency compounds.
- **Readers can compare indices on common criteria.** Every methodology page answers the same questions in the same order.

### Negative
- **Overhead per index.** Every index is ~1 hour of methodology-writing work on top of the pipeline code. This is a feature — it forces us to be slow about shipping indices that aren't fully understood.
- **Version-bump ergonomics are not yet automated.** We don't currently have tooling to reprocess historical data under a new methodology version. That's on the v0.2 roadmap.
- **Documentation can rot** if we write an index and forget to update the methodology when the query changes. Enforcement mechanism (not yet built): a CI check that compares the query string in the pipeline script to the one quoted in the methodology doc.

### Neutral
- The methodology page is also the *marketing surface*: prospective sponsors and citing publications read it to judge rigor. Treating it as a first-class artifact is both editorial discipline and go-to-market asset.

## The methodology page is more important than the pipeline code

If we had to choose between publishing the methodology and publishing the code, we would publish the methodology. Code can be re-written; a clear, honest specification is what lets a third party audit, reproduce, or replace the code.

## Alternatives considered

- **No methodology, just scripts + comments.** Rejected. Code comments rot faster than standalone docs.
- **Single global methodology page.** Rejected. Doesn't scale to indices with fundamentally different shapes.
- **Machine-readable methodology (YAML/JSON schema) only.** Rejected. Machine-readable is fine for CI checks but humans need prose. Will be added *alongside* the markdown doc in v0.3+.
- **Third-party specification frameworks** (Frictionless Data, Schema.org Dataset, DCAT). Deferred. Worth adopting in v0.3+ once we have 5+ indices; premature at v0.1.

## Related ADRs

- [ADR-0001 — Measurement-only publication](./0001-measurement-only-publication.md) — the credibility premise this ADR delivers on
- [ADR-0010 — Trailing-window time series](./0010-trailing-window-time-series.md) — the acknowledged drift behavior this methodology discipline surfaces honestly

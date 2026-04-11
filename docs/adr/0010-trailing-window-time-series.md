# ADR-0010: Trailing-window time series, accept backfill drift (v0.1)

- **Status**: Accepted (v0.1); scheduled for revision in v0.2
- **Date**: 2026-04-11

## Context

The arXiv API — and many similar data sources (NVD, GitHub Advisory, Crunchbase, FRED in some series, SEC EDGAR) — allow **retroactive changes** to records:

- **Category reassignment.** A paper originally filed under `cs.LG` may later be reclassified into `cs.AI` or removed from both.
- **Withdrawals.** A paper filed in March can be formally withdrawn in May, but it still counts in the March submission count.
- **Backfill of late submissions.** A paper with a `submittedDate` of 2026-03-31 23:58 may not be indexed until 2026-04-01.
- **Metadata corrections.** Typos, author list updates, abstract rewrites, DOI assignments.

This means: **the same query run today and run in six months can produce different counts for the same historical month.**

This is not a bug. It's how scientific data is actually maintained. Every serious dataset has this property.

The question is how our pipeline should handle it.

## Options

1. **Freeze on first capture.** Fetch a month exactly once, store the value, never touch it again. Pro: fully reproducible. Con: our number diverges from arXiv's current truth over time, and we can't explain the gap.
2. **Full historical re-fetch every run.** Re-pull every month in our entire history on every refresh. Pro: always matches source truth. Con: slow, expensive, and we lose the ability to cite "the March number as reported when we published Issue #01."
3. **Trailing window, no re-fetch of older months.** Fetch only the N most recent months each run; accept that older months are effectively frozen at whatever their value was when last in the window.
4. **Trailing window + periodic full re-fetch with explicit versioning.** Run the short trailing query monthly, and run a full historical re-fetch quarterly with a versioned snapshot.

Option 4 is the theoretical ideal. Options 1, 2, and 3 are simpler variants that each make a specific tradeoff.

## Decision

**For v0.1, we adopt Option 3: trailing 24-month window, no re-fetch of months outside the window. Small drift in the oldest months is accepted and documented in the methodology.**

Concretely for the arXiv AI velocity index:

- Each run fetches the trailing 24 calendar months from the previous full month
- The CSV and SVG are fully overwritten
- Git history preserves every past state, so point-in-time values are always recoverable
- The methodology page (ADR-0007) explicitly documents this as a known limitation

**v0.2 will upgrade to Option 4** — adding a quarterly full-window re-fetch that produces a versioned snapshot (`arxiv-ai-velocity-2026Q3.csv`) and logs the delta against the previous snapshot.

## Consequences

### Positive
- **Simple pipeline.** One query per month × 24 months = 24 API calls = ~75 seconds end to end.
- **Fast CI runs.** Well under GitHub Actions time budgets.
- **Git history is the audit trail.** A reader who wants to know "what did CyberFuturo report for July 2024 back in Issue #01" can `git show 3e783de:data/indices/arxiv-ai-velocity.csv` and get the exact value we cited.
- **Aligned with ADR-0007.** The methodology page documents the drift behavior explicitly, so readers are never misled.

### Negative
- **Older months drift.** If you fetch the 2024-08 value in April 2026 and again in April 2027, the numbers may differ slightly. The drift is typically <1% but non-zero.
- **Briefs may cite a number that no longer matches the current CSV.** A reader who clicks through from an archived brief to the live CSV may see a different value. Mitigation: the methodology page explicitly states this, and every brief's numbers are preserved in git at the commit of publication.
- **Quarterly re-fetch is not yet implemented.** The drift monitoring that Option 4 would give us is absent in v0.1.

### Neutral
- For the arXiv index specifically, empirical drift over 24 months is small (based on arXiv's own documentation and observed stability of older months). The risk is **known** and **bounded**, not **hidden**.

## Known limitations this ADR explicitly acknowledges

Reproduced from the arxiv-ai-velocity methodology (`src/indices/arxiv-ai-velocity/methodology.md`):

1. No resubmission handling
2. No withdrawal filter
3. No seasonality adjustment
4. Category overlap with non-AI fields
5. Single-point-in-time snapshots
6. UTC timezone, no adjustment

This ADR is the architectural parent of limitation #5. #1, #2, #3, #4, and #6 are each properties of the specific index, not the trailing-window design.

## v0.2 upgrade plan

Planned for v0.2 (Q3 2026):

1. Add a `--full-refetch` flag to ingestion scripts
2. Schedule a quarterly full-window cron (in addition to the monthly trailing cron)
3. Produce versioned snapshots: `data/indices/arxiv-ai-velocity-<YYYY>Q<q>.csv`
4. Compute and publish a delta report: "values that changed more than 1% since last quarter"
5. Update the methodology changelog with a note about the new behavior

This upgrade does not invalidate v0.1 data — the trailing window semantics remain for the monthly cron, and the quarterly snapshots add a second view on top.

## Alternatives considered

- **Option 1 (freeze on first capture).** Rejected. Our number would grow increasingly stale vs arXiv's own totals, and we'd have no way to update it without breaking reproducibility. Wrong tradeoff for a publication that will be cited against its own source.
- **Option 2 (full re-fetch every run).** Rejected for v0.1 — too expensive in API calls for the marginal accuracy gain. Would require ~500+ API calls per run to cover the full history we'll eventually accumulate.
- **Option 4 (trailing + periodic full re-fetch).** Deferred to v0.2. The right long-term answer; premature at v0.1 when we have only one index and 24 months of data.

## Related ADRs

- [ADR-0007 — Versioned per-index methodology](./0007-versioned-methodology-artifact.md) — this ADR is exactly the kind of tradeoff that methodology must surface honestly
- [ADR-0002 — Python stdlib-only pipeline](./0002-python-stdlib-only-pipeline.md) — constrains how complex we can make the re-fetch logic

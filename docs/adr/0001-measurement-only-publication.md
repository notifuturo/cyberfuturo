# ADR-0001: Measurement-only publication (no forecasts)

- **Status**: Accepted
- **Date**: 2026-04-11

## Context

Near-future technology analysis is dominated by opinion-driven essay newsletters (Stratechery, Exponential View, The Generalist) and vendor-funded trend reports (Gartner, Forrester, CrowdStrike Global Threat Report). Both formats have known credibility failure modes:

- **Essay newsletters** require a personal brand and years of compounding voice. They also fall prey to "hot take" decay — last year's confident prediction is next year's embarrassment.
- **Vendor-funded reports** are distributed as marketing collateral. Their audience knows this and discounts them accordingly.

A format gap exists for **rigorous, measurement-first publication from public data** — something like the Bloomberg Terminal or Cloudflare Radar, but for near-future technology indicators across AI, compute, and energy. No indie publication currently occupies that lane.

The automation constraint of the project ($0 budget, minimize human bandwidth) also rules out essay-first formats: we cannot compete with essayists on cadence or voice. We can compete on rigor and compounding data.

## Decision

**CyberFuturo publishes only measured data from public sources. No forecasts. No predictions. No interpretive overreach.**

Editorial prose in briefs may frame what a number means, describe what it excludes, and contextualize methodology. It may **not** assert what a number will become, recommend investment actions, or claim causal relationships that the data does not demonstrate.

The tagline — *"How fast the future is arriving, by the numbers"* — is meant to be taken literally. We describe arrival, not departure.

## Consequences

### Positive
- **Unfalsifiable upside.** A measurement cannot be "wrong" the way a prediction can. Reporting that arXiv cs.AI submissions were 7,406 in March 2026 is a verifiable fact; predicting they will reach 10,000 by September is a bet that can blow up.
- **Compounding authority.** Every month the dataset grows more valuable. Year-2 data is citable. Year-3 data is cited by *other* publications, which compounds back into our distribution.
- **Clear editorial rules.** Writers never have to decide whether a claim is "predictive enough" — the answer is always the same: don't predict.
- **Sponsor acceptability.** Vendors will sponsor a data publication they trust more readily than an opinion publication they can't control.
- **Slop-tax immunity.** Deterministic measurements aren't penalized by the 2025 AI-slop backlash the way generated prose is.

### Negative
- **Slower authority buildup than opinion-driven formats.** Forecasts go viral; measurements do not. We accept lower top-of-funnel in exchange for higher trust density.
- **Narrower content surface area.** We cannot do "10 startups to watch" listicles or tier-list essays. Every piece must cite a measurement.
- **Requires real data infrastructure** (ADR-0002, ADR-0007) to deliver on the rigor premise. There's no shortcut.

### Neutral
- The publication still has voice — in the editorial framing of *what the number means* and *what it does not measure*. The voice is just always anchored to a verifiable observation.

## Alternatives considered

- **Opinion-driven newsletter (Exponential View model).** Rejected. The lane is saturated with established operators (Azeem Azhar, Ben Thompson, Packy McCormick) and requires years of personal-brand compounding we don't have.
- **Hybrid — measurements with forecast layers.** Rejected. The forecast layer contaminates the measurement layer's credibility. Readers who catch one bad forecast discount the rest of the publication.
- **Pure data dashboard with no editorial.** Rejected. A dashboard alone has no distribution flywheel — no one subscribes to a data feed. The brief is the distribution wrapper that makes the data habit-forming.

## Related ADRs

- [ADR-0007 — Versioned methodology as first-class artifact](./0007-versioned-methodology-artifact.md) operationalizes the rigor claim.
- [ADR-0008 — LLMs never generate numbers](./0008-llms-never-generate-numbers.md) protects the measurement integrity at the pipeline level.

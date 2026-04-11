# ADR-0008: LLMs never generate numbers

- **Status**: Accepted
- **Date**: 2026-04-11

## Context

LLMs are useful for prose tasks: summarization, translation, outlining, copy-editing, source discovery, headline generation. They are also notorious for confabulating numerical values, statistics, citation counts, and historical dates, even when the prompt asks them to be precise.

CyberFuturo's entire credibility premise (ADR-0001) rests on published numbers being verifiable. A single hallucinated statistic in a brief would not just damage the individual claim — it would retroactively taint every other number on the site, because readers cannot distinguish "this specific number came from a hallucinated LLM response" from "this number came from a rigorous pipeline" without auditing each one.

This is asymmetric risk: one LLM-generated bad number erases months of earned trust.

## Decision

**In the CyberFuturo pipeline, LLMs may not write, infer, estimate, interpolate, round, or otherwise produce any numerical value that appears in a published artifact.**

All numbers must come from deterministic queries against public APIs (arXiv, NIST NVD, FRED, etc.) processed by stdlib-only code (ADR-0002).

LLMs are permitted for:

- **Editorial prose** — the "what this means" and "what this is not" paragraphs in briefs, drafted or polished by LLM, then human-reviewed
- **Source discovery** — "what data sources exist for battery $/kWh" type questions
- **Query debugging** — "why is this XML parsing failing"
- **Translation** — converting briefs between languages (future)
- **Copy editing** — tightening human-drafted prose

LLMs are **not** permitted for:

- Extracting numbers from scraped unstructured text (if a source is unstructured, we either find a structured source or don't publish the index)
- Estimating missing data points
- Producing "about X" or "roughly Y" numbers
- Generating interpolated chart values
- Writing the pipeline code's numeric constants (thresholds, cutoffs, rounding rules — these must be reviewed and justified by a human)
- Narrating what a number will become (that would also violate ADR-0001)

## Consequences

### Positive
- **Every published number is traceable to a deterministic source.** A reader can follow the methodology page → pipeline code → source API → raw response and verify the number.
- **Slop-tax avoidance.** The 2025 AI-slop backlash (~9× increase in "AI slop" mentions, ~40% engagement drop on LLM-generated articles) penalizes publications that can be identified as LLM-produced. CyberFuturo can openly disclose AI assistance in editorial prose without compromising data integrity, because the numbers are demonstrably not LLM-touched.
- **Simplicity.** The rule is crisp and testable: "did an LLM touch this number?" If yes, it cannot be published.
- **Auditable editorial disclosure.** The brief can honestly state *"human-edited, AI-assisted"* because the AI assistance is scoped to prose.

### Negative
- **LLMs can't do the "interesting" analytical work** that seems appealing — anomaly detection, outlier scoring, trend labeling. We defer all of these to v0.2+ when we can build them as separate, explicitly-labeled, human-reviewed layers.
- **Some data enrichment is out of reach.** For example, extracting a numeric value from a vendor press release requires either (a) the vendor publishing the number in a structured source, or (b) a human reading and typing it. LLM-extracted numbers are forbidden.
- **We reject some indices that other publications would happily run.** If the only way to get the number is to ask an LLM to read 50 PDFs and summarize, we don't publish that index.

### Neutral
- LLMs remain genuinely useful for **editorial productivity** — drafting the "what this means" sections, suggesting headlines, and reviewing the voice consistency across issues. That work is non-controversial because the output is labeled as editorial prose, not data.

## Enforcement

Current (v0.1): human code review. Every `scripts/build_index_*.py` is written or audited by a human. Every commit that adds a numeric literal is reviewed.

Planned (v0.2): a CI check that greps the pipeline code for any module or function that could be an LLM call (`anthropic`, `openai`, `claude`, `llm`, `chat`) and fails the build if found in `scripts/` or `src/indices/`.

Editorial prose in `docs/briefs/` is explicitly *exempt* from this check — LLM-assisted editorial is allowed there and must be disclosed in the brief itself.

## Alternatives considered

- **"LLMs only for prose, trust humans to not mix"** — the soft version of this ADR. Rejected because it relies on discipline that decays over time. Better to make the rule enforceable by machines.
- **"LLMs can propose numbers, but a human must verify each one"** — rejected. The verification step is the expensive one; if a human has to check every LLM-produced number anyway, the LLM isn't saving labor.
- **"Use LLMs for outlier detection with explicit disclosure"** — deferred to v0.3+ as a *labeled* feature, not mixed with the core measurement pipeline.

## Related ADRs

- [ADR-0001 — Measurement-only publication](./0001-measurement-only-publication.md)
- [ADR-0007 — Versioned per-index methodology](./0007-versioned-methodology-artifact.md)

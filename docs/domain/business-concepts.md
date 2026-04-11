# CyberFuturo — Business Concepts & Domain Model

This document is the canonical reference for CyberFuturo's business logic. It defines the ubiquitous language (per DDD), the core domain entities, the invariants that hold across them, and the business rules that govern the publication.

It is complementary to the [ADRs](../adr/README.md): ADRs describe **how** we chose to build; this document describes **what** we are building.

---

## 1. Mission

> **Publish the canonical, free, rigorously documented set of leading indicators for how fast the digital, compute, and energy foundations of the near future are actually being built.**

Everything in this document is downstream of that mission. When a decision is ambiguous, fall back to whether it advances or degrades this statement.

---

## 2. Ubiquitous language

Terms used throughout the project. Use these words, exactly these words, in code, docs, briefs, and conversations. Drift breaks shared understanding.

| Term | Definition |
|---|---|
| **Index** | A deterministic, versioned, reproducible time series of observations measuring a specific phenomenon (e.g. *arXiv AI research velocity*). Has a slug, unit, cadence, window, source, methodology, and license. |
| **Observation** | A single (timestamp, value) data point belonging to an index. Immutable once published under a methodology version. |
| **Methodology** | The versioned document describing exactly how an index is computed — query, source, transformations, known limitations. One methodology version per index version. |
| **Pipeline** | The ingestion + transformation + rendering code that produces an index's observations, CSV, and chart from a source API. |
| **Source** | An external public data endpoint the pipeline reads from (arXiv API, FRED, NVD, SEC EDGAR, etc.). |
| **Dataset** | The canonical output of a pipeline run — a CSV file with observations plus an SVG chart. Stored at `data/indices/<slug>.{csv,svg}`. |
| **Chart** | A rendered visualization of a dataset, produced by the pipeline in SVG form. Inline text, git-diffable, versioned alongside the CSV. |
| **Brief** (a.k.a. **Issue**) | A human-readable publication unit citing one or more indices. Has an issue number, publication date, reading time, and editorial prose. Published both as HTML on the site and (eventually) as an email. |
| **Changelog entry** | An append-only record of a change to a methodology or dataset, with version, date, author, rationale, and value delta (when applicable). |
| **Reader** | Someone who consumes CyberFuturo — via the site, an email, or a republication. Characterized by subscriber status (free/paid/none) and ICP signals (AppSec engineer, deep-tech VC, corporate innovation, journalist, etc.). |
| **Subscriber** | A reader who has given us their email via the subscribe form. The core audience asset. |
| **Sponsor** | A vendor paying for placement in one or more briefs. Always a named company, never a programmatic network. |
| **Slot** | A single paid placement within one brief. At most one slot per brief. |
| **Kill criterion** | A pre-committed numeric threshold that, if unmet by a deadline, forces a pivot or shutdown. Explicit before launch. |

**Non-vocabulary (words we deliberately avoid):** *"predict", "forecast", "will be", "expected to", "projected to", "on track to"* — these contradict [ADR-0001](../adr/0001-measurement-only-publication.md). Replace with *"is", "has reached", "as of [date]", "the trailing average shows"*.

---

## 3. Domain entities and aggregates

The system is organized around three bounded contexts:

1. **Publication** (the editorial and subscriber-facing side)
2. **Data** (the pipeline and datasets)
3. **Commerce** (sponsors, slots, revenue)

Entities and aggregates below are grouped by context.

### 3.1 Publication context

#### Aggregate: **Brief**

The brief is the atomic unit of publication.

- **Identity**: `issue_number` (sequential, starting at 01)
- **Fields**: `issue_number`, `publication_date`, `title`, `subtitle`, `reading_time_minutes`, `author`, `ai_assistance_disclosed`, `body` (sections), `sponsor_id` (nullable), `cited_indices` (list of `(index_slug, methodology_version)`)
- **Invariants**:
  1. Every brief has exactly one human author
  2. Every numeric claim in the body must cite at least one `(index_slug, methodology_version)` tuple
  3. A brief cannot be published until all cited indices are at the referenced methodology version
  4. If `ai_assistance_disclosed = true`, the disclosure appears in the brief body (not only in metadata)
  5. At most one sponsor per brief (`sponsor_id` nullable)
  6. The sponsor, if present, appears **below the first editorial paragraph** — never above the fold
  7. The brief's text references to numbers must match the CSV values at the commit of publication (enforced by git history, not a runtime check)

#### Aggregate: **Subscriber**

- **Identity**: `email` (primary), plus optional `external_id` from beehiiv or formsubmit
- **Fields**: `email`, `subscribed_at`, `source` (which channel they came from), `consent_verified` (whether they clicked a double-opt-in link), `paid_tier` (future), `preferred_language` (future)
- **Invariants**:
  1. No brief is delivered to a subscriber whose `consent_verified = false`
  2. Subscribers can unsubscribe with one click, no friction, no "downgrade" flows
  3. Email addresses are never sold, shared, or given to sponsors

### 3.2 Data context

#### Aggregate: **Index**

The central entity of the project.

- **Identity**: `slug` (kebab-case, unique)
- **Fields**: `slug`, `display_name`, `current_version`, `unit`, `cadence` (`monthly` / `quarterly` / `annual`), `window` (e.g. `trailing-24-months`), `source_id`, `license`, `first_published_at`, `last_refreshed_at`
- **Child entities**:
  - `Methodology[]` — one per version, immutable
  - `Observation[]` — one per `(timestamp, methodology_version)` tuple
  - `Chart` — the currently-rendered SVG for this index
- **Invariants**:
  1. **No publication without methodology.** An index cannot be published if it has zero methodology documents.
  2. **One active methodology version.** At any given time, exactly one methodology version is the `current_version`. Older versions are `superseded`.
  3. **Observations are tagged with methodology version.** When a methodology version bumps, old observations retain their original tag; new observations are produced under the new version.
  4. **Chart matches current dataset.** The SVG chart in `data/indices/<slug>.svg` must have been produced by the same pipeline run that produced the current CSV.
  5. **Every published observation is traceable to a deterministic source query.** LLMs cannot generate observations (ADR-0008).
  6. **Historical observations are preserved.** Past values must remain accessible from git even after a refresh overwrites the current dataset file.

#### Aggregate: **Methodology**

- **Identity**: `(index_slug, version)` compound key
- **Fields**: `index_slug`, `version` (semver-like), `what_this_measures`, `what_this_does_not_measure`, `exact_query`, `pipeline_source_path`, `outputs`, `known_limitations[]`, `changelog[]`, `how_to_reproduce`, `contact`, `license`
- **Invariants**:
  1. A methodology document is immutable once it has ever been cited by a published brief
  2. A new methodology version supersedes the previous but does not delete it
  3. Every methodology version has a corresponding row in the changelog
  4. The methodology version is referenced from every brief that cites the index

#### Entity: **Source**

- **Identity**: `source_id` (unique string, e.g. `arxiv-api`, `fred`, `nvd`)
- **Fields**: `source_id`, `display_name`, `base_url`, `access_method` (`rest-json`, `rest-xml`, `csv-download`, `oai-pmh`, ...), `rate_limit` (e.g. `3.1s between requests`), `license`, `update_cadence`, `reliability_notes`
- **Invariants**:
  1. Every source must have a stable, publicly documented access method
  2. Sources requiring authentication are only permitted if the API key is free-tier obtainable
  3. Sources with a ToS that prohibits derived-data republication cannot be used

#### Entity: **PipelineRun**

- **Identity**: `(index_slug, started_at)`
- **Fields**: `index_slug`, `methodology_version`, `started_at`, `finished_at`, `source_id`, `records_fetched`, `records_emitted`, `exit_code`, `error_log`
- **Invariants**:
  1. A pipeline run that fails (non-zero exit) does not overwrite the canonical dataset
  2. Successful runs must leave the repository in a consistent state (all of CSV, SVG, and methodology version references in sync)

### 3.3 Commerce context

#### Aggregate: **Sponsor**

- **Identity**: `sponsor_id` (slug, e.g. `lakera`, `protect-ai`)
- **Fields**: `sponsor_id`, `legal_name`, `display_name`, `icp_alignment_notes`, `contact_name`, `contact_email`, `first_contact_at`, `status` (`prospect` / `in_discussion` / `active` / `churned`), `rate_card_tier`, `slots_booked[]`, `payment_terms`
- **Invariants**:
  1. Sponsor status transitions are append-only events (no silent deletion of history)
  2. A sponsor cannot book a slot in a brief whose editorial independence would be compromised (e.g. a brief about their own product)
  3. Sponsor's display copy is their own but must be reviewed by editorial before publication

#### Aggregate: **Slot**

- **Identity**: `(brief_issue_number, sponsor_id)`
- **Fields**: `brief_issue_number`, `sponsor_id`, `rate_paid`, `display_copy`, `approved_at`, `published_at`
- **Invariants**:
  1. At most one slot per brief
  2. A slot cannot be sold into a brief that has already been published
  3. Slot display copy must comply with editorial rules (see §5)

### 3.4 Cross-context invariants

- **Every published brief has a version-locked dataset.** Git commits function as the anchor: the brief at commit `X` cites observations as they existed in `data/indices/*.csv` at commit `X`.
- **Sponsors never influence which indices exist.** An index is added because the editorial team wants to measure it, not because a sponsor wants it measured.
- **Corrections always propagate.** If a methodology error is found in a past brief, the next brief publishes a correction with a changelog entry — never a silent edit to the archive.

---

## 4. Business rules (invariants that apply publication-wide)

These are the rules that survive every edge case. They are the "constitution" of CyberFuturo.

| # | Rule | Enforcement |
|---|---|---|
| BR-01 | **No forecasts.** Every published claim is a measurement or a description of one. | Editorial review; ADR-0001 |
| BR-02 | **No LLM-generated numbers.** Numbers come from deterministic pipelines only. | Code review; ADR-0008; future CI import check |
| BR-03 | **Methodology before publication.** An index cannot be published before its methodology document is written, reviewed, and tagged. | `git` pre-commit hook (future); code review |
| BR-04 | **Every number is traceable.** A reader can follow brief → index → methodology → source in at most 3 clicks. | Site structure; cross-linking enforced in templates |
| BR-05 | **Corrections appear in the next brief.** Methodology errors are never silently edited out of history. | Editorial discipline; changelog entry required per ADR-0007 |
| BR-06 | **One sponsor per brief.** Never two, never three, never programmatic. | Commerce validation; Slot invariant |
| BR-07 | **Sponsors never appear above the fold.** Editorial always comes first. | Brief template constraint; sponsor contract |
| BR-08 | **Editorial independence is absolute.** A sponsor cannot review, suggest, or influence editorial content beyond their own display copy. | Sponsor agreement; editorial policy |
| BR-09 | **AI assistance is disclosed.** Every brief that used LLM assistance for editorial prose says so, visibly, in the brief body. | Brief template slot; editorial checklist |
| BR-10 | **Subscriber data is never shared.** Email addresses are not sold, swapped, or handed to sponsors — even aggregate segments. | Privacy policy; technical separation of subscriber DB from sponsor CRM |
| BR-11 | **Every index has a kill criterion.** If an index stops being useful or reliable, it is deprecated, not silently rotted. | Methodology page must include deprecation criteria |
| BR-12 | **Git history is the audit trail.** Past brief content and past dataset values must remain accessible. Destructive history rewrites are forbidden except in explicit repo-visibility scenarios (ADR-0006). | Repo policy; branch protection |

---

## 5. Editorial rules

The voice and style that defines CyberFuturo as a publication. These are not nice-to-haves; they are the texture of the brand.

### Voice

- **Data-first, prose-second.** Every brief leads with a number, not an anecdote.
- **Concrete, not speculative.** Replace "could," "might," "is expected to" with "is," "reached," "has been."
- **Honest about limits.** Every brief names what the number does *not* mean — usually as a dedicated section.
- **Short paragraphs.** 3-sentence max in body. Readers skim; skim-friendly is first-class.
- **No growth-hack emojis, no clickbait subject lines, no "you won't believe" phrasing.**

### Structure of a brief

Every brief has exactly this structure:

1. **Header** — issue number, date, reading time, raw-data link, methodology link
2. **The number** — pull-quote of the headline measurement, with units and comparison
3. **Chart** — the SVG, with alt text and source attribution
4. **What moved** — 2–4 specific observations, each with its own subheading
5. **What this is NOT** — explicit delimitation of what the number does not measure
6. **How this was built** — brief pointer to the methodology + source code
7. **Next** — 1–2 sentences on upcoming indices / issues
8. **Footer** — subscribe, archive, methodology, raw data links
9. *(optional)* **Sponsor slot** — below the first editorial section, clearly labeled

No other structure is permitted at v0.1. Variants are introduced by new ADRs.

### What a brief never contains

- Predictions
- Investment advice
- "Top 10" / "5 things to watch" style listicles
- Political opinion
- Personal speculation dressed as analysis
- LLM-generated numbers, charts, tables, or metadata
- Unattributed numbers
- Engagement-bait CTAs

---

## 6. Monetization logic

### Revenue stream priorities (ordered)

1. **Direct-sold sponsor slots** — primary revenue from months 4+
2. **Affiliate commissions** — bridge revenue while audience grows (HackTheBox, TryHackMe, Proton, 1Password — 15–40% payouts)
3. **Paid subscription tier** *(future, v0.4+)* — deeper analysis, archive search, API access
4. **Data licensing** *(future, v0.5+)* — commercial republication licenses, custom index commissions from VCs
5. **Display ads** *(never)* — explicitly excluded; CyberFuturo does not run programmatic ads

### Pricing ladder

| Tier | When | Price per slot | Notes |
|---|---|---|---|
| Founding | Briefs 1–8 | $750 / brief | Locks rate through brief #20 |
| Standard | Briefs 9–20 | $1,250 / brief | |
| Scale | Briefs 21+ | $1,500–$2,000 / brief | Rate adjusted by audience size |
| Custom | Any | Negotiated | For multi-brief bundles or exclusive categories |

### Pre-revenue kill criterion

If by **90 days after public launch of Issue #01**, CyberFuturo has:

- **Fewer than 500 subscribers** OR
- **Fewer than 2 sponsor inquiries from the target vendor list**

...then the current wedge has not validated. Pivot decisions:

1. First pivot: narrow the ICP (e.g. from "near-future tech broadly" to "AI+compute only")
2. Second pivot: change the language (e.g. Spanish-first per our earlier analysis)
3. Third pivot: shut down or reposition the domain

Each pivot is a new ADR.

### First-$1 vs lifetime-ceiling

- **Time to first paid sponsor**: realistic 4–8 months from launch
- **Revenue floor**: $0 (fully deferred until sponsor activation)
- **Realistic revenue at 24 months**: $3–15k/month recurring, depending on audience depth and sponsor rotation
- **Theoretical ceiling**: multi-revenue-stream hybrid (sponsorships + paid API + custom index commissions) can reach $15–50k/month at mature scale (5K+ engaged subs and 8–12 active indices)

---

## 7. Kill criteria (publication-level)

These are the pre-committed conditions under which CyberFuturo stops or repositions.

| Trigger | Threshold | Decision |
|---|---|---|
| Audience growth | <500 subs at day 90 | Pivot ICP or language (new ADR) |
| Sponsor validation | <2 inquiries from target vendor list at day 90 | Pivot monetization angle |
| Reproducibility breach | Any published number found to be wrong and not corrected within 30 days | Pause publication until process fixes |
| Slop-tax breach | Clear evidence of LLM-generated numbers shipping | Immediate retraction + audit |
| Infrastructure cost breach | Monthly infra cost >$20 before revenue | Re-evaluate ADR-0009 free-tier constraint |
| Competitor proof of impossibility | A well-funded incumbent publishes an equivalent free product with better distribution | Consider repositioning narrower (e.g. Spanish-first niche) |

Kill criteria are triggers for decisions, not automatic shutdowns. Every trigger produces a new ADR documenting what changed and what the response is.

---

## 8. What CyberFuturo is *not*

An intentional negative space — things the project deliberately does not do, and will say no to even when asked.

- **Not a consulting firm.** We do not do custom research for fees. (Custom *index commissions* are a separate product — a VC can pay us to publicly track a specific indicator, but the result is public and versioned like every other index.)
- **Not a trading signal service.** We do not provide investment advice, trading tips, or price forecasts.
- **Not a news aggregator.** We do not summarize other publications. Every piece of content we publish is an original measurement or a brief built on one.
- **Not a general tech blog.** We do not write about product launches, personal takes, or industry drama.
- **Not an AI-native publication.** LLMs assist with prose, but no index, number, or headline is LLM-authored.
- **Not a multi-author publication** (yet). For v0.1–v0.3, one human author, one editorial voice. Multi-author is a v1.0 consideration.
- **Not a tipping / donation product.** "Support us" buttons are rejected as out of scope — monetization is sponsor-driven or nothing.

---

## 9. Glossary of acronyms used elsewhere in the project

| Acronym | Expansion | Meaning in our context |
|---|---|---|
| ADR | Architecture Decision Record | See `docs/adr/` |
| DDD | Domain-Driven Design | The design discipline this doc follows |
| ICP | Ideal Customer Profile | For sponsors, the audience cohort they want to reach |
| PQC | Post-Quantum Cryptography | A topical area tracked by one planned future index |
| YoY | Year-over-Year | Standard comparison pattern in brief analysis |
| CPM | Cost per Mille (per thousand impressions) | Industry pricing model we explicitly *do not* use |
| CC-BY | Creative Commons Attribution | Derived index license |

---

## Changelog of this document

| Version | Date | Change |
|---|---|---|
| v0.1 | 2026-04-11 | Initial draft. Covers v0.1 launch state: one index (arxiv-ai-velocity), formsubmit-based subscriber capture, no sponsor relationships yet, all future roadmap items marked as such. |

Updates to this document should be proposed via ADR where they imply a domain model change. Typo fixes and clarifications can go straight in with a changelog entry.

# ADR-0009: $0 / free-tier-only infrastructure constraint

- **Status**: Accepted (enforced through v0.1)
- **Date**: 2026-04-11

## Context

CyberFuturo launches with **zero cash budget**. The project must reach its first revenue (sponsored slots, realistically 4–8 months out) without requiring the founder to pay for infrastructure.

This is not austerity for its own sake — it's a deliberate design constraint that:

1. **Forces simple choices.** Any vendor that doesn't offer a usable free tier is rejected at the vendor-selection step, not after a month of integration work.
2. **Defers financial pressure until validation.** We don't want to pay $50/month for tooling while we're still deciding whether the product has traction.
3. **Aligns with the measurement-first thesis** (ADR-0001). A publication that spends months of operating expense before publishing its first brief is not "lean" — it's a premature commitment.

## Decision

**All CyberFuturo infrastructure uses a free tier, with no credit card required, through v0.1 and v0.2.**

The approved stack:

| Component | Vendor | Free tier | Why |
|---|---|---|---|
| **Static hosting** | Cloudflare Pages | Unlimited bandwidth, 500 builds/mo | ADR-0004 |
| **Source control** | GitHub | Private + public repos | — |
| **CI / cron** | GitHub Actions | 2,000 min/mo (private repos) | Sufficient for monthly index refreshes |
| **Newsletter platform** | beehiiv | Launch plan free up to 2,500 subs | Migration point when we cross that threshold |
| **Form capture** | formsubmit.co | Unlimited captures, no auth required | Interim before beehiiv is wired |
| **LLM API** (editorial only) | Claude Haiku | ~$0.0002/request | ~$1–5/mo at v0.1 volume — the *only* cash cost allowed |
| **Domain** | Already owned | $0 ongoing | — |
| **Analytics** | Cloudflare Web Analytics | Free, GDPR-safe | Optional; not yet wired |
| **Email delivery** | beehiiv (sends from) | Included | No separate SMTP vendor |
| **Error tracking** | Sentry free tier | 5K events/mo | Optional |
| **Domain DNS** | Cloudflare DNS | Free | When domain is migrated |

**Hard rule:** any new vendor introduction requires an ADR that explicitly evaluates its free-tier limits and names the migration point.

**Explicitly disallowed under this ADR:**

- Paid hosting (Vercel Pro, Netlify Pro)
- Paid databases (Postgres hosting, DynamoDB pay-per-request)
- Paid monitoring (Datadog, New Relic)
- Paid analytics (Segment, Mixpanel growth tier)
- Paid CDN (KeyCDN, Bunny CDN)
- Paid email delivery (SendGrid, Postmark) — beehiiv covers this
- Any "trial" tier that auto-converts to paid

## Consequences

### Positive
- **The project can run indefinitely without revenue.** There is no month-over-month runway risk from infrastructure costs.
- **Forces simple architectural choices.** Every component is trivially replaceable because nothing is locked in by paid features.
- **Validates the thesis before spending.** We only pay for something after we've proven we need it.
- **Removes a class of founder psychology** — no guilt about "wasting money" on tooling that hasn't earned its keep.

### Negative
- **Free-tier quota ceilings become future migration triggers.** When we cross 2,500 beehiiv subs, we either pay or migrate. That's a forced decision we'll have to make from a position of known value (we have subscribers, so it's worth paying) rather than speculative value.
- **Some premium features are deferred.** Advanced beehiiv segmentation, beehiiv Ad Network, paid CF Pages features, private team CI minutes. None are currently blockers.
- **No vendor negotiation leverage.** We're a free-tier user and have zero influence over terms changes.
- **Risk of free-tier deprecation.** Vendors can revoke free tiers. Mitigation: every ADR that picks a vendor also documents the migration path (see ADR-0004's "Migration path" section).

### Neutral
- **Claude Haiku API cost is tolerated** because it's genuinely below the threshold of "worth tracking" (~$1–5/month). This is the only cash cost permitted under v0.1.

## Known free-tier escape hatches we can use *without* introducing paid vendors

- **GitHub Actions:** Switch to running the cron on a home-lab cron or a self-hosted runner if the 2,000 min/mo ceiling is threatened.
- **Cloudflare Pages:** No ceiling — unlimited bandwidth is the core offer.
- **beehiiv 2,500 ceiling:** Migrate to Buttondown, Ghost (self-hosted), or Substack (which has its own issues but is free forever). All migration paths.
- **formsubmit.co:** Replace with a custom Cloudflare Worker that receives the form POST and writes to a KV store (still free).

## Trigger: when to re-evaluate this ADR

Revisit this decision when **any one of** the following is true:

1. Sponsorship revenue exceeds $500/month for two consecutive months (we have budget to trade money for time)
2. A single free-tier limit is the binding constraint on growth
3. An incident post-mortem identifies a missing paid tool as the root cause

Until then, stay in the free tier.

## Alternatives considered

- **Accept $20–50/month from day 1** for better tooling. Rejected. Adds financial pressure before revenue validation, and nothing in the v0.1 roadmap actually requires paid features.
- **Use a specific cloud (AWS / GCP / Azure) free credit bundle.** Rejected. Credit bundles expire, and the engineering work to build on AWS primitives is disproportionate to what a static site and a cron job need.
- **Self-host everything on a home server.** Rejected. Introduces availability / uptime risk that the edge-hosted free tiers eliminate for $0.

## Related ADRs

- [ADR-0004 — Cloudflare Pages via direct-upload deploy](./0004-cloudflare-pages-direct-upload.md)
- [ADR-0002 — Python stdlib-only pipeline](./0002-python-stdlib-only-pipeline.md) — dep-free pipeline is a *cost* decision as well as a reproducibility one

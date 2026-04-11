# CyberFuturo — Monetization Roadmap

> **Purpose**: the honest plan for turning a free public learning repo into a revenue-generating product, in phases, without ever breaking the "free + public" promise that makes the growth engine work.
>
> **North star**: the content stays free forever. Revenue comes from complementary products (sponsors, credentials, enterprise) that don't require us to gate the lessons.

---

## Principles (non-negotiable)

1. **Lessons are always free.** No paywall, no "sign up to continue," no "register to see lesson 04." The 7 lessons shipped today stay free for anyone with a browser, forever.
2. **The repo is always public.** Public = distribution engine. Private = death.
3. **Sponsors never appear inside a lesson.** Sponsor mentions live on the landing page and in optional release notes, never inside `curriculum/lessons/*/lesson.md`. The student's learning experience is commercial-free.
4. **Subscriber/learner data is never sold, shared, or aggregated for third parties.** Privacy page is the contract.
5. **Every revenue stream is optional for the learner.** Nothing in the product ever blocks progress behind a fee.
6. **Phase transitions are driven by real signal, not by calendar.** We don't build the certification product until actual completions exist. We don't pitch enterprise until there's brand recognition. We don't raise rates until incumbents fill slots at the current rate.

---

## The 6 revenue streams (ranked by realism)

### 🥇 1. Direct-sold sponsorships

**Format**: A "Sponsor:" slot in the landing page hero area and in footer, visible across all 4 language pages. One primary sponsor at a time (exclusive); optional secondary slot when demand exists. **Never inside a lesson.**

**Copy shape** (to be added to the header, not the hero H1):

```html
<div class="sponsor-bar">
  Apoiado por <a href="https://sponsor.example">Sponsor Name</a> —
  <em>sponsor's one-line pitch relevant to beginner devs</em>
</div>
```

**Target buyers** (tiered by fit):

| Tier | Examples | Why they care |
|---|---|---|
| **A — highest fit** | GitHub, Vercel, Supabase, Railway, Neon, Cloudflare, Warp, Cursor | Their ICP is exactly beginner-to-intermediate devs. Their entire growth model is reaching devs early. |
| **B — strong fit** | 1Password, Proton, DigitalOcean, Fly.io, Linear, Raycast, Stripe, Hostinger | Developer-adjacent products that need awareness in the 18–28 beginner cohort. |
| **C — adjacent fit** | DataCamp, HackTheBox, TryHackMe, Boot.dev, Scrimba | Competitors / co-learners — unlikely to sponsor directly but relevant as affiliates (see stream #6). |

**Pricing ladder** (adjusted per audience size):

| Stage | Weekly active learners | Rate |
|---|---|---|
| Founding | < 2,000 | **$500/month** or **$150/week** |
| Growing | 2,000–10,000 | **$1,000–$2,000/month** |
| Established | 10,000–50,000 | **$2,500–$5,000/month** |
| Mature | 50,000+ | **$5,000–$15,000/month** |

**First dollar conditions**:
- Public launch posted on HN + 2 Reddit subs + LinkedIn + Twitter
- ≥500 GitHub stars OR ≥200 curriculum completions in the first month
- Cold-outreach email sent to a named content / DevRel contact at 5 tier-A companies

**Outreach email template**:

```
Subject: CyberFuturo — free beginner CS course, seeking founding sponsor

Hi [First name],

I run CyberFuturo, a free open-source EdTech project teaching the
prerequisites that every CS course assumes you already know — terminal,
git, SQL, Python, HTTP — via GitHub Codespaces, zero install.

We're live at https://cyberfuturo.com/ (Portuguese canonical, also
Spanish/English/French). 7 complete hands-on lessons with auto-grading.
Repo: https://github.com/notifuturo/cyberfuturo

Audience: [N] GitHub stars, [N] monthly active learners, 95%+ beginner
cohort in Brazil + LATAM — exactly the demographic [Sponsor Co] targets
with [specific product].

I'm looking for a founding sponsor for months [X]–[Y] at $500/month —
a single slot in the landing page header, clearly attributed, never
inside a lesson. Editorial independence is non-negotiable and written
into our rules page (https://cyberfuturo.com/rules).

Would a 15-min call next week work? I can walk through the audience
data and the sponsor format.

— [Your name]
```

Store a live copy in `_private/sponsor-outreach.md` (gitignored) with the target list and outreach log.

**Timeline**: first inquiry probably month 2–4 after public launch. First paid month 4–6.

---

### 🥈 2. Paid certification ($29 one-time)

**Format**: Every `./cf progress` at 100% shows a "Request your certificate" button that links to a Stripe Checkout. After successful payment, a GitHub Action or Cloudflare Worker generates a personalized certificate PDF and emails it.

**Architecture (buildable in one session)**:

```
Student hits 100% progress
    ↓
./cf complete  (new command)  →  opens browser to https://cyberfuturo.com/certificate?progress=<sha>
    ↓
Landing page validates the progress sha against a public list of completion hashes
    ↓
Student clicks Stripe Checkout ($29 Brazilian real-currency price: R$149)
    ↓
Stripe webhook → Cloudflare Worker → generate SVG certificate → convert to PDF
    ↓
Email PDF to student + add entry to public /verify/<id> page
```

**Stack** (every component free or near-free):

| Component | Service | Free tier enough? |
|---|---|---|
| Payment | Stripe | Yes (fees per transaction: 2.9% + 30¢) |
| Webhook handler | Cloudflare Worker | Yes (100k req/day free) |
| PDF generation | Python ReportLab or pure-stdlib SVG→embed in HTML→print | Yes |
| Email delivery | Resend / Postmark free tier, or Stripe's own receipt email | Yes |
| Database of completions | Cloudflare D1 or a single JSON file in the repo | Yes |
| Verification page | Static HTML generated by a GitHub Action on each new cert | Yes |

**Price rationale**:
- **$29 USD globally**: the sweet spot for a credential where the content is free. Matches Boot.dev certificate pricing.
- **R$149 BRL in Brazil**: regional pricing honors local purchasing power. ~$27 at current exchange rates.
- **€29 / £25** for Europe.

**Realistic conversion**:
- **Completion rate** of free EdTech courses: 2–5% of starters finish
- **Certificate conversion rate** of completers: 10–30% will pay
- **Blended**: ~0.5% of site visitors end up paying

**Revenue projections**:

| Monthly site visitors | Completions | Paying (20%) | Monthly revenue |
|---|---|---|---|
| 1,000 | ~30 | ~6 | **$174** |
| 5,000 | ~150 | ~30 | **$870** |
| 20,000 | ~600 | ~120 | **$3,480** |
| 50,000 | ~1,500 | ~300 | **$8,700** |
| 100,000 | ~3,000 | ~600 | **$17,400** |

**First dollar conditions**: ≥100 curriculum completions total. No earlier than month 4 post-launch.

**Build cost**: ~8 hours of focused work (Worker + Stripe + PDF renderer + verification page). Deferred until there's real completion data.

---

### 🥉 3. GitHub Sponsors / Patreon donations

**Format**: A passive "Support this project" link in every page footer. No commitment, no tiers, no perks. Just a donation button.

**Setup cost**: **5 minutes**. Enable GitHub Sponsors on the notifuturo account profile, add a `.github/FUNDING.yml` to the repo, add a footer link on cyberfuturo.com.

**Realistic revenue** (extrapolated from comparable free-EdTech projects):
- **The Odin Project**: ~$3,000/month on Patreon at ~250k monthly active users
- **Exercism.io**: ~$5,000/month on Stripe + Patreon at ~100k MAU
- **FreeCodeCamp**: $1M+/year in donations at millions of users

**For CyberFuturo** (orders of magnitude smaller audience):
- At 5k monthly active: **~$30–$100/month**
- At 50k monthly active: **~$300–$1,500/month**

**Why include it**: zero build cost, zero user friction, purely additive. And the number is small enough to not matter for revenue targets but large enough to cover the ~$1/month domain renewal.

**First dollar conditions**: none. Enable immediately after launch.

**Action**: add `.github/FUNDING.yml` and footer link in next session.

---

### 4. Corporate training / site licenses

**Format**: B2B deal. A small bootcamp, community college, or internal L&D team at a company pays $500–$5,000/year to use CyberFuturo as their onboarding or beginner track. May include:

- **Custom branding** — their logo on the landing page for their cohort
- **Progress tracking** — a dashboard showing which of their N learners have completed which lessons
- **Support contact** — a guaranteed 48-hour response SLA
- **Invoicing** — purchase order, W-9, actual invoice a procurement department can process

**Target buyers**:

| Segment | Examples | Typical deal size |
|---|---|---|
| Coding bootcamps | Le Wagon, Ironhack, Bertelsmann | $1,000–$3,000/year |
| Community colleges | US + LATAM public CS intros | $500–$2,000/year |
| F500 internal L&D | Engineering onboarding programs | $2,000–$5,000/year |
| NGOs / tech-education non-profits | Laboratoria, Reprograma, Digital Divide | Pay-what-you-can or free |

**First dollar conditions**:
- Real brand recognition (≥5,000 GitHub stars OR mentioned in a major press outlet)
- An active inbound inquiry (don't chase this; let it come to you)
- A recorded audience composition (i.e., you can quantify "N learners in Brazil, N in Mexico")

**Timeline**: probably year 2+. Highly variable.

---

### 5. Affiliate programs (passive revenue)

**Format**: Contextual affiliate links in lesson-adjacent content — never inside a lesson body, only in "see also" or "keep learning" sections. Revenue accrues passively based on click-through.

**Affiliate programs to apply for once audience exists**:

| Program | Commission | Relevance |
|---|---|---|
| HackTheBox | 20% recurring | Post-curriculum challenges |
| TryHackMe | 20% recurring | Beginner security |
| GitHub Copilot via referral | Varies | Mentioned in lesson 03 context |
| DigitalOcean | $25/signup | Hosting for projects |
| Hostinger | Variable | Hosting for projects |
| Fly.io | Variable | Deployment |
| Stripe Atlas | $25/referral | For founder-learners |

**Realistic revenue**: $100–$500/month passive at ~10k MAU.

**First dollar conditions**: ≥2,000 MAU. Apply to 3 programs, start with HTB + TryHackMe because their ICP is closest to ours.

---

### 6. Premium advanced track (deferred to v2)

**Format**: Free curriculum covers 7 prerequisite lessons. A separate paid "advanced" track — maybe containerization, deployment, databases at scale, real-world DevOps — sits in a separate private repo that $19/month members get access to.

**Why deferred**: The "prerequisites nobody teaches" wedge doesn't naturally extend to advanced content without competing with Codecademy, boot.dev, freeCodeCamp. Premium tier requires much more content investment than v0.1 justifies.

**Reconsider in year 2** if:
- Completion rates on the free track exceed 10% (signals real learning, not drive-by stars)
- Existing learners repeatedly ask "what should I learn next"
- At least 2 advanced-level lessons can be built that are demonstrably better than free alternatives

Otherwise: stay free-only and lean on streams #1–#5.

---

## Phased rollout — bound to real signal

### Phase 0: Launch (now — week 1)

**Status**: ✅ **complete**. 7 free lessons, live site, public repo, Codespaces working.

**Revenue**: **$0**. This is correct. The goal is signal, not cash.

**Metrics to watch**:
- GitHub stars
- Unique site visitors (per Cloudflare Web Analytics)
- Codespaces launches (from repo insights)
- `./cf check` passes (unknown — no telemetry)
- Inbound messages (emails, GitHub issues, DMs)

---

### Phase 1: First signal (week 2 — month 3)

**Actions**:
1. Enable GitHub Sponsors (5 min)
2. Add `.github/FUNDING.yml` and footer link (5 min)
3. Post on HN Show HN, r/brdev, r/learnprogramming, r/cscareerquestions, LinkedIn, Twitter
4. Respond to every single issue, comment, and DM within 24 hours
5. Track every mention of the project externally (Google Alerts, Bluesky search)

**Revenue target**: **$0–$200/month** (only donations, no paid product yet).

**Exit criteria to move to Phase 2**: any one of:
- 500 GitHub stars
- 1,000 unique site visitors in a week
- 50 curriculum completions verifiable via a public counter

---

### Phase 2: First sponsor (month 3–6)

**Actions**:
1. Build the audience data page (anonymized completion count, language breakdown, geo)
2. Cold-email 10 tier-A sponsor targets (see stream #1 template)
3. Close 1 founding sponsor at $500/month or $150/week
4. Add sponsor bar to landing page (all 4 languages)
5. Post "Launching with our founding sponsor [X]" on all channels — sponsor gets free press

**Revenue target**: **$500–$2,000/month**.

**Exit criteria to move to Phase 3**:
- ≥100 curriculum completions
- Sponsor relationship healthy (not churning)
- Inbound interest in "where's my certificate" mentioned at least 3 times

---

### Phase 3: Certificates (month 6–12)

**Actions**:
1. Build the certification pipeline (Stripe Checkout, Worker, PDF generator, verification page)
2. Launch at $29 USD / R$149 BRL / €29 EUR / £25 GBP
3. Post "Get your CyberFuturo certificate" announcement
4. Add a GitHub Action that updates the public verification list
5. Onboard second sponsor at higher rate based on new traffic

**Revenue target**: **$1,500–$5,000/month**.

**Exit criteria to move to Phase 4**:
- Certificate sales at steady-state ≥$1,000/month
- At least one corporate inquiry received
- 10,000 monthly active learners

---

### Phase 4: Scale (year 1+)

**Actions**:
1. Launch corporate license tier (1 page on the site, an "enterprise" contact form)
2. Open affiliate partnerships (HTB, TryHackMe first)
3. Raise sponsor rates to standard tier
4. Write a `state of CyberFuturo` annual post (the "X% of our learners are in Brazil; Y% complete the course" report)
5. Hire someone part-time to answer GitHub issues and pull requests (should be covered by sponsor revenue by now)

**Revenue target**: **$5,000–$15,000/month**.

---

### Phase 5: Brand (year 2+)

**Actions**:
1. Re-evaluate premium advanced track (see stream #6)
2. Consider job board
3. Consider community / Discord
4. Write the book / course companion
5. Begin speaking / conference presence

**Revenue target**: **$15,000–$50,000+/month**.

---

## What will never happen

These are off the table, forever, per the editorial rules:

- Gating any free lesson behind payment
- Showing ads inside a lesson
- Selling or sharing learner emails to sponsors
- "Free trial then charge" models
- Upselling sponsors to editorial content
- Hiding test/auto-grader logic from students (they can always read `test.py`)
- Requiring payment for a verification credential beyond our own certificate

The project is open-source and will remain so. The revenue model is **what we add around the free content**, not what we take away from it.

---

## Cost basis (reality check)

Against the revenue projections above, here's what CyberFuturo actually costs to run:

| Item | Cost |
|---|---|
| Domain (cyberfuturo.com) | ~$12/year = ~$1/month |
| GitHub (public repo, free) | $0 |
| Cloudflare Pages | $0 |
| Cloudflare Workers (when Phase 3 lands) | $0 free tier, then ~$5/month at scale |
| GitHub Actions for auto-deploy | $0 (public repo: unlimited free minutes) |
| Formsubmit.co for waitlist | $0 |
| Beehiiv (when newsletter gets added) | $0 up to 2,500 subs |
| Analytics (Cloudflare Web Analytics) | $0 |
| Stripe (when Phase 3 lands) | $0 monthly, 2.9%+$0.30 per transaction |
| Email delivery (Resend free tier) | $0 |
| **Total at Phase 2** | **~$1/month** |
| **Total at Phase 3** | **~$5–$10/month** |
| **Total at Phase 4** | **~$20–$50/month** |

**Break-even is trivially achieved at Phase 1 donations.** Every dollar above that is pure margin.

---

## Changelog

| Version | Date | Change |
|---|---|---|
| v0.1 | 2026-04-11 | Initial roadmap. 6 streams identified, 5-phase rollout documented. |

This is a **working plan**, not a **promise**. If Phase 1 signal doesn't materialize, we revisit the whole thing. If Phase 2 sponsorship negotiations reveal the rate card is off, we revisit. If certificates convert at 5% instead of 20%, we revisit. The roadmap exists to be refined, not to be cargo-culted.

---

*Written as of 2026-04-11 — the day the repo flipped public and the first phase officially began.*

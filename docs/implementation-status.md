# CyberFuturo — Implementation Status

> Last updated: 2026-04-21.
>
> Tracks the three specs in `docs/*-spec.md` and enumerates what's pending on the founder's side (things I cannot do autonomously because they require external accounts, credentials, content authorship, design decisions, or legal/business judgment).

---

## ✅ Shipped

### URL restructure spec — `docs/url-restructure-spec.md`

**LIVE.** Commits `b5eb2ce` + `76992cc`. Bare root 302s to the best language; `/pt/`, `/es/`, `/en/`, `/fr/` are equal. `_worker.js` owns all edge routing.

### Telemetry spec — `docs/telemetry-spec.md`

**LIVE.** Commit `1f42c7c`. `/api/ping` POST/OPTIONS/DELETE integrated into `_worker.js` as a route branch. Strict validation, idempotent inserts, tombstone forget table, zero PII. Four privacy pages live in all languages. Runner has opt-in prompt + fire-and-forget `ping()` + `./cf telemetry [status|on|off|forget]`.

**Endpoint returns 503 until you add the D1 binding** (see "Requires you" below).

### Product spec — `docs/product-spec.md` (Phase C — skeleton)

**CODE APPLIED in working tree.** Not yet committed. Covers the endpoint skeleton + access control. Scope notes after the file list.

**Files created:**

| Path | What it does |
|---|---|
| (none new in this round — schema extended in place) | — |

**Files modified:**

| Path | What changed |
|---|---|
| `scripts/d1_schema.sql` | Added `buyers`, `artifacts`, `webhook_log` tables + indexes (spec §4). All `CREATE IF NOT EXISTS`; re-running is safe. |
| `site/_worker.js` | Added `/api/purchase/stripe` (manual HMAC-SHA256 via Web Crypto, no Stripe SDK), `/api/activate`, `/auth`, and cookie-gate middleware for `/pt/livro/` `/es/libro/` `/en/book/` `/fr/livre/`. Welcome email via Resend, skipped gracefully when `RESEND_API_KEY` is absent. Worker is 572 lines — over CLAUDE.md's 500-line soft cap. Still single-file manageable (every route is a named section); will introduce a bundler + split when it exceeds ~700 or we need npm imports like the full Stripe SDK. |
| `curriculum/runner/main.py` | Added `./cf activate CODIGO` — POSTs `{code, anon_id}` to `/api/activate`, writes `activated=true` and `verify_url` to progress on success. Auto-generates an `anon_id` and opts-in to telemetry on first activation. |
| `.github/workflows/deploy.yml` | Post-deploy smoke tests: `/auth` without token → 400/503, `/api/activate` empty body → 400/503, `/api/purchase/stripe` no signature → 400/503, `/pt/livro/foo/` no cookie → 302 to `/pt/comprar/`. |

**Architectural decision — no Stripe SDK:**

Spec §5.2 imports `Stripe` from npm. Advanced-mode `_worker.js` has no bundler, so the SDK isn't loadable without a build step. Instead, HMAC signature verification is implemented directly against the Stripe docs (`t=<ts>,v1=<hmac>` header format, HMAC-SHA256 of `<ts>.<rawBody>` using `STRIPE_WEBHOOK_SECRET`). This is:
- Smaller (no npm dep, no bundler)
- Faster (cold-start reduces by a few ms)
- Auditable (30 lines of cryptography vs. Stripe SDK surface area)
- Exactly what Stripe officially documents for environments without their SDK

If the product spec later needs the full Stripe SDK (for refunds, customer portal, subscriptions), we introduce a wrangler build step at that point. For the webhook path only, manual HMAC is correct.

**Validation done:**

- `python3 -m py_compile curriculum/runner/main.py` passes; help lists the new `activate` subcommand
- `./cf activate` with no arg prints the usage message
- `./cf activate HELLO123` attempts the network call (currently hits the live prod site which 404s because the route isn't deployed yet — will pass after push + deploy)
- `sqlite3` in-memory roundtrip: schema applies cleanly, buyer + artifact + webhook_log inserts all succeed, webhook dedup returns rowcount=0 on replay
- `node --check site/_worker.js` parses; ESM import exposes a `fetch` function
- HMAC-SHA256 roundtrip via Web Crypto produces 64-hex output matching Stripe's expected format
- `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/deploy.yml'))"` passes

**Not included in this round** (deferred until founder prerequisites land):

- **Buy pages** (`/pt/comprar/` etc., spec §12) — need Payment Link URLs from Stripe dashboard
- **Chapter content refactor** (spec §3) — splits each `lesson.md` into `task.md` + `site/pt/livro/NN-slug/index.html`; chapter prose is founder-authored
- **52 SVG templates** (spec §10)
- **Handout/cert PDF generation** (spec §9.3) — Cloudflare Browser Rendering requires the Workers Paid plan (~$5/mo), contradicting the free-tier ADR. SVG-only fallback works on free tier; we'll wire that in once templates exist
- **Verify + backers pages** (spec §11) — nightly GitHub Action that reads D1 artifacts and rebuilds static HTML; depends on populated `artifacts` rows
- **Orientation pages** (`como-comecar/`, spec §13) — short content page, low priority
- **Landing-page price card** (spec §14) — updates `site/pt/index.html` etc. with the R$47/$9 CTA next to "Open in Codespaces"

---

## ⏸️ Requires you

These are the external-account / dashboard / content items only you can do.

### For telemetry (do this first; unlocks /api/ping):

1. **Create D1 database** (~5 min, one-time, needs `wrangler` authenticated):
   ```bash
   wrangler d1 create cf_telemetry
   # Copy the database_id from the output.
   wrangler d1 execute cf_telemetry --file scripts/d1_schema.sql
   ```
2. **Bind D1 to Pages project** (dashboard, ~5 min):
   - Cloudflare dashboard → Workers & Pages → `cyberfuturo` → Settings → Functions → D1 database bindings
   - Add binding: variable name `CF_TELEMETRY`, database `cf_telemetry`
   - Redeploy (push any commit, or click "Retry deployment")
3. **(Optional)** set `CF_TELEMETRY_DISABLED` env var as an operator escape hatch

### For product (do these before the buy flow works end-to-end):

1. **Stripe account** — enable BRL + Pix if possible
2. **Stripe product + prices + payment links:**
   - Product: "CyberFuturo — Livro Interativo"
   - Prices: `PRICE_BR` = R$47 BRL, `PRICE_GLOBAL` = $9 USD
   - Payment Links:
     - BR → `PRICE_BR`, methods: pix, boleto, card (up to 12×), custom field `lang_pref` (pt/es)
     - Global → `PRICE_GLOBAL`, methods: card, apple_pay, google_pay, link, custom field `lang_pref` (pt/es/en/fr)
   - Webhook endpoint: `POST https://cyberfuturo.com/api/purchase/stripe`, event: `checkout.session.completed` only, copy signing secret
3. **Pages env vars** (dashboard → Production):
   - `STRIPE_SECRET_KEY` = `sk_live_...`
   - `STRIPE_WEBHOOK_SECRET` = `whsec_...`
   - `RESEND_API_KEY` = `re_...` (create Resend account first; free tier 3,000/mo)
4. **R2 bucket** (for artifact PDFs when we get there):
   ```bash
   wrangler r2 bucket create cyberfuturo-artifacts
   ```
   Then dashboard → Pages → Settings → Functions:
   - R2 binding: `CF_ARTIFACTS` → `cyberfuturo-artifacts`
   - Browser Rendering: enable (note: requires Workers Paid plan). If staying on free tier, we ship SVG-only handouts instead.
5. **DNS records for email** — Resend dashboard generates the SPF/DKIM/DMARC records for `cyberfuturo.com`
6. **Paste the two Payment Link URLs** once I've written the buy-page routes (I'll leave sentinels for you to swap)
7. **Author chapter content** — the big unknown-scope item. All 9 chapters × 4 languages need prose teaching content
8. **Design 52 SVG templates** (9 handouts × 4 languages + 3 module certs × 4 languages + 1 final × 4 languages). One concrete PT example exists in spec §10

Estimated time on your side for 1-5 (excluding content authorship and template design): **~3-4 hours**.

---

## 📋 Wider roadmap (no action now)

- **Public `/stats/` dashboard** — nightly GitHub Action reads D1, rebuilds an aggregate stats page
- **YouTube companion channel** — optional, content strategy only
- **Hook-PDF sharing toolkit** — "share" button on verify pages for LinkedIn/Twitter/WhatsApp
- **Grant applications** — OEI, CPLP, OIF, Erasmus+, FINEP — pursue when brand recognition exists
- **Edition-upgrade flow** (v1.x → v2.0) — spec when v2.0 content is in sight

---

## Suggested order of operations

1. **Now**: review the Phase C diff → commit → push → watch deploy. Smoke tests cover the new endpoints without needing D1 data
2. **This week** (you): D1 create + dashboard binding (~15 min) — unlocks telemetry. Then Stripe + Resend + R2 setup (~3h) — unlocks the webhook path
3. **After that** (me): once Payment Links exist, ship the buy pages + the chapter-splitter tooling + SVG-only handout fallback
4. **Parallel track (you)**: chapter content authorship + SVG template design
5. **Launch candidate**: when step 3 is live AND v1.0 content exists AND Stripe Payment Links + webhook are end-to-end tested in Stripe test mode

At that point, the site is a fully self-running paid-book-with-certificates on Cloudflare free tier + Stripe fees. No servers. No ongoing human touch.

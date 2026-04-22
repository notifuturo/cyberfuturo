# CyberFuturo — Implementation Status

> Last updated: 2026-04-22.
>
> Tracks the three specs in `docs/*-spec.md` and enumerates what's pending on the founder's side (things I cannot do autonomously because they require external accounts, credentials, content authorship, design decisions, or legal/business judgment).

---

## 🎯 Next session — pick up here

**Infrastructure is fully wired on sandbox; both Stripe secrets are set.** The remaining gating items are founder account-setup only. In order of payoff:

1. **Create Resend account + add `RESEND_API_KEY`** (free tier 3,000/mo) — without this the webhook inserts the buyer row but sends no welcome email:
   - Sign up at resend.com
   - Add + verify the `cyberfuturo.com` domain (DNS records for SPF, DKIM, DMARC)
   - Create an API key
   - Upload: `printf 're_YOUR_KEY' | wrangler pages secret put RESEND_API_KEY --project-name=cyberfuturo`

2. **Enable R2** (dashboard → R2 → Enable, one-click, required when we add artifact PDFs next)

3. **Do a sandbox test purchase**:
   - Visit `https://cyberfuturo.pages.dev/pt/comprar/` in incognito
   - Pay with test card `4242 4242 4242 4242` (any future expiry, any CVC, any ZIP)
   - Expect welcome email (if Resend was set up)
   - Verify in D1: `wrangler d1 execute cf_telemetry --remote --command "SELECT email, substr(access_token,1,8) as tok, activation_code, lang_pref FROM buyers ORDER BY id DESC LIMIT 3"`
   - Open magic link `https://cyberfuturo.com/auth?t=<access_token>` → should 302 to `/pt/curso/00-bienvenido/` (which will then 404 since chapters don't exist yet)
   - In a Codespace: `./cf activate <ACTIVATION_CODE>` → expect "✔ Conta vinculada."

4. **Then tell me** — I'll pick up the next spec chunk (chapter content refactor, SVG-only handout fallback, verify pages, or whatever you prioritize).

---

## Current state summary

| Layer | Status |
|---|---|
| URL restructure (4-language equal paths) | ✅ Live |
| Root-redirect language selection | ✅ Live via `_worker.js` |
| Telemetry ingest + `./cf telemetry` | ✅ Live, D1 bound, end-to-end tested |
| Privacy pages (all 4 languages) | ✅ Live |
| Product endpoints (webhook, auth, activate, cookie gate) | ✅ Wired, awaiting Stripe secret |
| Buy pages (all 4 languages) | ✅ Live, Payment Link hardcoded |
| D1 schema | ✅ Applied to prod (`cf_telemetry`, id `97f0f6c2-...`) |
| `STRIPE_WEBHOOK_SECRET` | ✅ Set |
| `STRIPE_SECRET_KEY` | ✅ Set |
| `RESEND_API_KEY` | ⏸️ Founder to add |
| R2 bucket for PDFs | ⏸️ Founder to enable R2 feature |
| Orientation pages (4 langs) | ✅ Live |
| Course TOC landing (4 langs) | ✅ Live |
| Chapter 00 (free full sample, 4 langs) | ✅ Live |
| Chapter 01 (substantive preview, 4 langs) | ✅ Live |
| Chapters 02–08 (locked previews, 4 langs × 7 = 28 pages) | ✅ Live |
| Chapter reader design (editorial + terminal sidecar) | ✅ Live |
| Certificate template (cream paper, sample at /verify/cf-2026-sample/) | ✅ Live |
| Sitemap (generated, 56 URLs) | ✅ Live |
| Full teaching content for paid chapters 01–08 | ⏸️ Founder-authored (previews ship the pitch; full prose pending) |
| SVG handout templates (52 total) | ⏸️ Founder-authored |
| PDF rendering pipeline | ⏸️ Pending templates + R2 |
| Real /verify/ pages per buyer | ⏸️ Pending D1 `artifacts` rows |
| Backers wall | ⏸️ Pending buyer opt-ins |


---

## ✅ Shipped

### URL restructure spec — `docs/url-restructure-spec.md`

**LIVE.** Commits `b5eb2ce` + `76992cc`. Bare root 302s to the best language; `/pt/`, `/es/`, `/en/`, `/fr/` are equal. `_worker.js` owns all edge routing.

### Telemetry spec — `docs/telemetry-spec.md`

**LIVE.** Commit `1f42c7c`. `/api/ping` POST/OPTIONS/DELETE integrated into `_worker.js` as a route branch. Strict validation, idempotent inserts, tombstone forget table, zero PII. Four privacy pages live in all languages. Runner has opt-in prompt + fire-and-forget `ping()` + `./cf telemetry [status|on|off|forget]`.

**Endpoint returns 503 until you add the D1 binding** (see "Requires you" below).

### Product spec — `docs/product-spec.md` (Phase C — skeleton + Phase D — buy pages)

**SHIPPED** commits `20b1199` + `ec2bad9` + `d775540` (endpoint skeleton); **Phase D buy pages applied in working tree** (not yet committed). Scope notes after the file list.

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

**Phase D — buy pages (new, 2026-04-21):**

Payment Link URL baked into static HTML at `site/pt/comprar/`, `site/es/comprar/`, `site/en/buy/`, `site/fr/acheter/`. Each page: hero with $9 USD + "Stripe auto-converts locally + Pix for BR buyers via Adaptive Pricing" explanation, 5-item value list (chapters / handouts / certs / lifetime / exercises stay free), 4-question FAQ, primary CTA linking to the test Payment Link `https://buy.stripe.com/test_aFa28q9kbet9bXI8AcdIA00`. Landing pages gained a secondary "Buy the book · $9" button between "Open in Codespaces" and "See how it works". Footers cross-link to the localized buy page.

**Architectural decision — no country-routing Pages Function:**

The spec §12.1 wired each buy page to a Pages Function that picked one of two Payment Links based on `CF-IPCountry` (BR-specific BRL link vs. global USD link). With Stripe's Canada-registered account + Adaptive Pricing always-on for Payment Links, a **single** USD Payment Link covers all regions — Stripe shows BR buyers the BRL-converted amount with Pix enabled automatically at checkout. So buy pages are plain static HTML with a single hardcoded Payment Link URL. When flipping to live mode, the test URL needs to be replaced across the 4 files (marker comment in each HTML head notes this). Simpler, fewer moving parts, one URL source of truth.

**Phase E — orientation + footer wiring (new, 2026-04-22):**

Shipped 4 orientation pages per spec §13 at `/pt/como-comecar/`, `/es/como-empezar/`, `/en/getting-started/`, `/fr/comment-commencer/`. Each page: hero + CTA to Codespaces, three numbered steps (open Codespace → `./cf list` → `./cf start NN` + `./cf check`), pitch-back to the buy page for full chapters. Footer on every landing page replaced the old in-page `#comecar` anchor with a link to the dedicated orientation page (now discoverable off-landing); buy-page footers gained the same link. Sitemap adds the 4 new URLs with full hreflang alternates. Fully static, no Pages Function needed.

**Phase F — teaser gate (new, 2026-04-22):**

`_worker.js` cookie gate now allow-lists chapter `00-bienvenido` in all 4 language course paths, in preparation for the "read chapter 00 free, unlock the rest for $9" flow the designer settled on. A new `FREE_TEASER_SLUGS` set + `isFreeTeaser()` helper short-circuits `enforceAccessGate` before the DB + cookie checks. Smoke tests extended in `.github/workflows/deploy.yml` to cover both the gated path (`/pt/curso/foo/` still 302s to buy) and the teaser (`/{lang}/{course}/00-bienvenido/` does NOT redirect to a buy URL). Teaser chapter HTML itself is still unauthored — the gate just stops standing in the way. Validated with a 10-case node unit test of the slug matcher across all 4 language prefixes + nested asset paths + edge cases (bare prefix, trailing slug without slash).

**Phase H — Claude Design handoff implementation (new, 2026-04-22):**

Received hi-fi handoff from Claude Design in `_private/design-handoff-2026-04-22/` (gitignored). Direction: **"Editorial + Terminal"** — three-column chapter reader with Inter Tight prose body, persistent terminal sidecar, ASCII-tree TOC. Shipped across five commits:

  - **Phase H.1** (`76bda45` + `0fd3d1d`) — Foundation: `--surface-3`, `--glow-*`, `--paper-*` tokens, `--mono/--sans/--serif` font variables, Inter Tight loaded on every page, ambient radial hero glow, proof strip (8 pills, 4 langs), comparison table (regional competitors, 4 langs).
  - **Phase H.2** (`964a4df`) — Chapter 00 reader in 4 langs (editorial prose, in-article terminal mock, summary card, live-Codespace sidecar, pure-CSS mobile drawer via `:target`).
  - **Phase H.3** (`aa2cfc0`) — Course TOC landing + chapter 01 preview in 4 langs + worker `FREE_TEASER_SLUGS` expanded + smoke tests.
  - **Phase H.4** (`eb22fef`) — Cream-paper certificate at `/verify/cf-2026-sample/` (cf-cert-* CSS, Crimson Pro serif for buyer name, `@media print A4 landscape`).
  - **Phase H.5** (`788ae8c`) — Chapters 02–08 preview pages × 4 langs = 28 pages via `scripts/gen_chapter_previews.py` (stdlib Python generator, single source of truth for chapter metadata + per-language copy). Worker opens all 9 chapter slugs to anon browsing. Follow-up `ab90453` bumped post-deploy smoke sleep 12s → 20s to absorb edge propagation on large deploys.

Generators under `scripts/`:
  - `gen_chapter_previews.py` — writes `site/{lang}/{course_dir}/NN-slug/index.html` for chapters 02–08 × 4 langs (skips 00/01 which are hand-authored). Idempotent.
  - `gen_sitemap.py` — walks the expected page shapes across 4 langs, verifies every file exists, emits `site/sitemap.xml` with hreflang alternates + x-default. 56 URLs today.

Shipped from Claude Design's "Open questions" (first-brief §10) answered by the designer:
  - Reader typography: mono chrome + Inter Tight body prose ✓
  - Light/dark: dark site, cream certificates ✓
  - Imagery: type-only, no illustration ✓
  - Locked state: preview + banner, no hard redirect ✓
  - Mobile-first reader ✓

**Phase G — `livro/libro/book/livre` → `curso/curso/course/cours` rename (new, 2026-04-22):**

The paid product is an interactive course with progress tracking and a 4-tier certificate ladder, not a book, so the URL slug and copy both moved. Decision anchored to market research: Platzi (LatAm EdTech leader) uses `/cursos/`; in BR, Alura and Rocketseat reserve "Formação" for multi-curso certificate tracks and use "Curso" for a single linear 9-chapter unit, which CyberFuturo is. `/course/` is the global default (Coursera, Udemy, edX, Frontend Masters). Alternative `formação/formation/formación/formation` was considered but rejected — EN "formation" reads religious/military, not EdTech.

Changes: `_worker.js` `GATED_PATHS` + `/auth` redirect + welcome email body copy (PT/ES/EN/FR); 12 HTML files (hero CTA buttons, FAQ copy referencing "o livro"/"the book", orientation page "part of the book" → "part of the course"); CI smoke tests. Added a new `LEGACY_REDIRECTS` table + `matchLegacyRedirect` in `_worker.js` that 301s any `/{lang}/{livro|libro|book|livre}/...` hit to the new `/{lang}/{curso|curso|course|cours}/...` equivalent — preserves any magic-link URLs already sent out from sandbox testing. Smoke tests verify both the 301 path and the no-gate-on-new-teaser path across all 4 languages.

Chapters inside the course are still "capítulos" / "chapters" / "chapitres" — a curso having capítulos is the natural nesting. One false-positive `livres` string in `site/fr/index.html:222` is intentional: the SQL-lesson example ("Bibliothèque de livres avec filtres") references the SQLite books-library demo, not the CyberFuturo product.

`docs/product-spec.md` and `docs/url-restructure-spec.md` are historical design artifacts from before this rename and still say `/livro|libro|book|livre/`. Both have a banner at the top pointing here. When reading those specs, mentally substitute the new paths.

Landing-page price card (spec §14) remains partial: the secondary "Buy the book · $9" CTA from Phase D is live, but the country-routed R$47/$9 auto-localized card below the hero isn't wired yet (waits on the Pages Function pattern from spec §12.1, which we dropped in favor of Stripe Adaptive Pricing — so this item may already be obsolete; revisit when real BR buyers land).

**Not included in this round** (deferred until founder prerequisites land):

- Removed: ~~buy pages~~ ✓ done
- Removed: ~~orientation pages~~ ✓ done (Phase E)
- **Chapter content refactor** (spec §3) — splits each `lesson.md` into `task.md` + `site/pt/curso/NN-slug/index.html`; chapter prose is founder-authored
- **52 SVG templates** (spec §10)
- **Handout/cert PDF generation** (spec §9.3) — Cloudflare Browser Rendering requires the Workers Paid plan (~$5/mo), contradicting the free-tier ADR. SVG-only fallback works on free tier; we'll wire that in once templates exist
- **Verify + backers pages** (spec §11) — nightly GitHub Action that reads D1 artifacts and rebuilds static HTML; depends on populated `artifacts` rows

---

## ⏸️ Requires you

These are the external-account / dashboard / content items only you can do.

### For telemetry — DONE

✅ D1 database `cf_telemetry` created (id `97f0f6c2-9d6f-4fb9-9107-d0cd3836e2ac`, region ENAM) via wrangler CLI.
✅ Schema applied remotely (events + forgotten_ids + buyers + artifacts + webhook_log, all 5 tables live).
✅ D1 binding declared in **repo-root** `wrangler.toml` (with `pages_build_output_dir = "site"`) — Pages deploy picks it up automatically, no dashboard click needed.
✅ `STRIPE_WEBHOOK_SECRET` uploaded encrypted via `wrangler pages secret put`.
✅ End-to-end test: `POST /api/ping` → 204, row inserted in D1 with `country=CA` detected at the edge. `POST /api/activate` returns 400/404 (not 503). `/auth` returns 400. All endpoints are live.

All this happened via `wrangler` CLI already-authenticated on the dev machine as `futuronoti@gmail.com`. No dashboard work was needed.

**Gotcha note:** `wrangler.toml` had to live at the **repo root**, not inside `site/`. When `wrangler pages deploy site` runs, it treats everything in `site/` as static assets — so `site/wrangler.toml` got uploaded as a deployment artifact instead of being read as project config. At the repo root, wrangler finds it via its usual config search path and applies bindings.

**Optional operator escape hatch:** if you ever need to force-disable telemetry without code changes, set `CF_TELEMETRY_DISABLED=1` as a Pages env var. Leaving it unset is the default.

### For product (do these before the buy flow works end-to-end):

1. **Stripe account** — enable BRL + Pix if possible
2. **Stripe product + prices + payment links:**
   - Product: "CyberFuturo — Livro Interativo"
   - Prices: `PRICE_BR` = R$47 BRL, `PRICE_GLOBAL` = $9 USD
   - Payment Links:
     - BR → `PRICE_BR`, methods: pix, boleto, card (up to 12×), custom field `lang_pref` (pt/es)
     - Global → `PRICE_GLOBAL`, methods: card, apple_pay, google_pay, link, custom field `lang_pref` (pt/es/en/fr)
   - Webhook endpoint: `POST https://cyberfuturo.com/api/purchase/stripe`, event: `checkout.session.completed` only, copy signing secret
3. **Pages env vars:**
   - ✅ `STRIPE_WEBHOOK_SECRET` — already set for sandbox (rotate + re-put when going live; see §17)
   - ✅ `STRIPE_SECRET_KEY` — uploaded via `wrangler pages secret put` (rotate + re-put when flipping to live mode)
   - ⏸️ `RESEND_API_KEY` = `re_...` (create Resend account first; free tier 3,000/mo). Same `wrangler pages secret put` pattern.
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

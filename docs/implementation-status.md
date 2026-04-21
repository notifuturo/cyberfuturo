# CyberFuturo — Implementation Status

> Last updated: 2026-04-21.
>
> This doc tracks the progress of the three specs in `docs/*-spec.md` and enumerates what's pending on the founder's side (things I cannot do autonomously because they require external accounts, credentials, content authorship, design decisions, or legal/business judgment).

---

## ✅ Shipped

### URL restructure spec — `docs/url-restructure-spec.md`

**Status: LIVE.** Commits `b5eb2ce` (equalize 4 languages) and `76992cc` (switch to `_worker.js` advanced mode to fix root redirect).

The bare root now 302s to the best language (cookie → Accept-Language → CF-IPCountry → `en`), and all four language homes live under `/pt/`, `/es/`, `/en/`, `/fr/`. Thank-you pages moved into their language folders. `_worker.js` owns all edge routing; the `functions/` directory was retired because static-asset handling couldn't cleanly hand the root over to a Function.

### Telemetry spec — `docs/telemetry-spec.md`

**Status: CODE APPLIED in working tree.** Architecture note: because the site now runs in `_worker.js` advanced mode, the spec's `site/functions/api/ping.js` is integrated directly into `site/_worker.js` as a `/api/ping` route branch. Same validation rules, same contract, same CORS — just dispatched by method inside the worker rather than by Pages Functions file conventions. See the `// ---- /api/ping` section in `site/_worker.js`.

**Files created:**

| Path | What it does |
|---|---|
| `scripts/d1_schema.sql` | D1 schema: `events` (UNIQUE(anon_id,event,lesson)) + `forgotten_ids` tombstones |
| `site/pt/privacidade/index.html` | Privacy contract in PT (canonical) |
| `site/es/privacidad/index.html` | Privacy contract in ES |
| `site/en/privacy/index.html` | Privacy contract in EN |
| `site/fr/confidentialite/index.html` | Privacy contract in FR |

**Files modified:**

| Path | What changed |
|---|---|
| `site/_worker.js` | Added `/api/ping` POST/OPTIONS/DELETE handlers bound to `env.CF_TELEMETRY` D1. Strict input validation, `INSERT OR IGNORE` idempotency, tombstone check. Returns 503 if the binding is missing. |
| `curriculum/runner/main.py` | Telemetry opt-in prompt (PT/ES/EN/FR), fire-and-forget `ping()` (2s timeout, swallows all network errors), wired into `cmd_start` and `cmd_check`, new `./cf telemetry [status\|on\|off\|forget]` subcommand, updated `__doc__` help. All stdlib, no new deps. |
| `site/pt/index.html` etc. | Footer now links to the language's privacy page |
| `.github/workflows/deploy.yml` | Basic smoke check: 4 new privacy-page file existence tests. Post-deploy: /pt/privacidade/, /es/privacidad/, /en/privacy/, /fr/confidentialite/ all return 200; `OPTIONS /api/ping` returns 204. |

**Validation done:**

- `python3 -m py_compile curriculum/runner/main.py` passes
- `./cf help` shows the four new `telemetry` subcommands
- `./cf telemetry status` prints "ainda não perguntada" on a fresh progress file
- No HTML file is orphaned; privacy pages cross-link in all four languages
- `_worker.js` keeps the root-redirect behavior intact; `/api/ping` is now the only non-root route the worker owns

**What to do to ship this:**

```bash
cd /home/cypherborg/cyberfuturo
git status
git diff
# Review, then commit + push. After the deploy smoke test passes,
# the telemetry endpoint will be live but will return 503 until the D1
# binding is added in the Cloudflare dashboard. That's fine — the runner's
# fire-and-forget pings swallow 5xx errors and keep working.
```

**What still requires YOU (do this to actually start receiving pings):**

1. **Create D1 database** — one-time, requires `wrangler` authenticated:
   ```bash
   wrangler d1 create cf_telemetry
   # Copy the database_id from the output.
   wrangler d1 execute cf_telemetry --file scripts/d1_schema.sql
   ```

2. **Bind D1 to the Pages project** — dashboard route (preferred for a public repo):
   - Cloudflare dashboard → Workers & Pages → `cyberfuturo` → Settings → Functions → D1 database bindings
   - Add binding: variable name `CF_TELEMETRY`, database `cf_telemetry`
   - Redeploy (push any commit, or click "Retry deployment")

3. **(Optional) Set Pages env var** for the operator escape hatch:
   - `CF_TELEMETRY_DISABLED` — normally unset; set to force-disable without touching the DB

Estimated time on your side: **~15 minutes.**

---

## ⏸️ Ready-to-apply but pending founder involvement

### Product spec — `docs/product-spec.md`

Untouched this round; I'll pick this up after the telemetry commit lands and the D1 binding is in place.

**What I can do autonomously (next round):**
- Extend `scripts/d1_schema.sql` with the `buyers`, `artifacts`, `webhook_log` tables (section 4)
- Integrate `/api/purchase/stripe`, `/api/activate`, `/auth/*`, and the `/livro/` cookie gate into `site/_worker.js` as additional route branches (same pattern as `/api/ping`)
- Add `site/_lib/email.js` and `site/_lib/artifacts.js` helpers — these live outside the worker and get imported into it
- Patch `curriculum/runner/main.py` to add `cmd_activate` (section 7.2)
- Write the 4 buy-page routes (section 12.1)
- Write `.github/workflows/rebuild-verify.yml` and `scripts/rebuild_verify_pages.py` (section 11)

**Architecture note for next round:** the product spec was written with Pages Functions (`site/functions/...`) in mind. All of that code integrates into `site/_worker.js` and the `site/_lib/` module tree, following the same pattern the telemetry integration already established. This is simpler than it sounds — each endpoint is a named `handleFoo` function called from the worker's `fetch` switch.

**What requires YOU:**

1. **Create a Stripe account** (if not already) and, if possible, enable BRL + Pix. Stripe onboarding tells you what documentation is needed (personal/MEI/CNPJ).

2. **In Stripe dashboard, create:**
   - One product: "CyberFuturo — Livro Interativo"
   - Two Prices on that product: **R$47 BRL** (`PRICE_BR`) and **$9 USD** (`PRICE_GLOBAL`)
   - Two Payment Links:
     - BR → `PRICE_BR`, payment methods: `pix`, `boleto`, `card` (with installment support up to 12×), custom field `lang_pref` (dropdown pt/es)
     - Global → `PRICE_GLOBAL`, payment methods: `card`, `apple_pay`, `google_pay`, `link`, custom field `lang_pref` (dropdown pt/es/en/fr)
   - One webhook endpoint: `POST https://cyberfuturo.com/api/purchase/stripe`, events: `checkout.session.completed` only, copy the signing secret

3. **Set Pages env vars** (Cloudflare dashboard → Pages → `cyberfuturo` → Settings → Environment variables, Production):
   - `STRIPE_SECRET_KEY` = `sk_live_...`
   - `STRIPE_WEBHOOK_SECRET` = `whsec_...`
   - `RESEND_API_KEY` = `re_...` (create Resend account first; free tier 3,000/mo)

4. **Create R2 bucket + Browser Rendering binding:**
   ```bash
   wrangler r2 bucket create cyberfuturo-artifacts
   ```
   Then dashboard → Pages → `cyberfuturo` → Settings → Functions:
   - R2 binding: `CF_ARTIFACTS` → `cyberfuturo-artifacts`
   - Browser Rendering: enable and name the binding `CF_BROWSER`

5. **DNS records for email** — Resend dashboard will give you the SPF, DKIM, and DMARC records to add at your domain registrar for `cyberfuturo.com`.

6. **Paste Payment Link URLs** into the four buy-page routes (I'll leave them with `REPLACE_WITH_BR_LINK` and `REPLACE_WITH_GLOBAL_LINK` sentinels).

7. **Author chapter content.** This is the big unknown-scope item. All 9 chapters × 4 languages need prose teaching content (not just the task statements). Current `lesson.md` files have some of this but need to be split per the spec's refactor section (section 3) AND expanded into real book chapters with the teaching context / explanations / GUI→CLI translation table for chapter 00.

8. **Design 52 SVG templates** (9 handouts × 4 languages + 3 module certs × 4 languages + 1 final cert × 4 languages). Spec has ONE concrete example (handout for chapter 04 PT). The remaining 51 follow the same pattern. Founder can author these or commission them.

9. **Legal / tax decisions:**
   - **Brazilian NFe (nota fiscal)**: manual via prefecture site, or subscribe to NFe.io (~R$30-50/mo). Deferred until volume justifies automation.
   - **Stripe Tax**: optional, enable for automatic VAT in EU/UK/AU. Not required for launch.

Estimated time on your side (excluding chapter-content authorship and template design): **~3-4 hours of account setup + dashboard work**.

---

## 📋 What's left in the wider roadmap (beyond these three specs)

No action needed now; listed for visibility.

- **Public `/stats/` dashboard** — nightly GitHub Action reads D1, rebuilds an aggregate-only stats page (completions per lesson, country distribution, trend). Separate spec when ready.
- **YouTube companion channel** (optional) — PT-BR videos driving audience to the site. Separate content strategy, no technical spec needed.
- **Hook-PDF sharing toolkit** — when a buyer completes a chapter, a "share" button on their verify page opens a one-click LinkedIn / Twitter / WhatsApp share modal with the PDF attached. Nice-to-have, not MVP.
- **Grant applications** (OEI, CPLP, OIF, Erasmus+, FINEP) — pursued when brand recognition exists and application time is warranted.
- **Edition-upgrade flow** (v1.x → v2.0) — spec'd briefly in `product-spec.md` section 18; produce a real spec once v2.0 content is in sight.

---

## Suggested order of operations

1. **Today**: review the telemetry diff → commit → push → watch deploy → provision D1 + dashboard binding
2. **This week**: Stripe + Cloudflare (R2 + Browser Rendering) + Resend account setup (3-4 hours)
3. **After that**: I come back and ship product-spec code integrated into `_worker.js`
4. **Parallel track (founder-owned)**: chapter content authorship + SVG template design
5. **Launch candidate**: when #3 is live AND enough chapter content exists for v1.0 of the book AND Stripe Payment Links + webhook are live end-to-end tested

At that point, the site is a fully self-running paid-book-with-certificates on Cloudflare free tier + Stripe fees. No servers. No ongoing human touch.

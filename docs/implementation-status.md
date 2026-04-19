# CyberFuturo — Implementation Status

> Last updated: 2026-04-18.
>
> This doc tracks the progress of the three specs in `docs/*-spec.md` and enumerates what's pending on the founder's side (things I cannot do autonomously because they require external accounts, credentials, content authorship, design decisions, or legal/business judgment).

---

## ✅ Applied (code ready to review, not yet committed)

### URL restructure spec — `docs/url-restructure-spec.md`

All mechanical changes applied in the working tree. Review the diff before committing.

**Files moved** (via `git mv`, history preserved):

| From | To |
|---|---|
| `site/index.html` | `site/pt/index.html` |
| `site/obrigado.html` | `site/pt/obrigado/index.html` |
| `site/gracias.html` | `site/es/gracias/index.html` |
| `site/thank-you.html` | `site/en/thank-you/index.html` |
| `site/merci.html` | `site/fr/merci/index.html` |

**Files created:**

| Path | What it does |
|---|---|
| `site/functions/index.js` | Root-redirect Pages Function: picks language from cookie → Accept-Language → CF-IPCountry → `en` fallback, returns 302 |

**Files modified:**

| Path | What changed |
|---|---|
| `site/pt/index.html` | Canonical + og:url now `/pt/`; hreflang for PT points to `/pt/`; language switcher symmetric with `data-lang` attrs; form `_next` → `/pt/obrigado/`; brand link → `/pt/`; inline cookie-setting + mismatch-banner script added before `</body>` |
| `site/es/index.html` | hreflang PT row updated to `/pt/`; language switcher symmetric; form `_next` → `/es/gracias/`; footer "Português" link → `/pt/`; inline script added |
| `site/en/index.html` | Same pattern as ES. Form `_next` → `/en/thank-you/` |
| `site/fr/index.html` | Same pattern as ES. Form `_next` → `/fr/merci/` |
| `site/pt/obrigado/index.html` | Symmetric switcher; brand link + "back to home" → `/pt/`; footer "Início" → `/pt/` |
| `site/es/gracias/index.html` | Symmetric switcher; footer "Português" → `/pt/` |
| `site/en/thank-you/index.html` | Symmetric switcher; footer "Português" → `/pt/` |
| `site/fr/merci/index.html` | Symmetric switcher; footer "Português" → `/pt/` |
| `site/404.html` | Language switcher symmetric; "Português" button → `/pt/`; footer "Início" → `/pt/` (brand-link left as bare `/` on purpose — falls through the root-redirect, behaves correctly) |
| `site/robots.txt` | Disallow paths updated to new directory-form URLs |
| `site/sitemap.xml` | All 4 language home pages now at equal priority 1.0; PT at `/pt/`; hreflang map includes `x-default → /` on every entry; lastmod 2026-04-18 |
| `site/styles.css` | Added `.lang-mismatch` banner styles (fixed bottom-right, animated fade-in) |
| `.github/workflows/deploy.yml` | Basic smoke check validates new paths + function; HTML-reference validation forbids stale `.html` thank-you paths; post-deploy smoke test verifies `/` returns 302 + all 8 new paths return 200 + Accept-Language routing sanity |

**Validation done:**

- File tree matches the spec (`find site -type f` produces the expected 12-file layout)
- No HTML file references stale `/obrigado.html` / `/gracias.html` / `/thank-you.html` / `/merci.html`
- No HTML file has `href="/"` (orphan bare-root links) except the intentional brand-link on `site/404.html`, which falls through the root redirect correctly
- deploy.yml syntax parses (workflow grammar unchanged except for added checks)

**What to do to ship this:**

```bash
# Review the diff
cd /home/cypherborg/cyberfuturo
git status
git diff site/ .github/workflows/deploy.yml

# Commit
git add -A
git commit -m "site: equalize 4 languages under /pt/ /es/ /en/ /fr/ + smart root redirect

Moves PT content from bare root into /pt/, moves thank-you pages into
their language folders, adds a Cloudflare Pages Function at the root
that picks language via cookie → Accept-Language → CF-IPCountry → en.

Updates hreflang, canonical, og:url, language switchers, sitemap,
robots, and deploy smoke tests. Adds a tiny first-visit mismatch
banner that respects reduced-motion. No functional change for existing
visitors; Google will re-map / → /pt/ as it recrawls over ~1-2 weeks."

# Push when ready
git push

# After deploy (watch: gh run watch):
# - Submit updated sitemap to Google Search Console → Sitemaps → resubmit
#   https://cyberfuturo.com/sitemap.xml
```

---

## ⏸️ Ready-to-apply but pending founder involvement

### Telemetry spec — `docs/telemetry-spec.md`

**What I can still do autonomously** (but have not yet, to keep scope clean until URL restructure lands):
- Write `scripts/d1_schema.sql` (the SQL is in the spec, section 4)
- Write `site/functions/api/ping.js` (Pages Function code in spec section 5)
- Write the 4 privacy pages at `site/pt/privacidade/`, `site/es/privacidad/`, `site/en/privacy/`, `site/fr/confidentialite/` (contract text in spec section 2)
- Patch `curriculum/runner/main.py` (sections 6.1-6.7)

I'll do all of that as Phase B after you green-light the URL restructure commit, so the two changes don't tangle in review.

**What requires YOU:**

1. **Create D1 database** — one-time command, requires `wrangler` authenticated:
   ```bash
   wrangler d1 create cf_telemetry
   # Copy the database_id into a note
   wrangler d1 execute cf_telemetry --file scripts/d1_schema.sql
   ```

2. **Bind D1 to the Pages project** — dashboard work:
   - Cloudflare dashboard → Workers & Pages → `cyberfuturo` → Settings → Functions → D1 database bindings
   - Add binding: variable name `CF_TELEMETRY`, database `cf_telemetry`

3. **Set Pages env var** for the opt-out escape hatch (optional):
   - `CF_TELEMETRY_DISABLED` — leave unset normally; operators can set it to force-disable all telemetry without touching the DB

Estimated time on your side: **~15 minutes**.

### Product spec — `docs/product-spec.md`

**What I can do autonomously:**
- Extend `scripts/d1_schema.sql` with the `buyers`, `artifacts`, `webhook_log` tables (section 4)
- Write `site/functions/api/purchase/stripe.js` (section 5.2) — the Stripe webhook
- Write `site/functions/auth.js` (section 6) — magic-link cookie endpoint
- Write `site/functions/api/activate.js` (section 7.1) — activation endpoint
- Write `site/functions/_middleware.js` (section 8) — cookie gate for `/livro/` routes
- Write `site/functions/_lib/email.js` and `site/functions/_lib/artifacts.js` (sections 5.3 and 9)
- Patch `curriculum/runner/main.py` to add `cmd_activate` (section 7.2)
- Write the 4 buy-page routing Pages Functions (section 12.1)
- Write the `.github/workflows/rebuild-verify.yml` (section 11)
- Write `scripts/rebuild_verify_pages.py` (section 11)

**What requires YOU:**

1. **Create a Stripe account** (if not already) and, if possible, enable BRL + Pix. Stripe onboarding flow will tell you what documentation is needed (personal/MEI/CNPJ).

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

6. **Paste Payment Link URLs** into the four buy-page functions (file paths shown above; I'll leave them with `REPLACE_WITH_BR_LINK` and `REPLACE_WITH_GLOBAL_LINK` sentinels).

7. **Author chapter content.** This is the big unknown-scope item. All 9 chapters × 4 languages need prose teaching content (not just the task statements). Current `lesson.md` files have some of this but need to be split per the spec's refactor section (section 3) AND expanded into real book chapters with the teaching context / explanations / GUI→CLI translation table for chapter 00.

8. **Design 52 SVG templates** (9 handouts × 4 languages + 3 module certs × 4 languages + 1 final cert × 4 languages). I wrote ONE concrete example in the spec (handout for chapter 04 PT). The remaining 51 follow the same pattern. Founder can author these or commission them.

9. **Legal / tax decisions:**
   - **Brazilian NFe (nota fiscal)**: manual via prefecture site, or subscribe to NFe.io (~R$30-50/mo). Deferred until volume justifies automation.
   - **Stripe Tax**: optional, enable for automatic VAT in EU/UK/AU. Not required for launch.

Estimated time on your side (excluding chapter-content authorship and template design): **~3-4 hours of account setup + dashboard work**.

---

## 📋 What's left in the wider roadmap (beyond these three specs)

These are things discussed in conversation but not yet specified. No action needed now; listed for visibility.

- **Public `/stats/` dashboard** — nightly GitHub Action reads D1, rebuilds an aggregate-only stats page (completions per lesson, country distribution, trend). Separate spec when ready.
- **YouTube companion channel** (optional) — PT-BR videos driving audience to the site. Separate content strategy, no technical spec needed.
- **Hook-PDF sharing toolkit** — when a buyer completes a chapter, a "share" button on their verify page opens a one-click LinkedIn / Twitter / WhatsApp share modal with the PDF attached. Nice-to-have, not MVP.
- **Grant applications** (OEI, CPLP, OIF, Erasmus+, FINEP) — pursued when brand recognition exists and application time is warranted.
- **Edition-upgrade flow** (v1.x → v2.0) — spec'd briefly in `product-spec.md` section 18; produce a real spec once v2.0 content is in sight.

---

## Suggested order of operations

1. **Today**: review the URL restructure diff → commit → push → watch deploy → submit sitemap to GSC
2. **Within the week**: you do the Stripe + Cloudflare (D1 + R2) + Resend account setup (3-4 hours)
3. **After that**: I come back and ship telemetry spec code + product spec code in one bundle
4. **Parallel track (founder-owned)**: chapter content authorship + SVG template design
5. **Launch candidate**: when #3 is live AND enough chapter content exists for v1.0 of the book AND Stripe Payment Links + webhook are live end-to-end tested

At that point, the site is a fully self-running paid-book-with-certificates on Cloudflare free tier + Stripe fees. No servers. No ongoing human touch.

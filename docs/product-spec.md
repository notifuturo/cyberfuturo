# CyberFuturo — Product Spec (Paid Reading + Handouts + Credentials)

> **Status**: Draft v1.0 — 2026-04-18. Not yet applied. Review → approve → apply.
>
> **⚠️ Path rename (2026-04-22):** this spec was drafted with `/pt/livro/`, `/es/libro/`, `/en/book/`, `/fr/livre/` as the paid-chapter paths. Those are now `/pt/curso/`, `/es/curso/`, `/en/course/`, `/fr/cours/` (Phase G in [`implementation-status.md`](./implementation-status.md) — "curso/course/cours" matches how Platzi + Alura frame a single-track EdTech product and better signals the course + progress + certification shape). `_worker.js` serves 301s from the legacy paths. When reading this spec, substitute the new paths wherever the old ones appear.
>
> **Purpose**: define the monetized product layer of CyberFuturo: paid reading access to all 9 chapters, per-chapter shareable handouts as buyer-earned artifacts, three-tier credentials (handouts + module certs + final cert), and a fully automated purchase-to-completion pipeline. Built entirely on Cloudflare free-tier + Stripe (single processor, no intermediaries). No servers, no ongoing human touch.
>
> **Prerequisites**: [`url-restructure-spec.md`](./url-restructure-spec.md) applied (language-equal URLs at `/pt/`, `/es/`, `/en/`, `/fr/`) and [`telemetry-spec.md`](./telemetry-spec.md) applied (opt-in `/api/ping` + D1 database `cf_telemetry` bound to the Pages project).

---

## 1. Goals and non-goals

### Goals

- Sell lifetime reading access to the book for a single one-time price: **R$47 BRL for Brazil, $9 USD everywhere else.** Both prices represent the same BRL-anchored economic value.
- Keep the book content copy-pirateable (buyers' handouts are shareable) but keep **credentials non-transferable** (each cert is tied to a specific purchase and a specific completion timeline).
- Generate shareable per-chapter handouts automatically on each lesson pass. Handouts function as both a buyer reference artifact AND organic viral marketing when shared.
- Generate module + final certificates automatically on milestone completions.
- Run the entire sales, activation, reading-access, handout, and credential pipeline on Cloudflare's free tier — the only recurring vendor cost is Stripe transaction fees (2.9% + $0.30 globally; Pix fees are lower for BR).
- Preserve the existing "free exercises, auto-grader, repo is public" contract. The paywall covers only the teaching *chapters* — not the *exercises*.
- Single payment processor: **Stripe, no intermediaries.** No Hotmart, no Gumroad, no resellers. Two Stripe Payment Links (one BR-specific with Pix + boleto + card, one global card-only) fronting a single checkout webhook.

### Non-goals

- No account system, no username/password, no profile page. Access is cookie + magic link.
- No subscription, no recurring billing, no "cancel" flow. One-time purchase only.
- No full-book PDF download. The product is the site + handouts + certificates.
- No landing-page marketing PDFs. The only public PDFs are the handouts buyers choose to share.
- No community / Discord / chat features. Zero operational overhead.
- No per-chapter micro-pricing. One price, everything unlocks.

### Hard editorial constraints

- Chapter 00 (the GUI→CLI bridge) is PAID. It is the most-valuable, most-omitted content and gets the same treatment as every other chapter.
- Lesson 00's EXERCISE in the repo is still free (task.md + test.py + workspace/), because the repo is always public. This is consistent with the rest of the curriculum.
- A separate, free "how to get started" mechanical page tells beginners how to open Codespaces and run `./cf`. This is not a lesson — it's a product tutorial.

---

## 2. The definitive free/paid surface

### Free forever (no auth, no paywall)

| Surface | URL(s) | What it contains |
|---|---|---|
| Landing page | `/pt/`, `/es/`, `/en/`, `/fr/` (+ root redirect) | Hero, stack explanation, how-it-works, curriculum ToC, buy CTA |
| Getting started | `/pt/como-comecar/`, `/es/como-empezar/`, `/en/getting-started/`, `/fr/comment-commencer/` | Mechanical: open Codespaces, clone, run `./cf list` |
| About / philosophy | `/pt/sobre/`, `/es/acerca/`, `/en/about/`, `/fr/a-propos/` | Short essay on project thesis |
| Privacy | `/pt/privacidade/`, `/es/privacidad/`, `/en/privacy/`, `/fr/confidentialite/` | Privacy contract (from telemetry-spec section 2) |
| Buy | `/comprar/` (PT+ES), `/buy/` (EN), `/acheter/` (FR) | Purchase page, single Stripe Payment Link CTA (region-routed: BR → R$47 BRL, else → $9 USD) |
| Verify pages | `/verify/<id>/` | Public credential verification pages (any visitor) |
| Backers wall | `/backers/` | Opt-in public roster of buyers who completed |
| Data pages | `/data/*` | Arxiv velocity index and other open artifacts |
| GitHub repo | `github.com/notifuturo/cyberfuturo` | All 9 lessons' `task.md` + `test.py` + `workspace/` + `./cf` runner |

### Paid (R$47 BRL in Brazil / $9 USD everywhere else, one-time, lifetime access)

| Surface | URL(s) | What it contains |
|---|---|---|
| Book chapters | `/pt/livro/00-*/` through `/pt/livro/08-*/` (and localized siblings) | All 9 teaching chapters, cookie-gated |
| Buyer progress page | `/verify/<id>/` for the specific buyer | All their handouts + certs in one place |
| Per-chapter handouts | Downloadable from the buyer's progress page | 9 PDFs per buyer, one per chapter, with their name |
| Module certificates | Same | 3 formal PDFs on module milestones |
| Final certificate | Same | 1 summative PDF on full completion |
| Edition updates | Automatic | v1.x patches free; v2.0 is a discounted upgrade |

---

## 3. Lesson file refactor

Current curriculum structure (in `curriculum/lessons/NN-slug/`):
- `lesson.md` (canonical PT, mixes teaching + task)
- `lesson.es.md` (ES translation, mixes teaching + task)
- `test.py` (grader)
- `workspace/` (starter files)

New structure — splits teaching from task:

```
curriculum/lessons/NN-slug/
  task.md                    ← FREE, public repo. Terse problem statement (medium-verbosity).
  task.es.md
  task.en.md
  task.fr.md
  test.py                    ← FREE, public repo. Grader, unchanged.
  workspace/                 ← FREE, public repo. Starter files, unchanged.

site/pt/livro/NN-slug/index.html  ← PAID. Full teaching chapter, cookie-gated.
site/es/libro/NN-slug/index.html  ← PAID.
site/en/book/NN-slug/index.html   ← PAID.
site/fr/livre/NN-slug/index.html  ← PAID.
```

### Task-statement template (`task.md`)

"Medium verbosity" — enough to know WHAT to do, not enough to learn WHY:

```markdown
# Lição 01 — Terminal

Abra o terminal dentro do Codespace. Crie um arquivo chamado
`ola.txt` na pasta atual.

Quando estiver pronto, rode:

    ./cf check

O validador aceita qualquer conteúdo, desde que o arquivo exista.

---

## O que este validador checa

- `ola.txt` existe na pasta `curriculum/`
- Não é um diretório

## Precisa da explicação completa?

Esta lição tem um capítulo dedicado que explica **o que é um terminal,
por que ele existe, o que `touch` está fazendo por baixo, e como se
transita da interface gráfica que você já conhece**.

Leia em: https://cyberfuturo.com/pt/livro/01-terminal/
```

### Chapter template (paid site content)

Full teaching chapter — all the explanation, context, analogies, the *why*. Opens with whatever context the chapter needs (only lesson 00 gets the GUI→CLI translation table — per the decision in conversation). Ends with a reference to the free exercise in the repo.

### The `./cf show` command

The runner's `cmd_show` currently prints lesson.md. After the refactor, it prints task.md. Add a closing line:

```python
print(color(f"  Para a explicação completa, abra:", CYAN))
print(color(f"    https://cyberfuturo.com/{lesson_lang()}/livro/{lesson.slug}/", PURPLE))
```

---

## 4. Data model (D1 extensions)

Add to `scripts/d1_schema.sql` (after the `events` + `forgotten_ids` tables from the telemetry spec):

```sql
-- Buyers. One row per purchase. Email is the unique identity.
CREATE TABLE IF NOT EXISTS buyers (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  email           TEXT    NOT NULL UNIQUE,
  name            TEXT    NOT NULL,
  access_token    TEXT    NOT NULL UNIQUE,           -- long random, cookie value
  activation_code TEXT    UNIQUE,                     -- 8-char, single-use, NULL after use
  anon_id         TEXT    UNIQUE,                     -- set after /api/activate succeeds
  paid_at         INTEGER NOT NULL,
  activated_at    INTEGER,
  edition         TEXT    NOT NULL DEFAULT '1.0',
  source          TEXT    NOT NULL DEFAULT 'stripe' CHECK (source IN ('stripe')),
  amount_cents    INTEGER,                             -- in currency's smallest unit (centavos, cents)
  currency        TEXT,                                 -- 'brl' or 'usd' (lowercase, Stripe convention)
  backers_opt_in  INTEGER NOT NULL DEFAULT 0,         -- 0 private, 1 public on /backers/
  lang_pref       TEXT    CHECK (lang_pref IN ('pt','es','en','fr')),
  external_id     TEXT                                 -- Stripe checkout session id (cs_live_...)
);

CREATE INDEX IF NOT EXISTS idx_buyers_token ON buyers(access_token);
CREATE INDEX IF NOT EXISTS idx_buyers_code  ON buyers(activation_code);
CREATE INDEX IF NOT EXISTS idx_buyers_anon  ON buyers(anon_id);

-- Artifacts. One row per handout / module cert / final cert earned.
CREATE TABLE IF NOT EXISTS artifacts (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  buyer_id      INTEGER NOT NULL REFERENCES buyers(id),
  artifact_type TEXT    NOT NULL CHECK (artifact_type IN ('handout','module_cert','final_cert')),
  slug          TEXT    NOT NULL,                       -- chapter slug for handout, module slug for module_cert, 'complete' for final_cert
  lang          TEXT    NOT NULL CHECK (lang IN ('pt','es','en','fr')),
  verify_id     TEXT    NOT NULL UNIQUE,                -- short human-readable, e.g. 'cf-2026-a7b3c1'
  pdf_r2_key    TEXT,                                    -- R2 object key, e.g. 'handouts/cf-2026-a7b3c1.pdf'
  created_at    INTEGER NOT NULL,
  UNIQUE(buyer_id, artifact_type, slug)
);

CREATE INDEX IF NOT EXISTS idx_artifacts_buyer  ON artifacts(buyer_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_verify ON artifacts(verify_id);

-- Webhook dedup — prevents double-processing a retried webhook.
CREATE TABLE IF NOT EXISTS webhook_log (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  source        TEXT NOT NULL,
  external_id   TEXT NOT NULL,
  received_at   INTEGER NOT NULL,
  UNIQUE(source, external_id)
);
```

### R2 bucket for PDFs

Create a Cloudflare R2 bucket `cyberfuturo-artifacts` (free tier: 10 GB storage, 1M Class-A ops/mo, 10M Class-B ops/mo). Bind to the Pages project as `CF_ARTIFACTS`.

PDFs live in R2, not in D1 (D1 isn't for blob storage). Verify pages and download links resolve through a Pages Function that streams from R2 after auth check.

---

## 5. Purchase webhook

One source: Stripe. Two Payment Links fronting the single webhook — region-routed at the buy-page level, indistinguishable downstream.

### 5.1. Stripe setup (do this in the Stripe dashboard first)

Create the product once:

- **Product name**: CyberFuturo — Livro Interativo
- **Product description**: "Livro interativo com 9 capítulos, 4 idiomas, handouts por capítulo e certificados automáticos. Acesso vitalício. Atualizações grátis."

Create two Prices on the same product:

| Price ID (env var name) | Currency | Amount | Purpose |
|---|---|---|---|
| `PRICE_BR` | `brl` | **R$47,00** (4700 centavos) | Brazilian Payment Link |
| `PRICE_GLOBAL` | `usd` | **$9.00** (900 cents) | Global Payment Link |

Create two Payment Links (one per Price):

| Payment Link | Payment methods to enable | Custom fields |
|---|---|---|
| **BR** (links to `PRICE_BR`) | `pix`, `boleto`, `card` (with installment support up to 12×) | `lang_pref` dropdown (pt/es — though BR defaults pt) |
| **Global** (links to `PRICE_GLOBAL`) | `card`, `apple_pay`, `google_pay`, `link` | `lang_pref` dropdown (pt/es/en/fr) |

Both Payment Links point to the same webhook: `https://cyberfuturo.com/api/purchase/stripe`.

In Stripe dashboard → Developers → Webhooks, create one endpoint:

- **URL**: `https://cyberfuturo.com/api/purchase/stripe`
- **Events to listen for**: `checkout.session.completed` (only)
- **Signing secret**: copy into Pages env var `STRIPE_WEBHOOK_SECRET`

### 5.2. Webhook Pages Function

**File: `site/functions/api/purchase/stripe.js`**

```javascript
// Cloudflare Pages Function — Stripe purchase webhook.
// Env vars (set via Pages dashboard → Settings → Environment variables):
//   STRIPE_SECRET_KEY     — sk_live_... from Stripe API Keys
//   STRIPE_WEBHOOK_SECRET — whsec_... from the webhook endpoint config

import Stripe from "stripe";

export async function onRequestPost({ request, env }) {
  // 1. Verify Stripe signature. Stripe sends 'stripe-signature' header.
  const signature = request.headers.get("stripe-signature");
  const rawBody = await request.text();
  if (!signature) return new Response("missing signature", { status: 400 });

  const stripe = new Stripe(env.STRIPE_SECRET_KEY, { apiVersion: "2024-06-20" });
  let event;
  try {
    event = await stripe.webhooks.constructEventAsync(
      rawBody,
      signature,
      env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    return new Response(`bad signature: ${err.message}`, { status: 400 });
  }

  // 2. Only process completed checkouts. Ignore everything else Stripe may send.
  if (event.type !== "checkout.session.completed") {
    return new Response(null, { status: 204 });
  }

  const session = event.data.object;

  // Only process paid sessions (not 'unpaid' or 'expired').
  if (session.payment_status !== "paid") return new Response(null, { status: 204 });

  const external_id  = session.id;                                         // cs_live_... unique per checkout
  const email        = (session.customer_details?.email || "").toLowerCase();
  const name         = session.customer_details?.name || "CyberFuturo student";
  const amount_cents = session.amount_total;                                // e.g. 4700 (BRL centavos) or 900 (USD cents)
  const currency     = (session.currency || "usd").toLowerCase();           // 'brl' | 'usd'

  // Parse custom field for reading-language preference. Stripe puts custom fields on session.custom_fields.
  const langField = (session.custom_fields || []).find(f => f.key === "lang_pref");
  const lang_pref = langField?.dropdown?.value || langField?.text?.value || "pt";

  if (!external_id || !email) return new Response("bad payload", { status: 400 });

  // 3. Dedup — webhook_log UNIQUE(source, external_id) prevents double-processing.
  const dupCheck = await env.CF_TELEMETRY
    .prepare("INSERT OR IGNORE INTO webhook_log (source, external_id, received_at) VALUES ('stripe', ?, ?)")
    .bind(external_id, Math.floor(Date.now() / 1000))
    .run();
  if (dupCheck.meta.changes === 0) return new Response(null, { status: 200 });

  // 4. Insert buyer.
  const access_token    = crypto.randomUUID().replace(/-/g, "");
  const activation_code = generateCode(8);
  const now = Math.floor(Date.now() / 1000);

  try {
    await env.CF_TELEMETRY
      .prepare(`INSERT INTO buyers
        (email, name, access_token, activation_code, paid_at, edition, source, amount_cents, currency, lang_pref, external_id)
        VALUES (?, ?, ?, ?, ?, '1.0', 'stripe', ?, ?, ?, ?)`)
      .bind(email, name, access_token, activation_code, now, amount_cents, currency, lang_pref, external_id)
      .run();
  } catch (e) {
    // Email already exists (unique constraint). Buyer has purchased before — could be upgrade path or duplicate.
    // For v1.0: treat as no-op (Stripe should have prevented this via same customer_email), but do send the
    // welcome email again with existing tokens in case they lost it.
    const existing = await env.CF_TELEMETRY
      .prepare("SELECT access_token, activation_code FROM buyers WHERE email = ?")
      .bind(email).first();
    if (existing) {
      await sendWelcomeEmail(env, { email, name,
        access_token: existing.access_token,
        activation_code: existing.activation_code || "(already used)",
        lang_pref });
      return new Response(null, { status: 200 });
    }
    return new Response("db error", { status: 500 });
  }

  // 5. Send welcome email (via Resend).
  await sendWelcomeEmail(env, { email, name, access_token, activation_code, lang_pref });

  return new Response(null, { status: 200 });
}

function generateCode(len) {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // ambiguous chars removed
  const bytes = new Uint8Array(len);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, b => alphabet[b % alphabet.length]).join("");
}
```

**Notes on Stripe SDK on Cloudflare Workers:**

- Use Stripe SDK v14+ which supports Workers/Pages runtime (uses `fetch` instead of Node http).
- Package: `stripe` from npm. Cloudflare Pages picks it up automatically via `package.json` at repo root.
- The `constructEventAsync` method is required in the Workers runtime (not `constructEvent`) because HMAC verification uses the async Web Crypto API.

### 5.3. Welcome email (helper)

```javascript
// site/functions/_lib/email.js — imported by the Stripe webhook function.

export async function sendWelcomeEmail(env, { email, name, access_token, activation_code, lang_pref }) {
  const msgs = {
    pt: {
      subject: "CyberFuturo — seu acesso está pronto",
      body: (fname) => `Olá ${fname},

Seu acesso ao CyberFuturo está pronto.

1. Leia o livro no site. Clique aqui para entrar:
   https://cyberfuturo.com/auth?t=${access_token}
   (Este link abre o livro e te deixa logado por 2 anos.)

2. Pratique no Codespaces. Abra:
   https://codespaces.new/notifuturo/cyberfuturo?quickstart=1

3. Conecte seu progresso ao seu certificado. No terminal do Codespace, rode:
   ./cf activate ${activation_code}

A cada capítulo que você concluir, um handout vai aparecer na sua página
pessoal em https://cyberfuturo.com/verify/... (você recebe o link quando ativar).

Bom aprendizado,
— CyberFuturo`,
    },
    // es, en, fr versions follow the same pattern
  };

  const msg = msgs[lang_pref] || msgs.pt;
  const fname = name.split(" ")[0] || name;

  await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: "CyberFuturo <ola@cyberfuturo.com>",
      to: email,
      subject: msg.subject,
      text: msg.body(fname),
    }),
  });
}
```

Resend free tier: 3,000 emails/month, 100/day — sufficient for the first year of volume.

---

## 6. Magic link + cookie flow

**File: `site/functions/auth.js`**

```javascript
// Cloudflare Pages Function — magic link endpoint.
// GET /auth?t=<access_token> → validate → set cookie → redirect to reader.

const COOKIE_NAME = "cf_access";
const COOKIE_MAX_AGE = 63072000; // 2 years

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const token = url.searchParams.get("t") || "";
  if (!/^[0-9a-f]{32}$/.test(token)) return new Response("invalid token", { status: 400 });

  const buyer = await env.CF_TELEMETRY
    .prepare("SELECT id, lang_pref FROM buyers WHERE access_token = ?")
    .bind(token).first();
  if (!buyer) return new Response("token not found", { status: 404 });

  const lang = buyer.lang_pref || "pt";
  const headers = new Headers({
    "Set-Cookie": `${COOKIE_NAME}=${token}; Path=/; Max-Age=${COOKIE_MAX_AGE}; Secure; HttpOnly; SameSite=Lax`,
    "Location": `/${lang}/livro/00-bienvenido/`,
  });
  return new Response(null, { status: 302, headers });
}
```

Cookie is `Secure`, `HttpOnly`, `SameSite=Lax`. 2-year lifetime (one-time purchase, persistent access). Not cross-site trackable.

---

## 7. Activation endpoint + `./cf activate`

### 7.1. Pages Function

**File: `site/functions/api/activate.js`**

```javascript
const CODE_RE    = /^[A-HJ-NP-Z2-9]{8}$/;
const UUID_RE    = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export async function onRequestPost({ request, env }) {
  const body = await request.json().catch(() => null);
  if (!body) return json({ ok: false, error: "invalid json" }, 400);

  const code    = (body.code || "").trim().toUpperCase();
  const anon_id = (body.anon_id || "").trim().toLowerCase();

  if (!CODE_RE.test(code))   return json({ ok: false, error: "bad code" }, 400);
  if (!UUID_RE.test(anon_id)) return json({ ok: false, error: "bad anon_id" }, 400);

  const buyer = await env.CF_TELEMETRY
    .prepare("SELECT id FROM buyers WHERE activation_code = ? AND anon_id IS NULL")
    .bind(code).first();

  if (!buyer) return json({ ok: false, error: "invalid or already-used code" }, 404);

  const anonTaken = await env.CF_TELEMETRY
    .prepare("SELECT 1 FROM buyers WHERE anon_id = ?")
    .bind(anon_id).first();
  if (anonTaken) return json({ ok: false, error: "anon_id already linked" }, 409);

  const now = Math.floor(Date.now() / 1000);
  await env.CF_TELEMETRY
    .prepare("UPDATE buyers SET anon_id = ?, activated_at = ?, activation_code = NULL WHERE id = ?")
    .bind(anon_id, now, buyer.id).run();

  // Return the verify URL the buyer will watch.
  const verifyUrl = `https://cyberfuturo.com/verify/buyer-${buyer.id}/`;
  return json({ ok: true, verify_url: verifyUrl });
}

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json" },
  });
}
```

### 7.2. Runner subcommand — add to `curriculum/runner/main.py`

```python
def cmd_activate(progress: dict, args: list[str]) -> int:
    if not args:
        print(color("  Uso: ./cf activate CODIGO", RED))
        return 1
    code = args[0].strip().upper()
    anon_id = progress.get("anon_id")
    if not anon_id:
        # If user hasn't opted into telemetry, we need an anon_id anyway for activation.
        import uuid as _uuid
        anon_id = str(_uuid.uuid4())
        progress["anon_id"] = anon_id
        progress["telemetry_opt_in"] = True  # activation implies consent to completion pings
        save_progress(progress)

    payload = json.dumps({"code": code, "anon_id": anon_id}).encode("utf-8")
    req = urllib.request.Request(
        "https://cyberfuturo.com/api/activate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode("utf-8")).get("error", "activation failed")
        print(color(f"  ✘ {err}", RED))
        return 1
    except Exception:
        print(color("  ✘ Não consegui falar com o servidor. Tente de novo.", RED))
        return 1

    if not data.get("ok"):
        print(color(f"  ✘ {data.get('error', 'activation failed')}", RED))
        return 1

    progress["activated"] = True
    progress["verify_url"] = data.get("verify_url")
    save_progress(progress)

    print(color("  ✔ Conta vinculada.", GREEN + BOLD))
    print(f"  {DIM}Sua página pessoal: {data.get('verify_url')}{RESET}")
    print(f"  {DIM}Cada capítulo que você concluir vai gerar um handout lá.{RESET}")
    return 0
```

Route in `main()`:
```python
    if command == "activate":
        return cmd_activate(progress, args)
```

Add to `__doc__`:
```
  ./cf activate CODIGO  Vincula o seu workspace à sua compra (unlocks certs)
```

---

## 8. Cookie-gated reading routes

**File: `site/functions/_middleware.js`**

```javascript
// Gates all /pt/livro/*, /es/libro/*, /en/book/*, /fr/livre/* URLs behind a valid cf_access cookie.
// Public pages are unaffected.

const GATED_PREFIXES = ["/pt/livro/", "/es/libro/", "/en/book/", "/fr/livre/"];

export async function onRequest(context) {
  const { request, next, env } = context;
  const url = new URL(request.url);
  const path = url.pathname;

  const gated = GATED_PREFIXES.some(p => path.startsWith(p));
  if (!gated) return next();

  const cookie = request.headers.get("Cookie") || "";
  const match = cookie.match(/(?:^|;\s*)cf_access=([0-9a-f]{32})(?:;|$)/);
  if (!match) return redirectToBuy(path);

  const token = match[1];
  const buyer = await env.CF_TELEMETRY
    .prepare("SELECT 1 FROM buyers WHERE access_token = ?")
    .bind(token).first();
  if (!buyer) return redirectToBuy(path);

  return next();
}

function redirectToBuy(fromPath) {
  const lang = fromPath.split("/")[1] || "pt";
  const buyPath = { pt: "/comprar/", es: "/comprar/", en: "/buy/", fr: "/acheter/" }[lang] || "/comprar/";
  return Response.redirect(`https://cyberfuturo.com${buyPath}?from=${encodeURIComponent(fromPath)}`, 302);
}
```

Middleware runs before any Pages Function or static-file serve, so the check happens at the edge with one D1 query. Cache-negative for non-buyers (cheap redirect), cache-positive for buyers (static chapter file served).

---

## 9. Handout generation

Triggered from the telemetry `/api/ping` function on `event:"pass"` events. Extends `site/functions/api/ping.js` (from telemetry spec).

### 9.1. Extension to the ping function

Add, after the existing `INSERT OR IGNORE INTO events`:

```javascript
// Post-insert: if this is a pass event AND the anon_id is a linked buyer, trigger artifact generation.
if (event === "pass") {
  const buyer = await env.CF_TELEMETRY
    .prepare("SELECT id, name, backers_opt_in FROM buyers WHERE anon_id = ?")
    .bind(anon_id).first();
  if (buyer) {
    // Fire-and-forget; do not block the ping response.
    context.waitUntil(generateArtifactsOnPass(env, buyer, lesson, lang));
  }
}
```

### 9.2. Artifact generator

**File: `site/functions/_lib/artifacts.js`**

```javascript
const MODULES = {
  foundations:  { lessons: ["00-bienvenido", "01-terminal", "02-primer-git-commit"],      title: { pt: "Fundamentos",       es: "Fundamentos",        en: "Foundations",       fr: "Fondements" } },
  code_data:    { lessons: ["03-python-hola", "04-ramos-git", "05-primera-sql"],           title: { pt: "Código & Dados",   es: "Código y Datos",     en: "Code & Data",       fr: "Code & Données" } },
  web_patterns: { lessons: ["06-http-apis", "07-loops-dados", "08-dicionarios"],           title: { pt: "Web & Padrões",    es: "Web y Patrones",     en: "Web & Patterns",    fr: "Web & Modèles" } },
};
const ALL_LESSONS = Object.values(MODULES).flatMap(m => m.lessons);

export async function generateArtifactsOnPass(env, buyer, lesson, lang) {
  // 1. Handout for this specific lesson.
  await ensureArtifact(env, buyer, "handout", lesson, lang);

  // 2. Check module cert eligibility.
  for (const [modSlug, mod] of Object.entries(MODULES)) {
    if (!mod.lessons.includes(lesson)) continue;
    const passed = await env.CF_TELEMETRY
      .prepare(`SELECT COUNT(*) AS n FROM events WHERE anon_id = ? AND event = 'pass' AND lesson IN (${mod.lessons.map(() => "?").join(",")})`)
      .bind(buyer.anon_id, ...mod.lessons).first();
    if (passed.n === mod.lessons.length) {
      await ensureArtifact(env, buyer, "module_cert", modSlug, lang);
    }
  }

  // 3. Check final cert eligibility.
  const passedAll = await env.CF_TELEMETRY
    .prepare(`SELECT COUNT(*) AS n FROM events WHERE anon_id = ? AND event = 'pass' AND lesson IN (${ALL_LESSONS.map(() => "?").join(",")})`)
    .bind(buyer.anon_id, ...ALL_LESSONS).first();
  if (passedAll.n === ALL_LESSONS.length) {
    await ensureArtifact(env, buyer, "final_cert", "complete", lang);
  }
}

async function ensureArtifact(env, buyer, type, slug, lang) {
  const existing = await env.CF_TELEMETRY
    .prepare("SELECT 1 FROM artifacts WHERE buyer_id = ? AND artifact_type = ? AND slug = ?")
    .bind(buyer.id, type, slug).first();
  if (existing) return;

  const verify_id = `cf-${new Date().getFullYear()}-${randHex(6)}`;
  const pdfBytes  = await renderArtifactPdf(env, { type, slug, lang, buyerName: buyer.name });
  const r2Key     = `${type}/${verify_id}.pdf`;
  await env.CF_ARTIFACTS.put(r2Key, pdfBytes, {
    httpMetadata: { contentType: "application/pdf" },
  });

  const now = Math.floor(Date.now() / 1000);
  await env.CF_TELEMETRY
    .prepare(`INSERT INTO artifacts (buyer_id, artifact_type, slug, lang, verify_id, pdf_r2_key, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)`)
    .bind(buyer.id, type, slug, lang, verify_id, r2Key, now).run();

  // Emails: only for module + final certs (too noisy for per-handout emails).
  if (type !== "handout") {
    await sendCertEmail(env, buyer, type, slug, lang, verify_id);
  }
}

function randHex(n) {
  const bytes = new Uint8Array(n);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, b => b.toString(16).padStart(2, "0")).join("").slice(0, n);
}
```

### 9.3. PDF rendering

Handouts and certs are generated from SVG templates using Cloudflare's Browser Rendering (free tier: 10K/mo) or alternately via a simple HTML-to-PDF library.

**Template files (9 handout templates × 4 languages + 3 module templates × 4 languages + 1 final template × 4 languages = 52 SVG templates)** live in:

```
site/_templates/handouts/<slug>/<lang>.svg   e.g. 01-terminal/pt.svg, 01-terminal/en.svg, ...
site/_templates/modules/<slug>/<lang>.svg
site/_templates/final/<lang>.svg
```

Each SVG has placeholder strings like `{{BUYER_NAME}}` and `{{DATE}}` that get substituted before rendering.

```javascript
async function renderArtifactPdf(env, { type, slug, lang, buyerName }) {
  const tmplKey = `_templates/${type === "handout" ? "handouts" : type === "module_cert" ? "modules" : "final"}/${slug}/${lang}.svg`;
  // Load the SVG template. In production, fetched from a static asset or R2.
  const svg = await loadTemplate(tmplKey);
  const filled = svg
    .replace(/\{\{BUYER_NAME\}\}/g, escapeXml(buyerName))
    .replace(/\{\{DATE\}\}/g, new Date().toISOString().slice(0, 10));

  // Use Cloudflare Browser Rendering or html-to-pdf binding.
  const browser = await env.CF_BROWSER.launch();
  const page = await browser.newPage();
  await page.setContent(`<!doctype html><html><body>${filled}</body></html>`);
  const pdf = await page.pdf({ format: "A5" });
  await browser.close();
  return pdf;
}
```

For v1.0, if Browser Rendering feels heavy: SVG-only handouts work too. Buyers can download `.svg` files, or a GitHub Action nightly-converts SVG → PDF via `librsvg` and re-uploads to R2.

---

## 10. Handout template — concrete example

**File: `site/_templates/handouts/04-ramos-git/pt.svg`**

(A5 size, portrait, designed to be readable and shareable.)

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 595" width="420" height="595">
  <style>
    .bg { fill: #1e1e2e; }
    .title { fill: #e879f9; font-family: "JetBrains Mono", monospace; font-size: 22px; font-weight: 700; }
    .h { fill: #a5b4fc; font-family: "JetBrains Mono", monospace; font-size: 13px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; }
    .cmd { fill: #84cc16; font-family: "JetBrains Mono", monospace; font-size: 11px; }
    .gloss { fill: #cbd5e1; font-family: "JetBrains Mono", monospace; font-size: 10px; }
    .foot { fill: #94a3b8; font-family: "JetBrains Mono", monospace; font-size: 9px; }
    .brand { fill: #e879f9; font-family: "JetBrains Mono", monospace; font-size: 10px; font-weight: 700; }
  </style>
  <rect class="bg" width="420" height="595"/>
  <text x="20" y="40" class="brand">&gt;_ CyberFuturo — Capítulo 04</text>
  <text x="20" y="70" class="title">Ramos em Git</text>

  <text x="20" y="110" class="h">os comandos</text>
  <text x="20" y="130" class="cmd">git branch &lt;nome&gt;</text>
  <text x="170" y="130" class="gloss">cria um ramo</text>
  <text x="20" y="146" class="cmd">git checkout &lt;nome&gt;</text>
  <text x="170" y="146" class="gloss">muda para um ramo</text>
  <text x="20" y="162" class="cmd">git checkout -b &lt;nome&gt;</text>
  <text x="170" y="162" class="gloss">cria e muda</text>
  <text x="20" y="178" class="cmd">git branch</text>
  <text x="170" y="178" class="gloss">lista ramos locais</text>
  <text x="20" y="194" class="cmd">git branch -d &lt;nome&gt;</text>
  <text x="170" y="194" class="gloss">apaga ramo</text>
  <text x="20" y="210" class="cmd">git merge &lt;nome&gt;</text>
  <text x="170" y="210" class="gloss">funde no atual</text>

  <text x="20" y="250" class="h">fluxo típico</text>
  <text x="20" y="270" class="gloss">1. git checkout -b minha-feature</text>
  <text x="20" y="286" class="gloss">2. (faça suas mudanças e commite)</text>
  <text x="20" y="302" class="gloss">3. git checkout main</text>
  <text x="20" y="318" class="gloss">4. git merge minha-feature</text>
  <text x="20" y="334" class="gloss">5. git branch -d minha-feature</text>

  <text x="20" y="374" class="h">quando usar</text>
  <text x="20" y="394" class="gloss">• experimentar sem quebrar o main</text>
  <text x="20" y="410" class="gloss">• trabalhar em várias features ao mesmo tempo</text>
  <text x="20" y="426" class="gloss">• colaborar sem conflitos</text>

  <text x="20" y="466" class="h">armadilhas</text>
  <text x="20" y="486" class="gloss">✗ esquecer de voltar ao main antes do merge</text>
  <text x="20" y="502" class="gloss">✗ deletar ramo com mudanças não fundidas</text>
  <text x="20" y="518" class="gloss">✗ misturar várias features num ramo só</text>

  <line x1="20" y1="548" x2="400" y2="548" stroke="#3b3b4f" stroke-width="1"/>
  <text x="20" y="562" class="foot">Concluído por {{BUYER_NAME}} · {{DATE}}</text>
  <text x="20" y="576" class="foot">Capítulo completo: cyberfuturo.com/pt/livro/04-ramos-git/  ·  R$47 BR / $9 global · acesso vitalício · 4 idiomas</text>
</svg>
```

The other 35 handout templates follow the same skeleton, with content per chapter × language. Module and final cert templates are larger (A4), more formal.

---

## 11. Verify pages and backers wall

**File: `scripts/rebuild_verify_pages.py`**

GitHub Action reads D1 nightly and regenerates static pages:

- `site/verify/<verify_id>/index.html` — one per artifact, shows: type, title, buyer name (if opt-in or artifact requires it), completion date, download link to R2
- `site/verify/buyer-<buyer_id>/index.html` — one per buyer, shows all their artifacts + progress + signed link to PDFs
- `site/backers/index.html` — roster of buyers with `backers_opt_in=1`, showing name + country hint + final_cert completion date (if present)

**New workflow: `.github/workflows/rebuild-verify.yml`**

```yaml
name: Rebuild verify and backers pages

on:
  schedule:
    - cron: '0 */6 * * *'   # every 6 hours
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  rebuild:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: d1 execute cf_telemetry --command "SELECT * FROM artifacts" --json > data/artifacts.json
      - run: python3 scripts/rebuild_verify_pages.py
      - run: |
          git config user.name "cyberfuturo-bot"
          git config user.email "bot@cyberfuturo.com"
          git add site/verify/ site/backers/
          if ! git diff --cached --quiet; then
            git commit -m "verify: rebuild verify pages $(date -u +%FT%TZ)"
            git push
          fi
```

Script writes static HTML per verify page. Public pages (everyone can visit), but PDFs live in R2 behind a thin Pages Function that checks the verify_id → R2 key mapping and streams the file.

---

## 12. Buy page

**Files**: `site/pt/comprar/index.html`, `site/es/comprar/index.html`, `site/en/buy/index.html`, `site/fr/acheter/index.html` — but each is rendered by a Pages Function at the corresponding path (to do country-based price routing at the edge).

### 12.1. Region routing — Pages Function

**File: `site/functions/pt/comprar/index.js`** (duplicate the same pattern for `/es/comprar/`, `/en/buy/`, `/fr/acheter/`):

```javascript
// Route the buy button to the right Stripe Payment Link based on CF-IPCountry.
// Everything else on the page is static and identical.

const PAYMENT_LINKS = {
  br: "https://buy.stripe.com/REPLACE_WITH_BR_LINK",       // R$47 BRL, Pix + boleto + card
  global: "https://buy.stripe.com/REPLACE_WITH_GLOBAL_LINK" // $9 USD, card + Apple/Google Pay + Link
};

export async function onRequestGet({ request, env, next }) {
  const country = request.headers.get("CF-IPCountry") || "";
  const isBR = country === "BR";
  const link = isBR ? PAYMENT_LINKS.br : PAYMENT_LINKS.global;
  const priceLabel = isBR ? "R$47" : "$9 USD";
  const methods = isBR ? "Pix, boleto ou cartão" : "card · Apple Pay · Google Pay";

  // Fetch the static template (a sibling index.html.template) and do simple string substitution.
  const template = await env.ASSETS.fetch(new URL("/pt/comprar/_template.html", request.url)).then(r => r.text());
  const rendered = template
    .replace(/\{\{PAYMENT_LINK\}\}/g, link)
    .replace(/\{\{PRICE_LABEL\}\}/g, priceLabel)
    .replace(/\{\{METHODS\}\}/g, methods);

  return new Response(rendered, {
    headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=60" },
  });
}
```

### 12.2. Static template content

The buy page (PT localized shown; replicate for ES/EN/FR) contains:

- Hero: "Desbloqueie os 9 capítulos do CyberFuturo"
- Price block rendered from `{{PRICE_LABEL}}` + `{{METHODS}}` (auto-localizes on country)
- What you get (single column list): all 9 chapters × 4 languages, 9 handouts, 3 module certs, 1 final cert, free edition updates
- Single buy CTA button pointing at `{{PAYMENT_LINK}}`
- FAQ section including:
  - *"Posso compartilhar o livro com um amigo?"* — *"Você pode compartilhar os handouts de cada capítulo que você concluir. Eles são resumos, não substituem os capítulos completos. Só você pode ganhar os certificados ligados à sua compra."*
  - *"Por que tem preço diferente por país?"* — *"R$47 é o preço de ancoragem do mercado brasileiro. $9 USD é o equivalente exato em dólares. A gente cobra na moeda local onde consegue (Brasil tem Pix direto via Stripe) e em dólar no resto do mundo."*
  - *"Posso pagar parcelado?"* — *"No Brasil, sim: Pix à vista ou cartão em até 12×. No resto do mundo, cartão à vista via Stripe."*
- Link back to landing
- Footer: privacy, about, contact

---

## 13. Orientation page

**File: `site/pt/como-comecar/index.html`** (and localized siblings)

Static mechanical page:
- How to open Codespaces (screenshot + one-click link)
- How to clone the repo locally (optional)
- How `./cf list` / `./cf start` / `./cf check` work
- "When you buy, come back here" — link to buy page

No teaching content. Pure product mechanics.

---

## 14. Landing page updates

Existing `site/pt/index.html` (and siblings) gain:
- A "what you get for R$47 / $9" card below the hero CTA (price localizes per country via the same routing Pages Function pattern as the buy page, so BR visitors see R$47, everyone else sees $9 USD)
- A buy button alongside the existing "Open in Codespaces"
- The curriculum section now has "Chapter 00-08 — all paid" attribution
- Footer adds links to `/comprar/` (or localized equivalent), `/verify/`, `/backers/`, `/privacidade/`, `/como-comecar/`

---

## 15. Operator runbook

```bash
# 0. Prereqs: url-restructure-spec.md + telemetry-spec.md already applied and live.

# 1. Extend the D1 schema
wrangler d1 execute cf_telemetry --file scripts/d1_schema.sql

# 2. Create the R2 bucket for artifacts
wrangler r2 bucket create cyberfuturo-artifacts

# 3. Bind R2 + Browser Rendering to the Pages project
#    Dashboard → Pages → cyberfuturo → Settings → Functions → bindings:
#      R2:       CF_ARTIFACTS → cyberfuturo-artifacts
#      Browser:  CF_BROWSER   → (enable Browser Rendering)

# 4. Set Pages env vars (dashboard → Environment variables, Production):
#      STRIPE_SECRET_KEY     → sk_live_... from Stripe → Developers → API keys
#      STRIPE_WEBHOOK_SECRET → whsec_...  from Stripe → Developers → Webhooks → endpoint signing secret
#      RESEND_API_KEY        → re_... from resend.com (for welcome + cert emails)

# 5. Refactor the curriculum:
#    For each lessons/NN-slug/:
#      - Split lesson.md into task.md + a new chapter file at site/pt/livro/NN-slug/index.html
#      - Same for lesson.es.md → task.es.md + site/es/libro/...
#      - Add site/en/book/ and site/fr/livre/ chapter files (already translated or pending translation)

# 6. Create all Pages Functions (sections 5, 6, 7, 8, _middleware)

# 7. Author SVG templates under site/_templates/ (52 total)

# 8. Add the cf activate subcommand to curriculum/runner/main.py

# 9. Create site/pt/comprar/, site/pt/como-comecar/, etc.

# 10. Update landing pages (section 14)

# 11. Create .github/workflows/rebuild-verify.yml

# 12. Configure Stripe:
#     a. Create Product + two Prices (BRL R$47 + USD $9) per section 5.1
#     b. Create two Payment Links (BR + Global) per section 5.1
#     c. Create one webhook endpoint at https://cyberfuturo.com/api/purchase/stripe
#        listening to checkout.session.completed only. Copy signing secret to STRIPE_WEBHOOK_SECRET env var.
#     d. Paste the two Payment Link URLs into site/functions/{pt/comprar,es/comprar,en/buy,fr/acheter}/index.js

# 13. Commit + push
git add -A
git commit -m "product: paid reading + handouts + 3-tier credentials via Stripe"
git push

# 14. Verify deploy
gh run watch

# 15. End-to-end test (use Stripe test mode: test cards 4242 4242 4242 4242 for USD, 4000 0007 6000 0000 4 for BRL):
#     - Go through Stripe Checkout on the global Payment Link → complete
#     - Receive welcome email (check Resend dashboard if not in inbox)
#     - Click magic link → cookie set, redirected to /pt/livro/00-bienvenido/
#     - Chapter renders (not redirected to buy page)
#     - Open Codespaces → ./cf activate CODE → success
#     - ./cf start 00 → ./cf check → pass
#     - Within ~30s: handout appears at https://cyberfuturo.com/verify/buyer-<id>/
#     - Repeat from BR IP (or VPN) → should land on R$47 BRL Payment Link with Pix option visible
```

---

## 16. Verification

| Check | How | Expected |
|---|---|---|
| Paid chapter is cookie-gated | `curl -sS -I https://cyberfuturo.com/pt/livro/00-bienvenido/` (no cookie) | 302 redirect to /comprar/ |
| Paid chapter works with cookie | Same with `-H 'Cookie: cf_access=<valid_token>'` | 200 with chapter HTML |
| Free task is public in repo | `curl -sS https://raw.githubusercontent.com/notifuturo/cyberfuturo/main/curriculum/lessons/01-terminal/task.md` | Full task.md text, publicly readable |
| Stripe webhook dedupes | Send same payload twice (via Stripe dashboard "Send test webhook") | First succeeds (row created + email sent), second 200 no-op (no duplicate row) |
| BR Payment Link shows Pix | Visit /comprar/ from a BR IP | Page shows R$47, CTA goes to BR Payment Link; Stripe checkout shows Pix + boleto + card |
| Global Payment Link shows USD | Visit /buy/ from a US IP | Page shows $9 USD, CTA goes to Global Payment Link |
| Stripe signature verification | POST `/api/purchase/stripe` with garbage signature | 400 "bad signature" |
| Activation code single-use | Same code twice | First succeeds, second returns "invalid or already-used" |
| Handout appears after pass | Pass a lesson, wait ~60s | verify/buyer-<id>/ shows new handout |
| Module cert fires after 3 passes | Pass lessons 00+01+02 | verify page shows module_cert for 'foundations' |
| Final cert fires after all 9 | Pass all lessons | verify page shows final_cert |

---

## 17. Rollback

- **Revert the Pages Function changes** (pre-middleware behavior returns): redeploy prior commit. Chapters become 404-on-middleware-miss unless static files exist at those paths. Safest partial rollback: **deactivate the Stripe Payment Links** (dashboard → Payment Links → Deactivate) so no new buyers are created; existing buyers keep full access.
- **Full rollback**: `git revert <commit>` + push. Deploy reverts site + Functions. D1 buyers table retains existing rows; R2 artifacts retain files. Neither is deleted.
- **Hard wipe**: `wrangler d1 execute cf_telemetry --command "DELETE FROM buyers; DELETE FROM artifacts; DELETE FROM webhook_log"` + `wrangler r2 object delete --bucket cyberfuturo-artifacts --all`. Only if testing or migrating.

---

## 18. Open questions (for founder review)

1. **Stripe account type** — the spec assumes your Stripe account can accept BRL + Pix. If your account is registered outside Brazil, verify Pix availability in Stripe dashboard → Settings → Payment methods. If Pix isn't available yet, ship the BR Payment Link card-only and add Pix the moment Stripe enables it — no code changes needed, just toggle in the Payment Link settings.
2. **Stripe Tax** — enabling Stripe Tax (dashboard → Tax) auto-calculates VAT/IVA/GST for EU, UK, AU etc. Not mandatory for v1.0 at this scale but worth turning on once volume is non-trivial. Brazilian tax (NFe) is NOT handled by Stripe — see question 7.
3. **Pre-v1.0 translations** — chapter content for EN and FR may not exist in full yet. Spec assumes they do. If not, the buy page + cookie check should continue to serve only the languages that have chapter content; the switcher on gated pages hides languages for which content is missing.
4. **Browser Rendering vs SVG-only for handouts** — SVG alone is 1-click shareable on web and social; PDF is better for printing. Recommend: ship as PDF from v1.0 to match "book" framing. Budget 10K/mo Browser Rendering calls is ample.
5. **Email from address** — `ola@cyberfuturo.com` needs SPF + DKIM + DMARC records on the domain. Verify with Resend. Fallback: send via Gmail SMTP to `lujoeduca@gmail.com` signing as that address while DNS is pending.
6. **Founders' pricing promo** — launch at R$27 (BR) / $5 USD (global) for the first 100 buyers, then raise to R$47 / $9. Stripe Payment Links support time-limited pricing — create a discounted Price, expose a second pair of Payment Links for the promo window, swap back after. Two-line change in the country-routing function.
7. **Brazilian NFe (nota fiscal)** — Stripe processes the payment but does NOT issue NFe in Brazil. For v1.0 at small volume: manual NFe via the municipal prefecture site after each BR sale, or skip until volume justifies a service like NFe.io (~R$30-50/mo). The `buyers.external_id` column has the Stripe session ID for reference.
8. **Backers wall default** — spec defaults `backers_opt_in=0`. Consider adding a Stripe checkout custom field "Mostrar meu nome na lista pública de backers?" (yes/no) so buyers choose at purchase. One extra field in the Stripe Payment Link config.
9. **Edition upgrade path** — spec declares v1.0 as the edition but defers upgrade logic. When v2.0 ships: v1.0 buyers get a magic-link email with a Stripe promotion code (dashboard → Promotion codes) that discounts the v2.0 Payment Link by, say, 60%. Out of scope for this spec.

---

*Spec v1.0 — 2026-04-18. Apply after review.*

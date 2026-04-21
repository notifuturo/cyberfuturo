// Cloudflare Pages — Advanced Mode Worker.
//
// Route table (first match wins, otherwise static-asset fallthrough):
//   1. POST   /api/purchase/stripe     → Stripe webhook (manual HMAC via Web Crypto)
//   2. POST   /api/activate            → link activation_code → anon_id
//   3. POST|OPTIONS|DELETE /api/ping   → telemetry ingest (telemetry-spec.md §3-§5)
//   4. GET    /auth                    → magic link: set cf_access cookie + 302
//   5. *      /{lang}/{livro|libro|book|livre}/*
//                                      → cookie-gated (docs/product-spec.md §8)
//   6. GET|HEAD /                      → smart language redirect
//                                      (cookie → Accept-Language → CF-IPCountry → en)
//   7. anything else                   → env.ASSETS.fetch
//
// D1 binding: CF_TELEMETRY (single database, holds telemetry + product tables).
// Env vars:  STRIPE_WEBHOOK_SECRET, STRIPE_SECRET_KEY (reserved, not needed for HMAC),
//            RESEND_API_KEY (optional — skipped gracefully if absent).
//
// Why _worker.js instead of functions/: Pages Functions couldn't cleanly
// override the bare root (static-asset handler wins at '/'). Advanced mode
// lets the worker take every request and delegate to ASSETS only when we want.
// One file, one routing table, one place to reason about edge behavior.

// ---- Language config ------------------------------------------------------

const LANGS = ["pt", "es", "en", "fr"];
const LANG_SET = new Set(LANGS);

// Country-hint → language. Conservative mapping; when in doubt, we fall through
// to Accept-Language. Only listed countries get a country-based default.
const COUNTRY_LANG = {
  // Portuguese
  BR: "pt", PT: "pt", AO: "pt", MZ: "pt", CV: "pt", GW: "pt", ST: "pt", TL: "pt",
  // Spanish
  ES: "es", MX: "es", AR: "es", CO: "es", CL: "es", PE: "es", VE: "es",
  UY: "es", PY: "es", BO: "es", EC: "es", GT: "es", HN: "es", NI: "es",
  CR: "es", PA: "es", DO: "es", CU: "es", SV: "es", PR: "es",
  // French
  FR: "fr", BE: "fr", CH: "fr", LU: "fr", MC: "fr", CA: "fr",
  SN: "fr", CI: "fr", CM: "fr", MG: "fr", HT: "fr", TN: "fr",
  DZ: "fr", MA: "fr", BF: "fr", ML: "fr", NE: "fr", BJ: "fr",
  // English default for everywhere else (US, UK, AU, NZ, IE, IN, ZA, ...)
};

function parseAcceptLanguage(header) {
  if (!header) return [];
  return header
    .split(",")
    .map(s => s.trim())
    .map(s => {
      const [tag, qPart] = s.split(";");
      const q = qPart ? parseFloat(qPart.replace(/^q=/, "")) : 1.0;
      return { lang: tag.toLowerCase().slice(0, 2), q: Number.isFinite(q) ? q : 1.0 };
    })
    .filter(x => x.lang.length === 2)
    .sort((a, b) => b.q - a.q)
    .map(x => x.lang);
}

function pickLang(request) {
  const cookie = request.headers.get("Cookie") || "";
  const match = cookie.match(/(?:^|;\s*)cf_lang=(pt|es|en|fr)(?:;|$)/);
  if (match) return match[1];

  const accept = parseAcceptLanguage(request.headers.get("Accept-Language"));
  for (const prefix of accept) {
    if (LANG_SET.has(prefix)) return prefix;
  }

  const country = request.headers.get("CF-IPCountry");
  if (country && COUNTRY_LANG[country]) return COUNTRY_LANG[country];

  return "en";
}

// ---- Shared helpers -------------------------------------------------------

const CORS_HEADERS = {
  "Access-Control-Allow-Origin":  "*",
  "Access-Control-Allow-Methods": "POST, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "content-type",
  "Access-Control-Max-Age":       "86400",
};

function jsonResponse(obj, status, extraHeaders = {}) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", ...extraHeaders },
  });
}

function corsJson(obj, status) {
  return jsonResponse(obj, status, CORS_HEADERS);
}

async function hmacSha256Hex(secret, message) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false, ["sign"]
  );
  const sigBuf = await crypto.subtle.sign("HMAC", key, enc.encode(message));
  return Array.from(new Uint8Array(sigBuf), b => b.toString(16).padStart(2, "0")).join("");
}

function timingSafeEqualHex(a, b) {
  // Constant-time compare; both must be hex of identical length.
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

// ---- /api/ping — telemetry ingest -----------------------------------------
//
// Contract: docs/telemetry-spec.md §3-§5. Strict validation, idempotent insert
// via UNIQUE(anon_id, event, lesson), tombstone table for forget requests.
// Reads only the request body and CF-IPCountry — no IP, UA, referrer, or cookies.

const LESSON_RE = /^[0-9]{2}-[a-z0-9-]+$/;
const EVENTS    = new Set(["start", "pass"]);
const UUID_RE   = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const MAX_PING_BODY = 1024;

async function handlePingPost(request, env) {
  if (!env.CF_TELEMETRY) return corsJson({ error: "telemetry unavailable" }, 503);

  const raw = await request.text();
  if (raw.length > MAX_PING_BODY) return corsJson({ error: "payload too large" }, 413);

  let body;
  try { body = JSON.parse(raw); }
  catch { return corsJson({ error: "invalid json" }, 400); }

  const { event, lesson, lang, anon_id } = body || {};
  if (!EVENTS.has(event))      return corsJson({ error: "bad event" }, 400);
  if (!LESSON_RE.test(lesson)) return corsJson({ error: "bad lesson" }, 400);
  if (!LANG_SET.has(lang))     return corsJson({ error: "bad lang" }, 400);
  if (!UUID_RE.test(anon_id))  return corsJson({ error: "bad anon_id" }, 400);

  const country = request.headers.get("CF-IPCountry") || null;

  const tomb = await env.CF_TELEMETRY
    .prepare("SELECT 1 FROM forgotten_ids WHERE anon_id = ?")
    .bind(anon_id)
    .first();
  if (tomb) return new Response(null, { status: 204, headers: CORS_HEADERS });

  await env.CF_TELEMETRY
    .prepare("INSERT OR IGNORE INTO events (anon_id, event, lesson, lang, country, created_at) VALUES (?, ?, ?, ?, ?, ?)")
    .bind(anon_id, event, lesson, lang, country, Math.floor(Date.now() / 1000))
    .run();

  return new Response(null, { status: 204, headers: CORS_HEADERS });
}

async function handlePingDelete(request, env) {
  if (!env.CF_TELEMETRY) return corsJson({ error: "telemetry unavailable" }, 503);

  const raw = await request.text();
  if (raw.length > MAX_PING_BODY) return corsJson({ error: "payload too large" }, 413);

  let body;
  try { body = JSON.parse(raw); }
  catch { return corsJson({ error: "invalid json" }, 400); }

  const { anon_id } = body || {};
  if (!UUID_RE.test(anon_id)) return corsJson({ error: "bad anon_id" }, 400);

  const now = Math.floor(Date.now() / 1000);
  await env.CF_TELEMETRY.batch([
    env.CF_TELEMETRY.prepare("INSERT OR IGNORE INTO forgotten_ids (anon_id, created_at) VALUES (?, ?)").bind(anon_id, now),
    env.CF_TELEMETRY.prepare("DELETE FROM events WHERE anon_id = ?").bind(anon_id),
  ]);
  return new Response(null, { status: 204, headers: CORS_HEADERS });
}

async function handlePing(request, env) {
  switch (request.method) {
    case "OPTIONS": return new Response(null, { status: 204, headers: CORS_HEADERS });
    case "POST":    return handlePingPost(request, env);
    case "DELETE":  return handlePingDelete(request, env);
    default:
      return new Response("Method Not Allowed", {
        status: 405,
        headers: { Allow: "POST, DELETE, OPTIONS", ...CORS_HEADERS },
      });
  }
}

// ---- /auth — magic link ---------------------------------------------------
//
// GET /auth?t=<access_token> → validate → set cf_access cookie → 302 to reader.
// Cookie is Secure, HttpOnly, SameSite=Lax, 2-year lifetime.

const ACCESS_COOKIE       = "cf_access";
const ACCESS_COOKIE_MAXAGE = 63072000; // 2 years in seconds
const ACCESS_TOKEN_RE      = /^[0-9a-f]{32}$/;

async function handleAuth(request, env) {
  if (request.method !== "GET") {
    return new Response("Method Not Allowed", { status: 405, headers: { Allow: "GET" } });
  }
  if (!env.CF_TELEMETRY) return new Response("auth unavailable", { status: 503 });

  const url = new URL(request.url);
  const token = url.searchParams.get("t") || "";
  if (!ACCESS_TOKEN_RE.test(token)) return new Response("invalid token", { status: 400 });

  const buyer = await env.CF_TELEMETRY
    .prepare("SELECT id, lang_pref FROM buyers WHERE access_token = ?")
    .bind(token).first();
  if (!buyer) return new Response("token not found", { status: 404 });

  const lang = buyer.lang_pref || "pt";
  const bookSlug = { pt: "livro", es: "libro", en: "book", fr: "livre" }[lang] || "livro";
  return new Response(null, {
    status: 302,
    headers: {
      "Set-Cookie": `${ACCESS_COOKIE}=${token}; Path=/; Max-Age=${ACCESS_COOKIE_MAXAGE}; Secure; HttpOnly; SameSite=Lax`,
      "Location":   `/${lang}/${bookSlug}/00-bienvenido/`,
    },
  });
}

// ---- /api/activate — link activation_code → anon_id -----------------------

const ACTIVATION_CODE_RE = /^[A-HJ-NP-Z2-9]{8}$/;
const MAX_ACTIVATE_BODY  = 256;

async function handleActivate(request, env) {
  if (request.method !== "POST") {
    return new Response("Method Not Allowed", {
      status: 405,
      headers: { Allow: "POST", ...CORS_HEADERS },
    });
  }
  if (!env.CF_TELEMETRY) return corsJson({ ok: false, error: "unavailable" }, 503);

  const raw = await request.text();
  if (raw.length > MAX_ACTIVATE_BODY) return corsJson({ ok: false, error: "payload too large" }, 413);

  let body;
  try { body = JSON.parse(raw); }
  catch { return corsJson({ ok: false, error: "invalid json" }, 400); }

  const code    = String(body?.code    || "").trim().toUpperCase();
  const anon_id = String(body?.anon_id || "").trim().toLowerCase();
  if (!ACTIVATION_CODE_RE.test(code)) return corsJson({ ok: false, error: "bad code" }, 400);
  if (!UUID_RE.test(anon_id))         return corsJson({ ok: false, error: "bad anon_id" }, 400);

  const buyer = await env.CF_TELEMETRY
    .prepare("SELECT id FROM buyers WHERE activation_code = ? AND anon_id IS NULL")
    .bind(code).first();
  if (!buyer) return corsJson({ ok: false, error: "invalid or already-used code" }, 404);

  const anonTaken = await env.CF_TELEMETRY
    .prepare("SELECT 1 FROM buyers WHERE anon_id = ?")
    .bind(anon_id).first();
  if (anonTaken) return corsJson({ ok: false, error: "anon_id already linked" }, 409);

  const now = Math.floor(Date.now() / 1000);
  await env.CF_TELEMETRY
    .prepare("UPDATE buyers SET anon_id = ?, activated_at = ?, activation_code = NULL WHERE id = ?")
    .bind(anon_id, now, buyer.id).run();

  return corsJson({ ok: true, verify_url: `https://cyberfuturo.com/verify/buyer-${buyer.id}/` }, 200);
}

// ---- /api/purchase/stripe — Stripe webhook --------------------------------
//
// Signature verification is done here (no Stripe SDK, since _worker.js has no
// bundler). Format docs: https://stripe.com/docs/webhooks/signatures
//   Stripe-Signature: t=<ts>,v1=<hex-hmac>,v0=<legacy>
//   signedPayload = `${ts}.${rawBody}`
//   expected      = HMAC-SHA256(STRIPE_WEBHOOK_SECRET, signedPayload)

const STRIPE_TOLERANCE_S = 300; // 5 minutes — reject very stale signatures (replay defense)

async function verifyStripeSignature(rawBody, header, secret) {
  if (!header) return { ok: false, reason: "missing signature" };
  let ts = null;
  const sigs = [];
  for (const part of header.split(",")) {
    const [k, v] = part.split("=");
    if (k === "t") ts = parseInt(v, 10);
    else if (k === "v1") sigs.push(v);
  }
  if (!ts || !Number.isFinite(ts)) return { ok: false, reason: "bad timestamp" };
  if (sigs.length === 0)            return { ok: false, reason: "no v1 signature" };

  const nowS = Math.floor(Date.now() / 1000);
  if (Math.abs(nowS - ts) > STRIPE_TOLERANCE_S) return { ok: false, reason: "stale timestamp" };

  const expected = await hmacSha256Hex(secret, `${ts}.${rawBody}`);
  for (const sig of sigs) {
    if (timingSafeEqualHex(sig, expected)) return { ok: true };
  }
  return { ok: false, reason: "signature mismatch" };
}

// Maps Stripe Payment Link language dropdowns to ISO codes. Stripe auto-
// generates the custom-field `key` from the label (opaque to us), so we don't
// match on key — we pick whichever dropdown value is recognizable as a
// language, either as an ISO code directly or as a language name.
const LANG_NAME_TO_CODE = {
  "pt": "pt", "português": "pt", "portugues": "pt", "portuguese": "pt",
  "es": "es", "español": "es", "espanol": "es", "spanish": "es",
  "en": "en", "english": "en", "inglês": "en", "ingles": "en",
  "fr": "fr", "français": "fr", "francais": "fr", "french": "fr",
};

function extractLangPref(session) {
  const fields = session?.custom_fields || [];
  for (const f of fields) {
    const raw = String(
      f?.dropdown?.value || f?.text?.value || f?.numeric?.value || ""
    ).trim().toLowerCase();
    if (!raw) continue;
    const code = LANG_NAME_TO_CODE[raw];
    if (code) return code;
  }
  return "pt";
}

function generateActivationCode(len = 8) {
  // Human-friendly alphabet — no 0/O/1/I confusion.
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const bytes = new Uint8Array(len);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, b => alphabet[b % alphabet.length]).join("");
}

function generateAccessToken() {
  // 32 hex chars, matches ACCESS_TOKEN_RE.
  return crypto.randomUUID().replace(/-/g, "");
}

// Welcome email (all 4 languages). Sent via Resend if RESEND_API_KEY is set;
// silently skipped otherwise (operator can resend manually from D1 until the
// Resend account + DNS are ready).
const WELCOME_EMAIL = {
  pt: {
    subject: "CyberFuturo — seu acesso está pronto",
    body: (fname, access_token, activation_code) =>
`Olá ${fname},

Seu acesso ao CyberFuturo está pronto.

1. Leia o livro no site. Clique para entrar:
   https://cyberfuturo.com/auth?t=${access_token}
   (Este link abre o livro e te deixa logado por 2 anos.)

2. Pratique no Codespaces:
   https://codespaces.new/notifuturo/cyberfuturo?quickstart=1

3. Vincule seu progresso ao seu certificado. No terminal, rode:
   ./cf activate ${activation_code}

Cada capítulo concluído gera um handout na sua página pessoal.

— CyberFuturo`,
  },
  es: {
    subject: "CyberFuturo — tu acceso está listo",
    body: (fname, access_token, activation_code) =>
`Hola ${fname},

Tu acceso a CyberFuturo está listo.

1. Lee el libro en el sitio. Clic para entrar:
   https://cyberfuturo.com/auth?t=${access_token}
   (Este enlace abre el libro y te deja con sesión iniciada por 2 años.)

2. Practica en Codespaces:
   https://codespaces.new/notifuturo/cyberfuturo?quickstart=1

3. Vincula tu progreso a tu certificado. En el terminal, ejecuta:
   ./cf activate ${activation_code}

Cada capítulo completado genera un handout en tu página personal.

— CyberFuturo`,
  },
  en: {
    subject: "CyberFuturo — your access is ready",
    body: (fname, access_token, activation_code) =>
`Hi ${fname},

Your access to CyberFuturo is ready.

1. Read the book on the site. Click to log in:
   https://cyberfuturo.com/auth?t=${access_token}
   (This link opens the book and keeps you signed in for 2 years.)

2. Practice in Codespaces:
   https://codespaces.new/notifuturo/cyberfuturo?quickstart=1

3. Link your progress to your certificate. In the terminal, run:
   ./cf activate ${activation_code}

Every chapter you complete generates a handout on your personal page.

— CyberFuturo`,
  },
  fr: {
    subject: "CyberFuturo — votre accès est prêt",
    body: (fname, access_token, activation_code) =>
`Bonjour ${fname},

Votre accès à CyberFuturo est prêt.

1. Lisez le livre sur le site. Cliquez pour vous connecter :
   https://cyberfuturo.com/auth?t=${access_token}
   (Ce lien ouvre le livre et vous garde connecté pendant 2 ans.)

2. Pratiquez sur Codespaces :
   https://codespaces.new/notifuturo/cyberfuturo?quickstart=1

3. Liez votre progression à votre certificat. Dans le terminal :
   ./cf activate ${activation_code}

Chaque chapitre terminé génère un document sur votre page personnelle.

— CyberFuturo`,
  },
};

async function sendWelcomeEmail(env, { email, name, access_token, activation_code, lang_pref }) {
  if (!env.RESEND_API_KEY) return { sent: false, reason: "no api key" };
  const fname = (name || "").split(" ")[0] || "CyberFuturo student";
  const tpl = WELCOME_EMAIL[lang_pref] || WELCOME_EMAIL.pt;
  try {
    const resp = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.RESEND_API_KEY}`,
        "Content-Type":  "application/json",
      },
      body: JSON.stringify({
        from:    "CyberFuturo <ola@cyberfuturo.com>",
        to:      email,
        subject: tpl.subject,
        text:    tpl.body(fname, access_token, activation_code),
      }),
    });
    return { sent: resp.ok, reason: resp.ok ? "ok" : `resend ${resp.status}` };
  } catch (e) {
    return { sent: false, reason: `resend error: ${e?.message || e}` };
  }
}

async function handleStripeWebhook(request, env) {
  if (request.method !== "POST") {
    return new Response("Method Not Allowed", { status: 405, headers: { Allow: "POST" } });
  }
  if (!env.CF_TELEMETRY) return new Response("db unavailable", { status: 503 });
  if (!env.STRIPE_WEBHOOK_SECRET) return new Response("webhook secret missing", { status: 503 });

  const rawBody = await request.text();
  const signature = request.headers.get("stripe-signature");
  const sigResult = await verifyStripeSignature(rawBody, signature, env.STRIPE_WEBHOOK_SECRET);
  if (!sigResult.ok) return new Response(`bad signature: ${sigResult.reason}`, { status: 400 });

  let event;
  try { event = JSON.parse(rawBody); }
  catch { return new Response("bad json", { status: 400 }); }

  if (event.type !== "checkout.session.completed") return new Response(null, { status: 204 });

  const session = event.data?.object || {};
  if (session.payment_status !== "paid") return new Response(null, { status: 204 });

  const external_id  = session.id;
  const email        = String(session.customer_details?.email || "").toLowerCase();
  const name         = session.customer_details?.name || "CyberFuturo student";
  const amount_cents = Number.isFinite(session.amount_total) ? session.amount_total : null;
  const currency     = String(session.currency || "usd").toLowerCase();
  const lang_pref    = extractLangPref(session);

  if (!external_id || !email) return new Response("bad payload", { status: 400 });

  // Dedup via webhook_log UNIQUE(source, external_id).
  const dup = await env.CF_TELEMETRY
    .prepare("INSERT OR IGNORE INTO webhook_log (source, external_id, received_at) VALUES ('stripe', ?, ?)")
    .bind(external_id, Math.floor(Date.now() / 1000)).run();
  if (dup.meta?.changes === 0) return new Response(null, { status: 200 });

  const access_token    = generateAccessToken();
  const activation_code = generateActivationCode(8);
  const now = Math.floor(Date.now() / 1000);

  try {
    await env.CF_TELEMETRY
      .prepare(`INSERT INTO buyers
        (email, name, access_token, activation_code, paid_at, edition, source, amount_cents, currency, lang_pref, external_id)
        VALUES (?, ?, ?, ?, ?, '1.0', 'stripe', ?, ?, ?, ?)`)
      .bind(email, name, access_token, activation_code, now, amount_cents, currency, lang_pref, external_id)
      .run();
    await sendWelcomeEmail(env, { email, name, access_token, activation_code, lang_pref });
  } catch (e) {
    // Email already exists (unique constraint). Buyer has purchased before — resend
    // welcome with the existing tokens.
    const existing = await env.CF_TELEMETRY
      .prepare("SELECT access_token, activation_code FROM buyers WHERE email = ?")
      .bind(email).first();
    if (existing) {
      await sendWelcomeEmail(env, {
        email, name,
        access_token:    existing.access_token,
        activation_code: existing.activation_code || "(already used)",
        lang_pref,
      });
      return new Response(null, { status: 200 });
    }
    return new Response(`db error: ${e?.message || e}`, { status: 500 });
  }

  return new Response(null, { status: 200 });
}

// ---- Cookie gate for paid chapters ----------------------------------------
//
// Matches /pt/livro/, /es/libro/, /en/book/, /fr/livre/ (and deeper). Buyers
// with a valid cf_access cookie fall through to ASSETS; others 302 to the
// buy page preserving ?from= for post-purchase return.

const GATED_PATHS = [
  { prefix: "/pt/livro/", lang: "pt", buy: "/pt/comprar/" },
  { prefix: "/es/libro/", lang: "es", buy: "/es/comprar/" },
  { prefix: "/en/book/",  lang: "en", buy: "/en/buy/"     },
  { prefix: "/fr/livre/", lang: "fr", buy: "/fr/acheter/" },
];

function matchGatedPrefix(pathname) {
  for (const g of GATED_PATHS) {
    if (pathname.startsWith(g.prefix)) return g;
  }
  return null;
}

async function enforceAccessGate(request, env, url, gate) {
  // Without the DB binding we can't verify cookies; redirect to buy page
  // (fail-closed) so paid content is never served unauthenticated.
  if (!env.CF_TELEMETRY) return redirectToBuy(url, gate);

  const cookie = request.headers.get("Cookie") || "";
  const match = cookie.match(/(?:^|;\s*)cf_access=([0-9a-f]{32})(?:;|$)/);
  if (!match) return redirectToBuy(url, gate);

  const token = match[1];
  const row = await env.CF_TELEMETRY
    .prepare("SELECT 1 FROM buyers WHERE access_token = ?")
    .bind(token).first();
  if (!row) return redirectToBuy(url, gate);

  return null; // Allow fallthrough to static asset.
}

function redirectToBuy(url, gate) {
  const loc = new URL(gate.buy, url.origin);
  loc.searchParams.set("from", url.pathname);
  return Response.redirect(loc.toString(), 302);
}

// ---- Entry point ----------------------------------------------------------

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Product routes first — explicit endpoints, deterministic.
    if (path === "/api/purchase/stripe") return handleStripeWebhook(request, env);
    if (path === "/api/activate")        return handleActivate(request, env);
    if (path === "/api/ping")            return handlePing(request, env);
    if (path === "/auth")                return handleAuth(request, env);

    // Cookie gate for paid chapter URLs.
    const gate = matchGatedPrefix(path);
    if (gate) {
      const blocked = await enforceAccessGate(request, env, url, gate);
      if (blocked) return blocked;
    }

    // Smart language redirect at the bare root.
    if (path === "/" && (request.method === "GET" || request.method === "HEAD")) {
      const lang = pickLang(request);
      return Response.redirect(`${url.origin}/${lang}/`, 302);
    }

    return env.ASSETS.fetch(request);
  }
};

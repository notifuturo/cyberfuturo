// Cloudflare Pages — Advanced Mode Worker.
//
// Route table (first match wins, otherwise static-asset fallthrough):
//   1. POST|OPTIONS|DELETE /api/ping → telemetry ingest (D1 binding: CF_TELEMETRY)
//   2. GET|HEAD            /         → smart language redirect
//                                      (cookie → Accept-Language → CF-IPCountry → en)
//   3. anything else                 → env.ASSETS.fetch
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
  // Returns a lowercased list of 2-letter language prefixes in q-order.
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
  // 1. Cookie
  const cookie = request.headers.get("Cookie") || "";
  const match = cookie.match(/(?:^|;\s*)cf_lang=(pt|es|en|fr)(?:;|$)/);
  if (match) return match[1];

  // 2. Accept-Language
  const accept = parseAcceptLanguage(request.headers.get("Accept-Language"));
  for (const prefix of accept) {
    if (LANG_SET.has(prefix)) return prefix;
  }

  // 3. Country hint
  const country = request.headers.get("CF-IPCountry");
  if (country && COUNTRY_LANG[country]) return COUNTRY_LANG[country];

  // 4. English is the widest lingua franca among the remaining candidates.
  return "en";
}

// ---- /api/ping — telemetry ingest -----------------------------------------
//
// Contract: docs/telemetry-spec.md §3-§5. Strict validation, idempotent insert
// via UNIQUE(anon_id, event, lesson), tombstone table for forget requests.
// Reads only the request body and CF-IPCountry — no IP, UA, referrer, or cookies.

const LESSON_RE = /^[0-9]{2}-[a-z0-9-]+$/;
const EVENTS    = new Set(["start", "pass"]);
const UUID_RE   = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const MAX_BODY  = 1024;
const CORS_HEADERS = {
  "Access-Control-Allow-Origin":  "*",
  "Access-Control-Allow-Methods": "POST, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "content-type",
  "Access-Control-Max-Age":       "86400",
};

function jsonResponse(obj, status) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", ...CORS_HEADERS },
  });
}

async function handlePingPost(request, env) {
  if (!env.CF_TELEMETRY) return jsonResponse({ error: "telemetry unavailable" }, 503);

  const raw = await request.text();
  if (raw.length > MAX_BODY) return jsonResponse({ error: "payload too large" }, 413);

  let body;
  try { body = JSON.parse(raw); }
  catch { return jsonResponse({ error: "invalid json" }, 400); }

  const { event, lesson, lang, anon_id } = body || {};
  if (!EVENTS.has(event))      return jsonResponse({ error: "bad event" }, 400);
  if (!LESSON_RE.test(lesson)) return jsonResponse({ error: "bad lesson" }, 400);
  if (!LANG_SET.has(lang))     return jsonResponse({ error: "bad lang" }, 400);
  if (!UUID_RE.test(anon_id))  return jsonResponse({ error: "bad anon_id" }, 400);

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
  if (!env.CF_TELEMETRY) return jsonResponse({ error: "telemetry unavailable" }, 503);

  const raw = await request.text();
  if (raw.length > MAX_BODY) return jsonResponse({ error: "payload too large" }, 413);

  let body;
  try { body = JSON.parse(raw); }
  catch { return jsonResponse({ error: "invalid json" }, 400); }

  const { anon_id } = body || {};
  if (!UUID_RE.test(anon_id)) return jsonResponse({ error: "bad anon_id" }, 400);

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

// ---- Entry point ----------------------------------------------------------

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/ping") {
      return handlePing(request, env);
    }

    if (url.pathname === "/" && (request.method === "GET" || request.method === "HEAD")) {
      const lang = pickLang(request);
      return Response.redirect(`${url.origin}/${lang}/`, 302);
    }

    return env.ASSETS.fetch(request);
  }
};

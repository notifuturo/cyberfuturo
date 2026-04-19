// Cloudflare Pages Function — smart language redirect at the root.
// Deployed automatically by the existing deploy.yml workflow.
//
// Decision order:
//   1. Cookie cf_lang=xx (set on any language page visit) → redirect to /xx/
//   2. Accept-Language header best match among {pt, es, en, fr}
//   3. CF-IPCountry country code → language map
//   4. Fallback: /en/ (widest lingua franca for visitors without clear signal)

const LANGS = ["pt", "es", "en", "fr"];

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
  if (match) return { lang: match[1], source: "cookie" };

  // 2. Accept-Language
  const accept = parseAcceptLanguage(request.headers.get("Accept-Language"));
  for (const prefix of accept) {
    if (LANGS.includes(prefix)) return { lang: prefix, source: "accept-language" };
  }

  // 3. Country hint
  const country = request.headers.get("CF-IPCountry");
  if (country && COUNTRY_LANG[country]) {
    return { lang: COUNTRY_LANG[country], source: "country" };
  }

  // 4. English is the widest lingua franca among the remaining candidates.
  return { lang: "en", source: "fallback" };
}

export async function onRequestGet({ request }) {
  const { lang } = pickLang(request);
  const target = new URL(request.url);
  target.pathname = `/${lang}/`;
  target.search = "";
  return Response.redirect(target.toString(), 302);
}

export async function onRequestHead({ request }) {
  return onRequestGet({ request });
}

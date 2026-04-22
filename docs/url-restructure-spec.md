# CyberFuturo — URL Restructure Spec (Language Equality)

> **Status**: Draft v1.0 — 2026-04-18. Not yet applied. Review → approve → apply.
>
> **Purpose**: make the 4 supported languages equal in URL structure so Portuguese is no longer privileged as "the default." Introduces a smart root redirect that asks the visitor (via Accept-Language / CF-IPCountry / a persistent cookie) and falls back to an always-visible language switcher. Matches the Rosetta Stone product positioning.

---

## 1. Goals and non-goals

### Goals

- Every supported language lives at its own symmetric URL: `/pt/`, `/es/`, `/en/`, `/fr/`.
- The bare root `cyberfuturo.com/` becomes a **smart redirect**, not a language-privileged landing page.
- Returning visitors skip detection (cookie-remembered choice for 180 days).
- New visitors auto-route to their best match; an always-visible language switcher lets them override in one click.
- Search engines see language-equal siblings via `hreflang` — no SEO regression.

### Non-goals

- No blocking splash / interstitial / cookie consent modal. The root redirect is transparent.
- No account system — language choice is per-device, via cookie.
- No runtime language-switching beyond the static pages (nothing JS-heavy, ADR-0003 respected).
- No change to the `./cf` runner's `CF_LANG` convention — that keeps working as-is.

### Derived principle

Whenever this spec says "language," it means exactly one of `pt`, `es`, `en`, `fr`. Any other value is out of scope and rejected by validation.

---

## 2. Target URL structure

```
cyberfuturo.com/                    ← Pages Function, detects and redirects (302)
                                      - returning visitor with cf_lang cookie → go there
                                      - else: Accept-Language best match → go there
                                      - else: CF-IPCountry hint → go there
                                      - else: /pt/ (tiebreak, since PT is canonical content)

cyberfuturo.com/pt/                 ← Portuguese landing (MOVED from /)
cyberfuturo.com/es/                 ← Spanish landing (unchanged path)
cyberfuturo.com/en/                 ← English landing (unchanged path)
cyberfuturo.com/fr/                 ← French landing (unchanged path)

cyberfuturo.com/pt/obrigado/        ← PT thank-you (MOVED from /obrigado.html)
cyberfuturo.com/es/gracias/         ← ES thank-you (MOVED from /gracias.html)
cyberfuturo.com/en/thank-you/       ← EN thank-you (MOVED from /thank-you.html)
cyberfuturo.com/fr/merci/           ← FR thank-you (MOVED from /merci.html)

cyberfuturo.com/404.html            ← unchanged (Cloudflare Pages default)
cyberfuturo.com/favicon.svg         ← unchanged
cyberfuturo.com/styles.css          ← unchanged
cyberfuturo.com/robots.txt          ← unchanged
cyberfuturo.com/sitemap.xml         ← updated (see section 7)
cyberfuturo.com/data/*              ← unchanged (arxiv charts etc.)
```

The thank-you pages ALSO move to directory-based URLs (trailing slash, language-scoped) to match the new convention. Their form actions in `site/*/index.html` must be updated accordingly (section 5.3).

---

## 3. File-move plan

### 3.1. Move the Portuguese landing

```
site/index.html        →  site/pt/index.html
site/obrigado.html     →  site/pt/obrigado/index.html
```

Create `site/pt/` and `site/pt/obrigado/` (trailing-slash pattern).

### 3.2. Move the other thank-you pages into their language folders

```
site/gracias.html      →  site/es/gracias/index.html
site/thank-you.html    →  site/en/thank-you/index.html
site/merci.html        →  site/fr/merci/index.html
```

### 3.3. Old URLs → no backward compatibility

The old `/obrigado.html`, `/gracias.html`, `/thank-you.html`, `/merci.html` paths go away. Any forms that previously POSTed there now POST to the new `/xx/.../index.html` paths. Since these are internal form actions — not links shared externally — no redirect shim is needed.

The bare `/` is handled by the new Pages Function (section 4), which replaces the old static `site/index.html`.

---

## 4. Root Pages Function — smart redirect

File to create: **`site/functions/index.js`**

```javascript
// Cloudflare Pages Function — smart language redirect at the root.
// Deployed automatically by the existing deploy.yml workflow.
//
// Decision order:
//   1. Cookie cf_lang=xx (set on any language page visit) → redirect to /xx/
//   2. Accept-Language header best match among {pt, es, en, fr}
//   3. CF-IPCountry country code → language map
//   4. Fallback: /pt/ (tiebreak only; PT is where content is authored first)

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
  const { lang, source } = pickLang(request);
  const target = new URL(request.url);
  target.pathname = `/${lang}/`;
  target.search = "";   // never forward query strings — they'd create indexing noise
  return Response.redirect(target.toString(), 302);
  // Note: we deliberately do NOT set cf_lang here. That cookie is set only by
  // explicit user action (clicking the language switcher on a language page),
  // so detection never fights the user's own choice.
}

export async function onRequestHead({ request }) {
  // Let HEAD behave the same as GET so curl -I works sensibly.
  return onRequestGet({ request });
}
```

**Design notes:**

- The function handles only GET and HEAD at `/`. Any other method returns the default 405 from Cloudflare. That's fine — the root is a landing redirect, not an API.
- Returns a 302 (temporary) rather than 301 (permanent). If we later change the detection rules — say, to add a 5th language — existing user browsers won't have cached a permanent redirect decision. Tradeoff: 302 doesn't pass as much authority to the destination, but since the destination is a sibling on the same domain, Google handles this correctly per its international-SEO guide.
- `CF-IPCountry` is provided by Cloudflare at the edge. The IP itself never reaches the function.
- The fallback is English (the widest lingua franca among the 4 for visitors whose Accept-Language is ambiguous, e.g. bots without language headers). PT is the *content origin* language but not the *visitor-default* language.

---

## 5. HTML changes in each language page

### 5.1. `hreflang` tags — update in all 4 language landing pages

For each of `site/{pt,es,en,fr}/index.html`, the `<head>` currently has:

```html
<link rel="alternate" hreflang="pt-BR" href="https://cyberfuturo.com/">
<link rel="alternate" hreflang="es-419" href="https://cyberfuturo.com/es/">
<link rel="alternate" hreflang="en-US" href="https://cyberfuturo.com/en/">
<link rel="alternate" hreflang="fr-CA" href="https://cyberfuturo.com/fr/">
<link rel="alternate" hreflang="x-default" href="https://cyberfuturo.com/">
```

Change PT's line to point to `/pt/`:

```html
<link rel="alternate" hreflang="pt-BR" href="https://cyberfuturo.com/pt/">
<link rel="alternate" hreflang="es-419" href="https://cyberfuturo.com/es/">
<link rel="alternate" hreflang="en-US" href="https://cyberfuturo.com/en/">
<link rel="alternate" hreflang="fr-CA" href="https://cyberfuturo.com/fr/">
<link rel="alternate" hreflang="x-default" href="https://cyberfuturo.com/">
```

(`x-default` keeps pointing to `/` — that's now the smart-redirect URL, which is semantically correct: "don't know the user's language? go to the default, which picks for them.")

### 5.2. Canonical tag — update in `site/pt/index.html` only

Old:
```html
<link rel="canonical" href="https://cyberfuturo.com/">
```

New:
```html
<link rel="canonical" href="https://cyberfuturo.com/pt/">
```

Also in Open Graph:
```html
<meta property="og:url" content="https://cyberfuturo.com/pt/">
```

(`site/es/`, `site/en/`, `site/fr/` canonical + og:url are already correct; no change.)

### 5.3. Form actions — update thank-you page paths

Each `site/{pt,es,en,fr}/index.html` has:

```html
<form action="https://formsubmit.co/ajax/lujoeduca@gmail.com" method="POST">
  ...
  <input type="hidden" name="_next" value="https://cyberfuturo.com/obrigado.html">
  ...
</form>
```

Update the `_next` hidden input per language:

- `site/pt/index.html` → `https://cyberfuturo.com/pt/obrigado/`
- `site/es/index.html` → `https://cyberfuturo.com/es/gracias/`
- `site/en/index.html` → `https://cyberfuturo.com/en/thank-you/`
- `site/fr/index.html` → `https://cyberfuturo.com/fr/merci/`

### 5.4. Language switcher — symmetric links + cookie-setting

Current on PT (site/index.html):
```html
<div class="lang-switcher" role="navigation" aria-label="Selecionar idioma">
  <a href="/" class="active">PT</a>
  <a href="/es/">ES</a>
  <a href="/en/">EN</a>
  <a href="/fr/">FR</a>
</div>
```

Replace in all 4 language pages with:

```html
<div class="lang-switcher" role="navigation" aria-label="Selecionar idioma">
  <a href="/pt/" hreflang="pt" data-lang="pt">PT</a>
  <a href="/es/" hreflang="es" data-lang="es">ES</a>
  <a href="/en/" hreflang="en" data-lang="en">EN</a>
  <a href="/fr/" hreflang="fr" data-lang="fr">FR</a>
</div>
```

(Remove the `class="active"` — it's set at build time by the chapter renderer or by a trivial inline script; see 5.5.)

### 5.5. Tiny inline script — remember the current language

Add once, at the bottom of each of the 4 language `index.html` files, just before `</body>`:

```html
<script>
  // Mark the current language in the switcher and remember it for 180 days.
  // Vanilla JS, no framework, no external dependencies. ADR-0003 respected.
  (function() {
    var lang = document.documentElement.lang.slice(0, 2).toLowerCase();
    if (!/^(pt|es|en|fr)$/.test(lang)) return;
    document.cookie = "cf_lang=" + lang + "; path=/; max-age=15552000; SameSite=Lax";
    var sel = document.querySelector('.lang-switcher a[data-lang="' + lang + '"]');
    if (sel) sel.classList.add("active");
  })();
</script>
```

This script:
- Reads `<html lang="pt-BR">` (or `es-419`, `en-US`, `fr-CA`) to identify the page's language
- Sets the `cf_lang` cookie for 180 days so the next bare-root visit skips detection
- Applies `class="active"` to the current language's switcher link

### 5.6. Mismatch banner (optional, recommended) — show when detection disagreed

Add next to the script block, or in a shared place in the header markup:

```html
<div id="lang-mismatch" class="lang-mismatch" hidden></div>
<script>
  (function() {
    var page = document.documentElement.lang.slice(0, 2).toLowerCase();
    var prefs = (navigator.languages || [navigator.language || "en"])
                  .map(function(x){ return x.slice(0,2).toLowerCase(); });
    var first = prefs.find(function(p){ return ["pt","es","en","fr"].indexOf(p) >= 0; });
    if (first && first !== page) {
      var MSG = {
        pt: {text: "Você prefere outro idioma?", es: "Español", en: "English", fr: "Français", pt: "Português"},
        es: {text: "¿Prefieres otro idioma?",    es: "Español", en: "English", fr: "Français", pt: "Português"},
        en: {text: "Prefer another language?",    es: "Español", en: "English", fr: "Français", pt: "Português"},
        fr: {text: "Préférer une autre langue ?", es: "Español", en: "English", fr: "Français", pt: "Português"}
      };
      var banner = document.getElementById("lang-mismatch");
      banner.innerHTML = MSG[page].text + ' <a href="/' + first + '/">' + MSG[page][first] + '</a>';
      banner.hidden = false;
    }
  })();
</script>
```

And a matching minimal style in `site/styles.css`:

```css
.lang-mismatch {
  position: fixed;
  bottom: 16px;
  right: 16px;
  background: var(--card-bg, #2a2a3a);
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 13px;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.lang-mismatch a {
  color: var(--accent, #e879f9);
  font-weight: 600;
  margin-left: 6px;
}
```

Dismissal on click of the link is automatic (the user navigates away). No persistent "don't show again" is needed — the redirect cookie does the work on next visit.

---

## 6. `robots.txt` — update disallow paths

Old:
```
Disallow: /gracias.html
Disallow: /thank-you.html
Disallow: /merci.html
Disallow: /obrigado.html
```

New:
```
Disallow: /pt/obrigado/
Disallow: /es/gracias/
Disallow: /en/thank-you/
Disallow: /fr/merci/
```

Thank-you pages are already gitignored from indexing and shouldn't be crawlable.

---

## 7. Sitemap — symmetric and language-equal

Replace `site/sitemap.xml` with:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://cyberfuturo.com/pt/</loc>
    <lastmod>2026-04-18</lastmod>
    <priority>1.0</priority>
    <xhtml:link rel="alternate" hreflang="pt-BR" href="https://cyberfuturo.com/pt/"/>
    <xhtml:link rel="alternate" hreflang="es-419" href="https://cyberfuturo.com/es/"/>
    <xhtml:link rel="alternate" hreflang="en-US" href="https://cyberfuturo.com/en/"/>
    <xhtml:link rel="alternate" hreflang="fr-CA" href="https://cyberfuturo.com/fr/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://cyberfuturo.com/"/>
  </url>
  <url>
    <loc>https://cyberfuturo.com/es/</loc>
    <lastmod>2026-04-18</lastmod>
    <priority>1.0</priority>
    <xhtml:link rel="alternate" hreflang="pt-BR" href="https://cyberfuturo.com/pt/"/>
    <xhtml:link rel="alternate" hreflang="es-419" href="https://cyberfuturo.com/es/"/>
    <xhtml:link rel="alternate" hreflang="en-US" href="https://cyberfuturo.com/en/"/>
    <xhtml:link rel="alternate" hreflang="fr-CA" href="https://cyberfuturo.com/fr/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://cyberfuturo.com/"/>
  </url>
  <url>
    <loc>https://cyberfuturo.com/en/</loc>
    <lastmod>2026-04-18</lastmod>
    <priority>1.0</priority>
    <xhtml:link rel="alternate" hreflang="pt-BR" href="https://cyberfuturo.com/pt/"/>
    <xhtml:link rel="alternate" hreflang="es-419" href="https://cyberfuturo.com/es/"/>
    <xhtml:link rel="alternate" hreflang="en-US" href="https://cyberfuturo.com/en/"/>
    <xhtml:link rel="alternate" hreflang="fr-CA" href="https://cyberfuturo.com/fr/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://cyberfuturo.com/"/>
  </url>
  <url>
    <loc>https://cyberfuturo.com/fr/</loc>
    <lastmod>2026-04-18</lastmod>
    <priority>1.0</priority>
    <xhtml:link rel="alternate" hreflang="pt-BR" href="https://cyberfuturo.com/pt/"/>
    <xhtml:link rel="alternate" hreflang="es-419" href="https://cyberfuturo.com/es/"/>
    <xhtml:link rel="alternate" hreflang="en-US" href="https://cyberfuturo.com/en/"/>
    <xhtml:link rel="alternate" hreflang="fr-CA" href="https://cyberfuturo.com/fr/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://cyberfuturo.com/"/>
  </url>
</urlset>
```

Key changes vs. the old sitemap:

- PT's `<loc>` is now `/pt/` (was `/`).
- All 4 entries have `priority=1.0` (was PT=1.0, others=0.9 — now equalized).
- Every `<url>` includes the full hreflang alternates, including `x-default` pointing at `/` — the smart-redirect root is the correct `x-default` because it *is* the language-neutral landing.
- `<lastmod>` bumped to 2026-04-18 (apply the correct date when this ships).

---

## 8. GitHub Action — update `deploy.yml` smoke checks

Edit `.github/workflows/deploy.yml` in three places:

### 8.1. "Basic smoke check" step — file existence

Old (checks `site/index.html` at root):
```bash
test -f site/index.html          || { echo "site/index.html missing"; exit 1; }
test -f site/es/index.html       || { echo "site/es/index.html missing"; exit 1; }
test -f site/en/index.html       || { echo "site/en/index.html missing"; exit 1; }
test -f site/fr/index.html       || { echo "site/fr/index.html missing"; exit 1; }
```

New (checks all 4 language pages + thank-you pages + the redirect function):
```bash
test -f site/pt/index.html              || { echo "site/pt/index.html missing"; exit 1; }
test -f site/es/index.html              || { echo "site/es/index.html missing"; exit 1; }
test -f site/en/index.html              || { echo "site/en/index.html missing"; exit 1; }
test -f site/fr/index.html              || { echo "site/fr/index.html missing"; exit 1; }
test -f site/pt/obrigado/index.html     || { echo "site/pt/obrigado/ missing"; exit 1; }
test -f site/es/gracias/index.html      || { echo "site/es/gracias/ missing"; exit 1; }
test -f site/en/thank-you/index.html    || { echo "site/en/thank-you/ missing"; exit 1; }
test -f site/fr/merci/index.html        || { echo "site/fr/merci/ missing"; exit 1; }
test -f site/functions/index.js         || { echo "root redirect function missing"; exit 1; }
test -f site/styles.css                 || { echo "site/styles.css missing"; exit 1; }
test -f site/favicon.svg                || { echo "site/favicon.svg missing"; exit 1; }
test -f site/sitemap.xml                || { echo "site/sitemap.xml missing"; exit 1; }
test -f site/robots.txt                 || { echo "site/robots.txt missing"; exit 1; }
echo "all required files present"
```

### 8.2. "Validate HTML references" step — forbid stale paths

Replace the existing `/pt/`-forbid check (which is now wrong — `/pt/` is the new canonical PT path) with a check that forbids references to the old thank-you URLs:

```bash
# Fail if any HTML file references the old flat thank-you paths.
for stale in '"/obrigado.html"' '"/gracias.html"' '"/thank-you.html"' '"/merci.html"'; do
  if grep -r $stale site/ --include="*.html" > /dev/null; then
    echo "Found stale $stale references in site/:"
    grep -rn $stale site/ --include="*.html"
    exit 1
  fi
done
# Fail if any HTML file still links to bare /  as the PT landing.
if grep -rE 'href="/"[^/]' site/ --include="*.html" > /dev/null; then
  echo "Found bare href=\"/\" references (should be href=\"/pt/\" instead):"
  grep -rnE 'href="/"[^/]' site/ --include="*.html"
  exit 1
fi
echo "HTML reference validation passed"
```

### 8.3. "Post-deploy smoke test" step — new routes

Replace the old routes loop with:

```bash
sleep 5

# Root must 302 to some language
root_code=$(curl -sS -o /dev/null -w "%{http_code}" "https://cyberfuturo.pages.dev/")
if [ "$root_code" != "302" ]; then
  echo "FAIL: / expected 302 (smart redirect), got $root_code"
  exit 1
fi
echo "  /                        302 (redirect as expected)"

# Each language landing must be 200
for path in "/pt/" "/es/" "/en/" "/fr/"; do
  code=$(curl -sSL -o /dev/null -w "%{http_code}" "https://cyberfuturo.pages.dev${path}")
  printf "  %-24s %s\n" "$path" "$code"
  if [ "$code" != "200" ]; then
    echo "FAIL: $path returned $code"
    exit 1
  fi
done

# Each thank-you page must be 200
for path in "/pt/obrigado/" "/es/gracias/" "/en/thank-you/" "/fr/merci/"; do
  code=$(curl -sSL -o /dev/null -w "%{http_code}" "https://cyberfuturo.pages.dev${path}")
  printf "  %-24s %s\n" "$path" "$code"
  if [ "$code" != "200" ]; then
    echo "FAIL: $path returned $code"
    exit 1
  fi
done

# Accept-Language routing sanity
for pair in "es:/es/" "en:/en/" "fr:/fr/" "pt:/pt/"; do
  al="${pair%%:*}"
  expected="${pair##*:}"
  loc=$(curl -sS -o /dev/null -w "%{redirect_url}" -H "Accept-Language: ${al}" "https://cyberfuturo.pages.dev/")
  if [[ "$loc" != *"${expected}" ]]; then
    echo "FAIL: Accept-Language: $al expected redirect to *${expected}, got $loc"
    exit 1
  fi
done
echo "all routes green"
```

---

## 9. Operator runbook

Each step is reversible up to section 9.4 (the push).

```bash
# 1. Create new directories
mkdir -p site/pt/obrigado site/es/gracias site/en/thank-you site/fr/merci site/functions

# 2. Move PT landing and thank-you
git mv site/index.html     site/pt/index.html
git mv site/obrigado.html  site/pt/obrigado/index.html

# 3. Move other thank-you pages into their language folders
git mv site/gracias.html     site/es/gracias/index.html
git mv site/thank-you.html   site/en/thank-you/index.html
git mv site/merci.html       site/fr/merci/index.html

# 4. Apply the HTML edits from section 5 to all 4 language pages:
#     - 5.1  hreflang (PT: href="/" → href="/pt/")
#     - 5.2  canonical + og:url on site/pt/index.html only
#     - 5.3  form _next fields (per language)
#     - 5.4  language switcher markup
#     - 5.5  tiny inline cookie + active-class script
#     - 5.6  (optional) mismatch banner + CSS

# 5. Write the root Pages Function (section 4):
#     site/functions/index.js

# 6. Update robots.txt and sitemap.xml (sections 6 and 7).

# 7. Update .github/workflows/deploy.yml (section 8).

# 8. Local dry run — serve the site and test redirects with curl.
cd site && python3 -m http.server 8080 &
sleep 1
curl -sS -I http://localhost:8080/pt/    | head -1   # expect 200
curl -sS -I http://localhost:8080/es/    | head -1   # expect 200
# (Pages Function at / doesn't run locally with python3 -m http.server;
#  verify the redirect logic via preview deploy on Cloudflare Pages.)
pkill -f "python3 -m http.server 8080"

# 9. Commit and push
git add -A
git commit -m "site: equalize 4 languages under /pt/ /es/ /en/ /fr/ + smart root redirect"
git push

# 10. Watch the deploy
gh run watch

# 11. Verify end-to-end on the live site
curl -sS -I https://cyberfuturo.com/                     # expect 302
curl -sS -I https://cyberfuturo.com/pt/                  # expect 200
curl -sS -o /dev/null -w "%{redirect_url}\n" \
  -H "Accept-Language: es-MX,es;q=0.9" https://cyberfuturo.com/   # expect .../es/
curl -sS -o /dev/null -w "%{redirect_url}\n" \
  -H "Accept-Language: fr-FR,fr;q=0.9" https://cyberfuturo.com/   # expect .../fr/
curl -sS -o /dev/null -w "%{redirect_url}\n" \
  -H "Cookie: cf_lang=en" https://cyberfuturo.com/                # expect .../en/

# 12. Submit the updated sitemap to Google Search Console so reindexing starts
#     immediately rather than waiting for the next crawl.
#     → Search Console → Sitemaps → resubmit https://cyberfuturo.com/sitemap.xml
```

---

## 10. SEO migration plan

The inbound-link surface for `cyberfuturo.com/` is small (site just launched publicly April 2026) but there are a few things to do:

1. **Submit the updated sitemap** to Google Search Console after deploy (step 12 above).
2. **Expect a temporary re-shuffle**, 1-2 weeks: Google discovers the new `/pt/` URL, drops the old root mapping for Portuguese content, and re-indexes. Rankings may wobble briefly.
3. **No explicit 301s needed**: the root `/` now 302s to a language — Google follows this and uses the destination. Canonical and hreflang do the heavy lifting after that.
4. **Social-share cards** (OG tags): already per-language; nothing to change.
5. **Inbound links in Codespaces landing, GitHub repo README, etc.**: update any `https://cyberfuturo.com/` link to `https://cyberfuturo.com/pt/` only if the linker specifically means "the Portuguese version." Otherwise leave them — the redirect carries them to the reader's best language automatically, which is likely the intent.

---

## 11. Verification and first-week expectations

After deploy:

| Check | How | Expected |
|---|---|---|
| Root redirect works | `curl -I https://cyberfuturo.com/` | `HTTP/2 302` + `Location: .../pt/` (or /es/, /en/, /fr/ depending on curl's headers) |
| Language landings up | `curl -I https://cyberfuturo.com/{pt,es,en,fr}/` | `HTTP/2 200` |
| Cookie persists choice | Visit `/en/`, close browser, visit `/` | Redirect to `/en/` (cookie remembered) |
| Country-based route | Test via VPN: visit `/` from BR IP | Redirect to `/pt/` |
| First-visit banner | Set browser Accept-Language to es-MX, visit `/pt/` | Small banner offering Spanish |
| Sitemap renders | `curl https://cyberfuturo.com/sitemap.xml` | Returns 4 `<url>` entries, all priority 1.0 |
| Search Console | Within ~7 days | `/pt/` URL starts appearing; old `/` as PT drops from search |
| No 404s on internal links | Crawl via `wget --spider -r -nv https://cyberfuturo.com/pt/` | Zero 404s |

---

## 12. Rollback

If anything goes wrong:

```bash
# Full rollback: revert the commit and redeploy
git revert <commit-sha>
git push
# → Cloudflare Pages auto-redeploys the prior version within ~1 minute
```

Because the whole change is one commit, revert is one command. The live site returns to the current Portuguese-canonical state, and the smart-redirect function stops serving.

Cloudflare Pages keeps the last 10 deploys available; worst case, the "Promote to Production" button in the dashboard rolls back instantly without git.

---

## 13. Forward compatibility — what this unlocks

Because URL-level language equality is now correct, the next specs inherit it cleanly:

- **Course web reading pages** land at `/pt/curso/`, `/es/curso/`, `/en/course/`, `/fr/cours/` — symmetric from day one. *(Spec originally said `/livro/|/libro/|/book/|/livre/`; renamed 2026-04-22 — see Phase G in `implementation-status.md`. `_worker.js` 301s from the legacy paths.)*
- **Privacy pages** (from telemetry spec) already targeted `/pt/privacidade/`, `/es/privacidad/`, `/en/privacy/`, `/fr/confidentialite/` — this spec validates that choice.
- **Side-by-side Rosetta Stone reading mode** (`/pt+en/livro/...`) can be implemented as a later Pages Function; the URL namespace is free.
- **Stats page** lands at `/stats/` (language-neutral — numbers are numbers) or per-language `/pt/stats/` if localized copy matters.

No further structural URL work will be needed. This is the structural foundation.

---

## 14. Open questions for founder review

1. **Fallback language in the root redirect** — spec picks `en` as fallback for ambiguous visitors (bots without Accept-Language, countries not in the map). Is that right, or should it be `pt` since PT is the content origin? EN is wider; PT aligns with the project's authorship. Either works.
2. **Country-to-language map** — spec maps ~45 countries. Edge cases: Switzerland has 4 official languages, Belgium has 3, Canada is FR+EN. Current call: FR for all of them (ballpark correct for the content-consumer demographic). Consider refining if real traffic data contradicts.
3. **Mismatch banner — default on or off** — spec assumes recommended (section 5.6). Could also ship without it and add later based on user feedback. Ship-with-banner is slightly more helpful; ship-without-banner is slightly cleaner.
4. **Old-path redirects** — spec does NOT add explicit 301 redirects from `/obrigado.html` → `/pt/obrigado/`. These pages are gitignored from search engines and internal links have been updated, so in practice there's no one to redirect. If you want belt-and-suspenders, add a Pages Function for each. Current call: skip.

---

*Spec v1.0 — 2026-04-18. Apply after review. Recommended to apply before the ebook/course product spec so URL structure is stable when the `/livro/` routes go in.*

# CyberFuturo — Telemetry Spec (Opt-in Completion Pings)

> **Status**: Draft v1.0 — 2026-04-18. Not yet applied to the runner. Review → approve → apply.
>
> **Purpose**: give CyberFuturo the minimum viable telemetry loop needed to (a) validate completion rates before building any paid product, (b) fuel the public `/stats/` dashboard, (c) anchor the sponsor-pitch audience-data story — without collecting any personal data, without violating the privacy contract, and without deviating from the free-tier-only ADR.

---

## 1. Goals and non-goals

### Goals

- Count **lesson completions** (`./cf check` passes) per lesson, per country, per language.
- Count **lesson starts** (`./cf start`) for funnel analysis.
- Work on free-tier Cloudflare only (no new vendors, no paid SKUs).
- Be **opt-in** with a clear, truthful prompt. Empty/unknown answer = no pings.
- Require **zero ongoing human work** after deploy — event-driven, stateless, static-first.

### Non-goals

- No user accounts, emails, GitHub identifiers, or IP addresses stored.
- No tracking of which lines were written, what errors occurred, or how long a lesson took.
- No client-side analytics on the static site (per ADR-0003 — still no JS framework).
- No cross-device identity. Anon ID is local to one Codespace / workspace.

---

## 2. Privacy contract (must appear on the site)

A new `/privacidade/` (PT canonical) + `/es/privacidad/`, `/en/privacy/`, `/fr/confidentialite/` page is a **prerequisite**. Content below (PT version; mirror in other languages):

```
CyberFuturo — Privacidade

O que coletamos (só se você aceitar):
  - Quando uma lição é iniciada (slug da lição, ex. "01-terminal")
  - Quando uma lição é concluída (./cf check passa)
  - Um identificador anônimo aleatório, gerado uma vez no seu ambiente, guardado em curriculum/.progress.json
  - O idioma da lição que você está lendo (pt, es, en, fr)
  - O país que o Cloudflare detecta na borda (BR, MX, FR, ...) — o IP em si é descartado

O que NUNCA coletamos:
  - Seu email, nome, conta do GitHub
  - O seu código, seus arquivos, as mensagens de erro
  - Seu IP (o Cloudflare lê o país na borda e descarta o IP antes de chegar ao nosso armazenamento)
  - Qualquer coisa capaz de te identificar individualmente

O que acontece com os dados:
  - São guardados num banco de dados da Cloudflare (D1) controlado pelo CyberFuturo
  - Usados para gerar o painel público /stats/ (só contagens agregadas, nunca por pessoa)
  - Nunca vendidos, nunca compartilhados com sponsors, nunca cruzados com terceiros

Como desativar / apagar:
  - ./cf telemetry off          desativa os pings dali pra frente
  - ./cf telemetry forget       remove seu anon_id local e apaga os registros do servidor
  - Abrir uma issue em github.com/notifuturo/cyberfuturo pedindo remoção
    do seu anon_id também funciona
```

Mirror this content in ES/EN/FR as part of the same deploy.

---

## 3. Data flow

```
Student in Codespaces
  ./cf start 01            →  [local] save current="01-terminal"
                           →  [local] if opt-in && not yet pinged:
                                POST https://cyberfuturo.com/api/ping
                                body: {event:"start", lesson:"01-terminal", lang:"pt", anon_id:"..."}

  ./cf check               →  [local] run test.py
                           →  [local] on pass, append to completed[]
                           →  [local] if opt-in && not yet pinged:
                                POST https://cyberfuturo.com/api/ping
                                body: {event:"pass", lesson:"01-terminal", lang:"pt", anon_id:"..."}

         ↓ HTTPS

Cloudflare Pages Function (site/functions/api/ping.js)
  • Reads CF-IPCountry header (edge-detected)
  • Discards IP, user agent, referrer
  • Validates payload (lesson slug matches /^[0-9]{2}-[a-z0-9-]+$/, event in {start,pass}, lang in {pt,es,en,fr}, anon_id is uuid-shaped)
  • Rate-limits: INSERT OR IGNORE into UNIQUE(anon_id, event, lesson)
  • Returns 204 No Content

         ↓

Cloudflare D1 (CF_TELEMETRY binding)
  • Two tables: events, events_by_day (materialized daily)
  • Writes are idempotent — replaying pings is a no-op
  • Retention: indefinite (aggregate rows are tiny)

         ↓ read only

Nightly GitHub Action (future — separate spec)
  • wrangler d1 execute ... > stats.json
  • Regenerates site/stats/index.html from stats.json
  • git commit + push → Pages deploy auto-fires
```

Event-driven. No servers. No cron on the ingest path. The deploy cron is for the public stats page only, and runs once a day.

---

## 4. D1 schema

File to create: **`scripts/d1_schema.sql`**

```sql
-- CyberFuturo telemetry D1 schema v1
-- Apply with: wrangler d1 execute cf_telemetry --file scripts/d1_schema.sql

CREATE TABLE IF NOT EXISTS events (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  anon_id     TEXT    NOT NULL,
  event       TEXT    NOT NULL CHECK (event IN ('start', 'pass')),
  lesson      TEXT    NOT NULL,
  lang        TEXT    NOT NULL CHECK (lang IN ('pt', 'es', 'en', 'fr')),
  country     TEXT,
  created_at  INTEGER NOT NULL,
  UNIQUE (anon_id, event, lesson)
);

CREATE INDEX IF NOT EXISTS idx_events_lesson  ON events (lesson);
CREATE INDEX IF NOT EXISTS idx_events_country ON events (country);
CREATE INDEX IF NOT EXISTS idx_events_date    ON events (created_at);
CREATE INDEX IF NOT EXISTS idx_events_event   ON events (event);

-- Tombstones for /forget requests; ingest function checks this before inserting.
CREATE TABLE IF NOT EXISTS forgotten_ids (
  anon_id     TEXT    PRIMARY KEY,
  created_at  INTEGER NOT NULL
);
```

Why the UNIQUE constraint on `(anon_id, event, lesson)`: any ping that's already been recorded is silently ignored. This makes the client-side retry logic trivial (we never get duplicates even if the network retries).

---

## 5. Cloudflare Pages Function

File to create: **`site/functions/api/ping.js`**

```javascript
// Cloudflare Pages Function — telemetry ingest.
// Bound D1: CF_TELEMETRY  (configured in Pages project → Settings → Functions → D1 bindings).
// No build step. Cloudflare runs this as-is.

const LESSON_RE  = /^[0-9]{2}-[a-z0-9-]+$/;
const LANGS      = new Set(["pt", "es", "en", "fr"]);
const EVENTS     = new Set(["start", "pass"]);
const UUID_RE    = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const MAX_BODY   = 1024;               // bytes — defense against abuse
const CORS_HEADERS = {
  "Access-Control-Allow-Origin":  "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "content-type",
  "Access-Control-Max-Age":       "86400",
};

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS_HEADERS });
}

export async function onRequestPost({ request, env }) {
  // 1. Enforce body-size ceiling.
  const raw = await request.text();
  if (raw.length > MAX_BODY) {
    return json({ error: "payload too large" }, 413);
  }

  // 2. Parse JSON. Silently reject malformed input.
  let body;
  try { body = JSON.parse(raw); }
  catch { return json({ error: "invalid json" }, 400); }

  const { event, lesson, lang, anon_id } = body || {};

  // 3. Strict validation — reject anything that doesn't match the contract.
  if (!EVENTS.has(event))         return json({ error: "bad event" }, 400);
  if (!LESSON_RE.test(lesson))    return json({ error: "bad lesson" }, 400);
  if (!LANGS.has(lang))           return json({ error: "bad lang" }, 400);
  if (!UUID_RE.test(anon_id))     return json({ error: "bad anon_id" }, 400);

  // 4. Country hint from Cloudflare edge. Discard everything else about the request.
  const country = request.headers.get("CF-IPCountry") || null;

  // 5. Respect tombstones — if this anon_id asked to be forgotten, do nothing.
  const tomb = await env.CF_TELEMETRY
    .prepare("SELECT 1 FROM forgotten_ids WHERE anon_id = ?")
    .bind(anon_id)
    .first();
  if (tomb) return new Response(null, { status: 204, headers: CORS_HEADERS });

  // 6. Idempotent insert. UNIQUE(anon_id, event, lesson) makes this a no-op on replay.
  await env.CF_TELEMETRY
    .prepare("INSERT OR IGNORE INTO events (anon_id, event, lesson, lang, country, created_at) VALUES (?, ?, ?, ?, ?, ?)")
    .bind(anon_id, event, lesson, lang, country, Math.floor(Date.now() / 1000))
    .run();

  return new Response(null, { status: 204, headers: CORS_HEADERS });
}

// Handle /forget separately (DELETE /api/ping with a valid anon_id).
export async function onRequestDelete({ request, env }) {
  const raw = await request.text();
  if (raw.length > MAX_BODY) return json({ error: "payload too large" }, 413);
  let body;
  try { body = JSON.parse(raw); }
  catch { return json({ error: "invalid json" }, 400); }
  const { anon_id } = body || {};
  if (!UUID_RE.test(anon_id)) return json({ error: "bad anon_id" }, 400);

  // Tombstone, then delete any rows we have.
  const now = Math.floor(Date.now() / 1000);
  await env.CF_TELEMETRY.batch([
    env.CF_TELEMETRY.prepare("INSERT OR IGNORE INTO forgotten_ids (anon_id, created_at) VALUES (?, ?)").bind(anon_id, now),
    env.CF_TELEMETRY.prepare("DELETE FROM events WHERE anon_id = ?").bind(anon_id),
  ]);
  return new Response(null, { status: 204, headers: CORS_HEADERS });
}

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", ...CORS_HEADERS },
  });
}
```

**Design notes:**

- Strict input validation — every field is on an allow-list. Garbage payloads are rejected at the edge before touching D1.
- `INSERT OR IGNORE` + the UNIQUE constraint make replay safe. If a student's `./cf check` pings twice because of a network retry, we record the event once.
- `forgotten_ids` tombstone table means `./cf telemetry forget` produces a durable "don't record anything from this ID ever again" effect, even if the client re-pings later.
- The only data the function reads from the HTTP request is the body and `CF-IPCountry`. No IP, no UA, no referrer, no cookies.

---

## 6. Runner patch (curriculum/runner/main.py)

Add these sections to the existing runner. All net-new code is Python stdlib only (ADR-0002 honored). The diff is additive — no existing behavior changes when opt-in is declined.

### 6.1. New imports (top of file, after `import subprocess`)

```python
import urllib.request
import urllib.error
import uuid
```

### 6.2. New constants (after `PROGRESS_FILE = ...`)

```python
TELEMETRY_ENDPOINT = "https://cyberfuturo.com/api/ping"
TELEMETRY_TIMEOUT_S = 2.0   # ping must not slow the runner perceptibly
```

### 6.3. Extend progress file shape

In `load_progress()`, add these defaults alongside the existing ones:

```python
    data.setdefault("current", None)
    data.setdefault("completed", [])
    data.setdefault("telemetry_opt_in", None)   # None = never asked, True/False = decided
    data.setdefault("anon_id", None)             # set only if opted in
    data.setdefault("pinged", {"start": [], "pass": []})
```

### 6.4. New helper — prompt for opt-in on first meaningful command

```python
TELEMETRY_PROMPT = {
    "pt": (
        "\n"
        "  O CyberFuturo quer contar quantas pessoas começam e concluem cada lição.\n"
        "  Se você topar, a gente manda um ping anônimo (só o nome da lição, o idioma\n"
        "  e um ID aleatório gerado agora no seu workspace) pro site.\n"
        "\n"
        "  Não coletamos email, código, IP, ou qualquer coisa que te identifique.\n"
        "  Detalhes em https://cyberfuturo.com/privacidade/\n"
        "\n"
        "  Topar? [s/N]: "
    ),
    "es": (
        "\n"
        "  CyberFuturo quiere contar cuántas personas empiezan y terminan cada lección.\n"
        "  Si aceptas, enviamos un ping anónimo (solo el slug de la lección, el idioma\n"
        "  y un ID aleatorio generado ahora en tu workspace) al sitio.\n"
        "\n"
        "  No recogemos email, código, IP, ni nada que te identifique.\n"
        "  Detalles en https://cyberfuturo.com/es/privacidad/\n"
        "\n"
        "  ¿Aceptas? [s/N]: "
    ),
    "en": (
        "\n"
        "  CyberFuturo would like to count how many people start and finish each lesson.\n"
        "  If you opt in, we send an anonymous ping (just the lesson slug, the language,\n"
        "  and a random ID generated right now in your workspace) to the site.\n"
        "\n"
        "  We do not collect email, code, IP, or anything that could identify you.\n"
        "  Details at https://cyberfuturo.com/en/privacy/\n"
        "\n"
        "  Opt in? [y/N]: "
    ),
    "fr": (
        "\n"
        "  CyberFuturo aimerait compter combien de personnes commencent et terminent chaque leçon.\n"
        "  Si vous acceptez, nous envoyons un ping anonyme (juste le slug de la leçon, la langue\n"
        "  et un ID aléatoire généré maintenant dans votre workspace) au site.\n"
        "\n"
        "  Nous ne collectons ni e-mail, ni code, ni IP, ni rien qui puisse vous identifier.\n"
        "  Détails sur https://cyberfuturo.com/fr/confidentialite/\n"
        "\n"
        "  Accepter? [o/N]: "
    ),
}

_YES_ANSWERS = {"s", "sim", "y", "yes", "o", "oui", "si", "sí"}


def maybe_prompt_telemetry(progress: dict) -> None:
    """Ask the student once, on the first command that counts, whether to opt in.

    Silent no-op if:
      - the user has already answered (True or False)
      - stdin/stdout are not a TTY (Codespaces web UI falls through to the editor;
        we don't want to block non-interactive flows or CI)
      - the CF_TELEMETRY_DISABLED env var is set (escape hatch for operators)
    """
    if progress.get("telemetry_opt_in") is not None:
        return
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return
    if os.environ.get("CF_TELEMETRY_DISABLED"):
        progress["telemetry_opt_in"] = False
        save_progress(progress)
        return

    lang = lesson_lang()
    prompt = TELEMETRY_PROMPT.get(lang, TELEMETRY_PROMPT["pt"])
    try:
        answer = input(prompt).strip().lower()
    except (KeyboardInterrupt, EOFError):
        print()
        progress["telemetry_opt_in"] = False
        save_progress(progress)
        return

    if answer in _YES_ANSWERS:
        progress["telemetry_opt_in"] = True
        progress["anon_id"] = str(uuid.uuid4())
    else:
        progress["telemetry_opt_in"] = False
    save_progress(progress)
```

### 6.5. New helper — fire-and-forget ping

```python
def ping(progress: dict, event: str, lesson_slug: str) -> None:
    """Send a telemetry event. Silent failure on network errors — never blocks the user.

    Guarantees:
      - No-op if the user declined, or never opted in
      - No-op if this (event, lesson_slug) has already been pinged from this workspace
      - Never raises
      - Never takes more than TELEMETRY_TIMEOUT_S to return
    """
    if not progress.get("telemetry_opt_in"):
        return
    anon_id = progress.get("anon_id")
    if not anon_id:
        return
    pinged = progress.setdefault("pinged", {"start": [], "pass": []})
    slot = pinged.setdefault(event, [])
    if lesson_slug in slot:
        return

    payload = json.dumps({
        "event":   event,
        "lesson":  lesson_slug,
        "lang":    lesson_lang(),
        "anon_id": anon_id,
    }).encode("utf-8")
    req = urllib.request.Request(
        TELEMETRY_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TELEMETRY_TIMEOUT_S) as resp:
            if 200 <= resp.status < 300:
                slot.append(lesson_slug)
                save_progress(progress)
    except (urllib.error.URLError, TimeoutError, OSError):
        # Fire-and-forget. If the endpoint is down, we silently drop the event.
        # The local .progress.json is untouched so we'll try again next time.
        pass
```

### 6.6. Wire into `cmd_start` and `cmd_check`

In `cmd_start`, after `progress["current"] = lesson.slug; save_progress(progress)`:

```python
    maybe_prompt_telemetry(progress)
    ping(progress, "start", lesson.slug)
```

In `cmd_check`, inside the `if proc.returncode == 0:` block, after `save_progress(progress)`:

```python
        ping(progress, "pass", lesson.slug)
```

No telemetry code fires on `list`, `show`, `progress`, `help`, or `reset`. Only the two commands that matter.

### 6.7. New subcommand — `./cf telemetry`

Add a new `cmd_telemetry` and route it in `main()`:

```python
def cmd_telemetry(progress: dict, args: list[str]) -> int:
    sub = (args[0] if args else "status").lower()
    if sub == "status":
        state = progress.get("telemetry_opt_in")
        if state is True:
            print(color(f"  Telemetria: ATIVADA. anon_id={progress.get('anon_id')}", GREEN))
        elif state is False:
            print(color("  Telemetria: DESATIVADA.", GREY))
        else:
            print(color("  Telemetria: ainda não perguntada.", YELLOW))
        return 0
    if sub == "on":
        progress["telemetry_opt_in"] = True
        if not progress.get("anon_id"):
            progress["anon_id"] = str(uuid.uuid4())
        save_progress(progress)
        print(color("  Telemetria ativada.", GREEN))
        return 0
    if sub == "off":
        progress["telemetry_opt_in"] = False
        save_progress(progress)
        print(color("  Telemetria desativada.", YELLOW))
        return 0
    if sub == "forget":
        anon_id = progress.get("anon_id")
        if anon_id:
            payload = json.dumps({"anon_id": anon_id}).encode("utf-8")
            req = urllib.request.Request(
                TELEMETRY_ENDPOINT, data=payload,
                headers={"Content-Type": "application/json"},
                method="DELETE",
            )
            try:
                urllib.request.urlopen(req, timeout=TELEMETRY_TIMEOUT_S).read()
            except Exception:
                pass
        progress["telemetry_opt_in"] = False
        progress["anon_id"] = None
        progress["pinged"] = {"start": [], "pass": []}
        save_progress(progress)
        print(color("  anon_id local removido. Servidor avisado.", YELLOW))
        return 0
    print(color(f"  Uso: ./cf telemetry [status|on|off|forget]", RED))
    return 1
```

Route in `main()`:

```python
    if command == "telemetry":
        return cmd_telemetry(progress, args)
```

Update the `__doc__` help block at the top of the file to add:

```
  ./cf telemetry status  Mostra o estado da telemetria anônima
  ./cf telemetry on      Ativa a telemetria
  ./cf telemetry off     Desativa a telemetria
  ./cf telemetry forget  Apaga o anon_id local e pede ao servidor pra apagar os registros
```

---

## 7. Cloudflare config changes

### 7.1. D1 database

Run once from a machine with `wrangler` authenticated:

```bash
wrangler d1 create cf_telemetry
# Copy the database_id from the output — you'll need it below.

wrangler d1 execute cf_telemetry --file scripts/d1_schema.sql
```

### 7.2. Bind D1 to the Pages project

Add a new file: **`site/wrangler.toml`**

```toml
# Cloudflare Pages — function bindings for cyberfuturo
# Deployed via .github/workflows/deploy.yml (wrangler-action)

name = "cyberfuturo"
compatibility_date = "2026-04-15"
pages_build_output_dir = "."

[[d1_databases]]
binding       = "CF_TELEMETRY"
database_name = "cf_telemetry"
database_id   = "REPLACE_WITH_DATABASE_ID_FROM_STEP_7.1"
```

Alternatively (and more robustly for a public repo) — bind via the Pages dashboard:

1. Cloudflare dashboard → Workers & Pages → `cyberfuturo` → Settings → Functions → D1 database bindings
2. Add binding: variable name `CF_TELEMETRY`, database `cf_telemetry`
3. Save and redeploy

Dashboard binding is preferable because the `database_id` isn't checked into a public repo. Leave `site/wrangler.toml` out entirely if you take the dashboard route.

### 7.3. Update the deploy smoke test

Add one line to `.github/workflows/deploy.yml` in the `Post-deploy smoke test` step, after the existing routes loop:

```bash
# Telemetry endpoint is up (CORS preflight returns 204)
code=$(curl -sS -o /dev/null -w "%{http_code}" -X OPTIONS "https://cyberfuturo.pages.dev/api/ping")
if [ "$code" != "204" ]; then echo "FAIL: /api/ping OPTIONS returned $code"; exit 1; fi
echo "  /api/ping               OPTIONS 204"
```

---

## 8. Privacy pages

Before the runner patch ships, each of these must exist:

- `site/privacidade/index.html` (PT)
- `site/es/privacidad/index.html`
- `site/en/privacy/index.html`
- `site/fr/confidentialite/index.html`

Each page contains the contract text from section 2, styled to match `styles.css`. Link from the footer of every language landing page. The `deploy.yml` smoke check should be extended to verify all four return 200.

---

## 9. Operator runbook

Apply the spec sequentially. Each step is reversible up to the point where real pings start arriving (step 7).

```bash
# 1. Create D1 and schema
wrangler d1 create cf_telemetry
wrangler d1 execute cf_telemetry --file scripts/d1_schema.sql

# 2. Bind D1 in the Pages dashboard (see 7.2, dashboard route preferred)

# 3. Add the Pages Function
mkdir -p site/functions/api
# Paste section 5 into site/functions/api/ping.js

# 4. Ship the privacy pages (section 8) in all four languages

# 5. Patch the runner
# Apply section 6 edits to curriculum/runner/main.py

# 6. Update the smoke test
# Apply section 7.3 edit to .github/workflows/deploy.yml

# 7. Commit and push
git add site/functions/api/ping.js \
        site/privacidade/ site/es/privacidad/ site/en/privacy/ site/fr/confidentialite/ \
        curriculum/runner/main.py \
        scripts/d1_schema.sql \
        .github/workflows/deploy.yml \
        docs/telemetry-spec.md
git commit -m "telemetry: opt-in completion pings via Cloudflare Pages Function + D1"
git push

# 8. Verify the deploy workflow passes
gh run watch

# 9. Verify end-to-end from a fresh Codespace
#    - Open a new Codespace on the repo
#    - ./cf start 01        (accept opt-in at the prompt)
#    - ./cf check           (run the lesson to pass)
#    - Check D1 has exactly two rows:
wrangler d1 execute cf_telemetry --command "SELECT event, lesson, lang, country FROM events ORDER BY id DESC LIMIT 5"
```

---

## 10. Verification and first-week expectations

After deploy, watch for these signals over the first week:

| Metric | How to check | Expected early signal |
|---|---|---|
| **Pings arriving at all** | `wrangler d1 execute cf_telemetry --command "SELECT COUNT(*) FROM events"` | Non-zero within 48h of first traffic |
| **Opt-in rate** | `SELECT COUNT(DISTINCT anon_id) FROM events` vs. site traffic from Cloudflare Web Analytics | 20-40% of Codespace launchers, ballpark |
| **Start → pass conversion** | `SELECT lesson, SUM(event='start'), SUM(event='pass') FROM events GROUP BY lesson` | Lesson 00 should show near 1:1; later lessons fall off |
| **Country distribution** | `SELECT country, COUNT(*) FROM events GROUP BY country ORDER BY 2 DESC` | BR dominates, ES-speaking countries clear second, EN/FR tail |
| **Zero PII** | Inspect a few raw rows, confirm no emails, IPs, or code ever appear | Schema forbids it, but verify once after first week |

If pings aren't arriving, check in order:
1. Is the D1 binding present on the Pages project? (dashboard → Settings → Functions)
2. Does `curl -X POST https://cyberfuturo.com/api/ping -H content-type:application/json -d '{"event":"pass","lesson":"00-bienvenido","lang":"pt","anon_id":"11111111-1111-1111-1111-111111111111"}'` return 204?
3. Is `CF_TELEMETRY_DISABLED` set anywhere in your dev environment's env?

---

## 11. Rollback

Any of these reverses the loop cleanly:

- **Pause ingest**: remove the D1 binding from the Pages project. The function throws on insert, returns 5xx. Runner fire-and-forget swallows it — no user impact. Ping data stops arriving.
- **Pause client**: revert the runner patch. Existing opt-ins remain saved but no new pings are sent.
- **Wipe data**: `wrangler d1 execute cf_telemetry --command "DELETE FROM events"`. Schema remains, dashboard resets to zero.
- **Nuke everything**: `wrangler d1 delete cf_telemetry`. No trace left.

Every step is local to Cloudflare and reversible within 60 seconds.

---

## 12. What this spec explicitly does NOT include (separate specs follow)

- **Public `/stats/` dashboard** — nightly GitHub Action that reads D1 and rewrites the stats page. Next spec.
- **Payment integration ($1 enrollment)** — Stripe Payment Link + Pix + webhook Worker that issues certificate and Discord invite on completion. Spec after stats.
- **Certificate generator** — SVG template → PDF via a Worker. Spec after payments.
- **Discord invite automation** — Discord bot / webhook integration. Spec after payments.

Each is a strictly additive layer on top of this telemetry foundation. None require changes to what's shipped here.

---

## 13. Open questions (for founder review)

1. **Endpoint location** — `/api/ping` on the main site vs. a dedicated subdomain (`telemetry.cyberfuturo.com`). Main site is simpler and inherits the existing deploy; subdomain would let us isolate the D1 binding. Spec assumes main site.
2. **Retention** — the spec stores events forever. Simple, small, fine for years at expected volume. If uncomfortable, add a quarterly GitHub Action that rolls old raw events into daily aggregates and deletes raw rows older than 90 days.
3. **Rate limiting** — the spec relies on `INSERT OR IGNORE` for idempotency but doesn't cap events per anon_id per hour. At expected volume this is fine. If abuse becomes visible (e.g. a synthetic load test from one anon_id), add Cloudflare WAF rule on `/api/ping` or a per-anon_id rate check in the function.
4. **Opt-in prompt wording** — the PT version is the canonical truth for tone. Double-check ES/EN/FR translations before shipping.

---

*Spec v1.0 — 2026-04-18. Apply after review.*

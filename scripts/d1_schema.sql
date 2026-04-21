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

-- ---- Product-spec tables (docs/product-spec.md §4) ---------------------------
-- Everything below is additive. Safe to re-run on a live DB.

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
  pdf_r2_key    TEXT,                                    -- R2 object key, e.g. 'handouts/cf-2026-a7b3c1.pdf' (NULL until rendered)
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

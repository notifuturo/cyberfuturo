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

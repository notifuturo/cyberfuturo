#!/usr/bin/env bash
# delete_buyer.sh — honor a buyer's right-to-erasure request (GDPR Art.17 / LGPD Art.18).
#
# Implements the deletion promised in the privacy policy: it ANONYMIZES the
# buyer's personal data (name, email, access credentials) and deletes their
# certificates and telemetry, while retaining the minimal financial transaction
# record (amount, currency, paid_at, Stripe session id) for up to 5 years to meet
# tax/accounting obligations — exactly the "keeping only what tax law requires"
# carve-out stated in /en/privacy/ et al.
#
# Identity must be verified out-of-band first (the request must come from the
# address on file). This is operator-run, not a public endpoint, by design — a
# self-serve hard-delete would be an abuse/griefing vector.
#
# Usage:
#   scripts/delete_buyer.sh someone@example.com           # dry run: prints the SQL
#   scripts/delete_buyer.sh someone@example.com --yes      # execute against D1
#
# Requires: wrangler authenticated to the Cloudflare account (CLOUDFLARE_API_TOKEN).

set -euo pipefail

DB="cf_telemetry"
EMAIL="${1:-}"
CONFIRM="${2:-}"

if [[ -z "$EMAIL" ]]; then
  echo "usage: $0 <email> [--yes]" >&2
  exit 2
fi

# Validate the email shape and reject anything with a single quote (defense against
# breaking the SQL string — operator input is trusted, but fail safe anyway).
if ! [[ "$EMAIL" =~ ^[^[:space:]\'\"@]+@[^[:space:]\'\"@]+\.[^[:space:]\'\"@]+$ ]]; then
  echo "error: '$EMAIL' is not a valid email address" >&2
  exit 2
fi

NOW="$(date -u +%s)"
EMAIL_LC="$(printf '%s' "$EMAIL" | tr '[:upper:]' '[:lower:]')"

# Order matters: tombstone + clear telemetry BEFORE we anonymize the buyer row
# (steps 1-2 read the original email; step 3 rewrites it).
read -r -d '' SQL <<SQL || true
-- 1. Tombstone the linked anon_id so telemetry can never be re-ingested, then drop events.
INSERT OR IGNORE INTO forgotten_ids (anon_id, created_at)
  SELECT anon_id, ${NOW} FROM buyers WHERE email = '${EMAIL_LC}' AND anon_id IS NOT NULL;
DELETE FROM events WHERE anon_id IN
  (SELECT anon_id FROM buyers WHERE email = '${EMAIL_LC}' AND anon_id IS NOT NULL);
-- 2. Delete earned certificates/handouts (they carry the buyer name).
DELETE FROM artifacts WHERE buyer_id IN
  (SELECT id FROM buyers WHERE email = '${EMAIL_LC}');
-- 3. Anonymize PII; keep the financial record for tax retention. Revoking the
--    access_token here also immediately ends the buyer's course access.
UPDATE buyers SET
  email           = 'deleted-' || id || '@redacted.invalid',
  name            = '[deleted]',
  access_token    = 'revoked-' || id || '-' || hex(randomblob(8)),
  activation_code = NULL,
  anon_id         = NULL,
  public_id       = NULL,
  lang_pref       = NULL
WHERE email = '${EMAIL_LC}';
SQL

if [[ "$CONFIRM" != "--yes" ]]; then
  echo "DRY RUN — would execute against D1 '${DB}':"
  echo "----------------------------------------------------------------"
  echo "$SQL"
  echo "----------------------------------------------------------------"
  echo "Re-run with --yes to apply."
  exit 0
fi

echo "Erasing personal data for ${EMAIL_LC} from D1 '${DB}'..."
wrangler d1 execute "$DB" --command "$SQL"
echo "Done. Financial record retained (anonymized); telemetry + certificates removed."

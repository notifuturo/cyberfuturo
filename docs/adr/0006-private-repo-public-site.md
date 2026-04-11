# ADR-0006: Private repo, public site

- **Status**: Accepted (revised from an initial public-repo position)
- **Date**: 2026-04-11

## Context

During the initial launch push we created the GitHub repo as **public** and deployed the site to Cloudflare Pages. The rationale at the time was that "ship publicly" (the user's explicit request) implied both the site and the repo should be visible.

On review, the repo contained material that should not be publicly visible:

1. **`docs/sponsor-outreach.md`** — the full go-to-market playbook, including the target vendor list, pricing grid, email templates, the do/don't checklist, and variations by vendor. Any competitor reading this gets a complete view of our commercial strategy.
2. **`docs/issue-00-draft.md`** — an editorial draft labeled "verify before publish" with unverified CVE placeholders. Public visibility of a labeled draft is harmless in theory but corrosive to the measurement-first positioning in ADR-0001 — it suggests we publish without verification.
3. **`CLAUDE.md`** — project-internal tooling config describing swarm configuration, model routing rules, and hook wiring. Not secrets, but not meant for public consumption.

The repo was publicly visible for approximately **15 minutes** between initial push and correction. The probability of meaningful indexing in that window is low but nonzero — GitHub search and Google both take longer than 15 minutes to refresh, but GitHub's own commit API caches any URL a third party happened to fetch.

## Decision

**The repo is private. The site at `cyberfuturo.pages.dev` remains public.**

The sensitive files were handled as follows:

- `docs/sponsor-outreach.md` → moved to `_private/sponsor-outreach.md` (gitignored)
- `docs/issue-00-draft.md` → moved to `_private/issue-00-draft.md` (gitignored)
- `CLAUDE.md` → removed from tracking with `git rm --cached`; remains on disk and in `.gitignore`
- `.gitignore` updated to prevent re-tracking of any of the above

The cleanup commit removed the files from the HEAD tree but **git history still contains them** in earlier commits. A future history purge (via `git filter-repo`) is required before the repo can safely be re-flipped to public.

## Consequences

### Positive
- **Go-to-market strategy is protected.** Target vendor list, pricing grid, and outreach templates are not visible to competitors or casual crawlers.
- **Editorial drafts stay private.** Readers only see finished, verified content on the public site.
- **Live site is unaffected.** Because we use direct-upload deploy (ADR-0004), the site deployment is fully decoupled from repo visibility.
- **Future collaboration is invitation-scoped.** If we ever want to bring in a co-founder, editor, or contractor, we can grant repo access without changing any public surface.

### Negative
- **We lose the "reproducible research" openness benefit.** Part of the credibility premise of a measurement-first publication is that a skeptical reader can re-run the pipeline themselves. With the repo private, that's limited to invited readers. In v0.2 or v0.3 we may publish a *subset* of the repo (scripts, data, methodology) as a separate public repo.
- **Brief 15-minute exposure window.** Not zero risk. If we ever find evidence that material was scraped during that window, we should assume the sponsor outreach and draft contents are already out.
- **Two-repo future is complex.** The eventual split into "public methodology + data" and "private strategy + editorial" doubles some admin.

### Neutral
- The Cloudflare Pages deploy is direct-upload, which means it doesn't read from the repo at all. Repo visibility is entirely orthogonal to the site.

## If the repo is ever flipped back to public

Before flipping visibility, run:

```bash
git filter-repo --invert-paths \
  --path docs/sponsor-outreach.md \
  --path docs/issue-00-draft.md \
  --path CLAUDE.md
git push --force
```

This purges the files from git history. **Never flip visibility without running this first.**

## Alternatives considered

- **Keep public, delete sensitive files from HEAD.** Rejected. The files would remain in git history and any `git log -p` would expose them.
- **Keep public, run `git filter-repo` immediately.** Deferred. Destructive history rewrites are risky while the repo is still stabilizing. Once we've committed a few more changes and confirmed the state is good, a history purge becomes safer.
- **Two repos from day 1** (public for methodology, private for strategy). Rejected as premature at v0.1 scale — we don't yet know which files belong in which bucket, and maintaining sync between two repos is overhead we can't afford.

## Related

- [ADR-0001 — Measurement-only publication](./0001-measurement-only-publication.md) — the credibility premise that makes leaked drafts especially costly
- `.gitignore` — the enforcement mechanism for this decision

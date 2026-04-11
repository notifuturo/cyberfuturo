# ADR-0004: Cloudflare Pages via direct-upload deploy

- **Status**: Accepted
- **Date**: 2026-04-11

## Context

We need a host for the static site (ADR-0003) that is:

- **Free** on a permanent tier, no credit card required (ADR-0009)
- **Globally edge-cached** so subsecond load is actually achievable
- **SSL-automated** (no Let's Encrypt renewal dance)
- **Custom-domain-capable** for cyberfuturo.com
- **Deployable from a script** so we can automate refreshes without manual UI clicks

Candidates evaluated: Cloudflare Pages, GitHub Pages, Netlify, Vercel, Surge.sh, Bunny CDN.

Separately, within Cloudflare Pages, there are two deploy modes:

- **Git-connected** — CF auto-deploys on every push to a configured branch
- **Direct upload** — deploys triggered via `wrangler pages deploy` from any environment

## Decision

**Host on Cloudflare Pages. Deploy via `wrangler pages deploy` (direct upload mode) for v0.1.**

Cloudflare was chosen over the alternatives because:

| Criterion | Cloudflare Pages | GitHub Pages | Netlify | Vercel |
|---|---|---|---|---|
| Free tier bandwidth | **Unlimited** | 100 GB/mo | 100 GB/mo | 100 GB/mo |
| Free tier build minutes | **500/mo** (irrelevant in direct-upload) | 2,000/mo | 300/mo | 6,000/mo |
| Edge network | **~300 PoPs** | ~10 PoPs | ~50 PoPs | ~100 PoPs |
| Custom domain | Free | Free | Free | Free |
| Auto SSL | Yes | Yes | Yes | Yes |
| Deploy from CLI without a PR | `wrangler pages deploy` | No | `netlify deploy` | `vercel --prod` |
| Requires credit card | **No** | No | No | No |

Direct-upload was chosen over git-connected for v0.1 because:

- The repo is private (ADR-0006) and we want to keep the Cloudflare side decoupled from GitHub OAuth permissions
- Direct upload deploys are triggered from any machine with `wrangler` auth, not tied to a specific git host
- We can deploy partial updates (e.g., just a new chart) without a full git push

Git-connected will likely be adopted in v0.2 once the repo and workflow are stable and auto-deploy-on-push becomes valuable.

## Consequences

### Positive
- **Unlimited free bandwidth** — no surprise invoice even if a post goes viral
- **Subsecond global load** — Cloudflare's edge network is the largest of the candidates
- **Scripted deploy** — `wrangler pages deploy site` deploys in ~5 seconds; we can drive this from a local script, a CI cron, or a future agent
- **No vendor lock-in on content** — all source is in `site/` as plain HTML; any static host can serve it if we migrate

### Negative
- **Manual deploy step** — every update requires an explicit `wrangler pages deploy` call. Until we connect git in the Cloudflare dashboard, `git push` does not deploy.
- **Two identities to manage** — the Cloudflare account (`futuronoti@gmail.com`) and the GitHub account (`notifuturo`) are separate. Worth noting for future admin.
- **Wrangler auth is local-machine scoped** — needs a CF API token to deploy from CI (planned for v0.2 GitHub Actions workflow)

### Neutral
- The `CNAME` file in `site/` is present for GitHub Pages compatibility. It's harmless on Cloudflare (which uses its own custom-domain config) and kept as a safety net for a potential future migration.

## Current live URLs

- Canonical: https://cyberfuturo.pages.dev
- Latest deployment: `https://<hash>.cyberfuturo.pages.dev` (aliased from each deploy)
- Custom domain: **cyberfuturo.com** — pending DNS cutover

## Alternatives considered

- **GitHub Pages.** Rejected. Weaker edge network, slower cache invalidation, and we'd still need direct-upload equivalence for partial deploys. CNAME file remains as a fallback if we ever want to migrate.
- **Netlify.** Rejected. Comparable features, but build minutes are stingier and the edge network is smaller.
- **Vercel.** Rejected. Designed primarily for Next.js — the tooling overhead for a plain static site is wasted. Their ToS changes around commercial use also introduced uncertainty in 2024.
- **Bunny CDN + S3-compatible storage.** Rejected. Cheapest in theory, but no free tier and adds two vendors instead of one.

## Migration path

If we ever need to leave Cloudflare Pages:

1. The `site/` directory is complete and self-contained
2. No CF-specific syntax in any file
3. The CNAME file is already in place for GitHub Pages
4. `wrangler pages deploy` can be replaced with `rclone` / `rsync` / `netlify deploy` without source changes

## Related ADRs

- [ADR-0003 — Static site with no JavaScript framework](./0003-static-site-no-js-framework.md) — this is the content this host serves
- [ADR-0009 — $0 infrastructure constraint](./0009-free-tier-only-infrastructure.md) — drives the free-tier requirement

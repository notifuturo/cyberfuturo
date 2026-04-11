# ADR-0003: Static site with no JavaScript framework

- **Status**: Accepted
- **Date**: 2026-04-11

## Context

The cyberfuturo.com site needs to serve:

- A landing page with positioning, a featured chart, and a subscribe form
- One page per published issue
- One methodology page per published index
- Raw data downloads (CSV, SVG)

This is a small, mostly read-only content site. The obvious default stack in 2026 would be Next.js, Astro, or Hugo. Each adds a build system, a templating layer, and a toolchain to maintain.

We evaluated these against the characteristics that actually matter for CyberFuturo:

1. **Load speed** — readers skimming an issue on mobile should see the chart in <1s
2. **Archivability** — pages should render as PDF, print well, and be WARC-friendly for Wayback Machine preservation
3. **Zero build-step fragility** — the pipeline that builds the data (ADR-0002) should not be coupled to a separate build system for the site
4. **Inspectability** — a reader (or a future auditor) should be able to right-click → view source and see exactly what the page is
5. **Longevity** — the site should still work in 2036 without a single dependency update

A JavaScript framework fails (2), (4), and (5) in subtle ways. Build steps fail (3).

## Decision

**The site is plain HTML + one CSS file. No JavaScript framework, no build step, no component library, no hydration, no client-side routing.**

- Pages are hand-written HTML files committed to git under `site/`
- One shared `styles.css` is linked from every page
- Header and footer HTML are duplicated across pages (accepted tradeoff; see below)
- Charts are static SVG files embedded via `<img src>`
- The subscribe form is a plain HTML `<form>` posting to an external endpoint (ADR — see v0.1 form wiring in `docs/deploy.md`)
- Total weight per page: ~6.5 KB HTML + 5 KB CSS + 4.4 KB SVG ≈ **~16 KB above the fold**

No JavaScript ships on any page.

## Consequences

### Positive
- **Subsecond global load.** Cloudflare edge + 16 KB payload = instant. Mobile, airport Wi-Fi, satellite — all fine.
- **Zero build system to maintain.** `git add site/*.html && git push` is the entire deploy flow. Nothing rots.
- **Perfect archivability.** Print-to-PDF, Wayback Machine, `wget -m` all work out of the box.
- **Minimum attack surface.** No third-party JS means no supply-chain compromise, no analytics leakage, no tracking scripts, no CSP headaches.
- **AI-friendly readability.** LLMs, search engines, RSS readers, screen readers all parse plain semantic HTML trivially.
- **Debuggable with view-source.** A reader can audit every page the way a 2004 blog worked.

### Negative
- **Manual duplication of header/footer.** Every new page requires copy-pasting the shared shell. At ~3 pages today, this is fine. At ~30 pages (v1.0) we may introduce a minimal Python generator that still produces plain HTML as output.
- **No component library.** Every visual pattern is hand-written CSS. We accept this because the design is deliberately minimal.
- **No interactive charts.** Charts are static SVG. If interactive exploration becomes genuinely valuable, we'll add Observable Plot in an iframe, sandboxed.

### Neutral
- **SEO is fine.** Static HTML with proper semantic tags and sitemap.xml is the optimal substrate for search indexing.
- **The CSS is 250 lines.** That's the ceiling we're willing to accept; we'll refactor if it grows beyond that.

## Alternatives considered

- **Astro.** Rejected. Adds a build system and a TypeScript dependency chain. For three pages, the cost exceeds the benefit.
- **Hugo.** Rejected. Another templating language to learn, another binary to keep current, and markdown→HTML rendering still produces output we'd have to audit.
- **Next.js.** Rejected. Framework lock-in, SSR machinery for a site that needs no runtime, and a node_modules tree.
- **11ty (Eleventy).** Rejected. Closest to what we'd want, but still introduces a JavaScript toolchain we don't otherwise need.
- **Write our own generator in Python.** Deferred to v0.5 if page count exceeds ~10 and we genuinely tire of copy-paste. It would produce plain HTML output, preserving every benefit of this ADR.

## Related ADRs

- [ADR-0004 — Cloudflare Pages via direct-upload deploy](./0004-cloudflare-pages-direct-upload.md) is the host this decision optimizes for.
- [ADR-0005 — In-pipeline SVG chart rendering](./0005-inline-svg-chart-rendering.md) makes the "no JavaScript" constraint actually reachable.

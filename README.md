# CyberFuturo

**The $9 course that gets you past "I've never opened a terminal" to your first real Git commit on GitHub.**

Terminal, Git, Python, and SQL — the prerequisite every junior dev job assumes you already have. One weekend, in your browser, zero install. Four languages: Portuguese, Spanish, English, French.

- 🌐 Site: [cyberfuturo.com](https://cyberfuturo.com) · staging at [cyberfuturo.pages.dev](https://cyberfuturo.pages.dev)
- 📘 Free chapter 00 (welcome + first file): [/pt](https://cyberfuturo.com/pt/curso/00-bienvenido/) · [/es](https://cyberfuturo.com/es/curso/00-bienvenido/) · [/en](https://cyberfuturo.com/en/course/00-bienvenido/) · [/fr](https://cyberfuturo.com/fr/cours/00-bienvenido/)
- 🛒 Full course ($9 one-time, lifetime): [/pt](https://cyberfuturo.com/pt/comprar/) · [/es](https://cyberfuturo.com/es/comprar/) · [/en](https://cyberfuturo.com/en/buy/) · [/fr](https://cyberfuturo.com/fr/acheter/)
- 💻 Start the exercises in GitHub Codespaces: [Open Codespace](https://codespaces.new/notifuturo/cyberfuturo?quickstart=1)

---

## What this is

CyberFuturo is a hands-on beginner course for people who got stuck the first time another course told them to "open your terminal and run `pip install`." We teach the prerequisites every other course assumes you already have — the shell, Git, GitHub, Python, SQL, and HTTP APIs — through real exercises you run in a real Linux environment inside your browser (GitHub Codespaces, free tier).

**Free tier:** chapter 00 (welcome + first file) is free, along with every hands-on exercise in the repo. Anyone with a GitHub account (free) can clone the repo, open a Codespace, and work through the exercises on their own — 60h/month of Codespace time is included in the GitHub free tier.

**Paid tier ($9 once, lifetime):** unlocks the editorial chapters 01–08 that walk through terminal → Git → Python → SQL → HTTP, plus shareable per-chapter SVG handouts, 3 module certificates, and 1 final certificate. One purchase, no subscription. Brazilian buyers pay the BRL equivalent via Pix at checkout (Stripe Adaptive Pricing auto-converts); every other region pays in their local currency via card / Apple Pay / Google Pay / Link.

After ~4 hours of hands-on work, a learner walks away with:

- A terminal they know how to use — `pwd`, `ls`, `cd`, pipes, redirection
- A real Git repo on GitHub with their name, their commits, their public history
- A Python script they wrote calling a real public API
- A SQL query they wrote against a real database
- A shareable LinkedIn certificate naming exactly what they completed

That's the baseline every junior dev job assumes you already have, and that no other beginner course ships in one weekend.

---

## Who this is for

- **Maria** (Brazil, 22, 1st-gen university, wants out of retail/call-center into a junior tech job) — PT primary
- **Carlos** (LATAM, 28, self-taught WordPress/Webflow freelancer hitting the frontend ceiling, wants backend rates) — ES primary
- **Amélie** (Montréal / Paris, 31, mid-career switcher burned by unfinished courses) — FR/EN secondary

See [`docs/personas-and-positioning.md`](./docs/personas-and-positioning.md) for the full persona cards, market research, and landing-copy rationale.

## Who this is NOT for

- Already-employed engineers looking to level up (we teach prerequisites you already have)
- Bootcamp shoppers expecting job placement (we're a weekend, not a career program)
- ML / game dev / blockchain specialists (we teach the baseline under all of them)
- No-code / citizen-developer audiences (the CLI IS the point)

---

## Repo layout

```
cyberfuturo/
├── site/                         # Static site, deployed to Cloudflare Pages
│   ├── {pt,es,en,fr}/            # Equal-depth language paths
│   │   ├── index.html            # Landing page
│   │   ├── curso|course|cours/   # Chapter reader (per language)
│   │   │   └── NN-slug/          # Individual chapter pages (00–08)
│   │   ├── comprar|buy|acheter/  # Purchase page
│   │   ├── como-comecar|...      # Orientation page
│   │   └── privacidade|...       # Privacy page
│   ├── _templates/handouts/      # SVG handout templates per chapter × lang
│   ├── _worker.js                # Cloudflare Pages Function — routing, auth, webhook, telemetry
│   ├── verify/                   # Certificate + handout sample galleries
│   └── styles.css
├── curriculum/                   # Hands-on exercises + the ./cf runner
│   ├── lessons/NN-*/             # One directory per exercise
│   └── runner/main.py            # Zero-dependency Python runner (./cf start, check, next, …)
├── scripts/                      # Generators + maintenance scripts (stdlib-only Python)
│   ├── gen_chapter_previews.py   # Builds chapter preview pages for 02–08 × 4 langs
│   ├── gen_sitemap.py            # Walks the site, emits sitemap.xml with hreflang
│   └── d1_schema.sql             # Cloudflare D1 schema (telemetry + buyers + artifacts)
├── docs/
│   ├── personas-and-positioning.md   # Target personas + landing-copy rationale
│   ├── product-spec.md               # Full product spec (buy flow, auth, D1, artifacts)
│   ├── telemetry-spec.md             # Privacy-first usage telemetry
│   ├── url-restructure-spec.md       # Language-equal URL layout
│   ├── implementation-status.md      # Current state of each spec
│   ├── monetization-roadmap.md       # Revenue streams, pricing ladder
│   └── adr/                          # Architecture Decision Records
├── wrangler.toml                 # Cloudflare Pages config (D1 binding, build output)
└── .github/workflows/deploy.yml  # CI: smoke tests → deploy → post-deploy probes
```

---

## Running the exercises locally (without Codespaces)

You don't need this path — Codespaces is the intended environment — but if you want to work offline, the runner is pure Python 3.11+ stdlib:

```bash
git clone https://github.com/notifuturo/cyberfuturo.git
cd cyberfuturo/curriculum
./cf start 00    # open the first exercise
./cf check       # validate your work
./cf next        # advance to the next exercise
./cf progress    # see how far you've gotten
```

Any Linux, macOS, or WSL shell with Python 3.11+ will work. The runner has zero external dependencies — no `pip install`, no build step, no `node_modules`.

---

## Roadmap

- **v1.0** ✅ Live at cyberfuturo.pages.dev — 9 chapters × 4 languages (chapter 00 full, 01 substantive preview, 02–08 locked previews), certificate + handout samples, full buy flow
- **v1.1** — Full editorial prose for chapters 02–08 (currently previews)
- **v1.2** — Handout SVG templates for chapters 01–08 (chapter 00 shipped)
- **v1.3** — `renderArtifactPdf()` wired: personalized handouts + certs rendered server-side, stored in R2, linked from per-buyer `/verify/<id>/` pages
- **v2.0** — New chapters (networking, cloud primitives, HTTP beyond `curl`), v1 buyers upgrade via coupon

See [`docs/implementation-status.md`](./docs/implementation-status.md) for the current state of every spec.

---

## Contributing

Content corrections, translation tweaks, exercise bug reports → open an issue or PR. The repo is public and MIT-licensed; the lessons themselves are CC-BY-4.0. Translations especially welcome from native speakers of any of the four current languages.

## License

- **Code** (runner, scripts, site templates): MIT
- **Lesson content** (`curriculum/lessons/**/*.md`, chapter HTML): CC-BY-4.0 — attribution required if republished

## Contact

Issues, content corrections, translation feedback → open an issue on this repo.

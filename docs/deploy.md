# Deploying cyberfuturo.com

The `site/` directory is a completely static website. No build step, no framework, no server. To ship it publicly you need to do three things:

1. **Push the repo to a git host** (GitHub is easiest)
2. **Connect a static host to the repo** (Cloudflare Pages recommended)
3. **Point cyberfuturo.com DNS at the host**

Then replace one placeholder in the subscribe form.

Total time: ~30 minutes. Total cost: **$0**.

---

## Step 0 — Local smoke test

Always verify locally before pushing.

```bash
cd /home/cypherborg/cyberfuturo/site
python3 -m http.server 8765
# Open http://localhost:8765 in your browser
# Check: / , /issues/01.html , /methodology/arxiv-ai-velocity.html
```

All three pages should render, the chart SVG should display, and the "Read the full brief" and methodology links should work.

---

## Step 1 — Push to GitHub

If the repo does not yet have a remote:

```bash
cd /home/cypherborg/cyberfuturo
# On github.com create a new public repo called "cyberfuturo"
# Do NOT initialize it with a README — the repo is already initialized locally.

git remote add origin git@github.com:YOUR_USER/cyberfuturo.git
git add site/ scripts/ data/ docs/ src/
git commit -m "chore: initial site and first index (arXiv AI velocity v0.1)"
git branch -M main
git push -u origin main
```

If you prefer HTTPS instead of SSH, use `https://github.com/YOUR_USER/cyberfuturo.git`.

---

## Step 2 — Deploy to Cloudflare Pages (recommended)

Cloudflare Pages has a free tier with unlimited bandwidth and sub-second global edge delivery. No credit card required.

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**
2. Authorize Cloudflare to access your GitHub account
3. Select the `cyberfuturo` repo
4. Build settings:
   - **Project name**: `cyberfuturo`
   - **Production branch**: `main`
   - **Framework preset**: *None*
   - **Build command**: *(leave empty)*
   - **Build output directory**: `site`
   - **Root directory**: *(leave empty)*
5. Click **Save and Deploy**

In ~60 seconds you'll get a URL like `https://cyberfuturo.pages.dev`. Visit it and confirm everything loads.

Every subsequent `git push` to `main` auto-deploys.

### Connecting the cyberfuturo.com domain

1. In Cloudflare Pages → your project → **Custom domains** → **Set up a custom domain**
2. Enter `cyberfuturo.com`, click **Continue**
3. Cloudflare will either:
   - **If cyberfuturo.com is already on Cloudflare DNS**: one-click add, done in 30 seconds
   - **If it is elsewhere**: give you two DNS records to add at your registrar — a `CNAME` for `www` and an `A` or `CNAME` for the apex. Add them, wait for propagation (typically <10 minutes)
4. Cloudflare provisions an SSL certificate automatically

Add `www.cyberfuturo.com` the same way if you want the www subdomain to redirect.

---

## Alternative: GitHub Pages

If you prefer not to use Cloudflare:

1. In the GitHub repo → **Settings** → **Pages**
2. **Source**: Deploy from a branch → **Branch**: `main` → **Folder**: `/site`
3. Save. Wait ~60 seconds for first deploy.
4. Under **Custom domain**, enter `cyberfuturo.com` and save.
5. Add DNS records at your registrar per [GitHub's documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site). The `site/CNAME` file is already in place.

Note: GitHub Pages has slower cache invalidation and no edge network in some regions, but it works.

---

## Step 3 — Wire up the subscribe form

The form currently posts to a **placeholder** URL. It must be replaced before the site is useful.

### Option A — beehiiv (recommended, matches the long-term plan)

1. Go to [beehiiv.com](https://www.beehiiv.com) and sign up for a **Launch (free)** publication — up to 2,500 subscribers at $0.
2. Inside your beehiiv publication → **Settings** → **Subscribe Forms** → **Embed** → copy the form action URL. It looks like `https://embeds.beehiiv.com/YOUR_PUBLICATION_UUID`.
3. In `site/index.html` and `site/issues/01.html`, find the `<form>` tag and replace:
   ```html
   <form action="https://formsubmit.co/ajax/_EMAIL_" method="POST">
   ```
   with:
   ```html
   <form action="https://embeds.beehiiv.com/YOUR_PUBLICATION_UUID" method="POST">
   ```
4. Remove the two hidden `<input>` fields (`_subject` and `_captcha`) — those are formsubmit-specific.
5. Commit and push. Cloudflare auto-redeploys.

### Option B — formsubmit.co (zero-signup fallback)

If you want to capture email addresses immediately without creating a beehiiv account:

1. In `site/index.html` and `site/issues/01.html`, replace `_EMAIL_` in the form action with your own email address. Example: `https://formsubmit.co/ajax/you@yourdomain.com`
2. Commit and push.
3. The **first** submission from any visitor triggers a confirmation email to your address. Click the link in that email once to activate the form.

Submissions will arrive as plain emails. You are responsible for migrating them into beehiiv later.

---

## Step 4 — Verify the live site

Once deployed and DNS-attached:

- [ ] `https://cyberfuturo.com/` loads
- [ ] `https://cyberfuturo.com/issues/01.html` loads
- [ ] `https://cyberfuturo.com/methodology/arxiv-ai-velocity.html` loads
- [ ] The chart SVG renders at full width on the homepage
- [ ] The chart SVG renders at full width on issue #01
- [ ] Nav links work from all three pages
- [ ] The subscribe form accepts an email and either redirects to a beehiiv confirmation page or triggers the formsubmit.co activation email
- [ ] SSL certificate is active (green padlock, `https://` only)
- [ ] Test a submission from a real email address end-to-end

---

## What to do when the numbers need updating

The arXiv index is a monthly cadence — refresh on the 2nd of each month.

```bash
cd /home/cypherborg/cyberfuturo
python3 scripts/build_index_arxiv_ai.py
cp data/indices/arxiv-ai-velocity.csv site/data/
cp data/indices/arxiv-ai-velocity.svg site/data/
git add data/indices/ site/data/
git commit -m "data: refresh arxiv-ai-velocity $(date +%Y-%m)"
git push
```

Cloudflare auto-deploys the updated chart in ~30 seconds.

Automating this with GitHub Actions is the next step — see the roadmap in `docs/roadmap.md` (to be added).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Chart shows as broken image | SVG path wrong or file not copied to `site/data/` | Re-run the two `cp` commands in "What to do when the numbers need updating" |
| 404 on `/issues/01.html` | Cloudflare/GitHub deployed wrong folder | Confirm build output directory is `site` in Cloudflare Pages settings |
| Subscribe form 404s | Placeholder URL not replaced | Do Step 3 above |
| Custom domain shows Cloudflare error | DNS not propagated or wrong records | Wait 10 minutes, then check [whatsmydns.net](https://www.whatsmydns.net) for cyberfuturo.com |
| CNAME file causes conflicts | GitHub Pages sometimes rewrites it | Leave `site/CNAME` alone — it is correct as-is |

---

## What is NOT yet in place (intentional)

These are deliberate v0.1 omissions. Add them only if they unblock growth.

- **No analytics.** Add Plausible or Cloudflare Web Analytics if you need numbers.
- **No RSS feed.** Add a hand-written `site/rss.xml` when there are 3+ issues.
- **No comment system.** Replies go to your email via the subscribe form or a `mailto:` in the footer.
- **No newsletter archive page.** The nav currently points directly to issue #01; add a `/issues/` index when issue #03 ships.
- **No dark mode.** Skipped intentionally — adds CSS complexity for negligible reader value at v0.
- **No email-sending pipeline.** Issue #01 is web-only for now. The first email goes out from beehiiv manually, copy-pasted from the HTML.

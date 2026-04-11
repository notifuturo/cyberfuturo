# CyberFuturo — Operator's Manual

> **Purpose**: everything you need to run CyberFuturo after Claude Code is no longer available. Written as a sequence of runnable commands, not as a conceptual overview. If you find yourself reading a paragraph without knowing what to type, something is wrong with this document — open an issue.

This manual assumes a free-tier developer environment: GitHub account (free), Cloudflare account (free), no paid subscriptions.

---

## 0. Recovery: what to do if something is broken

**The live site is down.** Check in this order:

1. Is `https://cyberfuturo.com/` returning anything? → if 5xx, it's Cloudflare. Log into [dash.cloudflare.com](https://dash.cloudflare.com) → Workers & Pages → `cyberfuturo` → Deployments → check for the latest failure.
2. Is the DNS resolving? → `dig cyberfuturo.com` should return an IP. If not, check your domain registrar.
3. Is `https://cyberfuturo.pages.dev/` (Cloudflare's direct URL) working? → if yes, the problem is DNS; if no, the problem is the deployment.
4. Can you redeploy manually? → see section 4.

**A reader says a form didn't work.** FormSubmit.co has a free tier; activation email must have been clicked at least once per receiving email address. Sign in to `lujoeduca@gmail.com`, search for "FormSubmit", click the activation link. Test the form yourself with a real email.

**The Codespaces link doesn't work for a new student.** The GitHub repo must be **public** for unauthenticated users to open in Codespaces. Run: `gh repo view notifuturo/cyberfuturo --json visibility` — if it says PRIVATE, flip it public (see section 7).

---

## 1. The minimal dev environment

You need exactly four things installed locally. All free.

```bash
# macOS with Homebrew
brew install git gh node python@3.12
npm install -g wrangler

# Ubuntu / Debian
sudo apt update
sudo apt install git python3 python3-venv curl
type -p curl >/dev/null || sudo apt install curl
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g wrangler
```

Verify:

```bash
git --version
gh --version
python3 --version     # must be >= 3.11
wrangler --version
```

Then auth:

```bash
gh auth login           # follow prompts, pick HTTPS, pick browser auth
wrangler login          # opens browser for Cloudflare OAuth
```

---

## 2. Cloning the repo for the first time

```bash
git clone https://github.com/notifuturo/cyberfuturo.git
cd cyberfuturo
```

If you're on the `notifuturo` GitHub account (the one that owns the repo), this just works. If you're on a different account, make sure `gh auth status` points at the right one.

---

## 3. The site — what lives where

```
site/
├── index.html                       ← Portuguese (pt-BR) canonical, at /
├── es/index.html                    ← Latin American Spanish, at /es/
├── en/index.html                    ← American English, at /en/
├── fr/index.html                    ← Canadian French, at /fr/
├── obrigado.html                    ← PT thank-you
├── gracias.html                     ← ES thank-you
├── thank-you.html                   ← EN thank-you
├── merci.html                       ← FR thank-you
├── 404.html                         ← multilingual fallback
├── styles.css                       ← single shared stylesheet (Dracula + JetBrains Mono)
├── favicon.svg
├── robots.txt
├── sitemap.xml
└── data/                            ← CSV and SVG assets carried over from v0

curriculum/
├── .gitignore
├── README.md                        ← student-facing
├── cf                               ← launcher script (chmod +x)
├── welcome.sh                       ← ASCII banner on Codespace attach
├── runner/
│   └── main.py                      ← 400-line lesson runner (stdlib only)
└── lessons/
    ├── 00-bienvenido/               ← ES for now; translate per section 5
    ├── 01-terminal/
    ├── 02-primer-git-commit/
    └── 03-python-hola/

.devcontainer/devcontainer.json      ← Codespaces config
```

**Rule of thumb**: changes to `site/` are the marketing-site edits. Changes to `curriculum/` are the product edits. The two rarely cross.

---

## 4. Deploying the site to production

### Option A — from your laptop (manual, always works)

```bash
cd cyberfuturo
wrangler pages deploy site --project-name=cyberfuturo --branch=main --commit-dirty=true
```

You'll see an `.pages.dev` URL for the new deployment. The main `https://cyberfuturo.pages.dev/` alias updates automatically.

### Option B — via git push (once the GitHub Actions workflow is installed, section 8)

```bash
git add site/
git commit -m "site: <what changed>"
git push
```

GitHub Actions picks up the push and deploys automatically. See section 8 for installing the workflow (it's a one-time setup).

---

## 5. Editing the site — common tasks

### 5.1 Edit copy on an existing page

```bash
# Example: edit the Portuguese landing page
nano site/index.html   # or use VS Code, whatever
```

Then run the local smoke test (always):

```bash
cd site
python3 -m http.server 8000
# Open http://localhost:8000/ in your browser
# Check every page works: /, /es/, /en/, /fr/, /obrigado.html, /gracias.html
```

Then deploy (section 4).

### 5.2 Add a new language (e.g. Italian)

1. Decide the locale code. Italy would be `it-IT` or just `it`.
2. Copy one of the existing language pages as a starting point:

   ```bash
   mkdir -p site/it
   cp site/es/index.html site/it/index.html
   ```

3. Open `site/it/index.html` and translate every string, update:
   - `<html lang="it-IT">`
   - Every `hreflang` alternate link — **every language page must list every language**
   - `og:url`, `og:locale`, `og:locale:alternate`
   - The language switcher nav
   - The brand link href
   - The footer language list
   - The `_next` in the waitlist form (create `site/grazie.html` for the thank-you page)
4. Create `site/grazie.html` (or equivalent) following the pattern of `gracias.html`.
5. Update **every existing language page** to add the new language to its switcher and its hreflang alternates. This is tedious but necessary — visitors on the Spanish page should still see "IT" in the switcher.
6. Update `sitemap.xml` to include `/it/` with the same alternate map.
7. Smoke test locally, deploy.

### 5.3 Fix a copy error in the Portuguese landing

Same as 5.1. Edit, smoke test, deploy.

### 5.4 Change the Dracula palette / global style

Edit `site/styles.css`. The color variables are at the top in `:root`. Everything else cascades from there. Smoke test on all 4 language pages before deploying — the CSS is shared.

### 5.5 Fix a broken form

1. Go to https://formsubmit.co and log in with the email the forms point to (currently `lujoeduca@gmail.com`).
2. Confirm the activation link has been clicked at least once.
3. If you want to change the destination email: edit every `formsubmit.co/ajax/<EMAIL>` URL in every `<form>` tag across all 4 language pages. There are 4 forms (one per language), each on the main index page, plus 4 on the thank-you pages — no wait, thank-you pages don't have forms, only the main index pages do. So 4 edits.

---

## 6. Editing the curriculum — common tasks

### 6.1 Write a new lesson

```bash
cd curriculum/lessons
mkdir 04-github-branches
cd 04-github-branches
```

Create two files:

**`lesson.md`** — student-facing instructions. Follow the structure of existing lessons:

```markdown
# Title of the lesson

Intro paragraph (1–2 sentences).

## Tu tarea
A concrete, verifiable task.

## Comandos que vas a usar
```bash
# list of relevant commands
```

## Pistas
- hint 1
- hint 2

## Los pasos, uno por uno
1. ...

## Lo que acabas de aprender
- ...
```

**`test.py`** — auto-grader. Must exit 0 on pass, non-zero on fail. Copy a simple existing test (e.g. `lessons/00-bienvenido/test.py`) and adapt:

```python
"""Test for lesson 04 — github-branches."""
from pathlib import Path
import sys

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
TARGET = CURRICULUM_DIR / "some-file.txt"

def main() -> int:
    if not TARGET.exists():
        print("  ✘ missing file")
        return 1
    # more checks...
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Then test it:

```bash
cd curriculum
./cf list            # should show the new lesson
./cf start 4         # should print instructions
# do the task as if you were a student
./cf check           # should pass
```

Commit and deploy. The landing page will automatically show the new lesson once you also update the `<ul class="curriculum">` block in every language page to list it (optional but recommended).

### 6.2 Translate a lesson to another language

Currently lessons are in Spanish. To add a Portuguese variant for lesson 00:

**Option A (simple):** create a parallel file `lesson.pt.md`. Runner does NOT yet support multilingual display; it always reads `lesson.md`. See runner note at the end of this section.

**Option B (what actually ships):** replace `lesson.md` with the Portuguese version and rename the Spanish to `lesson.es.md`. Update the runner's `_print_lesson` function to optionally load a language-specific file based on an environment variable:

```python
# in curriculum/runner/main.py, replace the hard-coded lesson_file read with:
lang = os.environ.get("CF_LANG", "pt")
candidate = lesson.path / f"lesson.{lang}.md"
if not candidate.exists():
    candidate = lesson.path / "lesson.md"
text = candidate.read_text(encoding="utf-8")
```

Then a student who sets `export CF_LANG=pt` (Portuguese), `es` (Spanish), etc. gets their own translation. Default falls back to whatever `lesson.md` is.

This is a ~5-minute change and future-proofs the multilingual curriculum. Recommended for any future language addition.

### 6.3 Change the welcome banner

Edit `curriculum/welcome.sh`. It's pure bash with ANSI colors. Test with:

```bash
bash curriculum/welcome.sh
```

### 6.4 Fix a lesson auto-grader that's too strict

Look at the `test.py` of that lesson. Every check is a Python function that prints feedback. Loosen or rewrite the failing assertion. Always test locally as a student would before committing.

---

## 7. Repo visibility and Codespaces

For students to "Open in Codespaces" without needing to be granted access, the repo must be **public**.

### Check current visibility

```bash
gh repo view notifuturo/cyberfuturo --json visibility,isPrivate
```

### Flip to public (when you're ready)

**⚠️ Before flipping public, purge the git history of any sensitive files.** The `_private/` directory is already gitignored, but earlier commits in this repo contained `docs/sponsor-outreach.md`, `docs/issue-00-draft.md`, and `CLAUDE.md`. Purge them:

```bash
# one-time, installs git-filter-repo
pip3 install --user git-filter-repo

# from inside the repo:
git filter-repo --invert-paths \
  --path docs/sponsor-outreach.md \
  --path docs/issue-00-draft.md \
  --path CLAUDE.md \
  --path _private

# force push the rewritten history
git push --force

# now flip visibility
gh repo edit notifuturo/cyberfuturo --visibility public --accept-visibility-change-consequences
```

After flipping public, test the Codespaces deep link by opening https://codespaces.new/notifuturo/cyberfuturo?quickstart=1 in an incognito window where you're not signed in as notifuturo.

---

## 8. Installing the GitHub Actions auto-deploy workflow (one-time)

The workflow file is at `docs/github-workflow-deploy.yml.txt` (it has a `.txt` extension because the OAuth scope used to push to this repo doesn't have `workflow` permission — GitHub rejects commits that create or update `.github/workflows/*.yml` unless the token has the `workflow` scope).

To install:

### Option A — via GitHub web UI (easiest)

1. Open https://github.com/notifuturo/cyberfuturo in a browser.
2. Navigate to **Actions** → **New workflow** → **set up a workflow yourself**.
3. Open `docs/github-workflow-deploy.yml.txt` in your editor, copy the entire contents.
4. Paste into the GitHub web editor. Name the file `deploy.yml`.
5. Commit directly to `main`.

### Option B — via CLI with scope upgrade

```bash
gh auth refresh -s workflow   # upgrades your token
mkdir -p .github/workflows
mv docs/github-workflow-deploy.yml.txt .github/workflows/deploy.yml
git add .github/workflows/deploy.yml
git commit -m "ci: auto-deploy to Cloudflare Pages on push to main"
git push
```

### One-time secret setup (required by the workflow)

The workflow needs two secrets:

1. **`CLOUDFLARE_API_TOKEN`** — create at https://dash.cloudflare.com/profile/api-tokens → **Create Token** → **Custom token** → permissions: **Account / Cloudflare Pages / Edit**. Scope: your account. Copy the token (you'll only see it once).

2. **`CLOUDFLARE_ACCOUNT_ID`** — visible on your Cloudflare dashboard sidebar after you log in. A 32-character hex string.

Add both to the repo's Actions secrets:

```bash
gh secret set CLOUDFLARE_API_TOKEN
# paste the token when prompted
gh secret set CLOUDFLARE_ACCOUNT_ID
# paste the account ID when prompted
```

Or via the web UI: **Settings → Secrets and variables → Actions → New repository secret**.

After this, every `git push` to `main` triggers an automatic deploy to Cloudflare Pages. You no longer need to run `wrangler pages deploy` manually.

---

## 9. Pointing `cyberfuturo.com` to Cloudflare Pages

Currently the domain points at a different GitHub Pages site (the old waitlist). To flip it:

### If your domain is already on Cloudflare DNS

1. Log into Cloudflare → your domain → **DNS** → you'll see the GitHub Pages records.
2. Either delete those records or use **Workers & Pages → cyberfuturo → Custom domains → Set up a custom domain**. Enter `cyberfuturo.com`, click **Continue**. Cloudflare will auto-configure.
3. Wait ~60 seconds. SSL provisions automatically.

### If your domain is at another registrar

1. In **Cloudflare → Workers & Pages → cyberfuturo → Custom domains → Set up a custom domain**, enter `cyberfuturo.com`.
2. Cloudflare gives you two DNS records to add at your registrar (usually one `CNAME` for `www` and one `A` or `CNAME` for the apex).
3. Add those records in your registrar's DNS panel. Wait for propagation (up to a few hours, usually <10 minutes).

### Verify

```bash
dig +short cyberfuturo.com
curl -I https://cyberfuturo.com/
```

Should return the Cloudflare edge IPs and a 200 response.

---

## 10. Low-cost / free LLM alternatives after Claude Code

When you need AI help for things like drafting new lessons, reviewing code, or translating content — and you don't have this Claude Code subscription anymore — you have free options:

- **claude.ai** — Free tier, lower rate limit than Claude Code. Good for drafting prose and reviewing code in chat.
- **chat.openai.com** — Free tier, no API access, good for prose and quick questions.
- **gemini.google.com** — Free, generous rate limits, decent at long-form.
- **Groq.com** — Free API access to Llama models, very fast. Good for automation.
- **Local Llama** (Ollama.com) — Runs on your own machine, zero cost, works offline. Best for when you want absolute privacy.

**Prompts you'll use repeatedly** — keep these somewhere:

> "Please translate this CyberFuturo lesson from Spanish to Portuguese Brazilian. Preserve all code blocks exactly. Use informal `você`, not formal. Match the voice of the original: friendly, direct, no hype. Here is the lesson: [paste]"

> "Review this Python test file for the CyberFuturo lesson runner. It should exit 0 on pass and non-zero on fail. Check that error messages are clear and the logic handles missing files gracefully. Here is the file: [paste]"

> "I'm adding a new language to CyberFuturo. The canonical is Portuguese Brazilian (pt-BR) at `/`, with Spanish LatAm at `/es/`, American English at `/en/`, Canadian French at `/fr/`. I want to add [LANGUAGE]. Produce an `index.html` matching the structure of the Portuguese version. [paste the PT file]"

---

## 11. Backup and recovery

Everything that matters lives in **git history on the remote**. The remote is the backup. To fully snapshot the project to your laptop:

```bash
git clone --mirror https://github.com/notifuturo/cyberfuturo.git cyberfuturo-backup.git
# this is a bare-repo clone that includes every branch and tag
```

Store that somewhere safe. If the main remote ever vanishes, you can re-push from this.

The Cloudflare Pages deployment is deterministic from `git HEAD` + `site/` — losing Cloudflare doesn't lose your content, only the serving infrastructure. Re-deploy takes 30 seconds with `wrangler pages deploy site`.

---

## 12. Common errors and fixes

| Error | Cause | Fix |
|---|---|---|
| `wrangler pages deploy` → "unauthorized" | API token expired or missing | Run `wrangler login` and retry |
| Form submission → 404 | FormSubmit.co activation not clicked | Check `lujoeduca@gmail.com`, click the activation link |
| Codespaces button does nothing | Repo is private, viewer is not signed in | Flip repo public (section 7) |
| Lesson runner prints garbled characters | Terminal doesn't support color | `export TERM=xterm-256color` or accept it |
| `./cf check` hangs | Student's python script is reading stdin | Add a timeout to the test script, or pipe `/dev/null` |
| GitHub Actions auto-deploy failing | Secrets not set or token scope wrong | Re-check CLOUDFLARE_API_TOKEN permissions (Pages/Edit) |

---

## 13. Contact (yours)

Publication email: `lujoeduca@gmail.com`
GitHub admin: `notifuturo`
Cloudflare admin: `futuronoti@gmail.com`
Domain registrar: (fill in when you remember which one you used)

---

## Appendix: what this project is NOT

To avoid scope creep when someone asks "can you also add X?":

- **Not a full Codecademy replacement.** It teaches the prerequisites people skip, not a complete curriculum.
- **Not a chat support product.** Learners get help by reading the lesson and running `./cf check`. There is no staffed support channel.
- **Not a payment product.** There is no paid tier at v0. Future monetization is via sponsorships, not subscriptions.
- **Not a certification-issuing body.** No diplomas, no badges, no official credentials at v0.
- **Not tied to any university or bootcamp.** Independent project.

If a feature request doesn't fit one of the things on the "IS" list (teach prerequisites, free, Codespaces-first, multilingual, auto-graded), the default answer is no.

---

*Written as of 2026-04-11. Update the `Last updated` date at the top whenever you revise a section.*

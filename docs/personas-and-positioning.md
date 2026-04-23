# CyberFuturo — Personas & Landing Positioning

> Created 2026-04-23 in response to feedback that the landing copy is too generic — readers don't understand what CyberFuturo actually is. This doc names the target learner, what we're NOT, and proposes concrete replacement copy for the landing hero + supporting sections across all 4 languages.
>
> **Status**: decisions informed by market research (2026-04-23). Research brief + findings archived in git commit history. Final copy blocks below are the ship-ready source of truth.

---

## Decisions (2026-04-23, research-informed)

| # | Decision | Rationale |
|---|---|---|
| **1. Outcome frame** | **Replace.** Lead with price ($9) as hero number + "prerequisite gap" frame. Drop "weekend" from hero to proof strip. | LATAM competitor audit: Platzi/Alura/Rocketseat/Henry all lead with outcome or identity, never duration. At $9 vs. their $30-300/mo, price IS the differentiator. Junior dev postings (vagas.com.br, gupy.io, LinkedIn LATAM, Apr 2026): Git in ~85%, SQL in ~70%, Python in ~45% — "prerequisite" claim is defensible. |
| **2. Persona priority** | **Maria + Carlos co-primary, Amélie tertiary.** FR/EN exist as SEO + credibility plays, not acquisition targets. | LATAM addressable pool is 50-100x FR/QC (IBGE 2024-25 + Platzi/Alura cohort disclosures). Pix owns 45% of BR e-commerce at sub-R$100 (Bacen 2025). FR market tolerates $30-80; $9 reads "suspiciously cheap". Reddit/forum discourse: "travei no terminal" is a LATAM-loud pain, FR-discussion is thinner. |
| **3. Chapters + hours** | **$9 is the hero number.** "9 capítulos / ~4 horas" become proof pills, not hero. | Hero-copy research (CXL 2024, NN/g 2025): one dominant number wins attention. Compound framing (hours + chapters) is for *cards*, not heroes. Leading with price is optimal when price is the differentiator. |
| **4. Buy page in same PR** | **Bundle.** | Teachable/Gumroad/Podia case studies + Baymard 2025: consistent messaging landing → checkout lifts completion 8-15%. Split PR splits the attention window. |
| **5. README refresh** | **Same PR.** | GitHub 2025 Octoverse: README freshness is a top star-conversion factor for small repos. Relaunch case studies (Plausible, Maybe, Tailwind Play): atomic README + site + social = coherent narrative; staged = muddled. |

### Final positioning one-liner (the one sentence to tattoo on the brand)

> **"The $9 course that gets you past 'I've never opened a terminal' to your first real Git commit."**

Per language:

- **PT**: *"O curso de $9 que te leva do 'nunca abri um terminal' ao seu primeiro commit de verdade no Git."*
- **ES**: *"El curso de $9 que te lleva de 'nunca abrí una terminal' a tu primer commit real en Git."*
- **EN**: *"The $9 course that gets you past 'I've never opened a terminal' to your first real Git commit."*
- **FR**: *"Le cours à 9 $ qui te fait passer de 'je n'ai jamais ouvert un terminal' à ton premier vrai commit Git."*

---

## Final ship-ready copy (source of truth for HTML edits)

### Hero — H1

- **PT**: *O curso de **$9** que te leva do "nunca abri um terminal" ao seu primeiro commit de verdade no GitHub.*
- **ES**: *El curso de **$9** que te saca de "nunca abrí una terminal" a tu primer commit real en GitHub.*
- **EN**: *The **$9** course that gets you past "I've never opened a terminal" to your first real commit on GitHub.*
- **FR**: *Le cours à **9 $** qui te fait passer de "je n'ai jamais ouvert un terminal" à ton premier vrai commit sur GitHub.*

### Hero — subhead

- **PT**: *Terminal, Git, Python e SQL — a base que toda vaga de tech júnior assume que você já tem. Em um fim de semana, no navegador, sem instalar nada.*
- **ES**: *Terminal, Git, Python y SQL — la base que todo puesto junior da por supuesta. En un fin de semana, en tu navegador, sin instalar nada.*
- **EN**: *Terminal, Git, Python, and SQL — the prerequisite every junior dev job assumes you already have. One weekend, in your browser, zero install.*
- **FR**: *Terminal, Git, Python et SQL — le prérequis que tout poste junior suppose déjà acquis. En un week-end, dans ton navigateur, zéro installation.*

### Hero — fine print

- **PT**: *Capítulo 00 + todos os exercícios: grátis (Codespaces 60h/mês). Os outros 8 capítulos + certificado + handouts: $9 uma vez, vitalício. Sem mensalidade.*
- **ES**: *Capítulo 00 + todos los ejercicios: gratis (Codespaces 60h/mes). Los otros 8 capítulos + certificado + handouts: $9 una vez, de por vida. Sin suscripción.*
- **EN**: *Chapter 00 + all exercises: free (runs on Codespaces free tier, 60h/month). The other 8 chapters + certificate + handouts: $9 once, lifetime. No subscription.*
- **FR**: *Chapitre 00 + tous les exercices : gratuit (Codespaces 60h/mois). Les 8 autres chapitres + certificat + fiches : 9 $ une fois, à vie. Sans abonnement.*

### Hero — CTAs (label changes; destinations preserved)

| Slot | PT | ES | EN | FR | Destination |
|---|---|---|---|---|---|
| Primary | Ler capítulo 00 grátis → | Leer capítulo 00 gratis → | Read chapter 00 free → | Lire le chapitre 00 gratuit → | `/{lang}/curso\|course\|cours/00-bienvenido/` |
| Secondary | Curso completo · $9 | Curso completo · $9 | Full course · $9 | Cours complet · 9 $ | `/{lang}/comprar\|buy\|acheter/` |
| Tertiary | Ver como funciona | Ver cómo funciona | See how it works | Voir comment ça marche | `#como-funciona` anchor |

### Proof pills (all 4 languages share structure; labels translated)

Remove: ~~stdlib apenas~~, ~~sem build step~~, ~~funciona em 2036~~
Keep/translate: 9 capítulos · ~4h · $9 única · vitalício · sem mensalidade · 4 idiomas
Add: 0 instalação · Git real no fim · Certificado compartilhável · Funciona em Chromebook

Final pill set (PT shown; ES/EN/FR parallel):
- ▸ 0 instalação
- ▸ ~4 horas práticas
- ▸ 9 capítulos
- ▸ Git real no fim
- ▸ Certificado compartilhável
- ▸ Funciona em Chromebook
- ▸ $9 única · vitalício
- ▸ 4 idiomas · PT · ES · EN · FR

### NEW section — "Depois de 4 horas" (insert between proof pills and stack)

**PT:**
```
## Depois de 4 horas, você sai com:

▸ Um terminal que você sabe usar — pwd, ls, cd, pipes, redirecionamentos
▸ Um repositório Git real no GitHub — com seu nome, seus commits, seu histórico público
▸ Um script Python que você escreveu chamando uma API pública real
▸ Uma consulta SQL sua contra um banco real com dados
▸ Um certificado compartilhável no LinkedIn nomeando exatamente o que você completou

Esse é o currículo básico que toda vaga júnior de tech assume que você já tem. E que nenhum outro curso iniciante te entrega num fim de semana.
```

**ES / EN / FR** — parallel structure, translated; kept in HTML edits below.

### Stack section — H2 + intro rewrite

| | H2 | Intro |
|---|---|---|
| PT | As 6 camadas que separam você de uma vaga júnior | Python bonito não vale nada se você não sabe clonar um repositório. A gente começa onde você já está — VS Code e navegador — e desce uma camada por vez até onde as vagas pedem. |
| ES | Las 6 capas entre vos y un puesto junior | Un Python prolijo no sirve si no sabés clonar un repo. Empezamos donde ya estás — VS Code y navegador — y bajamos una capa por vez hasta donde los puestos lo piden. |
| EN | The 6 layers between you and a junior dev job | Clean Python doesn't matter if you can't clone a repo. We start where you already are — VS Code and a browser — and go down one layer at a time until you hit what job posts actually require. |
| FR | Les 6 couches entre toi et un poste junior | Un Python propre ne vaut rien si tu ne sais pas cloner un dépôt. On part d'où tu es déjà — VS Code et un navigateur — et on descend couche par couche jusqu'à ce que les offres d'emploi réclament. |

### Footer tagline

- **PT**: *CyberFuturo — a base que todo curso júnior assume que você já tem. $9, vitalício, em 4 idiomas.*
- **ES**: *CyberFuturo — la base que todo curso junior da por supuesta. $9, de por vida, en 4 idiomas.*
- **EN**: *CyberFuturo — the prerequisite every junior dev job assumes you already have. $9, lifetime, in 4 languages.*
- **FR**: *CyberFuturo — le prérequis que tout cours débutant suppose acquis. 9 $, à vie, en 4 langues.*

### Meta tags

| Lang | `<title>` | Meta description |
|---|---|---|
| PT | CyberFuturo — O curso de $9 que te leva do zero ao seu primeiro commit no GitHub | Terminal, Git, Python e SQL — a base que toda vaga de tech júnior assume que você já tem. Em um fim de semana, no navegador, sem instalar nada. Capítulo 00 grátis, curso completo por $9. |
| ES | CyberFuturo — El curso de $9 que te lleva del cero a tu primer commit en GitHub | Terminal, Git, Python y SQL — la base que todo puesto junior da por supuesta. En un fin de semana, en tu navegador, sin instalar nada. Capítulo 00 gratis, curso completo por $9. |
| EN | CyberFuturo — The $9 course that gets you to your first real Git commit | Terminal, Git, Python, and SQL — the prerequisite every junior dev job assumes you already have. One weekend, in your browser, zero install. Chapter 00 free, full course $9. |
| FR | CyberFuturo — Le cours à 9 $ qui te mène à ton premier vrai commit Git | Terminal, Git, Python et SQL — le prérequis que tout poste junior suppose acquis. En un week-end, dans ton navigateur, zéro installation. Chapitre 00 gratuit, cours complet à 9 $. |

---

## The core insight

CyberFuturo is specifically for people who **couldn't get past "open your terminal"** in other programming courses. That is the one sentence the current landing page fails to say.

Every other beginner course — Platzi, DataCamp, Codecademy, Le Wagon — silently assumes the learner already has: a working Linux/macOS shell, Git configured, an editor that can be launched from the command line, and the vocabulary to read instructions like `cd ~/projects && git clone …`. CyberFuturo is the course that **doesn't skip those 40 invisible prerequisites**. And it does so in the browser (Codespaces), so the learner doesn't need a "real" dev machine to start.

That's the whole pitch. The current copy dances around this with metaphors ("desconstrua a stack", "de trás para frente") and never names the reader.

---

## Target personas

Three concrete people. Primary = where the first 500 paying customers come from. Secondary = where months 6–12 expand.

### 🥇 Primary — "Maria" (22, São Paulo / Recife / Fortaleza)

| | |
|---|---|
| **Who** | 1st-generation-university student or recent grad. Communication, marketing, admin, or education major. Currently in retail, call-center, or admin assistant work. |
| **Why tech now** | Friends moved to tech and doubled their salary. She sees AI coming for her current role. Wants out. |
| **What she tried** | Free Python on YouTube, Platzi trial, DataCamp "Intro to Python". Quit each one at the same place: the instructor said "open your terminal and run `pip install pandas`" and she had no idea what that meant. |
| **Pain** | *"Cada curso começa no meio."* Every course assumes prerequisites she never got. |
| **Win** | Can open a terminal, clone a repo, run a script, explain in an interview what she did. Enough to clear the junior-filter auto-screen on vagas.com.br or LinkedIn. |
| **Words she uses** | "começar do zero", "vaga júnior", "estágio em TI", "não sei nem por onde começar", "sem faculdade de computação" |
| **Objection** | *"Mais um curso que vai ensinar `ls` e `cd` e parar aí sem me levar a lugar nenhum."* |
| **Language** | **PT** primary; also ES if she's from a border region |
| **Price elasticity** | $9 is acceptable; $29 is a stretch; $49 is no. R$47 equivalent via Pix is easier than $9 via card. |

### 🥇 Primary — "Carlos" (28, Buenos Aires / CDMX / Bogotá)

| | |
|---|---|
| **Who** | Self-taught web person. 3 years freelance making WordPress, Webflow, Shopify, Elementor sites. Comfortable with HTML/CSS and a little JS, but has never used a terminal seriously. |
| **Why tech now** | His freelance ceiling is $20/hour. Backend devs in his region charge $50+. He sees the wall between "designer-who-codes" and "real dev" and wants across. |
| **What he tried** | Laracasts, a Node tutorial, Fireship videos. Each starts with "abre la terminal y …" and he fakes it, then gets stuck on `git rebase` or `npm ci`. |
| **Pain** | *"Puedo entregar sitios a clientes pero no puedo leer un issue de GitHub."* |
| **Win** | Terminal + Git fluency, can explain what a migration is, can set up a basic Flask/Node API. Opens the door to backend freelance rates. |
| **Words he uses** | "salir de freelance básico", "cobrar más", "backend real", "GitHub en serio", "dejar de hacer solo frontend" |
| **Objection** | *"Los bootcamps cuestan USD 4.000; no me lo puedo permitir."* |
| **Language** | **ES** primary |
| **Price elasticity** | $9 is a no-brainer; treats it like a Netflix month. |

### 🥈 Secondary — "Amélie" (31, Montréal / Paris / Lyon)

| | |
|---|---|
| **Who** | 8 years in a non-tech job (teaching, nursing, marketing, finance). Already has a degree. |
| **Why tech now** | 2025–2026 career pressure: AI automating her current function. Decided on a tech switch. |
| **What she tried** | Attended Le Wagon / Ironhack info sessions, sticker-shocked by €8–14k. Started Codecademy Python, reached chapter 7, quit when asked to "clone the repo." |
| **Pain** | *"J'ai 31 ans, je n'ai pas le temps de recommencer à zéro. Il me faut quelque chose que je peux finir ce week-end."* She's bought 3 courses, finished none. |
| **Win** | ONE tangible artifact — a repo with 20+ commits, a script that runs, a certificate naming exactly what she completed. Proof to herself (and to LinkedIn) that she can cross the line. |
| **Words she uses** | "reconversion", "concret", "preuve", "portfolio", "en un week-end", "sans tout réapprendre" |
| **Objection** | *"J'ai déjà acheté trois cours et je n'en ai fini aucun."* |
| **Language** | **FR** primary, **EN** comfortable |
| **Price elasticity** | $9 is impulse-tier; she wants to be sure it will actually finish in a weekend. |

---

## Who this is NOT for

Naming non-targets is how the pitch gets sharp.

- **Already-employed engineers** looking to level up into ML, security, SRE, etc. (We teach prerequisites they already have.)
- **Bootcamp shoppers** expecting 6-month structure + job placement. (We're a weekend, not a career program.)
- **Specialty learners** — people who want game dev, ML, blockchain, mobile. (We don't teach any of those; we teach the baseline under all of them.)
- **No-code / citizen-developer audience.** (The terminal IS the point; we're not for someone trying to avoid it.)
- **Kids / under-16.** (Tone and pacing assume adult career motivation.)

---

## Positioning one-liner (replaces "Aprenda tecnologia de trás para frente")

> **"The prerequisite every junior dev job assumes you already have — terminal, Git, Python, SQL — done in one weekend, in your browser, for nine dollars."**

Per-language:

- **PT**: *"O terminal, o Git e o Python que todo curso júnior assume que você já sabe — em um fim de semana, no navegador, por nove dólares."*
- **ES**: *"La base que todo curso junior asume que ya tenés — terminal, Git, Python, SQL — en un fin de semana, en tu navegador, por nueve dólares."*
- **EN**: *"The prerequisite every junior dev job assumes you already have — terminal, Git, Python, SQL — in one weekend, in your browser, for nine dollars."*
- **FR**: *"Le prérequis que tout cours débutant suppose déjà acquis — terminal, Git, Python, SQL — en un week-end, dans ton navigateur, pour neuf dollars."*

Why this works: names the reader ("assume que você já sabe" calls out the gap), names the concrete outcome (4 named tools), names the effort ("um fim de semana" = finishable), names the friction (navegador = no install), and names the price (9 USD is the price of a pizza).

---

## Proposed new landing copy

### Hero (PT canonical — ES/EN/FR parallel below)

**H1:** O terminal, o Git e o Python que todo curso júnior **assume que você já sabe.**

**Subhead:** Em ~4 horas no navegador, você sai de *"nunca abri um terminal"* para *"tenho meu primeiro script Python rodando num repositório Git de verdade."* Sem instalar nada. Sem setup. Sem "configure seu ambiente". Você faz, a gente valida, o Git registra.

**CTAs:** (unchanged — Codespaces primary, Comprar secondary)

### Proof pills — new mix (outcome + trust, remove dev-plumbing)

**Remove** (these matter to engineers, not to Maria or Amélie):
- ~~stdlib apenas~~
- ~~sem build step~~
- ~~funciona em 2036~~

**Keep**:
- 4 idiomas · PT · ES · EN · FR
- 9 capítulos
- $9 única · vitalício
- sem mensalidade

**Add** (what a buyer actually cares about):
- 0 instalação
- ~4 horas
- Repositório Git real no fim
- Funciona em Chromebook
- Certificado compartilhável no LinkedIn

### NEW section — "Depois de 4 horas, você vai ter:"

Inserted **between** the proof pills and the current "A stack, camada por camada" section. This is the outcome-promise block that's currently missing entirely.

```
## Depois de 4 horas, você vai ter:

▸ Um terminal que você sabe usar — pwd, ls, cd, pipes, redirecionamentos
▸ Um repositório Git real no GitHub — com seu nome, seus commits, seu histórico público
▸ Um script Python escrito por você que chama uma API pública e extrai dados
▸ Uma consulta SQL que você escreveu contra um banco real com dados
▸ Um certificado compartilhável dizendo exatamente o que você completou

Isso é o currículo básico que toda vaga júnior de tech assume
que você já tem. E que nenhum outro curso iniciante te dá.
```

### Stack section — reframe

**Current H2:** "A stack, camada por camada"
**New H2:** "As 6 camadas que separam você de uma vaga júnior"

**Current intro:** *"A maioria dos cursos ensina Python da sintaxe para cima …"*
**New intro:** *"Python com sintaxe bonita não vale nada se você não sabe clonar um repositório. SQL não vale nada se você não sabe abrir um terminal. A gente começa onde você já está — o VS Code e o navegador — e desce uma camada por vez até onde as vagas pedem."*

(The 6 CAMADA items stay — their content already works. Just the section frame changes.)

### Pricing line (replaces current muted fineprint)

**Current:** *"Exercícios grátis (60h/mês de Codespaces). Curso completo: $9 USD uma vez. Acesso vitalício."*

**New:** *"Capítulo 00 + todos os exercícios: **grátis** (rodam no Codespaces, 60h/mês incluídas). Os outros 8 capítulos + certificado + handouts compartilháveis: **$9 uma vez, vitalício**. Sem mensalidade. Sem upsell. Se não gostar, tem seu repositório Git pra mostrar do mesmo jeito."*

### Footer tagline

**Current:** *"CyberFuturo — aprenda tecnologia de trás para frente. Grátis, open source, multilíngue."*
**New:** *"CyberFuturo — o pré-requisito que todo curso de programação esqueceu de te ensinar. Open source em 4 idiomas."*

---

## Per-language nuances

Same product, same outcome promise. Cultural knobs to turn:

| | PT (Maria) | ES (Carlos) | EN (Amélie / intl) | FR (Amélie) |
|---|---|---|---|---|
| **Reader state named** | "nunca abri um terminal" | "puedo entregar sitios pero no puedo leer un issue" | "stuck at 'clone the repo'" | "j'ai déjà acheté trois cours" |
| **Outcome framed as** | "vaga júnior" / "estágio" | "cobrar más" / "backend real" | "the prerequisite" / "the weekend fix" | "une preuve concrète" / "en un week-end" |
| **Price anchor** | "mais barato que uma pizza" | "menos que un mes de Netflix" | "less than a sandwich in Manhattan" | "moins qu'un café par jour pendant une semaine" |
| **Objection handled** | "não vai parar no `ls` e `cd`" | "no es otro bootcamp de USD 4.000" | "you actually finish this in a weekend" | "le seul cours que tu finiras ce week-end" |
| **Tone** | direct, warm, slightly self-deprecating | confident, street-smart, value-focused | plain, specific, no-BS | precise, reassuring, concrete |

---

## Rewrite scope — files to touch (after approval)

| File | What changes |
|---|---|
| `site/pt/index.html` | Hero H1 + subhead, proof pills, **new outcome section**, stack H2 + intro, pricing line, footer, `<title>`, meta description, og:title, og:description |
| `site/es/index.html` | Same blocks, ES copy |
| `site/en/index.html` | Same blocks, EN copy |
| `site/fr/index.html` | Same blocks, FR copy |
| `site/{pt,es,en,fr}/comprar\|buy\|acheter/index.html` | Hero copy sync (~20 min) — **optional, can defer** |
| `README.md` | Top-level README still describes old "indices publication" product — tangential but overdue |

Estimate: ~1.5 hours of edits once the messaging direction is locked.

---

## Open questions — please answer before I touch HTML

1. **Is "junior dev filter / one weekend / $9" the right outcome frame?** Alternatives I considered and rejected:
   - *"Survive the AI layoff wave"* — too negative, too vague
   - *"Build your portfolio"* — portfolio is a side-effect, not the promise
   - *"Certificate-first"* — certificate is the receipt, not the reason
2. **Persona priorities correct?** Maria + Carlos primary, Amélie secondary. If you want to prioritize FR/career-switcher instead, the hero needs to tilt.
3. **Keep the 9-chapter framing, or restructure as "4h core + 8h advanced"?** The honest work is ~4h for the first pass through 00–06 and longer if they do every exercise carefully. "4 hours" is the install-this-weekend hook; "9 chapters" is the product-shape trust signal. I want to use **both**.
4. **Rewrite the /comprar buy-page copy in the same pass, or defer?** Buy pages currently share the same generic problem ("O curso completo" etc.) but editing them isn't blocking the landing-page fix.
5. **README refresh in the same PR or a separate one?** Separate is cleaner since it's a different audience (GitHub visitors vs. site visitors).

---

## What I'll ship after you sign off

Single commit per language (4 commits), plus one commit for cross-cutting metadata updates. CI smoke tests stay green — none of the URLs change, only the copy inside them. Memory will save the final positioning line for future brand consistency.

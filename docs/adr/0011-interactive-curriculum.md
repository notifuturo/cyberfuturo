# ADR-0011: Interactive, Portuguese-first curriculum embedded in the repo

- **Status**: Accepted
- **Date**: 2026-04-15

## Context

CyberFuturo's mission is to publish rigorous, free leading indicators for how fast the digital foundations of the near future are being built. A natural extension of that mission is closing the digital-skills gap in Latin America: the same audience that benefits from CyberFuturo's indices often lacks structured, zero-cost paths to learn the tools that power modern tech work.

The curriculum teaches terminal navigation, Git, Python, SQL, and HTTP/APIs through hands-on lessons with automated validation. Each lesson requires the student to produce real artifacts (files, commits, scripts, queries) and verifies them with stdlib-only Python tests. The entire experience runs inside the project's devcontainer, requiring zero local setup.

The primary underserved audience is Brazilian and Latin American Portuguese speakers. Portuguese-first authoring targets this group directly; Spanish and English translations follow as secondary languages.

## Decision

**Ship an interactive, Portuguese-first curriculum embedded in the repository, validated by stdlib-only Python tests, runnable in the devcontainer.**

Concretely:

- Lessons live in `curriculum/lessons/NN-slug/`, each containing `lesson.md` (Portuguese), optional `lesson.es.md` / `lesson.en.md` translations, and `test.py`
- A stdlib-only runner (`curriculum/cf`) drives lesson selection, validation, and progress tracking
- Portuguese is the canonical language; the runner falls back to Portuguese when a requested translation is missing
- All tests use only the Python standard library, consistent with ADR-0002
- The curriculum runs inside the devcontainer with no additional dependencies

### Why Portuguese-first

Brazil is the largest economy in Latin America and has a massive population of aspiring developers with limited access to high-quality, free, Portuguese-language technical education. Spanish-speaking Latin America has more existing resources. Starting with Portuguese maximizes impact per lesson authored; Spanish and English translations are added incrementally.

## Consequences

### Positive

- **Hands-on learning.** Students produce real files, commits, and scripts — not multiple-choice answers. Every completed lesson is a verifiable artifact in their Git history.
- **Zero cost.** The curriculum runs entirely in GitHub Codespaces (free tier) or any machine with Python 3 and Git. No paid tools, no accounts beyond GitHub.
- **Reproducible.** The devcontainer pins the environment. A lesson that passes today will pass in a year.
- **Aligned with the publication.** Students who complete the curriculum can read, reproduce, and critique CyberFuturo's indices — converting learners into engaged readers.

### Negative

- **Maintenance burden.** Each new lesson requires authoring, translation, and test maintenance. Lessons are coupled to the repo's directory structure and runner implementation.
- **Repo structure coupling.** Lessons reference specific paths and conventions. Refactoring the repo layout requires updating lesson content and tests.
- **Translation lag.** Portuguese-first means Spanish and English versions may trail behind, temporarily excluding non-Portuguese speakers from new content.

### Neutral

- The curriculum is orthogonal to CyberFuturo's index publication pipeline. It shares the repo but does not depend on the data ingestion or site-generation code.

## Alternatives considered

- **External LMS (Moodle, Google Classroom).** Rejected. Adds a dependency, requires accounts, and breaks the "zero-cost, zero-setup" constraint.
- **Static tutorial pages on the site.** Rejected. Loses the interactive validation loop that makes lessons effective. Reading instructions is not the same as executing them.
- **English-first with translations.** Rejected. English-language beginner tech content is abundant. Portuguese-first targets the gap where impact is highest.

## Related ADRs

- [ADR-0002 — Python stdlib-only pipeline](./0002-python-stdlib-only-pipeline.md) — the curriculum runner and all lesson tests follow the same stdlib-only constraint
- [ADR-0003 — Static site with no JavaScript framework](./0003-static-site-no-js-framework.md) — the curriculum is content, not a web app; no JS framework needed
- [ADR-0009 — $0 / free-tier-only infrastructure](./0009-free-tier-only-infrastructure.md) — the curriculum must run on free-tier Codespaces with no paid dependencies

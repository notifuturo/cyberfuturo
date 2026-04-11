# CyberFuturo — Compliance Report

**Generated**: 2026-04-11 10:27  
**Overall**: PASS ✅

This report is produced by `scripts/compliance_check.py` and audits the repo against every [ADR](./adr/README.md) and business rule in [`docs/domain/business-concepts.md`](./domain/business-concepts.md).

Run locally with:
```bash
python3 scripts/compliance_check.py
```

## Lint gates

| # | Gate | Enforces | Status |
|---|---|---|---|
| 1 | `scripts/lint_editorial.py` — No-forecast vocabulary | BR-01 / ADR-0001 | PASS ✅ |
| 2 | `scripts/lint_pipeline.py` — Stdlib-only pipeline, no LLM | ADR-0002 / ADR-0008 | PASS ✅ |
| 3 | `scripts/lint_briefs.py` — Brief structure + disclosure | BR-04 / BR-09 | PASS ✅ |
| 4 | `scripts/lint_indices.py` — Versioned methodology + kill criteria | ADR-0007 / BR-11 | PASS ✅ |

## Required public pages

**Status**: PASS ✅

All required public pages present.

## Lint output

### `scripts/lint_editorial.py`

```
PASS  lint_editorial: scanned 8 files, zero forbidden words
```

### `scripts/lint_pipeline.py`

```
PASS  lint_pipeline: scanned 1 pipeline file(s), zero violations
```

### `scripts/lint_briefs.py`

```
PASS  lint_briefs: scanned 1 brief(s), all compliant
```

### `scripts/lint_indices.py`

```
PASS  lint_indices: scanned 1 index/indices, all compliant
```

## Coverage matrix

| Rule | Enforcement | Status |
|---|---|---|
| ADR-0001 measurement-only | lint_editorial.py forbidden-word scan | PASS ✅ |
| ADR-0002 stdlib only | lint_pipeline.py AST import check | PASS ✅ |
| ADR-0003 static site no JS | no enforcement script yet (manual review) | — |
| ADR-0004 CF Pages direct upload | no enforcement script yet (manual review) | — |
| ADR-0005 inline SVG | no enforcement script yet (manual review) | — |
| ADR-0006 private repo public site | manual — gh repo view --json visibility | — |
| ADR-0007 versioned methodology | lint_indices.py section check | PASS ✅ |
| ADR-0008 no LLM numbers | lint_pipeline.py module+URL check | PASS ✅ |
| ADR-0009 $0 free tier | manual — no automated check | — |
| ADR-0010 trailing window drift | lint_indices.py (via methodology limitations) | PASS ✅ |
| BR-01 no forecasts | lint_editorial.py | PASS ✅ |
| BR-02 no LLM numbers | lint_pipeline.py | PASS ✅ |
| BR-03 methodology before pub | lint_indices.py methodology presence | PASS ✅ |
| BR-04 traceability | lint_briefs.py citation tuple | PASS ✅ |
| BR-05 corrections next brief | editorial process (manual) | — |
| BR-06 one sponsor per brief | future sponsor-commerce validator | — |
| BR-07 sponsors below the fold | future template constraint | — |
| BR-08 editorial independence | editorial process (manual) | — |
| BR-09 AI disclosure | lint_briefs.py disclosure-marker check | PASS ✅ |
| BR-10 subscribers never shared | privacy page presence + policy statement | PASS ✅ |
| BR-11 every index has kill crit | lint_indices.py deprecation-criteria check | PASS ✅ |
| BR-12 git history audit trail | git history — manual review | — |

Rules marked `—` have no automated enforcement yet. They are tracked as manual-review items; upgrading them to automated checks is part of the v0.2 compliance roadmap.

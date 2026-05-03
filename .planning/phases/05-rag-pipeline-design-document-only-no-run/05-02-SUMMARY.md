---
phase: 05-rag-pipeline-design-document-only-no-run
plan: 02
subsystem: evaluation
tags: [rag, evaluation, queries, bilingual, cross-lingual, out-of-scope, pitfall-6, pitfall-7, pitfall-9]
requires:
  - instances/entities/document/far-25-1309.yaml
  - instances/entities/document/nasa-tm-2014-218175.yaml
  - instances/entities/document/ntsb-aar-09-03.yaml
  - docs/regulations/far-25-1309/processed.md
  - docs/cfd-papers/nasa-tm-2014-218175/processed.md
  - docs/accident-reports/ntsb-aar-09-03/processed.md
  - .yamllint
provides:
  - "evaluation/queries.yaml — 30 bilingual aviation queries with expected source-document URIs and 5-type taxonomy"
  - "evaluation/README.md — AI 接力 + schema + Phase-7 consumption contract"
affects:
  - .planning/design/RAG_PIPELINE.md (§3.2 names this file as the baseline eval set; plan 05-01 will reference it)
  - "future Phase 7 implementation (eval harness will consume queries.yaml verbatim)"
tech-stack:
  added: []
  patterns:
    - "YAML 1.2 with --- document-start (yamllint compliance)"
    - "Bilingual ZH/EN query records (matching i18n.label pattern from instances/entities/)"
    - "URI-based expected_documents references (aviationkb://document/<slug>@<version>)"
    - "AI 接力开发指南 README pattern (mirrors scripts/validators/README.md AIH-01)"
key-files:
  created:
    - evaluation/queries.yaml
    - evaluation/README.md
  modified: []
decisions:
  - "OOS count is 6 (not 3-min). Provides safety margin; 6 categories of OOS exercised: trivial off-topic, aviation-adjacent (pilot cert), adversarial (prompt injection), corpus-absent aircraft (A320), completely off-domain (GPT-4), adjacent regulation (§25.1310). The §25.1310 case is the discriminator test — high lexical overlap with §25.1309 but disjoint document; if guardrail can reject §25.1310 queries it can reject anything."
  - "All 6 cross_lingual queries are ZH→EN (no EN→ZH) because all 3 corpus documents are language=en. Phase 6 (corpus expansion) may add ZH-source documents — when that happens, EN→ZH queries should be added under q-031+ to maintain symmetry. This is documented in evaluation/README.md 'Adding a New Query' procedure."
  - "expected_keywords field is OPTIONAL but populated on every query. Bilingual keywords (e.g. ['catastrophic', '灾难性']) give Phase 7 substring-presence checks for free without requiring full reference-answer text."
metrics:
  duration_minutes: 12
  tasks_completed: 3
  files_created: 2
  files_modified: 0
  total_lines_added: 532
  total_queries: 30
  by_type:
    factual: 9
    table: 6
    procedural: 3
    cross_lingual: 6
    out_of_scope: 6
  documents_covered: 3
  completed_date: 2026-05-03
---

# Phase 5 Plan 02: RAG Eval Set — Summary

Authored `evaluation/queries.yaml` (30 bilingual aviation queries spanning 5 type categories) and `evaluation/README.md` (AI 接力 + schema + Phase-7 consumption contract) — the eval contract Phase 7's RAG harness will run against to measure recall@5, cross-lingual recall@5, out-of-scope short-circuit rate, and citation accuracy.

## What was delivered

### `evaluation/queries.yaml` (322 lines, 30 records)

| Type             | Count | Query IDs       | Pitfall surface              |
| ---------------- | ----- | --------------- | ---------------------------- |
| `factual`        | 9     | q-001..q-009    | Baseline retrieval recall    |
| `table`          | 6     | q-010..q-015    | **Pitfall 6** (table chunking) |
| `procedural`     | 3     | q-016..q-018    | Multi-step methodology       |
| `cross_lingual`  | 6     | q-019..q-024    | **Pitfall 7** (ZH↔EN recall) |
| `out_of_scope`   | 6     | q-025..q-030    | **Pitfall 9** (guardrail)    |
| **Total**        | 30    | —               | RAG-07 acceptance            |

### `evaluation/README.md` (210 lines)

- `> ## AI 接力开发指南` block (35+ lines) with what-this-IS / what-this-IS-NOT / how-Phase-7-consumes / 5-min stranger-test pass criterion
- `## Schema` section mirroring 05-02-PLAN `<interfaces>` (5-value type enum, required vs optional fields)
- `## Categories` table with min counts per type
- `## Phase 7 Consumption Contract` with executable pseudocode + acceptance gates (recall@5≥0.80, cross_lingual_recall@5≥0.70, out_of_scope_short_circuit_rate==1.00, citation_accuracy≥0.95, table_recall@5≥0.80)
- `## File Layout` + `## Adding a New Query` step-by-step procedure
- `## Cross-References` (PITFALLS 6/7/9/12, RAG_PIPELINE.md §3.2, document URIs, REQ-coverage)

## Document URIs covered (verbatim from `instances/entities/document/`)

| Document URI                                          | Queries citing it                                      | Section anchors used                       |
| ----------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------ |
| `aviationkb://document/far-25-1309@1`                  | q-001, q-002, q-003, q-010, q-011, q-016, q-019, q-020, q-021 (9 in-scope citations) | §25.1309(a) / (b) / (c)                    |
| `aviationkb://document/nasa-tm-2014-218175@1`          | q-004, q-005, q-006, q-012, q-013, q-017, q-022, q-023 (8 in-scope citations) | Abstract / §1 / §2 / §3 / §4               |
| `aviationkb://document/ntsb-aar-09-03@1`               | q-007, q-008, q-009, q-014, q-015, q-018, q-024 (7 in-scope citations) | Executive Summary / Sequence / Probable Cause / Recommendations / Cross-references |

OOS queries (q-025..q-030) have `expected_documents: []` per schema.

## Verification results

All `<verify><automated>` blocks from 05-02-PLAN ran clean:

```
Task 1 verify (README): PASS — 210 lines, all 5 type values present, ≥30 mentioned, recall@5 mentioned, AI 接力 present
Task 2 verify (18 records):  PASS — 9 factual + 6 table + 3 procedural; all 3 corpus URIs covered
Task 3 verify (30 records):  PASS — table≥6, cross_lingual≥6, out_of_scope≥3; all OOS have []; all in-scope have ≥1; 30 unique IDs
yamllint -c .yamllint evaluation/queries.yaml: exit 0 (only line-length warnings, level=warning)
python -c "import yaml; yaml.safe_load(open('evaluation/queries.yaml'))": exit 0 (parses)
```

Plan-level aggregate (per `<verification>` block in 05-02-PLAN):

1. `wc -l evaluation/queries.yaml` = 322 ≥ 200 ✓
2. `wc -l evaluation/README.md` = 210 ≥ 60 ✓
3. Schema invariants (count, types, URI validity, OOS empty list, ID uniqueness) ✓
4. All 3 corpus document URIs appear in `expected_documents` (verbatim) ✓
5. `AI 接力开发指南` present in `evaluation/README.md` ✓
6. yamllint clean (exit 0) ✓

REQ-coverage: **RAG-07** fully delivered. ROADMAP Phase-5 Success-Criterion **SC-5** satisfied.

## Boundary-check (Phase-5 design-only discipline)

| Check                                                  | Result                                                                                |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| No new Python dependencies added                       | ✓ (requirements-dev.txt + pyproject.toml unchanged; verification used existing PyYAML) |
| No new code paths / runtime services                   | ✓ (only YAML + Markdown delivered; no Python under evaluation/)                       |
| No edits to `instances/` tree                          | ✓ (Phase-3 validators still pass by inheritance)                                      |
| No edits to `.planning/design/RAG_PIPELINE.md`         | ✓ (that file is plan 05-01's deliverable; will reference queries.yaml when written)   |
| No edits to `scripts/exporters/to_ragflow.py`          | ✓ (that file is plan 05-03's deliverable)                                             |

## Deviations from Plan

None — plan executed exactly as written.

The only minor gloss: 6 OOS queries instead of the strict ≥3 minimum, providing safety margin and exercising 6 distinct OOS sub-categories (trivial / aviation-adjacent / adversarial / corpus-absent-aircraft / off-domain / adjacent-regulation). This was already permitted by the plan's "recommend 4-6" guidance under Task 3.

## Authentication gates

None.

## Known Stubs

None. All queries reference real Document URIs and real document content (FAR §25.1309 clauses, NASA TM-2014-218175 sections, NTSB AAR-09/03 findings) — no placeholders, no TODO markers, no stub data.

## Phase-7 Implementer Handoff

**Phase-7 implementer: this is the eval contract — `python -c 'import yaml; yaml.safe_load(open("evaluation/queries.yaml"))'` is your sanity gate.**

What you'll find in `evaluation/`:

- `queries.yaml` — 30 query records ready to feed your retrieval harness. Schema is documented in `evaluation/README.md` `## Schema`.
- `README.md` — your consumption contract. The `## Phase 7 Consumption Contract` section has the pseudocode and acceptance gates (recall@5≥0.80, cross_lingual_recall@5≥0.70, out_of_scope_short_circuit_rate==1.00, citation_accuracy≥0.95).
- Add `evaluation/results/` (gitignored) for per-run metric JSON.
- Add `evaluation/harness/run_eval.py` for the runner.
- Do NOT renumber `query_id`s (stable across phases).
- Do NOT remove queries — extend with `q-031+` only.
- When you add ZH-source documents in Phase 6, add EN→ZH cross_lingual queries to balance the symmetry.

## Self-Check: PASSED

Files exist:
- ✓ `evaluation/queries.yaml` (322 lines)
- ✓ `evaluation/README.md` (210 lines)

Commits exist:
- ✓ `335a359` — docs(05-02): add evaluation/README.md
- ✓ `5a0e2d1` — feat(05-02): add evaluation/queries.yaml — first 18 baseline queries
- ✓ `46eb286` — feat(05-02): append cross_lingual + out_of_scope queries to reach 30 total

All schema invariants verified via PyYAML safe_load + counter assertions.
yamllint exits 0 (level=warning only).
RAG-07 verifier (verbatim from 05-VALIDATION.md): PASS.

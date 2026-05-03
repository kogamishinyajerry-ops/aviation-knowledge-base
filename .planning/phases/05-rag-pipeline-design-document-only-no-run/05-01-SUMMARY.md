---
phase: 05-rag-pipeline-design-document-only-no-run
plan: 01
subsystem: rag-pipeline-design
tags: [rag, design, chunking, embedding, retrieval, citation, guardrail, cross-lingual, phase-5]
requires:
  - .planning/research/STACK.md (RAGFlow v0.25.1, BGE-M3, OpenDataLoader-PDF version pins)
  - .planning/research/ARCHITECTURE.md (Pattern 4 Git-Bridge Sync; Integration Boundaries)
  - .planning/research/PITFALLS.md (Pitfalls 6, 7, 8, 9)
  - .planning/REQUIREMENTS.md (RAG-01..06)
  - docs/regulations/far-25-1309/processed.md (concrete §-clause structure)
  - docs/cfd-papers/nasa-tm-2014-218175/processed.md (equation/figure layout)
  - docs/accident-reports/ntsb-aar-09-03/processed.md (factor table structure)
  - instances/entities/expert-note/canonical-example.yaml (i18n + URI scheme)
provides:
  - .planning/design/RAG_PIPELINE.md (authoritative Phase-5 RAG pipeline design)
affects:
  - Phase 6 (deployment plan — consumes §3 embedding + §6 guardrail thresholds for service config)
  - Phase 7 (RAG implementation — implements §2 chunker, §4 retrieval orchestrator, §5 citation injection, §6 guardrail in code)
tech-stack:
  added: []                # design only — no new dependencies
  patterns:
    - "[CITE:c_<8hex>] system-side citation token (sha256 truncated, opaque to LLM)"
    - "Three-step inject → resolve → validate citation flow (Pitfall 8 structural defense)"
    - "Hard pipeline branch guardrail (Pitfall 9 structural defense — LLM unreachable on no-context)"
    - "Atomic chunk rule with regulation-clause regex `§\\s*\\d+\\.\\d+(\\([a-z]\\))?(\\(\\d+\\))?`"
    - "BGE-M3 multilingual + bilingual glossary expansion weight 0.3 (Pitfall 7 defense)"
    - "RRF fusion (k=60) over vector top-20 + BM25 top-20 (AeroPower-RAG-validated)"
    - "Bilingual canned no-context response (ZH + EN both required)"
key-files:
  created:
    - .planning/design/RAG_PIPELINE.md (834 lines)
    - .planning/phases/05-rag-pipeline-design-document-only-no-run/05-01-SUMMARY.md
  modified: []
decisions:
  - "v1 PDF parser = RAGFlow 0.25.1 OpenDataLoader-PDF default; DeepDoc OCR + MinerU deferred to v2 per CLAUDE.md Out-of-Scope"
  - "v1 default embedding = BGE-M3 (568M, 8192 ctx, multilingual); v1 default reranker = bge-reranker-v2-m3"
  - "Chunk size 512 tokens / overlap 64 / soft max 1024 / atomic-block override up to 2048"
  - "Atomic chunks: tables, $$equations$$, regulation clauses (regex anchor), figure-caption pairs"
  - "Hybrid retrieval: vector top-20 + BM25 (k1=1.2, b=0.75, bigram=true) top-20 + RRF (k=60); rerank to top-5 with score_threshold 0.5"
  - "Synonym expansion weight 0.3 (AeroPower-RAG-validated, locked)"
  - "Citation token format: [CITE:c_<8hex>] where 8hex = first 8 chars of sha256(chunk_text + chunk_index)"
  - "LLM is FORBIDDEN to author citations; system prompt verbatim text included"
  - "Post-generation citation validator REJECTS (not warns) on unresolved tokens or no-citation-with-context"
  - "Guardrail thresholds: min_chunk_score=0.5, min_chunks_required=2 (locked v1 defaults)"
  - "Canned no-context response is verbatim bilingual (ZH + EN); both required, neither removable"
  - "Answer.llm_called audit field distinguishes 3 ops states (no LLM / LLM-called-rejected / LLM-called-accepted)"
  - "Cross-lingual: BGE-M3 native + glossary expansion + entity i18n field uploaded as RAGFlow meta_fields"
  - "Phase 7 must hit cross_lingual_recall@5 ≥ 70% (hard floor; no candidate ships below)"
  - "v1 only indexes wiki/**.md + docs/**/processed.md; YAML records surface via citation back-links per ARCHITECTURE.md Pattern 4"
metrics:
  start_time: "2026-05-03T (worktree pre-task)"
  end_time: "2026-05-03T (post-task)"
  tasks_completed: 4
  tasks_total: 4
  files_created: 1                # RAG_PIPELINE.md
  files_modified: 0
  lines_of_design: 834
  commits: 4
  deviations: 0
---

# Phase 5 Plan 01: RAG Pipeline Design Summary

Authored `.planning/design/RAG_PIPELINE.md` (834 lines) — the single authoritative design contract covering chunking, embedding selection, hybrid retrieval, citation injection, no-context guardrail, and cross-lingual retrieval — pinned to RAGFlow v0.25.1 + BGE-M3 + OpenDataLoader-PDF per `STACK.md`, defusing Pitfalls 6 / 7 / 8 / 9 by structural design (not by hope).

## What Shipped

A single Markdown design document at `.planning/design/RAG_PIPELINE.md` with:

- **Top-level frontmatter** pinning Phase 5 / v0.1.0 / Phase 7 amendment policy.
- **`> ## AI 接力开发指南` block** mirroring the `scripts/validators/README.md` + `PRD_v0.md` pattern: 5-minute stranger test checklist, Locked-vs-Directional table (15 rows), how-to-read / how-to-update sections.
- **§1 Scope and Non-Goals** — 7 in-scope items, 7 out-of-scope items (deferred), 3 non-goal commitments (will not be added in v1).
- **§2 Chunking Strategy** (RAG-01) — RAGFlow 0.25.1 OpenDataLoader-PDF default; atomic-chunk rules for tables / `$$equations$$` / regulation clauses (regex `§\s*\d+\.\d+(\([a-z]\))?(\(\d+\))?`) / figure-caption pairs; chunk size 512/overlap 64/atomic-override 2048; per-corpus configs (regulations / cfd-papers / accident-reports) keyed to actual `processed.md` files.
- **§3 Embedding Selection** (RAG-02) — BGE-M3 + bge-reranker-v2-m3 default per STACK.md; mini-benchmark plan (3 candidates × 4 metrics × `evaluation/queries.yaml` baseline); 4-rule decision criteria with cross-lingual recall ≥ 70% hard floor.
- **§4 Hybrid Retrieval** (RAG-03) — Vector top-20 + BM25 (k1=1.2, b=0.75, bigram=true) top-20 + RRF (k=60); synonym expansion weight 0.3 bilingual; bge-reranker-v2-m3 with score_threshold=0.5 feeding §6.
- **§5 Citation Injection** (RAG-04) — `[CITE:c_<8hex>]` token format locked; verbatim system prompt forbidding self-authored citations; `render_citations()` resolver pseudocode; `validate_answer_citations()` post-validator that REJECTS on unresolved or no-citation-with-context.
- **§6 Guardrail** (RAG-05) — `min_chunk_score=0.5` and `min_chunks_required=2` locked thresholds; verbatim bilingual canned response (ZH + EN); `answer_query()` pseudocode showing the hard pipeline branch BEFORE `llm.generate()`; `Answer.llm_called` audit field for 3-state ops distinction.
- **§7 Cross-lingual Retrieval** (RAG-06) — BGE-M3 native multilingual (no translation hop); glossary expansion plan (≥50 seed bilingual terms, Phase 6 AIH-04); entity i18n field uploaded as RAGFlow `meta_fields` at index time.
- **§8 ASCII Pipeline Diagram** — ingest-time (out-of-band) + 6-stage query-time flow; stage-to-section map table.
- **§9 Open Questions** — 9 explicit Phase 7+ deferrals.
- **§10 References** — repo source documents, external (RAGFlow / BGE-M3 / parser benchmarks), prior projects (AeroPower-RAG / cfd-harness-unified / H-Darrieus Case 3).

## REQ-ID Coverage

| REQ-ID  | Section(s)         | Status                                                                                                            |
|---------|--------------------|-------------------------------------------------------------------------------------------------------------------|
| RAG-01  | §2.1, §2.2, §2.4   | OpenDataLoader-PDF + atomic rules (tables/equations/clauses) + per-corpus configs — DONE                          |
| RAG-02  | §3.1, §3.2, §3.3   | BGE-M3 + bge-reranker-v2-m3 default + 3-candidate benchmark plan + 4-rule decision criteria — DONE               |
| RAG-03  | §4.1, §4.2, §4.3   | Vector + BM25 + RRF + synonym weight 0.3 + reranker — DONE                                                       |
| RAG-04  | §5.1, §5.2, §5.3   | `[CITE:c_<8hex>]` + render + validate (3-step structural Pitfall-8 defense) — DONE                              |
| RAG-05  | §6.1, §6.2, §6.3   | Locked thresholds + bilingual canned response + LLM-not-called proof — DONE                                       |
| RAG-06  | §7.1, §7.2, §7.3   | BGE-M3 multilingual + glossary plan + entity i18n meta_fields — DONE                                              |

## Pitfall Defenses (PITFALLS.md cross-reference)

| Pitfall | Failure mode (PITFALLS.md)              | Defense in this doc                                                            |
|---------|------------------------------------------|--------------------------------------------------------------------------------|
| 6       | Chunking breaks tables/equations         | §2.2 atomic-chunk rules — tables/equations/clauses preserved structurally      |
| 7       | Embedding doesn't recognize ZH↔EN terms  | §7 BGE-M3 multilingual + glossary 0.3 + entity i18n at index time             |
| 8       | Citation hallucination (LLM invents pgs) | §5 inject → resolve → validate; LLM only sees opaque `chunk_id`s              |
| 9       | Guardrail bypass on retrieval failure    | §6.3 hard pipeline branch — `llm.generate()` unreachable on no-context        |

## Files Created / Modified

**Created:**
- `.planning/design/RAG_PIPELINE.md` — 834 lines
- `.planning/phases/05-rag-pipeline-design-document-only-no-run/05-01-SUMMARY.md` — this file

**Modified:** none (Phase 5 design-only discipline preserved — instances/, scripts/, ontology/ all untouched).

## Commits

| Hash      | Message                                                                                  |
|-----------|------------------------------------------------------------------------------------------|
| `d8853a3` | docs(05-01): scaffold RAG_PIPELINE.md skeleton with AI handoff guide                     |
| `d2a6f62` | docs(05-01): fill §2 chunking + §3 embedding + §4 hybrid retrieval                       |
| `4520152` | docs(05-01): fill §5 citation injection + §6 guardrail (Core Value defenders)            |
| `956d7a9` | docs(05-01): fill §7 cross-lingual + §8 diagram + §9 open Qs + §10 refs                  |

(Final metadata commit — adding this SUMMARY.md — will follow after self-check.)

## Deviations from Plan

**None — plan executed exactly as written.**

All four task `<verify><automated>` blocks passed on first run:
- Task 1: ≥80 lines + 10 section headers + AI 接力指南 → actual 207 lines.
- Task 2: 8 token grep checks + ≥250 lines → actual 429 lines.
- Task 3: 10 token grep checks → all present.
- Task 4: 7 token grep checks + ≥450 lines + Python section assertion → actual 834 lines.

## Authentication Gates

None encountered. Pure local file authoring.

## Phase-5 Boundary Compliance

| Boundary check (per `05-VALIDATION.md`)                          | Status                                                                                                          |
|------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| No new Python deps                                               | OK — no `requirements*.txt` / `pyproject.toml` modified                                                          |
| No real RAGFlow HTTP call attempted                              | OK — pseudocode only; `requests`/`httpx` not imported in any script changed                                      |
| AI 接力开发指南 included                                          | OK — top-of-doc block, ≥30 lines, mirrors PRD_v0.md style                                                        |
| Phase-3 validators still pass on `instances/`                    | Untouched — `instances/` not modified by this plan (regression-safe by construction)                            |
| Plan touches only `.planning/design/RAG_PIPELINE.md`             | OK — single file modified                                                                                         |

## Threat Flags

None. This plan creates a single Markdown design document with no executable code paths, no network endpoints, no auth surfaces, no schema changes at trust boundaries. All security-relevant content is references to existing controls (confidentiality filter at ingest per plan 05-03; YAML record indexing explicitly out of scope).

## Phase 7 Implementer Note

> **Phase-7 implementer: read this doc + STACK.md + PITFALLS.md before writing any RAGFlow code.**

Specifically:
- Implement `scripts/rag/chunker_postprocess.py` per §2.2 atomic-rule pass.
- Implement `scripts/rag/orchestrator.py` per §6.3 `answer_query()` pseudocode (the LLM-not-called branch is non-negotiable).
- Implement `scripts/rag/citations.py` per §5.2 + §5.3 (`render_citations` + `validate_answer_citations`).
- Run §3.2 mini-benchmark before flipping default embedding model; amend §3.3 with measured numbers and bump RAG_PIPELINE.md to v0.2.0.
- Phase 7 acceptance test: 100% of `evaluation/queries.yaml` `out_of_scope` queries return `llm_called=False` (per §6.3).

## Self-Check: PASSED

- **Files claimed:**
  - FOUND: `.planning/design/RAG_PIPELINE.md` (834 lines)
  - FOUND: `.planning/phases/05-rag-pipeline-design-document-only-no-run/05-01-SUMMARY.md`
- **Commits claimed:**
  - FOUND: `d8853a3` (skeleton + AI handoff guide)
  - FOUND: `d2a6f62` (§2 + §3 + §4)
  - FOUND: `4520152` (§5 + §6 — Core Value defenders)
  - FOUND: `956d7a9` (§7 + §8 + §9 + §10)
- **Stub scan:** no remaining `TBD` / `placeholder` / `TODO` / `FIXME` markers in `RAG_PIPELINE.md` (the only `TBD` reference is a literal-string mention inside the `<task>` description-quoting context of an `<action>` block, which has been replaced; final scan confirms clean).
- **Aggregate `<verification>` block (per plan top-of-file, 10 items):**
  - [x] `wc -l` ≥ 450 → 834 lines
  - [x] All 10 numbered sections present (Python `ast`-style assertion confirmed)
  - [x] AI 接力开发指南 block present near top
  - [x] RAGFlow v0.25.1 + BGE-M3 + bge-reranker-v2-m3 + OpenDataLoader-PDF cited verbatim from STACK.md
  - [x] `[CITE:c_<8hex>]` token format defined; render + validator pseudocode present
  - [x] Hard threshold values present (`min_chunk_score = 0.5`, `min_chunks_required = 2`)
  - [x] Bilingual canned no-context response present (ZH + EN strings)
  - [x] Pitfalls 6, 7, 8, 9 explicitly cited by number
  - [x] ASCII pipeline diagram contains all 6 stages from query → render
  - [x] No `pip install` / `npm install` Phase-5 install instructions (boundary check passed)

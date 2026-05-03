# Roadmap: Aviation Knowledge Base MVP

**Created:** 2026-05-03
**Granularity:** standard
**Strategy:** Schema-first build order (per research/SUMMARY.md). Cannot validate what has no schema; cannot write demo data before validators exist; cannot design RAG chunking before concrete documents exist.

## Overview

Six phases deliver an engineering-grade aviation knowledge base baseline: repo skeleton + PRD v0 directional → ontology schema v0.1.0 → live validators + CI → demo data + document import spec → RAG pipeline design (document-only, no run) → deployment plan + PRD v1 final + AI handoff polish + future roadmap. Every phase produces an artifact the next phase consumes. No real services started in v1; the deliverable is a schema-versioned, audit-traceable, AI-handoff-ready foundation. Phases 2 and 5 carry research budget (`/gsd-research-phase`) before planning; phases 1, 3, 4, 6 skip research because patterns are standard and predecessors set the constraints.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Repo Skeleton + Git Baseline + PRD v0** - Locked directory layout, LFS, CI no-op stubs, pre-commit, AI handoff README, directional PRD
- [ ] **Phase 2: Ontology Schema v0.1.0** - Base + 17+4 entity schemas + 13+5 relation schemas, mandatory provenance/confidence, schema versioning (RESEARCH BEFORE PLAN)
- [ ] **Phase 3: Validators + CI Active** - `validate.py` + per-rule validators, fixture suite, pytest, GitHub Actions runs full validation
- [ ] **Phase 4: Demo Data + Document Import Spec** - ≥1 instance per entity type, ≥3 relations, ≥3 source documents, supersession + AI-pending demo, document import workflow
- [ ] **Phase 5: RAG Pipeline Design (document-only)** - Chunking-with-tables, BGE-M3 selection, hybrid retrieval, citation injection, no-context guardrail, eval ≥30 queries (RESEARCH BEFORE PLAN)
- [ ] **Phase 6: Deployment Plan + PRD v1 + Roadmap + AI Handoff Polish** - docker-compose draft, topology diagram, env example, future-phase triggers, final PRD, R12 polish across all docs

## Phase Details

### Phase 1: Repo Skeleton + Git Baseline + PRD v0
**Goal**: Lock the repo layout, baseline tooling, and directional PRD so every later phase has a stable home and a north star.
**Depends on**: Nothing (first phase)
**Requirements**: REPO-01, REPO-02, REPO-03, REPO-04, REPO-05, PRD-01
**Success Criteria** (what must be TRUE):
  1. Top-level directory tree matches `research/ARCHITECTURE.md` repo structure exactly (`ontology/`, `instances/`, `docs/`, `wiki/`, `deploy/`, `scripts/`, `tests/`, `evaluation/`, `process-log/`) — `tree -L 2 -d` output reviewable in PR
  2. `.gitattributes` configures Git LFS for `*.pdf`, `*.docx`, `*.xlsx`, `*.pptx` BEFORE any source document is committed (verified by attempting to add a sample binary)
  3. `README.md` opens with "AI 接力开发指南" header and a fresh Claude/Codex/DeepSeek session can describe project structure, current phase, and next action within 5 minutes of reading it
  4. GitHub Actions workflow runs to green on a no-op PR (lint job, schema-validation stub, link-check stub all pass without failing the build)
  5. `pre-commit run --all-files` runs `yamllint`, `check-jsonschema`, `check-merge-conflict`, `end-of-file-fixer` on a sample commit and exits 0
  6. `.planning/design/PRD_v0.md` exists with users, scope, non-goals, success metrics, deliverable list — sufficient for downstream phases to refer back when scoping
**Plans**: 5 plans
  - [ ] 01-01-PLAN.md — Repo skeleton + .gitignore + .gitattributes (LFS) + exporter stubs
  - [ ] 01-02-PLAN.md — README.md with AI 接力开发指南 + 5-minute stranger test
  - [ ] 01-03-PLAN.md — pre-commit config + .yamllint (pinned versions)
  - [ ] 01-04-PLAN.md — GitHub Actions CI baseline (lint + stub jobs)
  - [ ] 01-05-PLAN.md — PRD v0 directional + .planning/design/ scaffold
**Research needed**: No (standard patterns)

### Phase 2: Ontology Schema v0.1.0
**Goal**: Define every entity type, relation type, vocabulary, and provenance/confidence/versioning rule as schema-enforced contracts before a single instance file is written.
**Depends on**: Phase 1
**Requirements**: ONT-E-01, ONT-E-02, ONT-E-03, ONT-E-04, ONT-E-05, ONT-E-06, ONT-E-07, ONT-E-08, ONT-E-09, ONT-E-10, ONT-E-11, ONT-E-12, ONT-E-13, ONT-E-14, ONT-E-15, ONT-E-16, ONT-E-17, ONT-E-18, ONT-E-19, ONT-E-20, ONT-E-21, ONT-E-22, ONT-R-01, ONT-R-02, ONT-R-03, ONT-R-04, ONT-R-05, ONT-R-06, ONT-R-07, ONT-R-08, ONT-R-09, ONT-R-10, ONT-R-11, ONT-R-12, ONT-R-13, ONT-R-14, ONT-R-15, ONT-R-16, ONT-R-17, ONT-R-18, ONT-R-19, PROV-01, PROV-02, PROV-03, PROV-04, PROV-05, PROV-06, VER-01, VER-02, VER-03, VER-04
**Success Criteria** (what must be TRUE):
  1. All 17 baseline entity schemas + ADR-resolved decisions for the 4 research-recommended entities (Material, TestCase/TestReport, Configuration/EffectivityRange, Person/Organization) self-validate against JSON Schema Draft 2020-12 (`check-jsonschema --check-metaschema`)
  2. All 13 baseline relation schemas + ADR-resolved decisions for the 5 research-recommended relations (interfaces_with, complies_with, has_revision, applicable_during_phase, generated_by) self-validate
  3. `_meta.schema.json` makes `provenance.method` (enum: `human`/`ai_extracted`/`hybrid_reviewed`), `confidence.{score,rationale}`, structured `source.{document_id,locator,retrieval}` mandatory on every entity and relation — verified by feeding a record missing any field and seeing validation reject
  4. A test fixture record with `provenance.method=ai_extracted` AND `confidence.score=0.90` AND no `reviewer` is REJECTED by the schema (H-Darrieus failure-mode lock per PROV-04)
  5. `ontology/VERSION` reads `0.1.0`, `ontology/CHANGELOG.md` documents the initial schema set, every record carries `schema_version`, `migrations/` directory contains a placeholder pattern doc
  6. URI scheme ADR (`aviationkb://<type>/<slug>@<version>` and `<type-prefix>:<kebab-slug>`) committed in `.planning/decisions/`; S1000D Issue 6 DMC reservation documented in `ontology/mappings/`
**Plans**: TBD
**Research needed**: YES — entity/relation additions, S1000D Issue 6 DMC field shape, triple export format choice (run `/gsd-research-phase 2` before `/gsd-plan-phase 2`)

### Phase 3: Validators + CI Active
**Goal**: Make every schema rule, ID format, broken-ref check, and provenance constraint enforceable in CI so no malformed record reaches main.
**Depends on**: Phase 2
**Requirements**: VAL-01, VAL-02, VAL-03, VAL-04, VAL-05
**Success Criteria** (what must be TRUE):
  1. `python scripts/validate.py` (master entrypoint) runs schema validation, ID format check, broken-ref check, provenance check, and link check in a single pass on the entire `instances/` tree and exits 0 on a clean repo
  2. Per-rule validators under `scripts/validators/` (`schema.py`, `ids.py`, `relations.py`, `provenance.py`, `links.py`) are independently importable as Python modules with documented public functions
  3. `tests/fixtures/{valid,invalid}/` covers every entity type, every relation type, the `_pending/` promotion path, a supersession chain, and the `ai_extracted`-without-reviewer rejection — pytest reports ≥1 fixture per category
  4. `pytest tests/test_validators.py` runs all validator self-tests green; injecting a deliberately broken fixture causes the targeted test to fail (sanity check)
  5. GitHub Actions CI runs `validate.py` + `pytest` on every push and PR, blocks merge on failure, and the no-op PR from Phase 1 still passes after this phase lands
**Plans**: TBD
**Research needed**: No

### Phase 4: Demo Data + Document Import Spec
**Goal**: Populate canonical instances covering every entity type plus the document-import workflow so the schema is exercised by real-shaped data before RAG design begins.
**Depends on**: Phase 3
**Requirements**: DOC-01, DOC-02, DOC-03, DOC-04, DEMO-01, DEMO-02, DEMO-03, DEMO-04, DEMO-05, DEMO-06, DEMO-07
**Success Criteria** (what must be TRUE):
  1. At least one entity instance exists for every entity type accepted in Phase 2 (17 baseline + Phase-2-accepted research additions); all instances pass `validate.py` green
  2. At least three relation instances exist spanning at least three different relation types; all reference resolvable subject/object entities (broken-ref check passes)
  3. At least three source documents under `docs/<domain>/<doc-id>/` (one regulation, one CFD paper, one accident report) each ship `source.{pdf,md}` + `processed.md` + `metadata.yaml` with all DOC-02 mandatory fields populated
  4. One ExpertNote instance demonstrates the canonical provenance/source/confidence pattern (cited as the worked example in `AI 接力开发指南` of `docs/README.md`)
  5. One supersession demo (`RegulationClause` with `status: superseded` + `superseded_by` pointing to the active replacement clause), one AI-extracted record in `instances/_pending/` (verified NOT in canonical via grep), one bilingual entity using `i18n: { zh, en }`
  6. `docs/README.md` documents the manual + scripted import workflow, who reviews, where AI-extracted entities go, and the `confidentiality` gating rule (`restricted`/`itar_ear` flagged as not-ingested-by-default)
**Plans**: TBD
**Research needed**: No (light glossary source verification handled inline)

### Phase 5: RAG Pipeline Design (document-only, no run)
**Goal**: Specify chunking, embedding, retrieval, citation, and guardrail behavior in design documents — no real services started — so deployment topology in Phase 6 has concrete inputs.
**Depends on**: Phase 4
**Requirements**: RAG-01, RAG-02, RAG-03, RAG-04, RAG-05, RAG-06, RAG-07, RAG-08
**Success Criteria** (what must be TRUE):
  1. `.planning/design/RAG_PIPELINE.md` documents the chunking strategy with explicit table-as-atomic-chunk preservation (RAGFlow OpenDataLoader-PDF backend), citing RAGFlow 0.25.1 official behavior verified during Phase 5 research
  2. Embedding selection rationale ships BGE-M3 + bge-reranker-v2-m3 as defaults with a reproducible mini-benchmark plan against nomic-embed-text and multilingual-e5-large; cross-lingual ZH/EN test rationale documented per AeroPower-RAG findings
  3. Citation injection spec mandates system-side `[CITE:chunk_id]` token injection (LLM cannot self-author citations); render layer resolves chunk_id → (document, page, section, url); a post-generation validator rejects answers whose citations don't resolve to retrieved chunks
  4. Guardrail spec hard-codes the `retrieved_chunks=[] or all-below-threshold → "not found" response without LLM call` short-circuit; an out-of-scope query category exists in the eval set to verify this path
  5. `evaluation/queries.yaml` contains ≥30 evaluation queries with expected source documents, ≥20% table-query questions, and an out-of-scope category — usable as input to a future eval run
  6. `scripts/exporters/to_ragflow.py` skeleton exists with a documented spec covering Git-watch → RAGFlow HTTP API push, idempotent re-upload via content hash, and the `--rebuild` recovery command
**Plans**: TBD
**Research needed**: YES — RAGFlow 0.25.1 table-chunk preservation, HTTP API citation granularity, embedding mini-benchmark scope (run `/gsd-research-phase 5` before `/gsd-plan-phase 5`)

### Phase 6: Deployment Plan + PRD v1 + Roadmap + AI Handoff Polish
**Goal**: Ship the deployment topology (docker-compose draft, no run), the final PRD synthesizing every prior decision, the v2+ trigger conditions, and a polish pass so every design doc passes the 5-minute stranger test.
**Depends on**: Phase 5
**Requirements**: DEP-01, DEP-02, DEP-03, DEP-04, DEP-05, DEP-06, PRD-02, AIH-01, AIH-02, AIH-03, AIH-04, ROAD-01, ROAD-02
**Success Criteria** (what must be TRUE):
  1. `deploy/docker-compose.yml.draft` defines Wiki.js 2.5.314 + Postgres 16 + RAGFlow 0.25.1 + Caddy reverse proxy with the "DRAFT — NOT FOR PRODUCTION" header; `deploy/.env.example` lists all required env vars with no hardcoded secrets; topology diagram (Mermaid or ASCII) shows Git ↔ Wiki.js ↔ RAGFlow ↔ Caddy data flow
  2. `deploy/wiki-git-storage.md` documents the Wiki.js Git storage scope as `wiki/` ONLY (never the full repo); `deploy/authentik-phase2.md` documents the future SSO plan with RAGFlow OIDC bug status referenced and the Authentik service commented out in compose; backup/restore note covers Postgres dump + Git push + RAGFlow vector store as rebuildable derivative
  3. `.planning/design/PRD_v1.md` synthesizes all schema/architecture/RAG/deployment decisions, includes per-requirement acceptance criteria, and is signed off in CHANGELOG.md
  4. Every design document under `.planning/design/` carries an "AI 接力开发指南" section listing relevant files, current schema version, glossary entries, open questions, last-touched-by — the 5-minute stranger test passes for at least three sampled design docs after a context-clean break
  5. `process-log/` contains phase-completion entries for phases 1–6 recording AI session, decisions, deviations; `docs/GLOSSARY.md` ships ≥50 bilingual aviation seed entries
  6. `.planning/ROADMAP_FUTURE.md` documents v2+ trigger conditions for GraphRAG, Agent layer, Graph DB backend, OCR pipeline, multi-tenant RBAC, SSO, and decision agent — each with explicit "promote when X" criteria so they don't drift into v1
**Plans**: TBD
**Research needed**: No (light OIDC bug status recheck handled inline)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Repo Skeleton + Git Baseline + PRD v0 | 0/TBD | Not started | - |
| 2. Ontology Schema v0.1.0 | 0/TBD | Not started | - |
| 3. Validators + CI Active | 0/TBD | Not started | - |
| 4. Demo Data + Document Import Spec | 0/TBD | Not started | - |
| 5. RAG Pipeline Design (document-only) | 0/TBD | Not started | - |
| 6. Deployment Plan + PRD v1 + Roadmap + AI Handoff Polish | 0/TBD | Not started | - |

## Coverage Summary

**v1 requirements:** 94 total (counted across all categories in REQUIREMENTS.md)
**Mapped to phases:** 94/94 ✓
**Unmapped:** 0

> Note: REQUIREMENTS.md preamble said "78 total" but the actual count of REQ-IDs across all categories is 94 (REPO 5 + PRD 2 + ONT-E 22 + ONT-R 19 + PROV 6 + VER 4 + VAL 5 + DOC 4 + RAG 8 + DEP 6 + DEMO 7 + AIH 4 + ROAD 2 = 94). The 78 figure was likely from an earlier draft before the research-recommended entity/relation additions (ONT-E-19..22, ONT-R-15..19) were added. Coverage table updated to reflect actual count.

## Notes on Cross-Cutting Requirements

- **R12 / AIH-01..04** is a continuous discipline. AIH-01..04 are formally mapped to Phase 6 (final polish) for traceability, but every preceding phase MUST include the "AI 接力开发指南" section in its deliverables. Phase 6 is the gate where the 5-minute stranger test is run across all docs.
- **PRD split**: PRD-01 (directional v0) is in Phase 1 to give downstream phases a north star. PRD-02 (final v1) is in Phase 6 to synthesize all decisions made along the way.

---
*Roadmap created: 2026-05-03 by gsd-roadmapper*

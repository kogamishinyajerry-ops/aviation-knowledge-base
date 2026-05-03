# Aviation Knowledge Base MVP — Research Summary

**Project:** Aviation Knowledge Base MVP
**Domain:** Engineering-grade structured KB + RAG (Wiki.js + RAGFlow + YAML/JSON Schema + Git)
**Researched:** 2026-05-03
**Confidence:** HIGH (stack + pitfalls); MEDIUM-HIGH (features + architecture)

---

## Executive Summary

This is a **schema-first engineering knowledge base** targeting aviation engineers, airworthiness researchers, and AI coding assistants as future contributors. The product wins or loses on one axis: *provenance + auditability*, not on features. Confluence and Notion already own "pretty editing + collaboration." The differentiating moat is: every fact source-traceable, every AI answer cited, every schema change versioned, every entity tagged human-vs-AI. If any of these fail, the system reduces to another untrustworthy "aviation AI chatbox" — the Core Value explicitly calls this out.

The recommended approach is: **Git as single source of truth, everything else is a derivative**. Wiki.js Postgres is a page cache. RAGFlow's vector store is rebuildable from Git. This pattern — proven in the user's cfd-harness-unified project — eliminates most sync/consistency problems by design. Build order flows strictly from schema dependency: you cannot validate what has no schema, you cannot build demo data before validators exist, and you cannot design RAG chunking strategy before you have concrete documents to reason about. Every phase must deliver a working artifact that the next phase depends on — no speculative design.

The primary risks are not technical (the stack is validated and versions are pinned). They are procedural: (1) free-text `source` fields that look like citations but aren't verifiable, (2) AI-extracted entities promoted to canonical without human review (the H-Darrieus failure mode, first-hand), (3) confidence scores that are guesses rather than calibrated values, and (4) AI handoff context loss when the next Claude/Codex session starts cold. All four can be designed out in Phase 1 (schema) before any data exists — which is the correct time.

---

## Pinned Decisions (Cross-Cutting — Must Survive Into Roadmap)

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | **Wiki.js 2.5.314 + Postgres 16 + RAGFlow 0.25.1** | Pin versions. Wiki.js 3.0 alpha-since-2021. RAGFlow 0.25.1 introduces OpenDataLoader PDF backend (~14× faster, no GPU). |
| 2 | **Git is SSOT** | Wiki.js Postgres = page cache; RAGFlow vector store = derivative, rebuildable via `scripts/exporters/to_ragflow.py --rebuild`. |
| 3 | **Ontology +4 entities** (Material, TestCase, Configuration, Person) and **+5 relations** (interfaces_with, complies_with, has_revision, applicable_during_phase, generated_by) | Research found gaps in user's 17/13 baseline; schema phase evaluates additions. |
| 4 | **URI scheme** `aviationkb://<type>/<slug>@<version>` and internal ID `<type-prefix>:<kebab-slug>` | Stable IDs that survive backend swaps and map to RDF/Neo4j nodes in v2. |
| 5 | **Provenance + confidence MANDATORY schema fields; validator rejects `ai_extracted` with `confidence > 0.85` without human review** | Direct H-Darrieus failure-mode prevention. Schema-enforced, not policy. |
| 6 | **ATA iSpec 2200** referenced as `ata_chapter` field; **S1000D NOT adopted** but `s1000d_dmc` reserved as optional; **AP233 / ISO 10303 avoided** | ATA = lightweight chapter taxonomy. S1000D = 3000-page XML monolith, wrong fit. AP233 even heavier. |
| 7 | **Wiki.js + RAGFlow do NOT talk directly** — all cross-talk via Git; `scripts/exporters/to_ragflow.py` watches Git, pushes to RAGFlow HTTP API | Decoupled lifecycles. Git becomes the audit log. |
| 8 | **SSO deferred** — RAGFlow OIDC has open bugs (#3495 FR + #12568 Keycloak redirect-loop); v1 uses local accounts behind reverse proxy | Attempting SSO in v1 is a time sink with known breakage. |
| 9 | **BGE-M3 + bge-reranker-v2-m3 + OpenDataLoader-PDF** as RAG defaults | BGE-M3 validated on Chinese aviation regs in AeroPower-RAG (recall@3=100%). OpenDataLoader: deterministic, 72 min/10K pages. |
| 10 | **`instances/_pending/` quarantine** for AI-extracted records; canonical promotion requires `provenance.method = hybrid_reviewed` + human `reviewer` + `reviewed_at` | Architectural enforcement of H-Darrieus lesson — directory-level constraint, not workflow suggestion. |

---

## Stack (Pinned)

**Core:**
- Wiki.js **2.5.314** (knowledge portal, Markdown, ZH/EN, KaTeX). 2.x line; 3.0 alpha-since-2021.
- RAGFlow **0.25.1** (RAG ingestion, hybrid retrieval, citation, Q&A UI). OpenDataLoader-PDF default v1 parser.
- PostgreSQL **16.x** (only future-proof Wiki.js DB).
- BGE-M3 (embedding) + bge-reranker-v2-m3 (reranker). CPU-friendly on Apple Silicon (~2GB RAM).
- check-jsonschema 0.37.1 + yamllint 1.38 + pre-commit 3.7 (YAML-first validation).
- JSON Schema Draft 2020-12.
- Docker Engine 24.0+ + Compose 2.26.1+.

**Do NOT use:** Wiki.js 3.0 alpha, MariaDB/MySQL/SQLite/MSSQL (Wiki.js DB), Dify, Neo4j/Nebula (v1), S1000D as primary schema, AP233/ISO 10303, custom Vue/React frontend, OCR (v1), auto-crawlers, RAGFlow OIDC SSO (broken 2026-05), Marker-PDF/DL parsers as default, raw YAML in Wiki.js page bodies, JSON Schema Draft-04/07.

---

## Features (Condensed)

**Table stakes (v1):**
- Structured `source` object — mandatory schema field (never free-text)
- `provenance.method` enum: `human / ai_extracted / hybrid_reviewed`
- `confidence: { score, rationale }` on every entity/relation
- `instances/_pending/` quarantine; canonical promotion requires reviewed promotion
- Hybrid retrieval (vector + BM25 + RRF)
- Citation-mandatory RAG (system injects chunk_id; LLM cannot self-cite; hard refusal if no retrieved chunks)
- `RegulationClause.status: active / superseded / withdrawn`; retrieval defaults to active only
- Schema versioning: semver + CHANGELOG + per-record `schema_version`
- CI: schema validation + broken-ref detector + provenance check
- Stable URI scheme for GraphRAG v2 readiness
- Demo data: ≥1 instance per entity type + supersession example + AI-extraction staging example
- "AI 接力开发指南" section in every design doc (R12)

**Should-have (v1.x differentiators):**
- Confidence-weighted retrieval ranking
- Static knowledge graph HTML view
- Aviation bilingual glossary (≥50 seed terms)
- Triple-export script skeleton (yaml→jsonl-triples)
- Faceted browse index

**Defer to v2+:** GraphRAG layer, conflict-detection automation, graph-DB backend, OCR, multi-tenant RBAC, SSO, decision agent.

**Anti-features (deliberately NOT building):** real-time collab editing (Wiki.js owns this poorly; not a moat), LLM self-citation, auto-translation without review, inline code execution, free-text source fields, retrieval that crosses superseded regs without flag.

---

## Architecture (Component Map)

**Governing principle:** Git holds truth. Wiki.js Postgres = page cache. RAGFlow vector store = derivative.

| Component | Tier | Owns |
|-----------|------|------|
| Git repo | 1 (canonical) | Schemas, entity/relation YAML, source docs, wiki Markdown |
| Wiki.js | 2 (rendered portal) | Narrative pages; native Git storage module syncs `wiki/` only |
| RAGFlow | 3 (search index) | Vector index; rebuilt from Git via `to_ragflow.py` |
| Postgres | 2 cache | Wiki.js page cache + accounts; nightly pg_dump |

**Repo structure (locked at Phase 1):**

```
ontology/          # JSON Schema files + controlled vocabularies + mappings/ placeholders
  schemas/         # base.schema.json + entity-type schemas + relation-type schemas
  vocabularies/    # ata-chapters.yaml, jurisdictions.yaml, provenance-methods.yaml
  mappings/        # ata-to-iso10303.md, s1000d-dmc-reserved.md (placeholders)
  CHANGELOG.md
  VERSION
instances/
  entities/<type>/<id>.yaml
  relations/<id>.yaml
  _pending/        # AI-extracted quarantine
docs/<domain>/<doc-id>/
  source.{pdf,md}
  processed.md
  metadata.yaml
wiki/              # Wiki.js Git-synced Markdown (UI writes, Git reads) — scope ONLY this dir
deploy/
  docker-compose.yml.draft
  caddy/
  authentik/        # commented out — phase-2+ doc only
scripts/
  validators/      # schema, ids, relations, provenance, links
  importers/
  exporters/       # to_ragflow.py, to_rdf.py (stub), to_neo4j.py (stub), to_jsonl_triples.py (stub)
tests/
  fixtures/valid/
  fixtures/invalid/
  test_validators.py
evaluation/
  queries.yaml     # ≥30 eval queries with expected sources
.planning/         # GSD planning artifacts
process-log/       # audit trail per user's CLAUDE.md
```

**Three architectural guardrails (hard rules):**

1. Relations are always separate files in `instances/relations/` — never inline fields on entities (this is the most expensive future refactor if violated).
2. Wiki.js Git storage scope is `wiki/` only — never mount the whole repo.
3. All YAML consumers go through `scripts/exporters/` — adding a backend = new exporter, not refactor.

---

## Critical Pitfalls (Top 8 — design-around at Phase 2)

1. **Free-text `source` field** — Schema-enforce structured object: `document_id`, `locator{page,section}`, `retrieval{url,retrieved_at}`, `effective_date`. CI rejects on missing fields. **Never acceptable.**
2. **AI-extracted in canonical without review** — Quarantine at `_pending/`; canonical requires `hybrid_reviewed` + `reviewer` + `reviewed_at`. **Never acceptable.**
3. **Citation injection by LLM, not system** — System injects `[CITE:chunk_id]` tokens; LLM uses those tokens; render layer resolves to (doc, page, section, url); post-gen validator checks every citation maps to a retrieved chunk_id. **Never acceptable.**
4. **Guardrail not firing on empty retrieval** — `retrieved_chunks = []` or all below threshold → hard short-circuit to "not found" response, LLM not called. **Never acceptable.**
5. **Schema evolution without migration scripts** — Every schema bump ships `migrations/<from>_to_<to>.py`. Per-record `schema_version` required.
6. **Regulation supersession chain broken** — `RegulationClause` must have `jurisdiction`, `effective_date`, `superseded_by`, `status`. Retrieval defaults to `status: active`.
7. **Chunking strategy destroys tables** — Aviation docs are table-dense. RAGFlow must preserve tables as atomic chunks. Eval set ≥20% table-query questions.
8. **AI handoff context loss** — Every design doc contains "AI 接力开发指南" section. 5-minute stranger test.

---

## Build Order Recommendation (6 Phases)

| # | Phase | Delivers | Reqs | Research needed? |
|---|-------|----------|------|------------------|
| 1 | Repo Skeleton + Git Baseline | Directory layout, README + AI handoff header, .gitattributes (LFS), CI no-op stubs, exporter stubs | R1 | No (standard) |
| 2 | Ontology Schema v0.1.0 | base + 17+3 entity + 13+3 relation schemas, vocabularies, provenance/confidence mandatory, URI ADR, CHANGELOG, VERSION=0.1.0 | R3, R4, R5, R6 | **Yes** — evaluate +4 entity/+5 relation; verify S1000D Issue 6 DMC |
| 3 | Validators + CI Active | scripts/validate.py, fixture suite, pre-commit, CI gates live | R1 (CI), R3-R6 (enforced) | No (standard) |
| 4 | Demo Data + Doc Import Spec | ≥1 instance/type + ≥3 relations + ≥3 source docs + 1 ExpertNote + 1 supersession + 1 _pending example, docs/README.md, eval seed (≥10 queries) | R7, R10 | Light — bilingual glossary source |
| 5 | RAG Pipeline Design (no run) | Chunking-with-tables spec, BGE-M3 mini-benchmark, hybrid retrieval config, citation injection spec, no-context guardrail, eval ≥30 queries, to_ragflow.py spec+skeleton | R8 | **Yes** — RAGFlow 0.25.1 table-chunk + HTTP API citation granularity |
| 6 | Deployment Plan + Roadmap + AI Handoff Polish | docker-compose.yml.draft (Wiki.js + Postgres + RAGFlow + Caddy), .env.example, topology diagram, Wiki.js git-storage config, Authentik phase-2 doc, ROADMAP_FUTURE.md (GraphRAG/Agent/KG/OCR/RBAC/SSO triggers), R12 polish pass | R2 (PRD), R9, R11, R12 | Light — recheck OIDC bug status |

**Phase ordering rationale:**
- Schema before validators (cannot validate undefined schema)
- Validators before data (else demo data drifts to de-facto schema)
- Data before RAG design (chunking config requires concrete docs)
- RAG design before deployment (embedding/GPU choice feeds compose resources)
- Everything before roadmap polish (trigger conditions need v1 reality)

**Note on R2 (PRD):** PRD is positioned in Phase 6 because it needs the schema/architecture/RAG decisions to be concrete. If user wants the PRD earlier as a directional doc, it can be split into "PRD v0 directional" (Phase 1) + "PRD v1 final" (Phase 6).

---

## Open Questions (with phase resolution)

| # | Question | Resolves at |
|---|----------|------------|
| 1 | S1000D Issue 6 (2024) DMC field shape | Phase 2 (WebFetch verify); low risk, field is optional |
| 2 | RAGFlow 0.25.1 table-chunk preservation behavior | Phase 5 (Context7 + ragflow.io/docs verify) |
| 3 | RAGFlow HTTP API citation granularity (per-sentence vs per-answer) | Phase 5 (determines guardrail+injection design) |
| 4 | Triple export format choice (RDF/Turtle vs JSON-LD vs JSONL `{s,p,o,prov}`) | Phase 2 ADR (recommend JSONL for simplicity) |
| 5 | Aviation bilingual glossary seed (ICAO 9713 / ATA bilingual / CAAC) | Phase 4 |
| 6 | `interfaces_with` vs `requires` boundary semantics | Phase 2 ADR with worked examples |
| 7 | Embedding mini-benchmark (BGE-M3 vs nomic-embed-text vs multilingual-e5-large) | Phase 5 |
| 8 | RAGFlow Apple Silicon ARM image | Phase 6 (deployment doc — workaround if no official image) |
| 9 | Wiki.js ↔ Git two-way sync edge cases (conflicts, large pages) | Phase 6 |
| 10 | LLM choice for RAG (Ollama-local vs Claude/OpenAI API vs hybrid) | Phase 5 design doc |

---

## Roadmap Implications (Direct Guidance to Roadmapper)

1. **Use 6 phases as listed in Build Order Recommendation.** Standard granularity matches this naturally.
2. **Phase 2 + Phase 5 carry research budget.** Both need a `/gsd-research-phase` pass before `/gsd-plan-phase`.
3. **Phases 1, 3, 4, 6 skip research** — patterns are standard and predecessors set the constraints.
4. **R2 (PRD) splits across Phase 1 (directional v0) and Phase 6 (final v1)** — or place fully in Phase 6 if user prefers single-shot.
5. **R12 (AI 接力开发指南)** is a continuous discipline — every phase's deliverables must include the section, with a final polish pass in Phase 6.
6. **Hard quality gates** that must NOT be downgraded: structured `source`, `provenance.method`, `confidence.{score,rationale}`, `_pending/` quarantine, citation injection by system not LLM, no-context guardrail, schema versioning + per-record `schema_version`, supersession fields on RegulationClause.
7. **Anti-pattern guard:** roadmapper must not suggest "build a quick frontend in Phase X" or "spin up Neo4j" — both are out-of-scope per PROJECT.md and reinforced here.
8. **Test for AI handoff:** every phase artifact passes the 5-minute stranger test (a fresh Claude/Codex/DeepSeek session can resume in 5 minutes).

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions verified against GitHub releases + official docs (2026-05). BGE-M3 validated on user's AeroPower-RAG. |
| Features | MEDIUM-HIGH | Generic KB/RAG features HIGH. Aviation ontology gap analysis MEDIUM — based on ATA/S1000D training data, not current Issue 6 spec. |
| Architecture | MEDIUM-HIGH | Wiki.js Git sync, RAGFlow HTTP API, Authentik OIDC verified via official docs. GraphRAG migration path inferred from LinkML/DataHub patterns. |
| Pitfalls | HIGH | Grounded in user's first-hand failures: H-Darrieus hallucination (P2/P8), cfd-harness-unified dual-truth (P10), AeroPower-RAG cross-lingual results (P7). |

**Overall:** HIGH for technology decisions and pitfall prevention. MEDIUM for aviation ontology field names + S1000D mapping details — validate at schema phase.

---

## Sources

**Primary (HIGH):**
- Wiki.js GitHub Releases — v2.5.314 confirmed; 3.0 still alpha
- RAGFlow GitHub Releases — v0.25.1; OpenDataLoader added in 0.25
- RAGFlow HTTP API reference (ragflow.io/docs/http_api_reference)
- Wiki.js Git Storage docs (docs.requarks.io/storage/git)
- Authentik Wiki.js integration guide (integrations.goauthentik.io)
- BGE-M3 model card (huggingface.co/BAAI/bge-m3)
- User's AeroPower-RAG project — recall@3=100% on Chinese aviation regs
- User's MEMORY.md — H-Darrieus Case 3 failure mode

**Secondary (MEDIUM):**
- OpenDataLoader benchmark — 72 min vs 16.5h vs 6 days on 10K pages
- RAGFlow OIDC bug #12568 + FR #3495
- ATA iSpec 2200 chapter taxonomy

**Tertiary (needs phase-specific verification):**
- RAGFlow 0.25.1 table-chunk behavior — Phase 5
- S1000D Issue 6 (2024) DMC field format — Phase 2

---

*Research completed: 2026-05-03*
*Ready for roadmap: yes*
*Next: roadmapper agent reads this file to structure phases and milestones*

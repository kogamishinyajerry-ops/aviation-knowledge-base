# Requirements: Aviation Knowledge Base MVP

**Defined:** 2026-05-03
**Core Value:** 每一条知识都可追溯来源，每一个 AI 回答都有 citation；schema 可演化、版本化、对人类和 AI 都可读。

## v1 Requirements

Requirements for initial release (the 第一阶段 deliverable). Each maps to roadmap phases.

### Repository & CI Baseline

- [ ] **REPO-01**: Project repo has locked directory layout matching architecture spec (`ontology/`, `instances/`, `docs/`, `wiki/`, `deploy/`, `scripts/`, `tests/`, `evaluation/`, `process-log/`)
- [ ] **REPO-02**: Git LFS configured for `*.pdf`, `*.docx`, `*.xlsx`, `*.pptx` via `.gitattributes` before any source document is committed
- [ ] **REPO-03**: Top-level `README.md` includes "AI 接力开发指南" header that lets a fresh Claude/Codex/DeepSeek session resume in <5 minutes
- [ ] **REPO-04**: CI baseline (GitHub Actions workflow) installed with no-op stubs for schema-validation / link-check / yamllint jobs (filled in at validator phase)
- [ ] **REPO-05**: Pre-commit config (`.pre-commit-config.yaml`) initialized; minimum hooks: `yamllint`, `check-jsonschema`, `check-merge-conflict`, `end-of-file-fixer`

### Product Requirements Document (PRD)

- [ ] **PRD-01**: PRD v0 (directional) drafted in Phase 1 — defines users, scope, non-goals, success metrics, deliverable list — gives downstream phases a north star
- [ ] **PRD-02**: PRD v1 (final) at Phase 6 — incorporates all schema/architecture/RAG/deployment decisions; includes acceptance criteria per requirement; signed off in CHANGELOG

### Ontology — Entities (17 baseline + 4 evaluated)

- [ ] **ONT-E-01**: Base entity schema (`entity.base.schema.json`) defines mandatory fields: `id` (URI form), `type`, `version`, `schema_version`, `provenance`, `confidence`, `source`, `tags`, `i18n` (zh/en labels)
- [ ] **ONT-E-02**: Schema for **AircraftModel** (manufacturer, model_designation, type_certificate, configuration_variants, ata_chapter applicability)
- [ ] **ONT-E-03**: Schema for **AircraftSystem** (parent_aircraft_model, ata_chapter, function, criticality_level)
- [ ] **ONT-E-04**: Schema for **Subsystem** (parent_system, ata_subchapter, function)
- [ ] **ONT-E-05**: Schema for **Component** (manufacturer, part_number, mass, dimensions, criticality, ata_chapter)
- [ ] **ONT-E-06**: Schema for **Requirement** (requirement_text, jurisdiction, parent_artifact, type: functional/safety/performance, traceability_id)
- [ ] **ONT-E-07**: Schema for **RegulationClause** (jurisdiction enum: FAA/EASA/CAAC/ICAO/other, document, clause_id, effective_date, status: active/superseded/withdrawn, superseded_by, full_text_zh, full_text_en)
- [ ] **ONT-E-08**: Schema for **Standard** (issuing_body, standard_id, version, effective_date, status, scope)
- [ ] **ONT-E-09**: Schema for **Procedure** (procedure_type, target_system, steps, prerequisites, hazards, references)
- [ ] **ONT-E-10**: Schema for **FailureMode** (affected_component, failure_description, conditions {altitude/airspeed/configuration}, severity, detection_method, effects)
- [ ] **ONT-E-11**: Schema for **MaintenanceTask** (target_component, ata_chapter, interval, prerequisites, tools_required, certification_basis)
- [ ] **ONT-E-12**: Schema for **CFDMethod** (method_class: RANS/LES/DNS/Hybrid, equations, governing_assumptions, validation_status)
- [ ] **ONT-E-13**: Schema for **SimulationCase** (target_geometry, cfd_method_ref, mesh_ref, turbulence_model_ref, boundary_conditions, results_summary, reference_url to NASA TMR / ERCOFTAC / AIAA workshop)
- [ ] **ONT-E-14**: Schema for **MeshRequirement** (target_simulation, y_plus_target, cell_count_min/max, refinement_zones, quality_metrics)
- [ ] **ONT-E-15**: Schema for **TurbulenceModel** (family: SA/k-omega-SST/k-epsilon/RSM/etc, applicability, limitations, references)
- [ ] **ONT-E-16**: Schema for **AccidentCase** (date, location, aircraft_model_ref, phase_of_flight, causal_factors, contributing_factors, lessons_learned, official_report_url)
- [ ] **ONT-E-17**: Schema for **Document** (title, doc_type, language, publication_date, source_url, file_hash, page_count, ata_chapter_tags, confidentiality)
- [ ] **ONT-E-18**: Schema for **ExpertNote** (author, date, topic, content_md, related_entities, confidence, supersedes_note)
- [ ] **ONT-E-19** (research-recommended): Evaluate adding **Material** entity (alloy/composite spec) — accept or reject with rationale in ADR
- [ ] **ONT-E-20** (research-recommended): Evaluate adding **TestCase / TestReport** entity — accept or reject with rationale
- [ ] **ONT-E-21** (research-recommended): Evaluate adding **Configuration / EffectivityRange** entity — accept or reject with rationale
- [ ] **ONT-E-22** (research-recommended): Evaluate adding **Person / Organization** entity — accept or reject with rationale

### Ontology — Relations (13 baseline + 5 evaluated)

- [ ] **ONT-R-01**: Base relation schema (`relation.base.schema.json`) defines mandatory fields: `id`, `type`, `subject` (entity URI), `object` (entity URI), `provenance`, `confidence`, `source`, `valid_from`, `valid_until`
- [ ] **ONT-R-02**: Schema for **part_of** (composition, transitive, with cardinality hint)
- [ ] **ONT-R-03**: Schema for **applicable_to** (regulation/standard → aircraft model/system)
- [ ] **ONT-R-04**: Schema for **constrained_by** (component/system → requirement/regulation)
- [ ] **ONT-R-05**: Schema for **verified_by** (requirement → test/sim case/procedure)
- [ ] **ONT-R-06**: Schema for **derived_from** (requirement/note → parent artifact)
- [ ] **ONT-R-07**: Schema for **supersedes** (regulation/note → older version)
- [ ] **ONT-R-08**: Schema for **cites** (any → Document with locator)
- [ ] **ONT-R-09**: Schema for **causes** (failure_mode → effect, accident_case → causal_factor)
- [ ] **ONT-R-10**: Schema for **mitigated_by** (failure_mode → procedure/component/design)
- [ ] **ONT-R-11**: Schema for **requires** (component → maintenance_task / simulation → mesh)
- [ ] **ONT-R-12**: Schema for **equivalent_to** (NOT for cross-language pairs — handle bilingual via entity `i18n` field per FEATURES.md)
- [ ] **ONT-R-13**: Schema for **conflicts_with** (regulation vs regulation, standard vs standard, with rationale)
- [ ] **ONT-R-14**: Schema for **used_in** (cfd_method/turbulence_model/mesh → simulation_case)
- [ ] **ONT-R-15** (research-recommended): Evaluate adding **interfaces_with** (system ↔ system data/power/mechanical interface) — ADR with `requires` boundary
- [ ] **ONT-R-16** (research-recommended): Evaluate adding **complies_with** (component/design → standard/clause)
- [ ] **ONT-R-17** (research-recommended): Evaluate adding **has_revision** (entity → version-history record)
- [ ] **ONT-R-18** (research-recommended): Evaluate adding **applicable_during_phase** (procedure/req → flight phase)
- [ ] **ONT-R-19** (research-recommended): Evaluate `generated_by` as field on entity vs separate relation — ADR

### Provenance, Confidence, Audit (Quality-Hard Requirements)

- [ ] **PROV-01**: `_meta.schema.json` defines mandatory `provenance` object: `method` enum (`human` | `ai_extracted` | `hybrid_reviewed`), `actor`, `actor_role`, `created_at`, optional `reviewer`, `reviewed_at`, `tool` (e.g. claude-opus-4-7)
- [ ] **PROV-02**: `_meta.schema.json` defines mandatory `confidence` object: `score` (0.0–1.0), `rationale` (≥1 sentence), optional `calibration_method`
- [ ] **PROV-03**: Mandatory `source` object: `document_id` (URI to Document entity), `locator` (`page` and/or `section`), `retrieval` (`url`, `retrieved_at`), `effective_date` for time-sensitive sources
- [ ] **PROV-04**: Validator REJECTS records with `provenance.method = "ai_extracted"` AND `confidence.score > 0.85` AND no `reviewer` — H-Darrieus failure-mode lock
- [ ] **PROV-05**: `instances/_pending/` quarantine directory with same schema requirements; canonical promotion REQUIRES `provenance.method = "hybrid_reviewed"` + populated `reviewer` + `reviewed_at`
- [ ] **PROV-06**: Schema validates `source.document_id` resolves to an existing Document entity (broken-ref check in CI)

### Schema Versioning

- [ ] **VER-01**: `ontology/VERSION` file holds current ontology version (semver, starting `0.1.0`)
- [ ] **VER-02**: `ontology/CHANGELOG.md` records every breaking / non-breaking schema change with date + rationale
- [ ] **VER-03**: Every entity/relation YAML carries `schema_version` field; validator rejects records older than N-1 versions
- [ ] **VER-04**: `migrations/` directory pattern documented (Phase 1 placeholder); migration script convention: `<from>_to_<to>.py` taking YAML → YAML

### Validators & CI

- [x] **VAL-01**: `scripts/validate.py` master entrypoint runs: schema validation, ID format, broken refs, provenance fields, link check (03-01: master CLI + dispatch loop shipped; ids/provenance/relations/links logic filled by Wave-2 plans 03-03/03-04 against the frozen public API)
- [x] **VAL-02**: Per-rule validators under `scripts/validators/` (one file per concern, importable as Python modules) (03-01: all 5 modules importable; schema.py is the only real validator in Wave 1; the other four ship as `return []` stubs filled by 03-03/03-04)
- [ ] **VAL-03**: Test fixtures under `tests/fixtures/{valid,invalid}/` cover: every entity type, every relation type, _pending promotion, supersession chain, ai_extracted-without-reviewer rejection
- [ ] **VAL-04**: `pytest` test suite for validators (`tests/test_validators.py`) — all green required for CI pass
- [ ] **VAL-05**: GitHub Actions CI runs full validate.py + pytest on every push/PR

### Document Import & Metadata

- [ ] **DOC-01**: `docs/` directory convention: `docs/<domain>/<doc-id>/{source.{pdf,md,docx,html}, processed.md, metadata.yaml}`
- [ ] **DOC-02**: Document metadata schema enforces: `title`, `doc_type` enum (regulation / standard / paper / report / manual / accident_report / internal_note), `language` (zh / en / mixed), `source_url`, `publication_date`, `effective_date`, `confidentiality` enum (public / internal / restricted / itar_ear), `domain_tags`, `version`, `file_hash`, `processed_by` (tool used)
- [ ] **DOC-03**: Document import workflow documented in `docs/README.md` — manual + scripted paths, who reviews, where AI-extracted entities go
- [ ] **DOC-04**: Confidentiality field gates ingestion to RAGFlow — `restricted` / `itar_ear` documents flagged, NOT ingested by default

### RAG Pipeline Design (document-only, no run)

- [ ] **RAG-01**: Design doc `.planning/design/RAG_PIPELINE.md` covers chunking strategy with table preservation (RAGFlow OpenDataLoader-PDF backend; tables as atomic chunks)
- [ ] **RAG-02**: Embedding selection — BGE-M3 default + bge-reranker-v2-m3; mini-benchmark plan vs nomic-embed-text / multilingual-e5-large
- [ ] **RAG-03**: Hybrid retrieval config — vector + BM25 + RRF; query expansion plan (synonym dict weight 0.3, ZH/EN cross-language)
- [ ] **RAG-04**: Citation injection spec — system-side `[CITE:chunk_id]` token injection, NOT LLM-self-cite; render layer resolves to (document, page, section, url)
- [ ] **RAG-05**: Guardrail spec — `retrieved_chunks = []` or all below threshold → hard-coded "not found" response, LLM not called; output validator rejects citations not matching retrieved chunks
- [ ] **RAG-06**: Cross-lingual retrieval design — bilingual glossary expansion (≥50 seed terms), entity `i18n` field at index time
- [ ] **RAG-07**: Evaluation set `evaluation/queries.yaml` — ≥30 queries with expected source documents; ≥20% table-query questions; out-of-scope category included
- [ ] **RAG-08**: `scripts/exporters/to_ragflow.py` skeleton + design spec (Git watch → RAGFlow HTTP API)

### Deployment Plan (no execution v1)

- [ ] **DEP-01**: `deploy/docker-compose.yml.draft` topology: Wiki.js 2.5.314 + Postgres 16 + RAGFlow 0.25.1 + Caddy reverse proxy; clearly marked "DRAFT — NOT FOR PRODUCTION"
- [ ] **DEP-02**: `deploy/.env.example` lists all required env vars with placeholders; no hardcoded secrets
- [ ] **DEP-03**: Architecture topology diagram (ASCII or Mermaid) showing Git ↔ Wiki.js ↔ RAGFlow ↔ Caddy data flow
- [ ] **DEP-04**: `deploy/wiki-git-storage.md` documents Wiki.js Git storage module config (scope: `wiki/` only — NEVER full repo)
- [ ] **DEP-05**: `deploy/authentik-phase2.md` documents future SSO plan (commented out in compose); references RAGFlow OIDC bug status
- [ ] **DEP-06**: Backup/restore note covers Postgres dump + Git push + RAGFlow vector store treated as rebuildable derivative

### Demo Data

- [ ] **DEMO-01**: At least 1 instance per entity type (covering all 17 baseline + accepted research-recommended additions)
- [ ] **DEMO-02**: At least 3 relation instances spanning ≥3 different relation types
- [ ] **DEMO-03**: At least 3 source documents (one regulation, one CFD paper, one accident report) with full `metadata.yaml` + `processed.md`
- [ ] **DEMO-04**: One **ExpertNote** demonstrating full provenance / source / confidence pattern as the canonical example
- [ ] **DEMO-05**: One regulation supersession demo — old clause with `status: superseded`, `superseded_by` populated, plus the active replacement
- [ ] **DEMO-06**: One AI-extracted record in `instances/_pending/` showing the staging pattern (must NOT be in canonical)
- [ ] **DEMO-07**: One bilingual entity demonstrating `i18n: { zh, en }` pattern with stable cross-language retrieval keys

### AI Handoff & Documentation Quality (cross-cutting)

- [x] **AIH-01**: Every design document under `.planning/design/` includes "AI 接力开发指南" section listing relevant files, current schema version, glossary, open questions, last-touched-by
- [x] **AIH-02**: 5-minute stranger test passes on all major design docs — verified by re-reading after a context-clean break
- [ ] **AIH-03**: `process-log/` directory pattern set up; phase-completion entries record AI session, decisions, deviations
- [ ] **AIH-04**: Glossary file `docs/GLOSSARY.md` with bilingual aviation terms (≥50 seed entries)

### Roadmap & Future Path

- [ ] **ROAD-01**: `.planning/ROADMAP_FUTURE.md` documents v2+ trigger conditions for: GraphRAG layer, Agent layer, Graph DB backend (Neo4j/Nebula), OCR pipeline, multi-tenant RBAC, SSO, decision agent
- [ ] **ROAD-02**: Each future feature has explicit "promote when X" criteria so it doesn't get dragged into v1

## v2 Requirements

Deferred. Tracked but not in current roadmap.

### GraphRAG / Knowledge Graph

- **GRAPH-01**: RDF/Turtle export pipeline (`scripts/exporters/to_rdf.py` complete implementation)
- **GRAPH-02**: Neo4j or Nebula backend integration with stable URI mapping
- **GRAPH-03**: Hybrid retrieval over graph + vector
- **GRAPH-04**: Graph-aware UI (entity browser with relation traversal)

### Agent Layer

- **AGENT-01**: Tool-use agent for guided ingestion (still human-reviewed promotion)
- **AGENT-02**: Conflict-detection agent (regulation vs regulation, source vs source)
- **AGENT-03**: Staleness detection (regulatory supersession alerts)

### Operational Hardening

- **OPS-01**: SSO / OIDC unification (Authentik) once RAGFlow OIDC bugs resolved
- **OPS-02**: Multi-tenant + role-based access control
- **OPS-03**: Real run of docker-compose with monitoring (Prometheus / Grafana / Loki)
- **OPS-04**: OCR pipeline for scanned PDFs (Tesseract / DeepDoc fallback)
- **OPS-05**: Wiki.js → RAGFlow auto-sync daemon (currently manual via to_ragflow.py)

### Schema / Ontology Maturity

- **MAT-01**: ATA iSpec 2200 mapping table populated for major aircraft systems
- **MAT-02**: S1000D Issue 6 DMC export pipeline (uses reserved `s1000d_dmc` field)
- **MAT-03**: Schema migration tooling (auto-run on version bump)

## Out of Scope

Explicitly excluded for v1. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Dify (agent orchestration platform) | First-stage no agent orchestration; will add only if v2 agent layer outgrows custom code |
| Self-built Vue/React frontend | Wiki.js portal + RAGFlow UI sufficient; custom UI = scope explosion |
| Graph DB backend (Neo4j/Nebula) in v1 | Schema still iterating; YAML sufficient for ≤10K triples; defer to v2 GraphRAG phase |
| Auto-crawlers / scrapers | Quality > volume; v1 is curated import only |
| Decision-making agents (auto-tool-use loops) | Out of scope per Core Value — RAG retrieval-augmented Q&A only |
| Uncited AI answers | Hard NO — guardrail enforced; zero-tolerance hallucination policy |
| OCR / scanned image processing | Text-layer PDF/MD/HTML/DOCX only in v1; OCR adds non-deterministic fail mode |
| Multi-tenant / fine-grained RBAC | v1 single-org admin/reader; defer to v2 if user demand emerges |
| Real-time collaborative editing | Wiki.js owns this poorly; not differentiating; not aviation-specific |
| LLM self-citation | System injects chunks; LLM cannot author citations — prevents page-number hallucination |
| Auto-translation without human review | Aviation translation has legal/safety implications; bilingual is curated |
| Inline code execution | Anti-pattern in KB; security + maintenance burden |
| Real-running docker-compose v1 | v1 ships docker-compose.yml.draft + selection-rationale, not running infra |
| Wiki.js 3.0 | Alpha-since-2021; production unsafe; revisit after stable release |
| RAGFlow OIDC SSO | Open bugs (#3495, #12568) — defer until upstream fixes |
| ATA Spec 100 / S1000D as primary schema | S1000D is XML monolith; ATA Spec 100 is paper-era; we use lightweight `ata_chapter` field referencing iSpec 2200 |
| AP233 / ISO 10303 | Wrong shape (STEP/EXPRESS heavy machinery); not adopted |

## Traceability

Each requirement maps to exactly one phase. Populated by gsd-roadmapper on 2026-05-03.

| Requirement | Phase | Status |
|-------------|-------|--------|
| REPO-01 | Phase 1 | Pending |
| REPO-02 | Phase 1 | Pending |
| REPO-03 | Phase 1 | Pending |
| REPO-04 | Phase 1 | Pending |
| REPO-05 | Phase 1 | Pending |
| PRD-01 | Phase 1 | Pending |
| ONT-E-01 | Phase 2 | Pending |
| ONT-E-02 | Phase 2 | Pending |
| ONT-E-03 | Phase 2 | Pending |
| ONT-E-04 | Phase 2 | Pending |
| ONT-E-05 | Phase 2 | Pending |
| ONT-E-06 | Phase 2 | Pending |
| ONT-E-07 | Phase 2 | Pending |
| ONT-E-08 | Phase 2 | Pending |
| ONT-E-09 | Phase 2 | Pending |
| ONT-E-10 | Phase 2 | Pending |
| ONT-E-11 | Phase 2 | Pending |
| ONT-E-12 | Phase 2 | Pending |
| ONT-E-13 | Phase 2 | Pending |
| ONT-E-14 | Phase 2 | Pending |
| ONT-E-15 | Phase 2 | Pending |
| ONT-E-16 | Phase 2 | Pending |
| ONT-E-17 | Phase 2 | Pending |
| ONT-E-18 | Phase 2 | Pending |
| ONT-E-19 | Phase 2 | Pending |
| ONT-E-20 | Phase 2 | Pending |
| ONT-E-21 | Phase 2 | Pending |
| ONT-E-22 | Phase 2 | Pending |
| ONT-R-01 | Phase 2 | Pending |
| ONT-R-02 | Phase 2 | Pending |
| ONT-R-03 | Phase 2 | Pending |
| ONT-R-04 | Phase 2 | Pending |
| ONT-R-05 | Phase 2 | Pending |
| ONT-R-06 | Phase 2 | Pending |
| ONT-R-07 | Phase 2 | Pending |
| ONT-R-08 | Phase 2 | Pending |
| ONT-R-09 | Phase 2 | Pending |
| ONT-R-10 | Phase 2 | Pending |
| ONT-R-11 | Phase 2 | Pending |
| ONT-R-12 | Phase 2 | Pending |
| ONT-R-13 | Phase 2 | Pending |
| ONT-R-14 | Phase 2 | Pending |
| ONT-R-15 | Phase 2 | Pending |
| ONT-R-16 | Phase 2 | Pending |
| ONT-R-17 | Phase 2 | Pending |
| ONT-R-18 | Phase 2 | Pending |
| ONT-R-19 | Phase 2 | Pending |
| PROV-01 | Phase 2 | Pending |
| PROV-02 | Phase 2 | Pending |
| PROV-03 | Phase 2 | Pending |
| PROV-04 | Phase 2 | Pending |
| PROV-05 | Phase 2 | Pending |
| PROV-06 | Phase 2 | Pending |
| VER-01 | Phase 2 | Pending |
| VER-02 | Phase 2 | Pending |
| VER-03 | Phase 2 | Pending |
| VER-04 | Phase 2 | Pending |
| VAL-01 | Phase 3 — plan 03-01 | Complete |
| VAL-02 | Phase 3 — plan 03-01 (skeleton + schema.py) / 03-03+04 (stubs filled) | Complete (Wave 1 portion) |
| VAL-03 | Phase 3 — plan 03-01 (valid corpus) / 03-02 (invalid corpus) | Partial (valid only) |
| VAL-04 | Phase 3 | Pending |
| VAL-05 | Phase 3 | Pending |
| DOC-01 | Phase 4 | Pending |
| DOC-02 | Phase 4 | Pending |
| DOC-03 | Phase 4 | Pending |
| DOC-04 | Phase 4 | Pending |
| DEMO-01 | Phase 4 | Pending |
| DEMO-02 | Phase 4 | Pending |
| DEMO-03 | Phase 4 | Pending |
| DEMO-04 | Phase 4 | Pending |
| DEMO-05 | Phase 4 | Pending |
| DEMO-06 | Phase 4 | Pending |
| DEMO-07 | Phase 4 | Pending |
| RAG-01 | Phase 5 | Pending |
| RAG-02 | Phase 5 | Pending |
| RAG-03 | Phase 5 | Pending |
| RAG-04 | Phase 5 | Pending |
| RAG-05 | Phase 5 | Pending |
| RAG-06 | Phase 5 | Pending |
| RAG-07 | Phase 5 | Pending |
| RAG-08 | Phase 5 | Pending |
| DEP-01 | Phase 6 | Pending |
| DEP-02 | Phase 6 | Pending |
| DEP-03 | Phase 6 | Pending |
| DEP-04 | Phase 6 | Pending |
| DEP-05 | Phase 6 | Pending |
| DEP-06 | Phase 6 | Pending |
| PRD-02 | Phase 6 | Pending |
| AIH-01 | Phase 6 | Complete |
| AIH-02 | Phase 6 | Complete |
| AIH-03 | Phase 6 | Pending |
| AIH-04 | Phase 6 | Pending |
| ROAD-01 | Phase 6 | Pending |
| ROAD-02 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 94 total (REPO 5 + PRD 2 + ONT-E 22 + ONT-R 19 + PROV 6 + VER 4 + VAL 5 + DOC 4 + RAG 8 + DEP 6 + DEMO 7 + AIH 4 + ROAD 2)
- Mapped to phases: 94/94 ✓
- Unmapped: 0
- Note: Earlier preamble said 78; actual count after research-recommended additions (ONT-E-19..22, ONT-R-15..19) is 94. ROADMAP.md coverage summary documents the discrepancy.

**Phase distribution:**
- Phase 1 (Repo Skeleton + PRD v0): 6 requirements
- Phase 2 (Ontology Schema v0.1.0): 51 requirements
- Phase 3 (Validators + CI Active): 5 requirements
- Phase 4 (Demo Data + Doc Import): 11 requirements
- Phase 5 (RAG Pipeline Design): 8 requirements
- Phase 6 (Deployment + PRD v1 + Roadmap + AIH Polish): 13 requirements

---
*Requirements defined: 2026-05-03*
*Last updated: 2026-05-03 after roadmap traceability mapping*

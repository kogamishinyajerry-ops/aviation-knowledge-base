# Feature Research

**Domain:** Aviation Knowledge Base + RAG-based Engineering Q&A (Wiki.js + RAGFlow + YAML/JSON Schema)
**Researched:** 2026-05-03
**Confidence:** MEDIUM-HIGH (HIGH for generic KB/RAG patterns from Confluence/Notion/RAGAS/Anthropic; MEDIUM for aviation-specific because ATA/S1000D/AP233 cited from training data without Context7 verification — flag for second-pass validation)

---

## Executive Summary

An aviation knowledge base targeting engineers + airworthiness researchers + AI-coding-assistant successors must compete on **provenance + auditability + domain ontology fidelity**, not on generic features. Confluence/Notion already win at "pretty editor + collaboration" — this product cannot. The differentiating axis is: **every fact source-traceable, every AI answer cited, every schema change versioned, every entity tagged human-vs-AI**. The user's PROJECT.md Core Value already locks this in.

The user's 17 entities cover ~85% of the aviation engineering domain but have **3 gaps** (Material/MaterialAllowable, TestCase/TestReport, Configuration/EffectivityRange) and **1 redundancy risk** (MaintenanceTask vs Procedure overlaps). The 13 relations cover ~80% but miss **5 important edge cases** (interfaces_with, complies_with, has_revision, applicable_during_phase, generated_by). All called out below.

Anti-features explicitly respected per user constraint: no Dify/Agent loops, no custom frontend, no graph-DB, no auto-crawler, no OCR v1, no decision agents, no uncited AI output, no multi-tenant RBAC.

---

## Feature Landscape

### Table Stakes (Users Expect These — Missing = Unusable)

#### Knowledge Entry & Curation

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Wiki.js Markdown editor for narrative content | Industry standard for technical wikis; Confluence/Notion set baseline | LOW | Out-of-the-box Wiki.js 2.x. v1: ship as-is. |
| Structured entity entry via YAML files in Git | Schema-validated, diff-able, AI-parseable; engineers expect Git workflow | LOW | One file per entity instance OR one file per entity type with array. Recommend per-instance for diff readability. v1. |
| Human review gate for AI-extracted knowledge | Aviation = safety-critical; no auto-merge of AI extractions allowed | MEDIUM | `provenance.method = ai_extracted` requires `review.reviewed_by` + `review.reviewed_at` before status=published. v1. |
| Distinct human vs AI-extracted entity flag | User's H-Darrieus捏造图表 lesson; safety-critical separation | LOW | `provenance.method` enum: `human` / `ai_extracted` / `hybrid`. Schema-enforced. v1. Already in R5. |

#### Document Ingestion

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| PDF text-layer ingestion | 90% of aviation regs/standards/papers are PDF | MEDIUM | RAGFlow handles natively. Scanned PDFs deferred (OCR is anti-feature v1). v1. |
| DOCX ingestion | Internal engineering reports are DOCX | LOW | RAGFlow supports. v1. |
| Markdown / HTML ingestion | Web-published standards (FAA, EASA portals) | LOW | RAGFlow + manual import. v1. |
| Required metadata schema per document | Provenance is core value; can't trace without metadata | LOW | `title / type / source_url / publication_date / language / confidentiality / domain_tags / version` — already in R7. v1. |
| Source file preservation (original artifact retained) | Audit requires being able to re-derive | LOW | Store original in Git LFS or object storage with hash; cite by hash + path. v1. |
| Chunk-level provenance (which page/section a chunk came from) | Aviation citations need page numbers, clause IDs | MEDIUM | RAGFlow does page-level; need clause-ID extraction for regulations (e.g. "FAR 25.1309(b)(1)"). Differentiator-adjacent. v1 basic, v1.x clause-ID. |

#### Ontology Coverage (Evaluating User's 17 Entities)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| All 17 user-defined entities with JSON Schema | User mandate (R3) | MEDIUM | See "Ontology gap analysis" below — recommend additions. v1. |
| Entity ID stability + URI scheme | Cross-references must survive renames; AI successors need stable refs | LOW | Recommend `aviationkb://<entity_type>/<slug>@<version>`. v1. |
| Mapping fields to ATA Spec 100/iSpec 2200, S1000D DMC, AP233 | Industry-standard codes engineers already use; interop with PLM/MRO | LOW (field) / HIGH (full mapping) | Add optional `external_refs.ata_chapter`, `external_refs.s1000d_dmc`, `external_refs.ap233_id` fields. v1: fields exist; values populated incrementally. |

#### Relations

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| All 13 user-defined relations with schema | User mandate (R4) | MEDIUM | See "Relation gap analysis" below. v1. |
| Bidirectional relation querying (A→B and B→A) | Engineers ask both "what's part of X" and "what is X part of" | LOW | YAML stores one direction; build inverse index at validation/load time. v1. |
| Relation provenance (same `source` + `confidence` as entities) | Same audit principle | LOW | Relations are first-class records, same provenance fields. v1. |

#### Retrieval & Q&A

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Hybrid retrieval (vector + BM25 + RRF) | User's AeroPower-RAG validated this; SOTA baseline 2024-2026 | MEDIUM | RAGFlow has hybrid built-in; tune for ZH/EN aviation. v1. |
| Citation enforcement in every AI answer | Core value; zero hallucination tolerance | MEDIUM | RAGFlow citations + post-hoc validator that rejects answers without ≥1 citation. v1 hard requirement. |
| Multi-language ZH/EN | User audience; aviation is bilingual domain | MEDIUM | RAGFlow supports; need bilingual term glossary. v1. |
| Cross-document synthesis with per-claim citations | Single-doc Q&A is insufficient for engineering | MEDIUM | Standard RAG pattern; ensure each sentence in answer maps to ≥1 chunk. v1. |
| Query expansion (synonyms, abbreviations) | "FAR 25" = "14 CFR Part 25"; "EFCS" = "Electronic Flight Control System" | MEDIUM | AeroPower-RAG already proved value. Build aviation glossary YAML. v1.x (after glossary curated). |

#### Provenance & Audit

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Every entity has `source` field | Core value | LOW | Schema-required. v1. |
| Every entity has `confidence: 0..1` | User mandate (R5) | LOW | Schema field. AI extractions <0.8 flagged for human review. v1. |
| Git as truth store for change history | Standard in engineering; no separate audit log needed | LOW | Already implied by R1. v1. |
| Citation validator in CI | Catches uncited claims before merge | LOW | CI script checks every entity has ≥1 valid `source`. v1. |

#### Schema Versioning

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Semver per schema file | User mandate (R6) | LOW | Already in plan. v1. |
| CHANGELOG.md per schema directory | Standard practice | LOW | v1. |
| Migration scripts for breaking schema changes | Otherwise old data orphaned | MEDIUM | Python or Node scripts; document pattern even if no migrations yet at v1. v1: pattern doc + 1 example skeleton. |
| Backward-compat read window (≥1 minor version) | Engineers can't re-process all data on every change | MEDIUM | Loaders accept current + prior minor; deprecation warnings. v1.x (after first breaking change emerges). |

#### Search & Navigation

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Wiki.js full-text search across narrative pages | Out-of-the-box | LOW | v1. |
| Tag/taxonomy browse | Standard wiki feature | LOW | Wiki.js native + entity `domain_tags`. v1. |
| Faceted browse (by aircraft model / system / regulation) | Engineering domain has natural facets | MEDIUM | Wiki.js doesn't have rich facets; use tag combos OR build a simple static-rendered index page from YAML. v1.x. |

#### Quality Control

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| PR-based review for schema/entity changes | Standard Git workflow + aviation review culture | LOW | v1. |
| Schema validation in CI (JSON Schema) | Already in R1 | LOW | v1. |
| Broken-reference detection (relations pointing to deleted entities) | Easy to break; hard to find later | LOW | CI script. v1. |
| Superseded-regulation flag | Aviation regs evolve; using superseded rule is dangerous | LOW | `status` enum on RegulationClause: `active / superseded / withdrawn`; `supersedes` relation already covers it. v1. |

---

### Differentiators (Competitive Advantage in Aviation Domain)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Per-fact provenance + AI/human distinction baked into schema** | Confluence/Notion can't do this without bolt-on; aviation safety culture demands it | MEDIUM | Already R5. This is THE differentiator. v1. |
| **Aviation ontology with ATA/S1000D mapping fields** | Bridges to existing PLM/MRO/CMS tooling; not just another KB | MEDIUM | Field-level v1; full mapping incremental. v1. |
| **Bilingual ZH/EN with curated aviation glossary** | Western KBs are EN-only; Chinese aviation industry needs both | MEDIUM | Build `glossary/aviation_zh_en.yaml` over time. v1 seed (≥50 critical terms), v1.x expand. |
| **Citation-mandatory RAG (zero uncited answer)** | Many RAG systems are loose; this is enforced | MEDIUM | Guardrail in answer pipeline + visible in UI. v1. |
| **Conflict detection between sources** | Two regs/standards disagreeing is real and dangerous | HIGH | LLM-assisted pairwise comparison on overlapping entities; surface in `conflicts_with` relation with reviewer queue. v2 (defer — too costly v1, but reserve schema slot). |
| **Confidence-weighted retrieval ranking** | Down-rank low-confidence/AI-only chunks | MEDIUM | Use `confidence` field as RRF weight modifier. v1.x. |
| **Schema-as-product: human-readable + AI-parseable + machine-validatable** | Successor AIs (Claude/Codex/DeepSeek) can extend without re-learning | LOW (philosophy) / MEDIUM (execution) | YAML + JSON Schema + glossary + decision log. R12 captures this. v1. |
| **Extension hooks for GraphRAG v2 (entity URIs, stable IDs, relation triples exportable as RDF/JSONL)** | Avoid v2 rewrite | MEDIUM | Schema design choice now: stable URIs + triple-exportable relations. v1 must include export script (`yaml→jsonl-triples`). |
| **Provenance-aware answer rendering (footnotes show: source, confidence, extraction method, retrieval date)** | UI-level transparency engineers will trust | MEDIUM | RAGFlow citation extension. v1.x. |
| **Decision log integration (ADR-style, Notion-mirror pattern from cfd-harness-unified)** | Ontology decisions need their own audit trail | LOW | `.planning/decisions/ADR-*.md`. v1. |
| **Static knowledge graph view (HTML index from YAML)** | Engineers want to see structure without graph-DB | MEDIUM | Generate `graph.html` with vis.js or pyvis from YAML. v1.x (good demo asset). |

---

### Anti-Features (Deliberately NOT Building — Respecting User Exclusions)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Auto-decision Agent loop (Dify-style) | "AI does the work for me" appeal | Aviation safety: agent making tool calls without traceable human-approved chain is unauditable | RAG Q&A only; humans approve every AI extraction. (User constraint.) |
| Custom Vue/React frontend v1 | Looks more "professional" | Time sink; Wiki.js + RAGFlow UIs are sufficient for v1 | Use stock UIs; revisit in v2. (User constraint.) |
| Graph database backend (Neo4j/Nebula) | "Real" knowledge graph | Premature; <10K triples fit in YAML; binds backend before schema stabilizes | YAML + JSON Schema; export to triples/RDF when graph-DB justified. (User constraint.) |
| Auto web crawler | "Just suck in everything" | Aviation sources are licensed/copyrighted (Jeppesen, FAA paid databases); legal risk + noise | Manual + batch import with confidentiality field. (User constraint.) |
| OCR / scanned-document handling v1 | Old aviation docs are scans | Quality gates can't be met v1; OCR errors poison KB | Defer; manual transcription if critical doc; mark `confidentiality.ocr_pending`. (User constraint.) |
| Multi-tenant RBAC | "Enterprise-ready" | Over-engineered for single-org v1 | admin + reader roles; defer fine-grained perms. (User constraint.) |
| Uncited AI answer fallback ("answer if you can, otherwise say I don't know") | Helpfulness | Once you allow even one uncited answer, you're back to chatbot territory | Hard refuse if no citation; return "no source found, please consult X" message. (User constraint.) |
| Real-time collaborative editing of entities | Notion/Confluence parity | Conflicts with PR-review model needed for safety; Git is the truth | Wiki.js for collaborative narrative; entities stay PR-gated. |
| LLM-generated entity definitions without human review | "Bootstrapping speed" | H-Darrieus lesson — AI fabricates plausible-looking aviation data | AI extraction allowed but `status: draft` until human signs off. |
| Auto-translate ZH↔EN entity content | "Bilingual for free" | Aviation terms have legally precise translations; auto-translation is unsafe | Curated bilingual glossary; entity content authored in source language with optional reviewed translation. |
| Inline code execution / notebook integration | "Run CFD simulations from KB" | Out of scope; conflicts with cfd-harness-unified separation | KB references SimulationCase entities; execution stays in cfd-harness-unified. |

---

## Ontology Gap Analysis (User's 17 Entities)

### Coverage Verdict
The 17 cover the **product + safety + verification + simulation** dimensions well. Gaps are in **materials**, **testing**, **configuration management**, and the **information layer about the entities themselves**.

### Recommended Additions (4 entities)

| Entity | Why Add | v1 / Defer |
|--------|---------|-----------|
| **Material** (and/or **MaterialAllowable**) | Aviation engineering is material-driven (Al alloys, composites, titanium); allowables (S-N curves, B-basis) drive certification. Currently no slot. | v1 (just `Material`); `MaterialAllowable` v1.x |
| **TestCase** / **TestReport** | Distinct from `SimulationCase` — physical testing (wind tunnel, fatigue, EMI) is a separate evidence class. `verified_by` relation already exists; needs target entity. | v1 |
| **Configuration** (or **EffectivityRange**) | Aircraft are sold in configurations; "applies to AC tail# X-Y" is core to airworthiness. Without this, `applicable_to` is too coarse. | v1.x (defer if v1 demo doesn't hit it) |
| **Person** / **Organization** (lightweight) | Author of ExpertNote, issuing authority of RegulationClause, OEM of Component — currently free-text strings, fragile. | v1 (lightweight; just name + role + optional org) |

### Redundancy / Boundary Risks (call out, not delete)

| Pair | Risk | Resolution |
|------|------|-----------|
| `MaintenanceTask` vs `Procedure` | Both describe step-by-step actions. MaintenanceTask is operational (per ATA chapter 05/12); Procedure is broader (test/inspection/calibration). | Document boundary in schema doc: `MaintenanceTask` is a subtype of `Procedure` semantically; keep both but have `MaintenanceTask.parent_procedure` optional ref to a generic Procedure. |
| `Document` vs everything else | `Document` is meta — every other entity has a `source: Document` ref. Risk: people put narrative content in `Document` instead of `ExpertNote`. | Document = the artifact (PDF/DOCX); ExpertNote = curated knowledge nugget. Schema doc must clarify with examples. |
| `AircraftSystem` vs `Subsystem` | Subsystem implies hierarchy already in `part_of` relation. Why two types? | Keep both — ATA chapter level granularity warrants it (System = ATA 27 Flight Controls; Subsystem = primary flight controls vs secondary). Document the level criterion. |
| `CFDMethod` / `MeshRequirement` / `TurbulenceModel` | Fine-grained, but coverage of structural/thermal/EMC analysis is missing — risk of "CFD KB" not "aviation KB" | Either generalize to `AnalysisMethod` with `discipline: cfd/fea/thermal/emc` field, OR explicitly scope v1 to CFD and add others later. Recommend: keep CFD-specific names v1 (user's strength), add `AnalysisMethod` parent class v2. |

---

## Relation Gap Analysis (User's 13 Relations)

### Coverage Verdict
Solid hierarchical/causal/normative coverage. Gaps in **lateral** (peer interactions), **lifecycle** (revisions, phases), and **derivation tracking**.

### Recommended Additions (5 relations)

| Relation | Direction | Why Add | v1 / Defer |
|----------|-----------|---------|-----------|
| **interfaces_with** | Component ↔ Component / Subsystem ↔ Subsystem | Engineering interfaces (ICDs) are first-class; not capturable as `part_of` or `requires` | v1 |
| **complies_with** | Component/AircraftSystem → RegulationClause/Standard | Distinct from `verified_by` (which is evidence) — `complies_with` is the assertion of compliance, evidence chains via `verified_by` | v1 |
| **has_revision** / **revision_of** | Entity → Entity | Aviation = revision-driven (Issue 5, Rev B). `supersedes` is for terminal replacement; `revision_of` keeps lineage of incremental updates | v1 |
| **applicable_during_phase** | Entity → LifecyclePhase enum | "This procedure applies during ground test only"; "this CFD method is preliminary-design only". Lifecycle phase: concept/preliminary/detailed/certification/operational/retirement | v1.x |
| **generated_by** / **derived_from(version)** | Entity → Process/Tool/Person | Provenance for AI-extracted content; complements `provenance.method` field with structured trace | v1 (combined with `provenance.tool: <name>@<version>` field — simpler than full relation) |

### Edge Case Relations to Consider (v1.x or v2)

| Relation | Use Case | Verdict |
|----------|----------|---------|
| **alternative_to** | "Use this if primary path fails" — different from `equivalent_to` | v1.x |
| **contradicts** | Distinct from `conflicts_with`? | Merge into `conflicts_with`. No need for both. |
| **assumes** | Procedure assumes Configuration X | Useful but covers via `applicable_to` + lifecycle. Skip. |
| **traced_to** | Requirement → higher-level Requirement | Already covered by `derived_from`. Skip. |

### Redundancy Risks

| Pair | Risk | Resolution |
|------|------|-----------|
| `causes` vs `mitigated_by` | Both around FailureMode — fine, different directions | Keep. Document semantics. |
| `derived_from` vs `cites` | `cites` = referenced; `derived_from` = source of truth. | Keep both, schema doc must show example. `cites` is weaker. |
| `equivalent_to` vs cross-language pairs | If you have ZH and EN versions of same concept, `equivalent_to` could explode | Use `equivalent_to` only for genuine domain equivalence (e.g. FAR 25.1309 ≈ CS 25.1309). Cross-language is not a relation; it's a `translations` field on entity. |

---

## Feature Dependencies

```
Citation enforcement (RAG guardrail)
    └──requires──> Per-chunk provenance (during ingestion)
                       └──requires──> Document metadata schema
                                          └──requires──> JSON Schema validator in CI

AI vs Human extraction distinction
    └──requires──> provenance.method field in entity schema
                       └──requires──> Schema versioning (semver)

Confidence-weighted retrieval
    └──requires──> confidence field populated on every entity
                       └──requires──> Human review workflow for AI-extracted (calibration)

GraphRAG v2 readiness (extension hooks)
    └──requires──> Stable entity URIs
    └──requires──> Triple-exportable relation format (yaml→jsonl-triples script)
    └──requires──> Schema versioning

Faceted browse
    └──requires──> Tag/taxonomy on entities (domain_tags)
    └──requires──> Static index generation script

Conflict detection between sources (differentiator, deferred)
    └──requires──> Multiple sources per claim (entity → multiple Document refs)
    └──requires──> LLM pairwise comparator (defer to v2)

Bilingual retrieval
    └──requires──> Curated aviation glossary
    └──requires──> Embedding model with multilingual capability (BGE-M3 or similar)
    └──conflicts──> Auto-translation (anti-feature)

Schema-as-product (AI successor handoff)
    └──requires──> JSON Schema files
    └──requires──> Glossary
    └──requires──> ADR-style decision log
    └──requires──> Termset documentation in every schema doc
```

### Critical Dependency Notes

- **Citation enforcement requires per-chunk provenance:** RAGFlow gives page-level by default; aviation needs clause-ID resolution. This determines ingestion pipeline complexity from day 1.
- **AI/human distinction requires schema field — not policy:** Bolt-on policy gets bypassed; schema-required field cannot be.
- **GraphRAG v2 hooks must be designed in v1:** If entity URIs aren't stable + relations aren't triple-exportable in v1, v2 GraphRAG = full re-extraction = schedule killer.
- **Bilingual conflicts with auto-translation:** Build glossary; refuse auto-translate. Engineers vet translations.
- **Conflict detection deferred but schema slot reserved:** `conflicts_with` relation must exist v1 even if no automated populator; manual entries earn their place.

---

## MVP Definition

### Launch With (v1) — Documents/Schema/Demo Only Per User Constraint

- [ ] **17 entity JSON Schemas** + recommended 3 additions (Material, TestCase, Person/Organization) — core value lock
- [ ] **13 relation schemas** + recommended 4 additions (interfaces_with, complies_with, has_revision, generated_by-via-field) — coverage
- [ ] **provenance schema component** (source, confidence, method, reviewed_by, reviewed_at) — embedded in every entity — differentiator core
- [ ] **Document metadata schema** (R7 fields) — ingestion baseline
- [ ] **External-ref fields** (ata_chapter, s1000d_dmc, ap233_id) — interop hook
- [ ] **Stable URI scheme** (`aviationkb://<type>/<slug>@<version>`) — GraphRAG hook
- [ ] **Triple-export script skeleton** (yaml→jsonl-triples) — GraphRAG hook
- [ ] **Schema versioning + CHANGELOG.md per schema dir** — R6
- [ ] **CI: JSON Schema validation + broken-ref detector + citation validator (every entity has source)** — quality gate
- [ ] **RAG pipeline design doc (R8)** with hybrid retrieval, citation guardrail spec, ZH/EN bilingual approach, no-citation refusal policy
- [ ] **Wiki.js + RAGFlow deployment design doc (R9)** with extension points for GraphRAG noted
- [ ] **Aviation glossary seed (≥50 terms ZH/EN)** — bilingual differentiator seed
- [ ] **Demo data: ≥1 instance per entity type** + ≥3 relations + ≥3 documents + 1 ExpertNote with full provenance — R10
- [ ] **AI接力开发指南 section in every design doc** — R12
- [ ] **ADR decision log skeleton** — auditability

### Add After Validation (v1.x)

- [ ] **Confidence-weighted retrieval ranking** — once enough entities have varied confidence
- [ ] **Backward-compat schema loader (≥1 minor)** — once first breaking change emerges
- [ ] **Static knowledge graph HTML view** — once ≥50 entities populated (good demo asset)
- [ ] **Faceted browse index** — once tag taxonomy stabilizes
- [ ] **Configuration / EffectivityRange entity** — when first multi-tail-number scenario hits
- [ ] **MaterialAllowable entity** — when first structural fatigue case enters
- [ ] **applicable_during_phase relation** — when lifecycle modeling needs surface
- [ ] **Provenance-aware answer rendering UI** — once core RAG flow works
- [ ] **Aviation glossary expansion (>500 terms)**
- [ ] **Migration script first real example** — when first breaking schema change

### Future Consideration (v2+)

- [ ] **GraphRAG layer** — once ≥1K entities + retrieval quality plateau on flat RAG (trigger: measured)
- [ ] **Conflict detection between sources** — needs LLM cost budget + reviewer queue
- [ ] **AnalysisMethod parent class (FEA/thermal/EMC beyond CFD)** — when non-CFD analysis content arrives
- [ ] **Graph database backend (Neo4j/Nebula)** — when YAML hits scale ceiling (>10K triples or query latency)
- [ ] **OCR for scanned documents** — when manual-transcription backlog exceeds tolerance
- [ ] **Multi-tenant RBAC** — when second org/team onboards
- [ ] **Decision-style Agent (with hard guardrails)** — only after RAG+citation foundation proven for ≥6 months
- [ ] **Real-time collaborative entity editing** — likely never (PR-review model is correct for safety)
- [ ] **Single sign-on across Wiki.js + RAGFlow** — when user count justifies the auth-gateway investment

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| 17+3 entity JSON Schemas | HIGH | MEDIUM | P1 |
| 13+4 relation schemas | HIGH | LOW | P1 |
| provenance + AI/human distinction (schema-level) | HIGH | LOW | P1 |
| Citation enforcement spec | HIGH | LOW (spec only v1) | P1 |
| Hybrid retrieval design (BM25+vec+RRF) | HIGH | LOW (design only v1) | P1 |
| ZH/EN glossary seed | HIGH | MEDIUM | P1 |
| ATA/S1000D mapping fields | MEDIUM | LOW | P1 |
| Stable URI scheme + triple export | HIGH (v2 readiness) | LOW | P1 |
| CI validators (schema + broken-ref + citation) | HIGH | LOW | P1 |
| Wiki.js + RAGFlow deployment design | HIGH | MEDIUM | P1 |
| Demo data covering all entity types | HIGH | MEDIUM | P1 |
| AI接力 docs (R12) | HIGH (successor handoff) | LOW | P1 |
| Confidence-weighted ranking | MEDIUM | MEDIUM | P2 |
| Static graph HTML view | MEDIUM | MEDIUM | P2 |
| Faceted browse index | MEDIUM | MEDIUM | P2 |
| Configuration entity | MEDIUM | LOW | P2 |
| MaterialAllowable entity | MEDIUM | MEDIUM | P2 |
| Backward-compat loaders | MEDIUM | MEDIUM | P2 |
| Provenance-aware answer UI | HIGH | HIGH | P2 |
| GraphRAG layer | HIGH | HIGH | P3 |
| Conflict detection automation | HIGH | HIGH | P3 |
| Graph DB migration | LOW (premature) | HIGH | P3 |
| OCR pipeline | LOW (v1) | HIGH | P3 |
| Multi-tenant RBAC | LOW (v1) | HIGH | P3 |

---

## Competitor / Reference Feature Analysis

| Feature | Confluence | Notion | NASA NTRS | FAA Reg Library | RAGFlow stock | AeroPower-RAG | **Our Approach** |
|---------|-----------|--------|-----------|-----------------|---------------|---------------|------------------|
| Markdown/rich editing | ✅ rich | ✅ rich | ❌ | ❌ | ❌ | ❌ | ✅ Wiki.js Markdown |
| Per-fact provenance | ❌ | ❌ | partial (paper-level) | partial (clause-level) | partial (chunk-level) | ✅ chunk+page | ✅ entity-level + chunk-level + AI/human |
| Citation-mandatory AI | n/a | n/a | n/a | n/a | partial | ✅ | ✅ enforced (refuse if none) |
| Hybrid retrieval (vec+BM25+RRF) | ❌ | ❌ | BM25 only | BM25 only | ✅ | ✅ | ✅ |
| Aviation ontology | ❌ | ❌ | NTRS subjects (loose) | regulation tree | ❌ | partial | ✅ 17+3 entities, 13+4 relations |
| Bilingual ZH/EN | ❌ | partial | ❌ | EN only | partial | ✅ | ✅ glossary-backed |
| Schema versioning | ❌ | ❌ | ❌ | annual reg revision | ❌ | ❌ | ✅ semver per file + CHANGELOG |
| AI vs human knowledge flag | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ **unique** |
| Standards mapping (ATA/S1000D) | ❌ | ❌ | ❌ | ❌ | ❌ | partial | ✅ external_refs fields |
| Decision log (ADR) integration | ❌ (manual) | ❌ (manual) | ❌ | ❌ | ❌ | ❌ | ✅ .planning/decisions |
| GraphRAG-ready | ❌ | ❌ | ❌ | ❌ | partial | ❌ | ✅ stable URIs + triple export hooks v1 |

**Differentiation summary:** None of the listed references combine schema-versioned aviation ontology + AI/human provenance distinction + citation-mandatory bilingual hybrid RAG + GraphRAG-ready data shape. That's the moat.

---

## Confidence Assessment

| Area | Confidence | Reason |
|------|-----------|--------|
| Generic KB/RAG feature landscape (Confluence, Notion, RAGAS, hybrid retrieval) | HIGH | Well-documented in user's own AeroPower-RAG, RAGAS docs, Anthropic RAG patterns; training data + ecosystem agreement |
| User's 17 entities / 13 relations evaluation | MEDIUM-HIGH | Aviation domain knowledge in training; gap analysis cross-checked against ATA Spec 100, S1000D, AP233 from training data — flag for second-pass with current S1000D Issue 6 docs |
| ATA/S1000D/AP233 mapping field design | MEDIUM | Field-level design is safe; full mapping requires verifying current S1000D Issue 6 (2024) DMC structure — defer to schema-design phase with WebFetch verification |
| RAGFlow capabilities (citation, hybrid, multilingual) | MEDIUM | From training + general docs; recommend Context7 verification when implementation phase starts |
| Wiki.js capabilities | MEDIUM | Stable product; v2.x feature set well-known but verify search/auth specifics at deployment design |
| GraphRAG v2 hook design | MEDIUM | Microsoft GraphRAG paper + LangChain GraphRAG impls in training; export-format choice (RDF vs JSONL triples vs Cypher-CSV) deserves a separate ADR |
| Confidence-weighted retrieval | LOW-MEDIUM | Theoretically sound; not heavily benchmarked in published RAG literature — proceed but mark as v1.x experimental |

---

## Open Questions for Phase-Specific Research

1. **RAGFlow citation API surface** — does it expose per-sentence citations or only per-answer? Determines guardrail design granularity. (Verify in R8/R9 phase.)
2. **Aviation glossary — seed source.** ICAO Doc 9713 (ICVO terminology), ATA bilingual glossaries, CAAC bilingual aviation terms? Need licensed source. (Verify in glossary phase.)
3. **S1000D Issue 6 (2024) DMC structure** — current spec for `external_refs.s1000d_dmc` field shape. (Verify with WebFetch when schema phase starts.)
4. **Embedding model choice** — BGE-M3 vs nomic-embed-text vs OpenAI text-embedding-3 for ZH/EN aviation. AeroPower-RAG used nomic-embed-text — keep consistent or upgrade? (R8 phase.)
5. **Triple export format for GraphRAG hook** — RDF/Turtle vs JSON-LD vs simple JSONL `{s, p, o}`? Decision affects v2 GraphRAG migration cost. (ADR needed v1.)

---

## Sources

- User's PROJECT.md (`.planning/PROJECT.md`) — authoritative scope/constraints/exclusions
- User's MEMORY.md AeroPower-RAG entry — validated hybrid retrieval baseline
- User's CLAUDE.md cfd-harness-unified governance — provenance/audit cultural pattern
- ATA iSpec 2200 / Spec 100 (chapter numbering) — training data; flag for S1000D Issue 6 verification
- S1000D Issue 5.0/6.0 DMC structure — training data; flag for verification
- AP233 (ISO 10303-233) systems engineering data exchange — training data
- FAA 14 CFR Part 25 / FAR-EASA CS-25 cross-mapping — training data
- ICAO doc system (Doc 9713 terminology) — training data
- NASA NTRS (ntrs.nasa.gov) feature inspection — training data
- Confluence / Notion feature comparison — training data + general knowledge
- RAGAS evaluation framework — training data; current docs at ragas.io
- Anthropic published RAG patterns (contextual retrieval, citation patterns) — training data
- Microsoft GraphRAG paper (2024) — training data; current arxiv
- RAGFlow (infiniflow) docs — training data; flag for Context7 verification at implementation phase
- Wiki.js 2.x docs — training data; stable

---

*Feature research for: Aviation Knowledge Base MVP (Wiki.js + RAGFlow + YAML/JSON Schema)*
*Researched: 2026-05-03*

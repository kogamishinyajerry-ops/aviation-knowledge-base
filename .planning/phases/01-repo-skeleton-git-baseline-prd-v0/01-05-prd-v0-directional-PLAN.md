---
phase: 01-repo-skeleton-git-baseline-prd-v0
plan: 05
type: execute
wave: 3
depends_on:
  - 01-01
  - 01-02
files_modified:
  - .planning/design/.gitkeep
  - .planning/design/PRD_v0.md
autonomous: true
requirements:
  - PRD-01

must_haves:
  truths:
    - "`.planning/design/PRD_v0.md` exists and opens with an `## AI 接力开发指南` (or `## AI Handoff Guide`) section per R12 / AIH-01 discipline starting in Phase 1"
    - "PRD contains 6 mandatory sections in order: Users, Scope (in/out), Non-Goals, Success Metrics, Deliverable List, Open Questions, Acceptance Criteria placeholder for v1"
    - "Users section identifies all 4 user archetypes from PROJECT.md: 航空工程师 / CFD/适航研究人员 / 项目经理-决策者 / 接手开发的 AI 编码助手"
    - "Scope explicitly lists what is IN v1 (mapped to phases 2-6 deliverables) and what is OUT (lifted from PROJECT.md + REQUIREMENTS.md Out-of-Scope)"
    - "Success Metrics are MEASURABLE at v1 ship time (not aspirational): e.g., '≥1 instance per 17 baseline entity types', '≥3 source documents ingested', 'CI green', '5-min stranger test passes for ≥3 design docs'"
    - "Deliverable List enumerates artifacts grouped by phase, each tied to a REQ-ID"
    - "Open Questions inherits unresolved items from .planning/research/SUMMARY.md and adds any PRD-level ones"
    - "Acceptance Criteria placeholder explicitly defers detailed per-requirement criteria to PRD v1 (Phase 6) — the PRD v0 itself is directional, not contractual"
    - "Length 200-400 lines (directional, not exhaustive); v1 final PRD comes in Phase 6"
  artifacts:
    - path: ".planning/design/PRD_v0.md"
      provides: "Directional PRD — north star for downstream phase planning"
      min_lines: 200
      contains: "AI 接力开发指南"
    - path: ".planning/design/.gitkeep"
      provides: "Ensures `.planning/design/` directory is tracked even before PRD lands"
  key_links:
    - from: ".planning/design/PRD_v0.md"
      to: ".planning/PROJECT.md"
      via: "Markdown link in Core Value section"
      pattern: "\\.planning/PROJECT\\.md"
    - from: ".planning/design/PRD_v0.md"
      to: ".planning/REQUIREMENTS.md"
      via: "Deliverable List references REQ-IDs"
      pattern: "REPO-0[1-5]|PRD-0[12]|ONT-E|RAG-0|DEP-0"
    - from: ".planning/design/PRD_v0.md"
      to: ".planning/ROADMAP.md"
      via: "Deliverable List references phases"
      pattern: "Phase [1-6]"
    - from: ".planning/design/PRD_v0.md"
      to: ".planning/research/SUMMARY.md"
      via: "Open Questions section inherits from research summary"
      pattern: "research/SUMMARY\\.md"
---

<objective>
Write the directional PRD v0 — a north-star document that gives every downstream phase (2 through 6) a single point of reference for "what does v1 deliver, who is it for, and what is OUT of scope." This is PRD-01.

The PRD v0 is **directional, not contractual**. The contractual version is PRD v1, delivered in Phase 6 after all schema/architecture/RAG/deployment decisions are concrete. PRD v0 exists so:
1. Phase 2 schema designers know which entity types, provenance constraints, and audit requirements the product needs.
2. Phase 5 RAG designers know what the user actually asks (Q&A topics, language mix, citation expectations).
3. Phase 6 deployment planners know what scale (single host, ≤5 users) and what hard constraints (no SSO, no public exposure) drive topology.
4. Any future AI session reading this repo can in 5 minutes answer "is feature X in v1 scope?" by checking the PRD.

The PRD v0 lives at `.planning/design/PRD_v0.md`. The directory `.planning/design/` does not yet exist; this plan also creates the directory and adds a `.gitkeep` so it's tracked even before the PRD file lands.

Per AIH-01 / R12 discipline starting in Phase 1, this PRD opens with an `## AI 接力开发指南` section. That sets the precedent for every subsequent design doc.

Output: `.planning/design/PRD_v0.md` ~250-400 lines, structured per the `must_haves` spec, committed atomically.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/research/SUMMARY.md
@.planning/research/ARCHITECTURE.md
@.planning/research/PITFALLS.md
@README.md
@CLAUDE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create .planning/design/ directory with .gitkeep placeholder</name>
  <files>.planning/design/.gitkeep</files>
  <read_first>
    - .planning/PROJECT.md (confirms `.planning/design/` is the canonical home for design docs)
    - .planning/research/ARCHITECTURE.md (Recommended Project Structure references `.planning/design/` indirectly via mention of design docs)
  </read_first>
  <action>
```bash
mkdir -p /Users/Zhuanz/aviation-knowledge-base/.planning/design
touch /Users/Zhuanz/aviation-knowledge-base/.planning/design/.gitkeep
```
  </action>
  <verify>
    <automated>test -d /Users/Zhuanz/aviation-knowledge-base/.planning/design &amp;&amp; test -f /Users/Zhuanz/aviation-knowledge-base/.planning/design/.gitkeep &amp;&amp; echo OK</automated>
  </verify>
  <acceptance_criteria>
    - Directory `/Users/Zhuanz/aviation-knowledge-base/.planning/design/` exists
    - File `/Users/Zhuanz/aviation-knowledge-base/.planning/design/.gitkeep` exists
  </acceptance_criteria>
  <done>`.planning/design/` directory tracked; ready for PRD_v0.md to land in Task 2.</done>
</task>

<task type="auto">
  <name>Task 2: Write .planning/design/PRD_v0.md (directional PRD)</name>
  <files>.planning/design/PRD_v0.md</files>
  <read_first>
    - .planning/PROJECT.md (full read — extract: What This Is, Core Value, Active Requirements R1-R12, Out of Scope rationales, Constraints, Key Decisions)
    - .planning/REQUIREMENTS.md (full read — extract REQ-IDs by category to populate Deliverable List)
    - .planning/ROADMAP.md (extract: Phase goals + success criteria for each phase, to map deliverables to phases)
    - .planning/research/SUMMARY.md (extract: Open Questions section to populate PRD's open questions; Pinned Decisions for Constraints section)
    - .planning/research/PITFALLS.md ("Looks Done But Isn't" checklist informs the Acceptance Criteria placeholder section)
    - README.md (Plan 02 output — to ensure terminology consistency between README and PRD)
  </read_first>
  <action>
Write `/Users/Zhuanz/aviation-knowledge-base/.planning/design/PRD_v0.md` with EXACTLY this content. (This is a long document — do not abridge. The PRD IS the prompt for downstream phases.)

```markdown
# PRD v0 — Aviation Knowledge Base MVP (Directional)

**Version:** v0 (directional, not contractual)
**Status:** Phase 1 deliverable
**Replaces:** nothing
**Replaced by:** PRD v1 (Phase 6 — final, contractual)
**Authors:** gsd-planner-phase / Phase 1 / Plan 05 / 2026-05-03
**Source documents:** [PROJECT.md](../PROJECT.md), [ROADMAP.md](../ROADMAP.md), [REQUIREMENTS.md](../REQUIREMENTS.md), [research/SUMMARY.md](../research/SUMMARY.md), [research/ARCHITECTURE.md](../research/ARCHITECTURE.md)

***

## AI 接力开发指南

> 本节让任何接手 PRD 的 AI / 人在 5 分钟内理解：这是什么文档、它能说什么不能说什么、哪些字段是 locked、哪些是 directional。
>
> This section orients an AI/human picking up the PRD: what is this document, what it CAN and CANNOT decide, which fields are locked vs directional.

### What this document is

A directional PRD — a north star for Phases 2 through 6. It captures user archetypes, scope boundaries, success metrics, deliverable list, and open questions at the resolution available in **early Phase 1**, when no schemas have been authored yet, no demo data exists, and no RAG pipeline has been spec'd.

### What this document is NOT

- Not contractual. Contractual per-requirement acceptance criteria land in **PRD v1 (Phase 6)** after all schema/architecture/RAG/deployment decisions are concrete.
- Not a re-derivation of PROJECT.md / REQUIREMENTS.md / ROADMAP.md. It synthesizes them into a single product narrative.
- Not a technology spec. Stack decisions live in [research/STACK.md](../research/STACK.md).

### Locked vs Directional

| Section | Locked? | Notes |
|---------|---------|-------|
| Core Value (mirrored from PROJECT.md) | **Locked** | Cannot be relaxed in any later PRD revision |
| Tech Stack | **Locked** | Wiki.js 2.5.314 / RAGFlow 0.25.1 / Postgres 16 / YAML+JSON Schema / Git |
| Out of Scope (v1) | **Locked** | All items in §3.2 below cannot be re-added in v1 without an ADR |
| Users / Use Cases | Directional | May refine after Phase 4 demo data shows real shape |
| Success Metrics | Directional | PRD v1 hardens these into per-requirement acceptance criteria |
| Open Questions | Directional | Inherits from research/SUMMARY.md, resolves at the phases listed |

### How to read this PRD

1. Read §1 (Users) and §2 (Scope) first — they answer "is feature X in v1?"
2. §3 (Non-Goals / Out of Scope) is the strongest signal — if a feature appears here it cannot be added without an ADR.
3. §4 (Success Metrics) is the bar each phase must clear; §5 (Deliverable List) is what each phase actually produces.
4. §6 (Open Questions) is where unresolved items are tracked; if you find a new one, add it here.

### How to update this PRD

PRD v0 is FROZEN at the end of Phase 1. Updates go into PRD v1 (Phase 6). The only allowed in-flight edits to PRD v0 are:
- Typo fixes
- Cross-link repair if a target file moves
- Resolution of open questions (move the resolved question to a "Resolved" subsection, but keep its history)

If a phase needs to change a Locked decision, that requires an ADR in `.planning/decisions/` plus user sign-off — not a PRD v0 edit.

***

## 1. Users

### 1.1 Primary user archetypes (4)

**A. 航空工程师 / Aerospace Engineer**
- *Role:* Designs / maintains / certifies aircraft systems, components, procedures.
- *Why they need this:* They need to look up regulations (FAR / EASA CS / CCAR), supersession history, related accident cases, and component-level requirements without trusting an unsourced AI summary.
- *Critical need:* Citations that resolve to the original page/section/clause. Any answer without a verifiable citation is unusable in their workflow.
- *Languages:* Bilingual ZH/EN; switches based on document jurisdiction.

**B. CFD / 适航研究人员 / CFD & Airworthiness Researcher**
- *Role:* Designs simulation cases, validates against benchmarks (NASA TMR, ERCOFTAC, AIAA workshops), reviews accident reports.
- *Why they need this:* They sit between regulators and engineers; need to cross-reference simulation methods, turbulence models, mesh requirements with the regulations and accident causes those simulations bear on.
- *Critical need:* Provenance — distinguish "verified with experimental data" from "AI-extracted from a paper." The H-Darrieus failure mode (where AI fabricated chart data not in the original paper) is the failure they are actively guarding against.
- *Languages:* Mostly EN for international literature; ZH for CCAR / domestic projects.

**C. 项目经理 / 决策者 / Project Manager & Decision-Maker**
- *Role:* Plans projects, allocates budget, signs off on certification submissions.
- *Why they need this:* Needs an audit trail. "Why did we choose method X?" must be answerable from the knowledge base, with sources and date stamps. Industrial software delivery (per user's CLAUDE.md / cfd-ai-workbench experience) requires full process records.
- *Critical need:* Audit. Who said what, when, with what source. Schema versioning + Git history.
- *Languages:* Bilingual.

**D. 接手开发的 AI 编码助手 / Inheriting AI Coding Assistant** (Claude / Codex / DeepSeek / Gemini)
- *Role:* Picks up the project months after initial setup, reads cold, must continue work.
- *Why they need this:* Without the "AI 接力开发指南" pattern (R12), each new AI session redoes orientation from scratch — wasting context and risking misunderstanding decisions.
- *Critical need:* Self-contained design docs. Glossary. Open-questions log. Decision trail.
- *Languages:* Both, with bias toward EN for technical terms and ZH for project-specific jargon.

### 1.2 Out-of-scope users (v1)

- Multi-tenant external customers (no RBAC / multi-org in v1)
- General public (no public deployment in v1; confidentiality gating documented but not exercised)
- Real-time collaborators (Wiki.js handles narrative editing poorly; not a moat)

***

## 2. Scope

### 2.1 In scope (v1) — by phase

**Phase 1 (this phase): Foundation**
- Locked directory layout matching ARCHITECTURE.md
- Git LFS configured for `*.pdf, *.docx, *.xlsx, *.pptx`
- README.md with AI 接力开发指南
- Pre-commit hook config (yamllint, check-jsonschema, check-merge-conflict, end-of-file-fixer)
- GitHub Actions baseline (lint real, schema/link checks as labeled stubs)
- This PRD v0

**Phase 2: Ontology Schema v0.1.0**
- Base entity + relation schemas with mandatory provenance/confidence fields
- 17 baseline entity type schemas (AircraftModel, AircraftSystem, Subsystem, Component, Requirement, RegulationClause, Standard, Procedure, FailureMode, MaintenanceTask, CFDMethod, SimulationCase, MeshRequirement, TurbulenceModel, AccidentCase, Document, ExpertNote)
- 13 baseline relation type schemas (part_of, applicable_to, constrained_by, verified_by, derived_from, supersedes, cites, causes, mitigated_by, requires, equivalent_to, conflicts_with, used_in)
- 4 research-recommended entity additions evaluated via ADR (Material, TestCase/TestReport, Configuration/EffectivityRange, Person/Organization)
- 5 research-recommended relation additions evaluated via ADR (interfaces_with, complies_with, has_revision, applicable_during_phase, generated_by-vs-field)
- Provenance + confidence + source schemas mandatory; H-Darrieus lock (`ai_extracted` + `confidence > 0.85` without `reviewer` → REJECT)
- Schema versioning: `ontology/VERSION = 0.1.0`, CHANGELOG, per-record `schema_version`, migrations/ pattern
- URI scheme ADR (`aviationkb://<type>/<slug>@<version>`)

**Phase 3: Validators + CI Active**
- `scripts/validate.py` master entrypoint
- Per-rule validators: schema, IDs, relations (referent existence), provenance, links
- `tests/fixtures/{valid,invalid}/` covering every entity / relation type / `_pending/` promotion / supersession / ai_extracted-without-reviewer rejection
- pytest test suite green
- GitHub Actions runs validate.py + pytest on every PR; blocks merge on failure

**Phase 4: Demo Data + Document Import Spec**
- ≥1 instance per entity type (17 baseline + Phase-2-accepted additions)
- ≥3 relation instances spanning ≥3 relation types
- ≥3 source documents (1 regulation, 1 CFD paper, 1 accident report) with full metadata
- 1 ExpertNote demonstrating the canonical provenance/source/confidence pattern
- 1 supersession demo (RegulationClause superseded + replacement)
- 1 AI-extracted record in `instances/_pending/` (verified NOT in canonical)
- 1 bilingual entity using `i18n: { zh, en }`
- `docs/README.md` documenting import workflow + confidentiality gating

**Phase 5: RAG Pipeline Design (document-only, no run)**
- `.planning/design/RAG_PIPELINE.md` with:
  - Chunking strategy preserving tables (RAGFlow OpenDataLoader-PDF backend)
  - BGE-M3 + bge-reranker-v2-m3 selection rationale + mini-benchmark plan
  - Hybrid retrieval (vector + BM25 + RRF) configuration
  - System-side `[CITE:chunk_id]` token injection (LLM cannot self-cite)
  - No-context guardrail (`retrieved_chunks=[] → "not found"` short-circuit)
  - Cross-lingual ZH/EN retrieval design
- `evaluation/queries.yaml` with ≥30 evaluation queries (≥20% table-query, with out-of-scope category)
- `scripts/exporters/to_ragflow.py` skeleton + design spec

**Phase 6: Deployment Plan + PRD v1 + Roadmap + AI Handoff Polish**
- `deploy/docker-compose.yml.draft` (Wiki.js 2.5.314 + Postgres 16 + RAGFlow 0.25.1 + Caddy) marked DRAFT — NOT FOR PRODUCTION
- `deploy/.env.example` with all env vars, no hardcoded secrets
- Topology diagram (Mermaid or ASCII) showing Git ↔ Wiki.js ↔ RAGFlow ↔ Caddy data flow
- `deploy/wiki-git-storage.md` (Wiki.js Git scope = `wiki/` only, NEVER full repo)
- `deploy/authentik-phase2.md` (future SSO plan with RAGFlow OIDC bug status)
- `.planning/design/PRD_v1.md` (final, contractual; replaces this PRD v0)
- `.planning/ROADMAP_FUTURE.md` with v2+ trigger conditions (GraphRAG, Agent layer, Graph DB, OCR, multi-tenant, SSO, decision agent)
- `docs/GLOSSARY.md` with ≥50 bilingual aviation seed terms
- `process-log/` populated with phase-completion entries for all 6 phases
- 5-minute stranger test passes for ≥3 sampled design docs after a context-clean break

### 2.2 Out of scope (v1) — locked

These are **locked OUT** for v1. Re-adding any of them requires an ADR in `.planning/decisions/` plus explicit user sign-off.

| Feature | Reason locked out |
|---------|-------------------|
| Dify (agent orchestration) | First stage no agent orchestration; would increase coupling |
| Self-built Vue/React frontend | Wiki.js + RAGFlow UIs are sufficient; custom UI = scope explosion |
| Graph DB backend (Neo4j/Nebula) in v1 | YAML sufficient for ≤10K triples; defer to v2 GraphRAG phase |
| Auto-crawlers / scrapers | Quality > volume; v1 is curated import only |
| Decision-making agents (auto-tool-use loops) | Out of scope per Core Value — RAG retrieval-augmented Q&A only |
| Uncited AI answers | Hard NO — guardrail enforced; zero-tolerance hallucination policy |
| OCR / scanned image processing | Text-layer PDF/MD/HTML/DOCX only in v1 |
| Multi-tenant / fine-grained RBAC | v1 single-org admin/reader; v2 if user demand |
| Real-time collaborative editing | Wiki.js handles this poorly; not differentiating |
| LLM self-citation | System injects `[CITE:chunk_id]` tokens; LLM cannot author citations |
| Auto-translation without human review | Aviation translation has legal/safety implications; bilingual is curated |
| Inline code execution | Anti-pattern in KB; security + maintenance burden |
| Real-running docker-compose v1 | Phase 6 ships draft + selection rationale, not running infra |
| Wiki.js 3.0 | Alpha-since-2021; production unsafe |
| RAGFlow OIDC SSO | Open bugs (#3495, #12568); defer until upstream fixes |
| ATA Spec 100 / S1000D as primary schema | Custom YAML+JSON Schema; reserve `s1000d_dmc` field for future |
| AP233 / ISO 10303 | Wrong shape; STEP/EXPRESS heavy machinery |

### 2.3 Tech stack (locked)

Per [research/STACK.md](../research/STACK.md):
- **Wiki.js 2.5.314** (knowledge portal, Markdown, ZH/EN, KaTeX)
- **PostgreSQL 16.x** (Wiki.js DB; only future-proof option)
- **RAGFlow 0.25.1** (RAG ingestion + retrieval + citation)
- **JSON Schema Draft 2020-12** + **YAML 1.2** (ontology source)
- **check-jsonschema 0.37.1** + **yamllint 1.38** + **pre-commit 3.7+** (validation)
- **BGE-M3** (embedding) + **bge-reranker-v2-m3** (reranker)
- **OpenDataLoader-PDF** (RAGFlow's deterministic v1 PDF parser; no GPU needed)
- **Docker Engine 24.0+** + **docker-compose 2.26.1+** (orchestration; v1 draft only)
- **Git** + **Git LFS** (canonical truth + binary handling)

***

## 3. Non-Goals

(Strict subset of §2.2 emphasized for clarity — these are common requests we explicitly reject.)

- ❌ "Just spin up a chatbot real quick" — Core Value demands citation discipline; no shortcut version exists.
- ❌ "Use Notion / Confluence as backend" — would lose Git-as-SSOT and audit trail.
- ❌ "Build a slick UI" — Wiki.js + RAGFlow UIs are the UI in v1.
- ❌ "Auto-extract knowledge from PDFs into canonical" — must go through `instances/_pending/` quarantine + human review.
- ❌ "Add SSO so users have one login" — RAGFlow OIDC bugs make this a time sink in v1.

***

## 4. Success Metrics (directional — sharpened in PRD v1)

These are the v1-ship-time bars. Each is mapped to a phase's success criterion in [ROADMAP.md](../ROADMAP.md).

| Metric | Target (v1) | Verified in |
|--------|-------------|-------------|
| Repo layout matches ARCHITECTURE.md | 9/9 top-level dirs present, Git LFS configured, exporter stubs present | Phase 1 |
| README passes 5-minute stranger test | A fresh AI answers all 8 stranger-test questions in ≤5 min | Phase 1 + Phase 6 |
| All 17 baseline entity schemas + accepted research-additions self-validate | `check-jsonschema --check-metaschema` green | Phase 2 |
| All 13 baseline relation schemas + accepted research-additions self-validate | Same | Phase 2 |
| H-Darrieus lock active (schema rejects ai_extracted+conf>0.85+no reviewer) | 1 fixture confirms reject | Phase 2 + Phase 3 |
| `python scripts/validate.py` runs all rules in 1 pass on clean repo | exit 0 | Phase 3 |
| Per-rule validators are independently importable Python modules | pytest covers each | Phase 3 |
| Demo: ≥1 instance per entity type | All present, validate.py green | Phase 4 |
| Demo: ≥3 source docs with full metadata.yaml | 1 regulation, 1 CFD paper, 1 accident report | Phase 4 |
| Demo: 1 supersession + 1 _pending + 1 bilingual entity | 3 fixtures pass + reverse fixture (canonical never has ai_extracted method) green | Phase 4 |
| RAG: chunking strategy preserves tables atomically | Documented + RAGFlow 0.25.1 verified during Phase 5 research | Phase 5 |
| RAG: ≥30 evaluation queries with ≥20% table-query and out-of-scope category | `evaluation/queries.yaml` populated | Phase 5 |
| RAG: citation injection spec rejects LLM-self-author | Documented + post-gen validator design specced | Phase 5 |
| Deployment: docker-compose.yml.draft + .env.example + topology | All 3 present, marked DRAFT | Phase 6 |
| AIH: 5-minute stranger test passes for ≥3 sampled design docs | Re-tested after context-clean break | Phase 6 |
| GLOSSARY.md ≥50 bilingual aviation entries | Verified count | Phase 6 |
| ROADMAP_FUTURE.md has trigger conditions per future feature | Each "promote when X" criteria explicit | Phase 6 |

**Aggregate v1 ship gate:**
- All 6 phase success criteria from [ROADMAP.md](../ROADMAP.md) marked complete
- 94/94 v1 requirements mapped and addressed (per REQUIREMENTS.md traceability table)
- PRD v1 (final, contractual) signed off in CHANGELOG.md

***

## 5. Deliverable List (by phase, with REQ-IDs)

| Phase | Deliverable | REQ-IDs |
|-------|-------------|---------|
| 1 | Repo skeleton + .gitattributes (LFS) + .gitignore + exporter stubs | REPO-01, REPO-02 |
| 1 | README.md with AI 接力开发指南 | REPO-03 |
| 1 | GitHub Actions ci.yml (lint real, schema/link as stubs) | REPO-04 |
| 1 | .pre-commit-config.yaml + .yamllint | REPO-05 |
| 1 | PRD v0 (this document) | PRD-01 |
| 2 | Base entity + relation schemas, 17 entity + 13 relation type schemas, vocabularies, mappings/ placeholders | ONT-E-01..18, ONT-R-01..14 |
| 2 | Research-recommended additions (ADR-resolved): Material, TestCase, Configuration, Person/Org; interfaces_with, complies_with, has_revision, applicable_during_phase, generated_by | ONT-E-19..22, ONT-R-15..19 |
| 2 | Provenance + confidence + source schemas + H-Darrieus lock | PROV-01..06 |
| 2 | Schema versioning (VERSION=0.1.0, CHANGELOG, per-record schema_version, migrations/ pattern) | VER-01..04 |
| 3 | scripts/validate.py master + per-rule validators + fixtures + pytest suite + CI activation | VAL-01..05 |
| 4 | docs/<domain>/<doc-id>/ pattern + metadata schema + import workflow + confidentiality gating | DOC-01..04 |
| 4 | Demo: ≥1 instance per entity type, ≥3 relations, ≥3 docs, ExpertNote, supersession, AI-extracted, bilingual | DEMO-01..07 |
| 5 | RAG_PIPELINE.md design + chunking + embedding + retrieval + citation + guardrail + cross-lingual + eval ≥30 + to_ragflow.py spec | RAG-01..08 |
| 6 | docker-compose.yml.draft + .env.example + topology diagram + Wiki.js Git storage scope + Authentik plan + backup/restore note | DEP-01..06 |
| 6 | PRD v1 (final, contractual) | PRD-02 |
| 6 | AIH polish: design docs all carry handoff section, 5-min stranger test ≥3 docs, process-log entries 1-6, GLOSSARY ≥50 | AIH-01..04 |
| 6 | ROADMAP_FUTURE.md with v2+ trigger conditions | ROAD-01..02 |

**Total v1 requirements: 94 / 94 mapped** (per [REQUIREMENTS.md](../REQUIREMENTS.md) traceability table).

***

## 6. Open Questions

### 6.1 Inherited from research/SUMMARY.md (resolves at)

| # | Question | Resolves at |
|---|----------|-------------|
| 1 | S1000D Issue 6 (2024) DMC field shape — what optional field do we reserve? | Phase 2 (WebFetch verify) |
| 2 | RAGFlow 0.25.1 table-chunk preservation behavior — confirmed via Context7 / official docs? | Phase 5 (research before plan) |
| 3 | RAGFlow HTTP API citation granularity — per-sentence or per-answer? affects guardrail+injection design | Phase 5 |
| 4 | Triple export format — RDF/Turtle vs JSON-LD vs JSONL `{s,p,o,prov}`? Recommend JSONL for simplicity. | Phase 2 ADR |
| 5 | Aviation bilingual glossary seed source — ICAO 9713 / ATA bilingual / CAAC? | Phase 4 |
| 6 | `interfaces_with` vs `requires` boundary semantics — needs ADR with worked examples | Phase 2 |
| 7 | Embedding mini-benchmark scope — BGE-M3 vs nomic-embed-text vs multilingual-e5-large; how many ZH/EN test queries? | Phase 5 |
| 8 | RAGFlow Apple Silicon ARM image — official or workaround? | Phase 6 |
| 9 | Wiki.js ↔ Git two-way sync edge cases — conflicts, large pages, formatting drift? | Phase 6 |
| 10 | LLM choice for RAG (Ollama-local vs Claude/OpenAI API vs hybrid)? | Phase 5 design doc |

### 6.2 PRD-level questions (this document)

| # | Question | Proposed resolution |
|---|----------|---------------------|
| P-1 | Does v1 need a "comparison view" (e.g., FAR vs CCAR analogous clauses)? | Defer to v2 — high-value but requires bilingual relation type that isn't in baseline 13. Track under v2 ROADMAP_FUTURE.md. |
| P-2 | Should the supersession demo cover both "regulation" and "internal note" cases or just regulation? | Phase 4: regulation-only is sufficient for the demo gate; internal-note supersession is a documented pattern but not a v1 demo requirement. |
| P-3 | Does the AI 接力开发指南 section have a CI check (e.g., grep for the heading on every design doc)? | Phase 6: yes, add a tiny linter script that ensures every `.planning/design/*.md` contains the heading; placed in `scripts/validators/aih_section.py`. |
| P-4 | Bilingual glossary baseline — do we lock to ICAO 9713 terminology? | Phase 4 + Phase 6: start with ICAO 9713 + ATA bilingual + user's AeroPower-RAG glossary; no hard lock, but ICAO is the principal source. |
| P-5 | What is the v1 evidence that "every AI answer has a citation"? | Phase 5: post-generation validator that drops answers whose citations don't resolve to retrieved chunks. Phase 6: documented test path running ≥10 queries through the pipeline (no real run, but the test-design is part of v1). |

### 6.3 Resolved (track here as questions get answers)

(Empty as of Phase 1.)

***

## 7. Acceptance Criteria — Placeholder for v1

Detailed per-requirement acceptance criteria land in **PRD v1 (Phase 6)**. PRD v0 captures the directional bar; PRD v1 hardens it into pass/fail criteria after all schema/architecture/RAG/deployment decisions are concrete.

The structure PRD v1 will follow (so Phase 6 has a template):

```
For each REQ-ID in REQUIREMENTS.md:
- Given: <context — what state must exist before testing>
- When: <action — what is done to verify>
- Then: <observable outcome — measurable, not aspirational>
```

Example shape (placeholder; PRD v1 fills in all 94):

```
REQ: REPO-02 (Git LFS for binary doc types)
  Given: A clean clone of the repo
  When: A user runs `git lfs ls-files`
  Then: The output lists at least 4 LFS-tracked extensions: pdf, docx, xlsx, pptx
  And: Attempting to add a 10MB PDF without LFS tracking fails the pre-commit hook
       (via check-added-large-files with --maxkb=1024)
```

```
REQ: PROV-04 (H-Darrieus lock)
  Given: A YAML record with `provenance.method: ai_extracted` AND `confidence.score: 0.90` AND no `reviewer` field
  When: `python scripts/validate.py instances/<the-record>` runs
  Then: validate.py exits non-zero with a message identifying the H-Darrieus rule
  And: The same record with `reviewer` populated and method changed to `hybrid_reviewed` passes
```

PRD v1 will populate this pattern for all 94 requirements.

***

## 8. Cross-references

- **What this project IS:** [PROJECT.md](../PROJECT.md)
- **Full requirement inventory (94 IDs):** [REQUIREMENTS.md](../REQUIREMENTS.md)
- **Phase plan with success criteria:** [ROADMAP.md](../ROADMAP.md)
- **Tech stack rationale:** [research/STACK.md](../research/STACK.md)
- **Architecture (component map, data flow, anti-patterns):** [research/ARCHITECTURE.md](../research/ARCHITECTURE.md)
- **Research synthesis (pinned decisions, open questions):** [research/SUMMARY.md](../research/SUMMARY.md)
- **Pitfalls (12 critical, with prevention guidance):** [research/PITFALLS.md](../research/PITFALLS.md)
- **Project-level Claude Code conventions:** [../CLAUDE.md](../../CLAUDE.md)
- **Repo entry point + AI handoff:** [../README.md](../../README.md)

***

## 9. Change log

| Version | Date | Author | Change |
|---------|------|--------|--------|
| v0 | 2026-05-03 | gsd-planner-phase / Phase 1 / Plan 05 | Initial directional PRD |
| (v1 pending Phase 6) | TBD | TBD | Final contractual PRD with per-requirement acceptance criteria |

***

*PRD v0 — directional. PRD v1 (Phase 6) is the contractual final version.*
*Last touched by: gsd-planner-phase / Phase 1 / Plan 05 / 2026-05-03*
```

Notes for the executor:
- Do NOT cut sections. Every section above is load-bearing for downstream phases.
- Do NOT promote any "directional" item to "locked" — only Constraints, Tech Stack, Out-of-Scope, and Core Value are locked in v0. Everything else is directional and tightens in PRD v1.
- Do NOT add per-requirement acceptance criteria here — that is PRD v1's job. The placeholder section is intentional.
- Cross-reference paths use relative form (`../PROJECT.md`, `../research/SUMMARY.md`) because PRD lives at `.planning/design/PRD_v0.md` and target docs are one level up.
- Bilingual ZH/EN where it adds clarity; English-only where it would be noise.

Verify after writing:

```bash
cd /Users/Zhuanz/aviation-knowledge-base
test -f .planning/design/PRD_v0.md
wc -l .planning/design/PRD_v0.md
grep -c "^## " .planning/design/PRD_v0.md      # section count
grep -c "AI 接力开发指南" .planning/design/PRD_v0.md
grep -c "REPO-0\|PRD-0\|ONT-E\|ONT-R\|PROV-0\|VER-0\|VAL-0\|DOC-0\|RAG-0\|DEP-0\|DEMO-0\|AIH-0\|ROAD-0" .planning/design/PRD_v0.md   # REQ-ID coverage
```

Also run pre-commit on the new file (yamllint won't lint .md, but end-of-file-fixer and trailing-whitespace will):

```bash
~/.local/bin/pre-commit run --files .planning/design/PRD_v0.md 2>&1 | tail -5 || pre-commit run --files .planning/design/PRD_v0.md 2>&1 | tail -5
```
  </action>
  <verify>
    <automated>cd /Users/Zhuanz/aviation-knowledge-base &amp;&amp; test -f .planning/design/PRD_v0.md &amp;&amp; test "$(wc -l &lt; .planning/design/PRD_v0.md)" -ge 200 &amp;&amp; grep -q "^## AI 接力开发指南" .planning/design/PRD_v0.md &amp;&amp; grep -qE "^## 1\. Users" .planning/design/PRD_v0.md &amp;&amp; grep -qE "^## 2\. Scope" .planning/design/PRD_v0.md &amp;&amp; grep -qE "^## 3\. Non-Goals" .planning/design/PRD_v0.md &amp;&amp; grep -qE "^## 4\. Success Metrics" .planning/design/PRD_v0.md &amp;&amp; grep -qE "^## 5\. Deliverable List" .planning/design/PRD_v0.md &amp;&amp; grep -qE "^## 6\. Open Questions" .planning/design/PRD_v0.md &amp;&amp; grep -qE "^## 7\. Acceptance Criteria" .planning/design/PRD_v0.md &amp;&amp; echo OK</automated>
  </verify>
  <acceptance_criteria>
    - `test -f /Users/Zhuanz/aviation-knowledge-base/.planning/design/PRD_v0.md` exit 0
    - `wc -l /Users/Zhuanz/aviation-knowledge-base/.planning/design/PRD_v0.md` returns at least `200` (and at most ~500 — directional, not exhaustive)
    - PRD opens with `## AI 接力开发指南` section: `grep -q "^## AI 接力开发指南" PRD_v0.md` exit 0
    - All 7 mandated sections present (Users, Scope, Non-Goals, Success Metrics, Deliverable List, Open Questions, Acceptance Criteria placeholder): `grep -cE "^## (1\.|2\.|3\.|4\.|5\.|6\.|7\.)" PRD_v0.md` returns at least `7`
    - All 4 user archetypes named: `grep -cE "(航空工程师|CFD|项目经理|AI 编码助手)" PRD_v0.md` returns at least `4`
    - Out-of-Scope items match PROJECT.md: `grep -cE "(Dify|Neo4j|Vue/React|OCR|RAGFlow OIDC|S1000D|AP233)" PRD_v0.md` returns at least `5`
    - REQ-ID coverage: `grep -E "(REPO-0|PRD-0|ONT-E|ONT-R|PROV-0|VER-0|VAL-0|DOC-0|RAG-0|DEP-0|DEMO-0|AIH-0|ROAD-0)" PRD_v0.md | wc -l` returns at least `13` (one match per category)
    - All 6 phases referenced in Deliverable List: `grep -cE "Phase [1-6]" PRD_v0.md` returns at least `6`
    - Cross-references to all key planning docs: `grep -cE "\.\./(PROJECT|REQUIREMENTS|ROADMAP|research/(SUMMARY|ARCHITECTURE|PITFALLS|STACK))\.md" PRD_v0.md` returns at least `5`
    - Acceptance Criteria section EXPLICITLY defers detail to PRD v1: `grep -q "PRD v1" PRD_v0.md` exit 0
    - Pre-commit passes on the new file: `pre-commit run --files .planning/design/PRD_v0.md` exit 0
  </acceptance_criteria>
  <done>PRD v0 exists at `.planning/design/PRD_v0.md` with all 7 mandated sections; opens with AI handoff guide; 200-500 lines; cross-references all relevant planning docs; defers contractual acceptance criteria to PRD v1.</done>
</task>

</tasks>

<verification>
Phase-1 Plan-05 is complete when:
- [ ] `.planning/design/` directory exists with `.gitkeep`
- [ ] `.planning/design/PRD_v0.md` exists with line count 200-500
- [ ] PRD opens with `## AI 接力开发指南` section
- [ ] All 7 mandated sections present in order (Users, Scope, Non-Goals, Success Metrics, Deliverable List, Open Questions, Acceptance Criteria placeholder)
- [ ] All 4 user archetypes from PROJECT.md represented
- [ ] All Out-of-Scope items from PROJECT.md echoed
- [ ] All 6 phases mapped to deliverables with REQ-IDs
- [ ] Open Questions inherits from research/SUMMARY.md and adds 5 PRD-level ones
- [ ] Acceptance Criteria placeholder explicitly defers to PRD v1
- [ ] Pre-commit passes on the new file
</verification>

<success_criteria>
- Downstream phases (2-6) have a single point of reference for "is feature X in v1 scope?" (PRD-01)
- AI 接力开发指南 discipline now established in two places (README + first design doc) — sets the precedent for every subsequent design doc
- All 94 v1 REQ-IDs touchable through the Deliverable List (traceability check)
- Open Questions log is real, not aspirational — every question has a phase resolution target
- PRD v0 frozen at end of Phase 1; PRD v1 (Phase 6) is the contractual successor
</success_criteria>

<output>
After completion, create `.planning/phases/01-repo-skeleton-git-baseline-prd-v0/01-05-SUMMARY.md` documenting:
- Files created (`.planning/design/.gitkeep`, `.planning/design/PRD_v0.md`)
- PRD line count
- Section count and section names verified
- REQ-ID category coverage count
- Cross-reference link count
- 5-minute stranger test self-run on the PRD itself (executor reports orienting from PRD alone in ≤5 min)
- Open Questions inherited from research/SUMMARY.md (count) + PRD-level new ones added (count)
</output>

# PRD v1 — Aviation Knowledge Base MVP (Final, Contractual)

**Version:** v1.0.0
**Status:** Phase 6 deliverable — FINAL, CONTRACTUAL
**Replaces:** [.planning/design/PRD_v0.md](./PRD_v0.md) (directional, frozen at end of Phase 1)
**Replaced by:** nothing (v2 PRD will be authored when [.planning/ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md) triggers fire)
**Authors:** Phase 6 / plan 06-04 / Claude Opus 4.7 (1M context) / 2026-05-03
**Source documents:**
- [.planning/PROJECT.md](../PROJECT.md) (Core Value)
- [.planning/REQUIREMENTS.md](../REQUIREMENTS.md) (94 v1 REQ-IDs)
- [.planning/ROADMAP.md](../ROADMAP.md) (6 phases, success criteria)
- [.planning/research/STACK.md](../research/STACK.md), [ARCHITECTURE.md](../research/ARCHITECTURE.md), [PITFALLS.md](../research/PITFALLS.md), [SUMMARY.md](../research/SUMMARY.md), [FEATURES.md](../research/FEATURES.md)
- [.planning/design/PRD_v0.md](./PRD_v0.md), [.planning/design/RAG_PIPELINE.md](./RAG_PIPELINE.md)
- [deploy/docker-compose.yml.draft](../../deploy/docker-compose.yml.draft), [deploy/topology.md](../../deploy/topology.md), [deploy/wiki-git-storage.md](../../deploy/wiki-git-storage.md), [deploy/authentik-phase2.md](../../deploy/authentik-phase2.md), [deploy/backup-restore.md](../../deploy/backup-restore.md)
- [.planning/ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md)
- [docs/GLOSSARY.md](../../docs/GLOSSARY.md), [docs/README.md](../../docs/README.md)
- [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md), [ontology/VERSION](../../ontology/VERSION)
- [process-log/README.md](../../process-log/README.md)

***

## 0. AI 接力开发指南

> A fresh Claude / Codex / DeepSeek session reading ONLY this file should be
> able to (a) describe what the v1 system delivers, (b) point at every
> implementation artifact by path, (c) verify any of the 94 v1 REQ-IDs is
> met, and (d) know what is deferred and the trigger to revisit. If any of
> (a)–(d) cannot be answered from this doc alone, log it as a defect against
> this PRD and patch in the same PR.

### What this document IS

The single contractual reference for the v1.0.0 release. It synthesizes
every locked decision made across phases 1–6 with per-requirement acceptance
criteria. After this PRD signs off in
[ontology/CHANGELOG.md](../../ontology/CHANGELOG.md), no v1 work is
authorized that contradicts it.

The four invariants this PRD defends (any one violated = release blocked):

1. **Truth + citation**: every record has a structured `source.{document_id, locator, retrieval, effective_date}`; every AI answer has a `[CITE:c_<8hex>]` token resolving to retrieved chunks.
2. **Provenance discipline**: H-Darrieus REJECT rule is schema-enforced; AI-extracted records cannot reach canonical without `hybrid_reviewed` + populated reviewer.
3. **Audit trail**: Git is truth; every schema change is paired with a [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md) entry; every phase has a [process-log/](../../process-log/) completion log.
4. **Bilingual + AI-handoff**: every design doc carries an "AI 接力开发指南" section; [docs/GLOSSARY.md](../../docs/GLOSSARY.md) seeds ≥50 ZH/EN terms; the 5-minute stranger test passes on ≥3 sampled design docs (verified by plan 06-05).

### What this document is NOT

- Not a tutorial — it assumes the reader knows the v1 stack
  ([.planning/research/STACK.md](../research/STACK.md)) and the audit
  philosophy ([.planning/PROJECT.md](../PROJECT.md) Core Value).
- Not a substitute for the implementation artifacts — it CITES them by
  path (every section ends with the canonical path of the underlying spec).
- Not a v2 plan — [.planning/ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md) is
  the v2+ posture with measurable promote-when triggers.
- Not running infrastructure — `deploy/*` is DRAFT; no services run in v1.

### Locked vs Directional (final pass)

| Item | Status | Anchor |
|------|--------|--------|
| Core Value (truth + citation + provenance + bilingual + audit) | **Locked (canonical)** | §1 |
| Tech stack (Wiki.js 2.5.314 / RAGFlow 0.25.1 / Postgres 16 / Caddy 2 / Authentik DEFERRED) | **Locked (canonical)** | §3, [STACK.md](../research/STACK.md) |
| Schema set (17 baseline entities + ADR-002 additions = 22 entity types; 13 baseline + ADR-003 = 16 relation types) | **Locked (canonical)** | §4, [ontology/schemas/](../../ontology/schemas/) |
| Provenance / Confidence / Source structured objects + H-Darrieus REJECT rule | **Locked (canonical)** | §4, [ontology/_meta.schema.json](../../ontology/_meta.schema.json) |
| Validator pipeline (schema + ids + relations + provenance + links) | **Locked (canonical)** | §5, [scripts/validate.py](../../scripts/validate.py) |
| RAG pipeline contract (chunking / BGE-M3 / hybrid+RRF / `[CITE:c_<8hex>]` / guardrail) | **Locked (canonical)** | §6, [RAG_PIPELINE.md](./RAG_PIPELINE.md) Locked table |
| Deployment posture (single-host docker-compose, DRAFT not running, Authentik commented out) | **Locked (canonical)** | §7, [deploy/](../../deploy/) |
| Out-of-scope (v1) per CLAUDE.md | **Locked (canonical)** | §10 |
| v2+ promote-when triggers | **Locked (canonical)** | §8, [ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md) |
| Per-REQ acceptance criteria | **Locked (canonical)** | §9 |
| Open questions (PRD_v0 §6.1 / §6.2; RAG_PIPELINE §9) | All resolved or moved to ROADMAP_FUTURE | §11 |

### How to read this PRD

§1 Vision → §2 Users → §3 Stack → §4 Schema → §5 Validators → §6 RAG → §7 Deployment → §8 Roadmap → §9 Acceptance → §10 Out of Scope + Risks → §11 Open Questions Resolution → §12 Sign-off → Appendix A Cross-reference index.

§9 (Acceptance) is the contract — every v1 REQ-ID is listed with its
phase, artifact path, and verification command. A future auditor running
those commands on the v1.0.0 tag should observe all 94 PASS.

### How to update this PRD

PRD v1 is FROZEN at sign-off (the [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md)
entry written by plan 06-04 task 2). Updates require:

1. An ADR in [.planning/decisions/](../decisions/) documenting the proposed
   change with rationale.
2. User approval (per CLAUDE.md GSD workflow enforcement).
3. A new PRD version (PRD v1.1, PRD v2, etc.) — NOT an in-flight edit.

The only in-flight edits permitted are:

- Typo fixes
- Cross-link repair if a target file moves
- Marking a Resolved open question as Closed in §11 (with a [CHANGELOG](../../ontology/CHANGELOG.md) entry)

### 5-minute stranger test checklist

A fresh Claude / Codex / DeepSeek session reading this PRD should answer
ALL of these in 5 minutes:

- [ ] Q: What is the Core Value invariant? → §1 (truth + citation + provenance + bilingual + audit)
- [ ] Q: What stack does v1 lock? → §3 (Wiki.js 2.5.314 + RAGFlow 0.25.1 + Postgres 16 + Caddy)
- [ ] Q: How many entity / relation types? → §4 (22 entity / 16 relation, schema_version 0.1.0)
- [ ] Q: What enforces "no AI answer without citation"? → §6 (system-side `[CITE:c_<8hex>]` injection + post-generation validator)
- [ ] Q: Why isn't Authentik in v1? → §7, [deploy/authentik-phase2.md](../../deploy/authentik-phase2.md) (RAGFlow OIDC bug #12568 + FR #3495 upstream blockers)
- [ ] Q: When can OCR be added? → §8, [ROADMAP_FUTURE.md §4](../ROADMAP_FUTURE.md) (≥5 scanned-only PDFs OR named-deliverable demand OR ≥3 contributors over 3 months)
- [ ] Q: How is REQ-ID PROV-04 verified? → §9.2 (pytest case + ai_extracted-without-reviewer fixture in [tests/fixtures/invalid/](../../tests/fixtures/invalid/))
- [ ] Q: Where does the sign-off land? → §12, [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md)

If any answer is "TBD" or requires reading another doc, this PRD has
regressed and must be patched before the v1.0.0 release tag.

***

## 1. Vision

**Core Value (immutable, mirrored from [PROJECT.md](../PROJECT.md)):**
**每一条知识都可追溯来源，每一个 AI 回答都有 citation；schema 可演化、版本化、对人类和 AI 都可读。**
*Every piece of knowledge has a traceable source; every AI answer has a
citation; the schema is evolvable, versioned, and readable by both humans
and AI.*

The v1 system is an **engineering-grade aviation knowledge base baseline**.
Not a chat product, not a graph database, not an agent platform. It is the
foundation those things would be built on, with the audit + provenance +
citation discipline locked at schema time so future feature work cannot
erode it.

The four dimensions of Core Value, each defended by a specific v1 mechanism:

1. **Traceability** — every entity/relation carries `source.{document_id, locator, retrieval, effective_date}` enforced by [ontology/_meta.schema.json](../../ontology/_meta.schema.json) (PROV-03). Free-text source strings (Pitfall 1) are schema-rejected; CI fails the PR.
2. **Citation** — RAG answers carry system-injected `[CITE:c_<8hex>]` tokens that the LLM cannot author or fabricate (Pitfall 8). A post-generation validator drops answers whose citations don't resolve to retrieved chunks (RAG-04 / RAG-05, [RAG_PIPELINE.md §5](./RAG_PIPELINE.md)).
3. **Audit** — Git is the truth source; every schema change pairs with a [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md) entry (VER-02) and every phase pairs with a [process-log/](../../process-log/) completion log (AIH-03). PR + CHANGELOG is mandatory per CLAUDE.md Constraints.
4. **Evolvability** — `ontology/VERSION` is semver; per-record `schema_version` lets validators reject ≤N-1 records; [migrations/PATTERN.md](../../ontology/migrations/PATTERN.md) documents the YAML→YAML migration script convention (VER-01..04).

The audience is NOT a general user. It's:

- **Aerospace engineer** who wants source-grounded regulation lookups (no
  "FAR Part 25 says..." with no page reference).
- **CFD / airworthiness researcher** who has been burned by AI hallucinating
  chart data (the H-Darrieus Case 3 incident — see CLAUDE.md §"CFD Benchmark
  Report 项目"). The H-Darrieus REJECT rule (PROV-04) is named after this.
- **Project manager / decision-maker** who needs the "why did we choose X"
  answer to be reconstructible from Git + [process-log/](../../process-log/).
- **Inheriting AI coding assistant** (Claude / Codex / DeepSeek) who picks
  up the project months later and resumes from cold context — the
  AI 接力开发指南 sections + [docs/GLOSSARY.md](../../docs/GLOSSARY.md) +
  [ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md) are the substrate for this.

***

## 2. Users

### 2.1 Primary archetypes (4)

**A. 航空工程师 / Aerospace Engineer**
*Critical need:* Citations that resolve to original page/section/clause.
Any answer without a verifiable citation is unusable.
*v1 acceptance signal:* Run a ≥10-query smoke test from
[evaluation/queries.yaml](../../evaluation/queries.yaml) against a populated
RAGFlow instance — every answer must have a `[CITE:c_<8hex>]` token whose
chunk_id resolves to a chunk that was actually retrieved (post-generation
validator, [RAG_PIPELINE.md §5.3](./RAG_PIPELINE.md)).

**B. CFD / 适航研究人员 / CFD & Airworthiness Researcher**
*Critical need:* Provenance discipline. Distinguish "verified with
experimental data" from "AI-extracted from a paper." Defends against the
H-Darrieus failure mode.
*v1 acceptance signal:* PROV-04 H-Darrieus REJECT fixture
([tests/fixtures/invalid/](../../tests/fixtures/invalid/) — `ai_extracted` +
`confidence > 0.85` + no `reviewer`) fails validation; promotion path from
[instances/_pending/](../../instances/_pending/) requires
`provenance.method = hybrid_reviewed` + populated `reviewer` + `reviewed_at`.

**C. 项目经理 / 决策者 / Project Manager & Decision-Maker**
*Critical need:* Audit trail. "Why did we choose method X?" answerable
from the KB.
*v1 acceptance signal:* For each phase 1–6, the
[process-log/phase-N-completion.md](../../process-log/) entry lists AI
session, decisions, deviations, verification commits. The [ROADMAP.md](../ROADMAP.md)
phase-success-criteria column maps to verification commands in §9 of this
PRD. [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md) records every
schema change with rationale.

**D. 接手开发的 AI 编码助手 / Inheriting AI Coding Assistant**
*Critical need:* Self-contained design docs, glossary, open-questions log,
decision trail.
*v1 acceptance signal:* AIH-01 enforces every `.planning/design/*.md` has
an "AI 接力开发指南" section (validator script
[scripts/validators/aih_section.py](../../scripts/validators/) — landed in
plan 06-05); AIH-02 5-minute stranger test passes on ≥3 sampled design
docs after a context-clean break (verified in plan 06-05 STRANGER-TEST.md);
AIH-04 [docs/GLOSSARY.md](../../docs/GLOSSARY.md) ships ≥50 bilingual
seed entries.

### 2.2 Out-of-scope users (v1)

- Multi-tenant external customers (no RBAC / multi-org in v1; trigger in
  [ROADMAP_FUTURE.md §5](../ROADMAP_FUTURE.md))
- General public (no public deployment in v1; confidentiality gating
  documented but not exercised)
- Real-time collaborators (Wiki.js handles narrative editing poorly; not
  a moat)

***

## 3. Stack

Locked tech choices (authoritative reference: [STACK.md](../research/STACK.md)).
Each row is a hard contract — alternatives can only re-enter via ADR.

| Component | Locked Choice | Why this over alternatives |
|-----------|---------------|----------------------------|
| Knowledge portal | **Wiki.js 2.5.314** (May 2026) | 3.0 still alpha (5+ years in dev) — DO NOT chase. 2.x is the stable plateau. Postgres-native, OIDC-ready, KaTeX built-in. BookStack/Outline/Confluence rejected (no native ZH/EN, vendor lock-in, or weaker than Wiki.js for our shape). |
| RAG pipeline | **RAGFlow v0.25.1** (Apr 30, 2026) | OpenDataLoader-PDF backend (~14× faster than DL parsers), native citation grounding, Chinese localization, hybrid retrieval. Dify excluded by CLAUDE.md Constraints. Custom LangChain stack rejected — RAGFlow is batteries-included. |
| Database | **PostgreSQL 16.x** | Wiki.js 3.0 will require Postgres-only — using 16 in 2.x ensures seamless future upgrade. MariaDB/SQLite path = full export/reimport. |
| Vector + sparse backend | **Elasticsearch 8.x** (RAGFlow bundled) | RAGFlow default; Infinity backend deferred. v0.25 added ES 9.x compat. |
| Reverse proxy | **Caddy 2.x** | TLS auto-issuance; simplest config of the three (Caddy / Traefik / nginx) considered. |
| Object store | **MinIO** (RAGFlow bundled) | S3-compatible; document originals + (optionally) Wiki.js asset uploads. Single bucket = single backup target. |
| Cache / queue | **Redis 7.x** | Wiki.js cache + RAGFlow task queue, single shared instance acceptable for v1 single-host. |
| Embedding | **BAAI/bge-m3** + **bge-reranker-v2-m3** | Multilingual ZH/EN, 8192 ctx, dense + sparse + colbert in one model — natural fit for hybrid retrieval (matches user's AeroPower-RAG pattern). Self-hosted via Ollama or RAGFlow Xinference. OpenAI/Voyage rejected (SaaS + cost); Nomic-v2 rejected (smaller, less ZH-strong). |
| Schema language | **YAML 1.2** + **JSON Schema Draft 2020-12** | Industry default; ajv/check-jsonschema/jsonschema (Python) all support 2020-12. Draft-04/07 missing `$defs`, `unevaluatedProperties`. |
| Validator | **check-jsonschema 0.37.1** + custom Python ([scripts/validators/](../../scripts/validators/)) | Native YAML support (no convert step), built-in pre-commit hook syntax, schema caching. Industry default in 2026. |
| Auth (v1) | **Local accounts on Wiki.js + RAGFlow separately** | SSO DEFERRED — RAGFlow OIDC bug #12568 + FR #3495 are upstream blockers. See [deploy/authentik-phase2.md](../../deploy/authentik-phase2.md). |
| Container runtime | **Docker 24.0+** / **docker-compose 2.26.1+** | RAGFlow hard requirements. K8s deferred — v1 single-host. |
| Document ingestion | **OpenDataLoader-PDF** (RAGFlow bundled v0.25 default) | ~14× faster than MinerU on 10K-page corpora; no GPU needed. DeepDoc reserved as fallback for OCR (deferred per [ROADMAP_FUTURE.md §4](../ROADMAP_FUTURE.md)). |

Authority: [.planning/research/STACK.md](../research/STACK.md) (full
"Alternatives Considered" tables, version compatibility matrix, hardware
sizing, sources).

***

## 4. Schema (Ontology v0.1.0)

[ontology/VERSION](../../ontology/VERSION) = `0.1.0`. Schema set defined in
Phase 2; one post-release patch in Phase 3 plan 03-01 (removed
`unevaluatedProperties: false` from intermediate composition bases — see
[ontology/CHANGELOG.md](../../ontology/CHANGELOG.md) for rationale).

### 4.1 Entities (22 = 17 baseline + 5 ADR-002 accepted)

Each entity has a JSON Schema in [ontology/schemas/entity.<type>.schema.json](../../ontology/schemas/).
All compose via `allOf` + `$ref` from [entity.base.schema.json](../../ontology/schemas/entity.base.schema.json),
which composes from [_meta.schema.json](../../ontology/_meta.schema.json) for the
base fields (id, type, version, schema_version, provenance, confidence,
source, tags, i18n).

Baseline (17):
**AircraftModel**, **AircraftSystem**, **Subsystem**, **Component**,
**Requirement**, **RegulationClause**, **Standard**, **Procedure**,
**FailureMode**, **MaintenanceTask**, **CFDMethod**, **SimulationCase**,
**MeshRequirement**, **TurbulenceModel**, **AccidentCase**, **Document**,
**ExpertNote**.

ADR-002 accepted (5):
**Material**, **TestCase**, **TestReport**, **Person**, **Organization**.

ADR-002 deferred to v0.2.0:
**Configuration / EffectivityRange** (D-03 — schema iteration cost not
justified at v1 corpus shape; field-level `effectivity_range` patterns
were ADR-evaluated but full entity deferred).

### 4.2 Relations (16 = 13 baseline + 3 ADR-003 accepted)

Each relation has a JSON Schema in [ontology/schemas/relation.<type>.schema.json](../../ontology/schemas/).
All compose from [relation.base.schema.json](../../ontology/schemas/relation.base.schema.json) which
adds `subject` (entity URI), `object` (entity URI), `valid_from`,
`valid_until` to the base meta fields.

Baseline (13):
**part_of**, **applicable_to**, **constrained_by**, **verified_by**,
**derived_from**, **supersedes**, **cites**, **causes**, **mitigated_by**,
**requires**, **equivalent_to**, **conflicts_with**, **used_in**.

ADR-003 accepted (3):
**interfaces_with**, **complies_with**, **applicable_during_phase**.

ADR-003 internalized as fields (not relations):
**has_revision** → `version_history[]` field (D-07 / ADR-004);
**generated_by** → `provenance.actor` + `source.tool` (D-09 / ADR-005).

### 4.3 Provenance / Confidence / Source contracts

Three structured objects mandatory on every record (PROV-01..03), defined
in [ontology/_meta.schema.json](../../ontology/_meta.schema.json) `$defs`:

- **`provenance`** — `method` enum (`human` / `ai_extracted` /
  `hybrid_reviewed`), `actor`, `actor_role`, `created_at`, optional
  `reviewer`, `reviewed_at`, `tool` (e.g., `claude-opus-4-7`,
  `ragflow-0.25.1`).
- **`confidence`** — `score` (0.0–1.0), `rationale` (≥1 sentence; enum
  per ADR-005: `multi_source_agreement` / `single_authoritative_source` /
  `ai_extracted_unverified` / `expert_judgment` / `heuristic`), optional
  `calibration_method`.
- **`source`** — `document_id` (URI to a `Document` entity), `locator`
  (`page` and/or `section` and/or `paragraph`), `retrieval` (`url`,
  `retrieved_at`, `content_hash`), `effective_date` (mandatory for
  time-sensitive sources).

**H-Darrieus REJECT rule (PROV-04, locked in [ADR-005](../decisions/ADR-005-provenance-enum.md)):**
A record with `provenance.method = ai_extracted` AND
`confidence.score > 0.85` AND no `reviewer` is REJECTED at validation
time by [scripts/validators/provenance.py](../../scripts/validators/provenance.py).
[instances/_pending/](../../instances/_pending/) is the AI-extraction
quarantine; canonical promotion requires
`provenance.method = hybrid_reviewed` + populated `reviewer` +
`reviewed_at` (PROV-05). PROV-06 broken-ref check ensures
`source.document_id` resolves to an existing `Document` entity.

### 4.4 Schema versioning

[ontology/VERSION](../../ontology/VERSION) = semver; per-record
`schema_version` field (VER-03); [migrations/PATTERN.md](../../ontology/migrations/PATTERN.md)
+ `migrations/0_1_0_to_template.py.example` documents the convention
(`<from>_to_<to>.py` taking YAML → YAML via ruamel.yaml `YAML()` class
to preserve comments; VER-04). [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md)
records every change with rationale (VER-02).

URI scheme (locked in [ADR-001](../decisions/ADR-001-reserved.md) preamble):
`aviationkb://<type>/<slug>@<version>` (full canonical URI form);
`<type-prefix>:<kebab-slug>` (short form for cross-references inside YAML).

***

## 5. Validators

[scripts/validate.py](../../scripts/validate.py) (master entrypoint, VAL-01)
runs in single pass:

1. **schema validation** — [scripts/validators/schema.py](../../scripts/validators/schema.py): JSON Schema 2020-12 against entity + relation schemas (all 22 + 16 leaf schemas validated; intermediate composition bases skipped per the Phase 3 plan 03-01 patch noted in [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md)).
2. **id format check** — [scripts/validators/ids.py](../../scripts/validators/ids.py): URI scheme `aviationkb://<type>/<slug>@<version>` for canonical IDs.
3. **relation referent existence** — [scripts/validators/relations.py](../../scripts/validators/relations.py): subject + object entities resolve.
4. **provenance gate** — [scripts/validators/provenance.py](../../scripts/validators/provenance.py): H-Darrieus REJECT, [_pending/](../../instances/_pending/) promotion gate, `schema_version` ≥ N-1.
5. **link check** — [scripts/validators/links.py](../../scripts/validators/links.py): broken-ref + supersession integrity (no cycles, no breaks).

Per-rule validators are independently importable as Python modules with
documented public functions (VAL-02). Each `scripts/validators/*.py` exposes
a `validate(records, registry) -> list[ValidationError]` function;
[scripts/validators/errors.py](../../scripts/validators/errors.py) defines
the canonical error shape; [scripts/validators/loader.py](../../scripts/validators/loader.py)
handles YAML loading with [scripts/validators/README.md](../../scripts/validators/README.md)
documenting the public API.

Test fixtures: [tests/fixtures/{valid,invalid}/](../../tests/fixtures/)
covering every entity type, relation type, [_pending/](../../instances/_pending/)
promotion path, supersession chain, ai_extracted-without-reviewer rejection
(VAL-03 — partial in v1: valid corpus complete; invalid corpus 12 fixtures,
one per failure mode, per Phase 3 plan 03-02).

CI: [.github/workflows/](../../.github/workflows/) GitHub Actions runs
[validate.py](../../scripts/validate.py) + `pytest` on every push/PR;
blocks merge on failure (VAL-05). Pre-commit local hook
([.pre-commit-config.yaml](../../.pre-commit-config.yaml)) runs the same
validators locally before commit (Phase 3 plan 03-06).

Authority: [scripts/validators/README.md](../../scripts/validators/README.md)
(per-validator behavior contracts); Phase 3 plan SUMMARYs
([.planning/phases/03-validators-ci-active/03-{01..06}-SUMMARY.md](../phases/03-validators-ci-active/))
for execution detail.

***

## 6. RAG Pipeline (design contract)

The Phase 5 design doc [.planning/design/RAG_PIPELINE.md](./RAG_PIPELINE.md)
is the authoritative contract. PRD v1 mirrors its Locked-vs-Directional
table here for reference:

| Item | Locked? | Notes |
|------|---------|-------|
| RAGFlow 0.25.1 + OpenDataLoader-PDF | **Locked** | From [STACK.md](../research/STACK.md); no alternative considered in v1 |
| BGE-M3 default + bge-reranker-v2-m3 | **Locked (default)** | Mini-benchmark may swap if Phase 7 measures a clear winner per [RAG_PIPELINE.md §3.3](./RAG_PIPELINE.md) |
| Chunk size 512 / max 1024 / overlap 64 | **Locked (defaults)** | [RAG_PIPELINE.md §2.3](./RAG_PIPELINE.md) — atomic blocks override size cap |
| Atomic-chunk rules: tables, equations, regulation §-clauses, figure-captions | **Locked** | [RAG_PIPELINE.md §2.2](./RAG_PIPELINE.md) — Pitfall 6 prevention; CANNOT relax |
| Hybrid retrieval (vector + BM25 + RRF, k=60) | **Locked** | [RAG_PIPELINE.md §4](./RAG_PIPELINE.md) — AeroPower-RAG-validated |
| Synonym expansion weight 0.3 | **Locked** | [RAG_PIPELINE.md §4.2 / §7.2](./RAG_PIPELINE.md) — AeroPower-RAG-validated; Pitfall 7 |
| Citation token format `[CITE:c_<8hex>]` | **Locked** | [RAG_PIPELINE.md §5.1](./RAG_PIPELINE.md) — Pitfall 8 prevention; CANNOT change without ADR |
| LLM forbidden to self-author citations | **Locked** | [RAG_PIPELINE.md §5.1](./RAG_PIPELINE.md) — Pitfall 8; Core Value defender |
| Post-generation citation validator | **Locked** | [RAG_PIPELINE.md §5.3](./RAG_PIPELINE.md) — rejects unresolved chunk_ids |
| `min_chunk_score = 0.5` | **Locked** | [RAG_PIPELINE.md §6.1](./RAG_PIPELINE.md) — Pitfall 9 prevention; tunable per Phase 7 measurement only |
| `min_chunks_required = 2` | **Locked** | [RAG_PIPELINE.md §6.1](./RAG_PIPELINE.md) — single-hit retrieval too brittle |
| Canned no-context response (ZH + EN) | **Locked** | [RAG_PIPELINE.md §6.2](./RAG_PIPELINE.md) — text is contractual; localization changes are translation only |
| LLM-not-called on guardrail trip | **Locked** | [RAG_PIPELINE.md §6.3](./RAG_PIPELINE.md) — pipeline branch, NOT prompt instruction |
| Cross-lingual eval ≥6 in [evaluation/queries.yaml](../../evaluation/queries.yaml) | **Locked** | RAG-07; verified by [05-COVERAGE.md](../phases/05-rag-pipeline-design/05-COVERAGE.md) |
| Out-of-scope eval ≥3 in [evaluation/queries.yaml](../../evaluation/queries.yaml) | **Locked** | RAG-07; verified by [05-COVERAGE.md](../phases/05-rag-pipeline-design/05-COVERAGE.md) |
| [to_ragflow.py](../../scripts/exporters/to_ragflow.py) CLI surface (`--rebuild`, `--dry-run`, `--since=`, `--paths`) | **Locked** | RAG-08 plan 05-03; argparse implemented |
| `compute_doc_id` rule (sha256 of path+content) | **Locked** | Idempotency contract |
| LLM choice (Ollama Qwen2.5 vs remote Claude/GPT) | **Directional** | Phase 6 deployment plan picks based on hardware reality |
| Mini-benchmark numbers | **Directional** | [RAG_PIPELINE.md §3.2](./RAG_PIPELINE.md) specifies the protocol; Phase 7 runs and updates §3.3 |

**Pitfall guards (locked at design time):**

- **Pitfall 6 (chunk destroys table)**: atomic-block rules in
  [RAG_PIPELINE.md §2.2](./RAG_PIPELINE.md) — tables, equations,
  regulation §-clauses, figure-captions are atomic.
- **Pitfall 8 (citation hallucination)**: system-side `[CITE:c_<8hex>]`
  injection — the LLM never sees full citation text; cannot self-author;
  post-gen validator drops unresolved tokens.
- **Pitfall 9 (no-result hallucination)**: hard-coded threshold
  short-circuit; LLM not called when `retrieved_chunks=[]` or
  `max(scores) < min_chunk_score`.

[evaluation/queries.yaml](../../evaluation/queries.yaml) ships ≥30 queries
(≥6 cross-lingual, ≥3 out-of-scope, ≥20% table-query) as the input to a
future Phase 7 eval run.

[scripts/exporters/to_ragflow.py](../../scripts/exporters/to_ragflow.py)
skeleton (Phase 5 plan 05-03) locks CLI surface: `--rebuild`, `--dry-run`,
`--since=`, `--paths`. Idempotent re-upload via content hash
(`compute_doc_id` = sha256 of path + content).

***

## 7. Deployment

DRAFT only — **no services run in v1**. Phase 6 plan 06-01 deliverables
(all under [deploy/](../../deploy/)):

- [deploy/docker-compose.yml.draft](../../deploy/docker-compose.yml.draft) — Wiki.js 2.5.314 + Postgres 16 + RAGFlow 0.25.1 + Elasticsearch 8 + MinIO + Redis 7 + Caddy 2 services; Authentik service block commented out. Marked `# DRAFT — NOT FOR PRODUCTION` at the top.
- [deploy/.env.example](../../deploy/.env.example) — every env var with a `<CHANGE_ME>` placeholder; no hardcoded secrets; password-generation tips at the top.
- [deploy/topology.md](../../deploy/topology.md) — ASCII + Mermaid diagrams showing Git ↔ Wiki.js ↔ RAGFlow ↔ Caddy data flow; Postgres + Redis + MinIO + Elasticsearch as the stateful tier.
- [deploy/wiki-git-storage.md](../../deploy/wiki-git-storage.md) — DEP-04 hard rule: **Wiki.js Git scope = `wiki/` ONLY**, never the full repo (otherwise Wiki.js editing would mutate `ontology/` YAML and break schema integrity).
- [deploy/authentik-phase2.md](../../deploy/authentik-phase2.md) — DEP-05: SSO DEFERRED; references RAGFlow OIDC bug **#12568** (Keycloak redirect-loop since Quart migration) + feature-request **#3495** (OIDC support overall) as the upstream blockers; documents the `authentik` compose service block + Wiki.js OIDC integration that will be uncommented when [ROADMAP_FUTURE.md §6](../ROADMAP_FUTURE.md) trigger fires.
- [deploy/backup-restore.md](../../deploy/backup-restore.md) — DEP-06: Postgres dump + Git push are the **truth backup**; vector store + Elasticsearch indexes are **rebuildable derivatives** (regenerate via `python scripts/exporters/to_ragflow.py --rebuild`). MinIO is backed up as document originals. Off-host destination + RTO/RPO documented.

To promote to a real deployment:

1. Copy [deploy/docker-compose.yml.draft](../../deploy/docker-compose.yml.draft) → `docker-compose.yml` (drop `.draft` suffix).
2. Copy [deploy/.env.example](../../deploy/.env.example) → `.env` (gitignored), replace every `<CHANGE_ME>` (use `openssl rand -hex 24` for passwords, `openssl rand -hex 32` for secret keys).
3. Fill `deploy/caddy/Caddyfile` from the template (TLS hostnames, reverse-proxy paths).
4. Decide SSO posture: leave Authentik commented out (v1 path), or wait for [ROADMAP_FUTURE.md §6](../ROADMAP_FUTURE.md) trigger conditions to fire (RAGFlow #12568 closed AND #3495 merged ≥0.26.0 AND ≥2 confirmed user accounts demanding cross-service SSO).
5. `docker compose up -d` and run the post-up smoke test from [deploy/topology.md](../../deploy/topology.md).

Authority: each `deploy/*.md` is the canonical spec for its concern.

***

## 8. Roadmap

**v1 (this release):** complete after PRD v1 sign-off in
[ontology/CHANGELOG.md](../../ontology/CHANGELOG.md). 94 v1 REQ-IDs covered
across 6 phases (verification matrix in §9). Phase distribution per
[ROADMAP.md](../ROADMAP.md):

- Phase 1 (Repo Skeleton + PRD v0): 6 REQs
- Phase 2 (Ontology Schema v0.1.0): 51 REQs
- Phase 3 (Validators + CI Active): 5 REQs
- Phase 4 (Demo Data + Doc Import): 11 REQs
- Phase 5 (RAG Pipeline Design): 8 REQs
- Phase 6 (Deployment + PRD v1 + Roadmap + AIH Polish): 13 REQs

**v2+ (deferred):** see [.planning/ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md).
Seven feature areas, each with explicit "Promote when X" triggers:

1. **GraphRAG Layer** — promote when ≥10K instances OR ≥5 multi-hop eval failures OR named path-query use case
2. **Agent Layer** — promote when [_pending/](../../instances/_pending/) ≥100 records sustained AND PROV-04 stable ≥3 months AND named failure pattern
3. **Graph DB Backend (Neo4j / Nebula)** — promote when GraphRAG fired AND A/B win on ≥3 query categories AND concurrent-write bottleneck AND ADR signed
4. **OCR Pipeline** — promote when ≥5 scanned-only PDFs OR named-deliverable demand OR ≥3 contributors over 3 months
5. **Multi-tenant RBAC** — promote when ≥2 orgs sharing deployment AND single-org auth proven insufficient AND RBAC ADR signed AND SSO-prereq met
6. **SSO Unification (Authentik)** — promote when RAGFlow #12568 CLOSED AND #3495 merged ≥0.26.0 AND ≥2 cross-service accounts demanding it
7. **Decision Agent** — promote when RAG Q&A stable ≥6 months citation-failure ≤1% AND named multi-step deliverable AND provenance-ADR signed AND Agent Layer (§2) substrate proven

Each trigger has measurable counts, dates, upstream events, eval-set
failures, or documented user demand. No vague "someday" entries (per
maintainer note in [ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md): the trigger
IS the promise).

***

## 9. Acceptance — per-requirement criteria

**The contract.** For each REQ-ID, this section lists: phase, artifact
path(s), verification command. A future auditor running these commands on
the v1.0.0 tag should observe all 94 PASS. Phase 1–5 entries are concise
(artifacts already shipped — see [ROADMAP.md](../ROADMAP.md) success
criteria + per-plan SUMMARY files in [.planning/phases/](../phases/) for
detail). Phase 6 entries (the unique deliverables of this PRD's phase) are
verbose.

### 9.1 Repository & CI Baseline (Phase 1) — 6 REQs

| REQ | Phase | Artifact | Verification |
|-----|-------|----------|--------------|
| REPO-01 | 1 | top-level dirs `ontology/`, `instances/`, `docs/`, `wiki/`, `deploy/`, `scripts/`, `tests/`, `evaluation/`, `process-log/` | `find ontology instances docs wiki deploy scripts tests evaluation process-log -maxdepth 0 -type d` lists all 9 |
| REPO-02 | 1 | [.gitattributes](../../.gitattributes) | `grep -E "\.(pdf\|docx\|xlsx\|pptx) filter=lfs" .gitattributes` |
| REPO-03 | 1 | [README.md](../../README.md) | `grep -q "AI 接力开发指南" README.md` |
| REPO-04 | 1 | [.github/workflows/](../../.github/workflows/) | green CI run on the v1.0.0 tag (post-Phase-3 activation) |
| REPO-05 | 1 | [.pre-commit-config.yaml](../../.pre-commit-config.yaml) | `pre-commit run --all-files` exit 0 |
| PRD-01 | 1 | [.planning/design/PRD_v0.md](./PRD_v0.md) | file exists, marked superseded by [PRD_v1.md](./PRD_v1.md) (this file) — bidirectional cross-link in both files |

### 9.2 Ontology (Phase 2) — 51 REQs

**Entities (22 = 17 baseline + 5 ADR-002 accepted, ONT-E-01..22)** — each
has a JSON Schema in [ontology/schemas/entity.<type>.schema.json](../../ontology/schemas/);
verification: `check-jsonschema --check-metaschema ontology/schemas/entity.*.schema.json` exit 0.

| REQ | Entity | Schema path |
|-----|--------|-------------|
| ONT-E-01 | Base entity | [entity.base.schema.json](../../ontology/schemas/entity.base.schema.json) |
| ONT-E-02 | AircraftModel | [entity.aircraft-model.schema.json](../../ontology/schemas/entity.aircraft-model.schema.json) |
| ONT-E-03 | AircraftSystem | [entity.aircraft-system.schema.json](../../ontology/schemas/entity.aircraft-system.schema.json) |
| ONT-E-04 | Subsystem | [entity.subsystem.schema.json](../../ontology/schemas/entity.subsystem.schema.json) |
| ONT-E-05 | Component | [entity.component.schema.json](../../ontology/schemas/entity.component.schema.json) |
| ONT-E-06 | Requirement | [entity.requirement.schema.json](../../ontology/schemas/entity.requirement.schema.json) |
| ONT-E-07 | RegulationClause | [entity.regulation-clause.schema.json](../../ontology/schemas/entity.regulation-clause.schema.json) |
| ONT-E-08 | Standard | [entity.standard.schema.json](../../ontology/schemas/entity.standard.schema.json) |
| ONT-E-09 | Procedure | [entity.procedure.schema.json](../../ontology/schemas/entity.procedure.schema.json) |
| ONT-E-10 | FailureMode | [entity.failure-mode.schema.json](../../ontology/schemas/entity.failure-mode.schema.json) |
| ONT-E-11 | MaintenanceTask | [entity.maintenance-task.schema.json](../../ontology/schemas/entity.maintenance-task.schema.json) |
| ONT-E-12 | CFDMethod | [entity.cfd-method.schema.json](../../ontology/schemas/entity.cfd-method.schema.json) |
| ONT-E-13 | SimulationCase | [entity.simulation-case.schema.json](../../ontology/schemas/entity.simulation-case.schema.json) |
| ONT-E-14 | MeshRequirement | [entity.mesh-requirement.schema.json](../../ontology/schemas/entity.mesh-requirement.schema.json) |
| ONT-E-15 | TurbulenceModel | [entity.turbulence-model.schema.json](../../ontology/schemas/entity.turbulence-model.schema.json) |
| ONT-E-16 | AccidentCase | [entity.accident-case.schema.json](../../ontology/schemas/entity.accident-case.schema.json) |
| ONT-E-17 | Document | [entity.document.schema.json](../../ontology/schemas/entity.document.schema.json) |
| ONT-E-18 | ExpertNote | [entity.expert-note.schema.json](../../ontology/schemas/entity.expert-note.schema.json) |
| ONT-E-19 | Material (ADR-002 accepted) | [entity.material.schema.json](../../ontology/schemas/entity.material.schema.json) |
| ONT-E-20 | TestCase + TestReport (ADR-002 accepted) | [entity.test-case.schema.json](../../ontology/schemas/entity.test-case.schema.json) + [entity.test-report.schema.json](../../ontology/schemas/entity.test-report.schema.json) |
| ONT-E-21 | Configuration / EffectivityRange (DEFERRED to v0.2.0 per ADR-002) | rationale in [ADR-002](../decisions/ADR-002-entity-additions.md) |
| ONT-E-22 | Person + Organization (ADR-002 accepted) | [entity.person.schema.json](../../ontology/schemas/entity.person.schema.json) + [entity.organization.schema.json](../../ontology/schemas/entity.organization.schema.json) |

**Relations (16 = 13 baseline + 3 ADR-003 accepted, ONT-R-01..19)** — each
has a JSON Schema in [ontology/schemas/relation.<type>.schema.json](../../ontology/schemas/);
verification: `check-jsonschema --check-metaschema ontology/schemas/relation.*.schema.json` exit 0.

| REQ | Relation | Schema path |
|-----|----------|-------------|
| ONT-R-01 | Base relation | [relation.base.schema.json](../../ontology/schemas/relation.base.schema.json) |
| ONT-R-02 | part_of | [relation.part-of.schema.json](../../ontology/schemas/relation.part-of.schema.json) |
| ONT-R-03 | applicable_to | [relation.applicable-to.schema.json](../../ontology/schemas/relation.applicable-to.schema.json) |
| ONT-R-04 | constrained_by | [relation.constrained-by.schema.json](../../ontology/schemas/relation.constrained-by.schema.json) |
| ONT-R-05 | verified_by | [relation.verified-by.schema.json](../../ontology/schemas/relation.verified-by.schema.json) |
| ONT-R-06 | derived_from | [relation.derived-from.schema.json](../../ontology/schemas/relation.derived-from.schema.json) |
| ONT-R-07 | supersedes | [relation.supersedes.schema.json](../../ontology/schemas/relation.supersedes.schema.json) |
| ONT-R-08 | cites | [relation.cites.schema.json](../../ontology/schemas/relation.cites.schema.json) |
| ONT-R-09 | causes | [relation.causes.schema.json](../../ontology/schemas/relation.causes.schema.json) |
| ONT-R-10 | mitigated_by | [relation.mitigated-by.schema.json](../../ontology/schemas/relation.mitigated-by.schema.json) |
| ONT-R-11 | requires | [relation.requires.schema.json](../../ontology/schemas/relation.requires.schema.json) |
| ONT-R-12 | equivalent_to | [relation.equivalent-to.schema.json](../../ontology/schemas/relation.equivalent-to.schema.json) |
| ONT-R-13 | conflicts_with | [relation.conflicts-with.schema.json](../../ontology/schemas/relation.conflicts-with.schema.json) |
| ONT-R-14 | used_in | [relation.used-in.schema.json](../../ontology/schemas/relation.used-in.schema.json) |
| ONT-R-15 | interfaces_with (ADR-003 accepted) | [relation.interfaces-with.schema.json](../../ontology/schemas/relation.interfaces-with.schema.json) |
| ONT-R-16 | complies_with (ADR-003 accepted) | [relation.complies-with.schema.json](../../ontology/schemas/relation.complies-with.schema.json) |
| ONT-R-17 | has_revision (INTERNALIZED as field per ADR-004 D-07) | `version_history[]` field on entity base; rationale in [ADR-004](../decisions/ADR-004-field-shapes.md) |
| ONT-R-18 | applicable_during_phase (ADR-003 accepted) | [relation.applicable-during-phase.schema.json](../../ontology/schemas/relation.applicable-during-phase.schema.json) |
| ONT-R-19 | generated_by (INTERNALIZED as field per ADR-005 D-09) | `provenance.actor` + `source.tool`; rationale in [ADR-005](../decisions/ADR-005-provenance-enum.md) |

**Provenance (PROV-01..06):**

| REQ | Phase | Artifact | Verification |
|-----|-------|----------|--------------|
| PROV-01 | 2 | [_meta.schema.json](../../ontology/_meta.schema.json) `$defs.provenance` | `jq '."$defs".provenance.required' ontology/_meta.schema.json` includes `method`, `actor`, `actor_role`, `created_at` |
| PROV-02 | 2 | [_meta.schema.json](../../ontology/_meta.schema.json) `$defs.confidence` | `jq '."$defs".confidence.required' ontology/_meta.schema.json` includes `score`, `rationale` |
| PROV-03 | 2 | [_meta.schema.json](../../ontology/_meta.schema.json) `$defs.source` | `jq '."$defs".source.required' ontology/_meta.schema.json` includes `document_id`, `locator`, `retrieval`, `effective_date` |
| PROV-04 | 2 | [scripts/validators/provenance.py](../../scripts/validators/provenance.py) + [tests/fixtures/invalid/](../../tests/fixtures/invalid/) | `python scripts/validate.py tests/fixtures/invalid/h_darrieus_*.yaml` exit non-zero with rule-name in stderr |
| PROV-05 | 2 | [instances/_pending/README.md](../../instances/_pending/README.md) + [scripts/validators/provenance.py](../../scripts/validators/provenance.py) | promotion test fixture: ai_extracted in _pending validates; same record moved to canonical without `hybrid_reviewed` REJECTS |
| PROV-06 | 2 | [scripts/validators/links.py](../../scripts/validators/links.py) (broken-ref check) | fixture with `source.document_id` pointing to non-existent Document → REJECT |

**Schema versioning (VER-01..04):**

| REQ | Phase | Artifact | Verification |
|-----|-------|----------|--------------|
| VER-01 | 2 | [ontology/VERSION](../../ontology/VERSION) | `cat ontology/VERSION` = `0.1.0` |
| VER-02 | 2 | [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md) | `grep -q "0.1.0" ontology/CHANGELOG.md` |
| VER-03 | 2 | every record carries `schema_version` | `find instances -name '*.yaml' -exec grep -L "schema_version" {} \;` empty |
| VER-04 | 2 | [ontology/migrations/PATTERN.md](../../ontology/migrations/PATTERN.md) + `0_1_0_to_template.py.example` | both files exist; PATTERN documents `<from>_to_<to>.py` ruamel.yaml `YAML()` pattern |

### 9.3 Validators (Phase 3) — 5 REQs

| REQ | Phase | Artifact | Verification |
|-----|-------|----------|--------------|
| VAL-01 | 3 | [scripts/validate.py](../../scripts/validate.py) (master entrypoint) | `python scripts/validate.py instances/` exit 0 on clean repo |
| VAL-02 | 3 | [scripts/validators/{schema,ids,relations,provenance,links}.py](../../scripts/validators/) | `python -c "from scripts.validators import schema, ids, relations, provenance, links"` exit 0 |
| VAL-03 | 3 | [tests/fixtures/{valid,invalid}/](../../tests/fixtures/) | `find tests/fixtures/invalid -name '*.yaml' \| wc -l` ≥ 12; valid corpus covers every entity + relation type |
| VAL-04 | 3 | [tests/test_validators.py](../../tests/test_validators.py) | `pytest tests/test_validators.py` green |
| VAL-05 | 3 | [.github/workflows/](../../.github/workflows/) | green CI run; merge blocked on validation failure |

### 9.4 Demo Data + Document Import (Phase 4) — 11 REQs

| REQ | Phase | Artifact | Verification |
|-----|-------|----------|--------------|
| DOC-01 | 4 | `docs/<domain>/<doc-id>/` convention with `source.{pdf,md,docx,html}` + `processed.md` + `metadata.yaml` | `find docs -name 'metadata.yaml' \| wc -l` ≥ 3 |
| DOC-02 | 4 | document metadata schema enforcing title/doc_type/language/source_url/publication_date/effective_date/confidentiality/domain_tags/version/file_hash/processed_by | `jq '.required' ontology/schemas/entity.document.schema.json` covers all fields; or `metadata.schema.json` per Phase 4 plan |
| DOC-03 | 4 | [docs/README.md](../../docs/README.md) | `grep -q "import workflow" docs/README.md`; documents manual + scripted paths, who reviews, where AI-extracted entities go |
| DOC-04 | 4 | [docs/README.md](../../docs/README.md) confidentiality section | `grep -q "restricted\|itar_ear" docs/README.md` documenting non-default-ingestion |
| DEMO-01 | 4 | ≥1 instance per entity type | `find instances/entities -mindepth 1 -maxdepth 1 -type d \| wc -l` ≥ 22 (17 baseline + 5 ADR-002 accepted) |
| DEMO-02 | 4 | ≥3 relation instances spanning ≥3 relation types | `find instances/relations -name '*.yaml' \| wc -l` ≥ 3; `grep -h "^type:" instances/relations/**/*.yaml \| sort -u \| wc -l` ≥ 3 |
| DEMO-03 | 4 | 3 source documents (1 regulation, 1 CFD paper, 1 accident report) with full metadata | `ls docs/regulations/ docs/cfd/ docs/accidents/` populated |
| DEMO-04 | 4 | canonical ExpertNote at [instances/entities/expert-note/canonical-example.yaml](../../instances/entities/expert-note/) demonstrating full provenance/source/confidence pattern | file exists; cited in [docs/README.md](../../docs/README.md) AI 接力 |
| DEMO-05 | 4 | 1 RegulationClause with `status: superseded` + `superseded_by` pointing to active replacement | `grep -rl "status: superseded" instances/entities/regulation-clause/` non-empty |
| DEMO-06 | 4 | 1 AI-extracted record in [instances/_pending/](../../instances/_pending/) (verified NOT in canonical) | `find instances/_pending -name '*.yaml' \| wc -l` ≥ 1; `grep -r "method: ai_extracted" instances/entities/` empty |
| DEMO-07 | 4 | 1 bilingual entity using `i18n: { zh, en }` pattern | `grep -l "i18n:" instances/entities/**/*.yaml` non-empty with both `zh:` and `en:` fields populated |

### 9.5 RAG Pipeline (Phase 5) — 8 REQs

| REQ | Phase | Artifact | Verification |
|-----|-------|----------|--------------|
| RAG-01 | 5 | [.planning/design/RAG_PIPELINE.md §2](./RAG_PIPELINE.md) chunking with table-as-atomic | `grep -q "atomic" RAG_PIPELINE.md`; locked rules per RAG_PIPELINE.md Locked table |
| RAG-02 | 5 | [RAG_PIPELINE.md §3](./RAG_PIPELINE.md) BGE-M3 + bge-reranker-v2-m3 + mini-benchmark plan | `grep -q "bge-m3" RAG_PIPELINE.md` |
| RAG-03 | 5 | [RAG_PIPELINE.md §4](./RAG_PIPELINE.md) hybrid retrieval (vector + BM25 + RRF, k=60, synonym 0.3) | `grep -q "RRF" RAG_PIPELINE.md`; `grep -q "0.3" RAG_PIPELINE.md` (synonym weight) |
| RAG-04 | 5 | [RAG_PIPELINE.md §5](./RAG_PIPELINE.md) `[CITE:c_<8hex>]` citation injection | `grep -q "CITE:c_" RAG_PIPELINE.md` |
| RAG-05 | 5 | [RAG_PIPELINE.md §6](./RAG_PIPELINE.md) guardrail (`min_chunk_score=0.5`, `min_chunks_required=2`, canned bilingual no-context) | `grep -q "min_chunk_score" RAG_PIPELINE.md` |
| RAG-06 | 5 | [RAG_PIPELINE.md §7](./RAG_PIPELINE.md) cross-lingual (BGE-M3 multilingual + glossary expansion + i18n at index time) | `grep -q "i18n" RAG_PIPELINE.md`; `grep -q "glossary" RAG_PIPELINE.md` |
| RAG-07 | 5 | [evaluation/queries.yaml](../../evaluation/queries.yaml) ≥30 queries, ≥6 cross-lingual, ≥3 out-of-scope, ≥20% table-query | `python -c "import yaml; q=yaml.safe_load(open('evaluation/queries.yaml')); assert len(q['queries']) >= 30"` |
| RAG-08 | 5 | [scripts/exporters/to_ragflow.py](../../scripts/exporters/to_ragflow.py) skeleton with `--rebuild`, `--dry-run`, `--since=`, `--paths` argparse | `python scripts/exporters/to_ragflow.py --help` lists all 4 flags |

### 9.6 Deployment + AIH + Roadmap (Phase 6) — 13 REQs

| REQ | Phase | Artifact | Verification |
|-----|-------|----------|--------------|
| DEP-01 | 6 | [deploy/docker-compose.yml.draft](../../deploy/docker-compose.yml.draft) | `grep -q "DRAFT — NOT FOR PRODUCTION" deploy/docker-compose.yml.draft && python3 -c "import yaml; yaml.safe_load(open('deploy/docker-compose.yml.draft'))"` |
| DEP-02 | 6 | [deploy/.env.example](../../deploy/.env.example) | every compose `${VAR}` has a placeholder row; `grep -c "<CHANGE_ME>" deploy/.env.example` ≥ count of unique env vars in compose |
| DEP-03 | 6 | [deploy/topology.md](../../deploy/topology.md) | both ASCII and Mermaid diagrams present: `grep -q '```mermaid' deploy/topology.md && grep -q "Git" deploy/topology.md` |
| DEP-04 | 6 | [deploy/wiki-git-storage.md](../../deploy/wiki-git-storage.md) | `grep -q "wiki/ ONLY" deploy/wiki-git-storage.md` (case-sensitive scope rule) |
| DEP-05 | 6 | [deploy/authentik-phase2.md](../../deploy/authentik-phase2.md) + commented `authentik` block in compose | `grep -q "12568" deploy/authentik-phase2.md && grep -q "3495" deploy/authentik-phase2.md` |
| DEP-06 | 6 | [deploy/backup-restore.md](../../deploy/backup-restore.md) | `grep -q "rebuildable" deploy/backup-restore.md && grep -q "to_ragflow.py --rebuild" deploy/backup-restore.md` |
| PRD-02 | 6 | [.planning/design/PRD_v1.md](./PRD_v1.md) (this file) + sign-off in [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md) | `grep -q "PRD_v1" ontology/CHANGELOG.md && grep -q "AI 接力开发指南" .planning/design/PRD_v1.md` |
| AIH-01 | 6 | every [.planning/design/*.md](.) carries "AI 接力开发指南" section | `for f in .planning/design/*.md; do grep -q "AI 接力开发指南" "$f" \|\| echo MISSING; done` produces no MISSING |
| AIH-02 | 6 | 5-minute stranger test result file (plan 06-05) | `find .planning/phases/06-*/06-STRANGER-TEST.md` exits 0 with PASS verdict on ≥3 docs |
| AIH-03 | 6 | [process-log/phase-{1..6}-completion.md](../../process-log/) | `ls process-log/phase-*-completion.md \| wc -l` = 6; each file has the mandatory field labels (`AI session:`, `Date:`, `Plans:`, `Decisions:`, `Deviations:`, `Verification:`, `REQ-IDs covered:`, `Next phase:`) per [process-log/README.md](../../process-log/README.md) |
| AIH-04 | 6 | [docs/GLOSSARY.md](../../docs/GLOSSARY.md) | ≥50 bilingual rows: `awk '/^\|/ && !/---/ && !/Term/' docs/GLOSSARY.md \| wc -l` ≥ 50 |
| ROAD-01 | 6 | [.planning/ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md) | 7 named features (GraphRAG, Agent, Graph DB, OCR, Multi-tenant, SSO, Decision Agent): `grep -cE "^## [1-7]\." .planning/ROADMAP_FUTURE.md` ≥ 7 |
| ROAD-02 | 6 | [.planning/ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md) | 7 "Promote when" trigger blocks (one per feature): `grep -c "Promote when" .planning/ROADMAP_FUTURE.md` ≥ 7 |

**Aggregate v1 ship gate:** all 94 verification commands pass on the
v1.0.0 tag; all 6 phase success criteria from [ROADMAP.md](../ROADMAP.md)
marked complete; this PRD signed off in [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md).

***

## 10. Out of Scope (v1) + Risks

### 10.1 Out of scope (locked, per CLAUDE.md + REQUIREMENTS.md)

These features are LOCKED OUT for v1. Re-adding any of them requires an
ADR in [.planning/decisions/](../decisions/) plus user sign-off. The
[ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md) trigger column in §8 is the
sanctioned path for any of the deferred-with-trigger items.

| Feature | Reason locked out | Trigger to revisit |
|---------|-------------------|--------------------|
| Dify (agent orchestration) | First-stage no agent orchestration; coupling risk | none in v1 — see [ROADMAP_FUTURE.md §2 / §7](../ROADMAP_FUTURE.md) |
| Self-built Vue/React frontend | Wiki.js + RAGFlow UIs sufficient; custom UI = scope explosion | none planned |
| Graph DB backend (Neo4j / Nebula) in v1 | YAML sufficient for ≤10K triples; premature backend lock-in | [ROADMAP_FUTURE.md §3](../ROADMAP_FUTURE.md) |
| Auto-crawlers / scrapers | Quality > volume; v1 = curated import only | none planned |
| Decision-making agents (auto-tool-use loops) | Out of scope per Core Value — RAG retrieval-augmented Q&A only | [ROADMAP_FUTURE.md §7](../ROADMAP_FUTURE.md) |
| Uncited AI answers | Hard NO — guardrail enforced; zero-tolerance hallucination policy | NEVER (Core Value invariant) |
| OCR / scanned image processing | Text-layer PDF/MD/HTML/DOCX only in v1; non-deterministic fail mode | [ROADMAP_FUTURE.md §4](../ROADMAP_FUTURE.md) |
| Multi-tenant / fine-grained RBAC | v1 single-org admin/reader; over-designs without observed pattern | [ROADMAP_FUTURE.md §5](../ROADMAP_FUTURE.md) |
| Real-time collaborative editing | Wiki.js owns this poorly; not differentiating; not aviation-specific | none planned |
| LLM self-citation | System injects `[CITE:c_<8hex>]`; LLM cannot author citations | NEVER (Core Value invariant; Pitfall 8) |
| Auto-translation without human review | Aviation translation has legal/safety implications; bilingual is curated | none planned |
| Inline code execution | Anti-pattern in KB; security + maintenance burden | none planned |
| Real-running docker-compose v1 | v1 ships [docker-compose.yml.draft](../../deploy/docker-compose.yml.draft) + selection rationale, not running infra | n/a — promote to real deploy is per-deployer choice, not a v2 trigger |
| Wiki.js 3.0 | Alpha-since-2021; production unsafe | when 3.0 ships stable + Postgres-only migration story is documented |
| RAGFlow OIDC SSO | Open bugs (#3495 FR, #12568 Keycloak redirect-loop) | [ROADMAP_FUTURE.md §6](../ROADMAP_FUTURE.md) |
| ATA Spec 100 / S1000D as primary schema | S1000D is XML monolith; ATA Spec 100 is paper-era; we use lightweight `ata_chapter` field referencing iSpec 2200 | none planned (S1000D `s1000d_dmc` field reserved on Document for future export) |
| AP233 / ISO 10303 | Wrong shape (STEP/EXPRESS heavy machinery); not adopted | none planned |

### 10.2 Top risks (from [PITFALLS.md](../research/PITFALLS.md), surfaced for PM visibility)

| Risk | Pitfall | Mitigation in v1 |
|------|---------|------------------|
| Free-text source field | Pitfall 1 | Schema enforces structured `source` object; CI rejects (PROV-03) |
| Unreviewed AI extraction | Pitfall 2 | [_pending/](../../instances/_pending/) quarantine + H-Darrieus REJECT (PROV-04 / PROV-05) |
| Uncalibrated confidence | Pitfall 3 | `confidence.rationale` enum locked in [ADR-005](../decisions/ADR-005-provenance-enum.md) (PROV-02) |
| Schema migration debt | Pitfall 4 | per-record `schema_version` + [migrations/PATTERN.md](../../ontology/migrations/PATTERN.md) (VER-03 / VER-04) |
| Regulation supersession drift | Pitfall 5 | `superseded_by` field + supersession-chain validator in [scripts/validators/links.py](../../scripts/validators/links.py) |
| Chunk destroys table | Pitfall 6 | atomic-block chunking in [RAG_PIPELINE.md §2.2](./RAG_PIPELINE.md) |
| Synonym-expansion bias | Pitfall 7 | weight 0.3 (AeroPower-RAG-validated) in [RAG_PIPELINE.md §4.2](./RAG_PIPELINE.md) |
| Citation hallucination | Pitfall 8 | `[CITE:c_<8hex>]` system-side token; LLM cannot self-author; post-gen validator drops unresolved tokens |
| No-result hallucination | Pitfall 9 | guardrail short-circuit (`min_chunk_score=0.5`, `min_chunks_required=2`); LLM not called |
| Wiki.js / RAGFlow content desync | Pitfall 10 | Git is truth; [deploy/wiki-git-storage.md](../../deploy/wiki-git-storage.md) limits Wiki.js Git scope to `wiki/` only |
| Truth + cache discipline | Pitfall 11 | Postgres dump + Git push = truth backup; vector store rebuildable per [deploy/backup-restore.md](../../deploy/backup-restore.md) |
| AI handoff cold-start cost | Pitfall 12 | AIH-01..04: AI 接力 sections + [docs/GLOSSARY.md](../../docs/GLOSSARY.md) + [process-log/](../../process-log/) + 5-minute stranger test |

***

## 11. Open Questions Resolution

The open questions tracked in [PRD_v0 §6](./PRD_v0.md) and
[RAG_PIPELINE.md §9](./RAG_PIPELINE.md) are resolved or carried forward as
follows. Carried items each map to a [ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md)
entry with a measurable trigger.

### 11.1 PRD_v0 §6.1 (inherited from research/SUMMARY.md)

| # | Question | Status | Resolution / Tracking |
|---|----------|--------|-----------------------|
| 1 | S1000D Issue 6 (2024) DMC field shape — what optional field do we reserve? | RESOLVED | `Document.s1000d_dmc` reserved (optional); structural breakdown in [ontology/mappings/s1000d-dmc-reserved.md](../../ontology/mappings/s1000d-dmc-reserved.md) |
| 2 | RAGFlow 0.25.1 table-chunk preservation behavior | RESOLVED | OpenDataLoader-PDF v0.25 atomic-table support documented in [RAG_PIPELINE.md §2.2](./RAG_PIPELINE.md) |
| 3 | RAGFlow HTTP API citation granularity (per-sentence or per-answer) | RESOLVED | Per-chunk `[CITE:c_<8hex>]` injection; system-side resolver maps chunk_id → (document, page, section, url) per [RAG_PIPELINE.md §5](./RAG_PIPELINE.md) |
| 4 | Triple export format — RDF/Turtle vs JSON-LD vs JSONL `{s,p,o,prov}` | RESOLVED | JSONL `{s,p,o,prov}` per [ADR-006](../decisions/ADR-006-triple-export.md); [scripts/exporters/to_jsonl_triples.py](../../scripts/exporters/to_jsonl_triples.py) implements |
| 5 | Aviation bilingual glossary seed source (ICAO 9713 / ATA bilingual / CAAC) | RESOLVED | ICAO 9713 + ATA bilingual + AeroPower-RAG glossary; [docs/GLOSSARY.md](../../docs/GLOSSARY.md) ships ≥50 entries (plan 06-02) |
| 6 | `interfaces_with` vs `requires` boundary semantics | RESOLVED | [ADR-003](../decisions/ADR-003-relation-additions.md) with worked examples; relation schemas land the discipline |
| 7 | Embedding mini-benchmark scope (BGE-M3 vs nomic-embed-text vs multilingual-e5-large) | CARRIED-TO-PHASE-7 | Protocol locked in [RAG_PIPELINE.md §3.2](./RAG_PIPELINE.md); Phase 7 runs and updates §3.3 with measured numbers |
| 8 | RAGFlow Apple Silicon ARM image — official or workaround | RESOLVED | RAGFlow 0.25.1 ships ARM64 build; verified in Phase 6 plan 06-01 deploy spec |
| 9 | Wiki.js ↔ Git two-way sync edge cases | RESOLVED | [deploy/wiki-git-storage.md](../../deploy/wiki-git-storage.md) locks Wiki.js Git scope to `wiki/` only; conflicts handled via PR-flow (Wiki.js never edits ontology/instances YAML) |
| 10 | LLM choice for RAG (Ollama-local vs Claude/OpenAI API vs hybrid) | DIRECTIONAL | Pluggable per [RAG_PIPELINE.md §3.4](./RAG_PIPELINE.md); deployment phase decides per hardware. Carried as deployment-time choice, not a v2 trigger. |

### 11.2 PRD_v0 §6.2 (PRD-level questions)

| # | Question | Status | Resolution |
|---|----------|--------|------------|
| P-1 | Does v1 need a "comparison view" (e.g., FAR vs CCAR analogous clauses)? | DEFERRED | Tracked under [ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md); promote-when not explicit (high-value but no standalone entry) — propose new entry if user demand surfaces. |
| P-2 | Should the supersession demo cover both regulation and internal note cases? | RESOLVED | Regulation-only sufficient for the v1 demo gate (DEMO-05); internal-note supersession is a documented pattern (`supersedes_note` on ExpertNote schema) but not a demo requirement. |
| P-3 | Does the AI 接力开发指南 section have a CI check? | RESOLVED | Plan 06-05 adds `scripts/validators/aih_section.py` running in pre-commit + CI; verifies every `.planning/design/*.md` contains the heading. |
| P-4 | Bilingual glossary baseline — do we lock to ICAO 9713? | RESOLVED | ICAO 9713 + ATA bilingual + AeroPower-RAG glossary as the principal sources; no hard lock; [docs/GLOSSARY.md](../../docs/GLOSSARY.md) ships ≥50 entries with source attribution per row. |
| P-5 | What is the v1 evidence that "every AI answer has a citation"? | RESOLVED | Phase 5 design specifies the post-generation validator + `[CITE:c_<8hex>]` injection ([RAG_PIPELINE.md §5](./RAG_PIPELINE.md)); Phase 7 runs the actual eval against [evaluation/queries.yaml](../../evaluation/queries.yaml) for measured citation-failure rate. |

### 11.3 RAG_PIPELINE.md §9 open questions

| Question | Status | Tracking |
|----------|--------|----------|
| Confidence-aware retrieval filter (use entity `confidence.score` to filter chunks at retrieval time) | CARRIED-TO-V2 | [ROADMAP_FUTURE.md §2 (Agent Layer)](../ROADMAP_FUTURE.md) — wires this in alongside the AGENT-02 conflict-detection use case |
| GraphRAG escalation (when to add graph-traversal hop after vector retrieval) | CARRIED-TO-V2 | [ROADMAP_FUTURE.md §1 (GraphRAG Layer)](../ROADMAP_FUTURE.md) with explicit triggers (≥10K instances OR ≥5 multi-hop eval failures OR named path-query use case) |
| Mini-benchmark numbers | CARRIED-TO-PHASE-7 | Same as §11.1 #7 — Phase 7 measurement update |

***

## 12. Sign-off

This PRD is signed off by recording an entry in
[ontology/CHANGELOG.md](../../ontology/CHANGELOG.md) — the canonical
sign-off ledger established in Phase 2 plan 02-01 and authored as Phase 6
plan 06-04 task 2. The CHANGELOG entry is the legally binding sign-off
record; this section is informational.

**Ledger entry format** (added to [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md)
by this plan's Task 2):

```
## [PRD_v1 sign-off] — 2026-05-03

### Added
- PRD_v1 final, contractual at .planning/design/PRD_v1.md
  - 94 v1 REQ-IDs covered with per-requirement acceptance criteria
  - Synthesizes all locked decisions across phases 1–6
  - Replaces: .planning/design/PRD_v0.md (directional, frozen at end of Phase 1)
  - Authority for: schema set v0.1.0, validator pipeline, RAG pipeline contract,
    deployment posture (DRAFT), v2+ "Promote when" triggers
- Sign-off recorded in this CHANGELOG (canonical sign-off ledger)
```

After this PRD signs off, the v1.0.0 release tag may be created. v2 work
begins only when a [.planning/ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md)
trigger fires; until then, the project is COMPLETE for v1.

***

## Appendix A — Cross-reference index

The canonical files this PRD cites, in alphabetical order, with what each
is the authority for. A future auditor following any link should reach the
authoritative spec without an intermediate hop.

| File | Authority for |
|------|---------------|
| [.planning/PROJECT.md](../PROJECT.md) | Core Value invariant; project audience and constraints |
| [.planning/REQUIREMENTS.md](../REQUIREMENTS.md) | full v1 REQ-ID inventory (94); v2 deferred items; out-of-scope rationale |
| [.planning/ROADMAP.md](../ROADMAP.md) | 6 phases + per-phase success criteria; plan execution order |
| [.planning/ROADMAP_FUTURE.md](../ROADMAP_FUTURE.md) | 7 v2+ features with "Promote when" triggers (ROAD-01, ROAD-02) |
| [.planning/research/STACK.md](../research/STACK.md) | tech stack rationale + version compatibility + alternatives considered + sources |
| [.planning/research/ARCHITECTURE.md](../research/ARCHITECTURE.md) | repo structure; component map; data flow; anti-patterns; migration path to GraphRAG |
| [.planning/research/PITFALLS.md](../research/PITFALLS.md) | 12 critical pitfalls with prevention guidance (Pitfalls 1–9 are Core Value defenders) |
| [.planning/research/SUMMARY.md](../research/SUMMARY.md) | research synthesis; pinned decisions; original open-questions list |
| [.planning/research/FEATURES.md](../research/FEATURES.md) | feature inventory (incl. bilingual via entity `i18n` field design rationale) |
| [.planning/design/PRD_v0.md](./PRD_v0.md) | directional PRD (frozen at Phase 1); replaced by this file |
| [.planning/design/RAG_PIPELINE.md](./RAG_PIPELINE.md) | RAG pipeline contract — chunking / embedding / retrieval / citation / guardrail / cross-lingual (RAG-01..08) |
| [.planning/decisions/ADR-001-reserved.md](../decisions/ADR-001-reserved.md) | Phase 6 PRD-v0/v1 split + URI scheme reservation |
| [.planning/decisions/ADR-002-entity-additions.md](../decisions/ADR-002-entity-additions.md) | accept/defer of Material / TestCase / TestReport / Configuration / Person / Organization |
| [.planning/decisions/ADR-003-relation-additions.md](../decisions/ADR-003-relation-additions.md) | accept/internalize of interfaces_with / complies_with / has_revision / applicable_during_phase / generated_by |
| [.planning/decisions/ADR-004-field-shapes.md](../decisions/ADR-004-field-shapes.md) | confidence / i18n / version_history field shapes |
| [.planning/decisions/ADR-005-provenance-enum.md](../decisions/ADR-005-provenance-enum.md) | provenance enum (human / ai_extracted / hybrid_reviewed) + H-Darrieus REJECT rule |
| [.planning/decisions/ADR-006-triple-export.md](../decisions/ADR-006-triple-export.md) | JSONL `{s,p,o,prov}` triple export format choice |
| [.planning/decisions/ADR-007-schema-versioning.md](../decisions/ADR-007-schema-versioning.md) | schema versioning placement + migration script convention |
| [ontology/VERSION](../../ontology/VERSION) | current ontology version (`0.1.0`) |
| [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md) | canonical sign-off ledger; per-version schema changes with rationale |
| [ontology/_meta.schema.json](../../ontology/_meta.schema.json) | base fields composition root; provenance / confidence / source `$defs` |
| [ontology/schemas/](../../ontology/schemas/) | 22 entity + 16 relation leaf schemas (JSON Schema 2020-12) |
| [ontology/migrations/PATTERN.md](../../ontology/migrations/PATTERN.md) | YAML→YAML migration script convention (ruamel.yaml) |
| [ontology/vocabularies/](../../ontology/vocabularies/) | ATA chapters / jurisdictions / provenance methods (controlled vocabulary) |
| [ontology/mappings/](../../ontology/mappings/) | ATA-to-ISO10303 (deferred) + S1000D DMC (reserved) |
| [scripts/validate.py](../../scripts/validate.py) | master validator entrypoint (VAL-01) |
| [scripts/validators/](../../scripts/validators/) | per-rule validators (schema / ids / relations / provenance / links) (VAL-02) |
| [scripts/validators/README.md](../../scripts/validators/README.md) | per-validator behavior contracts; public API |
| [scripts/exporters/to_ragflow.py](../../scripts/exporters/to_ragflow.py) | RAGFlow ingestion CLI skeleton (RAG-08) |
| [scripts/exporters/to_jsonl_triples.py](../../scripts/exporters/to_jsonl_triples.py) | JSONL `{s,p,o,prov}` triple export (ADR-006) |
| [evaluation/queries.yaml](../../evaluation/queries.yaml) | ≥30 eval queries; ≥6 cross-lingual; ≥3 out-of-scope; ≥20% table-query (RAG-07) |
| [tests/fixtures/](../../tests/fixtures/) | valid + invalid corpus for validator self-tests (VAL-03) |
| [docs/README.md](../../docs/README.md) | document import workflow + confidentiality gating (DOC-03 / DOC-04) |
| [docs/GLOSSARY.md](../../docs/GLOSSARY.md) | bilingual aviation terms ≥50 (AIH-04) |
| [process-log/README.md](../../process-log/README.md) | phase-completion entry format (AIH-03) |
| [process-log/phase-{1..6}-completion.md](../../process-log/) | per-phase audit trail (AIH-03) |
| [deploy/docker-compose.yml.draft](../../deploy/docker-compose.yml.draft) | service topology (DEP-01) |
| [deploy/.env.example](../../deploy/.env.example) | env-var template with placeholders (DEP-02) |
| [deploy/topology.md](../../deploy/topology.md) | ASCII + Mermaid topology diagrams (DEP-03) |
| [deploy/wiki-git-storage.md](../../deploy/wiki-git-storage.md) | Wiki.js Git scope = `wiki/` only (DEP-04) |
| [deploy/authentik-phase2.md](../../deploy/authentik-phase2.md) | future SSO plan + RAGFlow OIDC bug status (DEP-05) |
| [deploy/backup-restore.md](../../deploy/backup-restore.md) | Postgres dump + Git push truth backup; vector store rebuildable (DEP-06) |
| [README.md](../../README.md) | repo entry point + AI 接力开发指南 (REPO-03) |
| [.gitattributes](../../.gitattributes) | Git LFS configuration for binary doc types (REPO-02) |
| [.pre-commit-config.yaml](../../.pre-commit-config.yaml) | local pre-commit hook config (REPO-05) |
| [.github/workflows/](../../.github/workflows/) | CI workflow files (REPO-04, VAL-05) |
| [CLAUDE.md](../../CLAUDE.md) | project-level Claude Code conventions; Constraints; GSD workflow enforcement |

***

*PRD v1 authored: 2026-05-03 by Phase 6 plan 06-04*
*Sign-off ledger entry: [ontology/CHANGELOG.md](../../ontology/CHANGELOG.md)*
*Last touched by: Claude Opus 4.7 (1M context) / Phase 6 / plan 06-04 / 2026-05-03*

# Architecture Research

**Domain:** Aviation Knowledge Base (engineering-grade structured KB + RAG, schema-first, audit-friendly)
**Researched:** 2026-05-03
**Confidence:** MEDIUM-HIGH (Wiki.js Git sync, RAGFlow ingestion API, Authentik OIDC verified via official docs; YAML-as-ontology + future GraphRAG migration path inferred from LinkML/Pydantic/DataHub patterns)

> **Decision posture:** This is an opinionated architecture for v1. Given the locked stack (Wiki.js + RAGFlow + YAML/JSON Schema + Git) and the hard "no graph DB / no Dify / no custom frontend / no decision agents" constraints, the architecture optimizes for: (1) **Git as single source of truth**, (2) **schema-first ontology**, (3) **traceable provenance on every record**, (4) **clean migration path to GraphRAG/KG without refactor**.

---

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                       Presentation Layer                              │
│                                                                        │
│   ┌────────────────────┐      ┌────────────────────────────┐         │
│   │  Wiki.js Portal    │      │   RAGFlow UI (chat + KB)   │         │
│   │  (human authoring  │      │   (Q&A with citations,     │         │
│   │   + Markdown view) │      │    document explorer)      │         │
│   └─────────┬──────────┘      └──────────────┬─────────────┘         │
│             │                                  │                      │
│             │ (optional, Phase 3)              │                      │
│             ▼                                  ▼                      │
│       ┌──────────────────────────────────────────────┐               │
│       │  Authentik (OIDC IdP) — Phase 2 optional     │               │
│       └──────────────────────────────────────────────┘               │
├──────────────────────────────────────────────────────────────────────┤
│                       Knowledge Layer (Git-backed)                    │
│                                                                        │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│   │  Ontology        │  │  Instances       │  │  Wiki Content    │  │
│   │  (schemas +      │  │  (entity records │  │  (Markdown pages │  │
│   │   entity types + │  │   + relations    │  │   authored in    │  │
│   │   relation types)│  │   as YAML)       │  │   Wiki.js)       │  │
│   └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│            │                      │                      │            │
│            └──────────┬───────────┴──────────┬───────────┘            │
│                       ▼                      ▼                        │
│            ┌──────────────────────────────────────┐                  │
│            │  Document Store                       │                  │
│            │  /docs/<domain>/<doc-id>/             │                  │
│            │  ├── source.{pdf,docx,md,html}        │                  │
│            │  ├── processed.md                     │                  │
│            │  └── metadata.yaml                    │                  │
│            └──────────────────────────────────────┘                  │
├──────────────────────────────────────────────────────────────────────┤
│                       Validation & CI Layer                           │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐│
│   │  GitHub Actions / GitLab CI                                    ││
│   │  ├── lint (yamllint, markdownlint)                             ││
│   │  ├── schema validate (jsonschema → ajv / python-jsonschema)    ││
│   │  ├── ID uniqueness check                                       ││
│   │  ├── relation referent existence check                         ││
│   │  ├── provenance/confidence required-field check                ││
│   │  └── link check (markdown → docs → instances)                  ││
│   └────────────────────────────────────────────────────────────────┘│
├──────────────────────────────────────────────────────────────────────┤
│                       Index/Retrieval Layer                           │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐│
│   │  RAGFlow                                                        ││
│   │  ├── Document parser (PDF/DOCX/MD/HTML)                         ││
│   │  ├── Chunker (with custom layout hints)                         ││
│   │  ├── Embedding (BGE-M3 / bge-large-zh recommended)              ││
│   │  ├── Vector index (RAGFlow internal — Infinity/Elasticsearch)  ││
│   │  ├── BM25 + RRF hybrid (built-in)                               ││
│   │  ├── Citation graph (built-in)                                  ││
│   │  └── HTTP API for ingestion + metadata                          ││
│   └────────────────────────────────────────────────────────────────┘│
├──────────────────────────────────────────────────────────────────────┤
│                       Storage Layer                                   │
│                                                                        │
│   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│   │  Git repo    │ │  PostgreSQL  │ │  RAGFlow     │ │  Object/   │ │
│   │  (truth)     │ │  (Wiki.js DB)│ │  storage     │ │  blob      │ │
│   │  YAML+MD+PDF │ │  page cache  │ │  (vectors +  │ │  (large    │ │
│   │              │ │  + users     │ │  parsed docs)│ │   PDFs)    │ │
│   └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Owns | Implementation | Stateful? |
|-----------|------|----------------|-----------|
| **Wiki.js Portal** | Human-authored narrative pages, Markdown rendering, page-level versioning, navigation tree | Wiki.js 2.x (3.x is beta as of 2026; pin 2.5.x for stability) | Yes (Postgres) |
| **RAGFlow** | Document parsing, chunking, embedding, hybrid retrieval, citation generation, Q&A UI | RAGFlow 0.24.x (Feb 2026, supports batch metadata) | Yes (its own DB + vector store) |
| **Ontology Layer** | Entity type schemas (17), Relation type schemas (13), version metadata, controlled vocabularies | JSON Schema files in `/ontology/schemas/`; entity/relation type defs in YAML | No (file-based) |
| **Instance Store** | Concrete entity records and relation records — the actual KB content | YAML files under `/instances/<entity-type>/<id>.yaml` | No (Git is truth) |
| **Document Store** | Raw + processed source documents with metadata sidecar | Filesystem under `/docs/`, large PDFs via Git LFS | No |
| **Validation/CI** | Schema enforcement, referential integrity, provenance gate | GitHub Actions + Python validator (`scripts/validate.py`) | No |
| **Auth Gateway** (Phase 2 optional) | SSO across Wiki.js + RAGFlow | Authentik (OIDC IdP) | Yes |
| **Sync Bridge** (Phase 2) | Push Wiki.js Markdown → Git; pull Git → RAGFlow ingestion | Wiki.js native Git storage module + RAGFlow HTTP API client (`scripts/sync_to_ragflow.py`) | No |

**Key boundary principle:** **Git holds the truth.** Wiki.js's Postgres is a *cache* of pages that are also in Git via the bidirectional Git storage module. RAGFlow's vector store is a *derivative* — rebuildable from Git at any time. This makes the system Git-restorable end-to-end.

---

## Recommended Project Structure

```
aviation-knowledge-base/
├── README.md                          # Project entry point + AI handoff guide
├── CHANGELOG.md                       # Top-level changelog (project-wide)
├── .planning/                         # GSD workflow artifacts (per CLAUDE.md)
│   ├── PROJECT.md
│   ├── research/                      # This directory
│   ├── decisions/                     # DEC-* records (key arch decisions)
│   └── retrospectives/
│
├── ontology/                          # SCHEMA LAYER — defines what can exist
│   ├── README.md                      # Ontology overview + AI handoff guide
│   ├── CHANGELOG.md                   # Schema-specific semver changelog
│   ├── VERSION                        # Top-level ontology version (e.g. 0.1.0)
│   ├── schemas/                       # JSON Schema files (machine validators)
│   │   ├── _meta.schema.json          # Common fields: id, version, source,
│   │   │                              # confidence, provenance, created_at
│   │   ├── entity.base.schema.json    # Base for all entities
│   │   ├── relation.base.schema.json  # Base for all relations
│   │   ├── entities/                  # One schema per entity type (17 files)
│   │   │   ├── aircraft_model.schema.json
│   │   │   ├── aircraft_system.schema.json
│   │   │   ├── subsystem.schema.json
│   │   │   ├── component.schema.json
│   │   │   ├── requirement.schema.json
│   │   │   ├── regulation_clause.schema.json
│   │   │   ├── standard.schema.json
│   │   │   ├── procedure.schema.json
│   │   │   ├── failure_mode.schema.json
│   │   │   ├── maintenance_task.schema.json
│   │   │   ├── cfd_method.schema.json
│   │   │   ├── simulation_case.schema.json
│   │   │   ├── mesh_requirement.schema.json
│   │   │   ├── turbulence_model.schema.json
│   │   │   ├── accident_case.schema.json
│   │   │   ├── document.schema.json
│   │   │   └── expert_note.schema.json
│   │   └── relations/                 # One schema per relation type (13 files)
│   │       ├── part_of.schema.json
│   │       ├── applicable_to.schema.json
│   │       ├── constrained_by.schema.json
│   │       ├── verified_by.schema.json
│   │       ├── derived_from.schema.json
│   │       ├── supersedes.schema.json
│   │       ├── cites.schema.json
│   │       ├── causes.schema.json
│   │       ├── mitigated_by.schema.json
│   │       ├── requires.schema.json
│   │       ├── equivalent_to.schema.json
│   │       ├── conflicts_with.schema.json
│   │       └── used_in.schema.json
│   ├── vocabularies/                  # Controlled term lists (YAML)
│   │   ├── ata_chapters.yaml          # ATA Spec 100 chapter codes (mapping reserved)
│   │   ├── confidentiality_levels.yaml
│   │   ├── domain_tags.yaml
│   │   ├── languages.yaml
│   │   └── provenance_methods.yaml    # human / ai_extracted / hybrid
│   └── mappings/                      # Reserved for future external standards
│       ├── README.md                  # Why these are placeholders for v1
│       ├── ata_spec_100.placeholder.yaml
│       ├── s1000d.placeholder.yaml
│       └── ap233.placeholder.yaml
│
├── instances/                         # CONTENT LAYER — actual KB records
│   ├── README.md                      # File naming + ID convention
│   ├── entities/
│   │   ├── aircraft_model/
│   │   │   ├── b737-800.yaml
│   │   │   └── arj21-700.yaml
│   │   ├── component/
│   │   │   └── ...
│   │   └── ...                        # Mirrors entity types
│   └── relations/
│       ├── part_of/
│       │   └── b737-800__has__cfm56-7b.yaml
│       └── ...                        # Mirrors relation types
│
├── docs/                              # DOCUMENT LAYER — source materials
│   ├── README.md                      # Import workflow + metadata spec
│   ├── airworthiness/
│   │   └── ccar25-r4/
│   │       ├── source.pdf              # via Git LFS
│   │       ├── processed.md            # text-extracted, normalized
│   │       └── metadata.yaml           # title, source_url, retrieved_at, ...
│   ├── cfd/
│   │   └── lanzafame-2014-h-darrieus/
│   │       ├── source.pdf
│   │       ├── processed.md
│   │       └── metadata.yaml
│   └── standards/
│       └── ...
│
├── wiki/                              # Wiki.js Markdown content (Git-synced)
│   ├── README.md                      # Edited via Wiki.js UI; pushed to Git
│   ├── home.md                        # via Wiki.js Git storage module
│   ├── domains/
│   │   ├── airworthiness/
│   │   ├── cfd/
│   │   └── ...
│   └── tutorials/
│       └── ai-handoff-guide.md
│
├── deploy/                            # DEPLOYMENT LAYER — config only (no run in v1)
│   ├── README.md                      # Topology diagram + selection rationale
│   ├── docker-compose/
│   │   ├── docker-compose.yml          # Wiki.js + Postgres + RAGFlow + (optional Authentik)
│   │   ├── .env.example
│   │   └── volumes/.gitkeep
│   ├── wiki-js/
│   │   ├── config.sample.yml
│   │   └── git-storage-config.md       # How to point Wiki.js Git at this repo's wiki/
│   ├── ragflow/
│   │   ├── service_conf.sample.yaml
│   │   └── ingestion-pipeline.sample.json
│   └── authentik/                     # Phase 2 optional
│       └── README.md
│
├── scripts/                           # AUTOMATION LAYER — validators + importers
│   ├── README.md
│   ├── validate.py                    # Master validator (used in CI)
│   ├── validators/
│   │   ├── schema.py                  # JSON Schema runner
│   │   ├── ids.py                     # Uniqueness + format check
│   │   ├── relations.py               # Referent existence check
│   │   ├── provenance.py              # confidence + provenance.method required
│   │   └── links.py                   # Cross-file link integrity
│   ├── importers/
│   │   ├── pdf_to_processed_md.py
│   │   └── document_metadata_template.py
│   ├── exporters/
│   │   ├── to_ragflow.py              # YAML+MD → RAGFlow HTTP API ingestion
│   │   ├── to_rdf.py                  # Phase 3+ : YAML → Turtle/RDF (placeholder)
│   │   └── to_neo4j.py                # Phase 3+ : YAML → Cypher (placeholder)
│   └── migrations/                    # Schema migration scripts (semver-driven)
│       ├── README.md
│       └── 0.1.0_to_0.2.0.py.placeholder
│
├── tests/                             # Test data + validator self-tests
│   ├── fixtures/
│   │   ├── valid/
│   │   └── invalid/
│   └── test_validators.py
│
├── process-log/                       # Per CLAUDE.md audit-friendly preference
│   ├── README.md                      # AI session archive + decision trail
│   └── 2026-05-03_init.md
│
└── .github/
    └── workflows/
        ├── validate.yml               # Run on every PR
        └── lint.yml
```

### Structure Rationale

- **`ontology/` vs `instances/`**: Schema-first design (LinkML/DataHub/OpenMetadata pattern). The schema is type-level, the instances are value-level. Mixing them is the most common KB anti-pattern.
- **`docs/<domain>/<doc-id>/` triplet (source + processed + metadata)**: Mirrors AeroPower-RAG's pattern. `processed.md` is the input to RAGFlow chunking; `metadata.yaml` is the bridge to ontology (via `Document` entity records that reference `doc-id`).
- **`wiki/` as Git-synced folder**: Wiki.js's [Git storage module](https://docs.requarks.io/storage/git) writes Markdown bidirectionally. Wiki.js DB is cache; Git is truth. Default 5-minute sync interval is acceptable for v1.
- **`scripts/exporters/`** with `to_rdf.py` and `to_neo4j.py` as placeholder files now: these are the **migration hooks** for Phase 3+ GraphRAG/KG. Creating empty stubs in v1 makes the intent visible and prevents architectural drift.
- **`mappings/` directory with placeholder ATA/S1000D/AP233 files**: Honors PROJECT.md "需要预留映射到这些标准的字段" — the placeholder structure communicates intent to future contributors without committing to specific mappings yet.
- **`process-log/`**: Per user's CLAUDE.md (Aircraft CAD Report / cfd-ai-workbench lessons) — explicit AI-process audit trail.

---

## Architectural Patterns

### Pattern 1: Git as Single Source of Truth (Schema + Instances + Docs)

**What:** All canonical knowledge — schemas, entity instances, relation instances, source documents, processed Markdown — lives in the Git repo. Wiki.js Postgres and RAGFlow's vector store are *derivatives* that can be reconstructed from Git.

**When to use:** Engineering KBs with strong audit requirements (aviation, finance, healthcare).

**Trade-offs:**
- ✅ Auditability (every change is a commit with author, time, diff)
- ✅ Disaster recovery (rebuild any component from Git)
- ✅ Reviewable changes via PR (mandatory schema gate)
- ❌ Real-time collaborative editing on YAML is awkward (mitigation: Wiki.js handles narrative content; YAML is for structured records, edited less frequently and with PR review)
- ❌ Large binaries need Git LFS

**Example (entity record):**
```yaml
# instances/entities/component/cfm56-7b.yaml
id: comp:cfm56-7b
type: Component
schema_version: 0.1.0
name:
  zh: CFM56-7B 涡扇发动机
  en: CFM56-7B Turbofan Engine
ata_chapter: "72"      # mapping reserved
manufacturer: cfm-international
introduced_year: 1996

# Mandatory provenance fields (per R5)
provenance:
  method: human                     # human | ai_extracted | hybrid
  reviewer: zhuanz
  reviewed_at: 2026-05-03T10:00:00Z
source:
  - kind: document
    ref: doc:cfm56-7b-tcds-easa
    page: 3
  - kind: url
    url: https://www.easa.europa.eu/...
    retrieved_at: 2026-05-01T08:00:00Z
confidence: 0.95
created_at: 2026-05-03T10:00:00Z
updated_at: 2026-05-03T10:00:00Z
```

### Pattern 2: Provenance + Confidence as First-Class Fields

**What:** Every entity and relation record has mandatory `provenance.method`, `source`, and `confidence` fields, validated by JSON Schema.

**When to use:** Anywhere AI-extracted knowledge mixes with human-curated knowledge (per H-Darrieus lesson in user's MEMORY.md).

**Trade-offs:**
- ✅ Cannot accidentally promote AI hallucination to canonical (blocked by validator)
- ✅ Downstream RAG can filter by `confidence ≥ X` or `method == 'human'`
- ❌ Some overhead for human authors (mitigation: defaults in template + scaffold script)

**Example (validator enforcement):**
```python
# scripts/validators/provenance.py
REQUIRED = ["provenance.method", "source", "confidence"]
ALLOWED_METHODS = {"human", "ai_extracted", "hybrid"}

def validate(record: dict, path: str) -> list[str]:
    errors = []
    method = record.get("provenance", {}).get("method")
    if method not in ALLOWED_METHODS:
        errors.append(f"{path}: provenance.method must be one of {ALLOWED_METHODS}")
    if record.get("source") in (None, []):
        errors.append(f"{path}: source must be non-empty")
    conf = record.get("confidence")
    if not (isinstance(conf, (int, float)) and 0.0 <= conf <= 1.0):
        errors.append(f"{path}: confidence must be float in [0.0, 1.0]")
    if method == "ai_extracted" and conf is not None and conf > 0.85:
        errors.append(
            f"{path}: ai_extracted records cannot self-report confidence > 0.85 "
            "without human review (set method='hybrid' after review)"
        )
    return errors
```

### Pattern 3: Stable URI-Style IDs (KG-Ready)

**What:** Every entity uses a `<type-prefix>:<slug>` ID scheme that is stable across backends (file → RDF → graph DB).

**When to use:** Any KB intending to migrate to a graph backend or to be linked from external systems.

**Trade-offs:**
- ✅ Renaming a file does not break references
- ✅ Direct mapping to RDF URIs (`https://akb.example.org/comp/cfm56-7b`)
- ✅ Resolves to graph node ID in Phase 3 Neo4j/Nebula
- ❌ Need a slug-validator to enforce format

**Convention:**
```
Entity ID:    <type-prefix>:<kebab-case-slug>
Examples:     comp:cfm56-7b
              ac:b737-800
              reg:ccar-25-1309
              cfd:lanzafame-2014-h-darrieus

Relation ID:  rel:<predicate>:<source>__<target>
Examples:     rel:part_of:comp:cfm56-7b__ac:b737-800
              rel:cites:expert_note:fan-blade-fod__doc:incident-2019-08-12
```

### Pattern 4: Git-Bridge Sync (Wiki.js ↔ Repo ↔ RAGFlow)

**What:** Wiki.js writes its Markdown content to Git via the [native Git storage module](https://docs.requarks.io/storage/git) (bidirectional, 5-min interval). A small script (`scripts/exporters/to_ragflow.py`) watches Git and pushes new/changed `wiki/**.md` and `docs/**/processed.md` to RAGFlow via its [HTTP API](https://ragflow.io/docs/http_api_reference).

**When to use:** Two systems that need to share content but have incompatible internal stores.

**Trade-offs:**
- ✅ No tight coupling: either side can be swapped (e.g., Wiki.js → BookStack)
- ✅ Git becomes the audit log of what RAGFlow has been told to index
- ❌ Sync lag (max ~5 min Wiki.js push + ~1 min RAGFlow ingest)
- ❌ Two-way conflicts on the same Markdown page if both Wiki.js UI edit + Git PR happen simultaneously (mitigation: Wiki.js page IDs are namespaced under `wiki/`; structured records under `instances/` are PR-only, not editable in Wiki.js UI)

**Sync direction policy:**
| Source | Edit point | Lands in Git via | Lands in RAGFlow via |
|--------|------------|------------------|----------------------|
| Narrative wiki page | Wiki.js UI | Wiki.js Git storage module (push) | `to_ragflow.py` watches `wiki/**.md` |
| Entity/relation YAML | Editor + PR | Direct commit | Optionally indexed (Phase 3 — needs YAML→prose template) |
| Source document | `scripts/importers/` + PR | Direct commit (LFS for binaries) | `to_ragflow.py` watches `docs/**/processed.md` + uploads `metadata.yaml` as RAGFlow doc metadata |

### Pattern 5: Schema Versioning via Per-File `schema_version` + Top-Level Semver

**What:** Each instance file carries `schema_version: X.Y.Z`. The validator checks per-record schema_version against the schema directory's VERSION. Migration scripts handle bumps.

**When to use:** Any evolving schema that has live records.

**Approach:**
```
ontology/VERSION                                  → 0.1.0
ontology/schemas/entities/component.schema.json   → "$id": ".../component/0.1.0"
instances/entities/component/cfm56-7b.yaml        → schema_version: 0.1.0

# When schema bumps:
ontology/VERSION                                  → 0.2.0
ontology/CHANGELOG.md                             → "0.2.0: added field X (breaking)"
scripts/migrations/0.1.0_to_0.2.0.py             → walks instances/, transforms, bumps
CI gate                                           → fails if any record has schema_version
                                                    older than VERSION minus N (configurable)
```

### Pattern 6: Review Queue for AI-Extracted Records

**What:** AI-extracted records land in `instances/_pending/` (not `instances/entities/`). Promotion to canonical requires a PR that (a) sets `provenance.method` to `hybrid`, (b) adds `reviewer` + `reviewed_at`, (c) passes validators.

**When to use:** Any KB ingesting AI-extracted content (not used in v1 since v1 is mostly human + demo data; included as architectural hook for v2).

**Directory layout:**
```
instances/_pending/             # Quarantine zone for AI-extracted candidates
├── entities/
└── relations/
                                # Promotion = move file from _pending/ to canonical
                                # location + edit provenance fields. PR enforces.
```

---

## Data Flow

### Flow 1: Human Authoring a Wiki Narrative Page

```
Author opens Wiki.js UI
    ↓
Edits Markdown page (e.g., "CFM56-7B Maintenance Overview")
    ↓
Wiki.js writes to Postgres + queues Git push
    ↓ (≤5 min)
Wiki.js Git storage module pushes wiki/maintenance/cfm56-7b.md to repo
    ↓
GitHub Actions runs lint + link check (no schema check — wiki/ is freeform)
    ↓
to_ragflow.py polls Git → uploads/updates RAGFlow doc with metadata
    ↓
Available in RAGFlow Q&A with citation back to wiki/maintenance/cfm56-7b.md
```

### Flow 2: Adding a Structured Entity Record

```
Author creates instances/entities/component/cfm56-7b.yaml in branch
    ↓
Opens PR
    ↓
CI runs scripts/validate.py:
    ├── jsonschema validate against ontology/schemas/entities/component.schema.json
    ├── ID uniqueness check (no other comp:cfm56-7b)
    ├── Provenance check (method, source, confidence present)
    ├── Relation referent check (skipped — this record has no outgoing relations)
    └── Link check (source.ref doc:cfm56-7b-tcds-easa exists)
    ↓
PR review (human + Codex per CLAUDE.md risk-tier)
    ↓
Merge to main → record is canonical
    ↓ (Phase 3+)
Optional: to_rdf.py emits Turtle for triple store; to_neo4j.py emits Cypher for graph DB
```

### Flow 3: Ingesting a New Source Document

```
Importer (human or scripts/importers/) creates:
  docs/<domain>/<doc-id>/source.pdf
  docs/<domain>/<doc-id>/processed.md      (text-extracted)
  docs/<domain>/<doc-id>/metadata.yaml
    ↓
Author also creates instances/entities/document/<doc-id>.yaml
  (the Document entity record that references the file path + provenance)
    ↓
PR with both the doc files and the entity record
    ↓
CI validates entity record + checks file paths exist
    ↓
On merge: to_ragflow.py uploads processed.md to RAGFlow with metadata
  (RAGFlow 0.24.0 supports batch metadata management via HTTP API)
    ↓
Available in retrieval; citations link back to docs/<domain>/<doc-id>/
```

### Flow 4: User Asks a Question (RAG Path)

```
User in RAGFlow UI: "B737 起落架适航条款是哪些？"
    ↓
RAGFlow query expansion (LLM-generated synonyms)
    ↓
RAGFlow hybrid retrieval:
    ├── Vector search (BGE-M3 embeddings)
    ├── BM25 keyword search
    └── RRF fusion
    ↓
Top-K chunks retrieved, each with source pointer (doc-id + chunk-id)
    ↓
LLM answer generation with citation injection
    ↓
Guardrail: If no chunks above relevance threshold → reply "no source found"
    ↓ (Phase 2+ enhancement)
Citation post-processor: Resolve doc-id → instances/entities/document/<id>.yaml
                          → augment citation with title, version, confidentiality
    ↓
User sees answer with clickable citations linking back to:
    - Wiki.js page (for wiki/**.md sources)
    - docs/<domain>/<doc-id>/source.pdf (for document sources)
```

### Flow 5: Schema Evolution

```
Schema author identifies need (e.g., add maintenance_interval_hours to Component)
    ↓
Branch: edit ontology/schemas/entities/component.schema.json
        + bump ontology/VERSION (semver)
        + edit ontology/CHANGELOG.md
        + write scripts/migrations/0.1.0_to_0.2.0.py if breaking
    ↓
Migration script run locally → all instances/entities/component/*.yaml updated
    ↓
PR with: schema diff + version bump + CHANGELOG + migrated instances
    ↓
CI: schema-self-validates + all instances pass new schema + IDs preserved
    ↓
Merge → coordinated update; downstream consumers see new field
```

---

## Build Order (Dependency-Driven)

This is the build order implied by the architecture. Each step strictly depends on the prior.

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 0: Repo Skeleton                                       │
│   • Top-level dirs                                            │
│   • README.md with AI handoff guide                           │
│   • Empty ontology/, instances/, docs/, wiki/, deploy/        │
│   • .github/workflows/ stubs (no-op CI passing)               │
│   • .gitignore + .gitattributes (LFS for *.pdf)               │
└──────────────┬──────────────────────────────────────────────┘
               ↓ blocks
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Schema Layer (Ontology v0.1.0)                       │
│   • ontology/schemas/_meta.schema.json (provenance + version) │
│   • ontology/schemas/entity.base.schema.json                  │
│   • ontology/schemas/relation.base.schema.json                │
│   • 17 entity schemas + 13 relation schemas                   │
│   • ontology/vocabularies/*.yaml (controlled lists)           │
│   • ontology/CHANGELOG.md + VERSION = 0.1.0                   │
└──────────────┬──────────────────────────────────────────────┘
               ↓ blocks
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Validators + CI                                      │
│   • scripts/validate.py master                                │
│   • scripts/validators/{schema,ids,relations,provenance,       │
│     links}.py                                                  │
│   • tests/fixtures/valid + invalid                            │
│   • .github/workflows/validate.yml (now actually doing work)  │
│   • Schema self-tests against fixtures                        │
└──────────────┬──────────────────────────────────────────────┘
               ↓ blocks
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Demo Data + Document Spec                            │
│   • ≥1 instance per entity type (R10) → instances/entities/  │
│   • ≥3 relation instances → instances/relations/              │
│   • ≥3 source documents → docs/<domain>/<doc-id>/             │
│   • 1 ExpertNote with full provenance trail                   │
│   • docs/README.md = import workflow + metadata.yaml spec     │
│   • All passing CI                                            │
└──────────────┬──────────────────────────────────────────────┘
               ↓ blocks
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: RAG Pipeline Design (Document Only — no run)         │
│   • deploy/ragflow/README.md = chunking + embedding choices   │
│   • deploy/ragflow/ingestion-pipeline.sample.json             │
│   • Hybrid retrieval (BM25+vector+RRF) configuration spec     │
│   • Citation post-processor design                            │
│   • Guardrail spec (relevance threshold, no-source policy)    │
│   • Eval methodology (golden set, recall@K, citation correct.)│
└──────────────┬──────────────────────────────────────────────┘
               ↓ blocks
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Deployment Plan (docker-compose draft, no run)       │
│   • deploy/docker-compose/docker-compose.yml                  │
│   • Topology diagram in deploy/README.md                      │
│   • Wiki.js + Postgres + RAGFlow + (optional Authentik)       │
│   • Network/storage/auth selection rationale                  │
│   • GraphRAG interface preservation note                      │
│   • Wiki.js Git storage module config → points to wiki/       │
└──────────────┬──────────────────────────────────────────────┘
               ↓ blocks
┌─────────────────────────────────────────────────────────────┐
│ Phase 6: Roadmap + AI Handoff Polish                          │
│   • .planning/ROADMAP_FUTURE.md (GraphRAG / Agent / KG)       │
│   • Trigger conditions for each future phase                  │
│   • All design docs reviewed for "AI 接力开发指南" sections    │
│   • Glossary + open-question log                              │
└─────────────────────────────────────────────────────────────┘
```

**Phase ordering rationale:**

1. **Schema before instances**: Cannot validate what has no schema; cannot create demo data without schema. This is the LinkML/DataHub pattern.
2. **Validators before demo data**: Demo data is the *first user* of the validator; if validator is missing, demo data drifts and becomes the de facto schema (a recurring KB anti-pattern).
3. **Demo data before RAG design**: RAG design requires concrete examples to reason about chunking, retrieval, citations. Designing in the abstract = guesswork.
4. **RAG design before deployment plan**: Deployment topology depends on RAGFlow's actual configuration choices (e.g., embedding model determines GPU requirement).
5. **Roadmap last**: Future-phase triggers depend on knowing what current state actually looks like.

---

## Integration Boundaries

### Wiki.js ↔ Git Repo

| Property | Value |
|----------|-------|
| Module | Wiki.js native Git storage ([docs](https://docs.requarks.io/storage/git)) |
| Direction | Bidirectional |
| Scope | `wiki/` directory only |
| Format | Markdown (or HTML if VisualEditor used — pin to Markdown editor) |
| Sync interval | 5 min default (configurable) |
| Conflict resolution | Wiki.js performs `git pull --rebase`; on conflict, Wiki.js admin UI shows error |
| Auth | SSH key or PAT in Wiki.js admin |

**Boundary contract:** Wiki.js is the *only* writer to `wiki/`. Other contributors must edit via Wiki.js UI (not direct PR), or coordinate via "lock page" workflow. **Reverse direction**: edits committed to `wiki/` from outside (e.g., bulk rename PR) are pulled by Wiki.js on the next interval.

### Git Repo → RAGFlow

| Property | Value |
|----------|-------|
| Module | Custom: `scripts/exporters/to_ragflow.py` |
| Direction | One-way (Git → RAGFlow) |
| Trigger | Polling cron (Phase 5 recommendation) or webhook on Git push |
| API | RAGFlow [HTTP API](https://ragflow.io/docs/http_api_reference); 0.24.0+ supports batch metadata |
| Scope | `wiki/**.md` + `docs/**/processed.md` (NOT raw YAML in `instances/` for v1) |
| Metadata | Pulled from `metadata.yaml` sidecar; uploaded as RAGFlow doc meta_fields |
| Idempotency | Use file path + content hash as RAGFlow document_id; re-upload only if changed |

**Boundary contract:** RAGFlow's vector store is **disposable**. Rebuilding from Git must be a one-command operation (`python scripts/exporters/to_ragflow.py --rebuild`).

**Why YAML instances are NOT indexed in v1:** YAML records are short and structured; embedding them as-is gives poor retrieval. Phase 3 (GraphRAG) handles structured data via graph traversal, not vector search. For v1, the *narrative* (wiki/**.md and docs/**/processed.md) is what RAG indexes; YAML records are surfaced via citation back-links, not retrieval.

### Wiki.js ↔ RAGFlow (No Direct Connection)

**Decision:** Wiki.js and RAGFlow do NOT talk to each other directly. All cross-talk goes via Git.

**Rationale:**
- Decouples lifecycles (one can be down/upgraded without the other)
- Git becomes the audit log of every cross-system message
- Either tool can be replaced without rewriting the integration

**Citation back-link from RAGFlow → Wiki.js:**
- RAGFlow stores `source_url` in document metadata = `https://wiki.example.org/wiki/<page-path>`
- Citation post-processor in `to_ragflow.py` constructs the URL from the file path under `wiki/`
- Users clicking a citation in RAGFlow UI land on the live Wiki.js page

### Auth Gateway (Phase 2 Optional)

| Component | Auth Mode | Notes |
|-----------|-----------|-------|
| Wiki.js | OIDC via Authentik ([documented](https://integrations.goauthentik.io/documentation/wiki-js/)) | Native support, configurable in Wiki.js Admin → Authentication |
| RAGFlow | OAuth2 / proxy-header | RAGFlow's native auth has limited OIDC support as of 0.24.x; recommend reverse-proxy + header-based auth (Authentik proxy outpost) |
| docker-compose | Authentik service | Phase 2 optional; v1 can stay on local Wiki.js + RAGFlow accounts |

**v1 recommendation:** Skip Authentik. Document the integration plan in `deploy/authentik/README.md` as a Phase 2 hook. v1 uses local Wiki.js admin + local RAGFlow admin (acceptable given Out-of-Scope "single org, single role").

---

## Schema Versioning Architecture

### Three-Tier Versioning

| Tier | What is versioned | Where | Bump rule |
|------|-------------------|-------|-----------|
| **Ontology version** | The whole schema set as a unit | `ontology/VERSION` + `ontology/CHANGELOG.md` | Semver: breaking change anywhere = major |
| **Per-schema $id** | Each individual schema file | `"$id"` field in JSON Schema, e.g., `https://akb.example.org/schema/entity/component/0.1.0` | Same as ontology version (synchronized) |
| **Per-record schema_version** | What schema each instance was authored against | `schema_version: 0.1.0` field in every YAML record | Updated by migration scripts |

### Migration Workflow

```
1. Schema author proposes change in branch:
   - Edit ontology/schemas/entities/<type>.schema.json
   - Increment ontology/VERSION
   - Add CHANGELOG entry with breaking? yes/no flag
   - If breaking: write scripts/migrations/<from>_to_<to>.py

2. Migration script:
   - Walks instances/**/*.yaml
   - Transforms each record (add field, rename, etc.)
   - Bumps each record's schema_version
   - Writes back

3. CI gate:
   - Validates ALL records against new schema
   - Fails if any record has schema_version > N versions behind (configurable, default 1)

4. PR review: schema diff + migration script + migrated records all in one PR
```

### Validator Behavior

```python
# scripts/validators/schema.py (sketch)
def validate(record_path: Path, record: dict) -> list[str]:
    rec_ver = record.get("schema_version")
    cur_ver = read_ontology_version()  # from ontology/VERSION

    if rec_ver is None:
        return [f"{record_path}: schema_version field is required"]

    if not version_compatible(rec_ver, cur_ver, max_lag_minor=1):
        return [
            f"{record_path}: schema_version {rec_ver} is too old "
            f"(current {cur_ver}); run scripts/migrations/{rec_ver}_to_{cur_ver}.py"
        ]

    schema_for_version = load_schema_at_version(record["type"], rec_ver)
    return jsonschema_validate(record, schema_for_version)
```

**Why per-record schema_version is required:** Allows gradual migration (instances at version N can coexist with version N+1 for one cycle), and gives validators enough info to load the right schema for old records during transition windows.

---

## Provenance & Confidence Storage

### Decision: Embedded in Each Record (Not Separate Store)

**Where:** Inside each entity/relation YAML, under top-level `provenance`, `source`, and `confidence` keys.

**Why embedded (not separate provenance store):**
- Single file = single audit unit (Git diff shows knowledge + provenance together)
- No join needed at validation time
- Self-contained record can be exported anywhere without losing trail
- Mirrors W3C PROV embedded pattern (vs. side-car PROV graphs which require infra)

### Required Schema (in `_meta.schema.json`, inherited by all entity/relation schemas)

```json
{
  "type": "object",
  "required": ["id", "type", "schema_version", "provenance", "source", "confidence"],
  "properties": {
    "provenance": {
      "type": "object",
      "required": ["method"],
      "properties": {
        "method": {
          "type": "string",
          "enum": ["human", "ai_extracted", "hybrid"]
        },
        "reviewer": {
          "type": "string",
          "description": "Required if method != 'ai_extracted'; required for promotion"
        },
        "reviewed_at": { "type": "string", "format": "date-time" },
        "extractor": {
          "type": "string",
          "description": "Required if method ∈ {'ai_extracted', 'hybrid'}; e.g., 'claude-opus-4.7' or 'codex-gpt-5.4'"
        },
        "extractor_prompt_hash": {
          "type": "string",
          "description": "SHA-256 of the prompt used; supports reproducibility"
        }
      }
    },
    "source": {
      "type": "array",
      "minItems": 1,
      "items": {
        "oneOf": [
          { "$ref": "#/$defs/document_source" },
          { "$ref": "#/$defs/url_source" },
          { "$ref": "#/$defs/expert_source" }
        ]
      }
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    }
  }
}
```

### Cross-Validator Rule (provenance.py)

- `method == "ai_extracted"` AND `confidence > 0.85` → **REJECT** (must be reviewed and promoted to "hybrid")
- `method == "human"` AND `reviewer` missing → **REJECT**
- `source` array empty → **REJECT** (zero-source AI claim is the H-Darrieus failure mode)

---

## Future-Proofing for GraphRAG / Agent / KG

### Migration Path Hooks (Built into v1)

| Future Phase | v1 Hook Already in Place | What Phase Adds |
|--------------|--------------------------|------------------|
| **Phase 3a: GraphRAG** | YAML `id` is URI-style (`comp:cfm56-7b`) → maps directly to RDF/Neo4j node ID; relations are explicit YAML records (not buried in entity fields) | Run `scripts/exporters/to_neo4j.py`; layer Cypher queries on top of RAGFlow vector retrieval |
| **Phase 3b: Knowledge Graph (Neo4j/Nebula)** | Same — IDs stable, relation files separate | Stand up graph DB; write Cypher loader that reads `instances/relations/**/*.yaml` |
| **Phase 4a: RDF/SPARQL** | `to_rdf.py` placeholder; URI scheme designed; controlled vocabularies in `vocabularies/` map to SKOS | Implement `to_rdf.py`: each YAML → Turtle triples; URI = `https://akb.example.org/<type>/<id>` |
| **Phase 4b: Decision Agent** | Out of Scope for v1 by user requirement; provenance fields make tool-call traceability easy when added | Build agent loop on top of RAGFlow + KG; provenance trail auto-attached to AI outputs |
| **Phase 5: External standard mapping (ATA / S1000D / AP233)** | `ontology/mappings/*.placeholder.yaml` files signal intent; `ata_chapter` field already in Component schema | Fill in mapping files; add validators that check ATA codes are in the controlled vocabulary |

### Guardrail Against Architectural Drift

The v1 architecture is *deliberately* compatible with later graph-DB migration. The following design choices are explicit prophylactics:

1. **No entity field stores a relation by ID inline** — every relation goes in `instances/relations/`. (Anti-pattern: putting `parent_aircraft: ac:b737-800` inside a Component record. This works in YAML but breaks bidirectional traversal in graph DB.)
2. **No global secondary indexes are computed** — the validator checks referential integrity by scanning, not by maintaining a separate index file. This means there is no v1 index to migrate.
3. **No application code consumes YAML directly** — all consumers go through `scripts/exporters/`. Adding a new backend = new exporter, not refactor.

---

## Failure Modes & Recovery

| Component dies | Impact | Recovery |
|-----------------|--------|----------|
| **Wiki.js (app)** | No new wiki pages can be authored; existing pages still browsable via Git/GitHub UI | Restart container; if Postgres OK, no data loss; if Postgres lost, re-init Wiki.js and let Git storage module sync `wiki/` back |
| **Wiki.js Postgres** | Wiki.js cache lost (users, page metadata) | Restore from backup; Git storage module reseeds page content; users re-created (small N for v1) |
| **RAGFlow (app)** | RAG Q&A unavailable; KB authoring unaffected | Restart; if vector store survived, full recovery; otherwise re-run `to_ragflow.py --rebuild` |
| **RAGFlow vector store** | Re-index needed (~minutes-to-hours depending on doc volume) | `to_ragflow.py --rebuild` regenerates from Git |
| **Git repo (origin)** | All editing blocked; Wiki.js + RAGFlow continue from caches | Restore from any local clone (every contributor has a copy); push to new origin |
| **Authentik (Phase 2)** | Login blocked for users who depend on SSO | Bypass with local accounts; restore Authentik from backup |

**Single point of failure analysis:** Git origin is the only true SPOF, and Git's distributed nature mitigates it (every clone = backup). Document store binaries via Git LFS — confirm LFS hosting choice has its own backup story (GitHub LFS does; self-hosted needs explicit backup).

**Backup policy (v1 minimum):**
- Git remote: rely on GitHub/GitLab redundancy
- Wiki.js Postgres: nightly `pg_dump` to a separate volume
- RAGFlow data: not backed up — declared as "rebuildable from Git"

---

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| **v1 (≤5 users, ≤500 entities, ≤100 docs)** | Single VPS / single Mac; docker-compose; SQLite-style operation. **No changes from baseline.** |
| **10–50 users, ≤5K entities, ≤1K docs** | Move Postgres to dedicated container; allocate GPU for embedding (BGE-M3 on CPU is slow at scale); add Authentik for SSO |
| **50+ users, ≤50K entities, ≤10K docs** | Consider migrating relations to a real graph DB (the migration path is already designed in); split RAGFlow vector store (Infinity → Elasticsearch cluster); CDN for `docs/` static files |
| **Enterprise (multi-org, ≥100K entities)** | Likely outgrowing Wiki.js — consider Backstage/DataHub-class platform; ontology layer migrates to LinkML; Git repo structure preserved |

### First Bottleneck

**Validator wall-time on large instance count.** When `instances/` exceeds ~10K files, the full-repo validator pass exceeds CI budgets. **Fix:** introduce sharded validation — only validate files touched by the PR + their dependents. Hook is already in `scripts/validate.py` (filter by `--changed` flag).

### Second Bottleneck

**RAGFlow embedding throughput** when `docs/` exceeds ~500 PDFs. **Fix:** GPU host or remote embedding API; RAGFlow supports both.

---

## Anti-Patterns (Aviation KB-Specific)

### Anti-Pattern 1: Putting Relations Inside Entity Records

**What people do:**
```yaml
# instances/entities/component/cfm56-7b.yaml
id: comp:cfm56-7b
parent_aircraft: ac:b737-800   # ← embedding the relation inline
maintenance_tasks:             # ← embedding a list of relation targets
  - mt:cfm56-7b-borescope
  - mt:cfm56-7b-oil-change
```

**Why wrong:**
- Relations have their own metadata (provenance, confidence, validity period) that has nowhere to live
- Bidirectional traversal requires duplicate data on both ends
- Migrating to graph DB requires teasing these out — exactly the refactor we want to avoid

**Do this instead:** Every relation gets its own file under `instances/relations/<predicate>/`.

### Anti-Pattern 2: Treating Wiki.js Pages as Authoritative Knowledge

**What people do:** Author "the spec for X" as a wiki page; let RAGFlow index it; rely on retrieval to answer questions about X.

**Why wrong:** Wiki pages are narrative, not structured. AI cannot reliably extract "the maximum operating altitude of B737-800" from a paragraph; structured data must be in the entity record. Narrative drift goes undetected; structured drift fails CI.

**Do this instead:** Wiki pages explain and contextualize; entity records hold the authoritative structured facts. The wiki page links to `comp:cfm56-7b`, not the other way around.

### Anti-Pattern 3: AI-Extracted Records Promoted Without Human Review

**What people do:** Run an extraction script, dump output to `instances/entities/`, pass CI because schema is correct.

**Why wrong:** This is exactly the "captured H-Darrieus chart that did not exist" failure mode in user's MEMORY.md. AI confidence on its own output is unreliable.

**Do this instead:** AI output lands in `instances/_pending/`; promotion to canonical requires (a) `provenance.method = "hybrid"`, (b) human `reviewer` + `reviewed_at`, (c) explicit confidence reduction or boost based on review.

### Anti-Pattern 4: Skipping the Document Entity Record for Source PDFs

**What people do:** Drop a PDF in `docs/foo/bar/source.pdf`, write a `metadata.yaml`, but never create a `Document` entity in `instances/entities/document/`.

**Why wrong:** Other entity records cite documents via `source.ref: doc:bar`; if no Document entity exists, the link checker fails; reverse traversal "what entities cite this document" is impossible.

**Do this instead:** Every imported source document gets a Document entity record. The importer script enforces this (`scripts/importers/document_metadata_template.py` produces both files).

### Anti-Pattern 5: Encoding Aircraft Hierarchy in Folder Structure

**What people do:**
```
instances/entities/aircraft_model/b737/components/landing_gear/...
```

**Why wrong:** Hierarchy belongs in *relations*, not in *file paths*. Folder hierarchy is one tree; aircraft systems form a DAG (a single hydraulic pump can be `part_of` multiple subsystems).

**Do this instead:** Flat `instances/entities/<type>/<id>.yaml` layout. All structure is in `instances/relations/`.

### Anti-Pattern 6: Letting Wiki.js Edit Both `wiki/` and `instances/`

**What people do:** Configure Wiki.js Git storage module to mount the entire repo so the wiki UI can edit YAML records too.

**Why wrong:** Wiki.js edits via WYSIWYG; YAML loses formatting and comments; CI starts failing on structural changes; round-trip corruption.

**Do this instead:** Wiki.js Git storage scope is `wiki/` only. Structured records are PR-only.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| GitHub/GitLab (origin) | SSH/HTTPS for both Wiki.js Git module + contributors | Use deploy key for Wiki.js; PAT for `to_ragflow.py` if needed |
| RAGFlow [HTTP API](https://ragflow.io/docs/http_api_reference) | Bearer token; called from `to_ragflow.py` | API token stored in env var; rotate per-deployment |
| Authentik (Phase 2) | OIDC for Wiki.js ([guide](https://integrations.goauthentik.io/documentation/wiki-js/)); reverse-proxy outpost for RAGFlow | RAGFlow native OIDC support is partial as of 0.24.x — verify before Phase 2 commit |
| Embedding model (Phase 4) | RAGFlow internal config; recommend BGE-M3 or bge-large-zh per AeroPower-RAG findings | Self-hosted via Ollama or remote API |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Wiki.js ↔ Git | Wiki.js Git storage module (bidirectional, 5-min interval) | Scope: `wiki/` only |
| Git ↔ RAGFlow | `scripts/exporters/to_ragflow.py` (Git → RAGFlow only) | Idempotent; supports `--rebuild` |
| Validator ↔ Schema | `scripts/validate.py` reads `ontology/schemas/`; runs in CI and locally | Single entry point |
| Entity record ↔ Document file | `source[*].ref = doc:<id>` resolved by link checker to `instances/entities/document/<id>.yaml` AND `docs/**/<id>/` path | Both must exist |
| Future: YAML ↔ Graph DB | `scripts/exporters/to_neo4j.py` (placeholder in v1) | Hook exists; implementation in Phase 3 |

---

## Sources

### Verified (HIGH confidence)
- [Wiki.js Git Storage documentation](https://docs.requarks.io/storage/git) — bidirectional sync mechanics, 5-min default interval
- [authentik Wiki.js integration guide](https://integrations.goauthentik.io/documentation/wiki-js/) — OIDC setup steps verified
- [RAGFlow HTTP API reference](https://ragflow.io/docs/http_api_reference) — document ingestion + metadata API
- [RAGFlow release notes](https://ragflow.io/changelog) — 0.24.0 (Feb 2026) batch metadata management; 0.21.0 ingestion pipeline
- [RAGFlow ingestion pipeline quickstart](https://ragflow.io/docs/ingestion_pipeline_quickstart) — pipeline composition
- [Wiki.js storage overview](https://docs.requarks.io/storage) — bidirectional capability of Git module

### Inferred from broader patterns (MEDIUM confidence)
- LinkML / DataHub / OpenMetadata schema-first patterns → ontology/instances split rationale
- W3C PROV embedded model → provenance-as-fields rationale
- AeroPower-RAG findings (user's prior project) → BGE-M3 / bge-large-zh embedding choice; hybrid retrieval (BM25+vector+RRF) viability for Chinese aviation docs
- cfd-harness-unified `.planning/` + Notion-as-mirror → Git-as-truth pattern

### Open questions (flagged for Phase 4 / 5 follow-up)
- **RAGFlow Authentik OIDC support level** — confirm via direct test in Phase 2 deployment; native support may require reverse-proxy outpost pattern
- **Wiki.js 2.x vs 3.x** — 3.x was beta as of 2026; recommend pinning 2.5.x; revisit at Phase 5
- **Git LFS host choice** — affects backup story; decide before first PDF ingest

---

*Architecture research for: aviation knowledge base MVP (Wiki.js + RAGFlow + YAML/JSON Schema + Git)*
*Researched: 2026-05-03*

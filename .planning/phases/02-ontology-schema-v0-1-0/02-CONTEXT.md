# Phase 2: Ontology Schema v0.1.0 — Context

**Gathered:** 2026-05-03
**Status:** Ready for research / planning
**Discuss mode:** discuss (interactive, 4 areas selected by user)

## AI 接力开发指南

> Fresh Claude / Codex / DeepSeek session opening this file cold should be able to read this header and the `<decisions>` block and immediately know what's locked for Phase 2.

- **Read first:** PROJECT.md (Core Value), REQUIREMENTS.md §Ontology+Provenance+Versioning, research/SUMMARY.md (10 pinned decisions), this file
- **Then:** spawn `/gsd-research-phase 2` to verify open questions before `/gsd-plan-phase 2`
- **Locked at this discuss:** entity-set (17 baseline + 3 added), relation-set (13 baseline + 3 added; 2 candidates internalized as fields), provenance/confidence/i18n/version_history field shapes, triple-export format, schema versioning placement, migrations language
- **Open (research will resolve):** ATA chapter enum strictness, S1000D Issue 6 DMC field shape, exact `_meta.schema.json` JSON Schema Draft 2020-12 syntax

<domain>
## Phase Boundary

**Deliver: schema-enforced contracts before a single instance file is written.**

Materializes:
1. `ontology/_meta.schema.json` — base provenance + confidence + source schemas (composed by every entity/relation)
2. `ontology/schemas/entity.base.schema.json` + 20 entity type schemas (17 baseline + Material + TestCase/TestReport + Person/Organization)
3. `ontology/schemas/relation.base.schema.json` + 16 relation type schemas (13 baseline + interfaces_with + complies_with + applicable_during_phase)
4. `ontology/vocabularies/{ata-chapters,jurisdictions,provenance-methods}.yaml`
5. `ontology/mappings/{ata-to-iso10303,s1000d-dmc-reserved}.md` (placeholders + ADRs)
6. `ontology/CHANGELOG.md` + `ontology/VERSION` (= `0.1.0`)
7. `migrations/` directory with placeholder pattern doc (Python)
8. `scripts/exporters/to_jsonl_triples.py` — Phase 2 enriches stub with schema-derived design notes (no implementation)
9. ADR set under `.planning/decisions/` for all gray-area resolutions

**Out of scope this phase** (handled elsewhere):
- Validators that enforce schema rules → Phase 3
- Demo data instances → Phase 4
- RAG pipeline / chunking → Phase 5
- Real docker-compose deployment → Phase 6 / never (per Constraints)
- Configuration / EffectivityRange entity → defer to v0.2.0

</domain>

<decisions>
## Implementation Decisions

### Entity additions (ADR-002)

- **D-01:** Accept **Material** entity in v0.1.0 — alloy / composite / heat-treatment families. Aerospace material constraints are first-class (titanium FAR 25.853, composite damage tolerance per AC 20-107B). Refusing now means `Component.composition` becomes free-text and rebuilds later.
- **D-02:** Accept **TestCase / TestReport** entity in v0.1.0 — `Requirement.verified_by` currently can only point at Procedure, which is too narrow for DO-160/DO-178C/DO-254 audit trails. TestCase = test plan; TestReport = test outcome with results.
- **D-03:** Defer **Configuration / EffectivityRange** entity to v0.2.0 — FEATURES.md flagged as v1.x. v0.1.0 demo data does not yet exercise applicability-by-serial-number patterns. Re-evaluate when AD/SB demo data lands.
- **D-04:** Accept **Person / Organization** entity in v0.1.0 — **mandatory**. `provenance.actor`, `provenance.reviewer`, `source.published_by` are URI fields. Without Person/Org schema they degrade to free text and break the H-Darrieus lock.

**Net entity count v0.1.0:** 17 baseline + 3 additions = **20 entity schemas** (Configuration deferred).

### Relation additions (ADR-003)

- **D-05:** Accept **interfaces_with** in v0.1.0 — peer-tier system↔system interface (avionics ↔ ECS via ARINC 429). Boundary with `requires` documented in ADR with worked examples.
- **D-06:** Accept **complies_with** in v0.1.0 — explicit normative compliance (Structure complies_with FAR §25.305). Sharper than the generic `constrained_by`.
- **D-07:** **has_revision** is NOT a relation. Internalize as entity field `version_history: [{version, date, author, change_summary}]` (D-15 below). Avoids low-value version-link explosion at the relation layer.
- **D-08:** Accept **applicable_during_phase** in v0.1.0 — flight phase (taxi/takeoff/cruise/approach/landing/missed/emergency) is independent semantics from `applicable_to`.
- **D-09:** **generated_by** is NOT a relation. Already encoded by `provenance.actor` (Person/Org URI) + `source.tool` (string). A separate relation duplicates.

**Net relation count v0.1.0:** 13 baseline + 3 additions = **16 relation schemas** (has_revision and generated_by become fields).

### Boundary clarifications (must be in ADRs with examples)

- **D-10:** `requires` vs `interfaces_with`: `requires` = cross-tier dependency (Component requires MaintenanceTask; SimulationCase requires MeshRequirement). `interfaces_with` = peer-tier (AvionicsBay interfaces_with ECS). Worked examples mandatory in `ontology/schemas/relation.requires.schema.json` and `relation.interfaces_with.schema.json` `description` fields.
- **D-11:** `constrained_by` vs `complies_with`: `constrained_by` = generic, any constraint type (cost, weight, regulation). `complies_with` = explicit regulation/standard compliance. Same worked-examples discipline.
- **D-12:** `equivalent_to` is NOT used for cross-language pairs (per research/SUMMARY.md decision #3). Bilingual handled via `i18n` field.

### Schema field shapes (ADR-004)

- **D-13:** `confidence: { score: number (0.0–1.0), rationale: string (≥1 sentence) }` — decimal scale required by H-Darrieus lock (`score > 0.85` threshold). `rationale` mandatory; empty string fails validation.
- **D-14:** `i18n` flat shape: `{ label: { zh, en }, full_text: { zh, en } }` — keys are language codes (ISO 639-1). Either or both languages may be empty (entity-level decision; e.g. accident-report Chinese-only). Per-translation provenance is NOT in v0.1.0; if needed later, sub-key `_provenance` can be added without breaking schema.
- **D-15:** `version_history` array shape: `[{ version: semver string, date: ISO8601, author: Person/Org URI, change_summary: string (≥1 sentence) }]`. Mandatory once a record bumps from v1; absence means v1.

### Provenance enum naming (ADR-005)

- **D-16:** `provenance.method` enum: **`human` | `ai_extracted` | `hybrid_reviewed`**. Verbatim per research/SUMMARY.md (#5). H-Darrieus lock validator condition: `(method == "ai_extracted") AND (confidence.score > 0.85) AND (reviewer is null OR reviewer == "")` → REJECT.
- **D-17:** Promotion from `instances/_pending/` to canonical requires the YAML to set `provenance.method = "hybrid_reviewed"` AND `reviewer` non-empty (Person/Org URI) AND `reviewed_at` ISO8601 timestamp. Enforced at validator layer (Phase 3), but schema-required fields are pre-validated here.

### Triple-export format (ADR-006)

- **D-18:** **JSONL `{s, p, o, provenance, confidence}`** — one triple per line. `s` and `o` are entity URIs (`aviationkb://<type>/<slug>@<version>`); `p` is relation type slug; `provenance` and `confidence` carry forward from the relation record. `jq`-friendly, `wc -l` triple count, conversion to JSON-LD/Turtle is trivial. RDF/Turtle deferred to v0.3.0+ if PROV-O alignment becomes valuable.
- **D-19:** Phase 2 only **enriches the existing `scripts/exporters/to_jsonl_triples.py` stub** — adds schema-derived design notes (which entity fields → triple components) but no implementation. Implementation lands in Phase 5 (RAG pipeline) or v0.2.0 GraphRAG sprint.

### Schema versioning placement (ADR-007)

- **D-20:** **Both** per-file `version` AND per-record `schema_version` are required.
  - `ontology/VERSION` (single line) = current ontology release version (semver, starts `0.1.0`).
  - Each schema file's frontmatter `version` field = schema's evolution within current ontology release.
  - Each instance YAML's `schema_version` = the schema version this record was written against (frozen at write time; CI rejects records older than N-1).
- **D-21:** `ontology/CHANGELOG.md` records every schema bump with date + rationale + breaking-change flag.
- **D-22:** `migrations/<from>_to_<to>.py` Python scripts handle automated upgrades. v0.1.0 ships placeholder pattern doc only; first real migration lands when `0.1.0 → 0.2.0` happens (likely Phase 4+ if Configuration entity is added).

### URI / ID scheme (carried from research/SUMMARY.md #4)

- **D-23:** External URI: `aviationkb://<type>/<slug>@<version>` (e.g. `aviationkb://aircraft-model/boeing-737-max-8@1`).
- **D-24:** Internal ID (foreign-key field on YAML): `<type-prefix>:<kebab-slug>` (e.g. `am:boeing-737-max-8`, `comp:cfm56-7b-engine`). Type prefix mapping: `am` AircraftModel, `sys` AircraftSystem, `subsys` Subsystem, `comp` Component, `req` Requirement, `regclause` RegulationClause, `std` Standard, `proc` Procedure, `fmode` FailureMode, `mtask` MaintenanceTask, `cfdmethod` CFDMethod, `simcase` SimulationCase, `mesh` MeshRequirement, `turb` TurbulenceModel, `acc` AccidentCase, `doc` Document, `note` ExpertNote, `mat` Material, `test` TestCase, `report` TestReport, `org` Organization, `pers` Person.
- **D-25:** Slug rules: lowercase ASCII + digits + hyphen; max 64 chars; must be unique within type; never reused after retirement (validator-enforced in Phase 3).

### migrations/ scripting

- **D-26:** **Python** for migration scripts. Aligns with Phase 3 validators (Python). Use `ruamel.yaml` (preserves comments) + `jsonschema`.

### Claude's Discretion (no decision needed from user)

- Exact `_meta.schema.json` JSON Schema Draft 2020-12 syntax — Claude follows ajv/check-jsonschema-friendly conventions
- Internal directory layout under `ontology/schemas/` (e.g. `entity/` vs flat) — Claude picks pragmatic
- ADR file naming convention under `.planning/decisions/` — Claude uses `ADR-NNN-<slug>.md` pattern unless STATE.md says otherwise
- ATA chapter list source seeding — Claude picks one of: ATA iSpec 2200 official PDF, Wikipedia ATA chapter table, or partial seed — research phase will confirm
- Validator-rule pseudocode in schema descriptions — Claude can place hints (validator implementation lives in Phase 3)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents (researcher / planner / executor) MUST read these before acting.**

### Project-level (apply to every phase)
- `.planning/PROJECT.md` — Core Value, Constraints, Out of Scope, Key Decisions
- `.planning/REQUIREMENTS.md` §Ontology Entities, §Ontology Relations, §Provenance/Confidence/Audit, §Schema Versioning — 51 REQ-IDs Phase 2 must satisfy
- `CLAUDE.md` — auto-generated stack pins (yamllint 1.38, check-jsonschema 0.37.1, JSON Schema Draft 2020-12)

### Research artifacts (research is already done, NOT re-running)
- `.planning/research/SUMMARY.md` §Pinned Decisions (10 cross-cutting decisions)
- `.planning/research/STACK.md` §Schema/Validation Layer
- `.planning/research/FEATURES.md` §Ontology Coverage (entity/relation gap analysis)
- `.planning/research/ARCHITECTURE.md` §Schema-first ontology + §Provenance/confidence design
- `.planning/research/PITFALLS.md` §P1-P5 (provenance failures), §P11 (AI handoff)

### Phase 1 outputs (foundation locked)
- `.planning/phases/01-repo-skeleton-git-baseline-prd-v0/01-VERIFICATION.md` — Phase 1 status (passed 6/6)
- `.planning/design/PRD_v0.md` §Deliverables — Ontology section reflects accepted entities/relations
- `.pre-commit-config.yaml` — `check-jsonschema` already wired to `^ontology/schemas/.*\.json$`; new schemas auto-validate on commit
- `.yamllint` — relaxed config (line-length warning 200) for bilingual content
- `.github/workflows/ci.yml` — `lint` job runs pre-commit on every PR

### To verify in research phase (not yet read)
- ATA iSpec 2200 chapter list — research phase WebFetch / spec lookup before populating `ontology/vocabularies/ata-chapters.yaml`
- S1000D Issue 6 DMC structure (s1000d.org / S1000D Spec Issue 6.0 release notes 2024) — research-phase WebFetch confirms `s1000d_dmc` reserved field shape
- JSON Schema Draft 2020-12 spec (`unevaluatedProperties`, `$dynamicAnchor`) — research can verify ajv/check-jsonschema 0.37.1 support level

### Tools (used during execution)
- `node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" commit ...` — atomic commits per task
- `pre-commit run --all-files` — local validation gate (already wired)
- `check-jsonschema --check-metaschema ontology/schemas/*.json` — Draft 2020-12 self-validation

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets (Phase 1 outputs)
- `scripts/exporters/to_jsonl_triples.py` — stub exists; Phase 2 enriches with schema-derived design notes (D-19)
- `scripts/exporters/{to_rdf,to_neo4j}.py` — stubs; Phase 2 NOT touching (deferred to v0.3.0+)
- `.pre-commit-config.yaml` — `check-jsonschema` regex `^ontology/schemas/.*\.json$` will pick up every new schema automatically — zero pre-commit config changes needed
- `.yamllint` — line-length warning 200 means bilingual `full_text` fields don't fail CI
- `instances/_pending/.gitkeep` — quarantine dir already exists (D-17)
- `migrations/` — does NOT exist yet; Phase 2 creates it as `ontology/migrations/` per D-22

### Established Patterns
- AI 接力开发指南 header — every design doc must open with this section (Phase 1 README + PRD v0 baseline)
- Atomic commits via `gsd-tools commit` — every schema file is its own commit (executor enforces)
- bilingual is curated, not auto-translated — i18n.zh / i18n.en written by humans (PROJECT.md hard rule)

### Integration Points
- `pre-commit-config.yaml` already locked on `ontology/schemas/**/*.json` — Phase 2 schemas plug in automatically
- CI workflow already has `lint` job that runs pre-commit — green-CI lock survives Phase 2 schema additions
- `.github/workflows/ci.yml` already has `schema-validation-stub` job marked "Phase 1 STUB — real in Phase 3" — Phase 3 will replace with `check-jsonschema --check-metaschema`

</code_context>

<specifics>
## Specific Ideas

- The H-Darrieus lock (validator REJECT condition in D-16) is **the** showcase of Core Value. Every ADR for provenance/confidence MUST cite H-Darrieus by name (not just the user's MEMORY.md pointer) so future Claude sessions know this isn't theoretical.
- ADRs land in `.planning/decisions/ADR-NNN-<slug>.md`. NNN = 3-digit zero-padded; reset per project; ADR-001 reserved for Phase 1 PRD-v0-vs-v1 split (created in Phase 6).
- Phase 2 ADRs proposed: ADR-002 entity additions, ADR-003 relation additions, ADR-004 schema field shapes, ADR-005 provenance enum, ADR-006 triple export, ADR-007 schema versioning. Six ADRs is the target.
- worked examples in schema `description` fields are MANDATORY for any entity/relation whose semantics overlap another (requires↔interfaces_with, constrained_by↔complies_with). 1-line is enough; long examples → ADR.

</specifics>

<deferred>
## Deferred Ideas

- **Configuration / EffectivityRange entity** → v0.2.0 (D-03). Trigger: when AD/SB demo data needs serial-number applicability scope. Until then `applicability_scope: free_text` on RegulationClause / Procedure suffices.
- **JSON-LD / RDF Turtle export** → v0.3.0+. Trigger: GraphRAG sprint. Path: JSONL → JSON-LD via `@context` injection (cheap), JSONL → RDF via PROV-O alignment.
- **Per-translation provenance on i18n** → v0.2.0+. Trigger: bilingual reviewer audit asks "who translated this? when?" Path: add `_provenance` sub-key to i18n.zh / i18n.en.
- **ATA chapter enum vs string-pattern** → resolve in `/gsd-research-phase 2` then ADR. Recommendation: enum strict; ATA chapter list is finite and stable.
- **S1000D Issue 6 DMC field shape** → resolve in `/gsd-research-phase 2` via WebFetch on s1000d.org. Stub field is `s1000d_dmc: optional string` if research stalls.
- **DO-178C / DO-254 specific TestCase fields** (test category, criticality level, evidence type) → v0.2.0+. v0.1.0 ships generic TestCase shape.

</deferred>

---

*Phase: 02-ontology-schema-v0-1-0*
*Context gathered: 2026-05-03 via interactive discuss (4 areas, 16 decisions captured)*
*Next: `/gsd-research-phase 2` to verify ATA chapters list + S1000D Issue 6 DMC shape, then `/gsd-plan-phase 2`*

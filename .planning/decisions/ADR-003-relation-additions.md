# ADR-003 — Relation Additions for v0.1.0 (interfaces_with, complies_with, applicable_during_phase accepted; has_revision and generated_by internalized as fields)

Status: ACCEPTED
Date: 2026-05-03
Deciders: user (CONTEXT.md interactive discuss, 2026-05-03)
Implements: D-05, D-06, D-07, D-08, D-09, D-10, D-11, D-12, ONT-R-15, ONT-R-16, ONT-R-17, ONT-R-18, ONT-R-19

## AI 接力开发指南

> Fresh Claude / Codex / DeepSeek session opening this ADR cold should be able to read the next 3 paragraphs and immediately know: (1) which 3 relations land as schemas in Plan 09, (2) which 2 candidates are NOT relations (encoded as fields instead), and (3) which boundary worked-examples MUST be copied verbatim into the relation schema `description` fields.

This ADR resolves the five research-recommended relation additions evaluated in REQUIREMENTS.md ONT-R-15..19. **Three are accepted** as relation schemas (`interfaces_with`, `complies_with`, `applicable_during_phase`). **Two are rejected** — the underlying need is real but better expressed as a FIELD on entities than as a relation:

- `has_revision` becomes the `version_history[]` field on `entity.base` (D-15, ADR-004 §version_history)
- `generated_by` is encoded by `provenance.actor` (Person/Org URI) + `provenance.tool` (string) — already provided by `_meta.schema.json#/$defs/provenance`

**Read this ADR before authoring** `relation.interfaces-with.schema.json`, `relation.complies-with.schema.json`, `relation.applicable-during-phase.schema.json` (Plan 09), and before authoring the worked-example sections of `relation.requires.schema.json`, `relation.constrained-by.schema.json`, `relation.equivalent-to.schema.json` (Plan 08). The boundary worked-example tables in this ADR are the canonical source — copy the USE / DON'T USE bullets verbatim into the leaf schema `description` fields (Pitfall #4 lock).

## Context

REQUIREMENTS.md ONT-R-15..19 listed five candidate relation additions. Each was evaluated against three filters:

1. Does the underlying semantic exist in real aviation engineering practice (FAA/EASA cert, ATA, S1000D, CFD validation workflows)?
2. Is it modeled better as a relation (graph edge between two entities) or as a field (property on a single entity)?
3. If relation: does it overlap with an existing relation? If yes, can the boundary be made explicit with worked examples readable by a fresh AI session?

The answers, in tabular form, drive the §Decision section.

## Decision

| REQ-ID | Candidate | Decision | Rationale |
|--------|-----------|----------|-----------|
| ONT-R-15 | **interfaces_with** | ACCEPT (D-05) | Peer-tier system↔system interface (e.g. avionics ↔ ECS via ARINC 429) is independent semantics from `requires` (cross-tier dependency) — see boundary table §`requires` vs `interfaces_with` below |
| ONT-R-16 | **complies_with** | ACCEPT (D-06) | Explicit regulatory / standards compliance is sharper than the generic `constrained_by` and is required for audit-grade airworthiness traceability — see boundary table §`constrained_by` vs `complies_with` below |
| ONT-R-17 | **has_revision** | REJECT — internalize as field (D-07) | Every entity gets `version_history[]` per D-15 / ADR-004; a separate has_revision relation would explode into per-version edges with no query benefit |
| ONT-R-18 | **applicable_during_phase** | ACCEPT (D-08) | Flight phase enum (taxi / takeoff / cruise / approach / landing / missed / emergency) is independent semantics from `applicable_to` (which targets aircraft model / system, not phase of flight) |
| ONT-R-19 | **generated_by** | REJECT — already encoded (D-09) | `provenance.actor` (Person/Org URI) + `provenance.tool` (e.g. `claude-opus-4-7`) already capture the same information; a separate relation duplicates and risks drift |

**Net relation count v0.1.0 = 13 baseline + 3 accepted = 16 relation schemas.**

## Boundary clarifications (worked examples)

### `requires` vs `interfaces_with` (D-10)

**`requires`** = cross-tier dependency between entities at different architectural levels.

| Use | Don't use |
|-----|-----------|
| `Component(brake_disc) requires MaintenanceTask(brake_inspection_500h)` | NOT `Component(brake_disc) requires Component(brake_pad)` (that's part_of within an assembly) |
| `SimulationCase(takeoff_performance) requires MeshRequirement(yPlus_target_30)` | NOT `AvionicsBay requires ECS` (that's interfaces_with — peer systems) |
| `Procedure(emergency_landing) requires Component(landing_gear)` | NOT `Standard requires Standard` (that's a citation — use cites) |

**`interfaces_with`** = peer-tier interface between two entities at the same architectural level.

| Use | Don't use |
|-----|-----------|
| `AircraftSystem(avionics) interfaces_with AircraftSystem(ECS) via ARINC 429` | NOT `AircraftSystem(avionics) interfaces_with Component(GPS_unit)` (use part_of for parent-child) |
| `AircraftSystem(hydraulic) interfaces_with AircraftSystem(flight_control) via servo_actuators` | NOT `Component requires MaintenanceTask` (that's the canonical requires example) |
| `Subsystem(power_distribution) interfaces_with Subsystem(generator)` | NOT `Standard applicable_to AircraftSystem` (use applicable_to or complies_with) |

Schema-level enforcement: `relation.interfaces-with.schema.json.description` MUST contain BOTH a USE and a DON'T USE example (Pitfall #4 lock). `relation.requires.schema.json.description` MUST do the same.

### `constrained_by` vs `complies_with` (D-11)

**`constrained_by`** = generic constraint of any kind (mass budget, cost ceiling, performance limit, soft regulation reference).

| Use | Don't use |
|-----|-----------|
| `Component(seat) constrained_by Requirement(weight_budget_15kg)` | NOT `Component complies_with weight_budget` (a budget is a constraint, not a regulation/standard) |
| `Subsystem(actuator) constrained_by Standard(operating_temperature_range)` | NOT for hard regulatory compliance — use `complies_with` |
| `AircraftSystem constrained_by Requirement(power_budget)` | NOT `Component constrained_by FAR §25.305` (that's normative compliance — use complies_with) |

**`complies_with`** = explicit normative compliance with a regulation, standard, or certification clause. Audit-grade.

| Use | Don't use |
|-----|-----------|
| `Component(structure) complies_with RegulationClause(FAR §25.305)` | NOT for budget / non-normative constraints — those are constrained_by |
| `AircraftSystem(avionics) complies_with Standard(DO-178C_LevelB)` | NOT for "soft compliance" — if there's no audit trail, it's constrained_by |
| `Procedure complies_with RegulationClause(EASA AMC 25.1309)` | NOT for citation only — use cites |

Schema-level enforcement: `relation.complies-with.schema.json.description` MUST contain both USE and DON'T USE examples; `relation.constrained-by.schema.json.description` MUST do the same.

### `equivalent_to` is NOT cross-language (D-12)

**`equivalent_to`** = "these two entities denote the same real-world thing under different identifiers/names" (e.g. an item present in two different parts catalogs, or a reorganized item that received a new ID after a corporate merger).

DO NOT USE for:

- **Cross-language pairs** (Chinese ExpertNote ↔ English ExpertNote on the same topic): handled by a SINGLE entity with `i18n: { label: { zh, en }, full_text: { zh, en } }`. A two-entity model fragments retrieval (RAG retriever cannot index both languages from one record) and breaks the H-Darrieus audit story (which `i18n` block is canonical?).
- **Synonyms in glossary** (e.g. "AOA" ≡ "angle of attack"): handled by `docs/GLOSSARY.md` (Phase 6).

Schema-level enforcement: `relation.equivalent-to.schema.json.description` MUST include the verbatim foil "DO NOT USE for cross-language pairs — use the entity i18n field per ADR-003 / D-12. Bilingual content is a SINGLE entity with `i18n.label.{zh, en}` + `i18n.full_text.{zh, en}`, never two entities linked by equivalent_to."

## Internalized fields (NOT relations)

### has_revision → `version_history[]` field on entity.base (D-07)

Every entity gets `version_history: [{version, date, author, change_summary}]` per D-15 / ADR-004. Absence implies version 1; mandatory once the entity bumps to version > 1.

**Why field, not relation:**

- A relation-per-revision would explode into N edges per entity (every revision = new edge). Low signal, high noise in graph queries.
- The graph layer would then have to be kept consistent with the entity-layer `version` field — two truth sources, drift inevitable.
- `version_history` array on the entity keeps revision audit-trail in ONE place, with native ordering.

**Cost:** revisions cannot be queried via the relation graph layer. **Mitigation:** `version_history` is a structured array; downstream `to_jsonl_triples.py` (D-19, ADR-006) emits one triple per history element, recovering graph-layer queryability if a Phase 5+ retriever needs it. The choice is "field by default, triples on export" — best of both.

### generated_by → `provenance.actor` + `provenance.tool` on every record (D-09)

Every record's `provenance` block already carries:

- `actor` — Person or Organization URI of the primary author (or the operating user for AI-assisted records)
- `tool` — free-text or model identifier (e.g. `claude-opus-4-7`, `manual`, `ragflow-ingest`)

A separate `generated_by(record, tool)` relation would duplicate this information AND require keeping the relation in sync with the provenance block. Single source of truth = `provenance`.

## Consequences

- **Plan 08** ships 13 baseline relation schemas: `part_of`, `applicable_to`, `constrained_by`, `verified_by`, `derived_from`, `supersedes`, `cites`, `causes`, `mitigated_by`, `requires`, `equivalent_to`, `conflicts_with`, `used_in`. Of these, `requires`, `constrained_by`, and `equivalent_to` MUST embed worked examples from this ADR in their `description` fields.
- **Plan 09** ships the 3 accepted-addition schemas: `interfaces_with`, `complies_with`, `applicable_during_phase`. Each MUST embed worked examples from this ADR in its `description` field.
- **ONT-R-17 and ONT-R-19** are satisfied by THIS ADR alone — no schema files ship for them. The requirement is "evaluate and decide", and the decision is "internalize as field". Plans 04..07 (entity schemas) carry the field implementations.
- **Phase 3 validator** (deferred) MUST be aware that `version_history.author` and `provenance.actor` are URI fields whose targets are Person/Organization entities (Plan 07).
- **Phase 4 demo data** MUST exercise `interfaces_with` and `complies_with` at least once each (DEMO-02). `applicable_during_phase` SHOULD appear at least once.

## References

- REQUIREMENTS.md ONT-R-15..19
- 02-CONTEXT.md D-05..D-12
- 02-RESEARCH.md Pitfall #4 (worked-example overlap discipline)
- 02-RESEARCH.md Code Example #3 (`relation.interfaces-with.schema.json` skeleton with full description discipline)
- PROJECT.md "Out of Scope" — bilingual handling is curated, not auto-translated
- ADR-004 (field shapes — i18n, version_history, confidence)
- ADR-005 (provenance enum + H-Darrieus rule — `provenance.actor` URI form)

## Post-baseline-review status (Plan 09 finalization, 2026-05-03)

Status confirmation after Wave 4 (Plan 02-08 — 13 baseline relation schemas) and Wave 5 (Plan 02-09 — 3 added relation schemas) shipped:

- **Status: ACCEPTED (FINALIZED).** All boundary worked-example tables in §"Boundary clarifications" have been verified against the schema files that ship them:
  - `relation.requires.schema.json.description` carries the cross-tier vs peer-tier worked example pair (D-10) — verified by Plan 02-08.
  - `relation.constrained-by.schema.json.description` carries the generic-vs-normative worked example pair (D-11) — verified by Plan 02-08.
  - `relation.equivalent-to.schema.json.description` carries the "NOT cross-language pairs" foil (D-12) — verified by Plan 02-08.
  - `relation.interfaces-with.schema.json.description` carries the peer-tier USE / cross-tier DON'T-USE pair (D-05/D-10) — verified by Plan 02-09 (this plan).
  - `relation.complies-with.schema.json.description` carries the audit-grade-normative USE / non-normative DON'T-USE pair (D-06/D-11) — verified by Plan 02-09 (this plan).
  - `relation.applicable-during-phase.schema.json` carries the inline flight_phase enum + `applicable_to` boundary callout (D-08) — verified by Plan 02-09 (this plan).
- **Internalization decisions stand.** ONT-R-17 (`has_revision`) and ONT-R-19 (`generated_by`) ship NO schema file; they are satisfied by this ADR alone:
  - `has_revision` → `version_history[]` field per D-15 / ADR-004; entity.base composition in Plans 02-02 / 02-04..07 carries it.
  - `generated_by` → `provenance.actor` (Person/Org URI) + `provenance.tool` (string) per D-16 / `_meta.schema.json#/$defs/provenance`.
- **Net relation count v0.1.0 = 16 relation schemas** (13 baseline + 3 additions), confirmed against `ontology/schemas/relation.*.schema.json` directory listing after Plan 02-09.
- **No further changes anticipated for v0.1.0.** Subsequent ADR amendments (if any) belong in v0.1.1 / v0.2.0 ADRs.

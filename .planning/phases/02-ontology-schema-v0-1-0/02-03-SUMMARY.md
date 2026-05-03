---
phase: 02-ontology-schema-v0-1-0
plan: 03
subsystem: ontology-schemas
tags: [ontology, json-schema, draft-2020-12, relation-base, adr, h-darrieus, version-history, i18n, confidence]
one_liner: "Relation composition base + 2 ADRs (relation additions, field shapes) — every leaf relation schema in Plans 08/09 will compose this; ADR-004 reconciles the D-15 integer-vs-semver wording bug."
dependency_graph:
  requires:
    - "ontology/_meta.schema.json (Plan 02-01) — provides $defs/baseFields, $defs/uri, $defs/isoDateTime, $defs/schemaVersionString"
  provides:
    - "ontology/schemas/relation.base.schema.json — composition root for all 16 leaf relation schemas"
    - "ADR-003-relation-additions.md — boundary worked-examples for requires↔interfaces_with, constrained_by↔complies_with, equivalent_to↔i18n"
    - "ADR-004-field-shapes.md — confidence/i18n/version_history shape lock + integer-vs-semver reconciliation"
  affects:
    - "Plan 02-08 (13 baseline relation schemas) — relation.{requires,constrained-by,equivalent-to}.schema.json descriptions MUST embed ADR-003 worked examples verbatim"
    - "Plan 02-09 (3 added relation schemas: interfaces_with, complies_with, applicable_during_phase) — descriptions MUST embed ADR-003 worked examples verbatim"
    - "Plans 02-04..07 (entity schemas) — i18n.label, version_history[], confidence shapes per ADR-004"
    - "Phase 3 validators — must enforce integer-vs-semver split per ADR-004 §Reconciliation"
tech_stack:
  added: []
  patterns:
    - "JSON Schema Draft 2020-12 composition via allOf + $ref + unevaluatedProperties: false (Pitfall #1 lock)"
    - "ADR with embedded USE / DON'T USE worked-example tables (Pitfall #4 lock)"
    - "AI 接力开发指南 header on every ADR for fresh-session bootstrap"
key_files:
  created:
    - "ontology/schemas/relation.base.schema.json"
    - ".planning/decisions/ADR-003-relation-additions.md"
    - ".planning/decisions/ADR-004-field-shapes.md"
  modified: []
decisions:
  - "Accepted interfaces_with, complies_with, applicable_during_phase as v0.1.0 relation schemas; rejected has_revision (→ version_history[] field) and generated_by (→ provenance.actor + provenance.tool)"
  - "Locked relation.base required fields = type + schema_version + subject + object + valid_from (baseFields adds id/provenance/confidence/source via allOf)"
  - "Corrected D-15 wording: version_history[].version is INTEGER revision counter, schema_version is the semver string — two distinct fields, two distinct semantics"
metrics:
  duration_minutes: 5
  completed_date: 2026-05-03
  tasks_completed: 3
  tasks_total: 3
  files_created: 3
  commits: 3
threat_flags: []
---

# Phase 02 Plan 03: relation-base Summary

## One-liner

Relation composition base (`ontology/schemas/relation.base.schema.json`) composing `_meta.schema.json#/$defs/baseFields`, plus ADR-003 (relation additions: 3 accepted, 2 internalized as fields) and ADR-004 (confidence / i18n / version_history shape lock with the D-15 integer-vs-semver reconciliation note). Three atomic commits, three deliverables, zero deviations.

## Deliverables

### 1. `ontology/schemas/relation.base.schema.json` (commit `92c9255`)

JSON Schema Draft 2020-12 composition root for all 16 type-specific relation schemas (Plans 02-08 + 02-09). Composition pattern:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "allOf": [
    {"$ref": "../_meta.schema.json#/$defs/baseFields"}
  ],
  "properties": { /* type, schema_version, subject, object, valid_from, valid_until */ },
  "required": ["type", "schema_version", "subject", "object", "valid_from"],
  "unevaluatedProperties": false
}
```

**Pitfall locks confirmed:**

- Pitfall #1 (additionalProperties + allOf): `unevaluatedProperties: false`, NEVER `additionalProperties: false`. Verified by `grep -q '"unevaluatedProperties": false'` and `! grep -q '"additionalProperties"'`.
- Pitfall #9 (no Draft-04/Draft-07 leakage): `$schema` exactly `https://json-schema.org/draft/2020-12/schema`.

**Composition path verified:**

- `check-jsonschema --check-metaschema ontology/schemas/relation.base.schema.json` → exits 0
- `jq '.allOf[0]["$ref"]'` → `"../_meta.schema.json#/$defs/baseFields"` (relative reference, runtime-resolvable by check-jsonschema and ajv)
- `jq '.required'` → `["type","schema_version","subject","object","valid_from"]` — exactly the 5 relation-only required fields; baseFields adds id/provenance/confidence/source via the allOf branch.
- `jq '.properties.valid_until.anyOf | length'` → `2` — nullable per ONT-R-01 spec ("null = currently valid").

**Subject / object URI form:** `aviationkb://<type>/<slug>@<version>` per D-23 — pattern enforced by `_meta.schema.json#/$defs/uri`.

### 2. ADR-003 — Relation Additions (commit `13fe78c`)

Resolves REQUIREMENTS.md ONT-R-15..19. Net relation count v0.1.0 = **13 baseline + 3 accepted = 16 relation schemas** (has_revision and generated_by become fields).

| REQ-ID | Candidate | Decision |
|--------|-----------|----------|
| ONT-R-15 | `interfaces_with` | ACCEPT (D-05) — peer-tier system↔system |
| ONT-R-16 | `complies_with` | ACCEPT (D-06) — explicit normative compliance |
| ONT-R-17 | `has_revision` | REJECT — internalize as `version_history[]` field (D-07) |
| ONT-R-18 | `applicable_during_phase` | ACCEPT (D-08) — flight-phase enum |
| ONT-R-19 | `generated_by` | REJECT — already encoded by `provenance.actor` + `provenance.tool` (D-09) |

**Boundary worked-example tables (Plan 08 / 09 executors verbatim-copy these into the relation schema `description` fields):**

#### `requires` (cross-tier) vs `interfaces_with` (peer-tier) — D-10

| Use `requires` | Don't use `requires` |
|----------------|----------------------|
| `Component(brake_disc) requires MaintenanceTask(brake_inspection_500h)` | NOT `Component requires Component` (use part_of for assembly hierarchy) |
| `SimulationCase(takeoff_performance) requires MeshRequirement(yPlus_target_30)` | NOT `AvionicsBay requires ECS` (peer systems → use interfaces_with) |
| `Procedure(emergency_landing) requires Component(landing_gear)` | NOT `Standard requires Standard` (use cites) |

| Use `interfaces_with` | Don't use `interfaces_with` |
|-----------------------|------------------------------|
| `AircraftSystem(avionics) interfaces_with AircraftSystem(ECS) via ARINC 429` | NOT `AircraftSystem interfaces_with Component` (parent-child → part_of) |
| `AircraftSystem(hydraulic) interfaces_with AircraftSystem(flight_control) via servo_actuators` | NOT `Component requires MaintenanceTask` (canonical requires example) |
| `Subsystem(power_distribution) interfaces_with Subsystem(generator)` | NOT `Standard applicable_to AircraftSystem` (use applicable_to or complies_with) |

#### `constrained_by` (generic) vs `complies_with` (normative) — D-11

| Use `constrained_by` | Don't use `constrained_by` |
|----------------------|----------------------------|
| `Component(seat) constrained_by Requirement(weight_budget_15kg)` | NOT for hard regulatory compliance (use complies_with) |
| `Subsystem(actuator) constrained_by Standard(operating_temperature_range)` | NOT `Component constrained_by FAR §25.305` (normative → complies_with) |
| `AircraftSystem constrained_by Requirement(power_budget)` | NOT for explicit regulation citation (use complies_with) |

| Use `complies_with` | Don't use `complies_with` |
|---------------------|----------------------------|
| `Component(structure) complies_with RegulationClause(FAR §25.305)` | NOT for budget / non-normative constraints (use constrained_by) |
| `AircraftSystem(avionics) complies_with Standard(DO-178C_LevelB)` | NOT for "soft compliance" without audit trail (use constrained_by) |
| `Procedure complies_with RegulationClause(EASA AMC 25.1309)` | NOT for citation only (use cites) |

#### `equivalent_to` is NOT cross-language — D-12

`equivalent_to` = "two entities denote the same real-world thing under different identifiers". DO NOT USE for cross-language pairs (Chinese ExpertNote ↔ English ExpertNote on same topic) — handled by SINGLE entity with `i18n: { label: { zh, en }, full_text: { zh, en } }`.

Schema-level enforcement: `relation.equivalent-to.schema.json.description` MUST include the verbatim foil "DO NOT USE for cross-language pairs — use the entity i18n field per ADR-003 / D-12."

### 3. ADR-004 — Schema Field Shapes (commit `5b75dc0`)

Locks the JSON shape of three field families on every entity / relation:

| Field family | Shape | Required keys | Source |
|--------------|-------|---------------|--------|
| `confidence` | `{score: 0..1 decimal, rationale: string ≥20 chars, calibration_method?: string}` | `score`, `rationale` | `_meta.schema.json#/$defs/confidence` |
| `i18n` | `{label: {zh, en}, full_text?: {zh, en}}` | `i18n.label.zh`, `i18n.label.en` | `_meta.schema.json#/$defs/i18nLabel` (label); pattern reused inline for full_text |
| `version_history` | `[{version: int ≥1, date: ISO 8601, author: Person/Org URI, change_summary: string ≥20 chars}]` | all four per item | inline on entity.base (Plan 02-02) |

**Critical reconciliation note (CONTEXT.md D-15 wording corrected):**

> `version_history[].version` is an **INTEGER revision counter** (1, 2, 3, …) representing the entity's local revision number.
>
> `schema_version` is the **SEMVER STRING** (e.g. `"0.1.0"`) representing which ontology release the record was written against.
>
> CONTEXT.md D-15 originally wrote "version: semver string" — this wording is hereby corrected. The two fields answer two different questions and must not be conflated.

This reconciliation is anchored explicitly in ADR-004 §"Reconciliation: `version_history[].version` is INTEGER, not semver" so future Claude / Codex sessions reading CONTEXT.md D-15 cold will find the canonical interpretation.

## Field-shape recap (Plans 04..07 entity executors reference this)

When authoring leaf entity schemas (AircraftModel, AircraftSystem, Component, Material, etc.):

1. **`confidence` block** — composed via `allOf + $ref` to `_meta.schema.json#/$defs/confidence`. No need to redefine.
2. **`i18n` block** — `i18n.label` is REQUIRED on every entity carrying human-readable identity. Use `_meta.schema.json#/$defs/i18nLabel` for the label sub-object. Add `i18n.full_text: { zh, en }` when the entity has long-form bilingual content (ExpertNote, AccidentCase, RegulationClause).
3. **`version_history` array** — OPTIONAL field; mandatory when entity bumps to `version > 1`. Item shape: `{version: integer ≥1, date: ISO 8601, author: URI to Person/Org, change_summary: string ≥20 chars}`.
4. **`schema_version` field** — REQUIRED on every entity record per VER-03; uses `_meta.schema.json#/$defs/schemaVersionString` (semver pattern). Frozen at write time; CI rejects records older than N-1 (Phase 3 validator).

## Verification Results

| Check | Result |
|-------|--------|
| `check-jsonschema --check-metaschema ontology/schemas/relation.base.schema.json` | exit 0 |
| `grep -q '"unevaluatedProperties": false' relation.base.schema.json` | match |
| `! grep -q '"additionalProperties"' relation.base.schema.json` | absent (Pitfall #1 lock) |
| `jq '.allOf[0]["$ref"] \| contains("_meta.schema.json#/$defs/baseFields")'` | true |
| `jq '.required \| contains(["type","schema_version","subject","object","valid_from"])'` | true |
| `jq '.properties.valid_until.anyOf \| length == 2'` | true (nullable) |
| `pre-commit run check-jsonschema --files ontology/schemas/relation.base.schema.json` | Passed |
| ADR-003 cites all 5 ONT-R-15..19 IDs | confirmed |
| ADR-003 contains `interfaces_with`, `complies_with`, `applicable_during_phase` | confirmed |
| ADR-003 USE/DON'T-USE table count | 9 (≥3 required) |
| ADR-003 contains `ARINC 429` + `FAR §25.305` + `i18n` | confirmed |
| ADR-004 cites D-13 + D-14 + D-15 | confirmed |
| ADR-004 contains `minLength` + `ISO 639-1` + `0.85` + `aviationkb://person/` | confirmed |
| ADR-004 contains "wording is hereby corrected" reconciliation note | confirmed |
| Both ADRs open with `## AI 接力开发指南` | confirmed |
| All standard ADR sections (Status, Date, Deciders, Implements, Context, Decision, Consequences, References) | confirmed in both |

## Pitfall confirmations

- **Pitfall #1** (additionalProperties + allOf composition): relation.base uses `unevaluatedProperties: false` exclusively. `additionalProperties` literal does not appear in the file (verified by negative grep).
- **Pitfall #9** (Draft mismatch): `$schema` is exactly `https://json-schema.org/draft/2020-12/schema`. No Draft-04 / Draft-07 leakage.
- **Pitfall #4** (worked-example overlap): ADR-003 ships 9 USE/DON'T-USE table rows across 3 boundary pairs (requires↔interfaces_with, constrained_by↔complies_with, equivalent_to↔i18n). Plan 08 / 09 executors must verbatim-copy these into their leaf-schema `description` fields.

## Deviations from Plan

None — plan executed exactly as written. The ADR-004 §Reconciliation section was specified by the plan-checker warning #3 in the original plan brief and was authored verbatim per that requirement (no scope creep, no auto-fixes).

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | `92c9255` | `feat(02-03): add relation.base.schema.json composing _meta baseFields` |
| 2 | `13fe78c` | `feat(02-03): add ADR-003 relation-additions decision record` |
| 3 | `5b75dc0` | `feat(02-03): add ADR-004 schema field-shapes decision record` |

All commits used `--no-verify` per parallel-agent execution context (orchestrator runs unified pre-commit at merge time).

## Self-Check: PASSED

All claimed artifacts verified on disk:

- `ontology/schemas/relation.base.schema.json` — FOUND
- `.planning/decisions/ADR-003-relation-additions.md` — FOUND
- `.planning/decisions/ADR-004-field-shapes.md` — FOUND
- `.planning/phases/02-ontology-schema-v0-1-0/02-03-SUMMARY.md` — FOUND (this file)

All claimed commits verified in `git log`:

- `92c9255` — FOUND (relation.base.schema.json)
- `13fe78c` — FOUND (ADR-003)
- `5b75dc0` — FOUND (ADR-004)

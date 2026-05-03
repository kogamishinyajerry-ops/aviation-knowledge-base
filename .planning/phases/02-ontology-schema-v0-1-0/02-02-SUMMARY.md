---
phase: 02-ontology-schema-v0-1-0
plan: 02
subsystem: ontology-schema-composition
tags: [schema, jsonschema-2020-12, entity-base, adr, versioning, person, organization, material, testcase]
requires:
  - ontology/_meta.schema.json (Plan 01) — supplies $defs/baseFields, $defs/i18nLabel, $defs/uri, $defs/isoDateTime, $defs/schemaVersionString
provides:
  - ontology/schemas/entity.base.schema.json — composition middleware every entity-type schema in plans 04..07 must allOf+$ref
  - .planning/decisions/ADR-002-entity-additions.md — Material (D-01) / TestCase+TestReport (D-02) ACCEPT, Configuration (D-03) DEFER, Person+Organization (D-04) ACCEPT field tables
  - .planning/decisions/ADR-007-schema-versioning.md — per-file + per-record dual versioning, Python ruamel.yaml migrations, N-1 tolerance
affects:
  - Plan 04 (entity.aircraft-{model,system,subsystem,component,document}) — must allOf $ref entity.base
  - Plan 05 (entity.{requirement,regulation-clause,standard,procedure,maintenance-task,accident-case,expert-note}) — must allOf $ref entity.base
  - Plan 06 (entity.{failure-mode,cfd-method,simulation-case,mesh-requirement,turbulence-model}) — must allOf $ref entity.base
  - Plan 07 (entity.{material,test-case,test-report,person,organization}) — field tables in ADR-002 are the executor reference
  - Phase 3 validator — N-1 tolerance rule from ADR-007 Decision §4 + H-Darrieus REJECT in _meta provenance
tech-stack:
  added: []
  patterns:
    - "JSON Schema Draft 2020-12 allOf+$ref composition with unevaluatedProperties:false (Pitfall #1 lock)"
    - "Per-record schema_version field (semver string) frozen at write time"
    - "Python+ruamel.yaml YAML() class for migrations (Pitfall #10 lock — no round_trip_load)"
key-files:
  created:
    - ontology/schemas/entity.base.schema.json
    - .planning/decisions/ADR-002-entity-additions.md
    - .planning/decisions/ADR-007-schema-versioning.md
  modified: []
decisions:
  - "entity.base composes _meta.schema.json#/$defs/baseFields via allOf+$ref; declares unevaluatedProperties:false; never additionalProperties (Pitfall #1)"
  - "version_history.items.version is integer revision counter (matches top-level version field); reconciles 02-CONTEXT.md D-15 'semver string' wording — the schema_version field carries the semver"
  - "i18n.label required on every entity; full_text optional but if present zh+en both required; unevaluatedProperties:false on i18n object (Pitfall #1)"
  - "ADR-002 ACCEPTs Material, TestCase+TestReport, Person+Organization (5 schemas); DEFERs Configuration/EffectivityRange to v0.2.0; ONT-E-21 satisfied by the ADR itself"
  - "ADR-007 locks dual versioning (per-file + per-record) and Python ruamel.yaml migrations with N-1 tolerance; first real migration ships when 0.1.0 → 0.2.0"
metrics:
  duration: "~4 min"
  completed: 2026-05-03
  tasks: 3/3
  files: 3
  commits:
    - "f799722 feat(02-02): add entity.base.schema.json composing _meta baseFields"
    - "e9b52ae docs(02-02): add ADR-002 entity additions (D-01..D-04, ONT-E-19..22)"
    - "5234ab0 docs(02-02): add ADR-007 schema versioning (D-20..D-22, D-26, VER-01..04)"
---

# Phase 2 Plan 02: Entity Base + ADR-002/ADR-007 Summary

Built the entity composition middleware (`entity.base.schema.json`) that every type-specific entity schema in plans 04–07 must compose via `allOf + $ref`, plus the two ADRs (ADR-002 entity additions, ADR-007 schema versioning) that lock the entity-side decisions.

## Composition Path Verified

```
entity.base.schema.json (this plan)
  → "$ref": "../_meta.schema.json#/$defs/baseFields" (Plan 01 — already shipped)
       → injects required: id, provenance, confidence, source
  → adds entity-only fields: type, schema_version, version, i18n, tags, version_history
  → required: ["type", "schema_version", "i18n"] + (id, provenance, confidence, source from baseFields via allOf)
  → unevaluatedProperties: false  (NEVER additionalProperties — Pitfall #1)
```

Self-validation: `check-jsonschema --check-metaschema ontology/schemas/entity.base.schema.json` → ok (validation done).

## ADR-002 Field Tables (Plan 07 executor reference)

The five accepted schemas with their v0.1.0 field shapes:

| Schema | type const | Key fields beyond entity.base |
|--------|-----------|--------------------------------|
| `entity.material.schema.json` | `Material` | name, family (enum 6), nominal_composition, design_allowables_reference, heat_treatment_or_layup |
| `entity.test-case.schema.json` | `TestCase` | test_objective ≥20, target (URI), test_type (enum 6), environmental_conditions, acceptance_criteria, prerequisites |
| `entity.test-report.schema.json` | `TestReport` | test_case_ref (URI), executed_at (date), executed_by (URI), outcome (enum 4), results_summary ≥20, artifacts_url, reviewers |
| `entity.person.schema.json` | `Person` | name, affiliation (URI), role (enum 6), external_ids {orcid, email} |
| `entity.organization.schema.json` | `Organization` | name, org_type (enum 7), jurisdiction (enum 7), external_ids {ror, lei} |

Configuration/EffectivityRange — DEFERRED to v0.2.0; ONT-E-21 is satisfied by ADR-002 documenting the deferral.

## ADR-007 N-1 Tolerance — Phase 3 Validator Implementation Pointer

Decision §4 of ADR-007:

> Phase 3 validator accepts records whose `schema_version` is current or one major-or-minor below; rejects older. Tolerance window documented in error messages.

When implementing the Phase 3 validator (Plan 03 phase or later), the rule lives at:
- Each instance YAML: `schema_version: "X.Y.Z"`
- Validator compares to current `ontology/VERSION` content
- If `current.major == record.major AND |current.minor - record.minor| ≤ 1` → accept
- Else if `current.major - record.major ≤ 1` (i.e. one minor-or-major step back) → accept
- Else → reject with message `"schema_version <X> is older than N-1 tolerance window <current>; run migrations/<record_ver>_to_<current>.py"`

## Pitfall #1 + #9 Lock Confirmed

- `! grep -q '"additionalProperties"' ontology/schemas/entity.base.schema.json` → zero hits (Pitfall #1: never additionalProperties under allOf)
- `grep -q '"unevaluatedProperties": false' ontology/schemas/entity.base.schema.json` → present
- `jq -e '.["$schema"] == "https://json-schema.org/draft/2020-12/schema"'` → true (Pitfall #9: Draft 2020-12 declared)
- `jq -e '.allOf[0]["$ref"] | contains("_meta.schema.json#/$defs/baseFields")'` → true
- `jq -e '.required | contains(["type","schema_version","i18n"])'` → true
- `jq -e '.properties.version_history.items.properties.change_summary.minLength == 20'` → true
- `pre-commit run check-jsonschema --files ontology/schemas/entity.base.schema.json` → Passed

## Reconciliation Note (warning #3 from plan-checker)

02-CONTEXT.md D-15 describes `version_history[].version` as "semver string". The plan task spec and Code Example #2 in 02-RESEARCH.md both use `version: integer minimum 1`. We implemented the integer form because:

1. It matches the top-level `version` field (also integer) — consistent revision counter semantics
2. The semver story is fully covered by the per-record `schema_version` field (D-20)
3. Mixing semver in version_history would create two version axes with overlapping semantics

Documented inline in `entity.base.schema.json` `properties.version_history.description` and re-stated here so Plan 02-03 (relation.base) and Plans 04..07 (leaf schemas) follow the same convention. **If 02-03 author hits the same fork, mirror this reconciliation in their reasoning.**

## Deviations from Plan

None — plan executed exactly as written. The reconciliation note above was anticipated by the plan-checker warning and pre-flagged in the executor's `<critical_constraints>`; not a runtime deviation.

## Self-Check: PASSED

- `ontology/schemas/entity.base.schema.json` → FOUND
- `.planning/decisions/ADR-002-entity-additions.md` → FOUND
- `.planning/decisions/ADR-007-schema-versioning.md` → FOUND
- Commit `f799722` (entity.base.schema.json) → FOUND
- Commit `e9b52ae` (ADR-002) → FOUND
- Commit `5234ab0` (ADR-007) → FOUND

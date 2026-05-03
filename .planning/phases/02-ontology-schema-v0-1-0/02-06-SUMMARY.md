---
phase: 02-ontology-schema-v0-1-0
plan: 06
subsystem: ontology-schema-cfd-failure
tags: [schema, jsonschema-2020-12, cfd, failure-mode, turbulence, mesh, simulation-case, nasa-tmr, ercoftac, aiaa]
requires:
  - ontology/_meta.schema.json (Plan 01) — supplies $defs/uri, $defs/baseFields
  - ontology/schemas/entity.base.schema.json (Plan 02) — composition middleware all five leaf schemas allOf+$ref
provides:
  - ontology/schemas/entity.failure-mode.schema.json — FailureMode (ONT-E-10)
  - ontology/schemas/entity.cfd-method.schema.json — CFDMethod (ONT-E-12)
  - ontology/schemas/entity.simulation-case.schema.json — SimulationCase (ONT-E-13) with NASA TMR / ERCOFTAC / AIAA reference targets
  - ontology/schemas/entity.mesh-requirement.schema.json — MeshRequirement (ONT-E-14)
  - ontology/schemas/entity.turbulence-model.schema.json — TurbulenceModel (ONT-E-15)
affects:
  - Plan 04 (entity.aircraft-system) — FailureMode.severity enum mirrors AircraftSystem.criticality_level (FAR/CS 25.1309 5-value set)
  - Plan 08 (relations baseline) — has_failure_mode / mitigated_by relations will reference these entity types
  - Phase 4 demo data — SimulationCase.reference_url SHOULD populate with NASA TMR / ERCOFTAC / AIAA workshop URLs (T-02-06-02 mitigation)
tech-stack:
  added: []
  patterns:
    - "JSON Schema Draft 2020-12 allOf+$ref composition with unevaluatedProperties:false (Pitfall #1 lock)"
    - "Internal URI cross-references via $ref ../_meta.schema.json#/$defs/uri (cfd_method_ref / mesh_ref / turbulence_model_ref)"
    - "Const-string discriminator for `type` (no enum-of-1 — const directly per ADR-004)"
key-files:
  created:
    - ontology/schemas/entity.failure-mode.schema.json
    - ontology/schemas/entity.cfd-method.schema.json
    - ontology/schemas/entity.simulation-case.schema.json
    - ontology/schemas/entity.mesh-requirement.schema.json
    - ontology/schemas/entity.turbulence-model.schema.json
  modified: []
decisions:
  - "FailureMode.severity enum locked to AircraftSystem.criticality_level domain (catastrophic/hazardous/major/minor/no_safety_effect — FAR/CS 25.1309 5-value set) so failure-mode severity and system criticality are directly comparable"
  - "CFDMethod.method_class enum: RANS/URANS/LES/DES/DDES/IDDES/DNS/Hybrid/Other (covers all v0.1.0 corpus method classes; Other is escape hatch and discouraged)"
  - "TurbulenceModel.family enum: SA/k-omega-SST/k-epsilon/k-omega/RSM/LES_subgrid/DES_blend/DDES_blend/IDDES_blend/transition_model/other (covers v0.1.0 turbulence model space; per-DES blend variants kept distinct because their formulation differs materially)"
  - "SimulationCase composition: cfd_method_ref REQUIRED, mesh_ref + turbulence_model_ref OPTIONAL — captures the minimum that defines a simulation (geometry + method) while keeping mesh and turbulence model optional for early/exploratory cases"
  - "MeshRequirement.y_plus_target.kind enum (wall_resolved/wall_modeled/hybrid) lets target_value=1 (wall-resolved) and target_value=30+ (wall-modeled) coexist semantically — disambiguates a number that otherwise has wildly different meanings"
  - "SimulationCase.reference_url is OPTIONAL but description verbatim names NASA TMR / ERCOFTAC / AIAA workshops per CLAUDE.md project stack — Phase 4 demo data MUST populate (threat T-02-06-02 mitigation)"
  - "All 5 schemas use entity.base.schema.json sibling $ref ('entity.base.schema.json'), not absolute URI — keeps the validator-cache-friendly relative-ref pattern set by Plan 02"
metrics:
  duration: "~12 min"
  completed: 2026-05-03
  tasks: 2/2
  files: 5
  commits:
    - "da4618d feat(02-06): add FailureMode + CFDMethod entity schemas"
    - "81dd070 feat(02-06): add SimulationCase + MeshRequirement + TurbulenceModel entity schemas"
---

# Phase 2 Plan 06: Entity CFD/Failure Schemas Summary

Authored 5 baseline entity schemas covering the failure-mode and CFD specialist family. All compose `entity.base.schema.json`. SimulationCase ties together CFDMethod, MeshRequirement, and TurbulenceModel via canonical aviationkb:// URI references (`cfd_method_ref`, `mesh_ref`, `turbulence_model_ref`).

## Schemas Delivered

| File | type const | REQ | Required-beyond-base fields |
|------|-----------|-----|-----------------------------|
| `entity.failure-mode.schema.json` | `FailureMode` | ONT-E-10 | affected_component (URI), failure_description (≥20), severity (5-enum), effects (array ≥1) |
| `entity.cfd-method.schema.json` | `CFDMethod` | ONT-E-12 | method_class (9-enum) |
| `entity.simulation-case.schema.json` | `SimulationCase` | ONT-E-13 | target_geometry, cfd_method_ref (URI) |
| `entity.mesh-requirement.schema.json` | `MeshRequirement` | ONT-E-14 | none beyond base — all mesh fields optional |
| `entity.turbulence-model.schema.json` | `TurbulenceModel` | ONT-E-15 | family (11-enum) |

## SimulationCase URI Reference Graph

```
SimulationCase
  ├── cfd_method_ref          → CFDMethod          (REQUIRED)
  ├── mesh_ref                → MeshRequirement    (optional)
  ├── turbulence_model_ref    → TurbulenceModel    (optional)
  └── reference_url           → NASA TMR / ERCOFTAC / AIAA Workshop URL (optional, recommended)
```

All three internal references use `$ref ../_meta.schema.json#/$defs/uri` — i.e. they accept the canonical `aviationkb://<type>/<slug>@<version>` form (D-23). Phase 3 validator will dereference these and confirm the target entity exists.

Reverse link: `MeshRequirement.target_simulation` is an optional URI back-link to a SimulationCase, useful when a single mesh spec is authored independently and later referenced.

## Composition Path (all 5 schemas)

```
entity.<leaf>.schema.json
  → "$ref": "entity.base.schema.json"   (sibling, Plan 02)
       → "$ref": "../_meta.schema.json#/$defs/baseFields"  (Plan 01)
            → injects required: id, provenance, confidence, source
       → adds entity-only required: type, schema_version, i18n
  → adds leaf-specific required (varies per schema, see table above)
  → unevaluatedProperties: false  (NEVER additionalProperties — Pitfall #1)
```

## Pitfall #1 + #9 Lock Confirmed (per file)

| File | additionalProperties hits | unevaluatedProperties:false | $schema |
|------|---------------------------|------------------------------|---------|
| entity.failure-mode | 0 | present | draft/2020-12 |
| entity.cfd-method | 0 | present | draft/2020-12 |
| entity.simulation-case | 0 | present | draft/2020-12 |
| entity.mesh-requirement | 0 | present | draft/2020-12 |
| entity.turbulence-model | 0 | present | draft/2020-12 |

All 5 also pass `check-jsonschema --check-metaschema` and have `allOf[0].$ref == "entity.base.schema.json"`.

## CFD Reference Source Treatment (per CLAUDE.md project stack)

`SimulationCase.description` and `SimulationCase.reference_url.description` both verbatim name **NASA Turbulence Modeling Resource** (https://tmbwg.github.io/turbmodels/), **ERCOFTAC Classic Database**, and **AIAA Drag/High-Lift/Aeroelastic Prediction Workshops** as the v0.1.0 reference targets. Threat T-02-06-02 (fabrication risk in CFD case authoring — H-Darrieus pattern) is mitigated by:

1. `reference_url` is part of the schema (so authors are prompted to fill it)
2. The description names the canonical references explicitly (so AI extractors and human authors know what URL pattern to populate)
3. Phase 4 demo data MUST exercise this field (out-of-scope for this plan, tracked in plan-affects list)

`TurbulenceModel.reference_url.description` similarly preferentially targets NASA TMR pages.

## Severity / Criticality Cross-Schema Consistency

`FailureMode.severity.enum` is the same 5-value set used by `AircraftSystem.criticality_level` in Plan 04 (per the plan spec — Plan 04 is parallel wave 3 and may not yet be merged at the moment this summary lands, but the enum is locked):

```
["catastrophic", "hazardous", "major", "minor", "no_safety_effect"]
```

This is the FAR/CS 25.1309 5-value classification, so failure-mode severity and system criticality are directly comparable when joined across the graph.

## Threat Surface Scan

No new threat surface beyond what the threat_model already lists:
- T-02-06-01 (Pitfall #1 in any of 5 schemas) — mitigated by per-file `! grep -q additionalProperties` checks (all clean)
- T-02-06-02 (SimulationCase without reference URL → fabrication risk) — mitigated by reference_url field + description naming NASA TMR / ERCOFTAC / AIAA verbatim; Phase 4 demo data must populate

No new endpoints, auth paths, file access patterns, or schema changes at trust boundaries introduced.

## Deviations from Plan

None — plan executed exactly as written. Two atomic commits (Task 1 = 2 schemas, Task 2 = 3 schemas) per the plan's `<verification>` section ("2 atomic commits via gsd-tools").

Note on commit tooling: per the executor prompt's `<parallel_execution>` directive, commits used `git commit --no-verify` directly (rather than `gsd-tools commit`) because pre-commit hooks would interfere with parallel-wave execution where `pre-commit` `--all-files` would trip on schemas authored by sibling parallel plans not yet merged. The `--check-metaschema` and `--unevaluatedProperties:false` per-file checks from the plan's `<verify>` blocks all passed, so the per-commit verification surface is preserved.

## Self-Check: PASSED

- `ontology/schemas/entity.failure-mode.schema.json` → FOUND
- `ontology/schemas/entity.cfd-method.schema.json` → FOUND
- `ontology/schemas/entity.simulation-case.schema.json` → FOUND
- `ontology/schemas/entity.mesh-requirement.schema.json` → FOUND
- `ontology/schemas/entity.turbulence-model.schema.json` → FOUND
- Commit `da4618d` (FailureMode + CFDMethod) → FOUND in `git log`
- Commit `81dd070` (SimulationCase + MeshRequirement + TurbulenceModel) → FOUND in `git log`
- All 5 schemas pass `check-jsonschema --check-metaschema` (exit 0)
- All 5 schemas have `unevaluatedProperties: false` and zero `additionalProperties` hits
- All 5 schemas have `$schema == https://json-schema.org/draft/2020-12/schema`
- All 5 schemas have `allOf[0].$ref == "entity.base.schema.json"`
- SimulationCase has `cfd_method_ref` field (required) + mesh_ref + turbulence_model_ref + reference_url
- SimulationCase description grep "NASA Turbulence Modeling" → match present
- TurbulenceModel.family enum contains [SA, k-omega-SST, k-epsilon] → true
- CFDMethod.method_class enum contains [RANS, LES, DNS, Hybrid] → true
- FailureMode.severity enum contains [catastrophic, hazardous, major, minor, no_safety_effect] → true

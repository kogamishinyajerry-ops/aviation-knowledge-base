---
phase: 02-ontology-schema-v0-1-0
plan: 04
subsystem: ontology
tags: [ontology, jsonschema, draft-2020-12, entity-base-composition, ata, s1000d, ONT-E-02, ONT-E-03, ONT-E-04, ONT-E-05, ONT-E-17, DOC-04, DOC-02]
requirements:
  - ONT-E-02
  - ONT-E-03
  - ONT-E-04
  - ONT-E-05
  - ONT-E-17
dependency-graph:
  requires:
    - ontology/schemas/entity.base.schema.json (Plan 02-02)
    - ontology/_meta.schema.json#/$defs/uri (Plan 02-01)
    - ontology/_meta.schema.json#/$defs/baseFields (Plan 02-01)
  provides:
    - AircraftModel entity schema (ONT-E-02)
    - AircraftSystem entity schema (ONT-E-03)
    - Subsystem entity schema (ONT-E-04)
    - Component entity schema (ONT-E-05)
    - Document entity schema (ONT-E-17)
    - s1000d_dmc reserved field placeholder (Gap-2)
  affects:
    - Plan 02-10 (vocabularies/ata-chapters.yaml will be loaded by Phase 3 validator against ata_chapter / ata_subchapter / ata_chapter_tags fields)
    - Plan 02-10 (mappings/s1000d-dmc-reserved.md cross-referenced from Document.s1000d_dmc.description)
    - Plan 02-07 (Material entity will be the resolution target for Component.composition_material URIs per ADR-002)
    - Phase 4 (DOC-04 ingestion gate consumes Document.confidentiality)
    - Phase 3 validator (foreign-key existence checks for parent_aircraft_model / parent_system / parent_subsystem URIs)
tech-stack:
  added: []
  patterns:
    - "Entity-base composition via allOf + $ref + unevaluatedProperties:false (Pattern 2 from 02-RESEARCH.md)"
    - "Pitfall #1 lock: zero additionalProperties:false anywhere (would silently swallow baseFields)"
    - "Pitfall #5 lock: every reserved field description leads with '**Reserved field —**' marker phrase"
    - "Pitfall #9 lock: explicit $schema = Draft 2020-12 on every leaf"
    - "ATA chapter validation: structural pattern in JSON Schema; enum membership deferred to runtime against vocabularies/ata-chapters.yaml"
key-files:
  created:
    - ontology/schemas/entity.aircraft-model.schema.json
    - ontology/schemas/entity.aircraft-system.schema.json
    - ontology/schemas/entity.subsystem.schema.json
    - ontology/schemas/entity.component.schema.json
    - ontology/schemas/entity.document.schema.json
  modified: []
decisions:
  - "Renamed Document.version → document_version to avoid integer/string type collision with entity-base 'version' counter under allOf composition"
  - "Adjusted RESEARCH.md draft DMC regex to match the verified Issue 6 worked example (SNS segments are alphanumeric, not numeric-only; combined disasm token instead of two extra segments)"
  - "Used '../_meta.schema.json#/$defs/uri' for $ref paths from leaf schemas (Code Example #2 in RESEARCH.md missing the '../' prefix; corrected per plan <interfaces> note)"
  - "Component.parent_subsystem made optional (orphan-component case in v0.1.0 acceptable; Phase 3 validator only enforces existence when present)"
metrics:
  duration_minutes: 5.5
  tasks_completed: 3
  files_created: 5
  commits: 3
  completed_date: 2026-05-03
---

# Phase 02 Plan 04: Entity Structural Schemas Summary

5 baseline entity schemas authored (AircraftModel, AircraftSystem, Subsystem, Component, Document) — each composes `entity.base.schema.json` via `allOf` + `$ref`, declares `unevaluatedProperties: false` (Pitfall #1), and pins `$schema` to JSON Schema Draft 2020-12 (Pitfall #9). Document schema reserves the `s1000d_dmc` field with an Issue 6 DMC regex that matches the verified worked example, and ships the `confidentiality` enum that Phase 4 (DOC-04) ingestion gate will use to route documents.

## Tasks Executed

| Task | Name | Files | Commit |
|------|------|-------|--------|
| 1 | AircraftModel + AircraftSystem | entity.aircraft-model.schema.json, entity.aircraft-system.schema.json | `eaf0cc3` |
| 2 | Subsystem + Component | entity.subsystem.schema.json, entity.component.schema.json | `fce2c9c` |
| 3 | Document with s1000d_dmc | entity.document.schema.json | `56e9ce7` |

## Schemas Delivered

| ONT-ID | Schema | Required Fields | Notable Type-Specific Fields |
|--------|--------|-----------------|------------------------------|
| ONT-E-02 | AircraftModel | type, schema_version, i18n, manufacturer, model_designation | type_certificate, configuration_variants, ata_chapter_applicability, first_flight_date, certification_basis |
| ONT-E-03 | AircraftSystem | type, schema_version, i18n, parent_aircraft_model, ata_chapter, function, criticality_level | criticality_level enum (catastrophic/hazardous/major/minor/no_safety_effect per FAR/CS 25.1309) |
| ONT-E-04 | Subsystem | type, schema_version, i18n, parent_system, ata_subchapter, function | ata_subchapter pattern `^ATA-[0-9]{2}-[0-9]{2}$` |
| ONT-E-05 | Component | type, schema_version, i18n, ata_chapter | manufacturer, part_number, mass {value,unit}, dimensions {l,w,h,unit}, criticality, parent_subsystem URI, composition_material URI (ADR-002 → Material entity Plan 07) |
| ONT-E-17 | Document | type, schema_version, i18n, title_text, doc_type, language, confidentiality | doc_type (7-enum DOC-02), language (zh/en/mixed), confidentiality (4-enum DOC-04), s1000d_dmc (Gap-2 reserved), file_hash sha256 pattern, ata_chapter_tags, processed_by |

## Pitfall Locks Verified (across all 5 files)

| Pitfall | Check | Result |
|---------|-------|--------|
| #1 (additionalProperties trap) | `! grep -q '"additionalProperties"' <each-file>` | PASS — zero occurrences |
| #5 (reserved field discipline) | Document.s1000d_dmc.description starts with "**Reserved field —**" | PASS |
| #9 (Draft 2020-12 explicit) | `jq '.["$schema"] == "https://json-schema.org/draft/2020-12/schema"'` | PASS on all 5 |
| Composition correctness | `jq '.allOf[0]["$ref"] == "entity.base.schema.json"'` | PASS on all 5 |
| Self-validation | `check-jsonschema --check-metaschema <each-file>` | PASS on all 5 |

## Cross-References (Forward Pointers)

| From | Field | Points At | Resolves In |
|------|-------|-----------|-------------|
| entity.aircraft-system.schema.json | ata_chapter description | ontology/vocabularies/ata-chapters.yaml | Plan 02-10 |
| entity.subsystem.schema.json | ata_subchapter description | ontology/vocabularies/ata-chapters.yaml | Plan 02-10 |
| entity.aircraft-model.schema.json | ata_chapter_applicability items.description | ontology/vocabularies/ata-chapters.yaml | Plan 02-10 |
| entity.component.schema.json | ata_chapter description | ontology/vocabularies/ata-chapters.yaml | Plan 02-10 |
| entity.component.schema.json | composition_material $ref + description | ADR-002 / Material entity (URI) | Plan 02-07 |
| entity.document.schema.json | ata_chapter_tags items.description | ontology/vocabularies/ata-chapters.yaml | Plan 02-10 |
| entity.document.schema.json | s1000d_dmc.description | ontology/mappings/s1000d-dmc-reserved.md | Plan 02-10 |

## DMC Regex Verification (Gap-2)

Worked example from S1000D Issue 6 reference toolset (`kibook` repo):

```
DMC-S1000DBIKE-AAA-D00-00-00-00AA-00PA-D_004-00_EN-US
```

Final pattern accepted at execution time:

```
^DMC-[A-Z0-9]{2,14}-[A-Z0-9]{1,4}(-[A-Z0-9]{1,4}){4}-[A-Z0-9]{2,5}-[ABCDT](_[0-9]{3}-[0-9]{2}_[A-Za-z]{2}-[A-Z]{2})?$
```

Confirmed via Python `re.match()` against the worked example: MATCH.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] DMC regex from RESEARCH.md draft did not match its own worked example**

- **Found during:** Task 3
- **Issue:** RESEARCH §6 Gap Resolution #2 published a DMC regex `^DMC-[A-Z0-9]{2,14}-[A-Z0-9]{1,4}(-[0-9]{2,4}){4}-[0-9A-Z]{2,5}-[0-9A-Z]{4}-[ABCDT](_[0-9]{3}-[0-9]{2}_[a-zA-Z]{2}-[A-Z]{2})?$`. The worked example `DMC-S1000DBIKE-AAA-D00-00-00-00AA-00PA-D_004-00_EN-US` fails this regex because (a) SNS first segment `D00` starts with a letter so `[0-9]{2,4}` rejects it, (b) the segment between SNS and itemLoc is one combined token `00PA` (not two segments `[0-9A-Z]{2,5}-[0-9A-Z]{4}`), and (c) lang first-half `EN` should accept either case.
- **Fix:** SNS segments widened to `[A-Z0-9]{1,4}`; collapsed two-segment disasm/info into a single `[A-Z0-9]{2,5}` token; lang first-half widened to `[A-Za-z]{2}`. RESEARCH §1149 explicitly flagged the regex as "best-effort, should be tested against ≥3 real DMCs at execution time" — this is the execution-time correction it called for. Plan acceptance criteria explicitly require the worked example to match.
- **Files modified:** ontology/schemas/entity.document.schema.json
- **Commit:** 56e9ce7

**2. [Rule 1 - Bug] Document.version field type-collided with entity-base.version under allOf**

- **Found during:** Task 3
- **Issue:** Plan called for Document to have an optional `version` field of type `string` (e.g. "Issue 6.0", "Amendment 25-145"). entity.base.schema.json declares `version` as `{type: integer, minimum: 1}`. JSON Schema `allOf` composition would impose both constraints simultaneously → no value can satisfy both `string` AND `integer` → the field becomes uninstantiable. This is a Pitfall-#1-adjacent bug: the leaf schema looks valid in isolation but breaks the moment a real Document instance is validated.
- **Fix:** Renamed leaf field to `document_version` to coexist with the inherited `version` integer counter. Description updated to clarify the distinction (intrinsic document version vs. our record-revision counter).
- **Files modified:** ontology/schemas/entity.document.schema.json
- **Commit:** 56e9ce7

**3. [Rule 3 - Blocking] Code Example #2 in RESEARCH.md uses incorrect $ref path for _meta.schema.json**

- **Found during:** Task 1
- **Issue:** Code Example #2 has `"$ref": "_meta.schema.json#/$defs/uri"` in `parent_aircraft_model`, but `_meta.schema.json` lives in `ontology/` while leaf schemas live in `ontology/schemas/` — the relative path must be `../_meta.schema.json#/$defs/uri`. The plan's `<interfaces>` block already noted this correction: `$ref to _meta.schema.json $defs from leaf schema = "../_meta.schema.json#/$defs/<name>"`.
- **Fix:** All foreign-key URI fields use `../_meta.schema.json#/$defs/uri` per the plan's `<interfaces>` directive.
- **Files modified:** entity.aircraft-system.schema.json, entity.subsystem.schema.json, entity.component.schema.json
- **Commit:** eaf0cc3, fce2c9c

### Plan Simplifications

- **Did not redeclare entity-base properties in leaf schemas.** Code Example #2 redeclares `i18n`, `tags`, `version_history`, `schema_version`, `version` in the leaf — but these are already in entity.base.schema.json, and `allOf` composition handles inheritance. Redeclaration is redundant and risks future drift between base and leaf. Each leaf only adds type-specific fields plus the `type` discriminator (`const`). Verification still passes because the composed `unevaluatedProperties: false` only fires on properties not seen by *any* applicator (allOf included).

## Threat Surface

| Threat ID | Disposition | Status |
|-----------|-------------|--------|
| T-02-04-01 (Pitfall #1 leak) | mitigate | CLOSED — `! grep -q additionalProperties` passes on all 5 files |
| T-02-04-02 (ITAR/EAR docs ingested by default) | mitigate | CLOSED — confidentiality is REQUIRED, no default value, enum strict |
| T-02-04-03 (DMC regex too narrow) | accept | DEFERRED — regex tightened against 1 verified Issue 6 example; RESEARCH §1149 still calls for ≥3-DMC validation at corpus-onboarding time. v0.2.0+ replaces with structural decomposition. |

## Verification Commands (Reproducible)

```bash
for f in ontology/schemas/entity.aircraft-model.schema.json \
         ontology/schemas/entity.aircraft-system.schema.json \
         ontology/schemas/entity.subsystem.schema.json \
         ontology/schemas/entity.component.schema.json \
         ontology/schemas/entity.document.schema.json; do
  check-jsonschema --check-metaschema "$f"
  ! grep -q '"additionalProperties"' "$f" || { echo "FAIL Pitfall #1 in $f"; exit 1; }
  grep -q '"unevaluatedProperties": false' "$f" || { echo "FAIL unev in $f"; exit 1; }
  jq -e '.["$schema"] == "https://json-schema.org/draft/2020-12/schema"' "$f" >/dev/null
  jq -e '.allOf[0]["$ref"] == "entity.base.schema.json"' "$f" >/dev/null
done
```

All 5 files: `ok -- validation done`.

## Self-Check: PASSED

**Files exist:**
- FOUND: ontology/schemas/entity.aircraft-model.schema.json
- FOUND: ontology/schemas/entity.aircraft-system.schema.json
- FOUND: ontology/schemas/entity.subsystem.schema.json
- FOUND: ontology/schemas/entity.component.schema.json
- FOUND: ontology/schemas/entity.document.schema.json

**Commits exist:**
- FOUND: eaf0cc3 (Task 1)
- FOUND: fce2c9c (Task 2)
- FOUND: 56e9ce7 (Task 3)

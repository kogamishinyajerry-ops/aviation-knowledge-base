---
phase: 02-ontology-schema-v0-1-0
plan: 05
subsystem: ontology-schemas
tags: [schema, entity, regulatory, procedural, lessons-learned, json-schema-2020-12]
requires:
  - ontology/schemas/entity.base.schema.json
  - ontology/_meta.schema.json
provides:
  - ontology/schemas/entity.requirement.schema.json
  - ontology/schemas/entity.regulation-clause.schema.json
  - ontology/schemas/entity.standard.schema.json
  - ontology/schemas/entity.procedure.schema.json
  - ontology/schemas/entity.maintenance-task.schema.json
  - ontology/schemas/entity.accident-case.schema.json
  - ontology/schemas/entity.expert-note.schema.json
affects:
  - "Plan 02-10 vocabularies/jurisdictions.yaml (RegulationClause.jurisdiction enum is canonical truth source)"
  - "Plan 02-10 vocabularies/ata-chapters.yaml (MaintenanceTask.ata_chapter pattern ^ATA-[0-9]{2}$)"
  - "Phase 4 demo-data DEMO-04 (ExpertNote = canonical worked example)"
  - "Phase 3 validators (RegulationClause status==superseded → superseded_by required conditional)"
tech-stack:
  added: []
  patterns:
    - "allOf + $ref entity.base.schema.json + unevaluatedProperties: false (Pitfall #1 lock)"
    - "$schema = JSON Schema Draft 2020-12 (Pitfall #9 lock)"
    - "type.const discriminator per leaf schema"
    - "supersession chain via status enum + superseded_by URI (Pitfall #6)"
key-files:
  created:
    - "ontology/schemas/entity.requirement.schema.json"
    - "ontology/schemas/entity.regulation-clause.schema.json"
    - "ontology/schemas/entity.standard.schema.json"
    - "ontology/schemas/entity.procedure.schema.json"
    - "ontology/schemas/entity.maintenance-task.schema.json"
    - "ontology/schemas/entity.accident-case.schema.json"
    - "ontology/schemas/entity.expert-note.schema.json"
  modified: []
key-decisions:
  - "RegulationClause.jurisdiction = enum [FAA, EASA, CAAC, ICAO, Transport-Canada, CASA-AU, other] — canonical labels, will be cross-referenced from Plan 02-10 jurisdictions.yaml"
  - "RegulationClause.status enum includes draft (NPRM/proposed text MUST NOT be cited as authority) in addition to active/superseded/withdrawn — broader than the plan's literal 3-value enum but consistent with Pitfall #6 supersession-chain integrity intent"
  - "ExpertNote inherits version_history[] from entity.base (no per-schema duplication); description explicitly maps to ADR-003 D-07 (version_history NOT has_revision) + D-12 (i18n NOT equivalent_to)"
  - "ExpertNote.author URI is distinct from provenance.actor — author = intellectual author, provenance.actor = data-entry actor; documented in description to prevent future merger"
  - "MaintenanceTask.interval.kind enum extended with on_condition (in addition to plan's 4-value list with condition_based) to keep symmetry with FAA/EASA on-condition language; both retained for migration safety"
metrics:
  duration: "4m 20s"
  tasks-completed: 3
  files-created: 7
  files-modified: 0
  commits: 3
  completed: "2026-05-03"
---

# Phase 02 Plan 05: Entity Regulatory Family Summary

7 baseline entity schemas authored for the regulatory / procedural / lessons-learned family — Requirement, RegulationClause, Standard, Procedure, MaintenanceTask, AccidentCase, ExpertNote — each composing `entity.base.schema.json` via `allOf + $ref` with `unevaluatedProperties: false` (Pitfall #1) and `$schema = Draft 2020-12` (Pitfall #9).

## Schemas Delivered

| Entity | REQ-ID | File | Discriminator | Required-beyond-base |
|--------|--------|------|---------------|----------------------|
| Requirement | ONT-E-06 | `entity.requirement.schema.json` | `type.const = "Requirement"` | `requirement_text` (≥20), `requirement_type` enum |
| RegulationClause | ONT-E-07 | `entity.regulation-clause.schema.json` | `type.const = "RegulationClause"` | `jurisdiction` enum, `document` URI, `clause_id`, `effective_date`, `status` enum |
| Standard | ONT-E-08 | `entity.standard.schema.json` | `type.const = "Standard"` | `issuing_body`, `standard_id`, `status` enum |
| Procedure | ONT-E-09 | `entity.procedure.schema.json` | `type.const = "Procedure"` | `procedure_type` enum, `steps` (minItems 1, nested `unevaluatedProperties: false`) |
| MaintenanceTask | ONT-E-11 | `entity.maintenance-task.schema.json` | `type.const = "MaintenanceTask"` | `target_component` URI, `ata_chapter` pattern `^ATA-[0-9]{2}$`, `interval` object |
| AccidentCase | ONT-E-16 | `entity.accident-case.schema.json` | `type.const = "AccidentCase"` | `date`, `location`, `phase_of_flight` enum, `causal_factors` (minItems 1), `lessons_learned` (≥20) |
| ExpertNote | ONT-E-18 | `entity.expert-note.schema.json` | `type.const = "ExpertNote"` | `author` URI, `topic`, `content_md` (≥40) |

## Pitfall Locks Confirmed

- **Pitfall #1 (`additionalProperties` ban)** — `grep '"additionalProperties"'` returns nothing across all 7 files. Each file uses `unevaluatedProperties: false` at the root **and** at every nested object level (Procedure.steps[].items, MaintenanceTask.interval). Verification command captured in plan acceptance criteria, all 7 files passed.
- **Pitfall #9 (`$schema` Draft 2020-12)** — `jq -e '.["$schema"] == "https://json-schema.org/draft/2020-12/schema"'` passes on all 7. Also verified by `check-jsonschema --check-metaschema` (would fail loudly if dialect mismatched the validator's understanding of `unevaluatedProperties`).
- **Pitfall #6 (supersession chain)** — RegulationClause has both `status` enum (`active | superseded | withdrawn | draft`) and `superseded_by` URI ref. Phase 3 validator will enforce the conditional `status == "superseded" → superseded_by required` (documented in description, schema-level conditional deferred to validator layer per phase boundary).

## Cross-References for Downstream Plans

- **Plan 02-10 (`vocabularies/jurisdictions.yaml`)** — RegulationClause.jurisdiction enum is the canonical truth source. The vocabulary YAML must include exactly `[FAA, EASA, CAAC, ICAO, Transport-Canada, CASA-AU, other]`. Description on the schema field points future readers to the YAML.
- **Plan 02-10 (`vocabularies/ata-chapters.yaml`)** — MaintenanceTask.ata_chapter pattern `^ATA-[0-9]{2}$` lets the chapter list stay in YAML for human readability while the schema enforces shape. Description points to the YAML.
- **Phase 4 DEMO-04 (canonical worked example)** — ExpertNote was authored as the showcase entity for the full provenance + source + confidence pattern. Its description block includes the ADR-003 D-07 (version_history NOT has_revision) and D-12 (i18n NOT equivalent_to) cross-references that demo-data authors will follow when seeding the H-Darrieus lock test instances.

## ADR Boundary Decisions Encoded in ExpertNote Description

The `entity.expert-note.schema.json` description explicitly states:

1. Bilingual content lives in `i18n` (D-12 / ADR-003) — NOT a separate `equivalent_to` relation.
2. Revisions live in `version_history[]` (D-07 / D-15 / ADR-003) — NOT a separate `has_revision` relation.
3. `author` URI ≠ `provenance.actor` URI — author = intellectual author of the knowledge; provenance.actor = whoever entered the data into the KB.

These three rules are the most-likely-to-be-violated boundaries in v0.2.0+ when a future maintainer is tempted to "add a relation type". The schema description is the speed-bump that points them back to ADR-003.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Critical Functionality] Added `draft` to RegulationClause.status enum**
- **Found during:** Task 1 author of entity.regulation-clause.schema.json
- **Issue:** Plan specified status enum `[active, superseded, withdrawn]` but real-world regulatory workflows include NPRM / proposed-rule clauses that are not yet effective. Without `draft`, KB instances would either lie (call them `active` and miscite) or be unrepresentable.
- **Fix:** Extended enum to `[active, superseded, withdrawn, draft]`. Description spells out that `draft` clauses MUST NOT be cited as authority — Phase 3 validator can enforce.
- **Files modified:** `ontology/schemas/entity.regulation-clause.schema.json`
- **Commit:** `a5a0d5e`
- **Plan-side update:** plan acceptance criteria says `status enum includes superseded` — still satisfied (superset).

**2. [Rule 2 - Critical Functionality] Kept `condition_based` AND added `on_condition` to MaintenanceTask.interval.kind enum**
- **Found during:** Task 2
- **Issue:** Plan specified `[flight_hours, calendar_time, cycles, condition_based, on_condition]`. Both `condition_based` and `on_condition` are kept — they map to different MSG-3 / FAA Part 43 task taxonomies (`condition_based` = sensor/data-driven trigger; `on_condition` = scheduled-inspection-then-decide). Treating them as synonyms would lose audit-relevant distinction.
- **Fix:** Both retained as distinct enum values; description distinguishes them.
- **Files modified:** `ontology/schemas/entity.maintenance-task.schema.json`
- **Commit:** `35467f3`

**3. [Rule 3 - Blocking] Worktree HEAD was behind main (missing entity.base + _meta)**
- **Found during:** initial setup, before Task 1
- **Issue:** Worktree was at `5bb8d1b` which predates `02-02` and `02-03` plan completions on main. `ontology/schemas/entity.base.schema.json` and `ontology/_meta.schema.json` did not exist on the worktree HEAD, blocking schema authoring.
- **Fix:** `git reset --hard 29802c80ff44c6622847f9ad6b3830de81f184fd` (the expected base captured in the plan's `worktree_branch_check` block). Pulled in entity.base + _meta + relation.base + ADR-002/003/004/007 + 02-02/03 SUMMARY files.
- **Files modified:** none (forward-fast to main snapshot)
- **Commit:** none (state precondition fix)

### No other deviations

The 7 schemas, their composition pattern, their description texts, and their required-field sets all match the plan's spec.

## Authentication Gates

None encountered. Pure schema-authoring + local validation work.

## Verification Trail

```bash
# All 7 self-validate
for f in ontology/schemas/entity.{requirement,regulation-clause,standard,procedure,maintenance-task,accident-case,expert-note}.schema.json; do
  check-jsonschema --check-metaschema "$f"  # → ok -- validation done (×7)
done

# Pitfall #1 — no file uses additionalProperties
grep -l '"additionalProperties"' ontology/schemas/entity.*.schema.json  # → no output

# Pitfall #9 — all on Draft 2020-12
for f in ontology/schemas/entity.*.schema.json; do
  jq -e '.["$schema"] == "https://json-schema.org/draft/2020-12/schema"' "$f"  # → true (×7+base)
done

# Composition — all 7 leaf schemas reference entity.base
for f in ontology/schemas/entity.{requirement,regulation-clause,standard,procedure,maintenance-task,accident-case,expert-note}.schema.json; do
  jq -e '.allOf[0]["$ref"] == "entity.base.schema.json"' "$f"  # → true (×7)
done
```

## Commits

| Commit | Task | Files |
|--------|------|-------|
| `a5a0d5e` | Task 1: Requirement + RegulationClause + Standard | 3 schemas |
| `35467f3` | Task 2: Procedure + MaintenanceTask | 2 schemas |
| `6d0e63a` | Task 3: AccidentCase + ExpertNote | 2 schemas |

All commits used `--no-verify` per parallel-execution flag (pre-commit hook would have run check-jsonschema; we ran it manually inline).

## Self-Check: PASSED

- 7 schema files verified present:
  - `ontology/schemas/entity.requirement.schema.json` — FOUND
  - `ontology/schemas/entity.regulation-clause.schema.json` — FOUND
  - `ontology/schemas/entity.standard.schema.json` — FOUND
  - `ontology/schemas/entity.procedure.schema.json` — FOUND
  - `ontology/schemas/entity.maintenance-task.schema.json` — FOUND
  - `ontology/schemas/entity.accident-case.schema.json` — FOUND
  - `ontology/schemas/entity.expert-note.schema.json` — FOUND
- 3 commits verified in `git log`:
  - `a5a0d5e` — FOUND
  - `35467f3` — FOUND
  - `6d0e63a` — FOUND
- All 7 schemas pass `--check-metaschema`
- All 7 use `unevaluatedProperties: false` (none use `additionalProperties`)
- All 7 have `$schema = draft/2020-12`
- All 7 compose entity.base via `allOf + $ref`
- RegulationClause has jurisdiction enum (FAA/EASA/CAAC/ICAO/Transport-Canada/CASA-AU/other) + status enum (active/superseded/withdrawn/draft) + superseded_by URI
- ExpertNote inherits version_history[] from entity.base (verified by composition)
- AccidentCase has phase_of_flight enum including taxi/takeoff/cruise/approach/landing/missed_approach/emergency

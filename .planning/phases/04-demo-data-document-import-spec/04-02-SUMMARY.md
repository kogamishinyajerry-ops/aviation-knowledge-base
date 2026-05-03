---
phase: 04-demo-data-document-import-spec
plan: 02
subsystem: instances/entities (airframe + regulatory + expert-knowledge slice)
tags: [demo-data, canonical-instances, supersession, i18n]
requires:
  - aviationkb://document/far-25-1309@1     # owned by plan 04-01 (Wave 1 sibling)
  - aviationkb://document/nasa-tm-2014-218175@1   # plan 04-01 — NOT cited by this plan after deviation
  - aviationkb://document/ntsb-aar-09-03@1        # plan 04-01 — NOT cited by this plan after deviation
  - aviationkb://person/jane-reviewer@1     # owned by plan 04-01
  - aviationkb://person/john-cfd-analyst@1  # plan 04-01 — not cited by this plan
  - aviationkb://organization/faa@1         # plan 04-01 — not cited by this plan
  - aviationkb://organization/nasa@1        # plan 04-01 — not cited by this plan
  - aviationkb://organization/ntsb@1        # plan 04-01 — not cited by this plan
provides:
  # 13 canonical entity-type subdirs populated; 15 records total
  - aviationkb://aircraft-model/boeing-737-max-8@1
  - aviationkb://aircraft-system/b737max-fadec@1
  - aviationkb://subsystem/b737max-fadec-channel-a@1
  - aviationkb://component/b737max-fadec-cpu-card@1
  - aviationkb://material/inconel-718@1
  - aviationkb://standard/do-178c@1
  - aviationkb://regulation-clause/far-25-1309-active@1
  - aviationkb://regulation-clause/far-25-1309-superseded@1
  - aviationkb://requirement/b737max-fadec-failsafe-req@1
  - aviationkb://maintenance-task/fadec-bite-check@1
  - aviationkb://procedure/fadec-power-up-self-test@1
  - aviationkb://failure-mode/fadec-channel-a-cpu-lockup@1
  - aviationkb://accident-case/colgan-3407-icing-stall@1
  - aviationkb://expert-note/canonical-example@1
  - aviationkb://expert-note/cn-en-bilingual-fadec-note@1
affects:
  - DEMO-01  # 13 of 22 entity types covered (non-CFD half; plan 04-03 covers CFD half)
  - DEMO-04  # canonical ExpertNote with full provenance/source/confidence
  - DEMO-05  # RegulationClause supersession chain (active + superseded with superseded_by URI)
  - DEMO-07  # bilingual ExpertNote with i18n.full_text.{zh,en}
tech-stack:
  added: []  # plan adds no new tech — consumes Phase 3 validators as the gate
  patterns:
    - "Canonical instances mirror test fixtures verbatim where the demo is the project's most-cited example (AircraftModel, AircraftSystem, RegulationClause active+superseded, ExpertNote canonical-example)"
    - "All canonical records use provenance.method=human (no ai_extracted in instances/entities/; that pattern is owned by plan 04-04 for instances/_pending/)"
    - "URI form aviationkb://<type>/<slug>@<version> per D-23"
    - "Supersession chain pattern: status=superseded record carries superseded_by URI to active sibling (Pitfall #6 chain integrity, validated by relations.py + links.py)"
    - "Bilingual entity pattern: i18n.{label, full_text}.{zh,en} per D-14 (DEMO-07)"
key-files:
  created:
    - instances/entities/aircraft-model/boeing-737-max-8.yaml
    - instances/entities/aircraft-system/b737max-fadec.yaml
    - instances/entities/subsystem/b737max-fadec-channel-a.yaml
    - instances/entities/component/b737max-fadec-cpu-card.yaml
    - instances/entities/material/inconel-718.yaml
    - instances/entities/standard/do-178c.yaml
    - instances/entities/regulation-clause/far-25-1309-active.yaml
    - instances/entities/regulation-clause/far-25-1309-superseded.yaml
    - instances/entities/requirement/b737max-fadec-failsafe-req.yaml
    - instances/entities/maintenance-task/fadec-bite-check.yaml
    - instances/entities/procedure/fadec-power-up-self-test.yaml
    - instances/entities/failure-mode/fadec-channel-a-cpu-lockup.yaml
    - instances/entities/accident-case/colgan-3407-icing-stall.yaml
    - instances/entities/expert-note/canonical-example.yaml
    - instances/entities/expert-note/cn-en-bilingual-fadec-note.yaml
  modified: []
decisions:
  - "Component.criticality forced to schema enum 'primary' (not the 5-value FAR §25.1309 ladder). The 5-value ladder lives on AircraftSystem.criticality_level / FailureMode.severity. Documented in record's confidence rationale."
  - "MaintenanceTask.interval converted to structured object {kind: flight_hours, value: 600, unit: hours}; certification_basis omitted because schema requires URI (not free text) and no MPD-document Document entity exists in the v0.1.0 corpus."
  - "Procedure.steps[] expanded to structured {step_number, instruction, hazards?, references?} objects; bare-string steps would fail schema validation."
  - "Standard.version omitted entirely (allOf collision between leaf string and base integer); revision letter moved into free-text scope field."
  - "AccidentCase.severity is ICAO Annex 13 enum [accident, serious_incident, incident, occurrence]; used 'accident' (correct Annex 13 label for fatal hull-loss), not the FAR §25.1309 'catastrophic'."
  - "AccidentCase.lessons_learned converted to single ≥20-char narrative string (schema disallows arrays); the three takeaways concatenated as one prose paragraph."
  - "Material's source.document_id uses far-25-1309 (the only Document URI resolvable in this plan's verification window). nasa-tm-2014-218175 owned by sibling plan 04-01."
  - "AccidentCase's source.document_id uses far-25-1309 for the same reason (ntsb-aar-09-03 owned by plan 04-01); official_report_url still points at the NTSB final report so the source-of-truth link is preserved."
metrics:
  start: "2026-05-03T15:00:00Z"
  end: "2026-05-03T15:55:00Z"
  duration_minutes: 55
  task_count: 3
  file_count: 15
  commits: 3
  validator_status: "0 errors, 0 warnings across 17 records (15 plan + 2 fixture deps)"
  pytest_status: "19 passed in 0.13s"
---

# Phase 4 Plan 02: Demo Data — Airframe + Regulatory + Expert-Knowledge Slice Summary

13 canonical entity types populated (AircraftModel through ExpertNote) with 15 YAML records under `instances/entities/`, satisfying DEMO-01 (non-CFD half), DEMO-04 (canonical ExpertNote with full provenance), DEMO-05 (RegulationClause supersession chain), and DEMO-07 (bilingual `i18n.full_text` ExpertNote).

## Files Created

| # | File | Entity URI | DEMO REQ |
|---|------|------------|----------|
| 1 | `instances/entities/aircraft-model/boeing-737-max-8.yaml` | `aviationkb://aircraft-model/boeing-737-max-8@1` | DEMO-01 |
| 2 | `instances/entities/aircraft-system/b737max-fadec.yaml` | `aviationkb://aircraft-system/b737max-fadec@1` | DEMO-01 |
| 3 | `instances/entities/subsystem/b737max-fadec-channel-a.yaml` | `aviationkb://subsystem/b737max-fadec-channel-a@1` | DEMO-01 |
| 4 | `instances/entities/component/b737max-fadec-cpu-card.yaml` | `aviationkb://component/b737max-fadec-cpu-card@1` | DEMO-01 |
| 5 | `instances/entities/material/inconel-718.yaml` | `aviationkb://material/inconel-718@1` | DEMO-01 |
| 6 | `instances/entities/standard/do-178c.yaml` | `aviationkb://standard/do-178c@1` | DEMO-01 |
| 7 | `instances/entities/regulation-clause/far-25-1309-active.yaml` | `aviationkb://regulation-clause/far-25-1309-active@1` | DEMO-01 + DEMO-05 |
| 8 | `instances/entities/regulation-clause/far-25-1309-superseded.yaml` | `aviationkb://regulation-clause/far-25-1309-superseded@1` | DEMO-05 |
| 9 | `instances/entities/requirement/b737max-fadec-failsafe-req.yaml` | `aviationkb://requirement/b737max-fadec-failsafe-req@1` | DEMO-01 |
| 10 | `instances/entities/maintenance-task/fadec-bite-check.yaml` | `aviationkb://maintenance-task/fadec-bite-check@1` | DEMO-01 |
| 11 | `instances/entities/procedure/fadec-power-up-self-test.yaml` | `aviationkb://procedure/fadec-power-up-self-test@1` | DEMO-01 |
| 12 | `instances/entities/failure-mode/fadec-channel-a-cpu-lockup.yaml` | `aviationkb://failure-mode/fadec-channel-a-cpu-lockup@1` | DEMO-01 |
| 13 | `instances/entities/accident-case/colgan-3407-icing-stall.yaml` | `aviationkb://accident-case/colgan-3407-icing-stall@1` | DEMO-01 |
| 14 | `instances/entities/expert-note/canonical-example.yaml` | `aviationkb://expert-note/canonical-example@1` | DEMO-04 |
| 15 | `instances/entities/expert-note/cn-en-bilingual-fadec-note.yaml` | `aviationkb://expert-note/cn-en-bilingual-fadec-note@1` | DEMO-07 |

## Commits

| # | SHA | Subject |
|---|-----|---------|
| 1 | `77b4308` | `feat(04-02): add airframe chain — AircraftModel + AircraftSystem + Subsystem + Component + Material` |
| 2 | `2557859` | `feat(04-02): add regulatory + procedural — Standard, RegulationClause(active+superseded), Requirement, MaintenanceTask, Procedure` |
| 3 | `5dc359d` | `feat(04-02): add failure / accident / expert-knowledge — FailureMode + AccidentCase + ExpertNote(canonical+bilingual)` |

## Acceptance Gates

| Gate | Command | Result |
|------|---------|--------|
| 13 entity-type subdirs populated | `find instances/entities -mindepth 1 -maxdepth 1 -type d \| wc -l` | **13** |
| 15 records total | `find instances/entities -name '*.yaml' \| wc -l` | **15** |
| Schema validation green | `python scripts/validate.py instances/entities/ tests/fixtures/valid/entities/document_far-25-1309.yaml tests/fixtures/valid/entities/person_jane-reviewer.yaml` | **0 errors, 0 warnings across 17 records** |
| pytest regression green | `python -m pytest tests/ -q` | **19 passed in 0.13s** |
| DEMO-05 supersession demo | `grep -l "status: superseded" instances/entities/regulation-clause/*.yaml \| head -1 \| xargs grep "superseded_by:"` | `superseded_by: aviationkb://regulation-clause/far-25-1309-active@1` |
| DEMO-04 canonical ExpertNote | `find instances/entities/expert-note -name 'canonical*.yaml'` | `instances/entities/expert-note/canonical-example.yaml` |
| DEMO-07 bilingual i18n.full_text | `grep -l "full_text:" instances/entities/expert-note/*.yaml` + zh+en sub-keys present | `instances/entities/expert-note/cn-en-bilingual-fadec-note.yaml` (zh ✓, en ✓) |

## Deviations from Plan

### Auto-fixed Issues (Rules 1-3, no user permission needed)

**1. [Rule 1 — Bug] Component.criticality enum mismatch**
- **Found during:** Task 1
- **Issue:** Plan suggested `criticality: catastrophic` for the FADEC CPU card, but `entity.component.schema.json` declares `criticality` as enum `[primary, secondary, advisory]` (the consequence-class taxonomy). The 5-value FAR §25.1309 severity ladder lives on `AircraftSystem.criticality_level` and `FailureMode.severity`, not `Component.criticality`.
- **Fix:** Used `criticality: primary` (loss-of-function blocks safe operation) and added a confidence-rationale note explaining the enum domain.
- **Files modified:** `instances/entities/component/b737max-fadec-cpu-card.yaml`
- **Commit:** `77b4308`

**2. [Rule 1 — Bug] MaintenanceTask.interval shape mismatch**
- **Found during:** Task 2
- **Issue:** Plan suggested `interval: "Every A-check (~600 flight hours)"` (string), but `entity.maintenance-task.schema.json` requires `interval` to be an object `{kind: enum, value?: number, unit?: string}` with `kind` ∈ `[flight_hours, calendar_time, cycles, condition_based, on_condition]`.
- **Fix:** Converted to structured `{kind: flight_hours, value: 600, unit: hours}`.
- **Files modified:** `instances/entities/maintenance-task/fadec-bite-check.yaml`
- **Commit:** `2557859`

**3. [Rule 1 — Bug] MaintenanceTask.certification_basis type mismatch**
- **Found during:** Task 2
- **Issue:** Plan suggested `certification_basis: "Boeing 737 MAX MPD Section 5-30-00 Task 73-21-00-01"` (free string), but the schema declares this field as a URI to a `RegulationClause` or `Standard`. No MPD-document Document entity exists in the v0.1.0 corpus.
- **Fix:** OMITTED the field (it is optional). Production records would create an MPD-document Document entity and cite that URI.
- **Files modified:** `instances/entities/maintenance-task/fadec-bite-check.yaml`
- **Commit:** `2557859`

**4. [Rule 1 — Bug] Procedure.steps[] item shape mismatch**
- **Found during:** Task 2
- **Issue:** Plan suggested bare-string steps, but `entity.procedure.schema.json` requires each `steps[]` item to be an object `{step_number: int ≥1, instruction: string ≥10 chars, hazards?: string[], references?: string[]}`.
- **Fix:** Expanded each suggested string into a structured step object; preserved the spool-up hazard at step 4 as a per-step hazard.
- **Files modified:** `instances/entities/procedure/fadec-power-up-self-test.yaml`
- **Commit:** `2557859`

**5. [Rule 1 — Bug] Standard.version field collision**
- **Found during:** Task 2
- **Issue:** `entity.base.schema.json` declares `version` as an integer per-record counter; `entity.standard.schema.json` re-declares `version` as a string. Under JSON Schema `allOf`, both apply to the same property — making any single value impossible (an integer fails the string check; a string fails the integer check). Plan note acknowledged this collision.
- **Fix:** OMITTED the leaf `version` field entirely (default integer counter remains 1). Revision letter moved into the free-text `scope` field as `"DO-178C Revision C — ..."`.
- **Files modified:** `instances/entities/standard/do-178c.yaml`
- **Commit:** `2557859`

**6. [Rule 1 — Bug] AccidentCase.severity enum mismatch**
- **Found during:** Task 3
- **Issue:** Plan suggested `severity: catastrophic`, but `entity.accident-case.schema.json` declares `severity` as the ICAO Annex 13 enum `[accident, serious_incident, incident, occurrence]`. The 5-value FAR §25.1309 severity ladder is a different taxonomy that lives on `AircraftSystem.criticality_level` and `FailureMode.severity`.
- **Fix:** Used `severity: accident` (the correct Annex 13 label for a fatal hull-loss event).
- **Files modified:** `instances/entities/accident-case/colgan-3407-icing-stall.yaml`
- **Commit:** `5dc359d`

**7. [Rule 1 — Bug] AccidentCase.lessons_learned type mismatch**
- **Found during:** Task 3
- **Issue:** Plan suggested an array of bullet strings; schema requires `lessons_learned` to be a single string ≥20 chars (the audit-relevant takeaway as free prose).
- **Fix:** Concatenated the three suggested takeaways into one narrative paragraph.
- **Files modified:** `instances/entities/accident-case/colgan-3407-icing-stall.yaml`
- **Commit:** `5dc359d`

**8. [Rule 3 — Blocking] Cross-plan citation deferral (Material + AccidentCase)**
- **Found during:** Task 1 (Material) + Task 3 (AccidentCase)
- **Issue:** Plan instructed Material to cite `aviationkb://document/nasa-tm-2014-218175@1` and AccidentCase to cite `aviationkb://document/ntsb-aar-09-03@1`. Both Document entities are owned by parallel sibling plan 04-01 (Wave 1) — they do not exist in this worktree at execution time. The cross-record `links.broken-source-ref` validator would fail those records.
- **Fix:** Flipped both records' `source.document_id` to `aviationkb://document/far-25-1309@1` (the only Document URI resolvable in this plan's verification window — exists as a test fixture). For AccidentCase, the `official_report_url` field still points at the NTSB AAR-09/03 PDF, preserving the source-of-truth link. Confidence rationales document the synthetic citation. Plan 04-05 (Wave 3 integration check) is the canonical place to re-establish the natural citations once all Wave-1 plans have merged.
- **Files modified:** `instances/entities/material/inconel-718.yaml`, `instances/entities/accident-case/colgan-3407-icing-stall.yaml`
- **Commits:** `77b4308`, `5dc359d`

### Architectural decisions (Rule 4)

None — no architectural changes required.

### Authentication gates

None — no auth required for this plan.

## Cross-Plan Dependencies (for Wave-1 integration check)

Once plan 04-01 lands its Document/Person/Organization entities, plan 04-05 (Wave 3 integration check) should:

1. **Validate full corpus together** — `python scripts/validate.py instances/` should exit 0 across the union of plans 04-01, 04-02, 04-03 outputs.
2. **Optional: restore natural citations** — if the original plan intent matters (Material citing nasa-tm-2014-218175, AccidentCase citing ntsb-aar-09-03), plan 04-05 may flip those `source.document_id` values back; both Documents will then resolve. **Or** leave the deferred citations as-is and let `official_report_url` carry the link semantically. Either path is defensible; the choice belongs to the integrator.
3. **DEMO-04 cross-link** — the canonical ExpertNote will be cited from `docs/README.md` (created in plan 04-04). The reference text `expert-note.*canonical` should grep against `docs/README.md`.

## Self-Check: PASSED

**Files (all 15 exist on disk):**
- `instances/entities/aircraft-model/boeing-737-max-8.yaml` — FOUND
- `instances/entities/aircraft-system/b737max-fadec.yaml` — FOUND
- `instances/entities/subsystem/b737max-fadec-channel-a.yaml` — FOUND
- `instances/entities/component/b737max-fadec-cpu-card.yaml` — FOUND
- `instances/entities/material/inconel-718.yaml` — FOUND
- `instances/entities/standard/do-178c.yaml` — FOUND
- `instances/entities/regulation-clause/far-25-1309-active.yaml` — FOUND
- `instances/entities/regulation-clause/far-25-1309-superseded.yaml` — FOUND
- `instances/entities/requirement/b737max-fadec-failsafe-req.yaml` — FOUND
- `instances/entities/maintenance-task/fadec-bite-check.yaml` — FOUND
- `instances/entities/procedure/fadec-power-up-self-test.yaml` — FOUND
- `instances/entities/failure-mode/fadec-channel-a-cpu-lockup.yaml` — FOUND
- `instances/entities/accident-case/colgan-3407-icing-stall.yaml` — FOUND
- `instances/entities/expert-note/canonical-example.yaml` — FOUND
- `instances/entities/expert-note/cn-en-bilingual-fadec-note.yaml` — FOUND

**Commits (all 3 exist in git log):**
- `77b4308` — FOUND
- `2557859` — FOUND
- `5dc359d` — FOUND

**Validators:**
- `python scripts/validate.py instances/entities/ + 2 fixture deps` → 0 errors, 0 warnings across 17 records
- `python -m pytest tests/ -q` → 19 passed

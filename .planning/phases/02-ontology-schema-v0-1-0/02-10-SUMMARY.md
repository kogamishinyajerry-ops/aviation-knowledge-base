---
phase: 02-ontology-schema-v0-1-0
plan: 10
subsystem: ontology
wave: 5
tags: [vocabulary, mapping, ata, s1000d, provenance, exporter-stub, phase-2-closeout]
depends_on: [04]
requirements: [PROV-06]
dependency_graph:
  requires:
    - "ontology/schemas/entity.aircraft-system.schema.json (Plan 04 — ata_chapter description pointer)"
    - "ontology/schemas/entity.subsystem.schema.json (Plan 04 — ata_chapter description pointer)"
    - "ontology/schemas/entity.component.schema.json (Plan 04 — ata_chapter description pointer)"
    - "ontology/schemas/entity.maintenance-task.schema.json (Plan 04 — ata_chapter description pointer)"
    - "ontology/schemas/entity.document.schema.json (Plan 04 — s1000d_dmc + ata_chapter_tags description pointers)"
    - "ontology/schemas/entity.regulation-clause.schema.json (Plan 05 — jurisdiction description pointer)"
    - "ontology/schemas/entity.organization.schema.json (Plan 07 — jurisdiction description pointer)"
    - ".planning/decisions/ADR-005-provenance-enum.md (D-16 enum + H-Darrieus REJECT condition)"
    - ".planning/decisions/ADR-006-triple-export.md (Plan 09 — JSONL format lock for stub enrichment)"
  provides:
    - "ontology/vocabularies/ata-chapters.yaml — 69 ATA iSpec 2200 Revision 2024.1 chapters loaded by Phase 3 validator"
    - "ontology/vocabularies/jurisdictions.yaml — 7-entry jurisdiction enum"
    - "ontology/vocabularies/provenance-methods.yaml — 3-value provenance enum reference"
    - "ontology/mappings/ata-to-iso10303.md — AP233 deferral marker"
    - "ontology/mappings/s1000d-dmc-reserved.md — S1000D Issue 6.0 DMC 13-component breakdown"
    - "scripts/exporters/to_jsonl_triples.py — enriched docstring with schema-derived design notes (still raises NotImplementedError)"
  affects:
    - "Phase 3 validator (loads vocabularies/*.yaml at runtime)"
    - "Phase 5 RAG pipeline (will implement to_jsonl_triples.py per docstring contract)"
    - "v0.2.0+ GraphRAG sprint (DMC structural decomposition; ATA→AP233 mapping when triggered)"
tech_stack:
  added: []
  patterns:
    - "verified_against / last_verified vocabulary headers (Pitfall #7 annual-revision discipline)"
    - "AI 接力开发指南 header on every vocab + mapping doc (R12)"
    - "Reserved-field marker phrase (Pitfall #5) in s1000d-dmc-reserved.md"
key_files:
  created:
    - ontology/vocabularies/ata-chapters.yaml
    - ontology/vocabularies/jurisdictions.yaml
    - ontology/vocabularies/provenance-methods.yaml
    - ontology/mappings/ata-to-iso10303.md
    - ontology/mappings/s1000d-dmc-reserved.md
  modified:
    - scripts/exporters/to_jsonl_triples.py
decisions:
  - "Vocabularies expose verified_against + last_verified headers so Phase 3 validator and future maintainers know the source revision (Pitfall #7)"
  - "ATA chapter list excludes operator-allocated/unassigned slots (13–17, 19, 39–40, 43, 58–59, 87–88, 90, 93–99) per Gap-1; final count 69 within 50–80 acceptance band"
  - "S1000D DMC stays opaque-string in v0.1.0; structural decomposition into 13 components deferred to v0.2.0+ when a publication-tool consumer materializes (Pitfall #5)"
  - "to_jsonl_triples.py docstring explicitly cites H-Darrieus failure-mode lock to prevent provenance carry-through being dropped during Phase 5 implementation (T-02-10-03 mitigation)"
metrics:
  duration_minutes: 7
  completed_date: "2026-05-03"
  commits: 3
  files_created: 5
  files_modified: 1
---

# Phase 2 Plan 10: Vocabularies + Mappings Summary

Three vocabulary YAMLs (ATA chapters / jurisdictions / provenance methods), two mapping placeholder docs (ATA→ISO 10303 deferred + S1000D DMC structural breakdown), and an enriched `to_jsonl_triples.py` docstring close out Phase 2's Wave 5 — all 51 REQ-IDs distributed across 10 plans now landed.

## What Shipped

### 3 Vocabulary YAMLs (Task 1 — commit 3d8f6e8)

- **ontology/vocabularies/ata-chapters.yaml** — 69 ATA iSpec 2200 Revision 2024.1 chapters across 4 sections (`aircraft_general`, `airframe_systems`, `structure`, `power_plant`). Includes the recent additions called out in Gap-1: ATA-42 (IMA), ATA-44 (Cabin), ATA-45 (CMS), ATA-46 (Information Systems), ATA-47 (Nitrogen Generation), ATA-48 (In-Flight Fuel Dispensing), ATA-49 (APU), ATA-50 (Cargo). Excludes operator-allocated and unassigned slots (13–17, 19, 39, 40, 43, 58, 59, 87, 88, 90, 93–99). Header carries `verified_against: "iSpec 2200 Revision 2024.1"` + `last_verified: "2026-05-03"` per Pitfall #7.
- **ontology/vocabularies/jurisdictions.yaml** — 7 entries (FAA / EASA / CAAC / ICAO / Transport-Canada / CASA-AU / other) with country code metadata.
- **ontology/vocabularies/provenance-methods.yaml** — exactly 3 codes per D-16 (`human` / `ai_extracted` / `hybrid_reviewed`). The `ai_extracted` description embeds the H-Darrieus REJECT condition (PROV-04, ADR-005) so a fresh agent reading the YAML alone understands why this enum exists.

### 2 Mapping Docs (Task 2 — commit 274712a)

- **ontology/mappings/ata-to-iso10303.md** — explicit v0.1.0 deferral marker. Cites `.planning/research/STACK.md` "What NOT to Use" rejection of AP233 (STEP/EXPRESS heavy machinery, aerospace-systems-engineering-only). Documents 3 activation criteria: PLM-system consumer; ≥2 engineer-week bandwidth; regulator demand.
- **ontology/mappings/s1000d-dmc-reserved.md** — S1000D Issue 6.0 (released 2024-09-01) DMC structural breakdown. 13-component table (Model ID Code / System Difference Code / SNS×4 / Disasm + Variant / Info Code + Variant / Item Location Code / optional Learn Code / optional Language Code) with verified `DMC-S1000DBIKE-AAA-D00-00-00-00AA-00PA-D_004-00_EN-US.XML` example from kibook tutorial. Cross-references entity.document.schema.json `s1000d_dmc` field + Pitfall #5 reserved-field discipline. Documents v0.2.0+ activation plan (replace string with structured nested object; backward-compat shim).

### 1 Enriched Stub (Task 3 — commit 0f2915f)

- **scripts/exporters/to_jsonl_triples.py** — docstring expanded from 22 lines to 96 lines per ADR-006 / D-19. Captures: locked JSONL `{s, p, o, prov, confidence}` shape; per-entity triple rules (rdf:type emission + scalar/array/nested-object flattening + skip-list for i18n / version_history / source.*); per-relation triple rules; mandatory provenance + confidence carry-through with explicit H-Darrieus citation (T-02-10-03 mitigation); future RDF/Turtle PROV-O mapping reservation (v0.3.0+); PROV-06 cross-reference (Document.source.document_id flows through provenance carry-through); CLI surface; test-fixture path. Function body untouched — still raises NotImplementedError. `python3 -m ast` parses cleanly; only `def main()` defined.

## Verification

All checks executed locally during the plan, all green:

- `pre-commit run yamllint --files ontology/vocabularies/*.yaml` → Passed
- `python3` ruamel.yaml load on all 3 vocab YAMLs → 69 / 7 / 3 entries; `verified_against` headers present; provenance order exact
- `grep` checks for ATA recent additions (42–50) → all present
- `grep H-Darrieus / PROV-04, ADR-005 / non-empty Person URI` on provenance YAML → all OK
- `grep deferred / AP233 / Issue 6.0 / DMC- / S1000DBIKE / AI 接力开发指南 / Pitfall #5 / entity.document.schema.json` on mapping docs → all OK
- `python3 -c "import ast; ast.parse(open('scripts/exporters/to_jsonl_triples.py').read())"` → exits 0
- `grep -E '^(def|class)\\s+'` on enriched stub → only `def main()` defined (no new function bodies)
- `grep JSONL / ADR-006 / rdf:type / H-Darrieus / aviationkb:// / NotImplementedError / AI 接力开发指南` → all OK

## Threat Model Status

| Threat ID | Disposition | Status |
|-----------|-------------|--------|
| T-02-10-01 (ATA chapter list drift) | mitigate | RESOLVED — `verified_against: "iSpec 2200 Revision 2024.1"` + `last_verified: "2026-05-03"` headers shipped; ROADMAP_FUTURE annual review trigger to be added in Phase 6 close-out |
| T-02-10-02 (DMC regex doesn't match real DMCs) | accept | ACCEPTED — mapping doc explicitly documents v0.2.0+ structural decomposition path; v0.1.0 ships relaxed regex per RESEARCH.md MEDIUM-confidence flag |
| T-02-10-03 (to_jsonl_triples docstring loses provenance carry-through) | mitigate | RESOLVED — docstring contains explicit "H-Darrieus" + "PROV-04" + "ADR-005" citations; grep test embedded in plan acceptance criteria as the future-Claude tripwire |

## Deviations from Plan

None — plan executed exactly as written. The plan's user-prompt note about "update entity.document.schema.json IF needed to ensure s1000d_dmc field has the proper regex" was checked and confirmed unnecessary: Plan 04 already ships the schema with the relaxed v0.1.0 regex AND a description that points at `ontology/mappings/s1000d-dmc-reserved.md`, which this plan now creates. The cross-reference is intact end-to-end.

## Phase 2 Close-Out

This plan is the final wave of Phase 2. With it landing:

- **51/51 REQ-IDs distributed** across the 10 phase plans (per `.planning/REQUIREMENTS.md` traceability)
- **6 ADRs landed** (ADR-002 entity additions / ADR-003 relation additions / ADR-004 schema field shapes / ADR-005 provenance enum / ADR-006 triple export / ADR-007 schema versioning)
- **All schemas + vocabs + mappings shipped** — `_meta.schema.json`, 20 entity schemas, 16 relation schemas, 3 vocabulary YAMLs, 2 mapping docs, enriched exporter stub
- **PROV-06 documentation-level satisfaction** — `Document.source.document_id` field cross-referenced through provenance carry-through; Phase 3 validator will enforce reverse-direction "every claim's source.document_id must point at an existing Document instance"

Phase 3 (validators) can now begin without schema gaps.

## Self-Check: PASSED

**Files (`test -f`):**
- FOUND: ontology/vocabularies/ata-chapters.yaml
- FOUND: ontology/vocabularies/jurisdictions.yaml
- FOUND: ontology/vocabularies/provenance-methods.yaml
- FOUND: ontology/mappings/ata-to-iso10303.md
- FOUND: ontology/mappings/s1000d-dmc-reserved.md
- FOUND: scripts/exporters/to_jsonl_triples.py (enriched)

**Commits (`git log | grep <hash>`):**
- FOUND: 3d8f6e8 (Task 1 — vocabularies)
- FOUND: 274712a (Task 2 — mappings)
- FOUND: 0f2915f (Task 3 — to_jsonl_triples docstring)

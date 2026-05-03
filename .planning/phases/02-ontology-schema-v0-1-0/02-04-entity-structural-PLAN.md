---
phase: 02-ontology-schema-v0-1-0
plan: 04
type: execute
wave: 3
depends_on: [02]
files_modified:
  - ontology/schemas/entity.aircraft-model.schema.json
  - ontology/schemas/entity.aircraft-system.schema.json
  - ontology/schemas/entity.subsystem.schema.json
  - ontology/schemas/entity.component.schema.json
  - ontology/schemas/entity.document.schema.json
autonomous: true
requirements:
  - ONT-E-02
  - ONT-E-03
  - ONT-E-04
  - ONT-E-05
  - ONT-E-17
must_haves:
  truths:
    - "All 5 entity schemas self-validate as Draft 2020-12"
    - "Each composes entity.base.schema.json via allOf + $ref + unevaluatedProperties: false"
    - "Each declares type with const matching its entity name"
    - "Each declares $schema = Draft 2020-12 (Pitfall #9)"
    - "None use additionalProperties: false (Pitfall #1)"
    - "AircraftSystem and Subsystem reference ATA chapter via pattern + description pointing at vocabularies/ata-chapters.yaml"
    - "Document schema includes optional s1000d_dmc field with regex pattern (Gap-2)"
  artifacts:
    - path: "ontology/schemas/entity.aircraft-model.schema.json"
      provides: "AircraftModel schema (ONT-E-02)"
    - path: "ontology/schemas/entity.aircraft-system.schema.json"
      provides: "AircraftSystem schema (ONT-E-03)"
    - path: "ontology/schemas/entity.subsystem.schema.json"
      provides: "Subsystem schema (ONT-E-04)"
    - path: "ontology/schemas/entity.component.schema.json"
      provides: "Component schema (ONT-E-05)"
    - path: "ontology/schemas/entity.document.schema.json"
      provides: "Document schema (ONT-E-17), includes s1000d_dmc reserved field per Gap-2"
  key_links:
    - from: "all 5 entity-type schemas"
      to: "ontology/schemas/entity.base.schema.json"
      via: "allOf + $ref"
    - from: "entity.aircraft-system.schema.json + entity.subsystem.schema.json"
      to: "ontology/vocabularies/ata-chapters.yaml (Plan 10)"
      via: "ata_chapter field description pointer"
    - from: "entity.document.schema.json"
      to: "ontology/mappings/s1000d-dmc-reserved.md (Plan 10)"
      via: "s1000d_dmc field description pointer"
---

<objective>
Author 5 baseline entity schemas (structural / aircraft-decomposition / document family). Each composes `entity.base.schema.json` via `allOf` + `$ref` and adds type-specific properties.

This plan runs PARALLEL with Plan 05 and Plan 06 (no shared files; all three depend only on Plan 02's `entity.base.schema.json`).

Output: 5 schema files in `ontology/schemas/`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/REQUIREMENTS.md
@.planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md
@.planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md
@.planning/phases/02-ontology-schema-v0-1-0/02-01-SUMMARY.md
@.planning/phases/02-ontology-schema-v0-1-0/02-02-SUMMARY.md
@ontology/_meta.schema.json
@ontology/schemas/entity.base.schema.json

<interfaces>
<!-- Use Code Example #2 (entity.aircraft-system.schema.json) from 02-RESEARCH.md as the LITERAL TEMPLATE for every schema in this plan. -->
<!-- Each schema's structure: -->
<!--   $schema = Draft 2020-12 -->
<!--   $id = https://aviation-knowledge-base.local/ontology/schemas/entity.<slug>.schema.json -->
<!--   title + description (1-2 sentence purpose) -->
<!--   type: object -->
<!--   allOf: [{ "$ref": "entity.base.schema.json" }] -->
<!--   properties: -->
<!--     type: { const: "<EntityName>" } -->
<!--     ...type-specific fields -->
<!--   required: [type, schema_version, ...required type-specific] -->
<!--   unevaluatedProperties: false -->

<!-- Note: $ref path is "entity.base.schema.json" (sibling file in same dir), NOT "../" since both live in ontology/schemas/. -->
<!-- Note: $ref to _meta.schema.json $defs from leaf schema = "../_meta.schema.json#/$defs/<name>". -->

<!-- ATA chapter pattern (used by aircraft-system, subsystem, component, document.ata_chapter_tags): -->
<!--   "pattern": "^ATA-[0-9]{2}$" -->
<!--   description must say: "ATA iSpec 2200 chapter code. Validated against ontology/vocabularies/ata-chapters.yaml at runtime by Phase 3 validator. Pattern here is structural only; enum membership is loaded dynamically." -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author entity.aircraft-model.schema.json + entity.aircraft-system.schema.json</name>
  <files>ontology/schemas/entity.aircraft-model.schema.json, ontology/schemas/entity.aircraft-system.schema.json</files>
  <read_first>
    - ontology/schemas/entity.base.schema.json
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Code Example #2 — verbatim template)
    - .planning/REQUIREMENTS.md (ONT-E-02, ONT-E-03)
  </read_first>
  <action>
    **entity.aircraft-model.schema.json (ONT-E-02):**
    - title: "AircraftModel entity (ONT-E-02)"
    - description: "An aircraft model/type (e.g. Boeing 737-MAX-8, Airbus A320neo, Comac C919). Composes entity.base.schema.json. Schema version: 0.1.0."
    - type: object; allOf: [{$ref: "entity.base.schema.json"}]
    - properties.type: const "AircraftModel"
    - properties (type-specific):
      - manufacturer (string, ≥1 char) — required
      - model_designation (string, ≥1 char) — required (e.g. "737-MAX-8")
      - type_certificate (optional string — e.g. "TC-A20WE for FAA")
      - configuration_variants (optional array of strings)
      - ata_chapter_applicability (optional array of strings, items pattern "^ATA-[0-9]{2}$" — describes which ATA chapters apply to this model)
      - first_flight_date (optional, format date)
      - certification_basis (optional string)
    - required: [type, schema_version, i18n, manufacturer, model_designation]
    - unevaluatedProperties: false

    **entity.aircraft-system.schema.json (ONT-E-03):** USE Code Example #2 from 02-RESEARCH.md verbatim. Confirm:
    - title: "AircraftSystem entity (ONT-E-03)"
    - properties.type: const "AircraftSystem"
    - parent_aircraft_model: $ref _meta uri (foreign key to AircraftModel)
    - ata_chapter: pattern ^ATA-[0-9]{2}$ with description pointing at ata-chapters.yaml
    - function: string minLength 20
    - criticality_level: enum [catastrophic, hazardous, major, minor, no_safety_effect]
    - required: [type, schema_version, i18n, parent_aircraft_model, ata_chapter, function, criticality_level]
  </action>
  <verify>
    <automated>for f in ontology/schemas/entity.aircraft-model.schema.json ontology/schemas/entity.aircraft-system.schema.json; do check-jsonschema --check-metaschema "$f" || exit 1; ! grep -q '"additionalProperties"' "$f" || exit 1; grep -q '"unevaluatedProperties": false' "$f" || exit 1; jq -e '.["$schema"] == "https://json-schema.org/draft/2020-12/schema"' "$f" || exit 1; done; jq -e '.properties.type.const == "AircraftModel"' ontology/schemas/entity.aircraft-model.schema.json &amp;&amp; jq -e '.properties.type.const == "AircraftSystem"' ontology/schemas/entity.aircraft-system.schema.json &amp;&amp; jq -e '.properties.ata_chapter.pattern == "^ATA-[0-9]{2}$"' ontology/schemas/entity.aircraft-system.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - Both files self-validate via `--check-metaschema`
    - Both files: zero `additionalProperties` strings (Pitfall #1)
    - Both files: `unevaluatedProperties: false` present
    - Both files: `$schema` declares Draft 2020-12 (Pitfall #9)
    - aircraft-model: `jq -e '.properties.type.const == "AircraftModel"'` exits 0
    - aircraft-system: `jq -e '.properties.type.const == "AircraftSystem"'` exits 0
    - aircraft-system: ATA chapter pattern present; description references `ata-chapters.yaml`
    - Both files: `jq -e '.allOf[0]["$ref"] == "entity.base.schema.json"'` exits 0
  </acceptance_criteria>
  <done>Both schemas exist, validate, compose entity.base, declare const types, and respect Pitfalls #1 + #9.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Author entity.subsystem.schema.json + entity.component.schema.json</name>
  <files>ontology/schemas/entity.subsystem.schema.json, ontology/schemas/entity.component.schema.json</files>
  <read_first>
    - ontology/schemas/entity.base.schema.json
    - ontology/schemas/entity.aircraft-system.schema.json (Task 1 sibling — same template)
    - .planning/REQUIREMENTS.md (ONT-E-04, ONT-E-05)
  </read_first>
  <action>
    **entity.subsystem.schema.json (ONT-E-04):**
    - title: "Subsystem entity (ONT-E-04)"
    - description: "A subsystem within an AircraftSystem, identified by ATA subchapter. Example: ATA-21-50 cabin pressurization is a subsystem of ATA-21 air conditioning. Composes entity.base.schema.json."
    - properties.type: const "Subsystem"
    - parent_system: $ref ../_meta.schema.json#/$defs/uri (URI to AircraftSystem)
    - ata_subchapter: type string, pattern `^ATA-[0-9]{2}-[0-9]{2}$`, description "ATA iSpec 2200 subchapter code (chapter-subchapter form). Validated against ontology/vocabularies/ata-chapters.yaml at runtime."
    - function: string minLength 20
    - required: [type, schema_version, i18n, parent_system, ata_subchapter, function]

    **entity.component.schema.json (ONT-E-05):**
    - title: "Component entity (ONT-E-05)"
    - description: "A discrete physical or functional component (e.g. brake disc, GPS unit, fuel pump). Composes entity.base.schema.json."
    - properties.type: const "Component"
    - manufacturer (optional string)
    - part_number (optional string — vendor part number)
    - mass (optional object: { value: number, unit: enum [kg, g, lb, slug] }) — leaf-level, unevaluatedProperties: false
    - dimensions (optional object: { length, width, height: number; unit: enum [mm, cm, m, in, ft] }) — leaf-level, unevaluatedProperties: false
    - criticality (optional enum [primary, secondary, advisory] — failure consequence)
    - ata_chapter (string, pattern `^ATA-[0-9]{2}$`, description references ata-chapters.yaml)
    - parent_subsystem (optional $ref ../_meta.schema.json#/$defs/uri — URI to Subsystem)
    - composition_material (optional URI — to Material entity per ADR-002)
    - required: [type, schema_version, i18n, ata_chapter]
  </action>
  <verify>
    <automated>for f in ontology/schemas/entity.subsystem.schema.json ontology/schemas/entity.component.schema.json; do check-jsonschema --check-metaschema "$f" || exit 1; ! grep -q '"additionalProperties"' "$f" || exit 1; grep -q '"unevaluatedProperties": false' "$f" || exit 1; done; jq -e '.properties.type.const == "Subsystem"' ontology/schemas/entity.subsystem.schema.json &amp;&amp; jq -e '.properties.type.const == "Component"' ontology/schemas/entity.component.schema.json &amp;&amp; jq -e '.properties.ata_subchapter.pattern == "^ATA-[0-9]{2}-[0-9]{2}$"' ontology/schemas/entity.subsystem.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - Both files self-validate via `--check-metaschema`
    - Pitfall #1 + #9 locks confirmed (no additionalProperties, $schema Draft 2020-12)
    - subsystem: `parent_system` references uri $def; ata_subchapter pattern matches `^ATA-[0-9]{2}-[0-9]{2}$`
    - component: `composition_material` field exists (forward reference to Material entity per ADR-002)
    - component: `mass` and `dimensions` are nested objects with their own `unevaluatedProperties: false`
    - Both: composition via `allOf` + `$ref entity.base.schema.json`
  </acceptance_criteria>
  <done>Subsystem and Component schemas validate, compose entity.base, embed ATA references, and Component links to Material via composition_material URI.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Author entity.document.schema.json with s1000d_dmc reserved field</name>
  <files>ontology/schemas/entity.document.schema.json</files>
  <read_first>
    - ontology/schemas/entity.base.schema.json
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Gap Resolution #2 — DMC regex, schema fragment; Pitfall #5 — reserved field discipline)
    - .planning/REQUIREMENTS.md (ONT-E-17)
  </read_first>
  <action>
    Create `ontology/schemas/entity.document.schema.json` per ONT-E-17. Structure:

    - title: "Document entity (ONT-E-17)"
    - description: "A source document (regulation, paper, accident report, manual, internal note). Documents are the resolution targets for `source.document_id` URIs (PROV-03, PROV-06). Composes entity.base.schema.json. Schema version: 0.1.0."
    - properties.type: const "Document"
    - properties (type-specific, per ONT-E-17 + DOC-02 fields):
      - title_text (string ≥1 char) — required (NOT i18n.label since i18n is from entity.base; this is the doc's actual title-of-record, in case it differs from the i18n display label)
      - doc_type (enum: `regulation / standard / paper / report / manual / accident_report / internal_note`) — required
      - language (enum: `zh / en / mixed`) — required
      - source_url (optional, format uri)
      - publication_date (optional, format date)
      - effective_date (optional, format date)
      - confidentiality (enum: `public / internal / restricted / itar_ear`) — required (DOC-04 gating field; Phase 4 enforces ingestion gating)
      - domain_tags (optional array of strings)
      - version (optional string — document's own version, distinct from entity-record version)
      - file_hash (optional string, pattern `^sha256:[a-f0-9]{64}$`)
      - page_count (optional integer minimum 1)
      - ata_chapter_tags (optional array, items pattern `^ATA-[0-9]{2}$`)
      - processed_by (optional string — tool used for processing, e.g. "ragflow-opendataloader-pdf")
      - s1000d_dmc — Use the EXACT schema fragment from 02-RESEARCH.md Gap Resolution #2:
        - type: string
        - pattern: `^DMC-[A-Z0-9]{2,14}-[A-Z0-9]{1,4}(-[0-9]{2,4}){4}-[0-9A-Z]{2,5}-[0-9A-Z]{4}-[ABCDT](_[0-9]{3}-[0-9]{2}_[a-zA-Z]{2}-[A-Z]{2})?$`
        - description MUST start with "**Reserved field —**" (Pitfall #5 marker phrase) and follow with: "S1000D Issue 6 Data Module Code (Issue 6.0 released 2024-09-01). Currently used only as opaque identifier for future round-tripping; structural decomposition into 7 components deferred to v0.2.0+. Format: DMC-<modelId>-<sysDiff>-<sns>-<disasm>-<infoCode>-<itemLoc>[_<learn>][_<lang>]. Example: DMC-S1000DBIKE-AAA-D00-00-00-00AA-00PA-D_004-00_EN-US. See ontology/mappings/s1000d-dmc-reserved.md for the full structural decomposition."
    - required: [type, schema_version, i18n, title_text, doc_type, language, confidentiality]
    - unevaluatedProperties: false
  </action>
  <verify>
    <automated>check-jsonschema --check-metaschema ontology/schemas/entity.document.schema.json &amp;&amp; jq -e '.properties.type.const == "Document"' ontology/schemas/entity.document.schema.json &amp;&amp; jq -r '.properties.s1000d_dmc.pattern' ontology/schemas/entity.document.schema.json | grep -q '^\^DMC-' &amp;&amp; jq -r '.properties.s1000d_dmc.description' ontology/schemas/entity.document.schema.json | grep -q 'Reserved field' &amp;&amp; jq -e '.properties.confidentiality.enum | contains(["public","internal","restricted","itar_ear"])' ontology/schemas/entity.document.schema.json &amp;&amp; ! grep -q '"additionalProperties"' ontology/schemas/entity.document.schema.json &amp;&amp; jq -e '.required | contains(["confidentiality"])' ontology/schemas/entity.document.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - File self-validates via `--check-metaschema`
    - Pitfall #1 + #9 locks confirmed
    - `properties.type.const == "Document"`
    - DMC regex pattern matches `^DMC-` prefix; full pattern matches the verified example `DMC-S1000DBIKE-AAA-D00-00-00-00AA-00PA-D_004-00_EN-US`
    - `s1000d_dmc.description` contains "Reserved field" marker phrase (Pitfall #5)
    - `s1000d_dmc.description` references `ontology/mappings/s1000d-dmc-reserved.md`
    - `confidentiality` is enum with exactly [public, internal, restricted, itar_ear] (DOC-04)
    - `confidentiality` is in required list (gating field)
    - `doc_type` enum has 7 values per DOC-02
    - composition: allOf $ref entity.base.schema.json
  </acceptance_criteria>
  <done>Document schema validates, encodes the s1000d_dmc reserved field per Gap-2 with Pitfall #5 marker, and ships the confidentiality enum that Phase 4 (DOC-04) ingestion gate uses.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Schema author → Phase 3 validator | If a leaf schema uses `additionalProperties: false`, Phase 3 validator silently rejects baseFields (Pitfall #1). |
| Document.s1000d_dmc → future S1000D consumer | If regex doesn't match real DMCs, future v0.2.0+ structural decomposition will fail. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-02-04-01 | Tampering | Pitfall #1 surfaces in any of 5 schemas | mitigate | Acceptance criteria check `! grep -q additionalProperties` per file |
| T-02-04-02 | Information Disclosure | Document.confidentiality missing → ITAR/EAR docs ingested by default | mitigate | confidentiality required + enum strict |
| T-02-04-03 | Tampering | s1000d_dmc regex too narrow → real DMCs fail | accept | RESEARCH.md flags this as MEDIUM-confidence; v0.2.0+ replaces with structural decomposition |
</threat_model>

<verification>
- All 5 schema files exist; each `check-jsonschema --check-metaschema` exits 0
- `pre-commit run --all-files` exits 0
- 5 atomic commits via gsd-tools
</verification>

<success_criteria>
- 5 entity schemas authored: AircraftModel, AircraftSystem, Subsystem, Component, Document
- Each composes entity.base.schema.json correctly
- Pitfall #1 + #9 locks verified on all 5
- Document.s1000d_dmc field reserves the S1000D Issue 6 DMC slot per Gap-2
- All 5 files committed (one commit per task — Tasks 1+2 each commit 2 files; Task 3 commits 1 file)
</success_criteria>

<output>
Create `.planning/phases/02-ontology-schema-v0-1-0/02-04-SUMMARY.md` with:
- 5 schema files listed
- Confirmation of Pitfall #1 + #9 across the batch
- Document.s1000d_dmc → mappings/s1000d-dmc-reserved.md cross-reference (Plan 10 deliverable)
- AircraftSystem/Subsystem ata_chapter → vocabularies/ata-chapters.yaml cross-reference (Plan 10 deliverable)
- Component.composition_material URI → Material entity (Plan 07 deliverable)
</output>

---
phase: 02-ontology-schema-v0-1-0
plan: 05
type: execute
wave: 3
depends_on: [02]
files_modified:
  - ontology/schemas/entity.requirement.schema.json
  - ontology/schemas/entity.regulation-clause.schema.json
  - ontology/schemas/entity.standard.schema.json
  - ontology/schemas/entity.procedure.schema.json
  - ontology/schemas/entity.maintenance-task.schema.json
  - ontology/schemas/entity.accident-case.schema.json
  - ontology/schemas/entity.expert-note.schema.json
autonomous: true
requirements:
  - ONT-E-06
  - ONT-E-07
  - ONT-E-08
  - ONT-E-09
  - ONT-E-11
  - ONT-E-16
  - ONT-E-18
must_haves:
  truths:
    - "All 7 entity schemas self-validate as Draft 2020-12"
    - "Each composes entity.base.schema.json via allOf + $ref + unevaluatedProperties: false"
    - "Each declares type with const matching its entity name"
    - "RegulationClause has jurisdiction enum + status enum + superseded_by URI per ONT-E-07"
    - "Pitfall #1 + #9 locks confirmed across all 7 schemas"
  artifacts:
    - path: "ontology/schemas/entity.requirement.schema.json"
      provides: "Requirement schema (ONT-E-06)"
    - path: "ontology/schemas/entity.regulation-clause.schema.json"
      provides: "RegulationClause schema (ONT-E-07) with jurisdiction + status + superseded_by"
    - path: "ontology/schemas/entity.standard.schema.json"
      provides: "Standard schema (ONT-E-08)"
    - path: "ontology/schemas/entity.procedure.schema.json"
      provides: "Procedure schema (ONT-E-09)"
    - path: "ontology/schemas/entity.maintenance-task.schema.json"
      provides: "MaintenanceTask schema (ONT-E-11)"
    - path: "ontology/schemas/entity.accident-case.schema.json"
      provides: "AccidentCase schema (ONT-E-16)"
    - path: "ontology/schemas/entity.expert-note.schema.json"
      provides: "ExpertNote schema (ONT-E-18) — canonical provenance/source/confidence example"
  key_links:
    - from: "all 7 entity-type schemas"
      to: "ontology/schemas/entity.base.schema.json"
      via: "allOf + $ref"
    - from: "entity.regulation-clause.schema.json"
      to: "ontology/vocabularies/jurisdictions.yaml (Plan 10)"
      via: "jurisdiction field description pointer"
---

<objective>
Author 7 baseline entity schemas covering the regulatory / procedural / lessons-learned family. Each composes `entity.base.schema.json`.

Runs PARALLEL with Plan 04 + Plan 06.
Output: 7 schema files in `ontology/schemas/`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/REQUIREMENTS.md
@.planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md
@.planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md
@.planning/phases/02-ontology-schema-v0-1-0/02-02-SUMMARY.md
@ontology/_meta.schema.json
@ontology/schemas/entity.base.schema.json

<interfaces>
<!-- Same template as Plan 04 — every leaf schema:
       allOf: [{ "$ref": "entity.base.schema.json" }]
       properties.type: { const: "<EntityName>" }
       unevaluatedProperties: false
       $schema: Draft 2020-12 -->
<!-- $ref to _meta.schema.json $defs from leaf schemas in ontology/schemas/ → "../_meta.schema.json#/$defs/<name>" -->
<!-- Per ADR-003 (Plan 03) D-12: ExpertNote uses i18n field for bilingual content; equivalent_to is NOT cross-language. -->
<!-- Per ADR-002 D-07/D-15: ExpertNote leverages entity.base's version_history[] for revisioning (NOT a has_revision relation). -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author entity.requirement.schema.json + entity.regulation-clause.schema.json + entity.standard.schema.json</name>
  <files>ontology/schemas/entity.requirement.schema.json, ontology/schemas/entity.regulation-clause.schema.json, ontology/schemas/entity.standard.schema.json</files>
  <read_first>
    - ontology/schemas/entity.base.schema.json
    - ontology/schemas/entity.aircraft-system.schema.json (Plan 04 sibling — same template)
    - .planning/REQUIREMENTS.md (ONT-E-06, ONT-E-07, ONT-E-08)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Pitfall #6 — supersession chain)
  </read_first>
  <action>
    **entity.requirement.schema.json (ONT-E-06):**
    - title: "Requirement entity (ONT-E-06)"
    - description: "An engineering requirement (functional / safety / performance). Composes entity.base.schema.json."
    - properties.type: const "Requirement"
    - requirement_text: string minLength 20 — required
    - jurisdiction: enum [FAA, EASA, CAAC, ICAO, Transport-Canada, CASA-AU, other] — optional (only set if regulatory)
    - parent_artifact: optional URI (URI to AircraftSystem / Component / Standard / etc — what this requirement is on)
    - requirement_type: enum [functional, safety, performance, environmental, interface, other] — required
    - traceability_id: optional string (cross-system identifier)
    - required: [type, schema_version, i18n, requirement_text, requirement_type]

    **entity.regulation-clause.schema.json (ONT-E-07):**
    - title: "RegulationClause entity (ONT-E-07)"
    - description: "A specific clause within a regulation (e.g. FAR §25.1309, EASA CS 25.1329, CAAC CCAR-25.1309). Includes supersession chain support (Pitfall #6). Composes entity.base.schema.json."
    - properties.type: const "RegulationClause"
    - jurisdiction: enum [FAA, EASA, CAAC, ICAO, Transport-Canada, CASA-AU, other] — required (description references ontology/vocabularies/jurisdictions.yaml)
    - document: $ref ../_meta.schema.json#/$defs/uri — required (URI to a Document entity that holds the regulation)
    - clause_id: string — required (e.g. "25.1309" or "AMC 25.1309")
    - effective_date: format date — required
    - status: enum [active, superseded, withdrawn, draft] — required (Pitfall #6: supersession chain)
    - superseded_by: optional $ref ../_meta.schema.json#/$defs/uri — URI to the active replacement RegulationClause (required if status == "superseded"; Phase 3 validator enforces conditional)
    - full_text_zh: optional string (i18n flat shape already covers labels; this is the canonical clause text in Chinese if available)
    - full_text_en: optional string (canonical English)
    - required: [type, schema_version, i18n, jurisdiction, document, clause_id, effective_date, status]

    **entity.standard.schema.json (ONT-E-08):**
    - title: "Standard entity (ONT-E-08)"
    - description: "An industry / military / consensus standard (e.g. RTCA DO-178C, MIL-STD-1553, SAE AS9100). Composes entity.base.schema.json."
    - properties.type: const "Standard"
    - issuing_body: string — required (e.g. "RTCA", "MIL", "SAE", "ISO")
    - standard_id: string — required (e.g. "DO-178C", "MIL-STD-1553B")
    - version: optional string (standard's own version, distinct from entity record version)
    - effective_date: optional format date
    - status: enum [active, superseded, withdrawn] — required
    - scope: optional string ≥20 chars (free-text scope description)
    - required: [type, schema_version, i18n, issuing_body, standard_id, status]
  </action>
  <verify>
    <automated>for f in ontology/schemas/entity.requirement.schema.json ontology/schemas/entity.regulation-clause.schema.json ontology/schemas/entity.standard.schema.json; do check-jsonschema --check-metaschema "$f" || exit 1; ! grep -q '"additionalProperties"' "$f" || exit 1; grep -q '"unevaluatedProperties": false' "$f" || exit 1; jq -e '.["$schema"] == "https://json-schema.org/draft/2020-12/schema"' "$f" || exit 1; done; jq -e '.properties.status.enum | contains(["superseded"])' ontology/schemas/entity.regulation-clause.schema.json &amp;&amp; jq -e '.properties.jurisdiction.enum | contains(["FAA","EASA","CAAC","ICAO"])' ontology/schemas/entity.regulation-clause.schema.json &amp;&amp; jq -e '.properties.type.const == "RegulationClause"' ontology/schemas/entity.regulation-clause.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - All 3 files self-validate via `--check-metaschema`
    - Pitfall #1 + #9 locks confirmed on all 3
    - Each composes entity.base via `allOf + $ref entity.base.schema.json`
    - regulation-clause has jurisdiction enum with at least FAA, EASA, CAAC, ICAO, other
    - regulation-clause has status enum including `superseded` (Pitfall #6 supersession chain)
    - regulation-clause description references `ontology/vocabularies/jurisdictions.yaml`
    - All 3 type.const values match (Requirement / RegulationClause / Standard)
  </acceptance_criteria>
  <done>3 regulatory-family schemas validate, support supersession chain, and reference jurisdictions vocabulary file (Plan 10 deliverable).</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Author entity.procedure.schema.json + entity.maintenance-task.schema.json</name>
  <files>ontology/schemas/entity.procedure.schema.json, ontology/schemas/entity.maintenance-task.schema.json</files>
  <read_first>
    - ontology/schemas/entity.base.schema.json
    - .planning/REQUIREMENTS.md (ONT-E-09, ONT-E-11)
  </read_first>
  <action>
    **entity.procedure.schema.json (ONT-E-09):**
    - title: "Procedure entity (ONT-E-09)"
    - description: "A documented procedure (operational / emergency / maintenance / certification). Composes entity.base.schema.json."
    - properties.type: const "Procedure"
    - procedure_type: enum [operational, emergency, maintenance, inspection, certification, repair, other] — required
    - target_system: optional URI (URI to AircraftSystem / Subsystem / Component)
    - steps: array, items: type object, properties: { step_number: integer ≥1, instruction: string ≥10 chars, hazards: optional array of strings, references: optional array of strings (URIs or doc refs) }; each step item unevaluatedProperties: false; minItems: 1 — required
    - prerequisites: optional array of strings
    - hazards: optional array of strings (procedure-level hazards distinct from per-step)
    - references: optional array of URIs (cites Document/Standard/RegulationClause)
    - required: [type, schema_version, i18n, procedure_type, steps]

    **entity.maintenance-task.schema.json (ONT-E-11):**
    - title: "MaintenanceTask entity (ONT-E-11)"
    - description: "A scheduled or condition-based maintenance task. Composes entity.base.schema.json."
    - properties.type: const "MaintenanceTask"
    - target_component: $ref ../_meta.schema.json#/$defs/uri — required (URI to Component / Subsystem / AircraftSystem)
    - ata_chapter: string, pattern `^ATA-[0-9]{2}$` — required (description references ata-chapters.yaml)
    - interval: object — required: { kind: enum [flight_hours, calendar_time, cycles, condition_based, on_condition], value: optional number, unit: optional string }; unevaluatedProperties: false
    - prerequisites: optional array of strings
    - tools_required: optional array of strings
    - certification_basis: optional URI (URI to RegulationClause or Standard)
    - estimated_duration_minutes: optional integer minimum 1
    - required: [type, schema_version, i18n, target_component, ata_chapter, interval]
  </action>
  <verify>
    <automated>for f in ontology/schemas/entity.procedure.schema.json ontology/schemas/entity.maintenance-task.schema.json; do check-jsonschema --check-metaschema "$f" || exit 1; ! grep -q '"additionalProperties"' "$f" || exit 1; grep -q '"unevaluatedProperties": false' "$f" || exit 1; done; jq -e '.properties.type.const == "Procedure"' ontology/schemas/entity.procedure.schema.json &amp;&amp; jq -e '.properties.type.const == "MaintenanceTask"' ontology/schemas/entity.maintenance-task.schema.json &amp;&amp; jq -e '.properties.steps.items.properties.step_number.minimum == 1' ontology/schemas/entity.procedure.schema.json &amp;&amp; jq -e '.properties.interval.properties.kind.enum | contains(["flight_hours","calendar_time"])' ontology/schemas/entity.maintenance-task.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - Both files self-validate via `--check-metaschema`
    - Pitfall #1 + #9 locks
    - procedure: steps array required, each item has step_number/instruction structure with unevaluatedProperties: false on item
    - maintenance-task: interval object with kind enum [flight_hours, calendar_time, cycles, condition_based, on_condition]
    - maintenance-task: ata_chapter pattern + description pointer
    - Both type.const values match
  </acceptance_criteria>
  <done>Procedure + MaintenanceTask schemas validate; structured nested objects use unevaluatedProperties: false at every level.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Author entity.accident-case.schema.json + entity.expert-note.schema.json</name>
  <files>ontology/schemas/entity.accident-case.schema.json, ontology/schemas/entity.expert-note.schema.json</files>
  <read_first>
    - ontology/schemas/entity.base.schema.json
    - .planning/REQUIREMENTS.md (ONT-E-16, ONT-E-18)
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-07/D-15 — version_history field for ExpertNote)
  </read_first>
  <action>
    **entity.accident-case.schema.json (ONT-E-16):**
    - title: "AccidentCase entity (ONT-E-16)"
    - description: "A documented accident or incident case. Composes entity.base.schema.json."
    - properties.type: const "AccidentCase"
    - date: format date — required (date of accident)
    - location: string — required (geographic, not coordinates — free text)
    - aircraft_model_ref: $ref ../_meta.schema.json#/$defs/uri — optional (URI to AircraftModel; sometimes unknown)
    - phase_of_flight: enum [taxi, takeoff, climb, cruise, approach, landing, missed_approach, emergency, ground, unknown] — required
    - causal_factors: array of strings (≥1 item) — required (free-text causal factor list)
    - contributing_factors: optional array of strings
    - lessons_learned: string ≥20 chars — required (the audit-relevant takeaway)
    - official_report_url: optional, format uri
    - severity: optional enum [accident, serious_incident, incident, occurrence]
    - required: [type, schema_version, i18n, date, location, phase_of_flight, causal_factors, lessons_learned]

    **entity.expert-note.schema.json (ONT-E-18):**
    - title: "ExpertNote entity (ONT-E-18) — canonical provenance/source/confidence example"
    - description: "A free-form expert note that demonstrates the full provenance + source + confidence pattern (cited as the worked example in docs/README.md AI 接力开发指南). Bilingual content goes via i18n field per ADR-003 / D-12 (NOT a separate equivalent_to relation). Revisions go via entity.base.version_history[] per ADR-003 / D-07 (NOT a has_revision relation). Composes entity.base.schema.json."
    - properties.type: const "ExpertNote"
    - author: $ref ../_meta.schema.json#/$defs/uri — required (URI to Person; distinct from provenance.actor — author is the note's intellectual author, provenance.actor is whoever entered the data into the KB)
    - topic: string ≥1 char — required (free-text topic identifier; example "fuel-system-corrosion-coastal-environment")
    - content_md: string ≥40 chars — required (Markdown body, English by default; bilingual via i18n.full_text)
    - related_entities: optional array of $ref ../_meta.schema.json#/$defs/uri (cross-references to AircraftSystem / Component / RegulationClause / etc)
    - supersedes_note: optional $ref ../_meta.schema.json#/$defs/uri — URI to a previous ExpertNote that this one replaces (used when the note evolves but the entity ID changes; for in-place revisions use version_history)
    - required: [type, schema_version, i18n, author, topic, content_md]
  </action>
  <verify>
    <automated>for f in ontology/schemas/entity.accident-case.schema.json ontology/schemas/entity.expert-note.schema.json; do check-jsonschema --check-metaschema "$f" || exit 1; ! grep -q '"additionalProperties"' "$f" || exit 1; grep -q '"unevaluatedProperties": false' "$f" || exit 1; done; jq -e '.properties.type.const == "AccidentCase"' ontology/schemas/entity.accident-case.schema.json &amp;&amp; jq -e '.properties.type.const == "ExpertNote"' ontology/schemas/entity.expert-note.schema.json &amp;&amp; jq -e '.properties.phase_of_flight.enum | contains(["takeoff","cruise","landing","emergency"])' ontology/schemas/entity.accident-case.schema.json &amp;&amp; grep -q 'version_history' ontology/schemas/entity.expert-note.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - Both files self-validate via `--check-metaschema`
    - Pitfall #1 + #9 locks
    - accident-case: phase_of_flight enum includes takeoff/cruise/landing/emergency at minimum
    - accident-case: lessons_learned field is required and string-typed (the audit takeaway)
    - expert-note: description references ADR-003 / D-12 (i18n carries cross-language) AND D-07 (version_history carries revisioning)
    - expert-note: author URI required (distinct from provenance.actor — verified by description text)
    - Both type.const values match
  </acceptance_criteria>
  <done>AccidentCase + ExpertNote schemas validate; ExpertNote description explicitly maps to ADR-003 boundary decisions for i18n and version_history.</done>
</task>

</tasks>

<threat_model>
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-02-05-01 | Tampering | Pitfall #1 in any of 7 schemas | mitigate | Acceptance criteria check `! grep -q additionalProperties` per file |
| T-02-05-02 | Repudiation | RegulationClause without supersession chain support → outdated regulations cited as active | mitigate | status enum includes `superseded`; superseded_by URI optional but conditionally required by Phase 3 validator |
| T-02-05-03 | Information Disclosure | ExpertNote description doesn't reference ADR-003 → future maintainer adds equivalent_to relation for bilingual pairs | mitigate | description text mandates the cross-reference |
</threat_model>

<verification>
- All 7 files exist; each `check-jsonschema --check-metaschema` exits 0
- `pre-commit run --all-files` exits 0
- 3 atomic commits via gsd-tools (one per task; Tasks 1+2+3 each commit a batch)
</verification>

<success_criteria>
- 7 entity schemas: Requirement, RegulationClause, Standard, Procedure, MaintenanceTask, AccidentCase, ExpertNote
- Each composes entity.base.schema.json
- RegulationClause supersession chain support (Pitfall #6)
- ExpertNote description encodes ADR-003 boundary decisions
- Pitfall #1 + #9 locks across batch
</success_criteria>

<output>
Create `.planning/phases/02-ontology-schema-v0-1-0/02-05-SUMMARY.md` with:
- 7 schemas listed
- Pitfall #1 + #9 confirmation
- RegulationClause → jurisdictions.yaml cross-reference (Plan 10)
- ExpertNote → DEMO-04 (Phase 4) canonical example reference
</output>

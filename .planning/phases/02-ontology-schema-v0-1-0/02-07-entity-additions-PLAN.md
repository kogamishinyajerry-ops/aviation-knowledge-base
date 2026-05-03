---
phase: 02-ontology-schema-v0-1-0
plan: 07
type: execute
wave: 4
depends_on: [02, 04, 05, 06]
files_modified:
  - ontology/schemas/entity.material.schema.json
  - ontology/schemas/entity.test-case.schema.json
  - ontology/schemas/entity.test-report.schema.json
  - ontology/schemas/entity.person.schema.json
  - ontology/schemas/entity.organization.schema.json
autonomous: true
requirements:
  - ONT-E-19
  - ONT-E-20
  - ONT-E-21
  - ONT-E-22
must_haves:
  truths:
    - "All 5 ADR-002 added entity schemas self-validate as Draft 2020-12"
    - "Each composes entity.base.schema.json"
    - "Pitfall #1 + #9 locks confirmed"
    - "Person + Organization shapes match ADR-002 6-field minimum (Gap Resolution #6)"
    - "ONT-E-21 (Configuration / EffectivityRange) is satisfied by ADR-002 deferral — no schema file ships"
  artifacts:
    - path: "ontology/schemas/entity.material.schema.json"
      provides: "Material schema (ONT-E-19, D-01)"
    - path: "ontology/schemas/entity.test-case.schema.json"
      provides: "TestCase schema (ONT-E-20, D-02 first half)"
    - path: "ontology/schemas/entity.test-report.schema.json"
      provides: "TestReport schema (ONT-E-20, D-02 second half) with test_case_ref FK to TestCase"
    - path: "ontology/schemas/entity.person.schema.json"
      provides: "Person schema (ONT-E-22, D-04 first half) — resolution target for provenance.actor / reviewer URIs"
    - path: "ontology/schemas/entity.organization.schema.json"
      provides: "Organization schema (ONT-E-22, D-04 second half)"
  key_links:
    - from: "entity.test-report.schema.json"
      to: "entity.test-case.schema.json"
      via: "test_case_ref URI (foreign key)"
    - from: "all _meta.schema.json#/$defs/provenance.actor and reviewer URIs"
      to: "entity.person.schema.json + entity.organization.schema.json"
      via: "URI resolution (Phase 3 validator confirms entity exists)"
---

<objective>
Author the 5 ADR-002 added entity schemas (Material, TestCase, TestReport, Person, Organization). ONT-E-21 (Configuration / EffectivityRange) is satisfied by ADR-002's deferral decision — no schema file ships.

This plan runs in Wave 4, AFTER Plans 04+05+06 complete the baseline schemas. Reason: ADR-002 should be reviewed against baseline shapes for consistency before adding additions.

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
@.planning/decisions/ADR-002-entity-additions.md
@.planning/phases/02-ontology-schema-v0-1-0/02-04-SUMMARY.md
@.planning/phases/02-ontology-schema-v0-1-0/02-05-SUMMARY.md
@.planning/phases/02-ontology-schema-v0-1-0/02-06-SUMMARY.md
@ontology/_meta.schema.json
@ontology/schemas/entity.base.schema.json

<interfaces>
<!-- ADR-002 (.planning/decisions/ADR-002-entity-additions.md, Plan 02 deliverable) holds the EXACT field tables for Material, TestCase, TestReport, Person, Organization. Use those tables verbatim. -->
<!-- Person.id format: aviationkb://person/<slug>@<version> -->
<!-- Organization.id format: aviationkb://organization/<slug>@<version> -->
<!-- TestReport.test_case_ref points at TestCase via internal URI -->
<!-- Material.composition_material is the field referenced by entity.component.schema.json (Plan 04) -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author entity.material.schema.json + entity.test-case.schema.json + entity.test-report.schema.json</name>
  <files>ontology/schemas/entity.material.schema.json, ontology/schemas/entity.test-case.schema.json, ontology/schemas/entity.test-report.schema.json</files>
  <read_first>
    - ontology/schemas/entity.base.schema.json
    - .planning/decisions/ADR-002-entity-additions.md (Material, TestCase, TestReport field tables)
    - .planning/REQUIREMENTS.md (ONT-E-19, ONT-E-20)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Open Question #1 — Material allowables; Open Question #2 — TestReport linking via FK not relation)
  </read_first>
  <action>
    **entity.material.schema.json (ONT-E-19, D-01):**
    - title: "Material entity (ONT-E-19, D-01)"
    - description: "An aerospace material (alloy / composite / polymer / ceramic / coating). Composes entity.base.schema.json. Per ADR-002, design_allowables_reference is free-text in v0.1.0; structured cites relation lands in v0.2.0+."
    - properties.type: const "Material"
    - name: string ≥1 char — required (e.g. "Ti-6Al-4V", "AS4/3501-6")
    - family: enum [metal_alloy, composite, polymer, ceramic, coating, other] — required
    - nominal_composition: optional string (free text in v0.1.0 per ADR-002)
    - design_allowables_reference: optional string (free text; e.g. "MIL-HDBK-5J Table 5.4.1.0(a)")
    - heat_treatment_or_layup: optional string
    - typical_applications: optional array of strings
    - required: [type, schema_version, i18n, name, family]

    **entity.test-case.schema.json (ONT-E-20, D-02):**
    - title: "TestCase entity (ONT-E-20, D-02)"
    - description: "A test plan (qualification / verification / validation / acceptance / development). Composes entity.base.schema.json. Per ADR-002, DO-178C / DO-254 specific criticality fields deferred to v0.2.0+."
    - properties.type: const "TestCase"
    - test_objective: string ≥20 chars — required
    - target: $ref ../_meta.schema.json#/$defs/uri — required (URI to Component / AircraftSystem / Subsystem — what's being tested)
    - test_type: enum [qualification, verification, validation, acceptance, development, other] — required
    - environmental_conditions: optional string (DO-160-shaped in v0.2.0+)
    - acceptance_criteria: string ≥20 chars — required
    - prerequisites: optional array of strings
    - required: [type, schema_version, i18n, test_objective, target, test_type, acceptance_criteria]

    **entity.test-report.schema.json (ONT-E-20, D-02):**
    - title: "TestReport entity (ONT-E-20, D-02)"
    - description: "A test report (outcome of a TestCase execution). Linked to TestCase via test_case_ref foreign key (NOT a relation per ADR-002 / Open Question #2). Composes entity.base.schema.json."
    - properties.type: const "TestReport"
    - test_case_ref: $ref ../_meta.schema.json#/$defs/uri — required (URI to TestCase entity; Phase 3 validator confirms FK exists)
    - executed_at: format date — required
    - executed_by: $ref ../_meta.schema.json#/$defs/uri — required (URI to Person or Organization)
    - outcome: enum [pass, fail, partial, inconclusive] — required
    - results_summary: string ≥20 chars — required
    - artifacts_url: optional, format uri (link to test data, photos, traces)
    - reviewers: optional array of $ref ../_meta.schema.json#/$defs/uri (Person URIs)
    - required: [type, schema_version, i18n, test_case_ref, executed_at, executed_by, outcome, results_summary]
  </action>
  <verify>
    <automated>for f in ontology/schemas/entity.material.schema.json ontology/schemas/entity.test-case.schema.json ontology/schemas/entity.test-report.schema.json; do check-jsonschema --check-metaschema "$f" || exit 1; ! grep -q '"additionalProperties"' "$f" || exit 1; grep -q '"unevaluatedProperties": false' "$f" || exit 1; done; jq -e '.properties.type.const == "Material"' ontology/schemas/entity.material.schema.json &amp;&amp; jq -e '.properties.type.const == "TestCase"' ontology/schemas/entity.test-case.schema.json &amp;&amp; jq -e '.properties.type.const == "TestReport"' ontology/schemas/entity.test-report.schema.json &amp;&amp; jq -e '.properties.family.enum | contains(["metal_alloy","composite"])' ontology/schemas/entity.material.schema.json &amp;&amp; jq -e '.properties.outcome.enum | contains(["pass","fail","partial","inconclusive"])' ontology/schemas/entity.test-report.schema.json &amp;&amp; jq -e '.required | contains(["test_case_ref"])' ontology/schemas/entity.test-report.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - All 3 files self-validate; Pitfall #1 + #9 locks
    - Material.family enum has at least 6 values (metal_alloy, composite, polymer, ceramic, coating, other)
    - TestCase.test_type enum: qualification, verification, validation, acceptance, development, other
    - TestReport.outcome enum: pass, fail, partial, inconclusive
    - TestReport.test_case_ref is required (the FK to TestCase per ADR-002 Open Question #2)
    - All 3 type.const values match
    - Composition via allOf + $ref entity.base.schema.json
  </acceptance_criteria>
  <done>Material + TestCase + TestReport schemas validate. TestReport FK to TestCase is required and shape-matches ADR-002 / Open Question #2 decision.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Author entity.person.schema.json + entity.organization.schema.json</name>
  <files>ontology/schemas/entity.person.schema.json, ontology/schemas/entity.organization.schema.json</files>
  <read_first>
    - ontology/schemas/entity.base.schema.json
    - .planning/decisions/ADR-002-entity-additions.md (Person, Organization field tables)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Gap Resolution #6 — 6-field minimum)
    - .planning/REQUIREMENTS.md (ONT-E-22)
    - ontology/_meta.schema.json (provenance.actor / reviewer URI shape — Person/Org are the resolution targets)
  </read_first>
  <action>
    **entity.person.schema.json (ONT-E-22, D-04):**
    - title: "Person entity (ONT-E-22, D-04) — resolution target for provenance.actor / provenance.reviewer URIs"
    - description: "A natural person (engineer, reviewer, expert, inspector). MANDATORY in v0.1.0 because provenance.actor and provenance.reviewer (defined in _meta.schema.json) require a resolvable URI target — without this schema, those fields degrade to free text and the H-Darrieus lock weakens. Composes entity.base.schema.json. Per ADR-002 / Gap Resolution #6, 6 fields minimum drawn from W3C PROV-O / schema.org / FOAF intersection. ORCID/ROR live resolution deferred to v0.2.0+."
    - properties.type: const "Person"
    - name: string ≥1 char — required
    - affiliation: optional $ref ../_meta.schema.json#/$defs/uri (URI to Organization)
    - role: optional enum [author, reviewer, expert, inspector, engineer, other]
    - external_ids: optional object: { orcid: optional string pattern `^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$`, email: optional string format email }; unevaluatedProperties: false
    - required: [type, schema_version, i18n, name]

    **entity.organization.schema.json (ONT-E-22, D-04):**
    - title: "Organization entity (ONT-E-22, D-04)"
    - description: "An organization (regulator, manufacturer, operator, research institute, standards body, consultancy). Composes entity.base.schema.json."
    - properties.type: const "Organization"
    - name: string ≥1 char — required
    - org_type: enum [regulator, manufacturer, operator, research_institute, standards_body, consultancy, other] — required
    - jurisdiction: optional enum [FAA, EASA, CAAC, ICAO, Transport-Canada, CASA-AU, other] (aligns with RegulationClause.jurisdiction; description references ontology/vocabularies/jurisdictions.yaml)
    - external_ids: optional object: { ror: optional string pattern `^https?://ror\.org/[a-z0-9]{9}$`, lei: optional string pattern `^[A-Z0-9]{20}$` }; unevaluatedProperties: false
    - required: [type, schema_version, i18n, name, org_type]
  </action>
  <verify>
    <automated>for f in ontology/schemas/entity.person.schema.json ontology/schemas/entity.organization.schema.json; do check-jsonschema --check-metaschema "$f" || exit 1; ! grep -q '"additionalProperties"' "$f" || exit 1; grep -q '"unevaluatedProperties": false' "$f" || exit 1; done; jq -e '.properties.type.const == "Person"' ontology/schemas/entity.person.schema.json &amp;&amp; jq -e '.properties.type.const == "Organization"' ontology/schemas/entity.organization.schema.json &amp;&amp; jq -e '.properties.role.enum | contains(["author","reviewer","expert"])' ontology/schemas/entity.person.schema.json &amp;&amp; jq -e '.properties.org_type.enum | contains(["regulator","manufacturer"])' ontology/schemas/entity.organization.schema.json &amp;&amp; jq -r '.properties.external_ids.properties.orcid.pattern' ontology/schemas/entity.person.schema.json | grep -q '\\d{4}-\\d{4}'</automated>
  </verify>
  <acceptance_criteria>
    - Both files self-validate; Pitfall #1 + #9 locks
    - Person.role enum includes author, reviewer, expert, inspector, engineer, other (6 values)
    - Organization.org_type enum: regulator, manufacturer, operator, research_institute, standards_body, consultancy, other (7 values)
    - Organization.jurisdiction enum aligns with RegulationClause.jurisdiction (Plan 05) — same domain
    - Person.external_ids.orcid pattern validates ORCID format `\d{4}-\d{4}-\d{4}-\d{3}[\dX]`
    - Organization.external_ids.ror pattern validates ROR format `https?://ror.org/[a-z0-9]{9}`
    - Both: `name` field required (Gap Resolution #6 minimum)
    - Both type.const values match
  </acceptance_criteria>
  <done>Person + Organization schemas validate; provide URI resolution targets for provenance.actor / provenance.reviewer; aligned with RegulationClause.jurisdiction enum. Gap Resolution #6 6-field minimum honored.</done>
</task>

</tasks>

<threat_model>
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-02-07-01 | Repudiation | Person/Organization absent → provenance.actor degrades to free text → H-Darrieus lock weakens | mitigate | Both schemas mandatory in v0.1.0 (D-04); plan ships them |
| T-02-07-02 | Tampering | Pitfall #1 in any of 5 schemas | mitigate | Per-file `! grep -q additionalProperties` |
| T-02-07-03 | Spoofing | TestReport without FK to TestCase → fabricated test outcomes can dangle | mitigate | test_case_ref required; Phase 3 broken-ref check |
</threat_model>

<verification>
- All 5 files exist; `--check-metaschema` exits 0 each
- `pre-commit run --all-files` exits 0
- 2 atomic commits via gsd-tools
- ONT-E-21 satisfied by ADR-002 (no schema file)
</verification>

<success_criteria>
- 5 schemas: Material, TestCase, TestReport, Person, Organization
- ONT-E-21 explicitly satisfied by ADR-002 deferral (no schema file)
- Each composes entity.base.schema.json
- Person + Organization shapes match Gap Resolution #6
- TestReport FK to TestCase per ADR-002 Open Question #2
- Pitfall #1 + #9 locks
</success_criteria>

<output>
Create `.planning/phases/02-ontology-schema-v0-1-0/02-07-SUMMARY.md` with:
- 5 schemas listed; ONT-E-21 ADR-002-deferred status
- Confirmation Person/Organization URI shapes resolve provenance.actor / reviewer references
- Component.composition_material → Material URI cross-reference (Plan 04 deliverable)
- Pitfall #1 + #9 confirmation
</output>

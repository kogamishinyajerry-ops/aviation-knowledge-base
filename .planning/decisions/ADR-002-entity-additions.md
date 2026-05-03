# ADR-002 — Entity Additions for v0.1.0 (Material, TestCase/TestReport, Configuration deferred, Person/Organization)

Status: ACCEPTED (FINALIZED in Plan 02-07 after baseline schemas authored in Plans 04+05+06)
Date: 2026-05-03 (initial draft) / 2026-05-03 (finalization)
Deciders: user (CONTEXT.md interactive discuss, 2026-05-03)
Implements: D-01, D-02, D-03, D-04, ONT-E-19, ONT-E-20, ONT-E-21, ONT-E-22

> AI 接力开发指南: This ADR resolves the four research-recommended entity additions evaluated in REQUIREMENTS.md ONT-E-19..22. v0.1.0 ships 17 baseline + 5 added entity schema files (Material, TestCase, TestReport, Person, Organization — TestCase + TestReport are two schemas; Person + Organization are two schemas). Configuration / EffectivityRange (ONT-E-21) is DEFERRED to v0.2.0 — NO schema file ships in v0.1.0; THIS ADR is the satisfaction record for ONT-E-21. Read this ADR before authoring or modifying any of: entity.material.schema.json, entity.test-case.schema.json, entity.test-report.schema.json, entity.person.schema.json, entity.organization.schema.json. Field tables below are FINAL and match what shipped in Plan 02-07.

## Context

REQUIREMENTS.md ONT-E-19..22 listed four research-recommended entity additions to evaluate during Phase 2. The decision matters because:

- (a) `provenance.actor` and `provenance.reviewer` are URI fields — without Person/Organization schemas they degrade to free text and the H-Darrieus REJECT lock weakens (PROJECT.md Core Value);
- (b) `Component.composition_material` referencing materials needs a structured target or it becomes free-text "aerospace-grade aluminum" descriptions that defeat traceability;
- (c) `Requirement.verified_by` currently can only point at Procedure, which is too narrow for DO-160/DO-178C/DO-254 audit trails — TestCase + TestReport widen the verification target set;
- (d) Configuration / EffectivityRange (serial-number applicability) is real but rare in v0.1.0 demo corpus; demo data must drive the schema, not vice versa.

This ADR was first drafted in Plan 02-02 (Wave 2) when entity.base.schema.json shipped. It was reopened and FINALIZED in Plan 02-07 (Wave 4) after the baseline entity schemas (Plans 04, 05, 06) shipped, so the field shapes for the additions could be reviewed against baseline-schema conventions for consistency. No field-table changes were required during finalization; the original Plan 02-02 draft survived intact, with this ADR now stamped FINALIZED.

## Decision

| REQ-ID   | Entity                              | Decision                | Schema file(s) shipped (v0.1.0)                                                       |
|----------|-------------------------------------|-------------------------|----------------------------------------------------------------------------------------|
| ONT-E-19 | **Material**                        | ACCEPT (D-01)           | `ontology/schemas/entity.material.schema.json`                                         |
| ONT-E-20 | **TestCase + TestReport**           | ACCEPT both (D-02)      | `ontology/schemas/entity.test-case.schema.json` + `entity.test-report.schema.json`     |
| ONT-E-21 | **Configuration / EffectivityRange**| DEFER to v0.2.0 (D-03)  | NONE — THIS ADR satisfies ONT-E-21                                                     |
| ONT-E-22 | **Person + Organization**           | ACCEPT both, MANDATORY (D-04) | `ontology/schemas/entity.person.schema.json` + `entity.organization.schema.json` |

Net entity schema count v0.1.0 = 17 baseline + 5 added = **22 entity schema files**. ONT-E-21 deferred so no schema file ships for it.

## Material schema scope (FINAL — matches shipped entity.material.schema.json)

Composes `entity.base.schema.json` via `allOf` + `$ref` + `unevaluatedProperties: false`. Pitfall #1 + #9 locked.

| Field                             | Type        | Required | Notes                                                                                                              |
|-----------------------------------|-------------|----------|--------------------------------------------------------------------------------------------------------------------|
| `type`                            | const       | yes      | `"Material"`                                                                                                       |
| `name`                            | string ≥1   | yes      | E.g. `Ti-6Al-4V`, `AS4/3501-6`                                                                                     |
| `family`                          | enum        | yes      | `metal_alloy / composite / polymer / ceramic / coating / other` (6 values)                                         |
| `nominal_composition`             | string      | no       | Free-text in v0.1.0 (RESEARCH Open Q1); structured composition lists deferred to v0.2.0+                            |
| `design_allowables_reference`     | string      | no       | Free-text in v0.1.0; e.g. `MIL-HDBK-5J Table 5.4.1.0(a)`. Upgrade to `cites` relation in v0.2.0+                    |
| `heat_treatment_or_layup`         | string      | no       | E.g. `Solution treated and aged (STA)`, `[0/45/90/-45]_2s symmetric`                                                |
| `typical_applications`            | array<string> | no     | Free-form list                                                                                                     |
| (inherited via base)              | —           | yes      | `id`, `schema_version`, `i18n.label`, `provenance`, `confidence`, `source`                                          |

**DO NOT model in v0.1.0:** structured MIL-HDBK-5/MMPDS allowable values, composite layup as a list (single string), test data references (those go via `cites` relation when needed).

## TestCase + TestReport schema scope (FINAL — matches shipped schemas)

Two separate entity types; foreign-key relationship NOT a relation (RESEARCH Open Q2 — defer relation upgrade to v0.2.0+ if uniformity becomes valuable).

### TestCase fields

| Field                       | Type            | Required | Notes                                                                                |
|-----------------------------|-----------------|----------|--------------------------------------------------------------------------------------|
| `type`                      | const           | yes      | `"TestCase"`                                                                         |
| `test_objective`            | string ≥20      | yes      | What the test demonstrates                                                           |
| `target`                    | URI ($ref)      | yes      | URI to Component / AircraftSystem / Subsystem under test                             |
| `test_type`                 | enum            | yes      | `qualification / verification / validation / acceptance / development / other`       |
| `environmental_conditions`  | string          | no       | Free-text; DO-160-shaped structured object deferred to v0.2.0+                       |
| `acceptance_criteria`       | string ≥20      | yes      | Pass/fail criteria                                                                   |
| `prerequisites`             | array<string>   | no       | Conditions / prior tests                                                             |
| (inherited via base)        | —               | yes      | `id`, `schema_version`, `i18n.label`, `provenance`, `confidence`, `source`           |

### TestReport fields

| Field                | Type           | Required | Notes                                                                                            |
|----------------------|----------------|----------|--------------------------------------------------------------------------------------------------|
| `type`               | const          | yes      | `"TestReport"`                                                                                   |
| `test_case_ref`      | URI ($ref)     | yes      | **FOREIGN KEY** to TestCase entity (RESEARCH Open Q2; T-02-07-03 mitigation; Phase 3 FK check)    |
| `executed_at`        | string format date | yes  | ISO 8601 date                                                                                    |
| `executed_by`        | URI ($ref)     | yes      | Person OR Organization URI                                                                       |
| `outcome`            | enum           | yes      | `pass / fail / partial / inconclusive`                                                           |
| `results_summary`    | string ≥20     | yes      | Human-readable outcome summary                                                                   |
| `artifacts_url`      | string format uri | no    | Link to test data / photos / traces                                                              |
| `reviewers`          | array<URI>     | no       | Person URIs who reviewed the underlying test (distinct from provenance.reviewer of the YAML)     |
| (inherited via base) | —              | yes      | `id`, `schema_version`, `i18n.label`, `provenance`, `confidence`, `source`                       |

**DO NOT model in v0.1.0:** DO-178C / DO-254 specific criticality fields (test category, criticality level, evidence type) — deferred to v0.2.0+ per CONTEXT.md Deferred Ideas. Detailed step-by-step trace also deferred.

## Configuration / EffectivityRange — DEFERRED to v0.2.0

REQ-ID ONT-E-21 is satisfied by THIS ADR documenting the deferral. **NO schema file lands in v0.1.0.**

**Rationale:** v0.1.0 demo data does not yet exercise applicability-by-serial-number patterns. FEATURES.md flags Configuration as v1.x. Until then, `applicability_scope: free_text` on RegulationClause / Procedure suffices.

**Trigger to revisit:** When AD/SB demo data lands (Phase 4 expansion or v0.2.0) and needs serial-number applicability scope.

**Path forward when activated in v0.2.0:** Add `entity.configuration.schema.json` and `entity.effectivity-range.schema.json`. A relation `applicable_to_configuration` may also be needed. Migration script `migrations/0_1_0_to_0_2_0.py` ports any free-text applicability strings on RegulationClause / Procedure into structured Configuration references.

## Person + Organization schema scope (FINAL — matches shipped schemas)

Per RESEARCH.md Gap Resolution #6, minimum 6 fields each drawn from W3C PROV-O / schema.org / FOAF intersection. Both MANDATORY in v0.1.0 because they are the URI resolution targets for `provenance.actor` and `provenance.reviewer` — without them the H-Darrieus REJECT lock degrades to free-text matching (ADR-005).

### Person fields

| Field                | Type           | Required | Notes                                                                                |
|----------------------|----------------|----------|--------------------------------------------------------------------------------------|
| `type`               | const          | yes      | `"Person"`                                                                           |
| `name`               | string ≥1      | yes      | Canonical Latin/romanized name; bilingual variants in `i18n.label`                   |
| `affiliation`        | URI ($ref)     | no       | URI to Organization                                                                  |
| `role`               | enum           | no       | `author / reviewer / expert / inspector / engineer / other` (6 values)               |
| `external_ids`       | object         | no       | `{ orcid?: pattern \d{4}-\d{4}-\d{4}-\d{3}[\dX], email?: format email }`              |
| (inherited via base) | —              | yes      | `id`, `schema_version`, `i18n.label`, `provenance`, `confidence`, `source`           |

URI form: `aviationkb://person/<slug>@<version>`.

### Organization fields

| Field                | Type           | Required | Notes                                                                                                            |
|----------------------|----------------|----------|------------------------------------------------------------------------------------------------------------------|
| `type`               | const          | yes      | `"Organization"`                                                                                                 |
| `name`               | string ≥1      | yes      | Canonical Latin display name                                                                                     |
| `org_type`           | enum           | yes      | `regulator / manufacturer / operator / research_institute / standards_body / consultancy / other` (7 values)     |
| `jurisdiction`       | enum           | no       | `FAA / EASA / CAAC / ICAO / Transport-Canada / CASA-AU / other` — aligned with RegulationClause.jurisdiction      |
| `external_ids`       | object         | no       | `{ ror?: pattern https?://ror.org/[a-z0-9]{9}, lei?: pattern [A-Z0-9]{20} }`                                      |
| (inherited via base) | —              | yes      | `id`, `schema_version`, `i18n.label`, `provenance`, `confidence`, `source`                                       |

URI form: `aviationkb://organization/<slug>@<version>`.

**Deferred to v0.2.0+:**
- ORCID / ROR / LEI live resolution (Phase 3 validator only format-checks pattern in v0.1.0; live fetch later)
- `prov:qualifiedAttribution` partial-authorship audit trail
- ITAR / EAR person classification (out of scope per PROJECT.md)
- Hierarchical organization structure (parent_org / divisions)
- Multi-affiliation per Person via a future `affiliated_with` relation

## Rationale (entity-by-entity longer form)

See 02-CONTEXT.md D-01..D-04 for the original locked-in rationales. Recap:

- **Material:** refusing now means `Component.composition_material` becomes free-text and gets rebuilt later when CFD validation cases need material properties traceable. Material schema is cheap; refactor cost later is high. The free-text `design_allowables_reference` is a deliberate v0.1.0 scoping choice — full structured allowables in v0.1.0 would either (a) require a half-baked numeric model that gets discarded, or (b) block the schema set on a multi-week MIL-HDBK-5 modeling effort. The reference field gives an audit trail without the modeling cost.

- **TestCase + TestReport:** separating plan and outcome lets `Requirement.verified_by` point at either; matches DO-160 audit trail practice. One entity (`Test`) collapsing both was considered and rejected — outcome data lifecycle differs from plan data (a TestCase is authored once and revised; a TestReport is created per execution and is immutable after sign-off). The FK choice over a relation (RESEARCH Open Q2) is also deliberate: TestCase ↔ TestReport is a tight 1:N coupling that doesn't benefit from the relation-table generality and would clutter triple exports.

- **Configuration / EffectivityRange:** serial-number applicability is real but rare in v0.1.0 demo corpus; demo data must drive the schema, not vice versa. Adding it speculatively risks the Pitfall #4 trap (schemas without instances rot).

- **Person / Organization:** D-04 is mandatory because the URI shape `aviationkb://person/<slug>@<version>` is already the ID format for provenance.actor (locked by ADR-005). Without these schemas, the URI dangles and the Phase 3 FK check has nothing to resolve against. The 6-field minimum (Gap-6) is a deliberate floor — enough to express PROV-O `prov:Agent` semantics without overreaching into HR-system territory.

## Consequences

- Plan 04 ships the 5 baseline-set structural entity schemas (AircraftModel, AircraftSystem, Subsystem, Component, Document)
- Plan 05 ships 7 baseline regulatory schemas (Requirement, RegulationClause, Standard, Procedure, MaintenanceTask, AccidentCase, ExpertNote)
- Plan 06 ships 5 baseline CFD/failure schemas (FailureMode, CFDMethod, SimulationCase, MeshRequirement, TurbulenceModel)
- **Plan 07 (THIS plan) ships 5 ADR-002 added schemas (Material, TestCase, TestReport, Person, Organization)** and FINALIZES this ADR
- ONT-E-21 (Configuration) is satisfied by THIS ADR (no schema file ships)
- Phase 4 demo data MUST include ≥1 instance per accepted entity type (DEMO-01)
- Phase 4 must include a Person + Organization demo to exercise the H-Darrieus lock end-to-end
- `Component.composition_material` field (Plan 04, entity.component.schema.json) is a URI reference to a Material entity — Phase 3 FK validator confirms resolution
- TestReport.test_case_ref is a URI reference to a TestCase entity — Phase 3 FK validator confirms resolution
- All `provenance.actor` and `provenance.reviewer` URIs in entity / relation YAMLs resolve to either Person or Organization entities — Phase 3 FK validator confirms resolution

## References

- `.planning/REQUIREMENTS.md` ONT-E-19, ONT-E-20, ONT-E-21, ONT-E-22
- `.planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md` D-01..D-04
- `.planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md` Gap Resolution #6 (Person/Organization 6-field minimal); Open Question #1 (Material allowables); Open Question #2 (TestCase + TestReport linking)
- `.planning/PROJECT.md` Core Value (every record traceable; H-Darrieus failure mode)
- `.planning/decisions/ADR-005-provenance-enum.md` (provenance enum + H-Darrieus REJECT rule that motivates Person/Organization mandatory in v0.1.0)
- W3C PROV-O `prov:Agent` (https://www.w3.org/TR/prov-o/)
- schema.org Person / Organization (https://schema.org/Person)

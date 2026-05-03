# ADR-002 — Entity Additions for v0.1.0 (Material, TestCase/TestReport, Configuration deferred, Person/Organization)

Status: ACCEPTED
Date: 2026-05-03
Deciders: user (CONTEXT.md interactive discuss, 2026-05-03)
Implements: D-01, D-02, D-03, D-04, ONT-E-19, ONT-E-20, ONT-E-21, ONT-E-22

## AI 接力开发指南

This ADR resolves the four research-recommended entity additions evaluated in REQUIREMENTS.md ONT-E-19..22. v0.1.0 ships 17 baseline + 3 additional entity classes (5 schema files for the 3 additions because TestCase + TestReport are two schemas and Person + Organization are two schemas). Configuration / EffectivityRange is deferred to v0.2.0. Read this ADR before authoring any of: entity.material.schema.json, entity.test-case.schema.json, entity.test-report.schema.json, entity.person.schema.json, entity.organization.schema.json.

## Context

REQUIREMENTS.md ONT-E-19..22 listed four research-recommended entity additions to evaluate during Phase 2. The decision matters because (a) `provenance.actor` and `provenance.reviewer` are URI fields — without Person/Organization schemas they degrade to free text and the H-Darrieus lock weakens; (b) `Component.composition` referencing materials needs a structured target or it becomes free-text aerospace-grade aluminum descriptions; (c) `Requirement.verified_by` currently can only point at Procedure, which is too narrow for DO-160/DO-178C/DO-254 audit trails.

## Decision

| REQ-ID | Entity | Decision | Rationale (short form; details below) |
|--------|--------|----------|----------------------------------------|
| ONT-E-19 | **Material** | ACCEPT in v0.1.0 (D-01) | Aerospace material constraints are first-class; refusing means rebuild later |
| ONT-E-20 | **TestCase + TestReport** (2 schemas) | ACCEPT in v0.1.0 (D-02) | DO-160/DO-178C/DO-254 audit trails need both plan and outcome |
| ONT-E-21 | **Configuration / EffectivityRange** | DEFER to v0.2.0 (D-03) | v0.1.0 demo data does not exercise serial-number applicability |
| ONT-E-22 | **Person + Organization** (2 schemas) | ACCEPT in v0.1.0 (D-04, mandatory) | URI targets for provenance.actor/reviewer; H-Darrieus lock requires resolvable URIs |

Net entity count v0.1.0 = 17 baseline + 5 schemas (Material, TestCase, TestReport, Person, Organization) = 22 entity schema files (ONT-E-21 deferred so no schema file).

## Material schema scope (v0.1.0)

Minimal shape: id (URI), type (`const: "Material"`), schema_version, i18n.label, name, family (enum: `metal_alloy / composite / polymer / ceramic / coating / other`), nominal_composition (free-text string in v0.1.0; structured in v0.2.0 if demo data exposes the need), design_allowables_reference (free text per RESEARCH.md Open Question #1 — upgrade to a `cites` relation in v0.2.0), heat_treatment_or_layup (optional string), provenance / confidence / source (from baseFields).

DO NOT model:
- MIL-HDBK-5/MMPDS allowable values as structured fields (free-text reference only in v0.1.0)
- Composite layup as a list (single string in v0.1.0)
- Test data references (those go via `cites` relation when needed)

## TestCase + TestReport schema scope (v0.1.0)

Two separate entity types; foreign-key relationship NOT a relation (RESEARCH.md Open Question #2 — defer relation upgrade to v0.2.0+ if uniformity becomes valuable).

**TestCase fields (v0.1.0):**
- id, type (`const: "TestCase"`), schema_version, i18n.label
- test_objective (string, ≥20 chars)
- target (URI to Component / AircraftSystem / Subsystem — what's being tested)
- test_type (enum: `qualification / verification / validation / acceptance / development / other`)
- environmental_conditions (optional string; DO-160-shaped in v0.2.0+)
- acceptance_criteria (string)
- prerequisites (optional array of strings)

**TestReport fields (v0.1.0):**
- id, type (`const: "TestReport"`), schema_version, i18n.label
- test_case_ref (URI to TestCase entity — foreign key, validated in Phase 3)
- executed_at (ISO date)
- executed_by (URI to Person or Organization)
- outcome (enum: `pass / fail / partial / inconclusive`)
- results_summary (string ≥20 chars)
- artifacts_url (optional string format uri — link to test data, photos, traces)
- reviewers (optional array of Person URIs)

DO NOT model:
- DO-178C / DO-254 specific criticality fields (defer to v0.2.0+ per CONTEXT.md Deferred Ideas)
- Detailed test step-by-step trace (defer; demo data only needs summary)

## Configuration / EffectivityRange — DEFERRED

REQ-ID ONT-E-21 is satisfied by THIS ADR documenting the deferral. NO schema file lands in v0.1.0.

Trigger to revisit: when AD/SB demo data (Phase 4 or v0.2.0 demo expansion) needs serial-number applicability scope. Until then, `applicability_scope: free_text` on RegulationClause / Procedure suffices.

Path forward: when activated, add `entity.configuration.schema.json` and `entity.effectivity-range.schema.json`; a relation `applicable_to_configuration` may also be needed.

## Person + Organization schema scope (v0.1.0)

Per RESEARCH.md Gap Resolution #6, minimum 6 fields each drawn from W3C PROV-O / schema.org / FOAF intersection.

**Person fields (v0.1.0):**
- id (URI: `aviationkb://person/<slug>@<version>`)
- type (`const: "Person"`)
- schema_version
- i18n.label (zh + en, both required strings even if one is repeated romanization)
- name (string ≥1 char)
- affiliation (optional URI to Organization)
- role (enum: `author / reviewer / expert / inspector / engineer / other`)
- external_ids (optional object: orcid pattern `^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$`, email format)

**Organization fields (v0.1.0):**
- id (URI: `aviationkb://organization/<slug>@<version>`)
- type (`const: "Organization"`)
- schema_version
- i18n.label
- name
- org_type (enum: `regulator / manufacturer / operator / research_institute / standards_body / consultancy / other`)
- jurisdiction (optional enum aligned with RegulationClause: `FAA / EASA / CAAC / ICAO / Transport-Canada / CASA-AU / other`)
- external_ids (optional object: ror pattern `^https?://ror.org/[a-z0-9]{9}$`, lei pattern `^[A-Z0-9]{20}$`)

Person + Organization are MANDATORY in v0.1.0 because they are the resolution targets for provenance.actor and provenance.reviewer URIs (D-04, ADR-005).

Defer to v0.2.0+:
- ORCID/ROR live resolution (Phase 3 validator format-checks pattern; live fetch later)
- `prov:qualifiedAttribution` partial-authorship audit
- ITAR/EAR person classification (out of scope per PROJECT.md)

## Rationale (entity-by-entity longer form)

See 02-CONTEXT.md D-01..D-04 for the original locked-in rationales. Recap:

- Material: refusing now means `Component.composition` becomes free-text and gets rebuilt later when CFD validation cases need material properties traceable. Material schema is cheap; refactor cost later is high.
- TestCase + TestReport: separating plan and outcome lets `Requirement.verified_by` point at either; matches DO-160 audit trail practice. One entity (`Test`) collapsing both was considered and rejected — outcome data lifecycle differs from plan data.
- Configuration / EffectivityRange: serial-number applicability is real but rare in v0.1.0 demo corpus; demo data must drive the schema, not vice versa.
- Person / Organization: D-04 is mandatory because the URI shape `aviationkb://person/<slug>@<version>` is already the ID format for provenance.actor. Without these schemas, the URI dangles.

## Consequences

- Plan 04 ships the 5 baseline-set entity schemas it covers (AircraftModel/System/Subsystem/Component/Document)
- Plan 05 ships 7 baseline schemas (Requirement/RegulationClause/Standard/Procedure/MaintenanceTask/AccidentCase/ExpertNote)
- Plan 06 ships 5 baseline schemas (FailureMode/CFDMethod/SimulationCase/MeshRequirement/TurbulenceModel)
- Plan 07 ships 5 ADR-002 added schemas (Material, TestCase, TestReport, Person, Organization) and finalizes this ADR if any field-set adjustments are required during authoring
- ONT-E-21 is satisfied by THIS ADR (no schema file ships)
- Phase 4 demo data MUST include ≥1 instance per accepted entity type (DEMO-01)
- Phase 4 must include a Person + Organization demo to exercise the H-Darrieus lock end-to-end

## References

- REQUIREMENTS.md ONT-E-19..22
- 02-CONTEXT.md D-01..D-04
- 02-RESEARCH.md Gap Resolution #6 (Person/Organization 6-field minimal); Open Question #1 (Material allowables); Open Question #2 (TestCase + TestReport linking)
- PROJECT.md Core Value (every record traceable; H-Darrieus failure mode)
- W3C PROV-O `prov:Agent` (https://www.w3.org/TR/prov-o/)
- schema.org Person / Organization (https://schema.org/Person)

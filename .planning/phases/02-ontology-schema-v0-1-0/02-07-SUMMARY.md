---
phase: 02-ontology-schema-v0-1-0
plan: 07
subsystem: ontology
tags: [schema, entity, material, testcase, testreport, person, organization, adr]
dependency_graph:
  requires:
    - ontology/schemas/entity.base.schema.json (Plan 02-02 / Wave 2)
    - ontology/_meta.schema.json (Plan 02-01 / Wave 1) — provides $defs/uri composed via $ref
    - .planning/decisions/ADR-002-entity-additions.md (Plan 02-02 initial draft; FINALIZED here)
  provides:
    - ontology/schemas/entity.material.schema.json
    - ontology/schemas/entity.test-case.schema.json
    - ontology/schemas/entity.test-report.schema.json
    - ontology/schemas/entity.person.schema.json
    - ontology/schemas/entity.organization.schema.json
    - .planning/decisions/ADR-002-entity-additions.md (FINALIZED)
  affects:
    - ontology/schemas/entity.component.schema.json (Plan 04) — composition_material URI now resolves to Material
    - All entity / relation YAMLs (Phase 4+) — provenance.actor / provenance.reviewer URIs now have Person + Organization to resolve to
    - Phase 3 validators — new FK targets: Material, TestCase, Person, Organization
tech-stack:
  added: []
  patterns:
    - "Pattern 2 (Entity Base + Type-Specific Composition) applied to all 5 added schemas via allOf + $ref entity.base.schema.json"
    - "FK-not-relation for tight 1:N coupling (TestReport.test_case_ref → TestCase) per RESEARCH Open Q2"
    - "Free-text scoping for v0.1.0 (Material.design_allowables_reference, TestCase.environmental_conditions) — structured upgrades deferred to v0.2.0+"
    - "6-field minimal Person/Organization per Gap-6 (W3C PROV-O ∩ schema.org ∩ FOAF intersection)"
key-files:
  created:
    - path: ontology/schemas/entity.material.schema.json
      role: Material entity schema (ONT-E-19, D-01) — family enum, free-text composition + allowables
    - path: ontology/schemas/entity.test-case.schema.json
      role: TestCase entity schema (ONT-E-20, D-02) — test plan with target URI + acceptance criteria
    - path: ontology/schemas/entity.test-report.schema.json
      role: TestReport entity schema (ONT-E-20, D-02) — test outcome with REQUIRED test_case_ref FK
    - path: ontology/schemas/entity.person.schema.json
      role: Person entity schema (ONT-E-22, D-04) — URI resolution target for provenance.actor/reviewer
    - path: ontology/schemas/entity.organization.schema.json
      role: Organization entity schema (ONT-E-22, D-04) — jurisdiction enum aligned with RegulationClause
  modified:
    - path: .planning/decisions/ADR-002-entity-additions.md
      role: Finalized after baseline schemas visible for consistency review (no field-table drift; status stamped FINALIZED)
decisions:
  - "Material.design_allowables_reference is free-text in v0.1.0 (RESEARCH Open Q1); structured `cites` relation upgrade deferred to v0.2.0+"
  - "TestReport.test_case_ref is a typed URI foreign key, NOT a relation (RESEARCH Open Q2); Phase 3 FK validator confirms resolution"
  - "TestReport.outcome enum is exactly [pass, fail, partial, inconclusive] — `partial` and `inconclusive` carry semantic weight distinct from `fail`"
  - "Person + Organization are MANDATORY in v0.1.0 (D-04) — required so provenance.actor / provenance.reviewer URIs have resolution targets and the H-Darrieus REJECT rule (ADR-005) operates on real entities not free text"
  - "Organization.jurisdiction enum aligned exactly with RegulationClause.jurisdiction (Plan 05) — same domain so a Regulator org and the regulations it issues can be cross-checked"
  - "ONT-E-21 (Configuration/EffectivityRange) satisfied by ADR-002 deferral — NO schema file ships; v0.2.0 trigger is AD/SB demo data needing serial-number applicability"
metrics:
  duration: "~12 min"
  completed: "2026-05-03"
---

# Phase 2 Plan 07: Entity Additions Summary

ADR-002 entity additions landed: 5 entity schemas (Material, TestCase, TestReport, Person, Organization) composing entity.base via allOf + $ref + unevaluatedProperties:false, all self-validating as JSON Schema Draft 2020-12. ADR-002 finalized after baseline schemas (Plans 04+05+06) visible — no field-table drift required.

## What Shipped

### Schemas (5)

| Schema | REQ-ID | type.const | Required fields beyond base | Key enums |
|--------|--------|------------|------------------------------|-----------|
| `entity.material.schema.json` | ONT-E-19, D-01 | `Material` | `name`, `family` | `family`: metal_alloy/composite/polymer/ceramic/coating/other |
| `entity.test-case.schema.json` | ONT-E-20, D-02 | `TestCase` | `test_objective` (≥20), `target` (URI), `test_type`, `acceptance_criteria` (≥20) | `test_type`: qualification/verification/validation/acceptance/development/other |
| `entity.test-report.schema.json` | ONT-E-20, D-02 | `TestReport` | `test_case_ref` (URI FK), `executed_at` (date), `executed_by` (URI), `outcome`, `results_summary` (≥20) | `outcome`: pass/fail/partial/inconclusive |
| `entity.person.schema.json` | ONT-E-22, D-04 | `Person` | `name` | `role`: author/reviewer/expert/inspector/engineer/other (6) |
| `entity.organization.schema.json` | ONT-E-22, D-04 | `Organization` | `name`, `org_type` | `org_type`: regulator/manufacturer/operator/research_institute/standards_body/consultancy/other (7); `jurisdiction`: FAA/EASA/CAAC/ICAO/Transport-Canada/CASA-AU/other |

All five inherit `id`, `schema_version`, `i18n.label`, `provenance`, `confidence`, `source` via `allOf $ref ./entity.base.schema.json`.

### ADR finalization (1)

`.planning/decisions/ADR-002-entity-additions.md` — status stamped FINALIZED with field tables matching the shipped schemas verbatim. ONT-E-21 (Configuration/EffectivityRange) deferral to v0.2.0 documented as the satisfaction record (no schema file ships).

## Pitfall Locks

- **Pitfall #1 (additionalProperties trap):** All 5 schemas use `unevaluatedProperties: false` (composition-friendly). Zero `additionalProperties` strings in any of the 5 files. Verified via `! grep -q '"additionalProperties"' <each-file>`.
- **Pitfall #9 ($schema declaration):** All 5 declare `"$schema": "https://json-schema.org/draft/2020-12/schema"`. Verified via `check-jsonschema --check-metaschema` exit 0 on each.

## Cross-References Wired In

- **TestReport ↔ TestCase:** `TestReport.test_case_ref` is a REQUIRED `$ref` to `_meta.schema.json#/$defs/uri` — Phase 3 validator confirms FK resolves to a real TestCase entity (T-02-07-03 mitigation: prevents fabricated test outcomes from dangling).
- **Person/Organization ← provenance:** All `provenance.actor` and `provenance.reviewer` URIs throughout the knowledge base will resolve to Person or Organization entities. Without this plan, those URIs degrade to free text and the H-Darrieus REJECT rule (ADR-005) loses its teeth.
- **Component → Material:** `Component.composition_material` (Plan 04 deliverable) is a URI reference; Phase 3 FK validator confirms resolution to a Material entity in this plan's deliverable set.
- **Organization.jurisdiction ↔ RegulationClause.jurisdiction:** Same enum domain (FAA/EASA/CAAC/ICAO/Transport-Canada/CASA-AU/other) so a regulator Organization and the RegulationClauses it issues can be cross-checked at validator time.

## Verification Evidence

```
$ check-jsonschema --check-metaschema ontology/schemas/entity.{material,test-case,test-report,person,organization}.schema.json
ok -- validation done  (×5)

$ for f in ontology/schemas/entity.{material,test-case,test-report,person,organization}.schema.json; do
    grep -c '"unevaluatedProperties": false' "$f"
  done
1 1 1 1 1   (each schema declares it at top level; nested external_ids objects also use it)

$ for f in ontology/schemas/entity.{material,test-case,test-report,person,organization}.schema.json; do
    grep -c '"additionalProperties"' "$f"
  done
0 0 0 0 0   (Pitfall #1 lock confirmed)

$ jq -e '.properties.type.const' on each → "Material" "TestCase" "TestReport" "Person" "Organization"

$ jq -e '.required | contains(["test_case_ref"])' entity.test-report.schema.json → true
$ jq -e '.properties.outcome.enum | contains(["pass","fail","partial","inconclusive"])' entity.test-report.schema.json → true
$ jq -e '.properties.role.enum | contains(["author","reviewer","expert"])' entity.person.schema.json → true
$ jq -e '.properties.org_type.enum | contains(["regulator","manufacturer"])' entity.organization.schema.json → true
$ jq -r '.properties.external_ids.properties.orcid.pattern' entity.person.schema.json → ^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$
```

## Decisions Made

1. **No field-table drift during finalization.** Plan 02-02 initial ADR-002 draft proved sufficient — the baseline schemas authored in Plans 04/05/06 did not surface any naming or shape inconsistencies that warranted re-opening field tables. ADR-002 status stamped FINALIZED with content unchanged.

2. **Material.design_allowables_reference stays free-text in v0.1.0.** Per RESEARCH Open Q1, structured allowables would either require a half-baked numeric model or block the schema set on weeks of MIL-HDBK-5 modeling. The reference field gives an audit trail without the modeling cost.

3. **TestReport.test_case_ref stays a typed URI FK, not a relation.** Per RESEARCH Open Q2, TestCase ↔ TestReport is a tight 1:N coupling that doesn't benefit from relation-table generality and would clutter triple exports.

4. **Organization.jurisdiction is OPTIONAL, not required.** Multi-jurisdiction operators (e.g. major airlines) leave it unset; only single-jurisdiction regulators / standards bodies fill it in. Required would force false precision.

5. **Person.affiliation single URI in v0.1.0.** Multi-affiliation deferred to v0.2.0+ via a future `affiliated_with` relation. Single primary affiliation is cheap and covers ≥95% of demo cases.

## Deferred to v0.2.0+

- Configuration / EffectivityRange entity (ONT-E-21 deferred per ADR-002)
- Structured Material allowables (replace free-text reference with `cites` relation to Standard)
- DO-178C / DO-254 specific TestCase fields (criticality level, evidence type, test category)
- TestReport step-by-step trace (currently summary only)
- ORCID / ROR / LEI live resolution (Phase 3 only format-checks pattern)
- Hierarchical organization structure (parent_org, divisions)
- Multi-affiliation per Person via `affiliated_with` relation
- ITAR / EAR person classification

## Deviations from Plan

None — plan executed exactly as written. Tasks 1 and 2 from PLAN.md authored 5 schemas; an additional finalization commit updated ADR-002 per the executor's prompt objective ("update ADR-002 with finalized shapes after baseline schemas are visible for consistency review"). The finalization required no field-table changes; only the status stamp moved from ACCEPTED to ACCEPTED (FINALIZED in Plan 02-07).

## Commits

| Task | Description | Commit |
|------|-------------|--------|
| 1 | Add Material + TestCase + TestReport entity schemas | `8bd7918` |
| 2 | Add Person + Organization entity schemas | `64794b9` |
| 3 (added) | Finalize ADR-002 after baseline schemas visible | `871c496` |

## Self-Check: PASSED

Files exist:
- FOUND: ontology/schemas/entity.material.schema.json
- FOUND: ontology/schemas/entity.test-case.schema.json
- FOUND: ontology/schemas/entity.test-report.schema.json
- FOUND: ontology/schemas/entity.person.schema.json
- FOUND: ontology/schemas/entity.organization.schema.json
- FOUND: .planning/decisions/ADR-002-entity-additions.md

Commits exist:
- FOUND: 8bd7918 (Task 1)
- FOUND: 64794b9 (Task 2)
- FOUND: 871c496 (ADR-002 finalization)

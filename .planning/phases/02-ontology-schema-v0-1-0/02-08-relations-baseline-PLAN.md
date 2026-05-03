---
phase: 02-ontology-schema-v0-1-0
plan: 08
type: execute
wave: 4
depends_on: [03]
files_modified:
  - ontology/schemas/relation.part-of.schema.json
  - ontology/schemas/relation.applicable-to.schema.json
  - ontology/schemas/relation.constrained-by.schema.json
  - ontology/schemas/relation.verified-by.schema.json
  - ontology/schemas/relation.derived-from.schema.json
  - ontology/schemas/relation.supersedes.schema.json
  - ontology/schemas/relation.cites.schema.json
  - ontology/schemas/relation.causes.schema.json
  - ontology/schemas/relation.mitigated-by.schema.json
  - ontology/schemas/relation.requires.schema.json
  - ontology/schemas/relation.equivalent-to.schema.json
  - ontology/schemas/relation.conflicts-with.schema.json
  - ontology/schemas/relation.used-in.schema.json
autonomous: true
requirements:
  - ONT-R-02
  - ONT-R-03
  - ONT-R-04
  - ONT-R-05
  - ONT-R-06
  - ONT-R-07
  - ONT-R-08
  - ONT-R-09
  - ONT-R-10
  - ONT-R-11
  - ONT-R-12
  - ONT-R-13
  - ONT-R-14
must_haves:
  truths:
    - "All 13 baseline relation schemas self-validate as Draft 2020-12"
    - "Each composes relation.base.schema.json via allOf + $ref + unevaluatedProperties: false"
    - "Pitfall #1 + #9 locks confirmed"
    - "relation.requires.schema.json description contains the requires-vs-interfaces_with USE/DON'T USE worked example from ADR-003 (Pitfall #4 lock)"
    - "relation.constrained-by.schema.json description contains the constrained_by-vs-complies_with worked example from ADR-003"
    - "relation.equivalent-to.schema.json description contains the verbatim foil 'DO NOT USE for cross-language pairs — use entity i18n field per ADR-003 / D-12'"
  artifacts:
    - path: "ontology/schemas/relation.part-of.schema.json"
      provides: "ONT-R-02"
    - path: "ontology/schemas/relation.applicable-to.schema.json"
      provides: "ONT-R-03"
    - path: "ontology/schemas/relation.constrained-by.schema.json"
      provides: "ONT-R-04 with worked-example boundary vs complies_with"
    - path: "ontology/schemas/relation.verified-by.schema.json"
      provides: "ONT-R-05"
    - path: "ontology/schemas/relation.derived-from.schema.json"
      provides: "ONT-R-06"
    - path: "ontology/schemas/relation.supersedes.schema.json"
      provides: "ONT-R-07"
    - path: "ontology/schemas/relation.cites.schema.json"
      provides: "ONT-R-08"
    - path: "ontology/schemas/relation.causes.schema.json"
      provides: "ONT-R-09"
    - path: "ontology/schemas/relation.mitigated-by.schema.json"
      provides: "ONT-R-10"
    - path: "ontology/schemas/relation.requires.schema.json"
      provides: "ONT-R-11 with worked-example boundary vs interfaces_with"
    - path: "ontology/schemas/relation.equivalent-to.schema.json"
      provides: "ONT-R-12 with verbatim 'NOT for cross-language' foil"
    - path: "ontology/schemas/relation.conflicts-with.schema.json"
      provides: "ONT-R-13"
    - path: "ontology/schemas/relation.used-in.schema.json"
      provides: "ONT-R-14"
  key_links:
    - from: "all 13 relation-type schemas"
      to: "ontology/schemas/relation.base.schema.json"
      via: "allOf + $ref"
---

<objective>
Author 13 baseline relation schemas. Each composes `relation.base.schema.json` via `allOf` + `$ref` and adds the relation-specific `type` const, optional metadata fields, and the worked-example discipline mandated by ADR-003.

Output: 13 schema files in `ontology/schemas/`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/REQUIREMENTS.md
@.planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md
@.planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md
@.planning/decisions/ADR-003-relation-additions.md
@.planning/decisions/ADR-004-field-shapes.md
@.planning/phases/02-ontology-schema-v0-1-0/02-03-SUMMARY.md
@ontology/_meta.schema.json
@ontology/schemas/relation.base.schema.json

<interfaces>
<!-- Use Code Example #3 (relation.interfaces-with.schema.json) from 02-RESEARCH.md as the LITERAL TEMPLATE for every schema in this plan. -->
<!-- Each schema's structure:
       $schema = Draft 2020-12
       $id = https://aviation-knowledge-base.local/ontology/schemas/relation.<slug>.schema.json
       title: "<relation_name> relation (ONT-R-NN)"
       description: 1-3 sentences PLUS USE / DON'T USE examples for boundary-prone relations
       type: object
       allOf: [{ "$ref": "relation.base.schema.json" }]
       properties:
         type: { const: "<relation_name>" }
         schema_version: { $ref: "../_meta.schema.json#/$defs/schemaVersionString" }
         subject + object inherited from relation.base
         valid_from + valid_until inherited from relation.base
         ...optional relation-specific metadata
       required: [type, schema_version, subject, object, valid_from]
       unevaluatedProperties: false -->

<!-- ADR-003 worked examples (Plan 03 output) — verbatim copy into descriptions: -->
<!--   relation.requires: include the cross-tier USE/DON'T USE table from ADR-003 -->
<!--   relation.constrained-by: include the generic-constraint USE/DON'T USE table -->
<!--   relation.equivalent-to: include the "NOT for cross-language" foil verbatim -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author 7 simple relation schemas (part_of, applicable_to, verified_by, derived_from, supersedes, cites, causes)</name>
  <files>ontology/schemas/relation.part-of.schema.json, ontology/schemas/relation.applicable-to.schema.json, ontology/schemas/relation.verified-by.schema.json, ontology/schemas/relation.derived-from.schema.json, ontology/schemas/relation.supersedes.schema.json, ontology/schemas/relation.cites.schema.json, ontology/schemas/relation.causes.schema.json</files>
  <read_first>
    - ontology/schemas/relation.base.schema.json
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Code Example #3 — verbatim relation template)
    - .planning/REQUIREMENTS.md (ONT-R-02..09)
  </read_first>
  <action>
    Author 7 schemas using Code Example #3 as template. For each, include:
    - $schema = Draft 2020-12
    - allOf $ref relation.base.schema.json
    - properties.type: const matching relation slug (note: const value uses snake_case as in ONT-R-XX names, e.g. `part_of`, NOT `part-of`)
    - properties.schema_version $ref _meta schemaVersionString
    - unevaluatedProperties: false

    **relation.part-of.schema.json (ONT-R-02):**
    - title: "part_of relation (ONT-R-02)"
    - description: "Composition relation. USE FOR: Component(brake_pad) part_of Component(brake_assembly); Subsystem part_of AircraftSystem; AircraftSystem part_of AircraftModel. Transitive: if A part_of B and B part_of C, then A is implicitly part_of C (Phase 3 validator may compute closure). Cardinality is 1-to-1 (each entity has at most one direct parent in the part_of tree)."
    - properties.type: const "part_of"
    - cardinality_hint: optional enum [exactly_one, one_or_more, optional] (description: "Hint about expected cardinality on the subject side; Phase 3 validator does not enforce — informational only.")

    **relation.applicable-to.schema.json (ONT-R-03):**
    - title: "applicable_to relation (ONT-R-03)"
    - description: "USE FOR: RegulationClause applicable_to AircraftModel; Standard applicable_to AircraftSystem; Procedure applicable_to Component. Establishes scope of regulatory / standards / procedural artifacts. NOT for compliance-grade audit trail (use complies_with — ONT-R-16); applicable_to is broader and includes 'this regulation could apply' even before formal compliance is asserted."
    - properties.type: const "applicable_to"
    - applicability_scope: optional string (free-text scope qualifier; e.g. "all configurations" or "post-2020 deliveries")

    **relation.verified-by.schema.json (ONT-R-05):**
    - title: "verified_by relation (ONT-R-05)"
    - description: "USE FOR: Requirement verified_by TestCase / TestReport / SimulationCase / Procedure. Establishes which artifact verifies a requirement. NOT for citation only — use cites."
    - properties.type: const "verified_by"
    - verification_method: optional enum [test, analysis, inspection, demonstration, simulation, similarity]

    **relation.derived-from.schema.json (ONT-R-06):**
    - title: "derived_from relation (ONT-R-06)"
    - description: "USE FOR: Requirement derived_from RegulationClause; ExpertNote derived_from AccidentCase; Procedure derived_from Standard. Establishes provenance of a derived artifact (distinct from cites which is reference, distinct from complies_with which is normative compliance)."
    - properties.type: const "derived_from"

    **relation.supersedes.schema.json (ONT-R-07):**
    - title: "supersedes relation (ONT-R-07)"
    - description: "USE FOR: RegulationClause(new) supersedes RegulationClause(old); Standard(rev_C) supersedes Standard(rev_B); ExpertNote supersedes ExpertNote. Pitfall #6 lock: when status=superseded on the OLD clause, this relation provides the FORWARD pointer to the new one. Phase 3 validator can cross-check that supersedes points to an entity whose previous version's status is indeed 'superseded'."
    - properties.type: const "supersedes"
    - supersession_reason: optional string ≥20 chars

    **relation.cites.schema.json (ONT-R-08):**
    - title: "cites relation (ONT-R-08)"
    - description: "USE FOR: any entity cites Document with locator. Distinguished from derived_from: cites = 'this artifact references that document'; derived_from = 'this artifact was DERIVED from that artifact'. Phase 4 demo data uses cites heavily because Document entities are the resolution targets for provenance.source.document_id."
    - properties.type: const "cites"
    - locator: optional object: { page: optional integer minimum 1, section: optional string, paragraph: optional integer minimum 1 }; unevaluatedProperties: false (description: "Sub-document locator within the cited Document")
    - quotation: optional string (the cited text fragment if direct-quoted)

    **relation.causes.schema.json (ONT-R-09):**
    - title: "causes relation (ONT-R-09)"
    - description: "USE FOR: FailureMode causes effect (free-text effect string); AccidentCase causes causal_factor. Note: causes is NOT a graph between entities only — sometimes the object is a free-text effect description. v0.1.0 keeps the object as URI for graph uniformity; free-text effects go into FailureMode.effects array (entity-side)."
    - properties.type: const "causes"
    - chain_position: optional enum [proximate, contributing, root] (causal-chain hint)
  </action>
  <verify>
    <automated>for s in part-of applicable-to verified-by derived-from supersedes cites causes; do f="ontology/schemas/relation.$s.schema.json"; check-jsonschema --check-metaschema "$f" || exit 1; ! grep -q '"additionalProperties"' "$f" || exit 1; grep -q '"unevaluatedProperties": false' "$f" || exit 1; jq -e '.allOf[0]["$ref"] == "relation.base.schema.json"' "$f" || exit 1; done; jq -e '.properties.type.const == "part_of"' ontology/schemas/relation.part-of.schema.json &amp;&amp; jq -e '.properties.type.const == "applicable_to"' ontology/schemas/relation.applicable-to.schema.json &amp;&amp; jq -e '.properties.type.const == "supersedes"' ontology/schemas/relation.supersedes.schema.json &amp;&amp; jq -e '.properties.type.const == "cites"' ontology/schemas/relation.cites.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - All 7 files self-validate; Pitfall #1 + #9 locks
    - Each composes relation.base via allOf + $ref
    - Filename uses kebab-case slug (e.g. `relation.part-of.schema.json`); type.const uses snake_case (e.g. `part_of`)
    - Each schema's description distinguishes itself from any boundary-overlap relation by name (cites vs derived_from; verified_by vs uses requirement)
    - Phase-4-relevant relations include locator (cites) and verification_method (verified_by) optional metadata
  </acceptance_criteria>
  <done>7 simple relations validate, compose relation.base, and exhibit boundary discipline in descriptions.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Author 6 boundary-discipline relation schemas (constrained_by, mitigated_by, requires, equivalent_to, conflicts_with, used_in)</name>
  <files>ontology/schemas/relation.constrained-by.schema.json, ontology/schemas/relation.mitigated-by.schema.json, ontology/schemas/relation.requires.schema.json, ontology/schemas/relation.equivalent-to.schema.json, ontology/schemas/relation.conflicts-with.schema.json, ontology/schemas/relation.used-in.schema.json</files>
  <read_first>
    - ontology/schemas/relation.base.schema.json
    - .planning/decisions/ADR-003-relation-additions.md (verbatim worked-example tables for requires/interfaces_with and constrained_by/complies_with)
    - .planning/REQUIREMENTS.md (ONT-R-04, ONT-R-10..14)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Pitfall #4 — worked-example overlap)
  </read_first>
  <action>
    **relation.constrained-by.schema.json (ONT-R-04):**
    - title: "constrained_by relation (ONT-R-04)"
    - description: "Generic constraint relation. USE FOR: Component(seat) constrained_by Requirement(weight_budget_15kg); AircraftSystem constrained_by Requirement(power_budget); Subsystem constrained_by Standard(operating_temperature_range). DO NOT USE FOR: explicit normative compliance with regulations / standards / certification clauses — that's complies_with (ONT-R-16). DO NOT USE FOR: hard regulatory compliance with audit trail — also complies_with. constrained_by is broader and includes budget / cost / non-normative constraints. Boundary per ADR-003 / D-11."
    - properties.type: const "constrained_by"
    - constraint_kind: optional enum [budget, regulatory_soft, performance, environmental, interface, other]

    **relation.mitigated-by.schema.json (ONT-R-10):**
    - title: "mitigated_by relation (ONT-R-10)"
    - description: "USE FOR: FailureMode mitigated_by Procedure / Component / design_change. Establishes a mitigation strategy for a failure mode. Often paired with causes (FailureMode causes Effect; FailureMode mitigated_by Procedure)."
    - properties.type: const "mitigated_by"
    - mitigation_type: optional enum [design, procedure, training, inspection, monitoring, redundancy]

    **relation.requires.schema.json (ONT-R-11):**
    - title: "requires relation (ONT-R-11)"
    - description: "Cross-tier dependency relation. USE FOR: Component(brake_disc) requires MaintenanceTask(brake_inspection_500h); SimulationCase(takeoff_performance) requires MeshRequirement(yPlus_target_30); Procedure(emergency_landing) requires Component(landing_gear). DO NOT USE FOR: peer-tier interface (e.g. AvionicsBay → ECS — that's interfaces_with, ONT-R-15). DO NOT USE FOR: parent-child within an assembly (use part_of). DO NOT USE FOR: citations (use cites). Boundary per ADR-003 / D-10."
    - properties.type: const "requires"

    **relation.equivalent-to.schema.json (ONT-R-12):**
    - title: "equivalent_to relation (ONT-R-12)"
    - description: "USE FOR: this entity denotes the same real-world thing as that entity, under different identifiers (e.g. an item in two different parts catalogs, or a reorganized item with new ID). DO NOT USE FOR: cross-language pairs (Chinese ExpertNote ↔ English ExpertNote on same topic) — use the entity i18n field per ADR-003 / D-12. Two-entity model fragments retrieval (Pitfall in research/Don't Hand-Roll table). DO NOT USE FOR: synonyms in glossary — those go in docs/GLOSSARY.md (Phase 6)."
    - properties.type: const "equivalent_to"
    - equivalence_basis: optional enum [identifier_change, catalog_remap, reorganization, vendor_alias, other]

    **relation.conflicts-with.schema.json (ONT-R-13):**
    - title: "conflicts_with relation (ONT-R-13)"
    - description: "USE FOR: RegulationClause conflicts_with RegulationClause; Standard conflicts_with Standard. Establishes that two normative artifacts are mutually inconsistent. Rationale field is mandatory because a conflict claim without explanation is unauditable."
    - properties.type: const "conflicts_with"
    - conflict_rationale: string ≥20 chars — required (description: "Mandatory rationale explaining the nature of the conflict — why these two normative sources are inconsistent.")
    - severity: optional enum [contradicts_directly, ambiguous_overlap, jurisdiction_conflict, version_skew]
    - required (additional to base): [conflict_rationale]

    **relation.used-in.schema.json (ONT-R-14):**
    - title: "used_in relation (ONT-R-14)"
    - description: "USE FOR: CFDMethod used_in SimulationCase; TurbulenceModel used_in SimulationCase; MeshRequirement used_in SimulationCase. Inverse of SimulationCase's URI fields (cfd_method_ref, turbulence_model_ref, mesh_ref) for query graph reuse — Phase 3 validator may compute one direction from the other to keep them consistent."
    - properties.type: const "used_in"
  </action>
  <verify>
    <automated>for s in constrained-by mitigated-by requires equivalent-to conflicts-with used-in; do f="ontology/schemas/relation.$s.schema.json"; check-jsonschema --check-metaschema "$f" || exit 1; ! grep -q '"additionalProperties"' "$f" || exit 1; grep -q '"unevaluatedProperties": false' "$f" || exit 1; done; grep -q "DO NOT USE" ontology/schemas/relation.constrained-by.schema.json &amp;&amp; grep -q "DO NOT USE" ontology/schemas/relation.requires.schema.json &amp;&amp; grep -q "DO NOT USE FOR: cross-language" ontology/schemas/relation.equivalent-to.schema.json &amp;&amp; grep -q "interfaces_with" ontology/schemas/relation.requires.schema.json &amp;&amp; grep -q "complies_with" ontology/schemas/relation.constrained-by.schema.json &amp;&amp; grep -q "i18n" ontology/schemas/relation.equivalent-to.schema.json &amp;&amp; jq -e '.required | contains(["conflict_rationale"])' ontology/schemas/relation.conflicts-with.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - All 6 files self-validate; Pitfall #1 + #9 locks
    - **relation.requires.schema.json description contains "DO NOT USE" + references "interfaces_with" by name** (Pitfall #4 lock; D-10 boundary)
    - **relation.constrained-by.schema.json description contains "DO NOT USE" + references "complies_with" by name** (Pitfall #4 lock; D-11 boundary)
    - **relation.equivalent-to.schema.json description contains "DO NOT USE FOR: cross-language" + references "i18n" by name** (D-12 lock)
    - relation.conflicts-with.schema.json has `conflict_rationale` required string field minLength 20
    - All 6 type.const values match
  </acceptance_criteria>
  <done>6 boundary-discipline relations validate; constrained_by / requires / equivalent_to descriptions verbatim implement ADR-003 boundary tables; conflicts_with rationale required.</done>
</task>

</tasks>

<threat_model>
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-02-08-01 | Tampering | Pitfall #1 in any of 13 schemas | mitigate | Per-file `! grep -q additionalProperties` |
| T-02-08-02 | Repudiation | Pitfall #4: ambiguous boundaries → Phase 4 demo data picks arbitrary relation | mitigate | requires / constrained_by / equivalent_to descriptions verbatim USE/DON'T-USE per ADR-003 |
| T-02-08-03 | Repudiation | conflicts_with without rationale → uninspectable conflict claims | mitigate | conflict_rationale required, ≥20 chars |
</threat_model>

<verification>
- All 13 files exist; `--check-metaschema` exits 0 each
- `pre-commit run --all-files` exits 0
- 2 atomic commits via gsd-tools
</verification>

<success_criteria>
- 13 baseline relation schemas authored (ONT-R-02..14)
- Each composes relation.base.schema.json
- Boundary discipline locked: requires/interfaces_with, constrained_by/complies_with, equivalent_to/i18n
- Pitfall #1 + #9 locks
</success_criteria>

<output>
Create `.planning/phases/02-ontology-schema-v0-1-0/02-08-SUMMARY.md` with:
- 13 schemas listed
- Boundary-discipline confirmation (3 relations carry verbatim ADR-003 tables in description)
- Pitfall #1 + #9 confirmation
- Pointer to Plan 09 for the 3 ADR-003 added relations (interfaces_with, complies_with, applicable_during_phase)
</output>

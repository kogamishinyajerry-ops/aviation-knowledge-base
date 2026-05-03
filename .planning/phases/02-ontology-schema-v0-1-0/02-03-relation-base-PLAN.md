---
phase: 02-ontology-schema-v0-1-0
plan: 03
type: execute
wave: 2
depends_on: [01]
files_modified:
  - ontology/schemas/relation.base.schema.json
  - .planning/decisions/ADR-003-relation-additions.md
  - .planning/decisions/ADR-004-field-shapes.md
autonomous: true
requirements:
  - ONT-R-01
must_haves:
  truths:
    - "relation.base.schema.json self-validates as Draft 2020-12"
    - "relation.base.schema.json composes _meta.schema.json#/$defs/baseFields via allOf + $ref"
    - "relation.base.schema.json declares unevaluatedProperties: false (NOT additionalProperties: false)"
    - "relation.base requires schema_version + type + subject + object + valid_from on every leaf relation"
    - "ADR-003 records relation-additions decision (interfaces_with/complies_with/applicable_during_phase accept; has_revision/generated_by internalize as fields) with worked examples for the boundary cases"
    - "ADR-004 records field-shape decisions: confidence decimal+rationale, i18n flat, version_history array shape"
  artifacts:
    - path: "ontology/schemas/relation.base.schema.json"
      provides: "Relation composition base — every relation-type schema allOf-refs this; adds type, schema_version, subject, object, valid_from, valid_until on top of baseFields"
    - path: ".planning/decisions/ADR-003-relation-additions.md"
      provides: "Decision for ONT-R-15..19: accept interfaces_with/complies_with/applicable_during_phase; reject has_revision (→ field) and generated_by (→ field). Worked examples for requires/interfaces_with and constrained_by/complies_with overlaps."
    - path: ".planning/decisions/ADR-004-field-shapes.md"
      provides: "Decision for D-13/D-14/D-15: confidence shape, i18n flat, version_history array shape"
  key_links:
    - from: "ontology/schemas/relation.base.schema.json"
      to: "ontology/_meta.schema.json#/$defs/baseFields"
      via: "allOf + $ref"
    - from: "ADR-003-relation-additions.md"
      to: "ontology/schemas/relation.{interfaces-with,complies-with,applicable-during-phase}.schema.json"
      via: "rationale → leaf schema concretization (schemas land in Plans 08 + 09)"
---

<objective>
Build the relation composition middleware: `relation.base.schema.json` (which every type-specific relation schema in plans 08/09 will compose), plus the two ADRs (003 relation additions, 004 field shapes) that lock the relation-side decisions.

This plan runs PARALLEL with Plan 02 (no shared files; both depend only on Plan 01's `_meta.schema.json`).

Purpose: Type-specific relation schemas (16 of them) cannot be authored without relation.base. ADR-003 and ADR-004 must be readable alongside leaf relation schemas so reviewers can verify the boundary semantics (requires vs interfaces_with, constrained_by vs complies_with).
Output: 3 files: 1 schema + 2 ADRs.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/REQUIREMENTS.md
@.planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md
@.planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md
@.planning/phases/02-ontology-schema-v0-1-0/02-01-SUMMARY.md
@ontology/_meta.schema.json

<interfaces>
<!-- _meta.schema.json provides the same $defs that this plan composes. -->
<!-- Relation-specific fields (NOT in _meta): subject, object, valid_from, valid_until -->
<!--   subject: URI to entity (the "from" peer) -->
<!--   object:  URI to entity (the "to" peer) -->
<!--   valid_from: ISO 8601 timestamp — when the relationship became valid -->
<!--   valid_until: nullable ISO 8601 timestamp — null = currently valid -->

<!-- D-05: interfaces_with — peer-tier (system↔system); boundary with `requires` -->
<!-- D-06: complies_with — explicit normative compliance; boundary with `constrained_by` -->
<!-- D-07: has_revision NOT a relation — internalized as version_history field (D-15) -->
<!-- D-08: applicable_during_phase — flight phase enum: taxi/takeoff/cruise/approach/landing/missed/emergency -->
<!-- D-09: generated_by NOT a relation — encoded by provenance.actor + source.tool -->
<!-- D-10: requires (cross-tier) vs interfaces_with (peer-tier) — worked examples mandatory -->
<!-- D-11: constrained_by (generic) vs complies_with (regulation/standard) — worked examples mandatory -->
<!-- D-12: equivalent_to NOT for cross-language (use i18n field) -->
<!-- D-13: confidence shape -->
<!-- D-14: i18n flat shape -->
<!-- D-15: version_history shape -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author ontology/schemas/relation.base.schema.json composing _meta</name>
  <files>ontology/schemas/relation.base.schema.json</files>
  <read_first>
    - ontology/_meta.schema.json (composition source)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Code Example #3 for interfaces_with — adapt the relation.base scaffolding section; Pattern #3; Pitfall #1 + #9)
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-23 URI form)
    - .planning/REQUIREMENTS.md (ONT-R-01)
  </read_first>
  <action>
    Create `ontology/schemas/relation.base.schema.json` as Draft 2020-12. Structure:

    1. `"$schema": "https://json-schema.org/draft/2020-12/schema"`
    2. `"$id": "https://aviation-knowledge-base.local/ontology/schemas/relation.base.schema.json"`
    3. `"title": "Relation Base (composes _meta.schema.json#/$defs/baseFields)"`
    4. `"description"` — "Relation composition base. Every type-specific relation schema (relation.part-of.schema.json etc.) MUST compose this via allOf + $ref + unevaluatedProperties: false. NEVER additionalProperties: false (Pitfall #1). Adds the relation-only fields (type, schema_version, subject, object, valid_from, valid_until) on top of universal baseFields. Schema version: 0.1.0."
    5. `"type": "object"`
    6. `"allOf": [{ "$ref": "../_meta.schema.json#/$defs/baseFields" }]`
    7. `"properties":`
       - `type` — string, minLength 1, description "Discriminator. Each leaf type schema overrides with const. Examples: 'part_of', 'interfaces_with', 'complies_with'."
       - `schema_version` — `{"$ref": "../_meta.schema.json#/$defs/schemaVersionString"}`
       - `subject` — `{"$ref": "../_meta.schema.json#/$defs/uri"}`, description "Subject entity URI (the 'from' peer in directional relations; either peer in symmetric ones — order is symbolic). Phase 3 validator confirms the entity exists."
       - `object` — `{"$ref": "../_meta.schema.json#/$defs/uri"}`, description "Object entity URI (the 'to' peer)."
       - `valid_from` — `{"$ref": "../_meta.schema.json#/$defs/isoDateTime"}`, description "When this relationship became valid. Required."
       - `valid_until` — `{"anyOf": [{"$ref": "../_meta.schema.json#/$defs/isoDateTime"}, {"type": "null"}]}`, description "When this relationship ceased to be valid. null = currently valid (no expiration)."
    8. `"required": ["type", "schema_version", "subject", "object", "valid_from"]` — note baseFields adds id/provenance/confidence/source via allOf
    9. `"unevaluatedProperties": false`
  </action>
  <verify>
    <automated>check-jsonschema --check-metaschema ontology/schemas/relation.base.schema.json &amp;&amp; grep -q '"unevaluatedProperties": false' ontology/schemas/relation.base.schema.json &amp;&amp; ! grep -q '"additionalProperties"' ontology/schemas/relation.base.schema.json &amp;&amp; jq -e '.allOf[0]["$ref"] | contains("_meta.schema.json#/$defs/baseFields")' ontology/schemas/relation.base.schema.json &amp;&amp; jq -e '.required | contains(["type","schema_version","subject","object","valid_from"])' ontology/schemas/relation.base.schema.json &amp;&amp; jq -e '.properties.valid_until.anyOf | length == 2' ontology/schemas/relation.base.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - `check-jsonschema --check-metaschema ontology/schemas/relation.base.schema.json` exits 0
    - `jq -e '.["$schema"] == "https://json-schema.org/draft/2020-12/schema"' ontology/schemas/relation.base.schema.json` exits 0
    - `! grep -q '"additionalProperties"' ontology/schemas/relation.base.schema.json` (Pitfall #1)
    - `grep -q '"unevaluatedProperties": false' ontology/schemas/relation.base.schema.json` exits 0
    - `jq -r '.allOf[0]["$ref"]' ontology/schemas/relation.base.schema.json` outputs string containing `_meta.schema.json#/$defs/baseFields`
    - `jq -e '.properties | has("type") and has("schema_version") and has("subject") and has("object") and has("valid_from") and has("valid_until")' ontology/schemas/relation.base.schema.json` exits 0
    - `jq -e '.properties.valid_until.anyOf | length == 2' ontology/schemas/relation.base.schema.json` exits 0 (nullable per ONT-R-01 spec)
    - `pre-commit run check-jsonschema --files ontology/schemas/relation.base.schema.json` exits 0
  </acceptance_criteria>
  <done>relation.base.schema.json validates as Draft 2020-12, composes _meta baseFields, requires the 5 relation-side fields per ONT-R-01.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Author ADR-003 relation-additions decision record</name>
  <files>.planning/decisions/ADR-003-relation-additions.md</files>
  <read_first>
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-05, D-06, D-07, D-08, D-09, D-10, D-11, D-12)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Pitfall #4 — worked-example overlap; Code Example #3 — interfaces_with worked examples)
    - .planning/REQUIREMENTS.md (ONT-R-15..19)
  </read_first>
  <action>
    Create `.planning/decisions/ADR-003-relation-additions.md`:

    ```markdown
    # ADR-003 — Relation Additions for v0.1.0 (interfaces_with, complies_with, applicable_during_phase accepted; has_revision and generated_by internalized as fields)

    Status: ACCEPTED
    Date: 2026-05-03
    Deciders: user (CONTEXT.md interactive discuss, 2026-05-03)
    Implements: D-05, D-06, D-07, D-08, D-09, D-10, D-11, D-12, ONT-R-15, ONT-R-16, ONT-R-17, ONT-R-18, ONT-R-19

    > AI 接力开发指南: This ADR resolves the five research-recommended relation additions evaluated in REQUIREMENTS.md ONT-R-15..19. Three are accepted as relation schemas (interfaces_with, complies_with, applicable_during_phase). Two are rejected — the underlying need is real but better expressed as a FIELD on entities than as a relation: has_revision becomes the `version_history[]` field on entity.base (D-15), and generated_by is encoded by `provenance.actor` (Person/Org URI) + `provenance.tool` (string) — already provided by `_meta.schema.json#/$defs/provenance`. Read this ADR before authoring relation.interfaces-with.schema.json, relation.complies-with.schema.json, relation.applicable-during-phase.schema.json (all Plan 09).

    ## Context

    REQUIREMENTS.md ONT-R-15..19 listed five candidate relation additions. Each was evaluated against:
    1. Does the underlying semantic exist in real aviation engineering practice?
    2. Is it modeled better as a relation (graph edge) or a field (entity property)?
    3. If relation: does it overlap with an existing relation? If yes, can the boundary be made explicit?

    ## Decision

    | REQ-ID | Candidate | Decision | Rationale |
    |--------|-----------|----------|-----------|
    | ONT-R-15 | **interfaces_with** | ACCEPT (D-05) | Peer-tier system↔system interface (e.g. avionics ↔ ECS via ARINC 429) is independent semantics from `requires` (cross-tier) — see boundary table below |
    | ONT-R-16 | **complies_with** | ACCEPT (D-06) | Explicit regulatory compliance is sharper than the generic `constrained_by` — see boundary table below |
    | ONT-R-17 | **has_revision** | REJECT — internalize as field (D-07) | Every entity gets `version_history[]` per D-15; a separate has_revision relation would explode into per-version edges |
    | ONT-R-18 | **applicable_during_phase** | ACCEPT (D-08) | Flight phase (taxi/takeoff/cruise/approach/landing/missed/emergency) is independent semantics from `applicable_to` (which targets aircraft model / system, not phase) |
    | ONT-R-19 | **generated_by** | REJECT — already encoded (D-09) | `provenance.actor` (Person/Org URI) + `provenance.tool` (e.g. 'claude-opus-4-7') already capture the same information; a separate relation duplicates |

    Net relation count v0.1.0 = 13 baseline + 3 accepted = 16 relation schemas.

    ## Boundary clarifications (worked examples)

    ### `requires` vs `interfaces_with` (D-10)

    **`requires`** = cross-tier dependency between entities at different architectural levels.

    | Use | Don't use |
    |-----|-----------|
    | `Component(brake_disc) requires MaintenanceTask(brake_inspection_500h)` | NOT `Component(brake_disc) requires Component(brake_pad)` (that's part_of within an assembly) |
    | `SimulationCase(takeoff_performance) requires MeshRequirement(yPlus_target_30)` | NOT `AvionicsBay requires ECS` (that's interfaces_with — peer systems) |
    | `Procedure(emergency_landing) requires Component(landing_gear)` | NOT `Standard requires Standard` (that's a citation — use cites) |

    **`interfaces_with`** = peer-tier interface between two entities at the same level.

    | Use | Don't use |
    |-----|-----------|
    | `AircraftSystem(avionics) interfaces_with AircraftSystem(ECS) via ARINC 429` | NOT `AircraftSystem(avionics) interfaces_with Component(GPS_unit)` (use part_of for parent-child) |
    | `AircraftSystem(hydraulic) interfaces_with AircraftSystem(flight_control) via servo_actuators` | NOT `Component requires MaintenanceTask` (that's the canonical requires example) |
    | `Subsystem(power_distribution) interfaces_with Subsystem(generator)` | NOT `Standard applicable_to AircraftSystem` (use applicable_to or complies_with) |

    Schema-level enforcement: `relation.interfaces-with.schema.json.description` MUST contain BOTH a USE and a DON'T USE example (Pitfall #4 lock). `relation.requires.schema.json.description` MUST do the same.

    ### `constrained_by` vs `complies_with` (D-11)

    **`constrained_by`** = generic constraint of any kind (mass budget, cost ceiling, regulation, performance limit).

    | Use | Don't use |
    |-----|-----------|
    | `Component(seat) constrained_by Requirement(weight_budget_15kg)` | NOT `Component complies_with weight_budget` (a budget is a constraint, not a regulation/standard) |
    | `Subsystem(actuator) constrained_by Standard(operating_temperature_range)` | NOT for hard regulatory compliance — use `complies_with` |
    | `AircraftSystem constrained_by Requirement(power_budget)` | NOT `Component constrained_by FAR §25.305` (that's normative compliance — use complies_with) |

    **`complies_with`** = explicit normative compliance with a regulation, standard, or certification clause. Audit-grade.

    | Use | Don't use |
    |-----|-----------|
    | `Component(structure) complies_with RegulationClause(FAR §25.305)` | NOT for budget / non-normative constraints — those are constrained_by |
    | `AircraftSystem(avionics) complies_with Standard(DO-178C_LevelB)` | NOT for "soft compliance" — if there's no audit trail, it's constrained_by |
    | `Procedure complies_with RegulationClause(EASA AMC 25.1309)` | NOT for citation only — use cites |

    Schema-level enforcement: `relation.complies-with.schema.json.description` MUST contain both USE and DON'T USE examples; `relation.constrained-by.schema.json.description` MUST do the same.

    ### `equivalent_to` is NOT cross-language (D-12)

    **`equivalent_to`** = "these two entities denote the same real-world thing under different identifiers/names" (e.g. an item in two different parts catalogs, or a reorganized item with new ID).

    DO NOT use for:
    - Cross-language pairs (Chinese ExpertNote ↔ English ExpertNote on same topic): handled by single entity with `i18n: { label: { zh, en }, full_text: { zh, en } }`. Two-entity model fragments retrieval (Pitfall in Don't Hand-Roll table).
    - Synonyms in glossary: handled by `docs/GLOSSARY.md` (Phase 6).

    Schema-level enforcement: `relation.equivalent-to.schema.json.description` MUST include the verbatim foil "DO NOT USE for cross-language pairs — use the entity i18n field per ADR-003 / D-12."

    ## Internalized fields (NOT relations)

    ### has_revision → `version_history[]` field on entity.base

    Every entity gets `version_history: [{version, date, author, change_summary}]` per D-15. Absence implies version 1; mandatory once version > 1. This avoids:
    - Explosion of low-value version-link edges (one per revision)
    - Inconsistency between graph-layer (relation) and entity-layer (record) revisioning

    Cost: revisions cannot be queried via the relation graph layer. Mitigation: `version_history` is a structured array; downstream `to_jsonl_triples.py` (D-19, ADR-006) emits one triple per history element, recovering graph-layer query if needed.

    ### generated_by → `provenance.actor` + `provenance.tool` on every record

    Every record's `provenance` block already carries:
    - `actor` (Person or Organization URI)
    - `tool` (free-text or model identifier — e.g. `claude-opus-4-7`, `manual`, `ragflow-ingest`)

    A separate `generated_by(record, tool)` relation would duplicate this information.

    ## Consequences

    - Plan 08 ships 13 baseline relation schemas (part_of, applicable_to, constrained_by, verified_by, derived_from, supersedes, cites, causes, mitigated_by, requires, equivalent_to, conflicts_with, used_in)
    - Plan 09 ships 3 accepted-addition schemas (interfaces_with, complies_with, applicable_during_phase) and updates this ADR if any field-set adjustments emerge
    - ONT-R-17 and ONT-R-19 are satisfied by THIS ADR (no schema files ship; the requirement is "evaluate and decide", and decision = "internalize as field")
    - `relation.requires.schema.json` (Plan 08) MUST contain the cross-tier worked example
    - `relation.constrained-by.schema.json` (Plan 08) MUST contain the generic-constraint worked example
    - `relation.equivalent-to.schema.json` (Plan 08) MUST contain the "NOT for cross-language" foil
    - Phase 4 demo data MUST exercise interfaces_with and complies_with at least once each (DEMO-02)

    ## References

    - REQUIREMENTS.md ONT-R-15..19
    - 02-CONTEXT.md D-05..D-12
    - 02-RESEARCH.md Pitfall #4 (worked-example overlap)
    - 02-RESEARCH.md Code Example #3 (interfaces_with skeleton with full description discipline)
    - PROJECT.md Out of Scope ("Auto-translation without human review")
    - ADR-004 (field shapes — i18n, version_history, confidence)
    ```
  </action>
  <verify>
    <automated>test -f .planning/decisions/ADR-003-relation-additions.md &amp;&amp; grep -q "ACCEPT" .planning/decisions/ADR-003-relation-additions.md &amp;&amp; grep -q "internalize as field" .planning/decisions/ADR-003-relation-additions.md &amp;&amp; grep -q "interfaces_with" .planning/decisions/ADR-003-relation-additions.md &amp;&amp; grep -q "complies_with" .planning/decisions/ADR-003-relation-additions.md &amp;&amp; grep -q "applicable_during_phase" .planning/decisions/ADR-003-relation-additions.md &amp;&amp; grep -q "DO NOT USE" .planning/decisions/ADR-003-relation-additions.md &amp;&amp; grep -q "AI 接力开发指南" .planning/decisions/ADR-003-relation-additions.md</automated>
  </verify>
  <acceptance_criteria>
    - File exists; all 5 ONT-R-15..19 IDs cited: `for r in ONT-R-15 ONT-R-16 ONT-R-17 ONT-R-18 ONT-R-19; do grep -q "$r" .planning/decisions/ADR-003-relation-additions.md || exit 1; done` exits 0
    - `grep -q "internalize as field" .planning/decisions/ADR-003-relation-additions.md` exits 0 (D-07/D-09 internalization explicit)
    - All accepted relation slugs appear: `for n in interfaces_with complies_with applicable_during_phase; do grep -q "$n" .planning/decisions/ADR-003-relation-additions.md || exit 1; done` exits 0
    - Worked examples present (USE / DON'T USE table format): `grep -c "DON'T USE\|DO NOT USE\|Don't use" .planning/decisions/ADR-003-relation-additions.md` returns ≥3 (one per overlap pair)
    - `grep -q "ARINC 429" .planning/decisions/ADR-003-relation-additions.md` exits 0 (concrete protocol example)
    - `grep -q "FAR §25.305\|FAR §25\." .planning/decisions/ADR-003-relation-additions.md` exits 0 (concrete regulation example)
    - `grep -q "i18n" .planning/decisions/ADR-003-relation-additions.md` exits 0 (D-12 cross-reference)
    - All ADR sections present (Status / Date / Deciders / Implements / Context / Decision / Consequences / References)
    - `grep -q "AI 接力开发指南" .planning/decisions/ADR-003-relation-additions.md` exits 0
  </acceptance_criteria>
  <done>ADR-003 records the 5 relation evaluations with concrete USE/DON'T-USE worked examples for the boundary cases (requires↔interfaces_with, constrained_by↔complies_with, equivalent_to↔i18n). Pitfall #4 mitigation is locked.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Author ADR-004 schema field-shapes decision record</name>
  <files>.planning/decisions/ADR-004-field-shapes.md</files>
  <read_first>
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-13, D-14, D-15)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Code Example #1 — verified field shapes)
    - ontology/_meta.schema.json (the actual implementation)
  </read_first>
  <action>
    Create `.planning/decisions/ADR-004-field-shapes.md`:

    ```markdown
    # ADR-004 — Schema Field Shapes (confidence, i18n, version_history)

    Status: ACCEPTED
    Date: 2026-05-03
    Deciders: user (CONTEXT.md interactive discuss, 2026-05-03)
    Implements: D-13, D-14, D-15

    > AI 接力开发指南: This ADR documents the exact JSON shape of three field families that show up on every entity and relation: `confidence`, `i18n`, and `version_history`. These shapes are encoded in `ontology/_meta.schema.json` (Plan 01). This ADR exists to explain WHY they are shaped that way. Read before extending any of these fields.

    ## Context

    Three field families show up across many entity types. If each entity invents its own shape, downstream consumers (RAG retriever, validator, exporter) must handle a shape-zoo. Picking shapes upfront and documenting the rationale makes future maintainers confident they can extend the field without breaking consumers.

    ## Decision

    ### `confidence` — object with score (decimal 0..1) + rationale (≥1 sentence string) (D-13)

    ```json
    {
      "confidence": {
        "score": 0.85,
        "rationale": "Multi-source agreement: cited in FAA AC 25.1309-1B and EASA AMC 25.1309 with identical text."
      }
    }
    ```

    Required: `score`, `rationale`. Optional: `calibration_method` (free-text for v0.1.0; structured in v0.2.0+).

    **Why decimal 0–1 (not letter grades, not percent integer):**
    - H-Darrieus REJECT threshold (`> 0.85`, ADR-005) needs a numeric comparison. Letter grades break this.
    - Percent integer (0–100) loses information at the threshold edge (we want the 0.86 vs 0.85 distinction).
    - Float [0, 1] is the standard ML / probability convention.

    **Why rationale required (not optional):**
    - A confidence score with no rationale is uninspectable. The H-Darrieus failure mode (high confidence + no audit trail) starts here.
    - `minLength: 20` enforces "at least one full sentence" in practice.

    ### `i18n` — flat object with label and full_text sub-objects (D-14)

    ```json
    {
      "i18n": {
        "label": {
          "zh": "机翼前缘除冰系统",
          "en": "Wing Leading-Edge De-Icing System"
        },
        "full_text": {
          "zh": "本系统使用…",
          "en": "This system uses…"
        }
      }
    }
    ```

    Schema rules:
    - `i18n.label` is REQUIRED; both `zh` and `en` keys must be present (either may be empty string for genuinely monolingual content like a Chinese-only accident report).
    - `i18n.full_text` is OPTIONAL; if present, both `zh` and `en` keys must be present (same monolingual rule).
    - Keys are exactly `zh` and `en` (ISO 639-1 codes). NOT `chinese`/`english`, NOT `zh_CN`/`en_US`. Future regional variants (e.g. `zh_TW`, `en_GB`) can be added in v0.2.0+ without breaking change.

    **Why flat (not nested per-language root, like `{zh: {label, full_text}, en: {label, full_text}}`):**
    - Adding a new field type (e.g. `summary`) is one place: `i18n.summary.{zh, en}`. The nested shape would be 2+ places.
    - Filtering "give me all label fields across both languages" is a single dot-path query.

    **Why required `zh` and `en` keys (not optional):**
    - Future RAG retriever indexes both languages from the same record (D-12, ADR-003). Optional keys would mean "language X is missing — skip" branches. Empty string is explicit.
    - Per-translation provenance is deferred to v0.2.0+ (CONTEXT.md Deferred Ideas) — when it lands, the empty-string convention extends naturally.

    ### `version_history` — array of revision records (D-15)

    ```json
    {
      "version_history": [
        {
          "version": 1,
          "date": "2026-04-01T10:00:00Z",
          "author": "aviationkb://person/jane-engineer@1",
          "change_summary": "Initial creation. Captured from FAA AC 25.1309-1B section 6.b.2.iii."
        },
        {
          "version": 2,
          "date": "2026-05-03T15:30:00Z",
          "author": "aviationkb://person/john-reviewer@1",
          "change_summary": "Updated criticality_level from 'major' to 'hazardous' after FailureMode review."
        }
      ]
    }
    ```

    Each item required: `version` (integer ≥1), `date` (ISO 8601 timestamp), `author` (Person or Organization URI), `change_summary` (string ≥20 chars).

    **Field-level rules:**
    - The array is OPTIONAL; absence implies the record is at version 1 (the implicit initial state).
    - When a record bumps to version > 1, `version_history` becomes mandatory and must contain entries from version 1 forward.
    - The latest array element's `version` must equal the entity's top-level `version` field (D-20). Phase 3 validator enforces.

    **Why an array on the entity (not separate has_revision relations):** see ADR-003 §"Internalized fields".

    **Why each item carries a Person/Org URI (not free-text "John"):** without a URI target, `version_history.author` becomes free text and the H-Darrieus failure mode reappears at the audit-trail layer.

    **Why `change_summary` ≥20 chars:** matches the `confidence.rationale` discipline; "fix typo" is too short to be auditable.

    ## Rationale (cross-cutting)

    Three field families, three different shapes, one consistent philosophy: **structured over free-text wherever a consumer downstream might need to query, validate, or render the field**. We refuse to cheap out on shape design; the cost is paid here, the savings are paid every Phase 3+ time we add a new validator or exporter.

    ## Consequences

    - `_meta.schema.json` exposes `$defs/confidence`, `$defs/i18nLabel` (and the `i18n` object structure pattern is reused inline in entity.base) — Plan 01 deliverable
    - `entity.base.schema.json` REQUIRES `i18n.label`; `version_history[]` is optional but structurally locked — Plan 02
    - Person/Organization schemas (Plan 07) populate the URI shape that `version_history.author` and `provenance.actor`/`reviewer` reference
    - Phase 4 demo data MUST include ≥1 instance with bilingual `i18n.full_text` (DEMO-07)
    - Phase 4 SHOULD include ≥1 instance with `version_history.length >= 2` to exercise the format

    ## References

    - REQUIREMENTS.md ONT-E-01 (entity base mandatory fields)
    - 02-CONTEXT.md D-13, D-14, D-15
    - 02-RESEARCH.md Code Example #1 (`_meta.schema.json` shape)
    - ADR-005 (provenance enum + H-Darrieus rule — confidence threshold)
    - ADR-003 (`equivalent_to` is NOT for cross-language — i18n field carries this)
    ```
  </action>
  <verify>
    <automated>test -f .planning/decisions/ADR-004-field-shapes.md &amp;&amp; grep -q 'D-13' .planning/decisions/ADR-004-field-shapes.md &amp;&amp; grep -q 'D-14' .planning/decisions/ADR-004-field-shapes.md &amp;&amp; grep -q 'D-15' .planning/decisions/ADR-004-field-shapes.md &amp;&amp; grep -q 'ISO 639-1' .planning/decisions/ADR-004-field-shapes.md &amp;&amp; grep -q 'minLength' .planning/decisions/ADR-004-field-shapes.md &amp;&amp; grep -q 'AI 接力开发指南' .planning/decisions/ADR-004-field-shapes.md</automated>
  </verify>
  <acceptance_criteria>
    - File exists at `.planning/decisions/ADR-004-field-shapes.md`
    - All three decisions implemented: `for d in D-13 D-14 D-15; do grep -q "$d" .planning/decisions/ADR-004-field-shapes.md || exit 1; done` exits 0
    - `grep -q 'minLength' .planning/decisions/ADR-004-field-shapes.md` exits 0 (rationale ≥20 chars rule documented)
    - `grep -q 'ISO 639-1' .planning/decisions/ADR-004-field-shapes.md` exits 0 (D-14 zh/en codes)
    - `grep -q '0\.85' .planning/decisions/ADR-004-field-shapes.md` exits 0 (H-Darrieus threshold cross-reference)
    - `grep -q 'aviationkb://person/' .planning/decisions/ADR-004-field-shapes.md` exits 0 (URI form example for version_history.author)
    - All ADR sections present (Status / Date / Deciders / Implements / Context / Decision / Rationale / Consequences / References)
    - `grep -q 'AI 接力开发指南' .planning/decisions/ADR-004-field-shapes.md` exits 0
  </acceptance_criteria>
  <done>ADR-004 documents the exact JSON shapes for confidence, i18n, and version_history with concrete examples and the rationale for each shape decision. Cross-references _meta.schema.json (Plan 01), ADR-005 (H-Darrieus threshold), ADR-003 (i18n carries cross-language).</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| `relation.base.schema.json` → 16 leaf relation schemas (Plans 08, 09) | Base mistakes propagate. Meta-validation catches structural issues. |
| ADR-003 worked examples → demo data authors (Phase 4) | Vague examples cause boundary-overlap inconsistency in demo data (Pitfall #4). |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-02-03-01 | Tampering | relation.base uses additionalProperties:false → silently rejects baseFields | mitigate | Pitfall #1 lock in acceptance criteria; explicit grep test |
| T-02-03-02 | Repudiation | ADR-003 omits boundary worked examples → Phase 4 demo data drifts | mitigate | Acceptance criteria require USE/DON'T USE table count ≥3 |
| T-02-03-03 | Information Disclosure | ADR-004 omits H-Darrieus threshold context → future maintainer changes confidence shape | mitigate | ADR-004 cross-references ADR-005 by ID |
</threat_model>

<verification>
- `check-jsonschema --check-metaschema ontology/schemas/relation.base.schema.json` exits 0
- `pre-commit run --all-files` exits 0
- All 3 files committed atomically
</verification>

<success_criteria>
- relation.base.schema.json validates as Draft 2020-12 and composes _meta correctly
- ADR-003 documents the 5 relation evaluations with concrete USE/DON'T-USE worked examples for the boundary cases
- ADR-004 documents the three field-family shapes with rationale tying back to H-Darrieus
- Pitfall #1 + #9 locks confirmed
- All 3 files committed via gsd-tools (atomic per task)
</success_criteria>

<output>
After completion, create `.planning/phases/02-ontology-schema-v0-1-0/02-03-SUMMARY.md` with:
- relation.base.schema.json composition path verified
- ADR-003 worked-example tables (Plan 08 executors verbatim-copy these into relation.{requires,interfaces-with,constrained-by,complies-with,equivalent-to}.schema.json descriptions)
- ADR-004 field-shape recap (Plan 04..07 executors reference this when authoring leaf entity schemas)
- Pitfall #1 + #9 confirmation
</output>

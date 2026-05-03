---
phase: 02-ontology-schema-v0-1-0
plan: 02
type: execute
wave: 2
depends_on: [01]
files_modified:
  - ontology/schemas/entity.base.schema.json
  - .planning/decisions/ADR-002-entity-additions.md
  - .planning/decisions/ADR-007-schema-versioning.md
autonomous: true
requirements:
  - ONT-E-01
  - VER-03
must_haves:
  truths:
    - "entity.base.schema.json self-validates as Draft 2020-12 (--check-metaschema exits 0)"
    - "entity.base.schema.json composes _meta.schema.json#/$defs/baseFields via allOf + $ref"
    - "entity.base.schema.json declares unevaluatedProperties: false (NOT additionalProperties: false)"
    - "entity.base requires schema_version + type + i18n on every leaf entity (VER-03 contract)"
    - "version_history field shape exists and matches D-15 (semver, ISO date, Person URI author, ≥20-char change_summary)"
    - "ADR-002 records entity-additions decision (Material, TestCase+TestReport, Person+Organization accepted; Configuration deferred)"
    - "ADR-007 records schema-versioning decision (per-file version + per-record schema_version + Python migrations)"
  artifacts:
    - path: "ontology/schemas/entity.base.schema.json"
      provides: "Entity composition base — every entity-type schema allOf-refs this; adds type, schema_version, version, i18n, tags, version_history on top of _meta baseFields"
      contains: '"$ref": "../[._]meta'
    - path: ".planning/decisions/ADR-002-entity-additions.md"
      provides: "Decision record for the 4 ONT-E-19..22 evaluations: Material accept (D-01); TestCase+TestReport accept (D-02); Configuration defer (D-03); Person+Organization accept (D-04)"
    - path: ".planning/decisions/ADR-007-schema-versioning.md"
      provides: "Decision record for D-20/D-21/D-22/D-26: per-file + per-record versioning, ontology/VERSION + CHANGELOG, Python migrations with ruamel.yaml"
  key_links:
    - from: "ontology/schemas/entity.base.schema.json"
      to: "ontology/_meta.schema.json#/$defs/baseFields"
      via: "allOf + $ref"
    - from: "ADR-002-entity-additions.md"
      to: "ontology/schemas/entity.{material,test-case,test-report,person,organization}.schema.json"
      via: "rationale → leaf-schema concretization (schemas land in Plan 04 + 07)"
---

<objective>
Build the entity composition middleware: `entity.base.schema.json` (which every type-specific entity schema in plans 04, 05, 06, 07 will compose via `allOf` + `$ref`), plus the two ADRs (002 entity additions, 007 schema versioning) that lock the entity-side decisions.

Purpose: Type-specific entity schemas (20 of them) cannot be validated until entity.base.schema.json exists. ADR-002 must land before plans 04/05/06/07 write the leaf schemas, so reviewers can read the rationale alongside the schema files.
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
<!-- _meta.schema.json (Plan 01) provides the following $defs that this plan composes: -->
<!--   $defs/uri          → URI form aviationkb://<type>/<slug>@<version> -->
<!--   $defs/baseFields   → required {id, provenance, confidence, source} — composed via allOf -->
<!--   $defs/i18nLabel    → bilingual label {zh, en} -->
<!--   $defs/isoDateTime  → ISO 8601 timestamp -->
<!--   $defs/schemaVersionString → semver pattern -->
<!-- All references use relative path "_meta.schema.json#/$defs/<name>" — schemas live in -->
<!-- ontology/schemas/, _meta lives in ontology/, so relative ref is "../_meta.schema.json#/$defs/<name>" -->
<!-- (The actual ref path depends on $id structure; use Code Example #2 in 02-RESEARCH.md as the literal reference.) -->

<!-- D-13: confidence shape — number 0..1 + rationale string ≥1 sentence -->
<!-- D-14: i18n flat — {label: {zh, en}, full_text: {zh, en}} -->
<!-- D-15: version_history[] — items {version: int ≥1, date: ISO8601, author: URI, change_summary: string ≥20 chars} -->
<!-- D-20: schema_version REQUIRED on every leaf record (instance YAML); per-file version field on schema source -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author ontology/schemas/entity.base.schema.json composing _meta</name>
  <files>ontology/schemas/entity.base.schema.json</files>
  <read_first>
    - ontology/_meta.schema.json (composition source — verify the $defs/baseFields shape)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Code Example #2 for AircraftSystem — adapt the entity.base scaffolding section; Pattern #2 §"Entity Base + Type-Specific Composition"; Pitfall #1 + #9)
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-13, D-14, D-15, D-20)
  </read_first>
  <action>
    Create `ontology/schemas/entity.base.schema.json` as a JSON Schema Draft 2020-12 document. Structure:

    1. `"$schema": "https://json-schema.org/draft/2020-12/schema"` (Pitfall #9)
    2. `"$id": "https://aviation-knowledge-base.local/ontology/schemas/entity.base.schema.json"`
    3. `"title": "Entity Base (composes _meta.schema.json#/$defs/baseFields)"`
    4. `"description"` — explicitly state: "Entity composition base. Every type-specific entity schema (entity.aircraft-model.schema.json etc.) MUST compose this via allOf + $ref + unevaluatedProperties: false. NEVER use additionalProperties: false (Pitfall #1). Adds the entity-only fields (type, schema_version, version, i18n, tags, version_history) on top of the universal baseFields (id, provenance, confidence, source) defined in _meta.schema.json. Schema version: 0.1.0."
    5. `"type": "object"`
    6. `"allOf": [{ "$ref": "../_meta.schema.json#/$defs/baseFields" }]`
    7. `"properties":` adding entity-only fields:
       - `type` — string, minLength 1, description "Discriminator. Each leaf type schema overrides this with `const`. Examples: 'AircraftSystem', 'Material', 'Person'."
       - `schema_version` — `{"$ref": "../_meta.schema.json#/$defs/schemaVersionString"}` — description "D-20 per-record schema version (semver). Phase 3 validator rejects records older than N-1."
       - `version` — integer, minimum 1, default 1, description "Per-record version. Defaults to 1 (implicit). Bumped each time the record is meaningfully revised (D-15 internalized has_revision)."
       - `i18n` — object with two sub-objects:
         - `label` — `{"$ref": "../_meta.schema.json#/$defs/i18nLabel"}`
         - `full_text` — type object, properties zh + en (both type string, BOTH required), unevaluatedProperties: false
         - REQUIRED: ["label"] (full_text optional but if present must be complete)
         - unevaluatedProperties: false on the i18n object
       - `tags` — type array, items {type string, pattern `^[a-z0-9]+(-[a-z0-9]+)*$`}, uniqueItems: true, description "Free-form kebab-case tags for faceting. NOT for ontological relationships — those are relation YAMLs."
       - `version_history` — type array (per D-15), items: type object, properties: version (integer minimum 1), date (`$ref` isoDateTime), author (`$ref` uri), change_summary (string minLength 20). REQUIRED: [version, date, author, change_summary]; unevaluatedProperties: false on each item. Description on the array: "D-15. Internalized has_revision (D-07). Absence implies version == 1. Mandatory once version > 1."
    8. `"required": ["type", "schema_version", "i18n"]` — note `id`, `provenance`, `confidence`, `source` are required by composed baseFields (allOf merges requireds)
    9. `"unevaluatedProperties": false` (Pitfall #1: never additionalProperties)

    File MUST end with newline.
  </action>
  <verify>
    <automated>check-jsonschema --check-metaschema ontology/schemas/entity.base.schema.json &amp;&amp; grep -q '"unevaluatedProperties": false' ontology/schemas/entity.base.schema.json &amp;&amp; ! grep -q '"additionalProperties"' ontology/schemas/entity.base.schema.json &amp;&amp; jq -e '.allOf[0]["$ref"] | contains("_meta.schema.json#/$defs/baseFields")' ontology/schemas/entity.base.schema.json &amp;&amp; jq -e '.required | contains(["type","schema_version","i18n"])' ontology/schemas/entity.base.schema.json &amp;&amp; jq -e '.properties.version_history.items.properties.change_summary.minLength == 20' ontology/schemas/entity.base.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - `check-jsonschema --check-metaschema ontology/schemas/entity.base.schema.json` exits 0
    - `jq -e '.["$schema"] == "https://json-schema.org/draft/2020-12/schema"' ontology/schemas/entity.base.schema.json` exits 0 (Pitfall #9)
    - `! grep -q '"additionalProperties"' ontology/schemas/entity.base.schema.json` (Pitfall #1: zero hits)
    - `grep -q '"unevaluatedProperties": false' ontology/schemas/entity.base.schema.json` exits 0
    - `jq -r '.allOf[0]["$ref"]' ontology/schemas/entity.base.schema.json` outputs a string containing `_meta.schema.json#/$defs/baseFields`
    - `jq -e '.properties | has("type") and has("schema_version") and has("version") and has("i18n") and has("tags") and has("version_history")' ontology/schemas/entity.base.schema.json` exits 0
    - `jq -e '.properties.version_history.items.required | contains(["version","date","author","change_summary"])' ontology/schemas/entity.base.schema.json` exits 0 (D-15)
    - `jq -e '.properties.version_history.items.properties.change_summary.minLength == 20' ontology/schemas/entity.base.schema.json` exits 0
    - `jq -e '.properties.i18n.required | contains(["label"])' ontology/schemas/entity.base.schema.json` exits 0 (D-14: label required, full_text optional but structured)
    - `pre-commit run check-jsonschema --files ontology/schemas/entity.base.schema.json` exits 0
  </acceptance_criteria>
  <done>entity.base.schema.json validates as Draft 2020-12, composes _meta baseFields, and exposes all entity-only fields per D-13/D-14/D-15/D-20. Pitfalls #1 and #9 verified absent/present respectively.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Author ADR-002 entity-additions decision record</name>
  <files>.planning/decisions/ADR-002-entity-additions.md</files>
  <read_first>
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-01, D-02, D-03, D-04 — entity additions decisions)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Gap Resolution #6 — Person/Organization 6-field minimal shape)
    - .planning/REQUIREMENTS.md (ONT-E-19, ONT-E-20, ONT-E-21, ONT-E-22)
  </read_first>
  <action>
    Create `.planning/decisions/ADR-002-entity-additions.md` with full ADR structure:

    ```markdown
    # ADR-002 — Entity Additions for v0.1.0 (Material, TestCase/TestReport, Configuration deferred, Person/Organization)

    Status: ACCEPTED
    Date: 2026-05-03
    Deciders: user (CONTEXT.md interactive discuss, 2026-05-03)
    Implements: D-01, D-02, D-03, D-04, ONT-E-19, ONT-E-20, ONT-E-21, ONT-E-22

    > AI 接力开发指南: This ADR resolves the four research-recommended entity additions evaluated in REQUIREMENTS.md ONT-E-19..22. v0.1.0 ships 17 baseline + 3 additional entity classes (5 schema files for the 3 additions because TestCase + TestReport are two schemas and Person + Organization are two schemas). Configuration / EffectivityRange is deferred to v0.2.0. Read this ADR before authoring any of: entity.material.schema.json, entity.test-case.schema.json, entity.test-report.schema.json, entity.person.schema.json, entity.organization.schema.json.

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
    ```
  </action>
  <verify>
    <automated>test -f .planning/decisions/ADR-002-entity-additions.md &amp;&amp; grep -q "ACCEPT" .planning/decisions/ADR-002-entity-additions.md &amp;&amp; grep -q "DEFER to v0.2.0" .planning/decisions/ADR-002-entity-additions.md &amp;&amp; grep -q "Material" .planning/decisions/ADR-002-entity-additions.md &amp;&amp; grep -q "TestCase" .planning/decisions/ADR-002-entity-additions.md &amp;&amp; grep -q "Person" .planning/decisions/ADR-002-entity-additions.md &amp;&amp; grep -q "Organization" .planning/decisions/ADR-002-entity-additions.md &amp;&amp; grep -q "AI 接力开发指南" .planning/decisions/ADR-002-entity-additions.md</automated>
  </verify>
  <acceptance_criteria>
    - File exists at `.planning/decisions/ADR-002-entity-additions.md`
    - All four ONT-E-19..22 IDs appear: `for r in ONT-E-19 ONT-E-20 ONT-E-21 ONT-E-22; do grep -q "$r" .planning/decisions/ADR-002-entity-additions.md || exit 1; done` exits 0
    - All five accepted schema names appear: `for n in entity.material entity.test-case entity.test-report entity.person entity.organization; do grep -q "$n" .planning/decisions/ADR-002-entity-additions.md || exit 1; done` exits 0
    - `grep -q "DEFER to v0.2.0" .planning/decisions/ADR-002-entity-additions.md` exits 0 (D-03 deferral explicit)
    - `grep -q "ONT-E-21 is satisfied by THIS ADR" .planning/decisions/ADR-002-entity-additions.md` exits 0 (deferral satisfies the REQ)
    - `grep -q "AI 接力开发指南" .planning/decisions/ADR-002-entity-additions.md` exits 0 (R12 discipline)
    - All ADR sections present: Status, Date, Deciders, Implements, Context, Decision, Rationale, Consequences, References
    - `grep -q "Gap Resolution #6" .planning/decisions/ADR-002-entity-additions.md` exits 0 (cross-references RESEARCH.md)
  </acceptance_criteria>
  <done>ADR-002 records the four entity-addition decisions with field-level scope for the 5 accepted schemas, the deferral rationale for Configuration, and the cross-references to research findings.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Author ADR-007 schema-versioning decision record</name>
  <files>.planning/decisions/ADR-007-schema-versioning.md</files>
  <read_first>
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-20, D-21, D-22, D-26)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Gap Resolution #5 — ruamel.yaml; Pitfall #6 — schema-version mismatch; Pitfall #10 — round_trip_load)
    - migrations/PATTERN.md (the pattern doc shipped in Plan 01)
  </read_first>
  <action>
    Create `.planning/decisions/ADR-007-schema-versioning.md`:

    ```markdown
    # ADR-007 — Schema Versioning Placement (per-file + per-record + Python migrations)

    Status: ACCEPTED
    Date: 2026-05-03
    Deciders: user (CONTEXT.md interactive discuss, 2026-05-03)
    Implements: D-20, D-21, D-22, D-26, VER-01, VER-02, VER-03, VER-04

    > AI 接力开发指南: This ADR locks the schema-versioning model for the entire project. The model is "both per-file and per-record version, with Python+ruamel.yaml migrations." Read this before bumping ontology/VERSION or writing your first migration script. The migration pattern doc lives at migrations/PATTERN.md (Phase 2 deliverable).

    ## Context

    Schema evolution requires three independent version axes:

    1. **Project ontology release version** (`ontology/VERSION`): the version the entire schema set advertises. Starts `0.1.0`.
    2. **Per-schema-file version** (in each schema's `description` or as a sidecar): the schema's evolution within the current ontology release. Used to coordinate review during a release window.
    3. **Per-record schema_version** (in every entity / relation YAML instance): the schema version this record was written against. Frozen at write time. CI rejects records older than N-1 versions.

    Without (3), migrating an instance YAML from `schema_version: 0.1.0` to `0.3.0` requires guessing what `0.2.0` looked like at the time the YAML was written. With (3), the migration runner reads the field and runs the right chain of migration scripts.

    Migrations need to (a) preserve YAML comments (otherwise human review is destroyed), (b) be idempotent (safe to re-run), (c) use a familiar Python toolchain so Phase 3 validators (also Python) can share dependencies.

    ## Decision

    1. **`ontology/VERSION`** — single-line semver, starts `0.1.0`. Bumped on every schema set release. Phase 2 ships `0.1.0`.
    2. **`ontology/CHANGELOG.md`** — Keep a Changelog format. Every schema bump (additive or breaking) lands an entry on the same PR. `## 0.1.0` initial entry shipped in Phase 2.
    3. **Per-record `schema_version`** — REQUIRED on every entity and relation instance YAML. Type: semver string (`^\d+\.\d+\.\d+$`). Defined as `_meta.schema.json#/$defs/schemaVersionString` and referenced by both entity.base + relation.base.
    4. **N-1 tolerance** — Phase 3 validator accepts records whose `schema_version` is current or one major-or-minor below; rejects older. Tolerance window documented in error messages.
    5. **Migrations are Python (D-26)** — `migrations/<from>_to_<to>.py`. ruamel.yaml YAML() class for round-trip with comment preservation; jsonschema for pre/post validation gates.
    6. **Migration template** — `migrations/0_1_0_to_template.py.example` (Phase 2 deliverable). Copied to a real `0_1_0_to_0_2_0.py` when the first migration ships.
    7. **Pattern doc** — `migrations/PATTERN.md` (Phase 2 deliverable). Mandatory reading before writing any migration script.

    ## Rationale

    - Per-file `version` alone (without per-record `schema_version`) leaves us blind to which historical schema each instance was written against — migration becomes guesswork.
    - Per-record `schema_version` alone (without per-file version) is fine for instances but doesn't track evolution within a release window.
    - Both is cheap and covers both audiences (instance authors and schema reviewers).
    - Python over Bash/yq/sed: yq drops comments and reorders keys; sed breaks YAML structure on edge cases (multiline strings, anchors, merge keys); Python+ruamel.yaml is the canonical idiom in 2026 (`[VERIFIED: yaml.dev/doc/ruamel.yaml/detail]`).
    - ruamel.yaml `YAML()` class over deprecated `round_trip_load`: see Pitfall #10 in 02-RESEARCH.md. `round_trip_load` removed in ruamel.yaml 0.19+.

    ## Consequences

    - `_meta.schema.json` exposes `$defs/schemaVersionString` (Plan 01 deliverable)
    - `entity.base.schema.json` and `relation.base.schema.json` REQUIRE the `schema_version` field on every leaf record (Plans 02, 03)
    - Phase 3 validator implements the N-1 tolerance + clear error messages (Pitfall #6)
    - Phase 4+ instance YAMLs all carry `schema_version: "0.1.0"`
    - First real migration script lands when `ontology/VERSION` bumps to `0.2.0` (likely Phase 4+ if Configuration entity is added per ADR-002)

    ## References

    - REQUIREMENTS.md VER-01..04
    - 02-CONTEXT.md D-20, D-21, D-22, D-26
    - 02-RESEARCH.md Gap Resolution #5 (ruamel.yaml idiom); Pitfall #6 (schema-version mismatch); Pitfall #10 (round_trip_load deprecation)
    - migrations/PATTERN.md (the actual pattern doc)
    - migrations/0_1_0_to_template.py.example (template)
    ```
  </action>
  <verify>
    <automated>test -f .planning/decisions/ADR-007-schema-versioning.md &amp;&amp; grep -q 'D-20' .planning/decisions/ADR-007-schema-versioning.md &amp;&amp; grep -q 'D-22' .planning/decisions/ADR-007-schema-versioning.md &amp;&amp; grep -q 'ruamel.yaml' .planning/decisions/ADR-007-schema-versioning.md &amp;&amp; grep -q 'YAML()' .planning/decisions/ADR-007-schema-versioning.md &amp;&amp; grep -q 'AI 接力开发指南' .planning/decisions/ADR-007-schema-versioning.md &amp;&amp; ! grep -q 'round_trip_load' .planning/decisions/ADR-007-schema-versioning.md</automated>
  </verify>
  <acceptance_criteria>
    - File exists; `grep -q "ACCEPTED" .planning/decisions/ADR-007-schema-versioning.md` exits 0
    - All implemented IDs cited: `for r in D-20 D-21 D-22 D-26 VER-01 VER-02 VER-03 VER-04; do grep -q "$r" .planning/decisions/ADR-007-schema-versioning.md || exit 1; done` exits 0
    - `grep -q 'YAML()' .planning/decisions/ADR-007-schema-versioning.md` exits 0
    - `! grep -q 'round_trip_load' .planning/decisions/ADR-007-schema-versioning.md` (Pitfall #10: zero hits)
    - `grep -q 'N-1 tolerance' .planning/decisions/ADR-007-schema-versioning.md` exits 0
    - `grep -q 'migrations/PATTERN.md' .planning/decisions/ADR-007-schema-versioning.md` exits 0 (cross-reference)
    - All ADR sections present (Status / Date / Deciders / Implements / Context / Decision / Rationale / Consequences / References)
    - `grep -q "AI 接力开发指南" .planning/decisions/ADR-007-schema-versioning.md` exits 0
  </acceptance_criteria>
  <done>ADR-007 locks the per-file + per-record dual versioning model, names Python+ruamel.yaml as the migration toolchain, and references the migration pattern doc and template shipped in Plan 01.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| `entity.base.schema.json` → leaf entity schemas (Plans 04..07) | If base schema is wrong, all 22 leaf schemas inherit the mistake. Meta-validation catches structural issues. |
| ADR-002 → executor authoring leaf schemas | If ADR field-set is vague, executor improvises and decisions drift. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-02-02-01 | Tampering | entity.base uses additionalProperties:false → silently rejects baseFields | mitigate | Pitfall #1 lock in acceptance criteria; explicit grep test that string is absent |
| T-02-02-02 | Repudiation | ADR-002 doesn't enumerate field shapes → executor invents fields | mitigate | ADR-002 explicit field tables for each accepted entity; tasks in Plans 04+07 reference the table verbatim |
| T-02-02-03 | Information Disclosure | ADR-007 forgets ruamel.yaml deprecation lesson → next migration uses round_trip_load | mitigate | ADR-007 cites Pitfall #10 by ID; explicit "zero hits for round_trip_load" acceptance test |
</threat_model>

<verification>
- `check-jsonschema --check-metaschema ontology/schemas/entity.base.schema.json` exits 0
- `pre-commit run --all-files` exits 0
- All 3 files committed atomically
</verification>

<success_criteria>
- entity.base.schema.json validates as Draft 2020-12 and composes _meta.schema.json correctly
- ADR-002 documents the 4 entity-addition decisions with explicit field tables
- ADR-007 documents the dual versioning model + Python migration toolchain choice
- Pitfall #1 lock confirmed (zero `additionalProperties` strings) on entity.base
- Pitfall #9 lock confirmed (`$schema` declares Draft 2020-12)
- All 3 files committed via gsd-tools (atomic per task)
</success_criteria>

<output>
After completion, create `.planning/phases/02-ontology-schema-v0-1-0/02-02-SUMMARY.md` with:
- entity.base.schema.json composition path verified (allOf $ref to _meta baseFields)
- ADR-002 field tables (executors in Plans 04, 05, 06, 07 should consult these tables verbatim)
- ADR-007 location of N-1 tolerance rule (Phase 3 validator implementation pointer)
- Confirmation Pitfall #1 + #9 holds
</output>

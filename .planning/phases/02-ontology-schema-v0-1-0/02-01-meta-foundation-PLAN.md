---
phase: 02-ontology-schema-v0-1-0
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - ontology/_meta.schema.json
  - ontology/VERSION
  - ontology/CHANGELOG.md
  - migrations/PATTERN.md
  - migrations/0_1_0_to_template.py.example
  - instances/_pending/README.md
  - .planning/decisions/ADR-001-reserved.md
  - .planning/decisions/ADR-005-provenance-enum.md
autonomous: true
requirements:
  - PROV-01
  - PROV-02
  - PROV-03
  - PROV-04
  - PROV-05
  - VER-01
  - VER-02
  - VER-04
must_haves:
  truths:
    - "_meta.schema.json self-validates as Draft 2020-12 (--check-metaschema exits 0)"
    - "_meta.schema.json defines $defs/{provenance,confidence,source,baseFields,uri,internalId,isoDateTime,i18nLabel} composable for every entity/relation"
    - "provenance.method enum is exactly [human, ai_extracted, hybrid_reviewed] (verbatim per D-16)"
    - "H-Darrieus REJECT condition documented verbatim in $defs/provenance description"
    - "ontology/VERSION reads 0.1.0 (semver pattern)"
    - "ontology/CHANGELOG.md has ## 0.1.0 initial-release entry"
    - "migrations/PATTERN.md documents the modern ruamel.yaml YAML() class pattern (NOT round_trip_load)"
    - "instances/_pending/README.md documents the hybrid_reviewed promotion gate"
    - "ADR-001 reserved-placeholder file exists; ADR-005 documents the provenance enum + H-Darrieus rule"
  artifacts:
    - path: "ontology/_meta.schema.json"
      provides: "Composition root: provenance + confidence + source + baseFields + i18nLabel + uri/internalId/isoDateTime helpers"
      contains: '"$schema": "https://json-schema.org/draft/2020-12/schema"'
    - path: "ontology/VERSION"
      provides: "Single-line semver string 0.1.0"
    - path: "ontology/CHANGELOG.md"
      provides: "Initial 0.1.0 release entry pointing at ADR-002..007"
    - path: "migrations/PATTERN.md"
      provides: "ruamel.yaml YAML() round-trip pattern with .ca.items comment-preservation"
    - path: "migrations/0_1_0_to_template.py.example"
      provides: "Migration script template (not executed in Phase 2)"
    - path: "instances/_pending/README.md"
      provides: "Quarantine directory README + canonical-promotion gate (D-17)"
    - path: ".planning/decisions/ADR-001-reserved.md"
      provides: "Placeholder ADR-001 reserved for Phase 6 PRD-v0/v1 split documentation"
    - path: ".planning/decisions/ADR-005-provenance-enum.md"
      provides: "Decision record for provenance.method enum + H-Darrieus REJECT condition"
  key_links:
    - from: "ontology/_meta.schema.json#/$defs/baseFields"
      to: "ontology/_meta.schema.json#/$defs/{uri,provenance,confidence,source}"
      via: "$ref composition"
    - from: "instances/_pending/README.md"
      to: "ADR-005-provenance-enum.md"
      via: "promotion-gate citation (D-17)"
---

<objective>
Build the Phase 2 composition root: `_meta.schema.json` (the schema every other Phase 2 schema composes via $ref), the version/changelog scaffolding, the migration pattern documentation, the _pending quarantine README, and the two ADRs that nothing else can depend on (ADR-001 reservation + ADR-005 provenance enum).

Purpose: Without this plan landing first, NO downstream entity or relation schema can validate. Pattern #1 from RESEARCH.md (`_meta.schema.json` as Composition Root) is the load-bearing decision for the entire phase.
Output: 8 files: 1 root schema + 2 ontology meta files + 2 migrations files + 1 quarantine README + 2 ADRs.
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
@.planning/phases/02-ontology-schema-v0-1-0/02-VALIDATION.md
@.pre-commit-config.yaml

<interfaces>
<!-- Pattern from RESEARCH.md Code Example #1 — copy this skeleton verbatim, adjusting only what notes call out. -->
<!-- Pitfall #1: NEVER use additionalProperties: false. Always unevaluatedProperties: false. -->
<!-- Pitfall #9: every schema MUST declare $schema = https://json-schema.org/draft/2020-12/schema -->
<!-- D-16: provenance.method enum is exactly ["human", "ai_extracted", "hybrid_reviewed"] -->
<!-- D-17: hybrid_reviewed promotion gate requires non-empty reviewer URI + reviewed_at -->
<!-- D-23 / D-24 / D-25: URI form aviationkb://<type>/<slug>@<version>; internal id <prefix>:<kebab-slug>; max 64 chars -->
<!-- Phase 2 quarantine dir already exists: instances/_pending/.gitkeep present -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author ontology/_meta.schema.json composition root</name>
  <files>ontology/_meta.schema.json</files>
  <read_first>
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Code Example #1 — copy verbatim adjusting only file path; Pitfall #1, #9; Architecture Pattern #1)
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-13, D-14, D-16, D-17, D-23, D-24, D-25)
    - .planning/PROJECT.md (Core Value — H-Darrieus failure mode)
  </read_first>
  <action>
    Create `ontology/_meta.schema.json` as a JSON Schema Draft 2020-12 document. Use Code Example #1 from RESEARCH.md as the literal starting point. The file MUST contain (all under `$defs`):

    1. `"$schema": "https://json-schema.org/draft/2020-12/schema"` at the top (Pitfall #9 lock)
    2. `"$id": "https://aviation-knowledge-base.local/ontology/_meta.schema.json"`
    3. `"title"` and `"description"` — description must explicitly state: "Composition root for all entity/relation schemas. Pattern: allOf + unevaluatedProperties: false (NEVER additionalProperties: false). H-Darrieus REJECT rule lives in $defs/provenance description and is enforced in Phase 3 validator."

    `$defs` MUST include all of these sub-schemas (copy from Code Example #1 unless noted):
    - `uri` — type string, format uri, pattern `^aviationkb://[a-z][a-z-]*\/[a-z0-9]+(-[a-z0-9]+)*@[0-9]+$` (D-23)
    - `internalId` — type string, pattern `^[a-z]+:[a-z0-9]+(-[a-z0-9]+)*$`, maxLength 80 (D-24/D-25); description enumerates all 22 type prefixes from D-24
    - `isoDateTime` — type string, format date-time
    - `i18nLabel` — type object, properties zh+en (both required strings), unevaluatedProperties: false (D-14)
    - `provenance` — properties: method (enum: human|ai_extracted|hybrid_reviewed per D-16), actor ($ref #/$defs/uri), actor_role (string minLength 1), created_at ($ref #/$defs/isoDateTime), reviewer ($ref #/$defs/uri — optional), reviewed_at ($ref #/$defs/isoDateTime — optional), tool (string). REQUIRED: method, actor, actor_role, created_at. unevaluatedProperties: false. Description MUST contain VERBATIM the H-Darrieus REJECT condition: "ENFORCED IN PHASE 3 VALIDATOR — H-Darrieus REJECT condition: (method == 'ai_extracted') AND (confidence.score > 0.85) AND (reviewer is null OR reviewer == '') → REJECT. Promotion from instances/_pending/ to canonical (D-17) requires method == 'hybrid_reviewed' AND non-empty reviewer URI AND reviewed_at timestamp." This satisfies PROV-04 at the schema-documentation level.
    - `confidence` — properties: score (number minimum 0.0 maximum 1.0), rationale (string minLength 20), calibration_method (optional string). REQUIRED: score, rationale. unevaluatedProperties: false. (D-13)
    - `source` — properties: document_id ($ref uri), locator (object: anyOf [page|section|paragraph]; unevaluatedProperties: false), retrieval (object: url+retrieved_at required, optional content_hash with pattern `^sha256:[a-f0-9]{64}$`), effective_date (string format date). REQUIRED: document_id, locator, retrieval. unevaluatedProperties: false. (PROV-03)
    - `baseFields` — type object, properties: id ($ref uri), provenance ($ref provenance), confidence ($ref confidence), source ($ref source). REQUIRED: id, provenance, confidence, source. (Used by entity.base + relation.base via allOf.)
    - `schemaVersionString` — type string, pattern `^\d+\.\d+\.\d+$`. (Reused by every leaf schema for the schema_version field — VER-03 contract.)

    Use 2-space indentation, sorted keys are NOT required, but include trailing newline at EOF (yamllint hook expects this on YAML — JSON files via end-of-file-fixer hook also require it).
  </action>
  <verify>
    <automated>check-jsonschema --check-metaschema ontology/_meta.schema.json &amp;&amp; jq -e '.["$defs"].provenance.properties.method.enum == ["human","ai_extracted","hybrid_reviewed"]' ontology/_meta.schema.json &amp;&amp; grep -q "H-Darrieus" ontology/_meta.schema.json &amp;&amp; ! grep -q '"additionalProperties"' ontology/_meta.schema.json &amp;&amp; grep -q '"unevaluatedProperties"' ontology/_meta.schema.json &amp;&amp; jq -e '.["$schema"] == "https://json-schema.org/draft/2020-12/schema"' ontology/_meta.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - `check-jsonschema --check-metaschema ontology/_meta.schema.json` exits 0 (Pitfall #9: meta-validates against Draft 2020-12 metaschema)
    - `jq '.["$defs"] | keys' ontology/_meta.schema.json` returns array containing all 9 names: baseFields, confidence, i18nLabel, internalId, isoDateTime, provenance, schemaVersionString, source, uri
    - `jq -r '.["$defs"].provenance.properties.method.enum | join(",")' ontology/_meta.schema.json` returns exactly `human,ai_extracted,hybrid_reviewed`
    - `grep -c "H-Darrieus" ontology/_meta.schema.json` returns ≥1 (PROV-04 description-level satisfaction)
    - `grep -q "hybrid_reviewed" ontology/_meta.schema.json` exits 0 (D-17 reference)
    - `! grep -q '"additionalProperties"' ontology/_meta.schema.json` (Pitfall #1: zero hits)
    - `grep -c '"unevaluatedProperties": false' ontology/_meta.schema.json` returns ≥6 (every nested object uses it)
    - `jq -e '.["$defs"].confidence.properties.score.maximum == 1.0 and .["$defs"].confidence.properties.score.minimum == 0.0' ontology/_meta.schema.json` exits 0 (D-13 decimal scale)
    - `jq -e '.["$defs"].confidence.properties.rationale.minLength == 20' ontology/_meta.schema.json` exits 0 (D-13 ≥1 sentence)
    - `jq -e '.["$defs"].source.required | contains(["document_id", "locator", "retrieval"])' ontology/_meta.schema.json` exits 0 (PROV-03)
    - `jq -r '.["$defs"].uri.pattern' ontology/_meta.schema.json` matches `^aviationkb://` prefix (D-23)
  </acceptance_criteria>
  <done>_meta.schema.json self-validates against Draft 2020-12 metaschema, exposes all $defs needed by entity.base + relation.base + every leaf schema, and embeds the H-Darrieus REJECT condition verbatim in the provenance description.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Create ontology/VERSION + ontology/CHANGELOG.md initial release entries</name>
  <files>ontology/VERSION, ontology/CHANGELOG.md</files>
  <read_first>
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-20, D-21)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Open Question #4 — CHANGELOG entry timing)
  </read_first>
  <action>
    Create `ontology/VERSION` — single line `0.1.0\n` (no other content; trailing newline mandatory for end-of-file-fixer hook).

    Create `ontology/CHANGELOG.md` with this exact structure:

    ```markdown
    # Ontology Changelog

    > AI 接力开发指南: This file is the truth source for ontology version transitions. Every schema change (additive or breaking) MUST land a CHANGELOG entry in the same PR. Format: Keep a Changelog (https://keepachangelog.com); semver per ontology/VERSION. Cross-reference: schema field shapes locked in ADR-004; provenance enum locked in ADR-005; entity additions in ADR-002; relation additions in ADR-003; triple export in ADR-006; schema versioning in ADR-007.

    ## 0.1.0 — 2026-05-03

    Initial schema set.

    ### Added
    - `_meta.schema.json` composition root: `$defs/{baseFields, provenance, confidence, source, uri, internalId, isoDateTime, i18nLabel, schemaVersionString}`
    - `entity.base.schema.json` + 20 entity-type schemas (17 baseline + Material + TestCase + TestReport + Person + Organization)
    - `relation.base.schema.json` + 16 relation-type schemas (13 baseline + interfaces_with + complies_with + applicable_during_phase)
    - Vocabularies: `ata-chapters.yaml` (~70 ATA iSpec 2200 Revision 2024.1 chapters), `jurisdictions.yaml`, `provenance-methods.yaml`
    - Mappings: `ata-to-iso10303.md` (deferred-to-v0.3+ placeholder), `s1000d-dmc-reserved.md` (Issue 6.0 DMC structural breakdown)
    - Migrations: `migrations/PATTERN.md` + `migrations/0_1_0_to_template.py.example` (ruamel.yaml YAML() class pattern)
    - ADRs: ADR-001 (reserved for Phase 6 PRD split), ADR-002 (entity additions), ADR-003 (relation additions), ADR-004 (field shapes), ADR-005 (provenance enum + H-Darrieus rule), ADR-006 (triple export JSONL choice), ADR-007 (schema versioning placement)

    ### Notes
    - JSON Schema Draft 2020-12 throughout. Composition pattern: `allOf` + `$ref` + `unevaluatedProperties: false`. NEVER `additionalProperties: false` (Pitfall #1).
    - `provenance.method` enum: `human | ai_extracted | hybrid_reviewed` (D-16); H-Darrieus REJECT condition documented in `_meta.schema.json#/$defs/provenance.description`; validator implementation lands in Phase 3 (VAL-01..05).
    - Configuration / EffectivityRange entity DEFERRED to v0.2.0 (D-03, ADR-002).
    - has_revision and generated_by are NOT relations — internalized as fields per D-07 (`version_history[]`) and D-09 (`provenance.actor` + `source.tool`).
    ```

    Both files committed in this single task (one commit).
  </action>
  <verify>
    <automated>grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' ontology/VERSION &amp;&amp; grep -q "## 0.1.0" ontology/CHANGELOG.md &amp;&amp; grep -q "AI 接力开发指南" ontology/CHANGELOG.md &amp;&amp; grep -q "ADR-002" ontology/CHANGELOG.md</automated>
  </verify>
  <acceptance_criteria>
    - `cat ontology/VERSION` outputs exactly `0.1.0` followed by a single newline
    - `wc -l ontology/VERSION` outputs `1`
    - `grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' ontology/VERSION` exits 0 (VER-01)
    - `grep -q "^## 0.1.0" ontology/CHANGELOG.md` exits 0 (VER-02 — semver heading present)
    - `grep -q "AI 接力开发指南" ontology/CHANGELOG.md` exits 0 (R12/AIH discipline)
    - `grep -c "ADR-00" ontology/CHANGELOG.md` returns ≥6 (cross-references all 6 ADRs)
    - `grep -q "Configuration / EffectivityRange entity DEFERRED" ontology/CHANGELOG.md` exits 0 (D-03 deferral noted)
    - `grep -q "has_revision and generated_by" ontology/CHANGELOG.md` exits 0 (D-07/D-09 internalization noted)
    - `pre-commit run end-of-file-fixer --files ontology/VERSION ontology/CHANGELOG.md` exits 0
  </acceptance_criteria>
  <done>VERSION file holds `0.1.0`; CHANGELOG.md has the initial 0.1.0 release entry citing all six ADRs and the key deferral/internalization decisions.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Create migrations/PATTERN.md + migrations/0_1_0_to_template.py.example</name>
  <files>migrations/PATTERN.md, migrations/0_1_0_to_template.py.example</files>
  <read_first>
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Gap Resolution #5 — ruamel.yaml idiom; Pitfall #10 — round_trip_load deprecation)
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-22, D-26)
  </read_first>
  <action>
    Create `migrations/PATTERN.md` documenting the canonical migration idiom. Required sections:

    ```markdown
    # Schema Migration Pattern (v0.1.0)

    > AI 接力开发指南: Phase 2 ships only this pattern doc + the `0_1_0_to_template.py.example` boilerplate. The first real migration script lands when ontology/VERSION bumps from 0.1.0 → 0.2.0 (likely Phase 4+ when Configuration entity is added per D-03 deferral). All migrations follow the rules below verbatim.

    ## Tooling

    - Python 3.9+ (matches Phase 3 validator runtime)
    - `ruamel.yaml >=0.17, <0.19` — comment-preserving round-trip
    - `jsonschema >=4.18` — Draft 2020-12 validation pre/post migration

    Add to `requirements-dev.txt` (NOT runtime requirements) when first migration ships.

    ## File-naming convention

    `migrations/<from_version>_to_<to_version>.py`. Slashes converted to underscores. Example: `migrations/0_1_0_to_0_2_0.py`.

    ## Canonical YAML edit pattern

    Use the modern `YAML()` class (NOT `round_trip_load` — deprecated since ruamel.yaml 0.15, removed in 0.19+; see Pitfall #10 in 02-RESEARCH.md):

    ```python
    from ruamel.yaml import YAML
    yaml = YAML()                  # round-trip mode by default in ≥0.15
    yaml.preserve_quotes = True
    yaml.width = 200               # match .yamllint line-length config
    data = yaml.load(path)
    # ... edit data in-place ...
    yaml.dump(data, path)
    ```

    ## Comment-preservation idiom

    To rename a key while keeping its trailing comment:

    ```python
    if "old_field" in data:
        data["new_field"] = data.pop("old_field")
        if hasattr(data, "ca") and "old_field" in data.ca.items:
            data.ca.items["new_field"] = data.ca.items.pop("old_field")
    ```

    `data.ca.items` is ruamel.yaml's "comment attribute" mapping — the only documented way to move a comment with its key.

    ## Idempotency rule

    Every migration script MUST be safe to re-run on already-migrated YAML. Check the `schema_version` field at the top:

    ```python
    if data.get("schema_version") == TARGET_VERSION:
        return  # already migrated; no-op
    ```

    ## Validation gates

    1. Pre-migration: `check-jsonschema --schemafile ontology/schemas/<entity>.schema.json <yaml-file>` (file passes the OLD schema)
    2. Run migration script
    3. Post-migration: `check-jsonschema --schemafile ontology/schemas/<entity>.schema.json <yaml-file>` against the NEW schema (file passes the NEW schema)

    Migration scripts MUST NOT validate against schemas; that is the validator's job (Phase 3, VAL-01..05). Migration scripts only transform.

    ## Test fixtures

    Phase 3 will land `tests/fixtures/migration/` with `before_*.yaml` + `expected_after_*.yaml` pairs per migration. Migration scripts ARE NOT tested in Phase 2.

    ## See also

    - 02-RESEARCH.md §Gap Resolution #5 (verified pattern source)
    - 02-RESEARCH.md §Pitfall #10 (round_trip_load deprecation)
    - ADR-007 (Schema versioning placement — D-20/D-21/D-22)
    ```

    Create `migrations/0_1_0_to_template.py.example` (note `.example` suffix so neither yamllint nor pre-commit treat it as runnable Python; intent is "template for future migrations"). Content per RESEARCH.md Gap Resolution #5 verbatim:

    ```python
    # migrations/0_1_0_to_template.py.example
    # Migration template — ruamel.yaml comment-preserving YAML edit
    # Pattern verified against ruamel.yaml >=0.17 (uses YAML() class, not deprecated round_trip_load)
    # Source: ruamel.yaml docs (yaml.dev/doc/ruamel.yaml/detail/) + 02-RESEARCH.md Gap Resolution #5
    # AI 接力开发指南: Copy this file to migrations/<from>_to_<to>.py when shipping the first real migration. Read migrations/PATTERN.md first.

    from pathlib import Path
    from ruamel.yaml import YAML

    SOURCE_VERSION = "0.1.0"
    TARGET_VERSION = "0.2.0"


    def migrate_one(path: Path) -> None:
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 200
        data = yaml.load(path)

        # Idempotency guard — re-running on already-migrated YAML is a no-op.
        if data.get("schema_version") == TARGET_VERSION:
            return

        # 1) Bump schema_version
        data["schema_version"] = TARGET_VERSION

        # 2) Example: rename a field while preserving its trailing comment
        if "old_field" in data:
            data["new_field"] = data.pop("old_field")
            if hasattr(data, "ca") and "old_field" in data.ca.items:
                data.ca.items["new_field"] = data.ca.items.pop("old_field")

        # 3) Example: add a new required field with a comment
        data["new_required_field"] = "TBD"
        data.yaml_add_eol_comment("filled by migration; review before commit", "new_required_field")

        yaml.dump(data, path)


    if __name__ == "__main__":
        import sys
        for p in sys.argv[1:]:
            migrate_one(Path(p))
    ```

    Both files in one commit.
  </action>
  <verify>
    <automated>grep -q 'YAML()' migrations/PATTERN.md &amp;&amp; grep -q '.ca.items' migrations/PATTERN.md &amp;&amp; ! grep -q 'round_trip_load' migrations/PATTERN.md &amp;&amp; grep -q 'TARGET_VERSION' migrations/0_1_0_to_template.py.example &amp;&amp; python3 -c "import ast; ast.parse(open('migrations/0_1_0_to_template.py.example').read())"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -q 'YAML()' migrations/PATTERN.md` exits 0 (modern class pattern)
    - `grep -q '.ca.items' migrations/PATTERN.md` exits 0 (comment-preservation idiom)
    - `! grep -q 'round_trip_load' migrations/PATTERN.md` (Pitfall #10: zero hits in pattern doc)
    - `grep -q 'AI 接力开发指南' migrations/PATTERN.md` exits 0 (R12 discipline)
    - `grep -q '0_1_0_to_0_2_0.py' migrations/PATTERN.md` exits 0 (file-naming convention)
    - `python3 -c "import ast; ast.parse(open('migrations/0_1_0_to_template.py.example').read())"` exits 0 (syntactically valid Python despite `.example` suffix)
    - `grep -q 'TARGET_VERSION = "0.2.0"' migrations/0_1_0_to_template.py.example` exits 0
    - `grep -q 'def migrate_one' migrations/0_1_0_to_template.py.example` exits 0
    - `! grep -q 'round_trip_load' migrations/0_1_0_to_template.py.example` (Pitfall #10)
  </acceptance_criteria>
  <done>migrations/PATTERN.md documents the canonical ruamel.yaml YAML() pattern with comment preservation; 0_1_0_to_template.py.example is parseable Python and demonstrates the idempotent migration shape.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 4: Create instances/_pending/README.md quarantine doc</name>
  <files>instances/_pending/README.md</files>
  <read_first>
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-16, D-17 — promotion gate)
    - .planning/PROJECT.md (Core Value — H-Darrieus failure mode)
    - instances/_pending/.gitkeep (already exists, just confirm directory)
  </read_first>
  <action>
    Create `instances/_pending/README.md` per PROV-05. Content:

    ```markdown
    # `instances/_pending/` — AI-Extracted Quarantine

    > AI 接力开发指南: This directory holds entity / relation YAML records that were created by AI extraction (`provenance.method = "ai_extracted"`) and have NOT yet been human-reviewed. They are intentionally separated from canonical content under `instances/entities/` and `instances/relations/` so the H-Darrieus failure mode (cited but unverified content) cannot leak into the knowledge base.

    ## Promotion Gate (D-17)

    A YAML record is allowed to move from `instances/_pending/` to canonical `instances/entities/` or `instances/relations/` ONLY when ALL of the following are true:

    1. `provenance.method == "hybrid_reviewed"` (NOT `ai_extracted`; NOT `human` either — the hybrid label is the audit trail saying "AI drafted, human reviewed")
    2. `provenance.reviewer` is a non-empty Person URI (`aviationkb://person/<slug>@<version>`)
    3. `provenance.reviewed_at` is a valid ISO 8601 timestamp
    4. `confidence.score` and `confidence.rationale` are filled out (never auto-promote on score alone)
    5. `check-jsonschema --schemafile ontology/schemas/<type>.schema.json <yaml>` exits 0 against the type's full schema

    The Phase 3 validator (`scripts/validate.py`, REQ-IDs VAL-01..05) enforces these rules at CI time. Phase 2 only declares the contract.

    ## H-Darrieus REJECT Rule (PROV-04, ADR-005)

    Even if a record stays in `_pending/`, the validator REJECTS any record where:

    - `provenance.method == "ai_extracted"` AND
    - `confidence.score > 0.85` AND
    - `provenance.reviewer` is null or empty

    Rationale: high confidence on unreviewed AI output is the exact failure mode that produced the H-Darrieus fabricated-figure incident in the user's MEMORY.md. We refuse to be that.

    ## Workflow

    1. AI tool (Claude / Codex / DeepSeek) extracts a candidate entity or relation from a source document, emits YAML with `provenance.method: "ai_extracted"` + `confidence.score` + `confidence.rationale` + structured `source.{document_id, locator, retrieval}`.
    2. YAML lands here as `instances/_pending/<entity-or-relation>/<slug>.yaml`.
    3. Human reviewer reads, edits, sets `provenance.reviewer` to their Person URI, sets `provenance.reviewed_at` to today's timestamp, flips `provenance.method` to `"hybrid_reviewed"`.
    4. PR review confirms; merging the PR moves the file to canonical.

    ## See also

    - `.planning/decisions/ADR-005-provenance-enum.md` — full provenance method enum + H-Darrieus rule
    - `ontology/_meta.schema.json#/$defs/provenance` — schema-level definition
    - Phase 3 plan (validators) — enforces the rule at CI time
    - Phase 4 plan (DEMO-06) — ships ≥1 record demonstrating this pattern end-to-end
    ```
  </action>
  <verify>
    <automated>grep -q 'hybrid_reviewed' instances/_pending/README.md &amp;&amp; grep -q 'H-Darrieus' instances/_pending/README.md &amp;&amp; grep -q 'AI 接力开发指南' instances/_pending/README.md &amp;&amp; grep -q 'ADR-005' instances/_pending/README.md</automated>
  </verify>
  <acceptance_criteria>
    - File `instances/_pending/README.md` exists
    - `grep -q "hybrid_reviewed" instances/_pending/README.md` exits 0 (D-17 promotion gate)
    - `grep -q "H-Darrieus" instances/_pending/README.md` exits 0 (PROV-04 rule cited by name)
    - `grep -q "AI 接力开发指南" instances/_pending/README.md` exits 0 (R12 discipline)
    - `grep -q "ADR-005" instances/_pending/README.md` exits 0 (cross-reference to ADR-005)
    - `grep -q "ontology/_meta.schema.json" instances/_pending/README.md` exits 0 (schema-level cross-reference)
    - `grep -q "score > 0.85" instances/_pending/README.md` exits 0 (verbatim threshold from D-16)
  </acceptance_criteria>
  <done>_pending README documents the promotion gate, the H-Darrieus REJECT rule, and the AI→human review workflow. Cross-references ADR-005 and _meta.schema.json.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 5: Author ADR-001 (reserved placeholder) + ADR-005 (provenance enum)</name>
  <files>.planning/decisions/ADR-001-reserved.md, .planning/decisions/ADR-005-provenance-enum.md</files>
  <read_first>
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-16, D-17 — provenance enum + promotion gate; <specifics> section — ADR numbering rule)
    - .planning/PROJECT.md (Core Value — H-Darrieus failure mode)
  </read_first>
  <action>
    Create `.planning/decisions/` directory if it doesn't exist (gsd-tools will create on commit).

    Create `.planning/decisions/ADR-001-reserved.md`:

    ```markdown
    # ADR-001 — Reserved (Phase 6 will document PRD-v0/v1 split)

    Status: RESERVED
    Date: 2026-05-03
    Deciders: project-init (Claude Opus 4.7)

    > AI 接力开发指南: This ADR is a placeholder. Per `02-CONTEXT.md` <specifics>, ADR-001 is reserved for Phase 6 retrospectively documenting the project-init decision to split the PRD into v0 (directional, Phase 1) and v1 (final, Phase 6). Do not edit this file in Phase 2. The numbering reservation prevents future Claude/Codex sessions from reusing ADR-001 for an unrelated decision.

    ## Reservation Reason

    Project init in 2026-05-03 split `PRD-01` (v0 directional, shipped Phase 1) and `PRD-02` (v1 final, shipped Phase 6). The split was a structural decision worth ADR-grade documentation, but it was made before the ADR convention existed in this project. Phase 6 will land the actual ADR content here, retrospectively.

    ## See also

    - `.planning/REQUIREMENTS.md` PRD-01 / PRD-02 entries
    - `.planning/ROADMAP.md` Phase 1 / Phase 6 sections
    - `.planning/design/PRD_v0.md` (existing Phase 1 deliverable)
    ```

    Create `.planning/decisions/ADR-005-provenance-enum.md`:

    ```markdown
    # ADR-005 — Provenance Method Enum + H-Darrieus REJECT Rule

    Status: ACCEPTED
    Date: 2026-05-03
    Deciders: user (CONTEXT.md interactive discuss, 2026-05-03)
    Implements: D-16, D-17, PROV-01, PROV-04, PROV-05

    > AI 接力开发指南: This ADR defines the provenance method enum used on every entity and relation in the knowledge base. The enum and the H-Darrieus REJECT rule are the single most load-bearing audit-discipline decision in the project. Do not change this enum without a full retrospective showing what failure mode the change addresses; doing so silently breaks the Core Value commitment.

    ## Context

    Per PROJECT.md Core Value, every knowledge record must be traceable to its source AND must distinguish human-authored vs AI-extracted content. The user's MEMORY.md records the H-Darrieus 2014 paper-reproduction incident: an AI session captioned a non-existent figure with high confidence and the result entered downstream documentation. The same failure pattern in an aviation knowledge base is a safety problem.

    The enum has to (a) be small enough that a human reviewer can hold it in their head, (b) draw a bright line between "AI alone said this" and "AI drafted + human signed off", and (c) feed a deterministic validator rule that REJECTS the H-Darrieus failure mode at CI time.

    ## Decision

    `provenance.method` is a JSON Schema enum with EXACTLY three values:

    | Value | Meaning |
    |-------|---------|
    | `human` | A human authored this record without AI assistance. `provenance.actor` is a Person URI. `reviewer` not required. |
    | `ai_extracted` | An AI tool extracted this record from a source document. `provenance.actor` MAY be a Person URI (the operator) or an Organization URI; `provenance.tool` SHOULD identify the model (e.g. `claude-opus-4-7`). Records with this method MUST live in `instances/_pending/` until promoted. |
    | `hybrid_reviewed` | An AI tool drafted, a human reviewed, edited, and signed off. `provenance.reviewer` is a non-empty Person URI; `provenance.reviewed_at` is an ISO 8601 timestamp. ONLY records with this method are allowed in canonical `instances/entities/` and `instances/relations/`. |

    ### H-Darrieus REJECT Rule (PROV-04)

    The Phase 3 validator (`scripts/validators/provenance.py`) MUST reject any record where ALL of the following hold:

    1. `provenance.method == "ai_extracted"`
    2. `confidence.score > 0.85`
    3. `provenance.reviewer` is null OR empty string

    Pseudocode:

    ```python
    if (record.provenance.method == "ai_extracted"
        and record.confidence.score > 0.85
        and not record.provenance.reviewer):
        raise ValidationError(
            "H-Darrieus REJECT: high-confidence AI-extracted record without reviewer. "
            "Either lower confidence (≤0.85) and explain in rationale, "
            "or assign a reviewer and flip method to 'hybrid_reviewed'."
        )
    ```

    Phase 2 documents this rule verbatim in `ontology/_meta.schema.json#/$defs/provenance.description`. Phase 2 schema makes the 6 fields required (method, actor, actor_role, created_at on provenance; score, rationale on confidence). Phase 2 schema CANNOT enforce the cross-field REJECT condition cleanly in pure JSON Schema (would need ugly `if/then/else` with negation); the rule is enforced in Phase 3 Python validator instead.

    ### Promotion Gate (D-17 / PROV-05)

    A YAML record is allowed to move from `instances/_pending/` to canonical only when ALL of:

    1. `provenance.method == "hybrid_reviewed"`
    2. `provenance.reviewer` is a non-empty Person URI
    3. `provenance.reviewed_at` is set
    4. The record passes `check-jsonschema` against its full type schema

    ## Rationale

    - Three values (not two, not five): minimum semantic resolution that distinguishes the H-Darrieus failure pattern. `manual / auto / assisted` was considered and rejected — `assisted` is too vague to map to a validator rule.
    - Threshold `> 0.85` (not `>= 0.85`): aligns with the user's empirical observation that high-confidence AI output is the dangerous regime; values below 0.85 are explicitly tagged as "uncertain" and don't need reviewer.
    - Validator rule lives in Python, not pure schema: `if/then/else` with negation against three independent fields is unmaintainable in JSON Schema; clearer in Python.

    ## Consequences

    - Every entity/relation YAML carries a 3-value enum field — schema-required.
    - `instances/_pending/` is a real directory with a README (PROV-05), not a convention.
    - Phase 3 ships the Python validator that implements the REJECT rule with a high-priority test fixture.
    - Phase 4 demo data MUST include ≥1 `_pending/` record (DEMO-06) and ≥1 `hybrid_reviewed` canonical record.
    - Future schema evolutions cannot add new enum values without an ADR explaining the new audit semantics.

    ## References

    - PROJECT.md Core Value
    - REQUIREMENTS.md PROV-01, PROV-04, PROV-05
    - 02-CONTEXT.md D-16, D-17
    - 02-RESEARCH.md Pitfall #8 (H-Darrieus enforcement gap)
    - User MEMORY.md `cfd-ai-workbench` § "诚实性问题（2026-04-01）"
    - Phase 3 plan (forthcoming) §`scripts/validators/provenance.py`
    ```

    Both ADRs in one commit.
  </action>
  <verify>
    <automated>test -f .planning/decisions/ADR-001-reserved.md &amp;&amp; test -f .planning/decisions/ADR-005-provenance-enum.md &amp;&amp; grep -q 'RESERVED' .planning/decisions/ADR-001-reserved.md &amp;&amp; grep -q 'H-Darrieus REJECT' .planning/decisions/ADR-005-provenance-enum.md &amp;&amp; grep -q 'hybrid_reviewed' .planning/decisions/ADR-005-provenance-enum.md &amp;&amp; grep -q 'AI 接力开发指南' .planning/decisions/ADR-001-reserved.md &amp;&amp; grep -q 'AI 接力开发指南' .planning/decisions/ADR-005-provenance-enum.md</automated>
  </verify>
  <acceptance_criteria>
    - Both files exist under `.planning/decisions/`
    - ADR-001: `grep -q "RESERVED" .planning/decisions/ADR-001-reserved.md` exits 0
    - ADR-001: `grep -q "Phase 6" .planning/decisions/ADR-001-reserved.md` exits 0
    - ADR-005: `grep -q "human" ADR-005-provenance-enum.md && grep -q "ai_extracted" ADR-005-provenance-enum.md && grep -q "hybrid_reviewed" ADR-005-provenance-enum.md` exits 0 (all three enum values present)
    - ADR-005: `grep -q "score > 0.85" .planning/decisions/ADR-005-provenance-enum.md` exits 0 (threshold cited verbatim)
    - ADR-005: `grep -q "H-Darrieus" .planning/decisions/ADR-005-provenance-enum.md` exits 0
    - ADR-005: contains all required ADR sections — Status / Date / Deciders / Context / Decision / Rationale / Consequences / References (grep each header)
    - Both files: `grep -q "AI 接力开发指南"` exits 0 (R12 discipline)
  </acceptance_criteria>
  <done>ADR-001 holds the placeholder reservation; ADR-005 fully documents the provenance enum, the H-Darrieus REJECT rule (with Python pseudocode), and the canonical-promotion gate, cross-referencing PROJECT.md / 02-CONTEXT.md / Phase 3 validator location.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Schema author → schema validator | Hand-rolled JSON Schema can have typos / wrong keywords; meta-validation catches structural issues. |
| Future Claude/Codex/DeepSeek → ADR/CHANGELOG | Untrusted future maintainer reads project state; could misinterpret missing context. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-02-01-01 | Tampering | `_meta.schema.json` typo (e.g. `unevalauted Properties`) silently accepts everything | mitigate | `--check-metaschema` in this plan's verify command + Phase 3 will add it to pre-commit |
| T-02-01-02 | Repudiation | Provenance fields drift if hand-rolled per entity | mitigate | `_meta.schema.json` `$defs/provenance` is the single source; entity.base + relation.base compose via `$ref` (Plan 02 + 03) |
| T-02-01-03 | Spoofing | AI-extracted records sneak into canonical bypassing H-Darrieus rule | mitigate | Schema makes 6 provenance fields required (this plan); ADR-005 documents the REJECT rule; Phase 3 validator enforces |
| T-02-01-04 | Information Disclosure | ADR-005 does not cite H-Darrieus origin → future maintainer doesn't understand the rule's purpose | mitigate | ADR-005 cites MEMORY.md verbatim; verbatim PROJECT.md Core Value reference |
</threat_model>

<verification>
Run `pre-commit run --all-files` — must exit 0. The `check-jsonschema` hook auto-applies to `ontology/_meta.schema.json` per the existing regex.

Run `check-jsonschema --check-metaschema ontology/_meta.schema.json` — must exit 0.

Run `grep -c "H-Darrieus" ontology/_meta.schema.json .planning/decisions/ADR-005-provenance-enum.md instances/_pending/README.md` — each file should have ≥1 hit.

Run `grep -q '"additionalProperties"' ontology/_meta.schema.json` — must exit non-zero (Pitfall #1: zero hits).
</verification>

<success_criteria>
- `_meta.schema.json` self-validates against Draft 2020-12 metaschema
- `ontology/VERSION` reads `0.1.0`; `ontology/CHANGELOG.md` has 0.1.0 entry
- `migrations/PATTERN.md` documents the modern `YAML()` ruamel.yaml class pattern (no `round_trip_load`)
- `migrations/0_1_0_to_template.py.example` parses as valid Python
- `instances/_pending/README.md` documents the hybrid_reviewed promotion gate + H-Darrieus rule
- `.planning/decisions/ADR-001-reserved.md` placeholder created; `.planning/decisions/ADR-005-provenance-enum.md` fully drafted with all required ADR sections
- All 8 files committed (5 atomic gsd-tools commits, one per task)
- `pre-commit run --all-files` exits 0
</success_criteria>

<output>
After completion, create `.planning/phases/02-ontology-schema-v0-1-0/02-01-SUMMARY.md` with:
- Files created (8) and their roles
- Confirmed Pitfall #1 verification (zero `additionalProperties: false` in `_meta.schema.json`)
- Confirmed Pitfall #9 verification (every JSON schema declares `$schema = Draft 2020-12`)
- H-Darrieus rule placement confirmation (in `_meta.schema.json` description, ADR-005, _pending README, CHANGELOG cross-ref)
- Pointer for downstream Plan 02 + Plan 03: where to find `$defs/baseFields` and how to compose it
</output>

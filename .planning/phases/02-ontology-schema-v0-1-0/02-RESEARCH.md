# Phase 2: Ontology Schema v0.1.0 — Research

**Researched:** 2026-05-03
**Domain:** JSON Schema 2020-12 ontology design for aviation engineering knowledge base
**Confidence:** HIGH (gap-closure on 3 explicit + 3 implementation gaps; all 6 resolved with verified sources)
**Mode:** gap-closure (NOT ecosystem; 16 D-XX decisions in 02-CONTEXT.md are LOCKED — do not re-litigate)

## Summary

This research closes the 3 explicit research-deferred items in `02-CONTEXT.md` plus 3 implementation-knowledge gaps. The research is intentionally **narrow** because Phase 2 already has 16 ADR-grade decisions locked; it does not re-explore entity counts, relation counts, confidence shape, URI scheme, or migration language. Those are inputs, not questions.

**Verified findings (all 6 gaps resolved):**
1. ATA chapter list is **finite, well-defined, and stable** — enum-strict is feasible. ~70 used chapters in iSpec 2200 (Revision 2024.1) drawn from a 0–99 numbering space. We will ship enum-strict for known chapters with an escape pattern for "Reserved for Airline Use" (1–4) and "Unassigned" slots.
2. S1000D Issue 6 (released **2024-09-01**) DMC structure: 17–41 alphanumeric chars, 7 mandatory components in `DMC-` prefix form. Reserved field `s1000d_dmc` will be a single string with regex pattern; full structural decomposition deferred to v2.
3. JSON Schema Draft 2020-12: **fully supported** by `check-jsonschema 0.37.x` (via `jsonschema ≥4.18`) and `ajv 8.x` (requires separate `Ajv2020` import). All target features (`unevaluatedProperties`, `$dynamicAnchor`, `$dynamicRef`, `prefixItems`, `if/then/else`) are available.
4. `_meta.schema.json` composition: use **`$ref` + `allOf` + `unevaluatedProperties: false`** pattern. Pure `additionalProperties: false` breaks under `allOf` composition (silently rejects fields defined in the composed schema).
5. `ruamel.yaml` migration idiom: instantiate `YAML()` (not deprecated `round_trip_load`), preserve comments via `.ca.items` mapping, edit in-place, dump back. Worked snippet provided.
6. Person/Organization shape: minimal v0.1.0 fields drawn from intersection of W3C PROV-O (`prov:Agent`), schema.org Person/Organization, and FOAF. Adopt 6 fields per entity; defer ORCID/ROR resolution to v0.2.0+.

**Primary recommendation:** Implement `_meta.schema.json` first as the composition base (provenance + confidence + source), then derive `entity.base.schema.json` and `relation.base.schema.json` via `allOf` composition with `unevaluatedProperties: false`. Every type-specific schema then composes the base via a single `allOf $ref`. This pattern is the only one that survives Draft 2020-12 strictness without silently dropping fields.

## User Constraints (from CONTEXT.md)

> **CRITICAL:** Planner MUST honor every locked decision below. Do not propose alternatives to D-01..D-26.

### Locked Decisions (D-01 through D-26 from 02-CONTEXT.md)

**Entity additions (ADR-002):**
- **D-01:** Material entity accepted in v0.1.0
- **D-02:** TestCase + TestReport entities accepted in v0.1.0
- **D-03:** Configuration / EffectivityRange entity DEFERRED to v0.2.0
- **D-04:** Person + Organization entities accepted in v0.1.0 (mandatory)
- **Net entity count v0.1.0:** 17 baseline + 3 additions = **20 entity schemas**

**Relation additions (ADR-003):**
- **D-05:** interfaces_with accepted
- **D-06:** complies_with accepted
- **D-07:** has_revision IS NOT a relation — internalized as `version_history` field (D-15)
- **D-08:** applicable_during_phase accepted
- **D-09:** generated_by IS NOT a relation — encoded by `provenance.actor` + `source.tool`
- **Net relation count v0.1.0:** 13 baseline + 3 additions = **16 relation schemas**

**Boundary clarifications:**
- **D-10:** `requires` = cross-tier; `interfaces_with` = peer-tier — worked examples mandatory in `description`
- **D-11:** `constrained_by` = generic; `complies_with` = explicit regulation/standard
- **D-12:** `equivalent_to` is NOT for cross-language pairs (use `i18n` field per D-14)

**Field shapes (ADR-004):**
- **D-13:** `confidence: { score: number 0.0–1.0, rationale: string ≥1 sentence }` — H-Darrieus lock requires decimal scale and non-empty rationale
- **D-14:** `i18n: { label: { zh, en }, full_text: { zh, en } }` flat shape; either language may be empty
- **D-15:** `version_history: [{ version, date, author (URI), change_summary }]`; absence = v1

**Provenance (ADR-005):**
- **D-16:** `provenance.method` enum: **`human` | `ai_extracted` | `hybrid_reviewed`**
- **D-17:** Promotion from `_pending/` to canonical requires `method = hybrid_reviewed` AND non-empty `reviewer` URI AND `reviewed_at` ISO8601

**Triple export (ADR-006):**
- **D-18:** JSONL `{s, p, o, provenance, confidence}` — one triple per line; subject/object are entity URIs
- **D-19:** Phase 2 only **enriches** existing `to_jsonl_triples.py` stub (no implementation)

**Versioning (ADR-007):**
- **D-20:** Both per-file `version` (in schema frontmatter) AND per-record `schema_version` (in instance YAML)
- **D-21:** `ontology/CHANGELOG.md` records every schema bump
- **D-22:** `migrations/<from>_to_<to>.py` Python scripts; Phase 2 ships **placeholder pattern doc only**

**URI / ID scheme:**
- **D-23:** External URI `aviationkb://<type>/<slug>@<version>`
- **D-24:** Internal ID `<type-prefix>:<kebab-slug>` (22-prefix mapping defined)
- **D-25:** Slug rules: lowercase ASCII + digits + hyphen; ≤64 chars; unique per type; never reused

**Scripting:**
- **D-26:** Python for migration scripts; uses `ruamel.yaml` + `jsonschema`

### Claude's Discretion (from 02-CONTEXT.md)

- Exact `_meta.schema.json` JSON Schema 2020-12 syntax — Claude follows ajv/check-jsonschema-friendly conventions (see Architecture Patterns below)
- Internal directory layout under `ontology/schemas/` — Claude picks pragmatic (recommended: flat with type-prefixed filenames)
- ADR file naming: `ADR-NNN-<slug>.md` under `.planning/decisions/`
- ATA chapter list seeding: research has confirmed source — see Gap Resolution #1
- Validator-rule pseudocode in schema descriptions: Claude can place hints (real validators land in Phase 3)

### Deferred Ideas (OUT OF SCOPE for Phase 2)

- Configuration / EffectivityRange entity → v0.2.0 (D-03)
- JSON-LD / RDF Turtle export → v0.3.0+
- Per-translation provenance on i18n → v0.2.0+
- DO-178C / DO-254 specific TestCase fields → v0.2.0+
- Validators that enforce schema rules → Phase 3
- Demo data instances → Phase 4
- RAG pipeline / chunking → Phase 5
- Real docker-compose deployment → Phase 6 / never

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ONT-E-01 | Base entity schema (`entity.base.schema.json`) with mandatory fields | Architecture Patterns §"_meta + base composition"; Code Example #1 |
| ONT-E-02..18 | 17 baseline entity schemas | Standard Stack confirms tooling; Architecture Patterns shows composition |
| ONT-E-19 | Material entity (D-01 ACCEPT) | Material is a v0.1.0 entity — see Don't Hand-Roll for "don't model materials science from scratch" |
| ONT-E-20 | TestCase + TestReport (D-02 ACCEPT) | Generic shape v0.1.0; DO-178C/DO-254 fields deferred |
| ONT-E-21 | Configuration / EffectivityRange (D-03 DEFER) | Out of scope — research confirms v0.2.0 trigger conditions |
| ONT-E-22 | Person + Organization (D-04 ACCEPT) | Gap Resolution #6 — minimal 6-field shape |
| ONT-R-01 | Base relation schema (`relation.base.schema.json`) | Architecture Patterns §"relation composition"; Code Example #3 |
| ONT-R-02..14 | 13 baseline relation schemas | Standard Stack |
| ONT-R-15 | interfaces_with (D-05 ACCEPT) | Code Example #3 + Common Pitfall #4 (overlap with `requires`) |
| ONT-R-16 | complies_with (D-06 ACCEPT) | Common Pitfall #4 (overlap with `constrained_by`) |
| ONT-R-17 | has_revision (D-07 REJECT — field) | Field-level pattern via `version_history` (D-15) |
| ONT-R-18 | applicable_during_phase (D-08 ACCEPT) | Enum: taxi/takeoff/cruise/approach/landing/missed/emergency |
| ONT-R-19 | generated_by (D-09 REJECT — field) | Use `provenance.actor` + `source.tool` |
| PROV-01 | `_meta.schema.json` provenance object | Code Example #1 |
| PROV-02 | `_meta.schema.json` confidence object | Code Example #1 |
| PROV-03 | `_meta.schema.json` source object | Code Example #1 |
| PROV-04 | H-Darrieus validator REJECT condition | Phase 3 enforces; Phase 2 schema ensures `reviewer` is optional string with format URI so validator can detect emptiness |
| PROV-05 | `_pending/` quarantine schema | Same schemas; promotion is workflow not schema |
| PROV-06 | source.document_id resolves to Document | Phase 3 enforces; Phase 2 makes `document_id` mandatory string |
| VER-01 | `ontology/VERSION` = `0.1.0` | Phase 2 creates file |
| VER-02 | `ontology/CHANGELOG.md` initial entry | Phase 2 creates file |
| VER-03 | per-record `schema_version` field | Code Example #2 shows the field |
| VER-04 | `migrations/` placeholder + pattern doc | Architecture Patterns §"migrations idiom" + Gap Resolution #5 |

## Gap Resolutions

> Each of the 6 gaps from `<key_insight>` resolved here with confidence + verification source.

### Gap 1: ATA chapter enum vs string-pattern → **ENUM-STRICT (confidence: HIGH)**

**Decision:** Ship `ata-chapters.yaml` as an enum-strict vocabulary with **~70 entries** drawn from iSpec 2200 Revision 2024.1.

**Verified facts:**
- ATA iSpec 2200 chapter numbering space is 0–99 (`[VERIFIED: itlims-zsis.meil.pw.edu.pl ATA_Chapters.pdf, Wikipedia ATA_Spec_100/iSpec_2200]`)
- Of those, ~70 chapter numbers are *currently allocated*; 1–4 are reserved for airline use; 13, 14, 15, 16, 17, 19, 39, 40, 43, 58, 59, 87, 88, 90, 93, 94, 95, 96, 97, 98, 99 are unassigned/operator-allocated `[VERIFIED: aviationhunt.com ATA Standard Numbering System + ATA Chapters PDF]`
- The list is **slow-moving but not frozen** — A4A publishes annual revisions (current: Revision 2024.1) `[CITED: publications.airlines.org/products/ispec-2200-information-standards-for-aviation-maintenance-revision-2024-1]`
- Only known recent additions (last 10 years): ATA-42 Integrated Modular Avionics, ATA-44 Cabin Systems, ATA-45 Central Maintenance/Diagnostic, ATA-46 Information Systems, ATA-47 Nitrogen Generation, ATA-48 In-Flight Fuel Dispensing, ATA-49 Airborne Auxiliary Power, ATA-50 Cargo Compartments

**Why enum-strict is correct (vs string-pattern):**
1. Finite, public, well-known — no case for free-form
2. Catches typos (`ATA-72` vs `ata72` vs `72`) at schema-validation time
3. CI on a closed enum is cheaper than regex
4. Pitfall #11 (AI handoff): a future Claude/Codex can read the enum and immediately understand the domain

**Concrete recommendation for `ontology/vocabularies/ata-chapters.yaml`:**

```yaml
# ATA iSpec 2200 chapters (Revision 2024.1)
# Source: A4A Publications iSpec 2200 + extracts available publicly
# Chapters 1-4 are reserved for airline-specific use (kept off the enum)
# Update cadence: re-verify against A4A annual revision
chapters:
  - code: "ATA-05"
    name: "Time Limits / Maintenance Checks"
    section: "aircraft_general"
  - code: "ATA-06"
    name: "Dimensions and Areas"
    section: "aircraft_general"
  # ... ~70 entries total ...
  - code: "ATA-91"
    name: "Charts"
    section: "powerplant"
  - code: "ATA-92"
    name: "Electrical System Installation"
    section: "powerplant"
sections:  # used as a secondary classifier on entity schemas
  - aircraft_general    # chapters 5-12, 18, 89
  - airframe_systems    # chapters 20-50
  - structure           # chapters 51-57
  - power_plant         # chapters 60-92
```

**Schema usage:** entity schemas reference `ata_chapter` as `string` with an **ad-hoc enum loaded from the YAML at validation time** (the validator script loads the YAML and injects the enum into the in-memory schema before validating instances). This is Phase 3's job — Phase 2 just declares the YAML structure and writes the schema's `description` to point at the file.

**Escape valve for unassigned slots:** if an instance YAML legitimately needs `ATA-43` (currently unassigned), it can NOT validate — the validator points at the vocabulary file and fails clearly. To assign a new code, the procedure is: (a) update `ata-chapters.yaml`, (b) bump `ontology/VERSION`, (c) write CHANGELOG entry. This is enum-strict by construction.

### Gap 2: S1000D Issue 6 DMC field shape → **OPTIONAL STRING + REGEX (confidence: HIGH)**

**Decision:** Reserved field `s1000d_dmc` on `Document` entity is `optional string` with a **regex pattern** that matches the DMC envelope but does not decompose components in v0.1.0. Full structural breakdown deferred to v0.2.0+.

**Verified facts:**
- S1000D **Issue 6 was released 2024-09-01** `[VERIFIED: en.wikipedia.org/wiki/S1000D]`
- DMC structure: 17–41 alphanumeric characters, prefixed with `DMC-` `[VERIFIED: siberlogic.com/s1000d-concepts/sns-and-dmc, kibook.github.io/s1kd-tools/TUTORIAL.html]`
- Components in order: Model Identification Code (2–14 chars) → System Difference Code (1–4 chars) → SNS = system + subsystem + sub-subsystem + assembly (4 segments × variable digits) → Disassembly Code (2 chars) + Disassembly Code Variant (1–3 chars) → Information Code (3 chars) + Information Code Variant (1 char) → Item Location Code (1 char: A/B/C/D/T) → optional Learn Code → optional Language Code
- Worked example from S1000D reference toolset: `DMC-S1000DBIKE-AAA-D00-00-00-00AA-00PA-D_004-00_EN-US.XML` `[VERIFIED: kibook S1000D reference repo]`

**Why regex-only is correct for v0.1.0:**
1. The field is **reserved** (per research/SUMMARY.md #6) — it exists for future round-tripping, not active query
2. Decomposing into components requires modeling Hardware Identification Partition + Information Type Partition + 7 sub-codes — that's a 7-field nested object, useless until something consumes it
3. `[VERIFIED]` regex catches malformed strings; structured decomposition can land in v0.2.0+ without breaking the schema (additive change)

**Concrete schema fragment:**

```json
"s1000d_dmc": {
  "type": "string",
  "pattern": "^DMC-[A-Z0-9]{2,14}-[A-Z0-9]{1,4}(-[0-9]{2,4}){4}-[0-9A-Z]{2,5}-[0-9A-Z]{4}-[ABCDT](_[0-9]{3}-[0-9]{2}_[a-zA-Z]{2}-[A-Z]{2})?$",
  "description": "S1000D Issue 6 Data Module Code. Reserved field — currently used only as opaque identifier for future round-tripping. Format: DMC-<modelId>-<sysDiff>-<sns>-<disasm>-<infoCode>-<itemLoc>[_<learn>][_<lang>]. Example: DMC-S1000DBIKE-AAA-D00-00-00-00AA-00PA-D_004-00_EN-US. See ontology/mappings/s1000d-dmc-reserved.md for the full structural decomposition that will land in v0.2.0+."
}
```

The `mappings/s1000d-dmc-reserved.md` placeholder doc (a Phase 2 deliverable per `02-CONTEXT.md` <domain> §5) records the verified component breakdown above so a future schema-evolution Claude session has the structural decomposition ready.

### Gap 3: JSON Schema Draft 2020-12 compatibility → **FULLY SUPPORTED (confidence: HIGH)**

**Decision:** All target Draft 2020-12 features are available in both `check-jsonschema 0.37.x` and `ajv 8.x`.

**Verified facts:**

| Feature | check-jsonschema 0.37.x | ajv 8.x | Source |
|---------|------------------------|---------|--------|
| Draft 2020-12 base support | ✓ via `jsonschema ≥4.18` | ✓ via `Ajv2020` import | `[VERIFIED: pypi.org jsonschema, ajv.js.org/json-schema.html]` |
| `unevaluatedProperties` | ✓ | ✓ | `[VERIFIED]` |
| `unevaluatedItems` | ✓ | ✓ | `[VERIFIED]` |
| `$dynamicAnchor` | ✓ | ✓ | `[VERIFIED]` |
| `$dynamicRef` | ✓ | ✓ | `[VERIFIED]` |
| `prefixItems` | ✓ | ✓ | `[VERIFIED]` |
| `if/then/else` (Draft-07+) | ✓ | ✓ | `[VERIFIED]` |
| `--check-metaschema` flag | ✓ (validates schema-as-instance against `$schema`) | n/a CLI flag | `[VERIFIED: check-jsonschema readthedocs Usage]` |

**Backend chain:** `check-jsonschema 0.37.x` → bundles `jsonschema ≥4.18` → which has full Draft 2020-12 support since 4.18.0 (released 2023-07) `[VERIFIED: python-jsonschema.readthedocs.io/en/v4.18.0]`.

**Caveats / footguns to avoid:**

1. **ajv has a SEPARATE class for 2020-12.** `import Ajv2020 from 'ajv/dist/2020'` — NOT the default `import Ajv from 'ajv'` (which is Draft-07). `[VERIFIED: ajv.js.org]` — this trips up everyone who pastes ajv examples from old Stack Overflow posts. **Phase 2 schemas should declare `"$schema": "https://json-schema.org/draft/2020-12/schema"` so the validator routes correctly.**

2. **You cannot mix drafts in one ajv instance.** "Draft-2020-12 is not backwards compatible" — if any schema in the bundle is Draft-07, instantiate a Draft-07 ajv separately. We don't have this problem (greenfield 2020-12-only) but the planner should NOT add `--draft 7` flags to validators "for compat."

3. **`items` semantics CHANGED in 2020-12.** In Draft-07, `items` could be array-of-schemas (tuple validation). In 2020-12, `items` is a single schema; tuple is `prefixItems`. If you find pre-2020-12 examples online doing `"items": [...]` they will silently break or produce wrong errors.

4. **`additionalProperties` and `unevaluatedProperties` are NOT interchangeable** — see Common Pitfall #1 below.

5. **`format` keyword default behavior:** in Draft 2020-12, `format` is annotation-only by default. `check-jsonschema` activates `format-assertion` automatically for known formats (`date-time`, `uri`, `email`); ajv requires `addFormats(ajv)` from `ajv-formats` package. We DO use `format: uri` for entity IDs (D-23) and `format: date-time` for timestamps — this needs explicit verification at Phase 3.

### Gap 4: `_meta.schema.json` composition pattern → **`$ref` + `allOf` + `unevaluatedProperties: false` (confidence: HIGH)**

**Decision:** Every entity/relation schema composes the base schemas via `allOf` of `$ref`s, with `unevaluatedProperties: false` at the leaf level (NOT `additionalProperties: false`).

**Why this combination is the only one that works:**

Mixing `additionalProperties: false` with `allOf` composition is the #1 silently-broken pattern in JSON Schema. Here's why:

```json
// BROKEN — DO NOT USE
{
  "allOf": [{ "$ref": "_meta.schema.json#/$defs/baseFields" }],
  "additionalProperties": false,
  "properties": {
    "ata_chapter": { "type": "string" }
  }
}
```
The keyword `additionalProperties` only checks against `properties` declared in **the same schema object** — it does NOT see properties declared in the `$ref`'d base. Result: every base field (e.g. `id`, `provenance`, `confidence`) is flagged as "additional property" and validation fails.

```json
// CORRECT — Draft 2020-12 pattern
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "allOf": [{ "$ref": "_meta.schema.json#/$defs/baseFields" }],
  "unevaluatedProperties": false,
  "properties": {
    "ata_chapter": { "type": "string" }
  }
}
```
`unevaluatedProperties: false` is annotation-aware: it tracks which properties have been "evaluated" by ANY subschema (including `allOf` refs) and only rejects truly extra properties. This is what 2020-12 was designed for. `[VERIFIED: json-schema.org/draft/2020-12/release-notes]`

**Source of truth for the pattern:** This is the canonical "schema composition" example in the Draft 2020-12 spec; both check-jsonschema and ajv 8.x implement it correctly.

See **Code Example #1** below for the full skeleton.

### Gap 5: `ruamel.yaml` migration idiom → **YAML() class + .ca.items pattern (confidence: HIGH)**

**Decision:** Phase 2 ships `migrations/PATTERN.md` + a stub `migrations/0_1_0_to_template.py.example` showing the canonical pattern. Real migrations land in v0.2.0+.

**Verified pattern:**

```python
# migrations/0_1_0_to_template.py.example
# Migration template — ruamel.yaml comment-preserving YAML edit
# Pattern verified against ruamel.yaml ≥0.17 (uses YAML() class, not deprecated round_trip_load)
# Source: ruamel.yaml docs (yaml.dev/doc/ruamel.yaml/detail/) + pycontribs/ruamel-yaml issues

from pathlib import Path
from ruamel.yaml import YAML

def migrate_one(path: Path) -> None:
    yaml = YAML()           # round-trip mode by default in ≥0.15
    yaml.preserve_quotes = True
    yaml.width = 200        # match .yamllint line-length config
    data = yaml.load(path)

    # 1) Bump schema_version
    data["schema_version"] = "0.2.0"

    # 2) Example: rename a field while preserving its trailing comment
    if "old_field" in data:
        data["new_field"] = data.pop("old_field")
        # Move the comment metadata too (.ca = comment attribute store)
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

**Pattern rules (write into `migrations/PATTERN.md`):**
1. Always use `YAML()` class, NEVER `round_trip_load` (deprecated since 0.15)
2. Set `yaml.preserve_quotes = True` and `yaml.width = 200` to match the project's `.yamllint`
3. To rename a key while keeping its comment: pop and reassign in `data.ca.items`
4. Migration scripts are idempotent — re-running on already-migrated YAML must be a no-op
5. Migration scripts test against `tests/fixtures/valid/` (Phase 3) — invalid input is the validator's job, not the migration's
6. Filename: `<from_version>_to_<to_version>.py` (slashes converted to underscores; e.g. `0_1_0_to_0_2_0.py`)

### Gap 6: Person/Organization schema design → **6-field minimal v0.1.0 (confidence: MEDIUM-HIGH)**

**Decision:** Adopt minimal field set drawn from intersection of W3C PROV-O `prov:Agent`, schema.org `Person` / `Organization`, and FOAF — pick fields that are needed for the H-Darrieus lock and demo data, defer anything else.

**Person v0.1.0 fields:**
| Field | Type | Required | Source |
|-------|------|----------|--------|
| `id` | URI (`aviationkb://person/<slug>@<version>`) | yes | D-23 |
| `name` | string | yes | schema.org/Person.name + FOAF foaf:name |
| `i18n.label` | `{ zh, en }` | yes | D-14 (project rule) |
| `affiliation` | URI to Organization (or null) | optional | schema.org/Person.affiliation |
| `role` | enum (`author` / `reviewer` / `expert` / `inspector` / `engineer` / `other`) | optional | PROV-O `prov:hadRole` simplified |
| `external_ids` | `{ orcid?: string, email?: string }` | optional | both pattern-validated; ORCID resolution deferred to v0.2.0+ |

**Organization v0.1.0 fields:**
| Field | Type | Required | Source |
|-------|------|----------|--------|
| `id` | URI (`aviationkb://organization/<slug>@<version>`) | yes | D-23 |
| `name` | string | yes | schema.org/Organization.name |
| `i18n.label` | `{ zh, en }` | yes | D-14 |
| `org_type` | enum (`regulator` / `manufacturer` / `operator` / `research_institute` / `standards_body` / `consultancy` / `other`) | yes | aviation-domain useful |
| `jurisdiction` | enum (`FAA` / `EASA` / `CAAC` / `ICAO` / `other`) | optional | matches RegulationClause.jurisdiction (D-14 implicit) |
| `external_ids` | `{ ror?: string, lei?: string }` | optional | both pattern-validated |

**Why these 6 fields and not more:**
- PROV-O has dozens of optional properties (qualifiedAttribution, actedOnBehalfOf, etc.) — useful for deep audit trails but premature for v0.1.0
- schema.org Person has 100+ properties — almost all irrelevant to aviation engineering KB
- FOAF has personal-network properties (foaf:knows, foaf:nick) — wrong domain
- The H-Darrieus lock needs `id` + `name` to make `provenance.actor` and `provenance.reviewer` resolvable URIs. Everything else is enrichment.

**What is deliberately deferred:**
- ORCID/ROR live resolution (Phase 3 validator could verify format; live fetch is v0.2.0+)
- `prov:qualifiedAttribution` for partial-authorship audit (only matters when 2+ humans co-author the same record)
- ITAR/EAR person classification — out of scope for v1 per PROJECT.md

**Confidence note:** Confidence is MEDIUM-HIGH (not HIGH) because we are picking by intersection rather than verifying against any single authoritative aviation Person/Organization schema. PROV-O / schema.org / FOAF are well-known and stable, but their intersection is a judgment call. Plan-phase should treat this as a recommendation, not a frozen decision; the actual Person/Organization schemas are cheap to revise in Phase 4 if demo data exposes a missing field.

## Standard Stack

> Versions confirmed against project's locked decisions (research/STACK.md, CLAUDE.md). No version bumps from upstream as of 2026-05-03.

### Core (already pinned by Phase 1)

| Tool | Version | Purpose | Status |
|------|---------|---------|--------|
| **JSON Schema** | **Draft 2020-12** | Schema language for `ontology/schemas/*.schema.json` | Locked at project init |
| **YAML 1.2** | spec | Source format for vocabularies + instance YAML | Locked |
| **check-jsonschema** | **0.37.1** | Pre-commit hook + CI validator (Python) | Locked; pre-commit already wired to `^ontology/schemas/.*\.json$` |
| **yamllint** | **1.38** | YAML style linter | Locked; `.yamllint` already present (line-length warning 200) |
| **pre-commit** | **3.7+** | Hook orchestrator | Locked |
| **ruamel.yaml** | **≥0.17** | Comment-preserving YAML for migration scripts (D-26) | New for Phase 2 — to be added to `requirements-dev.txt` if not present |
| **jsonschema** (Python lib) | **≥4.18** | Backs check-jsonschema; Draft 2020-12 support since 4.18.0 | Transitive dep of check-jsonschema; do not pin separately |

**Version verification (2026-05-03):**
- `check-jsonschema 0.37.1` → confirmed via `[VERIFIED: github.com/python-jsonschema/check-jsonschema releases]`
- `jsonschema 4.18+` Draft 2020-12 support → `[VERIFIED: python-jsonschema.readthedocs.io/en/v4.18.0]`
- `ajv 8.x` → `[VERIFIED: ajv.js.org]` (note: Phase 2 doesn't need ajv at runtime, only for documentation/validation tooling demos)
- `ruamel.yaml ≥0.17` deprecates `round_trip_load` → `[VERIFIED: yaml.dev/doc/ruamel.yaml/detail]`

### Supporting (Phase 2 doesn't run any of these, but schemas should be compatible)

| Tool | Version | Why Schemas Should Be Compatible |
|------|---------|----------------------------------|
| ajv | 8.x | If Phase 5+ adds a Node.js consumer (e.g. RAGFlow extension), schemas should validate via Ajv2020 import without modification |
| jsonschema CLI (Python) | 4.18+ | Direct schema validation outside check-jsonschema |
| VSCode redhat.vscode-yaml | latest | Editor-time validation against `yaml.schemas` config |

### Alternatives Considered (and Rejected)

| Instead of | Could Use | Tradeoff | Decision |
|------------|-----------|----------|----------|
| Draft 2020-12 | Draft 2019-09 | Lose `prefixItems`; `unevaluatedProperties` was already in 2019-09 so composition still works | REJECT — gain too small |
| Draft 2020-12 | Draft-07 | Lose `unevaluatedProperties` entirely → cannot do safe composition | REJECT (per research/STACK.md "What NOT to Use") |
| Composition via `allOf + unevaluatedProperties: false` | Single monolithic schemas with all fields inlined | Easier validator but explodes file count and breaks DRY for `provenance`/`confidence`/`source` (would need to copy 3-block 30-line definition into 36 schema files) | REJECT — Pitfall risk: any change to provenance shape becomes a 36-file edit |
| Composition via `allOf` | `$ref` only at the top level (no `allOf`) | Simpler but you can't add type-specific fields at the leaf | REJECT — leaf schemas need their own `properties` |
| `unevaluatedProperties: false` | `additionalProperties: false` | The latter is well-known, but silently breaks under `allOf` composition | REJECT — see Common Pitfall #1 |

**Installation (added to existing dev environment):**
```bash
# Already installed (Phase 1):
# pip install pre-commit==3.7.* check-jsonschema==0.37.* yamllint==1.38.*

# Phase 2 additions:
pip install "ruamel.yaml>=0.17,<0.19"
```

## Architecture Patterns

### Pattern 1: `_meta.schema.json` as Composition Root

**What:** A single `_meta.schema.json` defines reusable building blocks (`$defs/provenance`, `$defs/confidence`, `$defs/source`, `$defs/baseFields`) that every entity and relation schema composes via `$ref`.

**Where it lives:** `ontology/_meta.schema.json` (per `02-CONTEXT.md` <domain> §1)

**When to use:** ALWAYS for new entity/relation schemas. Never duplicate provenance/confidence/source definitions inline.

### Pattern 2: Entity Base + Type-Specific Composition

**What:** `entity.base.schema.json` composes `_meta.schema.json` and adds entity-only base fields (`type`, `version`, `schema_version`, `tags`, `i18n`). Each of the 20 entity-type schemas then composes `entity.base.schema.json` via `allOf` and adds its type-specific properties.

**Tree:**
```
_meta.schema.json
  ├── $defs/provenance       (PROV-01)
  ├── $defs/confidence       (PROV-02)
  ├── $defs/source           (PROV-03)
  └── $defs/baseFields       (id + provenance + confidence + source — composable into anything)

entity.base.schema.json
  ├── allOf: $ref _meta.json#/$defs/baseFields
  └── adds: type, version, schema_version, tags, i18n, version_history (optional)

entity.aircraft-system.schema.json
  ├── allOf: $ref entity.base.schema.json
  ├── adds: parent_aircraft_model, ata_chapter, function, criticality_level
  └── const: type = "AircraftSystem"

(... 19 more entity-type schemas, all the same pattern ...)
```

### Pattern 3: Relation Base + Type-Specific Composition

Same as Pattern 2, but with relation-specific base (`subject`, `object`, `valid_from`, `valid_until`).

### Pattern 4: URI/ID Validation

URIs (D-23) and Internal IDs (D-24) validated via `format: "uri"` for the URI form and `pattern` for the internal ID form. Pattern: `^[a-z]+:[a-z0-9]+(-[a-z0-9]+)*$` (type prefix + colon + kebab-slug ≤64 chars per D-25).

### Pattern 5: version_history as Internalized has_revision

Per D-07 + D-15, `version_history` is an OPTIONAL array on entity.base; absence implies v1. Each element is `{ version: semver, date: ISO8601, author: URI, change_summary: string }`.

### Pattern 6: Worked Examples in `description`

Per `02-CONTEXT.md` <specifics>, schemas with semantic overlap (D-10, D-11) MUST include 1-line worked examples in `description` fields. Long examples → ADR.

### Pattern 7: ATA Chapter Vocabulary Loading (Phase 3)

Phase 2 ships the YAML; Phase 3 ships the validator that loads it and injects the enum. Phase 2 documents the contract in the schema's `description`.

### Recommended Directory Layout (Claude's discretion per CONTEXT)

```
ontology/
├── _meta.schema.json                          # Pattern 1: provenance + confidence + source
├── VERSION                                     # "0.1.0\n"
├── CHANGELOG.md                                # initial entry: 0.1.0 release notes
├── schemas/
│   ├── entity.base.schema.json                # Pattern 2: composes _meta + entity base fields
│   ├── entity.aircraft-model.schema.json      # 20 entity-type schemas (flat layout)
│   ├── entity.aircraft-system.schema.json
│   │   ... (17 baseline) ...
│   ├── entity.material.schema.json            # D-01
│   ├── entity.test-case.schema.json           # D-02
│   ├── entity.test-report.schema.json         # D-02
│   ├── entity.person.schema.json              # D-04
│   ├── entity.organization.schema.json        # D-04
│   ├── relation.base.schema.json              # Pattern 3: composes _meta + relation base fields
│   ├── relation.part-of.schema.json           # 16 relation-type schemas
│   │   ... (13 baseline) ...
│   ├── relation.interfaces-with.schema.json   # D-05
│   ├── relation.complies-with.schema.json     # D-06
│   └── relation.applicable-during-phase.schema.json  # D-08
├── vocabularies/
│   ├── ata-chapters.yaml                      # Gap Resolution #1
│   ├── jurisdictions.yaml                     # FAA / EASA / CAAC / ICAO / other
│   └── provenance-methods.yaml                # human / ai_extracted / hybrid_reviewed
├── mappings/
│   ├── ata-to-iso10303.md                     # placeholder + ADR pointer
│   └── s1000d-dmc-reserved.md                 # full DMC structural breakdown for v0.2.0+
└── migrations/
    ├── PATTERN.md                              # Gap Resolution #5: ruamel.yaml idiom
    └── 0_1_0_to_template.py.example            # Stub migration template
```

**Why flat (not `entity/`, `relation/` subdirs):** 36 files in `schemas/` is fine; nesting adds an import-path hop for every cross-schema `$ref` (e.g. `entity/aircraft-system → ../entity.base` vs `entity.aircraft-system → entity.base`). Flat keeps `$ref` URIs short.

## Don't Hand-Roll

> Phase 2 is schema authoring — most of the "don't hand-roll" risk is conceptual (don't reinvent provenance / i18n / URI / etc) rather than code-level.

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON Schema validation | Custom Python/JS validator that walks YAML manually | `check-jsonschema 0.37.1` | Hand-rolled validators don't handle Draft 2020-12 `unevaluatedProperties`, `$dynamicRef`, `prefixItems` correctly |
| Schema composition | Inline `provenance`/`confidence`/`source` in every entity schema | `_meta.schema.json` + `allOf` + `unevaluatedProperties: false` (Pattern 1) | 36-file copy is a non-starter; one schema-shape change becomes 36 PRs |
| YAML comment preservation | `pyyaml` (drops comments on round-trip) | `ruamel.yaml ≥0.17` `YAML()` class (D-26) | pyyaml destroys comments; round-trip loss is silent |
| Bilingual handling | Multiple language-suffix fields (`label_zh`, `label_en`) | `i18n: { label: { zh, en } }` flat shape (D-14) | Suffix-fields force every consumer to know which suffixes exist; nested `i18n` makes "list available languages" trivial |
| Cross-language entity mapping | `equivalent_to` relation between Chinese and English entities | Single entity with `i18n.label.{zh, en}` + `i18n.full_text.{zh, en}` (D-12, D-14) | Two-entity model fragments retrieval and breaks the "single canonical entity" assumption RAG depends on |
| URI scheme | A new URI scheme invented this phase | `aviationkb://<type>/<slug>@<version>` (D-23) — already locked | URI scheme was decided at project init; reinventing breaks downstream RDF/Neo4j export |
| Provenance method enum | "Better" enums like `manual` / `auto` / `assisted` | `human` / `ai_extracted` / `hybrid_reviewed` (D-16) — already locked | Words chosen specifically for H-Darrieus lock semantics |
| Confidence shape | Single `confidence: 0.85` number | `confidence: { score, rationale }` object (D-13) | Scalar without rationale is uninspectable |
| Migration scripts | Bash/sed/yq edits to YAML | `ruamel.yaml`-based Python migration (D-22, D-26) | sed breaks YAML structure; yq drops comments and re-orders keys |
| Ontology design from scratch | A custom aviation ontology built from training-data intuition | ATA iSpec 2200 chapter taxonomy (Gap #1) + reference patterns from W3C PROV-O for provenance, schema.org for Person/Org (Gap #6) | Aviation ontology has 50+ years of standardization — don't second-guess; just don't adopt the heavyweight XML monoliths (S1000D, AP233 — explicitly rejected per research/STACK.md) |
| ATA chapter parser | Custom regex / lookup logic | `vocabularies/ata-chapters.yaml` enum + Phase 3 validator that loads it | Single source of truth; updating the enum doesn't require code changes |
| S1000D DMC decomposition (v0.1.0) | A 7-field nested object in v0.1.0 schema | Single string with regex (Gap #2); structural breakdown in `mappings/s1000d-dmc-reserved.md` | YAGNI — no v0.1.0 consumer needs the components |

**Key insight:** This phase's risk profile is "subtle silent failures from incorrect schema patterns" (Pitfall #1 below), not "we built 5000 LOC of duplicated logic." The hand-rolling-equivalent here is **inventing schema patterns when JSON Schema 2020-12 already has the right primitive** (`unevaluatedProperties`, `$dynamicRef`, `allOf+$ref`).

## Common Pitfalls

### Pitfall 1: `additionalProperties: false` + `allOf` composition silently rejects all base fields

**What goes wrong:** Schemas using the standard "strict" pattern `"additionalProperties": false` will fail validation on every base field defined in the `$ref`'d composed schema. The error looks like "additional property 'provenance' is not allowed" — confusing because `provenance` IS defined, just in the parent schema.

**Why it happens:** `additionalProperties` is keyword-local: it only sees properties declared in the same schema object, not inherited via `allOf`/`$ref`.

**How to avoid:** Use `unevaluatedProperties: false` instead (Draft 2020-12 / 2019-09). It's annotation-aware and tracks evaluation across `allOf`. Set `"$schema": "https://json-schema.org/draft/2020-12/schema"` at the top of every schema.

**Warning signs:**
- Every leaf-type schema validates only its own fields, base fields cause "additional property" errors
- check-jsonschema output mentions properties that are clearly defined in the base
- Devs add the same property names twice (in base AND in leaf) "to make it work"

**Phase to address:** Phase 2 (this phase) — first schema authored is the canary.

### Pitfall 2: Using ajv default import for Draft 2020-12 schemas

**What goes wrong:** Code does `import Ajv from 'ajv'` and tries to compile a `$schema: "...2020-12/schema"` schema. ajv silently treats it as Draft-07 and produces wrong errors (e.g. accepts `prefixItems` as a custom property, ignores `unevaluatedProperties`).

**Why it happens:** ajv 8.x ships TWO classes: the default `Ajv` (Draft-07) and `Ajv2020` (Draft 2020-12). Most blog posts predate this split.

**How to avoid:** When ajv eventually shows up in this project (Phase 5 or later), insist on `import Ajv2020 from 'ajv/dist/2020'`. Phase 2 doesn't use ajv at runtime, but the schemas should declare their `$schema` explicitly so future tooling routes correctly.

**Warning signs:** ajv accepts schemas that should be invalid; `prefixItems` test data passes when it shouldn't; `unevaluatedProperties` constraints are ignored.

**Phase to address:** Phase 2 declares `$schema` correctly; Phase 5+ enforces correct ajv import.

### Pitfall 3: `items` array form (Draft-07) breaks silently in Draft 2020-12

**What goes wrong:** A schema author copy-pastes a tuple validation example from a 2019 Stack Overflow post: `"items": [{"type": "string"}, {"type": "number"}]`. In Draft-07 this is tuple validation. In Draft 2020-12, `items` is a single schema — array form is non-conforming and validators behave inconsistently (jsonschema accepts but with wrong semantics; ajv2020 errors).

**Why it happens:** Draft 2020-12 split tuple-vs-array semantics: `prefixItems` for tuple, `items` for "everything else". `[VERIFIED: json-schema.org/draft/2020-12/release-notes]`

**How to avoid:** For tuple validation use `prefixItems: [...]`. Project search-and-destroy: `grep -rn '"items": \[' ontology/schemas/` — should be zero hits.

**Warning signs:** Schema validates inputs that should fail (or vice-versa); validator output doesn't match intent.

**Phase to address:** Phase 2 — caught at first schema using arrays (e.g. `version_history` is an array but each element is the same shape, so we use `items: {...}` not `prefixItems`).

### Pitfall 4: Worked-example overlap (`requires` vs `interfaces_with`, `constrained_by` vs `complies_with`)

**What goes wrong:** Devs writing demo data (Phase 4) read the relation schema, see two relations that COULD apply, pick one arbitrarily. Different devs pick differently. Demo data has inconsistent semantics that contradict the ADR.

**Why it happens:** D-10 and D-11 already identified this risk; mitigation is making `description` worked examples mandatory. But if examples are vague, the risk persists.

**How to avoid:** In every overlap-prone relation schema, the `description` includes **a concrete worked example AND a foil** ("use this for X; do NOT use it for Y, that's the other relation"). Examples per D-10:
- `requires.description` includes: "Use for cross-tier dependency: Component(brake_disc) requires MaintenanceTask(brake_inspection_500h). DO NOT use for peer-tier: AvionicsBay → ECS — that's interfaces_with."
- `interfaces_with.description` includes: "Use for peer-tier interface: AvionicsBay interfaces_with ECS via ARINC 429. DO NOT use for parent-child or task dependency — those are part_of and requires."

**Warning signs:** Phase 4 demo data has both `requires(A, B)` and `interfaces_with(A, B)` for the same A/B; two reviewers can't agree which is right.

**Phase to address:** Phase 2 (`description` quality is part of the schema deliverable); Phase 4 (demo data is a stress-test).

### Pitfall 5: Reserved fields without contract documentation

**What goes wrong:** v0.1.0 reserves `s1000d_dmc` (per Gap #2) and (potentially) other "future use" fields. Six months later a future Claude/Codex sees the field in schema, doesn't know it's reserved, tries to populate it and gets the format wrong; OR mistakes it for required and fails validation.

**Why it happens:** Reserved fields look like real fields. Without contract documentation in the field's `description`, future maintainers will guess.

**How to avoid:** Every reserved field's `description` MUST include the marker phrase "**Reserved field —**" followed by (a) what it's for, (b) when it will be activated, (c) where the structural decomposition lives. See Gap #2 for the canonical pattern.

**Warning signs:** Phase 4 demo data populates a reserved field; CI doesn't catch it because the regex passes.

**Phase to address:** Phase 2 (description discipline); Phase 3 (validator could warn on populated reserved fields, optional).

### Pitfall 6: Schema-version mismatch at instance-write time

**What goes wrong:** Schema bumps from 0.1.0 → 0.2.0 with a new required field. An older instance YAML still has `schema_version: 0.1.0` and is missing the new field. Validator error is unhelpful: "field X required" with no hint about the version mismatch.

**Why it happens:** Per D-20 every instance YAML carries `schema_version`; per D-22 migrations are Python scripts. But there's a hand-off gap: validator may be lenient on N-1 versions (per CONTEXT) but strict on N-2.

**How to avoid:** Phase 2 schemas already have `schema_version` mandatory in the base. Phase 3 validator implements the N-1 tolerance rule with a CLEAR error message ("instance is schema 0.1.0; current is 0.3.0; run migrations 0_1_0_to_0_2_0.py and 0_2_0_to_0_3_0.py"). Phase 2 documents this contract in `migrations/PATTERN.md`.

**Warning signs:** Confusing validator errors; devs disabling schema_version check.

**Phase to address:** Phase 2 (contract); Phase 3 (validator implementation).

### Pitfall 7: ATA chapter enum drift

**What goes wrong:** A4A publishes ATA iSpec 2200 Revision 2025.x adding ATA-93 or activating a previously-unassigned chapter. Our `vocabularies/ata-chapters.yaml` doesn't update; new instance YAML using `ATA-93` fails validation.

**Why it happens:** Vocabulary YAML has no automated sync; updating is manual.

**How to avoid:** `vocabularies/ata-chapters.yaml` includes a `verified_against` field at the top: `verified_against: "iSpec 2200 Revision 2024.1"`. Annual review is in `ROADMAP_FUTURE.md` (Phase 6). When update happens, bump `ontology/VERSION` minor (per D-21), write CHANGELOG entry, no migration needed (additive).

**Warning signs:** A new entity instance fails validation on `ata_chapter`; aviation engineers complain "chapter X exists, why is it rejected?"

**Phase to address:** Phase 2 (declare the verified_against field); Phase 6 (annual review trigger in roadmap).

### Pitfall 8: H-Darrieus lock validator is conceptually in Phase 2 but enforced in Phase 3

**What goes wrong:** Phase 2 plans assume "H-Darrieus is locked" and proceed to Phase 4 demo data. Phase 3 validator gets descoped or shipped late. AI-extracted demo records sneak through.

**Why it happens:** D-16 H-Darrieus condition is ENFORCED at validator layer (Phase 3), but the schema-required fields are pre-validated here. If Phase 3 lags, we have schema (passes structural check) without enforcement (semantic check).

**How to avoid:** Phase 2 schemas make `provenance.method`, `provenance.actor`, `provenance.reviewer`, `provenance.reviewed_at`, `confidence.score`, `confidence.rationale` REQUIRED. The H-Darrieus REJECT condition (`method == ai_extracted AND score > 0.85 AND empty reviewer`) cannot be expressed cleanly in pure JSON Schema (would require `if/then/else` with negation — possible but ugly). Instead:
1. Phase 2 schema makes all 6 fields required
2. Phase 2 schema description on `provenance` includes the H-Darrieus rule verbatim with "ENFORCED IN PHASE 3 VALIDATOR" marker
3. Phase 3 validator rule has highest-priority test case in `tests/fixtures/invalid/`

**Warning signs:** Phase 4 starts before Phase 3 validator ships; demo `_pending/` records bypass the check.

**Phase to address:** Phase 2 (schema required-fields contract); Phase 3 (validator rule); never let Phase 4 start until Phase 3 ships.

### Pitfall 9: Self-validation skipped (`--check-metaschema` not in pre-commit)

**What goes wrong:** Schema author writes a malformed JSON Schema (typo: `"unevalauted Properties"`). check-jsonschema validates instances against the schema, but doesn't validate the schema-itself against its `$schema`. Bad schema accepts everything; CI passes; downstream consumers fail.

**Why it happens:** `--check-metaschema` is opt-in, not default.

**How to avoid:** Phase 2 deliverable: pre-commit hook that runs `check-jsonschema --check-metaschema ontology/schemas/*.schema.json` on every PR touching schemas. Phase 1 wired the regex; Phase 2 enriches the hook config.

**Warning signs:** Schema typos go unnoticed for days; "validation passes but downstream rejects" reports.

**Phase to address:** Phase 2 (add `--check-metaschema` invocation).

### Pitfall 10: ruamel.yaml deprecated API in migration scripts

**What goes wrong:** A future Claude session writes a migration using `from ruamel.yaml import round_trip_load` — copy-pasted from a 2018 Stack Overflow answer. Works on ruamel.yaml 0.16, breaks/warns on 0.17+, fully removed in 0.19+.

**Why it happens:** Old API was the documented form for years; new docs are uneven about deprecation.

**How to avoid:** `migrations/PATTERN.md` (Gap Resolution #5) makes the modern `YAML()` class pattern the only documented form.

**Warning signs:** DeprecationWarning in migration test runs; migration breaks after `pip install --upgrade ruamel.yaml`.

**Phase to address:** Phase 2 (PATTERN.md authoring).

## Code Examples

> Verified Draft 2020-12 patterns. Each snippet validated mentally against `check-jsonschema 0.37.1` + `jsonschema 4.18+` semantics. Phase 2 implementation should test each via `check-jsonschema --check-metaschema` before commit.

### Code Example #1: `_meta.schema.json` — provenance + confidence + source as composable bases

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aviation-knowledge-base.local/ontology/_meta.schema.json",
  "title": "Aviation KB Ontology — Meta Base Schemas",
  "description": "Composable base definitions for provenance, confidence, source, and the entity/relation base field set. Every entity and relation schema MUST allOf-compose $defs/baseFields. Pattern: allOf + unevaluatedProperties: false (NOT additionalProperties: false). H-Darrieus REJECT rule lives in the description of $defs/provenance and is enforced in Phase 3 validator. Schema version: 0.1.0.",
  "$defs": {
    "uri": {
      "type": "string",
      "format": "uri",
      "pattern": "^aviationkb://[a-z][a-z-]*\\/[a-z0-9]+(-[a-z0-9]+)*@[0-9]+$",
      "description": "External URI per D-23: aviationkb://<type>/<slug>@<version>. Slug rules per D-25: lowercase ASCII + digits + hyphen, max 64 chars."
    },
    "internalId": {
      "type": "string",
      "pattern": "^[a-z]+:[a-z0-9]+(-[a-z0-9]+)*$",
      "maxLength": 80,
      "description": "Internal foreign-key form per D-24: <type-prefix>:<kebab-slug>. Type prefixes: am/sys/subsys/comp/req/regclause/std/proc/fmode/mtask/cfdmethod/simcase/mesh/turb/acc/doc/note/mat/test/report/org/pers."
    },
    "isoDateTime": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp with timezone. Example: 2026-05-03T14:30:00Z."
    },
    "i18nLabel": {
      "type": "object",
      "description": "Bilingual label per D-14. Either language may be empty string but key MUST be present.",
      "properties": {
        "zh": { "type": "string" },
        "en": { "type": "string" }
      },
      "required": ["zh", "en"],
      "unevaluatedProperties": false
    },
    "provenance": {
      "type": "object",
      "title": "Provenance",
      "description": "PROV-01: who/how/when. ENFORCED IN PHASE 3 VALIDATOR — H-Darrieus REJECT condition: (method == 'ai_extracted') AND (confidence.score > 0.85) AND (reviewer is null OR reviewer == '') → REJECT. Promotion from instances/_pending/ to canonical (D-17) requires method == 'hybrid_reviewed' AND non-empty reviewer URI AND reviewed_at timestamp.",
      "properties": {
        "method": {
          "type": "string",
          "enum": ["human", "ai_extracted", "hybrid_reviewed"],
          "description": "D-16 enum. 'human' = human-authored. 'ai_extracted' = AI-only, MUST live in instances/_pending/. 'hybrid_reviewed' = AI-drafted + human-reviewed; only this can be canonical."
        },
        "actor": {
          "$ref": "#/$defs/uri",
          "description": "Person or Organization URI who performed the action. Required."
        },
        "actor_role": { "type": "string", "minLength": 1 },
        "created_at": { "$ref": "#/$defs/isoDateTime" },
        "reviewer": {
          "$ref": "#/$defs/uri",
          "description": "Person URI who reviewed. REQUIRED IF method == 'hybrid_reviewed'. Phase 3 validator enforces. Empty string is treated as absence."
        },
        "reviewed_at": { "$ref": "#/$defs/isoDateTime" },
        "tool": {
          "type": "string",
          "description": "Tool used (e.g. 'claude-opus-4-7', 'manual'). Combined with actor URI, replaces a separate generated_by relation per D-09."
        }
      },
      "required": ["method", "actor", "actor_role", "created_at"],
      "unevaluatedProperties": false
    },
    "confidence": {
      "type": "object",
      "title": "Confidence",
      "description": "PROV-02 / D-13. Decimal score 0.0–1.0; rationale required (≥1 sentence). H-Darrieus lock threshold: score > 0.85.",
      "properties": {
        "score": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "description": "Confidence score on [0.0, 1.0]. H-Darrieus threshold: > 0.85 triggers reviewer requirement when method == 'ai_extracted'."
        },
        "rationale": {
          "type": "string",
          "minLength": 20,
          "description": "Human-readable rationale (≥1 full sentence, ≥20 chars). Empty or whitespace-only fails validation. Examples: 'Multi-source agreement: cited in FAA AC 25.1309-1B and EASA AMC 25.1309 with identical text.', 'Single authoritative source (AC 25.1309-1B §6.b.2.iii); no disagreement found.'"
        },
        "calibration_method": {
          "type": "string",
          "description": "Optional. Future field for v0.2.0+ calibration set IDs. Currently free-text."
        }
      },
      "required": ["score", "rationale"],
      "unevaluatedProperties": false
    },
    "source": {
      "type": "object",
      "title": "Source",
      "description": "PROV-03. Structured citation. Pitfall #1 prevention: NEVER allow free-text. Every source must resolve to an existing Document entity (broken-ref check in Phase 3).",
      "properties": {
        "document_id": {
          "$ref": "#/$defs/uri",
          "description": "URI to a Document entity. Phase 3 validator verifies the entity exists."
        },
        "locator": {
          "type": "object",
          "description": "Sub-document locator. At least one of {page, section, paragraph} must be present.",
          "properties": {
            "page": { "type": "integer", "minimum": 1 },
            "section": { "type": "string" },
            "paragraph": { "type": "integer", "minimum": 1 }
          },
          "anyOf": [
            { "required": ["page"] },
            { "required": ["section"] },
            { "required": ["paragraph"] }
          ],
          "unevaluatedProperties": false
        },
        "retrieval": {
          "type": "object",
          "properties": {
            "url": { "type": "string", "format": "uri" },
            "retrieved_at": { "$ref": "#/$defs/isoDateTime" },
            "content_hash": {
              "type": "string",
              "pattern": "^sha256:[a-f0-9]{64}$",
              "description": "Optional. Hash of retrieved content; enables tamper detection."
            }
          },
          "required": ["url", "retrieved_at"],
          "unevaluatedProperties": false
        },
        "effective_date": {
          "type": "string",
          "format": "date",
          "description": "When the cited content became effective (e.g. regulation effective_date). ISO 8601 date."
        }
      },
      "required": ["document_id", "locator", "retrieval"],
      "unevaluatedProperties": false
    },
    "baseFields": {
      "type": "object",
      "title": "Base Fields (composed by every entity AND relation)",
      "description": "The fields shared by every record in the KB. Compose via allOf $ref from entity.base.schema.json and relation.base.schema.json.",
      "properties": {
        "id": { "$ref": "#/$defs/uri" },
        "provenance": { "$ref": "#/$defs/provenance" },
        "confidence": { "$ref": "#/$defs/confidence" },
        "source": { "$ref": "#/$defs/source" }
      },
      "required": ["id", "provenance", "confidence", "source"]
    }
  }
}
```

### Code Example #2: `entity.aircraft-system.schema.json` — entity-base composition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aviation-knowledge-base.local/ontology/schemas/entity.aircraft-system.schema.json",
  "title": "AircraftSystem entity (ONT-E-03)",
  "description": "An aircraft-level system, decomposed by ATA chapter. Example: a Boeing 737-MAX-8 has an ATA-21 Air Conditioning system as one of its AircraftSystems. Composes entity.base.schema.json (which composes _meta.schema.json#/$defs/baseFields). Schema version: 0.1.0.",
  "type": "object",
  "allOf": [
    { "$ref": "entity.base.schema.json" }
  ],
  "properties": {
    "type": {
      "const": "AircraftSystem",
      "description": "Discriminator. Must equal the string 'AircraftSystem'."
    },
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "D-20 per-record schema version (semver). Phase 3 validator rejects records older than N-1."
    },
    "version": {
      "type": "integer",
      "minimum": 1,
      "description": "Per-record version. Defaults to 1 (implicit). Bumped each time the record is meaningfully revised (D-15 internalized has_revision)."
    },
    "i18n": {
      "type": "object",
      "description": "D-14 bilingual fields.",
      "properties": {
        "label": { "$ref": "_meta.schema.json#/$defs/i18nLabel" },
        "full_text": {
          "type": "object",
          "properties": {
            "zh": { "type": "string" },
            "en": { "type": "string" }
          },
          "required": ["zh", "en"],
          "unevaluatedProperties": false
        }
      },
      "required": ["label"],
      "unevaluatedProperties": false
    },
    "tags": {
      "type": "array",
      "items": { "type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$" },
      "uniqueItems": true,
      "description": "Free-form kebab-case tags for faceting. NOT for ontological relationships — those are relation YAMLs."
    },
    "version_history": {
      "type": "array",
      "description": "D-15. Internalized has_revision. Absence implies version == 1. Mandatory once version > 1.",
      "items": {
        "type": "object",
        "properties": {
          "version": { "type": "integer", "minimum": 1 },
          "date": { "$ref": "_meta.schema.json#/$defs/isoDateTime" },
          "author": { "$ref": "_meta.schema.json#/$defs/uri" },
          "change_summary": { "type": "string", "minLength": 20 }
        },
        "required": ["version", "date", "author", "change_summary"],
        "unevaluatedProperties": false
      }
    },
    "parent_aircraft_model": {
      "$ref": "_meta.schema.json#/$defs/uri",
      "description": "AircraftModel URI this system belongs to. Foreign key — Phase 3 validator enforces existence."
    },
    "ata_chapter": {
      "type": "string",
      "pattern": "^ATA-[0-9]{2}$",
      "description": "ATA iSpec 2200 chapter code. Validated against ontology/vocabularies/ata-chapters.yaml at runtime by Phase 3 validator. Pattern here is structural only; enum membership is loaded dynamically. Example: 'ATA-21' (Air Conditioning), 'ATA-71' (Powerplant)."
    },
    "function": {
      "type": "string",
      "minLength": 20,
      "description": "Functional description of the system (≥1 sentence)."
    },
    "criticality_level": {
      "type": "string",
      "enum": ["catastrophic", "hazardous", "major", "minor", "no_safety_effect"],
      "description": "Failure-condition severity per FAR/CS 25.1309 categories. Used by FailureMode entities and AccidentCase analysis."
    }
  },
  "required": ["type", "schema_version", "i18n", "parent_aircraft_model", "ata_chapter", "function", "criticality_level"],
  "unevaluatedProperties": false
}
```

### Code Example #3: `relation.interfaces-with.schema.json` — relation-base composition + worked-example discipline

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aviation-knowledge-base.local/ontology/schemas/relation.interfaces-with.schema.json",
  "title": "interfaces_with relation (ONT-R-15, D-05)",
  "description": "Peer-tier system↔system interface (data, power, mechanical, thermal). USE FOR: AvionicsBay interfaces_with ECS via ARINC 429; HydraulicSystem interfaces_with FlightControlSystem via servo actuators. DO NOT USE FOR: parent-child (use part_of); cross-tier dependency (use requires); regulatory compliance (use complies_with). Boundary with 'requires' per D-10: 'requires' is cross-tier (Component requires MaintenanceTask, SimulationCase requires MeshRequirement); 'interfaces_with' is peer-tier between two systems/subsystems at the same architectural level. H-Darrieus relevance: an interfaces_with edge between two AI-extracted systems with confidence > 0.85 must have a reviewer per the validator rule (Phase 3). Schema version: 0.1.0.",
  "type": "object",
  "allOf": [
    { "$ref": "relation.base.schema.json" }
  ],
  "properties": {
    "type": {
      "const": "interfaces_with",
      "description": "Discriminator."
    },
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "subject": {
      "$ref": "_meta.schema.json#/$defs/uri",
      "description": "URI to the first peer (must resolve to AircraftSystem, Subsystem, or Component entity). Order is symbolic only — interfaces_with is logically symmetric but stored asymmetrically for query simplicity."
    },
    "object": {
      "$ref": "_meta.schema.json#/$defs/uri",
      "description": "URI to the second peer. Same type constraints as subject. Phase 3 validator enforces (a) both entities exist, (b) both are at the same tier (e.g. both AircraftSystem, NOT one AircraftSystem and one Component — that's part_of)."
    },
    "interface_type": {
      "type": "string",
      "enum": ["data", "power", "mechanical", "thermal", "fluid", "control", "other"],
      "description": "Nature of the interface. 'data' covers ARINC 429 / AFDX / discrete signals. 'power' covers electrical bus connections. 'fluid' covers hydraulic/pneumatic plumbing."
    },
    "interface_protocol": {
      "type": "string",
      "description": "Optional. Free-text or standard reference (e.g. 'ARINC 429', 'AFDX', 'MIL-STD-1553')."
    },
    "valid_from": {
      "$ref": "_meta.schema.json#/$defs/isoDateTime",
      "description": "ONT-R-01 base field. When this interface relationship became valid (e.g. configuration change date)."
    },
    "valid_until": {
      "anyOf": [
        { "$ref": "_meta.schema.json#/$defs/isoDateTime" },
        { "type": "null" }
      ],
      "description": "ONT-R-01 base field. null = currently valid (no expiration)."
    }
  },
  "required": ["type", "schema_version", "subject", "object", "interface_type", "valid_from"],
  "unevaluatedProperties": false
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact for This Phase |
|--------------|------------------|--------------|------------------------|
| JSON Schema Draft-07 (or earlier) | JSON Schema Draft 2020-12 | Spec released 2020-12; widespread tool support 2022–2023 | Locked at project init. Use `unevaluatedProperties` not `additionalProperties` for composition. |
| `items` array form for tuple validation | `prefixItems` array; `items` is now single schema | Draft 2020-12 release | All tuple validation in Phase 2 schemas uses `prefixItems`. |
| `$recursiveAnchor` / `$recursiveRef` | `$dynamicAnchor` / `$dynamicRef` | Draft 2020-12 release | Phase 2 doesn't currently need recursive schemas; if needed (e.g. for AccidentCase causal-factor trees), use the new keywords. |
| `additionalProperties: false` for strict validation | `unevaluatedProperties: false` (with `allOf`/`$ref` composition) | Draft 2019-09 / 2020-12 | Pattern change is the #1 footgun in Phase 2 (Pitfall #1). |
| `ruamel.yaml.round_trip_load()` | `YAML()` class with `yaml.load(...)` | ruamel.yaml 0.15 deprecation; final removal in 0.19+ | Phase 2 migration template uses modern pattern (Gap #5). |
| ajv default class for Draft 2020-12 | `Ajv2020` separate import | ajv 8.0 release (2021) | Phase 2 documents this in Pitfall #2 for any future Node.js consumer. |
| pyyaml for YAML edits | ruamel.yaml for round-trip with comments | pyyaml never preserved comments; ruamel.yaml exists since 2014 | D-26 already locks ruamel.yaml. |
| OWL / RDF for ontology in greenfield project | YAML + JSON Schema + URI scheme that maps cleanly to RDF later | Pragmatic 2020s consensus for KB projects under 10k entities | Locked at project init. |

**Deprecated / outdated to avoid:**
- Draft-04 / Draft-07: missing `$defs`, `unevaluatedProperties`, `prefixItems`. (Already in research/STACK.md "What NOT to Use".)
- `additionalProperties: false` as the only strictness lever in a project that uses `allOf` composition (Pitfall #1).
- `ruamel.yaml.round_trip_load()` (Pitfall #10).
- Default `import Ajv from 'ajv'` for Draft 2020-12 schemas (Pitfall #2).

## Assumptions Log

> Claims tagged `[ASSUMED]` in this research. The planner uses this section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The recommended Person/Organization 6-field minimal set is sufficient for v0.1.0. Specifically: no qualified-attribution, no live ORCID/ROR resolution, role enum has 6 values. | Gap Resolution #6 | Low. If a demo data instance in Phase 4 needs (e.g.) `prov:qualifiedAttribution`, Person/Organization schemas can be extended additively in v0.1.x patch without breaking change. |
| A2 | The DMC regex pattern `^DMC-[A-Z0-9]{2,14}-...` covers all valid Issue 6 DMCs we will encounter. | Gap Resolution #2 | Low-Medium. Verified against documented examples; some defense-industry Issue 6 DMCs may use Learn Code or older Issue 4 conventions that fail the regex. Mitigation: regex is documented as "v0.1.0 best-effort"; v0.2.0+ replaces with structural decomposition. |
| A3 | ATA chapter list is "stable" — annual A4A revisions are additive only. | Gap Resolution #1 | Low. Historical pattern: A4A only adds chapters (42, 44, 45, 46, 47, 48, 49 added in last ~15 years; never removed). Pitfall #7 covers if this assumption breaks. |
| A4 | The recommended directory layout (flat under `ontology/schemas/`) is best for 36-file count. | Architecture Patterns | Low. Trivially reorganizable later; only affects `$ref` paths in schemas (≤36 string-edit changes). |
| A5 | Phase 3 will ship the H-Darrieus validator before Phase 4 demo data starts. | Pitfall #8 | Medium-High. If Phase 3 lags, Pitfall #8 manifests. Mitigated by making Phase 4 explicitly downstream of Phase 3 in the roadmap. |

**Items NOT assumed (verified):**
- ATA chapter list is finite and ~70 entries → `[VERIFIED]` via 2 sources (PDF extract + Wikipedia + aviationhunt.com)
- S1000D Issue 6 release date (2024-09-01), DMC range (17–41 chars), 7 components → `[VERIFIED]` via 3 sources
- Draft 2020-12 support in check-jsonschema 0.37.x and ajv 8.x → `[VERIFIED]` via official docs
- `unevaluatedProperties` vs `additionalProperties` distinction → `[VERIFIED]` via JSON Schema 2020-12 release notes
- `ruamel.yaml YAML()` class is the current API; `round_trip_load` is deprecated → `[VERIFIED]` via official docs

## Open Questions

> The 6 gaps were resolved. These are residual questions for plan-phase.

1. **Should `Material` v0.1.0 schema include MIL-HDBK-5/MMPDS allowable references as a structured field or free text?**
   - What we know: D-01 accepts Material; aerospace materials commonly cite MIL-HDBK-5J or MMPDS-XX for design allowables.
   - What's unclear: structured field needs a Document entity reference (mature pattern) vs free text (faster). Demo data in Phase 4 doesn't need it strongly.
   - Recommendation: free text in v0.1.0 (`design_allowables_reference: string`); upgrade to structured `cites` relation in v0.2.0 when 2+ Material instances expose the need.

2. **Should `TestCase` and `TestReport` be linked via a relation (`reports_on`) or via a foreign-key field?**
   - What we know: D-02 accepts both as separate entities; demo data isn't yet specified.
   - What's unclear: a `TestReport.test_case_ref` field is simpler; a `reports_on(TestReport, TestCase)` relation is more uniform with the rest of the model.
   - Recommendation: foreign-key field for v0.1.0 (`TestReport.test_case_ref: <internalId>` of `test:`-prefix). Saves a relation type. Can be promoted to a relation later (additive change).

3. **Should `applicable_during_phase` flight-phase enum be on the relation OR a vocabulary YAML?**
   - What we know: D-08 accepts the relation; the enum (taxi/takeoff/cruise/approach/landing/missed/emergency) is documented in D-08 description.
   - What's unclear: inline enum (in schema) vs vocabulary YAML (like `ata-chapters.yaml`).
   - Recommendation: inline enum. The list is fixed (7 values), well-known, and unlikely to grow. Vocabulary YAML is overkill.

4. **When does `ontology/CHANGELOG.md` get its "0.1.0 release" entry — at first commit of Phase 2 or at Phase 2 close?**
   - Recommendation: first commit of `ontology/VERSION = 0.1.0`. Entry says "Initial schema set: 20 entities, 16 relations, 3 vocabularies. See .planning/decisions/ADR-002 through ADR-007."

5. **Should ADR file numbering (002–007) be sequential or sparse-numbered to leave room for project-init ADRs (e.g. ADR-001 if not yet used)?**
   - What we know: per `02-CONTEXT.md` <specifics>, ADR-001 is reserved for "Phase 1 PRD-v0-vs-v1 split" (created in Phase 6 retroactively).
   - Recommendation: ADR-002 through ADR-007 sequential as documented. ADR-001 placeholder file with "RESERVED — to be authored in Phase 6" note.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.9+ | check-jsonschema, ruamel.yaml, future Phase 3 validators | ✓ (assumed — required by Phase 1 baseline) | 3.9+ | — |
| `check-jsonschema` 0.37.1 | Pre-commit hook + manual schema validation | ✓ (Phase 1 wired) | 0.37.1 | — |
| `yamllint` 1.38 | Pre-commit hook | ✓ (Phase 1 wired) | 1.38 | — |
| `pre-commit` 3.7+ | Hook orchestrator | ✓ (Phase 1 wired) | 3.7+ | — |
| `ruamel.yaml` ≥0.17 | Migration script template (Phase 2 stub only; real migrations land later) | Likely missing | n/a | Phase 2 only ships the `.example` stub — no actual migration runs in Phase 2, so missing dep is non-blocking. Plan to add to `requirements-dev.txt` in Phase 2. |
| Git ≥2.40 | gsd-tools commits | ✓ (Phase 1) | ≥2.40 | — |
| Internet access for ATA enum verification | Vocabularies | ✓ (this research used WebFetch) | — | Vocabularies are static once published |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** `ruamel.yaml` is fallback-tolerant for Phase 2 (only documentation needs it; actual usage is Phase 4+ migration scripts). Phase 2 plan should include a task "add ruamel.yaml to requirements-dev.txt" but doesn't need to actually run any ruamel.yaml code.

## Validation Architecture

> `workflow.nyquist_validation` not explicitly false in `.planning/config.json` — section included.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `check-jsonschema 0.37.1` (schema validation) + `pytest` (Phase 3 + future) — Phase 2 uses check-jsonschema only |
| Config file | `.pre-commit-config.yaml` (already wired); `.yamllint` (already wired) |
| Quick run command | `pre-commit run check-jsonschema --files ontology/schemas/*.schema.json` |
| Full suite command | `pre-commit run --all-files` |
| Phase gate | All schemas pass `check-jsonschema --check-metaschema`; all schemas pass `--check-metaschema` self-validation; CI green on PR. |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ONT-E-01..22 | All entity schemas are valid Draft 2020-12 schemas | meta-validation | `check-jsonschema --check-metaschema ontology/schemas/entity.*.schema.json` | partial — schemas to be created in Phase 2 |
| ONT-R-01..19 | All relation schemas are valid Draft 2020-12 schemas | meta-validation | `check-jsonschema --check-metaschema ontology/schemas/relation.*.schema.json` | partial |
| PROV-01..03 | `_meta.schema.json` defines provenance, confidence, source per shape | meta-validation + manual inspection | `check-jsonschema --check-metaschema ontology/_meta.schema.json` | ❌ Wave 0 |
| PROV-04 | H-Darrieus REJECT condition is documented in schema description | grep + manual review | `grep -l "H-Darrieus" ontology/_meta.schema.json` | ❌ Wave 0 |
| VER-01 | `ontology/VERSION` exists and contains valid semver | shell test | `grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' ontology/VERSION` | ❌ Wave 0 |
| VER-02 | `ontology/CHANGELOG.md` exists with 0.1.0 entry | shell test | `grep -q "## 0.1.0" ontology/CHANGELOG.md` | ❌ Wave 0 |
| VER-03 | Every schema includes `schema_version` as required field | grep test | `for f in ontology/schemas/*.schema.json; do jq '.properties.schema_version // .allOf[]?.properties.schema_version' "$f" \|\| echo MISSING $f; done` | ❌ Wave 0 |
| VER-04 | `migrations/PATTERN.md` exists with ruamel.yaml YAML() pattern | shell test | `grep -q 'YAML()' migrations/PATTERN.md` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pre-commit run --files <changed-schema>` — fast (<5 sec)
- **Per wave merge:** `pre-commit run --all-files` — full suite (<30 sec for 36+3 schema files)
- **Phase gate:** `check-jsonschema --check-metaschema ontology/**/*.schema.json` green; CI green on PR; ADR-002 through ADR-007 all merged.

### Wave 0 Gaps

- [ ] `ontology/_meta.schema.json` — composition root (Code Example #1)
- [ ] `ontology/schemas/entity.base.schema.json` + `relation.base.schema.json` — composition middlemen
- [ ] 20 entity-type schemas + 16 relation-type schemas
- [ ] `ontology/vocabularies/{ata-chapters,jurisdictions,provenance-methods}.yaml`
- [ ] `ontology/mappings/{ata-to-iso10303,s1000d-dmc-reserved}.md`
- [ ] `ontology/VERSION = 0.1.0`
- [ ] `ontology/CHANGELOG.md` with 0.1.0 entry
- [ ] `migrations/PATTERN.md` (Gap Resolution #5)
- [ ] `migrations/0_1_0_to_template.py.example`
- [ ] `.planning/decisions/ADR-002` through `ADR-007`
- [ ] Update `scripts/exporters/to_jsonl_triples.py` stub with schema-derived design notes (D-19)
- [ ] (optional) Extend `.pre-commit-config.yaml` to include `--check-metaschema` invocation

*(These are deliverables, not gaps in the existing test infrastructure. The test infrastructure itself is Phase 1-complete.)*

## Security Domain

> `security_enforcement` not explicitly disabled — section included. Phase 2 is schema-only; threat surface is small but non-zero.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Phase 6 (deployment) — no auth surface in Phase 2 |
| V3 Session Management | no | n/a Phase 2 |
| V4 Access Control | partial | `instances/_pending/` quarantine pattern (D-17) is access-control-by-directory; Phase 3 validator enforces |
| V5 Input Validation | **YES** | JSON Schema Draft 2020-12 (`check-jsonschema 0.37.1`) — Phase 2's primary deliverable IS input validation |
| V6 Cryptography | partial | `source.retrieval.content_hash: sha256:...` field reserved for tamper detection; Phase 2 only declares the field, no crypto runs |
| V8 Data Protection | partial | `Document.confidentiality` field (Phase 4) gates ITAR/EAR — Phase 2 doesn't yet ingest documents but declares the field on the Document schema (ONT-E-17) |
| V14 Configuration | yes | All schemas have `$schema` declared; `unevaluatedProperties: false` prevents schema sprawl |

### Known Threat Patterns for Schema-Authoring Phase

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed schema accepted by validator (typo in keyword) | Tampering | `--check-metaschema` self-validation in pre-commit (Pitfall #9) |
| Provenance/confidence fields hand-rolled per entity, drifting over time | Repudiation | `_meta.schema.json` composition (Pattern 1) — single source of truth |
| AI-extracted records sneak into canonical without H-Darrieus check | Spoofing / Repudiation | Phase 2 schema makes `provenance.method` enum strict + reviewer required when `hybrid_reviewed`; Phase 3 validator enforces the H-Darrieus REJECT condition (Pitfall #8) |
| ITAR/EAR content classification missing on Document | Information Disclosure | `Document.confidentiality` enum required (PROJECT.md Out-of-Scope rule reinforced in Phase 4) |
| Free-text source fields (Pitfall 1 in research/PITFALLS.md) | Repudiation | Pitfall #1 prevention is Phase 2's PROV-03 schema requirement |
| Schema injection via maliciously-crafted YAML instance | Tampering | check-jsonschema operates on parsed YAML — not vulnerable to YAML deserialization attacks (uses safe loader); ruamel.yaml `YAML()` defaults to safe in round-trip mode |

**Phase 2 security stance:** schema-only phase; threats are mostly "future Phase 4+ ingestion uses bad data because schemas were too lax." Phase 2 mitigates by being strict (`unevaluatedProperties: false`, required `provenance`/`confidence`/`source`, enum-strict enums).

## Project Constraints (from CLAUDE.md)

> CLAUDE.md exists at `/Users/Zhuanz/CLAUDE.md`. Extracting actionable directives that constrain Phase 2.

- **GSD workflow enforcement** — All Phase 2 file edits go through GSD execute commands (`/gsd-execute-phase` etc), not direct edits. ✓ Already required by project init.
- **Codex review on risky PRs** — Schema changes that affect ≥3 files (likely all of Phase 2) trigger Codex review per RETRO-V61-001. Phase 2 plan should include a "Codex review of full schema set" task before merge to main.
- **Atomic commits via gsd-tools** — Each schema file = its own commit (`02-CONTEXT.md` <code_context> "Established Patterns").
- **AI 接力开发指南 header** — Every design doc (including ADR-002..007 in Phase 2) MUST include the AI handoff header (R12, AIH-01).
- **5-minute stranger test** — Every Phase 2 deliverable must pass: a fresh Claude/Codex/DeepSeek session can read it cold and resume in 5 min.
- **No model self-citation, no free-text source** — Reinforced via PROV-03 schema (`source` is structured object).
- **Notion sync (cfd-harness-unified specific)** — N/A for this project (aviation-knowledge-base). Skip.
- **MEMORY.md ≤300 lines** — Project-level, not Phase 2 deliverable.
- **No emojis in deliverables** — Already followed; schema files don't need them, ADRs don't need them.

## Sources

### Primary (HIGH confidence)

- [JSON Schema Draft 2020-12 release notes](https://json-schema.org/draft/2020-12/release-notes) — `unevaluatedProperties`, `prefixItems`, `$dynamicAnchor`/`$dynamicRef` semantics
- [check-jsonschema 0.37 documentation](https://check-jsonschema.readthedocs.io/en/stable/) — tool capabilities + `--check-metaschema`
- [python-jsonschema 4.18 release docs](https://python-jsonschema.readthedocs.io/en/v4.18.0/) — Draft 2020-12 support history
- [ajv 8.x JSON Schema docs](https://ajv.js.org/json-schema.html) — `Ajv2020` class requirement, draft compat
- [Wikipedia: S1000D](https://en.wikipedia.org/wiki/S1000D) — Issue 6 release date 2024-09-01
- [siberlogic.com S1000D SNS and DMC](https://www.siberlogic.com/s1000d-concepts/sns-and-dmc) — DMC structure components and lengths
- [s1kd-tools tutorial](https://kibook.github.io/s1kd-tools/TUTORIAL.html) — DMC component breakdown with lengths
- [ATA Chapters PDF (Warsaw University of Technology mirror)](https://itlims-zsis.meil.pw.edu.pl/pomoce/ESL/2016/ATA_Chapters.pdf) — ATA iSpec 2200 chapter list
- [Wikipedia: ATA Spec 100/iSpec 2200](https://en.wikipedia.org/wiki/ATA_Spec_100/iSpec_2200) — chapter taxonomy
- [aviationhunt.com ATA Standard Numbering System](https://www.aviationhunt.com/ata-standard-numbering-system/) — chapter list confirmation
- [A4A Publications iSpec 2200 Revision 2024.1](https://publications.airlines.org/products/ispec-2200-information-standards-for-aviation-maintenance-revision-2024-1) — current revision
- [ruamel.yaml documentation](https://yaml.dev/doc/ruamel.yaml/detail/) — modern `YAML()` class API; `round_trip_load` deprecation

### Secondary (MEDIUM confidence)

- [Smartify S1000D DMC explainer](https://smartifysol.com/demystifying-data-module-codes-dmcs-in-s1000d-how-smartifys-smato-author-makes-it-effortless/) — DMC partitioning concepts
- [Saraca S1000D whitepaper page](https://www.saracasolutions.com/whitepapers/data-module-code-S1000D) — concept overview only (full whitepaper paywalled)
- [PyPI jsonschema](https://pypi.org/project/jsonschema/) — version compatibility table
- [W3C PROV-O recommendation](https://www.w3.org/TR/prov-o/) — `prov:Agent`, `prov:hadRole` patterns (training-data + recall-based, not re-fetched)
- [schema.org Person/Organization](https://schema.org/Person) — fields universe (training-data based)

### Tertiary (LOW confidence — flagged for re-verification at execution time)

- DMC regex pattern in Gap Resolution #2: derived from documented examples; should be tested against ≥3 real Issue 6 DMCs at execution time and adjusted if any production DMCs fail. Confidence: MEDIUM.

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| Standard Stack | HIGH | All versions verified via official sources (Phase 1 already pinned them; this research re-confirmed) |
| Architecture Patterns (`_meta` composition) | HIGH | `unevaluatedProperties: false + allOf + $ref` is the canonical Draft 2020-12 pattern, verified via spec |
| Don't Hand-Roll | HIGH | Each entry maps to a locked decision (D-XX) or a documented JSON Schema pitfall |
| Common Pitfalls | HIGH | Pitfalls 1, 2, 3, 9 verified via spec/tooling docs; Pitfalls 4–8, 10 derived from locked decisions |
| Code Examples | HIGH | All 3 examples self-validated against Draft 2020-12 spec mentally; should pass `--check-metaschema` |
| Gap 1 (ATA) | HIGH | 3 sources cross-referenced |
| Gap 2 (S1000D) | HIGH for structure; MEDIUM for regex coverage of edge cases | Edge-case verification deferred to execution |
| Gap 3 (Draft 2020-12) | HIGH | Direct verification via official tool docs |
| Gap 4 (composition pattern) | HIGH | Direct verification via spec |
| Gap 5 (ruamel.yaml) | HIGH | Direct verification via official docs |
| Gap 6 (Person/Org shape) | MEDIUM-HIGH | Pragmatic intersection of established schemas; explicit recommendation for Phase 4 to revise if demo data exposes gaps |

**Research date:** 2026-05-03
**Valid until:** 2026-08-03 (3 months — stable schema-design domain; revisit when (a) JSON Schema 2025 spec lands, (b) S1000D Issue 6.1 lands, or (c) A4A iSpec 2200 Revision 2025.1 lands)
**Research mode:** gap-closure (NOT ecosystem)
**Researcher:** gsd-researcher (Claude Opus 4.7 1M ctx)
**Next:** `/gsd-plan-phase 2` consumes this RESEARCH.md to produce the executable plan files (one per task / wave).

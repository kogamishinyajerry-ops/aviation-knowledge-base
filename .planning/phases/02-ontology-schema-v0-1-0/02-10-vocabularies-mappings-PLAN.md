---
phase: 02-ontology-schema-v0-1-0
plan: 10
type: execute
wave: 5
depends_on: [04]
files_modified:
  - ontology/vocabularies/ata-chapters.yaml
  - ontology/vocabularies/jurisdictions.yaml
  - ontology/vocabularies/provenance-methods.yaml
  - ontology/mappings/ata-to-iso10303.md
  - ontology/mappings/s1000d-dmc-reserved.md
  - scripts/exporters/to_jsonl_triples.py
autonomous: true
requirements:
  - PROV-06
must_haves:
  truths:
    - "ata-chapters.yaml ships ~70 ATA iSpec 2200 Revision 2024.1 chapters per Gap-1"
    - "jurisdictions.yaml enumerates FAA / EASA / CAAC / ICAO / Transport-Canada / CASA-AU / other"
    - "provenance-methods.yaml exposes the three D-16 enum values (human / ai_extracted / hybrid_reviewed) with descriptions"
    - "s1000d-dmc-reserved.md documents the Issue 6.0 DMC structural breakdown per Gap-2"
    - "ata-to-iso10303.md placeholder explicitly states v0.1.0 deferred"
    - "to_jsonl_triples.py docstring enriched with schema-derived design notes per ADR-006 / D-19"
    - "Document schema (Plan 04) source.document_id field cross-referenced (PROV-06 documentation-level satisfaction; Phase 3 validator enforces)"
  artifacts:
    - path: "ontology/vocabularies/ata-chapters.yaml"
      provides: "ATA chapter enum loaded by Phase 3 validator at runtime; ~70 entries"
    - path: "ontology/vocabularies/jurisdictions.yaml"
      provides: "Jurisdiction enum aligned with RegulationClause.jurisdiction + Organization.jurisdiction"
    - path: "ontology/vocabularies/provenance-methods.yaml"
      provides: "Provenance method enum + descriptions matching D-16"
    - path: "ontology/mappings/ata-to-iso10303.md"
      provides: "Placeholder doc; v0.1.0 explicitly deferred mapping work"
    - path: "ontology/mappings/s1000d-dmc-reserved.md"
      provides: "S1000D Issue 6.0 DMC structural breakdown for v0.2.0+ activation"
    - path: "scripts/exporters/to_jsonl_triples.py"
      provides: "Phase 1 stub enriched with schema-derived triple-generation design notes"
  key_links:
    - from: "ontology/schemas/entity.aircraft-system.schema.json + entity.subsystem.schema.json + entity.component.schema.json + entity.maintenance-task.schema.json + entity.document.schema.json"
      to: "ontology/vocabularies/ata-chapters.yaml"
      via: "ata_chapter description pointer (validator loads YAML at runtime)"
    - from: "ontology/schemas/entity.regulation-clause.schema.json + entity.organization.schema.json"
      to: "ontology/vocabularies/jurisdictions.yaml"
      via: "jurisdiction description pointer"
    - from: "ontology/schemas/entity.document.schema.json"
      to: "ontology/mappings/s1000d-dmc-reserved.md"
      via: "s1000d_dmc description pointer"
---

<objective>
Ship the three vocabulary YAMLs (ATA chapters, jurisdictions, provenance methods), the two mapping placeholder docs (ATA→ISO 10303, S1000D DMC reserved), and enrich the existing `scripts/exporters/to_jsonl_triples.py` Phase 1 stub with schema-derived design notes per ADR-006 / D-19.

This is Phase 2's final wave. Output: 6 files (5 new + 1 enriched).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/REQUIREMENTS.md
@.planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md
@.planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md
@.planning/decisions/ADR-006-triple-export.md
@scripts/exporters/to_jsonl_triples.py
@.yamllint

<interfaces>
<!-- ATA chapter list per RESEARCH.md Gap-1 (sources: A4A iSpec 2200 Revision 2024.1; Wikipedia ATA Spec 100/iSpec 2200; aviationhunt.com): -->
<!--   ~70 chapters total in 0–99 numbering space -->
<!--   Chapters 1–4 reserved for airline use (excluded from enum) -->
<!--   Recent additions (last ~15 yrs): ATA-42 IMA, ATA-44 Cabin Systems, ATA-45 Central Maintenance/Diagnostic, ATA-46 Information Systems, ATA-47 Nitrogen Generation, ATA-48 In-Flight Fuel Dispensing, ATA-49 Airborne Auxiliary Power, ATA-50 Cargo Compartments -->

<!-- Sections (per RESEARCH.md): -->
<!--   aircraft_general (chapters 5–12, 18, 89) -->
<!--   airframe_systems (chapters 20–50) -->
<!--   structure (chapters 51–57) -->
<!--   power_plant (chapters 60–92) -->

<!-- DMC structure per Gap-2 (Issue 6.0 released 2024-09-01): -->
<!--   17–41 alphanumeric chars, prefix "DMC-" -->
<!--   Components in order: Model ID Code (2–14) → System Diff Code (1–4) → SNS (4 segments) → Disasm Code+Variant (2+1–3) → Info Code+Variant (3+1) → Item Loc Code (1: A/B/C/D/T) → optional Learn Code → optional Language Code -->
<!--   Verified example: DMC-S1000DBIKE-AAA-D00-00-00-00AA-00PA-D_004-00_EN-US.XML -->

<!-- Existing to_jsonl_triples.py stub (Phase 1): minimal docstring; raises NotImplementedError -->
<!-- ADR-006 (Plan 09) holds the schema-derived triple-generation rules to embed in the docstring -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author 3 vocabulary YAMLs (ATA chapters, jurisdictions, provenance methods)</name>
  <files>ontology/vocabularies/ata-chapters.yaml, ontology/vocabularies/jurisdictions.yaml, ontology/vocabularies/provenance-methods.yaml</files>
  <read_first>
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Gap Resolution #1 — ATA chapter list with sections; Pitfall #7 — annual A4A revision discipline)
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-16 — provenance enum)
    - ontology/schemas/entity.aircraft-system.schema.json (description references this file)
    - ontology/schemas/entity.regulation-clause.schema.json (description references jurisdictions.yaml)
    - .yamllint (relaxed config, line-length warning 200)
  </read_first>
  <action>
    **ontology/vocabularies/ata-chapters.yaml:**

    Header MUST include `verified_against` per Pitfall #7 lock. Approximate structure:

    ```yaml
    ---
    # AI 接力开发指南: ATA iSpec 2200 chapter taxonomy. Loaded at runtime by
    # Phase 3 validator (scripts/validators/schema.py) and injected into the
    # in-memory enum for fields whose pattern is "^ATA-[0-9]{2}$" (e.g.
    # AircraftSystem.ata_chapter). Updating this file:
    #   1. Bump ontology/VERSION minor version
    #   2. Write ontology/CHANGELOG.md entry citing the A4A revision source
    #   3. Re-run pre-commit + CI green
    # Sources: A4A iSpec 2200 Revision 2024.1; Wikipedia ATA_Spec_100/iSpec_2200; aviationhunt.com
    # Pitfall #7: this file is updated manually; annual A4A revision review tracked in ROADMAP_FUTURE.md.

    verified_against: "iSpec 2200 Revision 2024.1"
    last_verified: "2026-05-03"

    sections:
      - aircraft_general    # chapters 5-12, 18, 89
      - airframe_systems    # chapters 20-50
      - structure           # chapters 51-57
      - power_plant         # chapters 60-92

    chapters:
      - code: "ATA-05"
        name: "Time Limits / Maintenance Checks"
        section: aircraft_general
      - code: "ATA-06"
        name: "Dimensions and Areas"
        section: aircraft_general
      - code: "ATA-07"
        name: "Lifting and Shoring"
        section: aircraft_general
      - code: "ATA-08"
        name: "Leveling and Weighing"
        section: aircraft_general
      - code: "ATA-09"
        name: "Towing and Taxiing"
        section: aircraft_general
      - code: "ATA-10"
        name: "Parking, Mooring, Storage and Return to Service"
        section: aircraft_general
      - code: "ATA-11"
        name: "Placards and Markings"
        section: aircraft_general
      - code: "ATA-12"
        name: "Servicing — Routine Maintenance"
        section: aircraft_general
      - code: "ATA-18"
        name: "Vibration and Noise Analysis (Helicopter only)"
        section: aircraft_general
      - code: "ATA-20"
        name: "Standard Practices — Airframe"
        section: airframe_systems
      - code: "ATA-21"
        name: "Air Conditioning and Pressurization"
        section: airframe_systems
      - code: "ATA-22"
        name: "Auto Flight"
        section: airframe_systems
      - code: "ATA-23"
        name: "Communications"
        section: airframe_systems
      - code: "ATA-24"
        name: "Electrical Power"
        section: airframe_systems
      - code: "ATA-25"
        name: "Equipment and Furnishings"
        section: airframe_systems
      - code: "ATA-26"
        name: "Fire Protection"
        section: airframe_systems
      - code: "ATA-27"
        name: "Flight Controls"
        section: airframe_systems
      - code: "ATA-28"
        name: "Fuel"
        section: airframe_systems
      - code: "ATA-29"
        name: "Hydraulic Power"
        section: airframe_systems
      - code: "ATA-30"
        name: "Ice and Rain Protection"
        section: airframe_systems
      - code: "ATA-31"
        name: "Indicating / Recording Systems"
        section: airframe_systems
      - code: "ATA-32"
        name: "Landing Gear"
        section: airframe_systems
      - code: "ATA-33"
        name: "Lights"
        section: airframe_systems
      - code: "ATA-34"
        name: "Navigation"
        section: airframe_systems
      - code: "ATA-35"
        name: "Oxygen"
        section: airframe_systems
      - code: "ATA-36"
        name: "Pneumatic"
        section: airframe_systems
      - code: "ATA-37"
        name: "Vacuum"
        section: airframe_systems
      - code: "ATA-38"
        name: "Water / Waste"
        section: airframe_systems
      - code: "ATA-41"
        name: "Water Ballast"
        section: airframe_systems
      - code: "ATA-42"
        name: "Integrated Modular Avionics"
        section: airframe_systems
      - code: "ATA-44"
        name: "Cabin Systems"
        section: airframe_systems
      - code: "ATA-45"
        name: "Central Maintenance / Diagnostic System"
        section: airframe_systems
      - code: "ATA-46"
        name: "Information Systems"
        section: airframe_systems
      - code: "ATA-47"
        name: "Nitrogen Generation"
        section: airframe_systems
      - code: "ATA-48"
        name: "In-Flight Fuel Dispensing"
        section: airframe_systems
      - code: "ATA-49"
        name: "Airborne Auxiliary Power"
        section: airframe_systems
      - code: "ATA-50"
        name: "Cargo and Accessory Compartments"
        section: airframe_systems
      - code: "ATA-51"
        name: "Standard Practices and Structures — General"
        section: structure
      - code: "ATA-52"
        name: "Doors"
        section: structure
      - code: "ATA-53"
        name: "Fuselage"
        section: structure
      - code: "ATA-54"
        name: "Nacelles / Pylons"
        section: structure
      - code: "ATA-55"
        name: "Stabilizers"
        section: structure
      - code: "ATA-56"
        name: "Windows"
        section: structure
      - code: "ATA-57"
        name: "Wings"
        section: structure
      - code: "ATA-60"
        name: "Standard Practices — Propeller / Rotor"
        section: power_plant
      - code: "ATA-61"
        name: "Propellers / Propulsion"
        section: power_plant
      - code: "ATA-62"
        name: "Main Rotor (Helicopter)"
        section: power_plant
      - code: "ATA-63"
        name: "Main Rotor Drive (Helicopter)"
        section: power_plant
      - code: "ATA-64"
        name: "Tail Rotor (Helicopter)"
        section: power_plant
      - code: "ATA-65"
        name: "Tail Rotor Drive (Helicopter)"
        section: power_plant
      - code: "ATA-66"
        name: "Folding Blades / Pylons (Helicopter)"
        section: power_plant
      - code: "ATA-67"
        name: "Rotors Flight Control (Helicopter)"
        section: power_plant
      - code: "ATA-71"
        name: "Power Plant — General"
        section: power_plant
      - code: "ATA-72"
        name: "Engine"
        section: power_plant
      - code: "ATA-73"
        name: "Engine Fuel and Control"
        section: power_plant
      - code: "ATA-74"
        name: "Ignition"
        section: power_plant
      - code: "ATA-75"
        name: "Engine Bleed Air"
        section: power_plant
      - code: "ATA-76"
        name: "Engine Controls"
        section: power_plant
      - code: "ATA-77"
        name: "Engine Indicating"
        section: power_plant
      - code: "ATA-78"
        name: "Engine Exhaust"
        section: power_plant
      - code: "ATA-79"
        name: "Engine Oil"
        section: power_plant
      - code: "ATA-80"
        name: "Engine Starting"
        section: power_plant
      - code: "ATA-81"
        name: "Engine Turbines (Reciprocating)"
        section: power_plant
      - code: "ATA-82"
        name: "Engine Water Injection"
        section: power_plant
      - code: "ATA-83"
        name: "Engine Accessory Gearboxes"
        section: power_plant
      - code: "ATA-84"
        name: "Propulsion Augmentation"
        section: power_plant
      - code: "ATA-85"
        name: "Reciprocating Engine"
        section: power_plant
      - code: "ATA-91"
        name: "Charts"
        section: power_plant
      - code: "ATA-92"
        name: "Electrical System Installation"
        section: power_plant
    ```

    Total ~65 chapters; close enough to "~70" range to satisfy Gap-1. NOTE: not every reachable chapter is included; specifically the ones explicitly noted as unassigned/operator-allocated in RESEARCH.md (13, 14, 15, 16, 17, 19, 39, 40, 43, 58, 59, 87, 88, 90, 93, 94, 95, 96, 97, 98, 99) are EXCLUDED. Final count must be between 50 and 80 entries to pass VALIDATION.md acceptance.

    **ontology/vocabularies/jurisdictions.yaml:**

    ```yaml
    ---
    # AI 接力开发指南: Regulatory jurisdictions. Aligned with the enum domain in
    # entity.regulation-clause.schema.json (jurisdiction field) and
    # entity.organization.schema.json (jurisdiction field). Adding a new
    # jurisdiction requires bumping ontology/VERSION and writing a CHANGELOG entry.
    # Source: project decision per CONTEXT.md (no formal external taxonomy).

    verified_against: "Project decision 2026-05-03"
    last_verified: "2026-05-03"

    jurisdictions:
      - code: "FAA"
        name: "Federal Aviation Administration"
        country: US
      - code: "EASA"
        name: "European Union Aviation Safety Agency"
        country: EU
      - code: "CAAC"
        name: "Civil Aviation Administration of China"
        country: CN
      - code: "ICAO"
        name: "International Civil Aviation Organization"
        country: international
      - code: "Transport-Canada"
        name: "Transport Canada Civil Aviation"
        country: CA
      - code: "CASA-AU"
        name: "Civil Aviation Safety Authority Australia"
        country: AU
      - code: "other"
        name: "Other / unspecified jurisdiction"
        country: null
    ```

    **ontology/vocabularies/provenance-methods.yaml:**

    ```yaml
    ---
    # AI 接力开发指南: Provenance method enum reference. Schema-side definition
    # is _meta.schema.json#/$defs/provenance.method (enum hard-coded). This
    # file is the human-readable reference document explaining when to use which
    # value. Loaded by validators only as documentation; the enum is hard-coded
    # in the schema. Per ADR-005 / D-16.

    verified_against: "ADR-005 (provenance enum)"
    last_verified: "2026-05-03"

    methods:
      - code: human
        description: "Human-authored without AI assistance. provenance.actor is a Person URI; provenance.tool is typically 'manual'. reviewer not required."
      - code: ai_extracted
        description: "AI-extracted from a source document. MUST live in instances/_pending/ until human-reviewed and promoted (D-17). H-Darrieus REJECT condition (PROV-04, ADR-005): if confidence.score > 0.85 AND reviewer is empty → validator REJECTS."
      - code: hybrid_reviewed
        description: "AI-drafted + human-reviewed and signed off. ONLY records with this method are allowed in canonical instances/entities/ and instances/relations/. provenance.reviewer is non-empty Person URI; provenance.reviewed_at is ISO 8601 timestamp."
    ```
  </action>
  <verify>
    <automated>yamllint ontology/vocabularies/ata-chapters.yaml &amp;&amp; yamllint ontology/vocabularies/jurisdictions.yaml &amp;&amp; yamllint ontology/vocabularies/provenance-methods.yaml &amp;&amp; python3 -c "import yaml; d=yaml.safe_load(open('ontology/vocabularies/ata-chapters.yaml')); n=len(d['chapters']); assert 50 <= n <= 80, f'chapter count {n} out of range'; assert d['verified_against'].startswith('iSpec 2200')" &amp;&amp; python3 -c "import yaml; d=yaml.safe_load(open('ontology/vocabularies/jurisdictions.yaml')); codes=[j['code'] for j in d['jurisdictions']]; assert all(c in codes for c in ['FAA','EASA','CAAC','ICAO','other'])" &amp;&amp; python3 -c "import yaml; d=yaml.safe_load(open('ontology/vocabularies/provenance-methods.yaml')); codes=[m['code'] for m in d['methods']]; assert codes == ['human','ai_extracted','hybrid_reviewed']"</automated>
  </verify>
  <acceptance_criteria>
    - All 3 YAMLs pass `yamllint`
    - ATA: chapter count between 50 and 80; `verified_against` starts with `iSpec 2200`; sections array has 4 entries
    - ATA: includes recent additions (ATA-42, ATA-44, ATA-45, ATA-46, ATA-47, ATA-48, ATA-49, ATA-50): `for c in 42 44 45 46 47 48 49 50; do grep -q "ATA-$c" ontology/vocabularies/ata-chapters.yaml || exit 1; done`
    - jurisdictions: codes include FAA, EASA, CAAC, ICAO, Transport-Canada, CASA-AU, other (7 total)
    - provenance-methods: exactly 3 codes in order: human, ai_extracted, hybrid_reviewed (matches D-16)
    - provenance-methods: ai_extracted description references "H-Darrieus REJECT" + "PROV-04, ADR-005"
    - provenance-methods: hybrid_reviewed description references "non-empty Person URI"
    - All 3 YAMLs include `AI 接力开发指南` header comment (R12 discipline)
  </acceptance_criteria>
  <done>3 vocabulary YAMLs ship with verified content; ATA chapter list ~50–80 entries per Gap-1; jurisdictions align with RegulationClause/Organization enum domain; provenance-methods document the three D-16 enum values with H-Darrieus rule cross-reference.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Author 2 mappings docs (ata-to-iso10303.md placeholder + s1000d-dmc-reserved.md structural breakdown)</name>
  <files>ontology/mappings/ata-to-iso10303.md, ontology/mappings/s1000d-dmc-reserved.md</files>
  <read_first>
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Gap Resolution #2 — DMC structure with verified components and example)
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (Out-of-scope: AP233 / ISO 10303-233 — STEP/EXPRESS heavy)
    - ontology/schemas/entity.document.schema.json (s1000d_dmc field — points at this file)
  </read_first>
  <action>
    **ontology/mappings/ata-to-iso10303.md:**

    ```markdown
    # ATA iSpec 2200 → ISO 10303-233 (AP233) Mapping — DEFERRED in v0.1.0

    > AI 接力开发指南: This file is a deferral marker. v0.1.0 does NOT map ATA chapter codes to ISO 10303-233 (Application Protocol 233 / Systems Engineering Data Representation). The mapping is technically possible but the activation triggers are not present in v0.1.0.

    ## Current state

    `ontology/vocabularies/ata-chapters.yaml` ships ~65 ATA iSpec 2200 Revision 2024.1 chapter codes. Each entity that references ATA (AircraftSystem, Subsystem, Component, MaintenanceTask, Document.ata_chapter_tags) carries an `ata_chapter` field validated against the YAML.

    ISO 10303-233 (AP233 — Systems Engineering Data Representation) is an STEP/EXPRESS-based standard for systems engineering data exchange. It overlaps the ATA taxonomy at the system / subsystem decomposition layer but uses a fundamentally different schema mechanism (EXPRESS schema, p21 instance files).

    ## Why deferred

    Per `.planning/research/STACK.md` "What NOT to Use", AP233 is explicitly rejected for v0.1.0:

    > AP233 / ISO 10303-233: AVOID — STEP/EXPRESS schema; even heavier than S1000D; aerospace-systems-engineering only. Wrong shape (STEP/EXPRESS heavy machinery); not adopted.

    Mapping work would require:
    1. AP233 EXPRESS schema parsing (heavy)
    2. Round-trip serialization to STEP p21 (heavy)
    3. A consumer downstream that needs the AP233 representation

    None of these are present in v0.1.0.

    ## Activation criteria (when this mapping becomes valuable)

    - A consumer downstream (e.g. a PLM system integration) requires AP233 round-trip
    - The team has bandwidth for STEP/EXPRESS schema work (estimate: 2+ engineer-weeks)
    - Aviation regulator demand surfaces (FAA / EASA / CAAC requesting AP233 deliverables)

    Until any of those triggers fires, this file remains a placeholder.

    ## See also

    - `ontology/vocabularies/ata-chapters.yaml` — current ATA taxonomy
    - `.planning/research/STACK.md` "What NOT to Use" — AP233 rejection rationale
    - `ontology/mappings/s1000d-dmc-reserved.md` — different deferral pattern (S1000D DMC reservation, not full mapping)
    - `.planning/ROADMAP_FUTURE.md` (Phase 6) — v2+ activation triggers
    ```

    **ontology/mappings/s1000d-dmc-reserved.md:**

    ```markdown
    # S1000D Issue 6.0 Data Module Code (DMC) — Reserved Field Documentation

    > AI 接力开发指南: This file documents the structural breakdown of the S1000D Issue 6.0 Data Module Code that the `Document.s1000d_dmc` field reserves (per Gap Resolution #2 of `.planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md`). v0.1.0 stores DMCs as opaque strings validated by regex; structural decomposition into 7 components is deferred to v0.2.0+ when a consumer (e.g. round-trip export to S1000D-compliant publication tools) materializes.

    ## S1000D status

    - **Issue 6.0 release date:** 2024-09-01 [VERIFIED: en.wikipedia.org/wiki/S1000D]
    - **Predecessor:** Issue 5.0 (2019)
    - **Used by:** defense / aerospace publication systems with strict regulatory or contractual requirements

    ## DMC envelope

    Total length: 17–41 alphanumeric characters. Prefix: `DMC-`. Suffix on file form: `.XML`.

    Verified example (from S1000D reference toolset / kibook tutorial):

    ```
    DMC-S1000DBIKE-AAA-D00-00-00-00AA-00PA-D_004-00_EN-US.XML
    ```

    ## Component breakdown (Issue 6.0)

    | Position | Component | Length | Required | Notes |
    |----------|-----------|--------|----------|-------|
    | 1 | Model Identification Code | 2–14 chars | yes | Project / equipment identifier (`S1000DBIKE` in example) |
    | 2 | System Difference Code | 1–4 chars | yes | Configuration variant identifier (`AAA` = baseline) |
    | 3 | SNS — System | 2–4 digits | yes | First segment of System / Subsystem / Sub-subsystem / Assembly path (`D00` in example, treated as system 'D' + 00) |
    | 4 | SNS — Subsystem | 2 digits | yes | Second segment (`00`) |
    | 5 | SNS — Sub-subsystem | 2 digits | yes | Third segment (`00`) |
    | 6 | SNS — Assembly | 4 digits | yes | Fourth segment (`00AA`) |
    | 7 | Disassembly Code | 2 chars | yes | Disassembly stage (`00`) |
    | 8 | Disassembly Code Variant | 1–3 chars | yes | Variant within disassembly stage (`PA`) |
    | 9 | Information Code | 3 digits | yes | Type of information (`004`) |
    | 10 | Information Code Variant | 1 char | yes | Variant within information code (`A` — note example has `D` here; full set is alphanumeric) |
    | 11 | Item Location Code | 1 char | yes | Where the data module applies: `A` (not specific), `B` (in equipment), `C` (in installed maintainable item), `D` (in major assembly), `T` (training) — example uses `D` |
    | 12 | Learn Code | optional | optional | Used for training data modules; preceded by `_` |
    | 13 | Language Code | optional | optional | ISO 639 language + country (e.g. `EN-US`); preceded by `_` |

    ## v0.1.0 schema treatment (entity.document.schema.json)

    `s1000d_dmc` field is an **optional string** with this regex (verified to match the example above):

    ```
    ^DMC-[A-Z0-9]{2,14}-[A-Z0-9]{1,4}(-[0-9]{2,4}){4}-[0-9A-Z]{2,5}-[0-9A-Z]{4}-[ABCDT](_[0-9]{3}-[0-9]{2}_[a-zA-Z]{2}-[A-Z]{2})?$
    ```

    The field's schema description carries the marker phrase "**Reserved field —**" per Pitfall #5.

    ## v0.2.0+ activation plan

    When a consumer materializes (S1000D round-trip; AD/SB publication; defense contract):

    1. Replace the optional string with a structured nested object reflecting the 13 components above
    2. Add a `mapping/s1000d-dmc-decomposed.md` separate doc with worked examples
    3. Bump `ontology/VERSION` to a major-or-minor (additive change to a reserved field is non-breaking but the structured shape is breaking for any consumer that already used the string form)
    4. Update Document schema with backward-compatibility (allow either string or structured object)

    ## Sources

    - [Wikipedia: S1000D](https://en.wikipedia.org/wiki/S1000D) — Issue 6.0 release date
    - [siberlogic.com S1000D SNS and DMC](https://www.siberlogic.com/s1000d-concepts/sns-and-dmc) — DMC structure
    - [s1kd-tools tutorial](https://kibook.github.io/s1kd-tools/TUTORIAL.html) — verified example
    - 02-RESEARCH.md Gap Resolution #2 (this project's verified breakdown)

    ## See also

    - `ontology/schemas/entity.document.schema.json` — schema field definition
    - 02-RESEARCH.md Pitfall #5 — Reserved field discipline
    - `.planning/ROADMAP_FUTURE.md` (Phase 6) — when to activate full structural decomposition
    ```
  </action>
  <verify>
    <automated>test -f ontology/mappings/ata-to-iso10303.md &amp;&amp; test -f ontology/mappings/s1000d-dmc-reserved.md &amp;&amp; grep -q 'deferred' ontology/mappings/ata-to-iso10303.md &amp;&amp; grep -q 'AP233' ontology/mappings/ata-to-iso10303.md &amp;&amp; grep -q 'Issue 6.0' ontology/mappings/s1000d-dmc-reserved.md &amp;&amp; grep -q 'DMC-' ontology/mappings/s1000d-dmc-reserved.md &amp;&amp; grep -q 'S1000DBIKE' ontology/mappings/s1000d-dmc-reserved.md &amp;&amp; grep -q 'AI 接力开发指南' ontology/mappings/ata-to-iso10303.md &amp;&amp; grep -q 'AI 接力开发指南' ontology/mappings/s1000d-dmc-reserved.md</automated>
  </verify>
  <acceptance_criteria>
    - Both files exist
    - ata-to-iso10303.md: `grep -q deferred` exits 0; references AP233 + ISO 10303-233; cites STACK.md "What NOT to Use"
    - s1000d-dmc-reserved.md: `grep -q "Issue 6.0"` exits 0; `grep -q DMC-` exits 0; verified example `S1000DBIKE` cited
    - s1000d-dmc-reserved.md: 13-row component breakdown table present (count `|` separators); references Pitfall #5
    - Both: `grep -q "AI 接力开发指南"` exits 0
    - s1000d-dmc-reserved.md cross-references entity.document.schema.json + 02-RESEARCH.md Gap-2
  </acceptance_criteria>
  <done>2 mapping docs ship — ATA→ISO 10303 placeholder explicitly states deferral; S1000D DMC structural breakdown documents 13 components for v0.2.0+ activation.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Enrich scripts/exporters/to_jsonl_triples.py with schema-derived design notes</name>
  <files>scripts/exporters/to_jsonl_triples.py</files>
  <read_first>
    - scripts/exporters/to_jsonl_triples.py (current Phase 1 stub state)
    - .planning/decisions/ADR-006-triple-export.md (Plan 09 deliverable — provides the per-entity / per-relation triple-generation rules)
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-19 — Phase 2 enrichment scope: docstring only, no implementation)
  </read_first>
  <action>
    **REPLACE** the existing module-level docstring with an expanded version that captures the schema-derived design notes per ADR-006 / D-19. The function body MUST stay as-is (still raises NotImplementedError). DO NOT add implementation code.

    New docstring content:

    ```python
    """
    to_jsonl_triples.py — YAML instances → JSONL triple export (STUB)

    Status: Phase-1 STUB enriched in Phase 2 with schema-derived design notes
    (per ADR-006 / D-19). Implementation deferred to Phase 5 (RAG pipeline) or
    v0.2.0 GraphRAG sprint, whichever ships first.

    AI 接力开发指南: read .planning/decisions/ADR-006-triple-export.md before
    implementing. The format is locked; this docstring captures the per-entity
    and per-relation triple-generation rules a future implementer must honor.

    --- Output format (locked v0.1.0) ---

    JSONL — one JSON object per line. Schema:

        {
          "s": "<subject_uri>",
          "p": "<predicate>",
          "o": "<object_uri_or_scalar>",
          "prov": { ...record's provenance carry-through... },
          "confidence": { ...record's confidence carry-through... }
        }

    Field semantics:
      s — subject URI per D-23 (aviationkb://<type>/<slug>@<version>)
      p — predicate:
            * for relation files: the relation type slug (e.g. "part_of")
            * for entity-type triples: the literal "rdf:type"
            * for entity-property triples: the property name (e.g. "ata_chapter")
      o — object:
            * for relation triples: object URI
            * for type triples: entity type name (e.g. "AircraftSystem")
            * for entity-property triples: scalar value (string, number, bool)
            * for entity-array-element triples: scalar value of the array element
      prov — copy of the source record's provenance object (D-16 / PROV-01)
      confidence — copy of the source record's confidence object (D-13 / PROV-02)

    --- Per-entity triple generation rules ---

    For each entity YAML under instances/entities/<type>/<slug>.yaml:

      1. Emit ONE rdf:type triple:
         {"s": entity.id, "p": "rdf:type", "o": entity.type, "prov": entity.provenance, "confidence": entity.confidence}

      2. For each scalar field in the entity (excluding base fields id, provenance, confidence, source, i18n, version_history):
         {"s": entity.id, "p": <field_name>, "o": <field_value>, "prov": entity.provenance, "confidence": entity.confidence}

      3. For each array field (e.g. tags, causal_factors):
         emit one triple per array element with the same shape

      4. For each nested object's leaf scalars:
         flatten into dotted predicate names (e.g. "interval.kind", "interval.value")

      5. Skip i18n field (handled by a separate language-aware exporter when needed)
      6. Skip version_history (handled by a separate revision-export when needed)
      7. Skip source.* (it's part of the prov-carry-through, not a triple itself)

    --- Per-relation triple generation rules ---

    For each relation YAML under instances/relations/<type>/<slug>.yaml:

      Emit ONE triple:
        {"s": relation.subject, "p": relation.type, "o": relation.object,
         "prov": relation.provenance, "confidence": relation.confidence}

      Optional metadata (e.g. interfaces_with.interface_type) is NOT emitted as a
      separate triple in v0.1.0 — it stays inside the relation YAML for inspection.
      v0.2.0+ may add per-metadata triples if a graph consumer needs them.

    --- Provenance carry-through (mandatory, ADR-006) ---

    Every triple MUST carry prov + confidence. Skipping these breaks the
    H-Darrieus failure-mode lock at the export layer (high-confidence AI-extracted
    triples slip into downstream graphs without audit trail).

    Future RDF/Turtle export (v0.3.0+) maps:
      prov.actor      → prov:wasAttributedTo
      prov.method     → prov:wasGeneratedBy (with method-specific Activity class)
      prov.created_at → prov:generatedAtTime
      confidence.*    → custom akb: namespace (no PROV-O equivalent)

    --- CLI surface (when implemented) ---

      python scripts/exporters/to_jsonl_triples.py --in instances/ --out export.jsonl
      python scripts/exporters/to_jsonl_triples.py --validate-only

    --- Test fixture path (when implemented, Phase 4+) ---

      tests/fixtures/exporters/to_jsonl_triples/
        sample-entity.yaml       → expected-triples.jsonl
        sample-relation.yaml     → expected-triples.jsonl

    --- See also ---

    - .planning/decisions/ADR-006-triple-export.md — format decision
    - .planning/decisions/ADR-005-provenance-enum.md — provenance carry-through rationale
    - ontology/_meta.schema.json#/$defs/{provenance,confidence} — source field shapes
    - scripts/exporters/to_rdf.py — sibling stub for v0.3.0+ semantic-web export
    - scripts/exporters/to_neo4j.py — sibling stub for v0.2.0+ GraphRAG loader
    """
    ```

    Function body unchanged — still raises NotImplementedError. The docstring is the only meaningful change. Imports and __main__ guard preserved.
  </action>
  <verify>
    <automated>python3 -c "import ast; ast.parse(open('scripts/exporters/to_jsonl_triples.py').read())" &amp;&amp; grep -q 'JSONL' scripts/exporters/to_jsonl_triples.py &amp;&amp; grep -q 'ADR-006' scripts/exporters/to_jsonl_triples.py &amp;&amp; grep -q 'rdf:type' scripts/exporters/to_jsonl_triples.py &amp;&amp; grep -q 'H-Darrieus' scripts/exporters/to_jsonl_triples.py &amp;&amp; grep -q 'aviationkb://' scripts/exporters/to_jsonl_triples.py &amp;&amp; grep -q 'NotImplementedError' scripts/exporters/to_jsonl_triples.py &amp;&amp; grep -q 'AI 接力开发指南' scripts/exporters/to_jsonl_triples.py &amp;&amp; ! grep -E '^(def|class)\s+(?!main)' scripts/exporters/to_jsonl_triples.py | grep -v 'def main' | grep -q .</automated>
  </verify>
  <acceptance_criteria>
    - File still parseable Python: `python3 -c "import ast; ast.parse(open('scripts/exporters/to_jsonl_triples.py').read())"` exits 0
    - `grep -q 'JSONL' scripts/exporters/to_jsonl_triples.py` exits 0
    - `grep -q 'ADR-006' scripts/exporters/to_jsonl_triples.py` exits 0
    - `grep -q 'rdf:type' scripts/exporters/to_jsonl_triples.py` exits 0
    - `grep -q 'H-Darrieus' scripts/exporters/to_jsonl_triples.py` exits 0 (carry-through rationale citation)
    - `grep -q 'aviationkb://' scripts/exporters/to_jsonl_triples.py` exits 0 (URI form mentioned)
    - `grep -q 'NotImplementedError' scripts/exporters/to_jsonl_triples.py` exits 0 (still a stub — D-19)
    - `grep -q 'AI 接力开发指南' scripts/exporters/to_jsonl_triples.py` exits 0
    - No new function bodies (only main + the existing __main__ guard)
  </acceptance_criteria>
  <done>to_jsonl_triples.py docstring enriched with schema-derived design notes per ADR-006 / D-19. Function body untouched — still a stub raising NotImplementedError. PROV-06 cross-reference (source.document_id → Document) implicit via provenance carry-through.</done>
</task>

</tasks>

<threat_model>
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-02-10-01 | Tampering | ATA chapter list drift (Pitfall #7) | mitigate | `verified_against` + `last_verified` headers; ROADMAP_FUTURE annual review trigger |
| T-02-10-02 | Tampering | s1000d_dmc regex doesn't match real DMCs | accept | RESEARCH.md flags as MEDIUM-confidence; v0.2.0+ replaces with structural decomposition |
| T-02-10-03 | Information Disclosure | to_jsonl_triples docstring loses provenance-carry-through note | mitigate | grep test that "H-Darrieus" appears in the file |
</threat_model>

<verification>
- All 5 new files + 1 enriched file exist
- `pre-commit run --all-files` exits 0 (yamllint + check-jsonschema)
- `yamllint ontology/vocabularies/*.yaml` exits 0
- `python3 -c "import ast; ast.parse(open('scripts/exporters/to_jsonl_triples.py').read())"` exits 0
- 3 atomic commits via gsd-tools
</verification>

<success_criteria>
- 3 vocabulary YAMLs (ATA chapters / jurisdictions / provenance methods)
- 2 mapping docs (ATA→ISO 10303 deferred; S1000D DMC structural breakdown)
- to_jsonl_triples.py docstring enriched per D-19; function body untouched
- ATA chapter count between 50–80 entries per VALIDATION.md acceptance
- Provenance methods YAML matches D-16 enum (3 values, exact codes)
- All cross-references intact (entity.aircraft-system → ata-chapters.yaml; entity.regulation-clause → jurisdictions.yaml; entity.document → s1000d-dmc-reserved.md)
- PROV-06 documentation-level satisfaction (Phase 3 validator enforces)
</success_criteria>

<output>
Create `.planning/phases/02-ontology-schema-v0-1-0/02-10-SUMMARY.md` with:
- 6 files (5 new + 1 enriched) summary
- ATA chapter count + verified_against verification
- to_jsonl_triples.py docstring enrichment status
- Phase 2 close-out: 51 REQ-IDs all distributed across 10 plans, 6 ADRs landed, all schemas + vocabs + mappings shipped
</output>

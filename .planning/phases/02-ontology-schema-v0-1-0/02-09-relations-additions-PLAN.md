---
phase: 02-ontology-schema-v0-1-0
plan: 09
type: execute
wave: 5
depends_on: [03, 08]
files_modified:
  - ontology/schemas/relation.interfaces-with.schema.json
  - ontology/schemas/relation.complies-with.schema.json
  - ontology/schemas/relation.applicable-during-phase.schema.json
  - .planning/decisions/ADR-006-triple-export.md
autonomous: true
requirements:
  - ONT-R-15
  - ONT-R-16
  - ONT-R-17
  - ONT-R-18
  - ONT-R-19
must_haves:
  truths:
    - "All 3 ADR-003 added relation schemas self-validate as Draft 2020-12"
    - "Each composes relation.base.schema.json"
    - "interfaces_with description contains the verbatim USE/DON'T USE table from ADR-003 (boundary vs requires)"
    - "complies_with description contains the verbatim USE/DON'T USE table from ADR-003 (boundary vs constrained_by)"
    - "applicable_during_phase has flight phase enum (taxi/takeoff/cruise/approach/landing/missed/emergency)"
    - "ONT-R-17 (has_revision) satisfied by ADR-003 internalization decision — no schema file"
    - "ONT-R-19 (generated_by) satisfied by ADR-003 internalization decision — no schema file"
    - "ADR-006 documents the JSONL triple export choice and the Phase 2 stub-only enrichment scope"
  artifacts:
    - path: "ontology/schemas/relation.interfaces-with.schema.json"
      provides: "interfaces_with relation (ONT-R-15, D-05) — peer-tier system↔system"
    - path: "ontology/schemas/relation.complies-with.schema.json"
      provides: "complies_with relation (ONT-R-16, D-06) — explicit normative compliance"
    - path: "ontology/schemas/relation.applicable-during-phase.schema.json"
      provides: "applicable_during_phase relation (ONT-R-18, D-08) — flight phase scope"
    - path: ".planning/decisions/ADR-006-triple-export.md"
      provides: "JSONL triple format decision (D-18) + Phase 2 stub-only enrichment scope (D-19)"
  key_links:
    - from: "all 3 added relation schemas"
      to: "ontology/schemas/relation.base.schema.json"
      via: "allOf + $ref"
    - from: "ADR-006-triple-export.md"
      to: "scripts/exporters/to_jsonl_triples.py (Plan 10)"
      via: "design rationale → stub enrichment"
---

<objective>
Author the 3 ADR-003 accepted relation schemas (interfaces_with, complies_with, applicable_during_phase) AND ADR-006 (triple export format). ONT-R-17 and ONT-R-19 are satisfied by ADR-003's internalization decision (no schema files ship for has_revision or generated_by).

Output: 3 schema files + 1 ADR.
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
@.planning/phases/02-ontology-schema-v0-1-0/02-08-SUMMARY.md
@ontology/_meta.schema.json
@ontology/schemas/relation.base.schema.json

<interfaces>
<!-- Use Code Example #3 (relation.interfaces-with.schema.json) from 02-RESEARCH.md as the verbatim template for interfaces_with — the example IS the specification. -->
<!-- ADR-003 Plan 03 deliverable holds the verbatim USE/DON'T USE worked-example tables for interfaces_with and complies_with. -->
<!-- Flight phase enum (D-08): taxi, takeoff, cruise, approach, landing, missed_approach, emergency. -->
<!-- ADR-006 covers D-18 (JSONL format) + D-19 (stub-only enrichment in Phase 2). -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author 3 added relation schemas (interfaces_with, complies_with, applicable_during_phase)</name>
  <files>ontology/schemas/relation.interfaces-with.schema.json, ontology/schemas/relation.complies-with.schema.json, ontology/schemas/relation.applicable-during-phase.schema.json</files>
  <read_first>
    - ontology/schemas/relation.base.schema.json
    - .planning/decisions/ADR-003-relation-additions.md (verbatim worked-example tables)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Code Example #3 — interfaces_with verbatim template)
    - .planning/REQUIREMENTS.md (ONT-R-15, ONT-R-16, ONT-R-18)
  </read_first>
  <action>
    **relation.interfaces-with.schema.json (ONT-R-15, D-05):**
    USE Code Example #3 from 02-RESEARCH.md verbatim. Confirm:
    - title: "interfaces_with relation (ONT-R-15, D-05)"
    - description starts with "Peer-tier system↔system interface (data, power, mechanical, thermal). USE FOR: AvionicsBay interfaces_with ECS via ARINC 429; HydraulicSystem interfaces_with FlightControlSystem via servo actuators. DO NOT USE FOR: parent-child (use part_of); cross-tier dependency (use requires); regulatory compliance (use complies_with). Boundary with 'requires' per ADR-003 / D-10..."
    - properties.type: const "interfaces_with"
    - interface_type: enum [data, power, mechanical, thermal, fluid, control, other]
    - interface_protocol: optional string (e.g. ARINC 429 / AFDX / MIL-STD-1553)
    - required (additional): [interface_type]

    **relation.complies-with.schema.json (ONT-R-16, D-06):**
    - title: "complies_with relation (ONT-R-16, D-06)"
    - description: "Explicit normative compliance with a regulation, standard, or certification clause. Audit-grade. USE FOR: Component(structure) complies_with RegulationClause(FAR §25.305); AircraftSystem(avionics) complies_with Standard(DO-178C_LevelB); Procedure complies_with RegulationClause(EASA AMC 25.1309). DO NOT USE FOR: budget / non-normative constraints — those are constrained_by (ONT-R-04). DO NOT USE FOR: 'soft compliance' without audit trail — also constrained_by. DO NOT USE FOR: citation only — use cites (ONT-R-08). Boundary per ADR-003 / D-11."
    - properties.type: const "complies_with"
    - compliance_evidence: optional $ref ../_meta.schema.json#/$defs/uri (URI to TestReport / SimulationCase / Procedure that demonstrates compliance)
    - compliance_status: optional enum [demonstrated, claimed, in_progress, exempted]

    **relation.applicable-during-phase.schema.json (ONT-R-18, D-08):**
    - title: "applicable_during_phase relation (ONT-R-18, D-08)"
    - description: "Flight phase scope. USE FOR: Procedure applicable_during_phase emergency; Requirement applicable_during_phase takeoff; Procedure applicable_during_phase landing. Phase enum is fixed (per CONTEXT.md Open Question #3 — inline enum, not a separate vocabulary YAML). NOT for aircraft-model scope (that's applicable_to, ONT-R-03)."
    - properties.type: const "applicable_during_phase"
    - flight_phase: enum [taxi, takeoff, climb, cruise, approach, landing, missed_approach, emergency, ground_operations] — required (description: "Per D-08 inline enum.")
    - required (additional): [flight_phase]

    Note: The `subject` of applicable_during_phase is an entity URI (Procedure / Requirement / etc); the `object` is conceptually the flight phase. v0.1.0 uses the `object` field for backward URI compatibility but the FLIGHT PHASE itself is captured by the `flight_phase` enum. Description must clarify this.
  </action>
  <verify>
    <automated>for s in interfaces-with complies-with applicable-during-phase; do f="ontology/schemas/relation.$s.schema.json"; check-jsonschema --check-metaschema "$f" || exit 1; ! grep -q '"additionalProperties"' "$f" || exit 1; grep -q '"unevaluatedProperties": false' "$f" || exit 1; done; jq -e '.properties.type.const == "interfaces_with"' ontology/schemas/relation.interfaces-with.schema.json &amp;&amp; jq -e '.properties.type.const == "complies_with"' ontology/schemas/relation.complies-with.schema.json &amp;&amp; jq -e '.properties.type.const == "applicable_during_phase"' ontology/schemas/relation.applicable-during-phase.schema.json &amp;&amp; jq -e '.properties.interface_type.enum | contains(["data","power","mechanical","thermal"])' ontology/schemas/relation.interfaces-with.schema.json &amp;&amp; jq -e '.properties.flight_phase.enum | contains(["takeoff","cruise","landing","emergency"])' ontology/schemas/relation.applicable-during-phase.schema.json &amp;&amp; grep -q 'ARINC 429' ontology/schemas/relation.interfaces-with.schema.json &amp;&amp; grep -q 'FAR §25\.305\|FAR §25\.' ontology/schemas/relation.complies-with.schema.json &amp;&amp; grep -q 'DO NOT USE' ontology/schemas/relation.complies-with.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - All 3 files self-validate; Pitfall #1 + #9 locks
    - interfaces_with: interface_type enum has at least [data, power, mechanical, thermal, fluid, control, other]; description names ARINC 429 + ECS by example
    - complies_with: description contains "DO NOT USE" + references "constrained_by"; description names FAR §25 by example
    - applicable_during_phase: flight_phase enum has at least [taxi, takeoff, climb, cruise, approach, landing, missed_approach, emergency, ground_operations]; flight_phase required
    - All 3 type.const values match
    - Composition via allOf + $ref relation.base.schema.json
  </acceptance_criteria>
  <done>3 added relations validate, embed worked-example boundary discipline per ADR-003, and use the inline flight_phase enum per CONTEXT.md Open Question #3.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Author ADR-006 triple-export decision record</name>
  <files>.planning/decisions/ADR-006-triple-export.md</files>
  <read_first>
    - .planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-18, D-19)
    - .planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Don't Hand-Roll table — JSON-LD/RDF deferred)
    - scripts/exporters/to_jsonl_triples.py (the existing Phase 1 stub being enriched in Plan 10)
  </read_first>
  <action>
    Create `.planning/decisions/ADR-006-triple-export.md`:

    ```markdown
    # ADR-006 — Triple Export Format (JSONL `{s, p, o, prov, confidence}`)

    Status: ACCEPTED
    Date: 2026-05-03
    Deciders: user (CONTEXT.md interactive discuss, 2026-05-03)
    Implements: D-18, D-19

    > AI 接力开发指南: This ADR locks the triple-export format for v0.1.0 and the scope of work allowed in Phase 2 against the existing `scripts/exporters/to_jsonl_triples.py` stub. The export is Phase 5+ implementation; Phase 2 only enriches the stub with schema-derived design notes. RDF/Turtle / JSON-LD are explicitly deferred to v0.3.0+.

    ## Context

    The knowledge base needs a downstream-friendly triple format for:
    - Ad-hoc analysis (jq filters, wc -l counts, grep)
    - Future GraphRAG sprint (v0.2.0+ Neo4j/Nebula loader; v0.3.0+ RDF round-trip)
    - Provenance + confidence carry-through (any export that drops these fails the Core Value)

    Three candidates were considered:

    | Format | Pros | Cons |
    |--------|------|------|
    | **JSONL** `{s, p, o, prov, confidence}` | jq-friendly; one triple per line; `wc -l` triple count; trivially convertible to JSON-LD/Turtle later | Not standard semantic-web format |
    | **RDF/Turtle** | Standard, PROV-O-aligned | Heavyweight in Phase 2 (no consumer needs it yet); test fixture generation is non-trivial |
    | **N-Triples** | Simple, standard | No native provenance/confidence carry-through; would need PROV-O reification, which is verbose |

    ## Decision

    ### v0.1.0 format: JSONL with provenance + confidence (D-18)

    One JSON object per line. Schema:

    ```jsonl
    {"s": "aviationkb://component/brake-disc-737-max-8@1", "p": "requires", "o": "aviationkb://maintenance-task/brake-inspection-500h@1", "prov": {"method": "human", "actor": "aviationkb://person/jane-engineer@1", "actor_role": "maintenance_engineer", "created_at": "2026-04-01T10:00:00Z"}, "confidence": {"score": 0.95, "rationale": "Multi-source agreement: cited in 737 MAX 8 maintenance manual ATA-32-21-00 and FAA AD 2026-04-15."}}
    {"s": "aviationkb://component/brake-disc-737-max-8@1", "p": "rdf:type", "o": "Component", "prov": {...}, "confidence": {...}}
    ```

    Field semantics:
    - `s` — subject URI (entity URI: `aviationkb://<type>/<slug>@<version>`)
    - `p` — predicate (relation type slug for relation triples; `rdf:type` for entity-type triples; field name for entity-property triples like `ata_chapter`)
    - `o` — object URI (for relation triples) OR scalar value (for entity-property triples)
    - `prov` — relation/entity provenance carried forward (PROV-01 / D-16)
    - `confidence` — relation/entity confidence carried forward (PROV-02 / D-13)

    Per-entity triple generation rule: emit `{rdf:type}` triple + one triple per scalar field + one triple per array element + one triple per nested object's leaf scalars. Per-relation triple: one triple per relation file using the file's subject/object/type/provenance/confidence.

    ### Phase 2 scope: stub enrichment only (D-19)

    Phase 2 ONLY enriches `scripts/exporters/to_jsonl_triples.py` with schema-derived design notes (which entity fields → triple components). NO implementation. NO test fixtures.

    Implementation lands in Phase 5 (RAG pipeline) or v0.2.0 GraphRAG sprint, whichever ships first.

    ### Why JSONL over RDF/Turtle for v0.1.0

    1. No v0.1.0 consumer needs the full semantic-web stack
    2. JSONL is `jq` / `wc -l` / `grep` friendly — debugging on real data is fast
    3. Conversion path JSONL → JSON-LD via `@context` injection is cheap (1-line per triple)
    4. Conversion path JSONL → RDF/Turtle via PROV-O alignment is cheap when v0.3.0+ needs it
    5. The opposite (RDF → JSONL) is also possible but requires reification handling for PROV-O
    6. RDF in v0.1.0 is YAGNI

    ## Rationale (provenance carry-through)

    Every triple carries `prov` and `confidence` blocks because:
    - Without them, the H-Darrieus failure mode (high-confidence AI extraction without reviewer) silently lands in graph-layer queries
    - Phase 4 demo data (DEMO-04) demonstrates the carry-through pattern end-to-end
    - When v0.3.0+ ships RDF/Turtle export, PROV-O alignment maps `prov.actor` → `prov:wasAttributedTo`, `prov.method` → `prov:wasGeneratedBy` (with method-specific Activity classes)

    ## Consequences

    - Plan 10 enriches `scripts/exporters/to_jsonl_triples.py` docstring with the per-entity / per-relation triple-generation rules above
    - `scripts/exporters/to_rdf.py` and `scripts/exporters/to_neo4j.py` stubs remain untouched in Phase 2 (deferred to v0.3.0+)
    - Phase 5 RAG pipeline design (RAG-08) may use JSONL as the intermediate format between YAML instances and RAGFlow ingestion
    - Phase 4 demo data must include a sample `.jsonl` file showing the format (DEMO-04 worked example)

    ## References

    - REQUIREMENTS.md (no direct REQ-ID; satisfies the v1 architecture goal of "future-proof export")
    - 02-CONTEXT.md D-18, D-19
    - 02-RESEARCH.md Don't Hand-Roll (JSON-LD/RDF deferred to v0.3.0+)
    - PROJECT.md Out of Scope ("Graph DB backend (Neo4j/Nebula) in v1")
    - Phase 1 stub: `scripts/exporters/to_jsonl_triples.py`
    - Future deliverable: `scripts/exporters/to_rdf.py` (v0.3.0+ when GraphRAG sprint starts)
    - W3C PROV-O recommendation (mapping target for v0.3.0+ RDF export)
    ```
  </action>
  <verify>
    <automated>test -f .planning/decisions/ADR-006-triple-export.md &amp;&amp; grep -q 'JSONL' .planning/decisions/ADR-006-triple-export.md &amp;&amp; grep -q 'D-18' .planning/decisions/ADR-006-triple-export.md &amp;&amp; grep -q 'D-19' .planning/decisions/ADR-006-triple-export.md &amp;&amp; grep -q 'PROV-O' .planning/decisions/ADR-006-triple-export.md &amp;&amp; grep -q 'AI 接力开发指南' .planning/decisions/ADR-006-triple-export.md &amp;&amp; grep -q 'YAGNI\|deferred to v0.3' .planning/decisions/ADR-006-triple-export.md</automated>
  </verify>
  <acceptance_criteria>
    - File exists at `.planning/decisions/ADR-006-triple-export.md`
    - All ADR sections present (Status / Date / Deciders / Implements / Context / Decision / Rationale / Consequences / References)
    - `grep -q 'JSONL' .planning/decisions/ADR-006-triple-export.md` exits 0
    - `grep -q 'PROV-O' .planning/decisions/ADR-006-triple-export.md` exits 0 (alignment path mentioned)
    - `grep -q 'aviationkb://' .planning/decisions/ADR-006-triple-export.md` exits 0 (concrete URI example)
    - Both implemented IDs cited: `for d in D-18 D-19; do grep -q "$d" .planning/decisions/ADR-006-triple-export.md || exit 1; done`
    - `grep -q 'AI 接力开发指南' .planning/decisions/ADR-006-triple-export.md` exits 0
    - `grep -q 'scripts/exporters/to_jsonl_triples.py' .planning/decisions/ADR-006-triple-export.md` exits 0 (cross-reference to stub being enriched)
  </acceptance_criteria>
  <done>ADR-006 documents the JSONL-with-provenance triple format choice and locks Phase 2 work to docstring enrichment only.</done>
</task>

</tasks>

<threat_model>
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-02-09-01 | Tampering | Pitfall #1 in any of 3 schemas | mitigate | Per-file `! grep -q additionalProperties` |
| T-02-09-02 | Repudiation | complies_with description weak → demo data confuses with constrained_by | mitigate | Description carries verbatim ADR-003 USE/DON'T-USE table |
| T-02-09-03 | Information Disclosure | ADR-006 omits provenance carry-through → future export drops audit trail | mitigate | ADR-006 §"Provenance carry-through" and per-triple `prov`+`confidence` mandate |
</threat_model>

<verification>
- All 3 schemas + 1 ADR exist; each schema's `--check-metaschema` exits 0
- `pre-commit run --all-files` exits 0
- 2 atomic commits via gsd-tools
- ONT-R-17 + ONT-R-19 explicitly satisfied by ADR-003 (no schema files)
</verification>

<success_criteria>
- 3 added relation schemas: interfaces_with, complies_with, applicable_during_phase
- ADR-006 documents JSONL choice + Phase 2 stub-only scope
- Boundary discipline locked (interfaces_with vs requires; complies_with vs constrained_by)
- ONT-R-17 (has_revision) + ONT-R-19 (generated_by) satisfied by ADR-003 internalization
- Pitfall #1 + #9 locks
</success_criteria>

<output>
Create `.planning/phases/02-ontology-schema-v0-1-0/02-09-SUMMARY.md` with:
- 3 schemas + ADR-006 listed
- Boundary worked-example confirmation
- Phase 2 to_jsonl_triples.py enrichment scope (Plan 10 deliverable)
- Pitfall #1 + #9 confirmation
</output>

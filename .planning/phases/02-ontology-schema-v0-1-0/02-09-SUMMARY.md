---
phase: 02-ontology-schema-v0-1-0
plan: 09
subsystem: ontology-schemas
tags: [ontology, json-schema, draft-2020-12, relations, additions, boundary-discipline, h-darrieus, adr-003, adr-006, triple-export]
one_liner: "3 ADR-003 added relation schemas (interfaces_with / complies_with / applicable_during_phase) shipped + ADR-006 (JSONL `{s,p,o,prov,confidence}` triple export) + ADR-003 finalized; net relation count v0.1.0 = 16."
dependency_graph:
  requires:
    - "ontology/schemas/relation.base.schema.json (Plan 02-03) — composition root carrying subject/object/valid_from/valid_until + baseFields"
    - "ontology/_meta.schema.json (Plan 02-01) — provides $defs/uri, $defs/schemaVersionString, baseFields"
    - ".planning/decisions/ADR-003-relation-additions.md (Plan 02-03 initial draft) — canonical USE/DON'T-USE boundary tables for interfaces_with and complies_with"
    - ".planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md (D-05/06/08 ACCEPT, D-07/09 internalize, D-18/19 triple format)"
    - ".planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md (Code Example #3 — interfaces_with verbatim template)"
    - "ontology/schemas/relation.requires.schema.json + relation.constrained-by.schema.json (Plan 02-08) — sibling worked-example anchors that close the boundary loop with this plan's interfaces_with + complies_with"
  provides:
    - "ontology/schemas/relation.interfaces-with.schema.json (ONT-R-15 — peer-tier system↔system, interface_type required enum)"
    - "ontology/schemas/relation.complies-with.schema.json (ONT-R-16 — explicit normative compliance with optional compliance_evidence URI + compliance_status enum)"
    - "ontology/schemas/relation.applicable-during-phase.schema.json (ONT-R-18 — inline flight_phase enum per D-08)"
    - ".planning/decisions/ADR-006-triple-export.md (D-18 + D-19 — JSONL `{s,p,o,prov,confidence}` choice + Phase 2 stub docstring-only enrichment scope)"
    - "Closure: ADR-003 finalized post-baseline-review (no schema files for has_revision / generated_by — internalized as fields per D-07/D-09)"
  affects:
    - "Plan 02-10 (vocabularies + mappings + to_jsonl_triples.py docstring enrichment) — ADR-006 §Decision provides the verbatim per-entity / per-relation triple-generation rules to embed"
    - "Phase 3 validator — must enforce interfaces_with peer-tier check (subject and object same architectural tier); must cross-check compliance_evidence URI resolves to TestReport / SimulationCase / Procedure when compliance_status == 'demonstrated'; must enforce applicable_during_phase.flight_phase against the inline enum"
    - "Phase 4 demo data (DEMO-02 + DEMO-04) — must exercise interfaces_with and complies_with at least once each; SHOULD exercise applicable_during_phase; sample .jsonl file required to demonstrate ADR-006 triple format end-to-end including hybrid_reviewed provenance carry-through"
    - "Future v0.3.0+ GraphRAG sprint — ADR-006 §Rationale provides the PROV-O alignment path (prov.actor → prov:wasAttributedTo, prov.method → prov:wasGeneratedBy)"
tech_stack:
  added: []
  patterns:
    - "JSON Schema Draft 2020-12 composition via allOf + $ref to relation.base.schema.json (relative reference, identical to Plan 02-08 baseline relations)"
    - "unevaluatedProperties: false on every leaf relation schema (Pitfall #1 lock; allOf-aware strictness)"
    - "Filename uses kebab-case slug (relation.applicable-during-phase.schema.json); type.const uses snake_case (applicable_during_phase)"
    - "Verbatim ADR-003 USE/DON'T-USE boundary tables embedded in description fields (Pitfall #4 lock)"
    - "ADR-003 finalization via append-only Edit (NOT rewrite) — protects the on-main initial draft against the merge-conflict pattern that bit Plan 02-07's ADR-002 finalization"
    - "ADR-006 documents per-entity / per-relation triple-generation rules so Plan 02-10 has a contract for to_jsonl_triples.py docstring enrichment without writing implementation"
key_files:
  created:
    - "ontology/schemas/relation.interfaces-with.schema.json"
    - "ontology/schemas/relation.complies-with.schema.json"
    - "ontology/schemas/relation.applicable-during-phase.schema.json"
    - ".planning/decisions/ADR-006-triple-export.md"
  modified:
    - ".planning/decisions/ADR-003-relation-additions.md (append-only post-baseline-review status block)"
decisions:
  - "Adopted Code Example #3 from 02-RESEARCH.md verbatim as the interfaces_with template — title, description, allOf+$ref to relation.base, type.const='interfaces_with', interface_type required enum [data,power,mechanical,thermal,fluid,control,other], optional interface_protocol — confirmed it composes cleanly with the existing relation.base.schema.json (which already requires subject/object/valid_from at the base layer, so leaf schemas don't redeclare them)"
  - "complies_with carries optional compliance_evidence (URI to TestReport/SimulationCase/Procedure) + compliance_status enum [demonstrated, claimed, in_progress, exempted]. compliance_evidence is intentionally OPTIONAL at the schema layer — Phase 3 validator enforces 'compliance_status==demonstrated implies compliance_evidence present' as a cross-field rule (schema-level required would over-constrain claimed/in_progress/exempted records)"
  - "applicable_during_phase keeps the inline flight_phase enum per D-08 (CONTEXT.md Open Question #3 — no separate ontology/vocabularies/flight-phases.yaml). Description explicitly clarifies the v0.1.0 trade-off: the base 'object' URI field (inherited from relation.base) is repurposed as a placeholder phase-entity URI of the form aviationkb://flight-phase/<phase>@1, while the flight_phase enum is the semantic source of truth — keeps the relation valid against relation.base.required without forcing flight phases to be first-class entities in v0.1.0"
  - "ADR-006 chose JSONL over RDF/Turtle for v0.1.0: jq/wc-l/grep friendly; no v0.1.0 consumer needs SPARQL; conversion to JSON-LD via @context injection is one-liner-per-triple; conversion to RDF with PROV-O alignment deferred to v0.3.0+. Every triple carries prov + confidence so the H-Darrieus invariant (no high-confidence AI extraction without reviewer) survives the export boundary"
  - "ADR-006 locks Phase 2 scope to docstring-only enrichment of scripts/exporters/to_jsonl_triples.py — no implementation, no test fixtures. main() continues to raise NotImplementedError until Phase 5 / v0.2.0 GraphRAG sprint. Plan 02-10 inherits the docstring contract spelled out in ADR-006 §Decision"
  - "ADR-003 finalized via append-only Edit (post-baseline-review closing block) NOT rewrite — the on-main initial draft from Plan 02-03 already carried the four boundary worked-example tables (D-10/D-11/D-12 + the requires/constrained_by/equivalent_to/interfaces_with/complies_with details) and the internalization rationale for has_revision (→ version_history[]) and generated_by (→ provenance.actor + provenance.tool). The finalization block confirms each of the six relation schemas now carries its verbatim description anchor, and reaffirms net relation count v0.1.0 = 16"
metrics:
  duration_minutes: 9
  completed_date: 2026-05-03
  tasks_completed: 2
  tasks_total: 2
  files_created: 4
  files_modified: 1
  commits: 3
threat_flags: []
---

# Phase 02 Plan 09: Relations Additions + Triple-Export ADR Summary

## One-liner

Three ADR-003 added relation schemas (`interfaces_with`, `complies_with`, `applicable_during_phase`) shipped as JSON Schema Draft 2020-12 composition-style files in `ontology/schemas/`. ADR-006 (JSONL `{s, p, o, prov, confidence}` triple export + Phase 2 docstring-only scope) authored. ADR-003 finalized via append-only post-baseline-review closing block. Net relation count for v0.1.0 closes at **16 relation schemas** (13 baseline from Plan 02-08 + 3 additions in this plan); ONT-R-17 (`has_revision`) and ONT-R-19 (`generated_by`) ship NO schema files — both internalized as fields per D-07/D-09.

## Deliverables

### 3 added relation schemas

| File | type.const | ONT-R | Required (additional) | Optional metadata | Boundary discipline (verbatim in description) |
|------|------------|-------|-----------------------|-------------------|-----------------------------------------------|
| `relation.interfaces-with.schema.json` | `interfaces_with` | 15 | `interface_type` enum | `interface_protocol` string | **D-05 / D-10**: peer-tier system↔system; DO NOT USE for parent-child (use `part_of`), cross-tier dependency (use `requires`), regulatory compliance (use `complies_with`). ARINC 429 worked example present. |
| `relation.complies-with.schema.json` | `complies_with` | 16 | (none beyond base) | `compliance_evidence` URI; `compliance_status` enum [demonstrated, claimed, in_progress, exempted] | **D-06 / D-11**: explicit normative compliance, audit-grade. DO NOT USE for budget / non-normative constraints (use `constrained_by`); DO NOT USE for soft-compliance / no audit trail (use `constrained_by`); DO NOT USE for citation only (use `cites`). FAR §25.305 + DO-178C_LevelB worked examples present. |
| `relation.applicable-during-phase.schema.json` | `applicable_during_phase` | 18 | `flight_phase` enum [taxi, takeoff, climb, cruise, approach, landing, missed_approach, emergency, ground_operations] | (none beyond base) | **D-08**: flight phase scope; NOT for aircraft-model scope (use `applicable_to`). Inline enum per CONTEXT.md Open Question #3 — no separate vocabulary YAML in v0.1.0. |

### ADR-006 (new)

`.planning/decisions/ADR-006-triple-export.md` — Status: ACCEPTED. Implements D-18 + D-19. Documents:

- The JSONL line shape `{s, p, o, prov, confidence}` with concrete `aviationkb://` URI worked examples
- Per-entity triple-generation rule (one `rdf:type` triple + one per scalar field + one per array element + one per nested-object leaf scalar)
- Per-relation triple-generation rule (one triple per relation file using the file's own provenance + confidence — NOT the subject/object entity blocks)
- Why JSONL over RDF/Turtle for v0.1.0 (six numbered reasons)
- Phase 2 scope lock: docstring enrichment only, no implementation, no test fixtures; `main()` continues to raise `NotImplementedError`
- PROV-O alignment path for v0.3.0+ RDF/Turtle export (`prov.actor` → `prov:wasAttributedTo`, `prov.method` → `prov:wasGeneratedBy`, etc.)

### ADR-003 finalization

`.planning/decisions/ADR-003-relation-additions.md` — appended a "Post-baseline-review status (Plan 09 finalization, 2026-05-03)" closing block confirming:

- Status: ACCEPTED (FINALIZED)
- Each ADR-003 boundary worked-example table is verifiably embedded in a concrete schema description (six relations enumerated: requires / constrained_by / equivalent_to from Plan 02-08; interfaces_with / complies_with / applicable_during_phase from this plan)
- ONT-R-17 (`has_revision`) and ONT-R-19 (`generated_by`) ship NO schema file — satisfied by `version_history[]` and `provenance.actor` + `provenance.tool` respectively
- Net relation count v0.1.0 = 16 (13 baseline + 3 additions), confirmed against the directory listing
- No further changes anticipated for v0.1.0

## Boundary-discipline confirmation

Per Plan acceptance criteria + ADR-003 / D-05..D-11. Verified by `grep`:

| Schema | Required text fragments | grep result |
|--------|-------------------------|-------------|
| `relation.interfaces-with` | `"DO NOT USE"` AND `"requires"` AND `"ARINC 429"` | all present |
| `relation.complies-with` | `"DO NOT USE"` AND `"constrained_by"` AND `"FAR §25"` | all present |
| `relation.applicable-during-phase` | `"flight_phase"` AND `"taxi"` AND `"takeoff"` AND `"cruise"` AND `"approach"` AND `"landing"` AND `"missed_approach"` AND `"emergency"` | all present in enum + description |

## ONT-R-17 + ONT-R-19 (NOT-A-RELATION) confirmation

| ONT-R | Candidate | Outcome | Where the requirement is satisfied |
|-------|-----------|---------|-----------------------------------|
| ONT-R-17 | `has_revision` | NOT a relation per ADR-003 / D-07 | `version_history: [{version, date, author, change_summary}]` field on `entity.base.schema.json` per D-15 / ADR-004 (composed by every entity schema in Plans 02-02 / 02-04..07) |
| ONT-R-19 | `generated_by` | NOT a relation per ADR-003 / D-09 | `provenance.actor` (Person/Org URI) + `provenance.tool` (string) in `_meta.schema.json#/$defs/provenance` per D-16 / ADR-005 (composed via baseFields by every entity and relation schema) |

No schema files ship for these. The plan's `<files_modified>` frontmatter ALREADY reflected this (only 4 files: 3 schemas + ADR-006 + the in-place ADR-003 amendment).

## Pitfall confirmations

- **Pitfall #1** (additionalProperties + allOf): all 3 added schemas use `unevaluatedProperties: false`; literal `"additionalProperties"` does NOT appear in any of them. Verified by `! grep -q '"additionalProperties"'`.
- **Pitfall #9** (Draft mismatch): all 3 schemas declare `"$schema": "https://json-schema.org/draft/2020-12/schema"` exactly. No Draft-04 / Draft-07 leakage.
- **Pitfall #4** (worked-example overlap): interfaces_with carries the cross-tier-vs-peer-tier USE/DON'T-USE pair; complies_with carries the audit-grade-normative-vs-non-normative USE/DON'T-USE pair. Both reference the boundary sibling by name (`requires` and `constrained_by` respectively).

## Verification Results

```bash
# Each of the 3 added schemas — Draft 2020-12 metaschema validation
for s in interfaces-with complies-with applicable-during-phase; do
  check-jsonschema --check-metaschema "ontology/schemas/relation.$s.schema.json"
done
# → 3 × "ok -- validation done"
```

| Check | Result |
|-------|--------|
| `check-jsonschema --check-metaschema` × 3 files | 3 × exit 0 |
| `grep -q '"unevaluatedProperties": false'` × 3 | 3 × match |
| `! grep -q '"additionalProperties"'` × 3 | 3 × absent (Pitfall #1 lock) |
| `jq '.allOf[0]["$ref"] == "relation.base.schema.json"'` × 3 | 3 × true |
| `jq '.properties.type.const'` matches snake_case name × 3 | interfaces_with / complies_with / applicable_during_phase — all true |
| `jq -e '.properties.interface_type.enum \| contains(["data","power","mechanical","thermal"])'` | true |
| `jq -e '.properties.flight_phase.enum \| contains(["takeoff","cruise","landing","emergency"])'` | true |
| `grep -q "DO NOT USE"` on interfaces_with + complies_with | both match |
| `grep -q "ARINC 429"` on interfaces_with | match |
| `grep -q "FAR §25"` on complies_with | match |
| `grep -q "constrained_by"` on complies_with | match |
| `grep -q "requires"` on interfaces_with | match |
| ADR-006 `grep -q 'JSONL\|D-18\|D-19\|PROV-O\|aviationkb://\|YAGNI\|AI 接力开发指南\|scripts/exporters/to_jsonl_triples.py'` | all 8 fragments present |
| Net `ls ontology/schemas/relation.*.schema.json \| wc -l` | 17 (= 1 base + 16 leaf relations) |

### ADR-006 acceptance criteria (8/8 grep checks)

```text
JSONL                                              ✓
D-18                                               ✓
D-19                                               ✓
PROV-O                                             ✓
aviationkb://                                      ✓
AI 接力开发指南                                     ✓
YAGNI                                              ✓
scripts/exporters/to_jsonl_triples.py              ✓
```

## Deviations from Plan

None — plan executed exactly as written. Three minor, planner-anticipated execution choices worth recording:

1. **`compliance_evidence` URI is OPTIONAL at the schema layer** (the Plan brief said "optional"). Phase 3 validator will enforce the cross-field rule "`compliance_status == 'demonstrated'` implies `compliance_evidence` present and resolvable to TestReport / SimulationCase / Procedure". Making it required at the schema layer would over-constrain `claimed` / `in_progress` / `exempted` records, which legitimately don't have evidence yet.
2. **`applicable_during_phase.object` URI carry-through** — relation.base requires `object`, so `applicable_during_phase` records still set `object`. The schema description explicitly tells authors to use a placeholder `aviationkb://flight-phase/<flight_phase>@1` URI; the **`flight_phase` enum is the semantic source of truth** for v0.1.0. This avoids forcing flight phases to be first-class entities in v0.1.0 while keeping the relation.base contract honored. A future v0.2.0+ ADR could promote flight phases to entities and reuse the existing `object` field cleanly.
3. **ADR-003 finalization via append-only Edit** — per the executor's anti-merge-conflict prompt, the on-main initial draft was kept verbatim and a "Post-baseline-review status" closing block was appended. This avoids the merge-conflict pattern that bit ADR-002 in Plan 02-07's finalization.

## Threat-model dispositions

| Threat ID | Disposition | How mitigated |
|-----------|-------------|---------------|
| T-02-09-01 (Pitfall #1 in any of 3) | mitigated | per-file `! grep -q '"additionalProperties"'` confirmed; every file uses `unevaluatedProperties: false` |
| T-02-09-02 (complies_with weak description → demo confuses with constrained_by) | mitigated | description carries verbatim ADR-003 USE/DON'T-USE table including FAR §25.305 + DO-178C worked examples and explicit "DO NOT USE for budget / non-normative" sibling reference |
| T-02-09-03 (ADR-006 omits provenance carry-through → future export drops audit trail) | mitigated | ADR-006 §Decision mandates `prov` + `confidence` blocks per triple; §Rationale documents the H-Darrieus invariant preservation across the export boundary; PROV-O alignment path for v0.3.0+ documented |

## Self-Check: PASSED

All 6 declared files exist on disk; all 3 task commits (`8b9dce8`, `0b00c09`, `8e25bff`) are present in `git log`.

```text
FOUND: ontology/schemas/relation.interfaces-with.schema.json
FOUND: ontology/schemas/relation.complies-with.schema.json
FOUND: ontology/schemas/relation.applicable-during-phase.schema.json
FOUND: .planning/decisions/ADR-006-triple-export.md
FOUND: .planning/decisions/ADR-003-relation-additions.md
FOUND: .planning/phases/02-ontology-schema-v0-1-0/02-09-SUMMARY.md

FOUND: 8b9dce8 (feat(02-09): add 3 ADR-003 relation schemas)
FOUND: 0b00c09 (docs(02-09): add ADR-006 triple export format)
FOUND: 8e25bff (docs(02-09): finalize ADR-003 with post-baseline-review status)
```

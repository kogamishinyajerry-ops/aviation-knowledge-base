---
phase: 02-ontology-schema-v0-1-0
plan: 08
subsystem: ontology-schemas
tags: [ontology, json-schema, draft-2020-12, relations, baseline, boundary-discipline, h-darrieus, adr-003]
one_liner: "13 baseline relation schemas (ONT-R-02..14) composing relation.base; requires/constrained_by/equivalent_to descriptions verbatim implement ADR-003 boundary tables; conflicts_with carries mandatory ≥20-char rationale."
dependency_graph:
  requires:
    - "ontology/schemas/relation.base.schema.json (Plan 02-03) — composition root with subject/object/valid_from/valid_until + baseFields"
    - "ontology/_meta.schema.json (Plan 02-01) — provides $defs/schemaVersionString and the URI/baseFields plumbing reachable through relation.base"
    - ".planning/decisions/ADR-003-relation-additions.md (Plan 02-03) — canonical source for the verbatim USE/DON'T-USE boundary tables"
  provides:
    - "ontology/schemas/relation.part-of.schema.json (ONT-R-02)"
    - "ontology/schemas/relation.applicable-to.schema.json (ONT-R-03)"
    - "ontology/schemas/relation.constrained-by.schema.json (ONT-R-04 + boundary vs complies_with per D-11)"
    - "ontology/schemas/relation.verified-by.schema.json (ONT-R-05)"
    - "ontology/schemas/relation.derived-from.schema.json (ONT-R-06)"
    - "ontology/schemas/relation.supersedes.schema.json (ONT-R-07 + active→superseded RegulationClause status flow per Pitfall #6)"
    - "ontology/schemas/relation.cites.schema.json (ONT-R-08 + cite-as-reference Document URI target)"
    - "ontology/schemas/relation.causes.schema.json (ONT-R-09)"
    - "ontology/schemas/relation.mitigated-by.schema.json (ONT-R-10)"
    - "ontology/schemas/relation.requires.schema.json (ONT-R-11 + boundary vs interfaces_with per D-10)"
    - "ontology/schemas/relation.equivalent-to.schema.json (ONT-R-12 + 'NOT for cross-language' i18n foil per D-12)"
    - "ontology/schemas/relation.conflicts-with.schema.json (ONT-R-13 + required conflict_rationale ≥20 chars)"
    - "ontology/schemas/relation.used-in.schema.json (ONT-R-14)"
  affects:
    - "Plan 02-09 (interfaces_with, complies_with, applicable_during_phase) — closes the boundary loop opened by relation.requires/constrained_by descriptions"
    - "Phase 3 validators — must enforce supersedes ↔ RegulationClause.status='superseded' coupling and used_in ↔ SimulationCase URI-field inverse-consistency"
    - "Phase 4 demo data — exercises cites with Document locator; uses chain_position on causes; conflicts_with with audit-grade rationale"
tech_stack:
  added: []
  patterns:
    - "JSON Schema Draft 2020-12 composition via allOf + $ref to relation.base.schema.json (relative reference, runtime-resolvable by check-jsonschema)"
    - "unevaluatedProperties: false on every leaf relation schema (Pitfall #1 lock; allOf-aware strictness)"
    - "Filename uses kebab-case slug (relation.part-of.schema.json); type.const uses snake_case (part_of)"
    - "Verbatim ADR-003 boundary tables embedded in description fields (Pitfall #4 lock)"
key_files:
  created:
    - "ontology/schemas/relation.part-of.schema.json"
    - "ontology/schemas/relation.applicable-to.schema.json"
    - "ontology/schemas/relation.verified-by.schema.json"
    - "ontology/schemas/relation.derived-from.schema.json"
    - "ontology/schemas/relation.supersedes.schema.json"
    - "ontology/schemas/relation.cites.schema.json"
    - "ontology/schemas/relation.causes.schema.json"
    - "ontology/schemas/relation.constrained-by.schema.json"
    - "ontology/schemas/relation.mitigated-by.schema.json"
    - "ontology/schemas/relation.requires.schema.json"
    - "ontology/schemas/relation.equivalent-to.schema.json"
    - "ontology/schemas/relation.conflicts-with.schema.json"
    - "ontology/schemas/relation.used-in.schema.json"
  modified: []
decisions:
  - "Adopted Code Example #3 template verbatim — every leaf schema is allOf+$ref to relation.base.schema.json with type.const discriminator + optional metadata + unevaluatedProperties:false"
  - "Locked Pitfall #4 boundary discipline: requires (cross-tier vs interfaces_with peer-tier), constrained_by (generic vs complies_with normative), equivalent_to (NOT for cross-language — i18n field instead). All three descriptions cite ADR-003 / D-10..D-12 by ID"
  - "Made conflict_rationale a required ≥20-char string on relation.conflicts-with (T-02-08-03 mitigation: a conflict claim without explanation is unauditable)"
  - "Did NOT redeclare subject / object / valid_from / valid_until on leaf schemas — those are inherited from relation.base via allOf. Only added type.const + schema_version + relation-specific optional metadata. unevaluatedProperties:false enforces no stray fields on the merged schema"
metrics:
  duration_minutes: 7
  completed_date: 2026-05-03
  tasks_completed: 2
  tasks_total: 2
  files_created: 13
  commits: 2
threat_flags: []
---

# Phase 02 Plan 08: Relations Baseline Summary

## One-liner

13 baseline relation schemas (ONT-R-02..14) authored as JSON Schema Draft 2020-12 files in `ontology/schemas/`. Each composes `relation.base.schema.json` via `allOf + $ref`, locks `unevaluatedProperties: false` (Pitfall #1), and exposes a `type` const discriminator matching the snake_case relation name. Three relations carry verbatim ADR-003 boundary worked-examples in their descriptions (requires↔interfaces_with per D-10; constrained_by↔complies_with per D-11; equivalent_to↔i18n per D-12). One relation (`conflicts_with`) carries a mandatory ≥20-char `conflict_rationale` string for audit-grade conflict claims.

## Deliverables

### 13 leaf relation schemas

| # | File | type.const | ONT-R | Optional metadata | Boundary discipline |
|---|------|------------|-------|-------------------|---------------------|
| 1 | `relation.part-of.schema.json` | `part_of` | 02 | `cardinality_hint` enum | composition; transitive |
| 2 | `relation.applicable-to.schema.json` | `applicable_to` | 03 | `applicability_scope` string | distinct from complies_with — broader scope |
| 3 | `relation.constrained-by.schema.json` | `constrained_by` | 04 | `constraint_kind` enum | **D-11 boundary**: NOT for normative compliance → use complies_with |
| 4 | `relation.verified-by.schema.json` | `verified_by` | 05 | `verification_method` enum (test/analysis/inspection/demonstration/simulation/similarity) | distinct from cites |
| 5 | `relation.derived-from.schema.json` | `derived_from` | 06 | none | distinct from cites and complies_with |
| 6 | `relation.supersedes.schema.json` | `supersedes` | 07 | `supersession_reason` ≥20 chars | **Pitfall #6**: anchored to RegulationClause status flow active→superseded |
| 7 | `relation.cites.schema.json` | `cites` | 08 | `locator: {page, section, paragraph}`, `quotation` | object MUST resolve to Document entity URI |
| 8 | `relation.causes.schema.json` | `causes` | 09 | `chain_position` enum (proximate/contributing/root) | URI-only in v0.1.0; free-text effects → FailureMode.effects |
| 9 | `relation.mitigated-by.schema.json` | `mitigated_by` | 10 | `mitigation_type` enum | paired with causes |
| 10 | `relation.requires.schema.json` | `requires` | 11 | none | **D-10 boundary**: NOT for peer-tier → use interfaces_with; NOT for parent-child → use part_of |
| 11 | `relation.equivalent-to.schema.json` | `equivalent_to` | 12 | `equivalence_basis` enum | **D-12 boundary**: NOT for cross-language pairs — use entity i18n field |
| 12 | `relation.conflicts-with.schema.json` | `conflicts_with` | 13 | `conflict_rationale` (REQUIRED ≥20 chars), `severity` enum | T-02-08-03 mitigation |
| 13 | `relation.used-in.schema.json` | `used_in` | 14 | none | inverse of SimulationCase URI fields (cfd_method_ref / turbulence_model_ref / mesh_ref) |

## Boundary discipline confirmation

Per Plan acceptance criteria + ADR-003 / D-10..D-12, three relations embed verbatim USE / DON'T USE locks in their `description` fields. Verified by `grep`:

| Relation | Required text fragments | grep result |
|----------|-------------------------|-------------|
| `relation.requires` | `"DO NOT USE"` AND `"interfaces_with"` | both present |
| `relation.constrained-by` | `"DO NOT USE"` AND `"complies_with"` | both present |
| `relation.equivalent-to` | `"DO NOT USE FOR: cross-language"` AND `"i18n"` | both present |
| `relation.cites` | references `Document` as cite-resolution target | present |
| `relation.supersedes` | references active→superseded `RegulationClause` status flow (Pitfall #6) | present |

## Pitfall confirmations

- **Pitfall #1** (additionalProperties + allOf composition): every leaf schema uses `unevaluatedProperties: false` exclusively; `additionalProperties` literal does NOT appear in any of the 13 files. Verified by negative grep over the file set.
- **Pitfall #9** (Draft mismatch): every `$schema` is exactly `https://json-schema.org/draft/2020-12/schema`. No Draft-04 / Draft-07 leakage.
- **Pitfall #4** (worked-example overlap): three boundary-prone relations carry verbatim ADR-003 USE/DON'T-USE locks readable to a fresh AI session.
- **Pitfall #6** (supersession status drift): `relation.supersedes.description` ties the relation to the RegulationClause active→superseded status flow so Phase 3 validator can cross-check that supersedes points to an entity whose previous version's status is `superseded`.

## Verification Results

```bash
# Each of the 13 schemas — Draft 2020-12 metaschema validation
for s in part-of applicable-to verified-by derived-from supersedes cites causes \
         constrained-by mitigated-by requires equivalent-to conflicts-with used-in; do
  check-jsonschema --check-metaschema "ontology/schemas/relation.$s.schema.json"
done
# → 13 × "ok -- validation done"
```

| Check | Result |
|-------|--------|
| `check-jsonschema --check-metaschema` × 13 files | 13 × exit 0 |
| `grep -q '"unevaluatedProperties": false'` × 13 | 13 × match |
| `! grep -q '"additionalProperties"'` × 13 | 13 × absent (Pitfall #1 lock) |
| `jq '.allOf[0]["$ref"] == "relation.base.schema.json"'` × 13 | 13 × true |
| `jq '.properties.type.const'` matches snake_case name × 13 | 13 × true |
| `jq -e '.required \| contains(["conflict_rationale"])'` on conflicts-with | true |
| `grep -q "DO NOT USE"` on requires + constrained-by | both match |
| `grep -q "interfaces_with"` on relation.requires | match |
| `grep -q "complies_with"` on relation.constrained-by | match |
| `grep -q "DO NOT USE FOR: cross-language"` on relation.equivalent-to | match |
| `grep -q "i18n"` on relation.equivalent-to | match |

## Deviations from Plan

None — plan executed exactly as written. The optional metadata fields specified in the plan brief (`cardinality_hint`, `applicability_scope`, `verification_method`, `supersession_reason`, `locator`+`quotation`, `chain_position`, `constraint_kind`, `mitigation_type`, `equivalence_basis`, `severity`) all landed verbatim. The 5 base required fields (`type`, `schema_version`, `subject`, `object`, `valid_from`) are inherited from relation.base via the allOf composition — leaf schemas only added their own `required: [conflict_rationale]` where applicable (relation.conflicts-with).

## Threat-model dispositions

| Threat ID | Disposition | How mitigated |
|-----------|-------------|---------------|
| T-02-08-01 (Pitfall #1 in any of 13) | mitigated | per-file `! grep -q '"additionalProperties"'` confirmed; every file uses `unevaluatedProperties: false` |
| T-02-08-02 (Pitfall #4 boundary ambiguity) | mitigated | requires / constrained_by / equivalent_to descriptions verbatim implement ADR-003 / D-10..D-12 worked examples |
| T-02-08-03 (conflicts_with without rationale) | mitigated | `conflict_rationale` required, `minLength: 20` |

## Pointer to Plan 09

Plan 09 ships the 3 ADR-003-accepted-addition relation schemas that close the boundary loop opened by this plan:

- `relation.interfaces-with.schema.json` (ONT-R-15) — peer-tier complement to `requires` (D-05)
- `relation.complies-with.schema.json` (ONT-R-16) — normative complement to `constrained_by` (D-06)
- `relation.applicable-during-phase.schema.json` (ONT-R-18) — flight-phase scope independent from `applicable_to` (D-08)

Each Plan-09 schema MUST embed the matching ADR-003 worked-example table verbatim in its description (mirroring the discipline locked here).

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | `2abdee7` | `feat(02-08): add 7 simple relation schemas (part_of, applicable_to, verified_by, derived_from, supersedes, cites, causes)` |
| 2 | `1a5c2b5` | `feat(02-08): add 6 boundary-discipline relation schemas (constrained_by, mitigated_by, requires, equivalent_to, conflicts_with, used_in)` |

All commits used `--no-verify` per parallel-agent execution context (orchestrator runs unified pre-commit at merge time).

## Self-Check: PASSED

All claimed artifacts verified on disk:

- `ontology/schemas/relation.part-of.schema.json` — FOUND
- `ontology/schemas/relation.applicable-to.schema.json` — FOUND
- `ontology/schemas/relation.verified-by.schema.json` — FOUND
- `ontology/schemas/relation.derived-from.schema.json` — FOUND
- `ontology/schemas/relation.supersedes.schema.json` — FOUND
- `ontology/schemas/relation.cites.schema.json` — FOUND
- `ontology/schemas/relation.causes.schema.json` — FOUND
- `ontology/schemas/relation.constrained-by.schema.json` — FOUND
- `ontology/schemas/relation.mitigated-by.schema.json` — FOUND
- `ontology/schemas/relation.requires.schema.json` — FOUND
- `ontology/schemas/relation.equivalent-to.schema.json` — FOUND
- `ontology/schemas/relation.conflicts-with.schema.json` — FOUND
- `ontology/schemas/relation.used-in.schema.json` — FOUND
- `.planning/phases/02-ontology-schema-v0-1-0/02-08-SUMMARY.md` — FOUND (this file)

All claimed commits verified in `git log`:

- `2abdee7` — FOUND (Task 1: 7 simple relations)
- `1a5c2b5` — FOUND (Task 2: 6 boundary-discipline relations)

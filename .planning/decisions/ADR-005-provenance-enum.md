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
        "Either lower confidence (<=0.85) and explain in rationale, "
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
- Phase 4 demo data MUST include >=1 `_pending/` record (DEMO-06) and >=1 `hybrid_reviewed` canonical record.
- Future schema evolutions cannot add new enum values without an ADR explaining the new audit semantics.

## References

- PROJECT.md Core Value
- REQUIREMENTS.md PROV-01, PROV-04, PROV-05
- 02-CONTEXT.md D-16, D-17
- 02-RESEARCH.md Pitfall #8 (H-Darrieus enforcement gap)
- User MEMORY.md `cfd-ai-workbench` § "诚实性问题（2026-04-01）"
- Phase 3 plan (forthcoming) §`scripts/validators/provenance.py`

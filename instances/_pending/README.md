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
- Phase 4 plan (DEMO-06) — ships >=1 record demonstrating this pattern end-to-end

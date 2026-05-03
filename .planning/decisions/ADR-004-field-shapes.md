# ADR-004 — Schema Field Shapes (confidence, i18n, version_history)

Status: ACCEPTED
Date: 2026-05-03
Deciders: user (CONTEXT.md interactive discuss, 2026-05-03)
Implements: D-13, D-14, D-15

## AI 接力开发指南

> Fresh Claude / Codex / DeepSeek session opening this ADR cold should read the next paragraph and the §Decision tables, then the §Reconciliation note (CRITICAL — D-15 wording was corrected). Do not extend or re-shape these three field families without amending this ADR.

This ADR documents the exact JSON shape of three field families that show up on every entity and many relations: `confidence`, `i18n`, and `version_history`. These shapes are encoded in `ontology/_meta.schema.json` (Plan 02-01, already shipped). This ADR exists to explain WHY they are shaped that way and to lock the rules so that Plans 04..07 (leaf entity schemas), Plan 08..09 (relation schemas), and Phase 3 (validators) all reference the same definitions.

## Context

Three field families appear across many entity types. If each entity invents its own shape, downstream consumers (RAG retriever in Phase 5, validators in Phase 3, exporters in Phase 5+) face a "shape zoo": every consumer must handle every variation. Picking shapes upfront and documenting the rationale makes future maintainers confident that they can extend a field without breaking existing consumers.

The three families:

1. **`confidence`** — every record carries one (per `_meta.schema.json#/$defs/confidence`); the H-Darrieus REJECT rule (ADR-005) keys on `confidence.score > 0.85`
2. **`i18n`** — bilingual content (zh / en) on every entity that has human-readable labels or descriptions
3. **`version_history`** — revision audit trail on every entity that bumps past version 1

## Decision

### `confidence` — object with `score` (decimal 0..1) + `rationale` (≥20 chars) (D-13)

Implemented at `_meta.schema.json#/$defs/confidence`. Required keys: `score`, `rationale`. Optional: `calibration_method` (free-text in v0.1.0; structured in v0.2.0+).

```json
{
  "confidence": {
    "score": 0.85,
    "rationale": "Multi-source agreement: cited in FAA AC 25.1309-1B and EASA AMC 25.1309 with identical text."
  }
}
```

**Why decimal [0.0, 1.0] (not letter grades, not percent integer):**

- The H-Darrieus REJECT threshold (`score > 0.85`, ADR-005) needs a numeric comparison. Letter grades break this.
- Percent integer (0–100) loses information at the threshold edge — we want the 0.86 vs 0.85 distinction.
- Float [0, 1] is the standard ML / probability convention.

**Why `rationale` required (not optional):**

- A confidence score with no rationale is uninspectable. The H-Darrieus failure mode (high confidence + no audit trail) starts here.
- `minLength: 20` enforces "at least one full sentence" in practice. Empty / "TODO" / "n/a" rationales fail validation by design.

### `i18n` — flat object with `label` and `full_text` sub-objects (D-14)

Implemented as the pattern reused inline in `entity.base` (Plan 02-02); the `i18n.label` shape uses `_meta.schema.json#/$defs/i18nLabel` directly.

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

**Schema rules:**

- `i18n.label` is REQUIRED on every entity carrying human-readable identity. Both `zh` and `en` keys must be present (either may be the empty string for genuinely monolingual content like a Chinese-only accident report).
- `i18n.full_text` is OPTIONAL; if present, both `zh` and `en` keys must be present (same monolingual rule).
- Keys are exactly `zh` and `en` (ISO 639-1 codes). NOT `chinese`/`english`, NOT `zh_CN`/`en_US`. Future regional variants (e.g. `zh_TW`, `en_GB`) can be added in v0.2.0+ without breaking change because the schema uses `unevaluatedProperties: false` only at the i18n-block boundary, not on the language-key map (see `_meta.schema.json#/$defs/i18nLabel`).

**Why flat (not nested per-language root, like `{zh: {label, full_text}, en: {label, full_text}}`):**

- Adding a new field type (e.g. `summary`) is one place: `i18n.summary.{zh, en}`. The nested shape would be 2+ places.
- Filtering "give me all label fields across both languages" is a single dot-path query (`i18n.label.*`).

**Why required `zh` AND `en` keys (not optional):**

- The Phase 5 RAG retriever indexes both languages from the same record (D-12, ADR-003). Optional keys would mean "language X is missing — skip" branches scattered through the retrieval code. Empty string is explicit and uniform.
- Per-translation provenance is deferred to v0.2.0+ (CONTEXT.md "Deferred Ideas") — when it lands, the empty-string convention extends naturally.

### `version_history` — array of revision records (D-15)

Optional on every entity in v0.1.0; mandatory once `version > 1`.

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

**Per-item required fields:**

- `version` — integer ≥1 (revision counter)
- `date` — ISO 8601 timestamp
- `author` — Person or Organization URI per D-23 (e.g. `aviationkb://person/jane-engineer@1`)
- `change_summary` — string ≥20 chars

**Array-level rules:**

- The array is OPTIONAL; absence implies the record is at version 1 (the implicit initial state).
- When an entity bumps to `version > 1`, `version_history` becomes mandatory and must contain entries from version 1 forward (chronological order, no gaps).
- The latest array element's `version` must equal the entity's top-level `version` field (D-20). Phase 3 validator enforces.

**Why an array on the entity (not separate has_revision relations):** see ADR-003 §"Internalized fields".

**Why each item carries a Person/Org URI (not free-text "John"):** without a URI target, `version_history.author` becomes free text and the H-Darrieus failure mode reappears at the audit-trail layer. Audit-grade revision tracking requires a URI you can dereference to a Person/Organization entity (Plan 07).

**Why `change_summary` ≥20 chars:** matches the `confidence.rationale` discipline; "fix typo" is too short to be auditable.

## Reconciliation: `version_history[].version` is INTEGER, not semver (corrects D-15 wording)

CONTEXT.md D-15 originally read:

> `version_history` array shape: `[{ version: semver string, date: ISO8601, author: Person/Org URI, change_summary: string (≥1 sentence) }]`

**This wording is hereby corrected.** The actual decision (and the implementation in `_meta.schema.json` + the leaf entity schemas in Plans 04..07) is:

- **`version_history[].version` is an INTEGER revision counter** (1, 2, 3, …) representing the entity's local revision number.
- **`schema_version` is the SEMVER string** (e.g. `"0.1.0"`) representing which ontology release the record was written against. This is the `schemaVersionString` `$defs` in `_meta.schema.json` and is per-record, NOT per-revision.

The two fields answer two different questions:

| Field | Type | Semantics | Owner |
|-------|------|-----------|-------|
| `version_history[].version` | integer ≥1 | "Which revision of THIS entity is this?" | Entity author / reviewer |
| `schema_version` | semver string `^\d+\.\d+\.\d+$` | "Which ontology release was this record written against?" | Frozen at write time; `ontology/VERSION` is the source |

Conflating the two would couple every entity revision to an ontology release bump, which is wrong: an entity can be revised many times within a single ontology release (e.g. `0.1.0`), and an ontology release can ship without any individual entity changing.

**This reconciliation note is the canonical source.** Future Claude sessions reading CONTEXT.md D-15 must treat the present ADR as the authoritative interpretation. CONTEXT.md will be patched out-of-band; this ADR resolves the ambiguity in the meantime.

## Rationale (cross-cutting)

Three field families, three different shapes, one consistent philosophy: **structured over free-text wherever a downstream consumer might need to query, validate, or render the field**. We refuse to cheap out on shape design; the cost is paid here once, the savings are paid every Phase 3+ time we add a new validator or exporter.

Concrete payoff:

- `confidence.score > 0.85` is a single numeric predicate — the entire H-Darrieus REJECT validator (ADR-005) is one comparison.
- `i18n.label.zh` / `i18n.label.en` are stable dot-paths — the RAG retriever indexes them with a single template.
- `version_history[].author` is a URI — graph queries "all entities revised by Person X" are trivial.

## Consequences

- `_meta.schema.json` already exposes `$defs/confidence`, `$defs/i18nLabel`, `$defs/uri`, `$defs/isoDateTime`, `$defs/schemaVersionString` — Plan 02-01 deliverable, locks the shapes documented here.
- `entity.base.schema.json` REQUIRES `i18n.label`; `version_history[]` is optional but structurally locked — Plan 02-02 (parallel sibling).
- Person / Organization schemas (Plan 07) populate the URI shape that `version_history.author` and `provenance.actor` / `reviewer` reference.
- Phase 3 validator MUST enforce the integer-vs-semver split documented in §Reconciliation; conflating them is a bug.
- Phase 4 demo data MUST include ≥1 instance with bilingual `i18n.full_text` (DEMO-07) and SHOULD include ≥1 instance with `version_history.length >= 2` to exercise the format.

## References

- REQUIREMENTS.md ONT-E-01 (entity base mandatory fields), VER-03 (schema_version on every record)
- 02-CONTEXT.md D-13, D-14, D-15 (D-15 wording superseded by §Reconciliation above)
- 02-RESEARCH.md Code Example #1 (`_meta.schema.json` shape)
- ontology/_meta.schema.json (Plan 02-01) — `$defs/confidence`, `$defs/i18nLabel`, `$defs/schemaVersionString`
- ADR-005 (provenance enum + H-Darrieus rule — `confidence.score > 0.85` threshold)
- ADR-003 (`equivalent_to` is NOT for cross-language — i18n field carries this)

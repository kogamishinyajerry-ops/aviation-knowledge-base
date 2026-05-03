---
phase: 03-validators-ci-active
plan: 03
subsystem: validators
tags: [validators, provenance, ids, h-darrieus, pending-gate, schema-version, PROV-04, PROV-05, VER-03]
dependency_graph:
  requires:
    - "03-01 (validator skeleton + 11 valid fixtures)"
    - "03-02 (12 invalid fixtures)"
  provides:
    - "scripts/validators/ids.py (real)"
    - "scripts/validators/provenance.py (real)"
    - "5 namespaced rules: ids.uri-format, ids.type-prefix-mismatch, provenance.h-darrieus, provenance.pending-gate, provenance.schema-version-mismatch"
  affects:
    - "scripts/validate.py (no edit; consumes both modules through existing dispatch loop)"
tech_stack:
  added: []
  patterns:
    - "All rules use namespaced rule= identifiers (module.rule-name) for grep-stable assertions"
    - "Public API stable: validate_record(path: Path, record: Any, **ctx) -> list[ValidationError]"
    - "Cross-record context surfaced via **ctx (repo_root, by_id, records) — non-cross-record callers ignore"
key_files:
  created: []
  modified:
    - "scripts/validators/ids.py"
    - "scripts/validators/provenance.py"
decisions:
  - "H-Darrieus boundary uses STRICT > 0.85 per ADR-005 — exactly 0.85 with no reviewer is allowed"
  - "Empty-string reviewer counts as 'no reviewer' for H-Darrieus (PROV-04 edge case)"
  - "_pending check is path-based via '/_pending/' substring in posix path, not Path.parts membership"
  - "schema_version mismatch is WARNING (not ERROR) at v0.1.0 because no N-1 exists yet; hardens to ERROR at v0.2.0+"
  - "ids.type-prefix-mismatch only fires when id is itself a syntactically valid URI; otherwise ids.uri-format already covers it (avoid double-error noise)"
  - "CFDMethod manually mapped to 'cfd-method' URI segment to avoid naive PascalCase→kebab producing 'c-f-d-method'"
metrics:
  duration: "~25 min"
  completed_date: "2026-05-03"
  tasks_completed: 2
  files_modified: 2
  commits: 2
---

# Phase 03 Plan 03: Provenance + ID Validators Summary

Filled in the Wave-1 stubs `scripts/validators/ids.py` and `scripts/validators/provenance.py` with the rules JSON Schema cannot express: URI/type cross-field consistency, the H-Darrieus REJECT cross-field rule (PROV-04 / ADR-005), the `_pending` promotion gate (PROV-05 / D-17), and the schema_version cross-record warning (VER-03 partial). Valid corpus stays green (11/11 records, 0 errors, 0 warnings); every targeted invalid fixture trips exactly the documented rule with the documented severity.

## Rules Implemented

| Rule | Module | Severity | Trigger | Maps to |
|------|--------|----------|---------|---------|
| `ids.uri-format` | `ids.py` | error | Field expected to be canonical URI does not match `^aviationkb://[a-z][a-z-]*/[a-z0-9]+(-[a-z0-9]+)*@[0-9]+$`. Checked on `id`, `subject`, `object`, `provenance.actor`, `provenance.reviewer` (when non-empty), `source.document_id` | D-23 |
| `ids.type-prefix-mismatch` | `ids.py` | error | Entity record's URI `<type>` segment ≠ kebab-case of `record.type` (cross-field) | D-24 / D-25 |
| `provenance.h-darrieus` | `provenance.py` | error | `method == "ai_extracted"` AND `score > 0.85` (STRICT) AND (reviewer absent OR reviewer == `""`) | PROV-04 / ADR-005 |
| `provenance.pending-gate` | `provenance.py` | error | Path contains `/_pending/` AND `method != "hybrid_reviewed"`, OR method is hybrid_reviewed but reviewer/reviewed_at missing | PROV-05 / D-17 |
| `provenance.schema-version-mismatch` | `provenance.py` | **warning** | `record.schema_version != ontology/VERSION` content | VER-03 (partial — warn only at v0.1.0; hardens to error at v0.2.0+) |

## Tasks Completed

### Task 1 — `scripts/validators/ids.py`
- Implements `ids.uri-format` and `ids.type-prefix-mismatch`.
- URI regex kept in lockstep with `ontology/_meta.schema.json#/$defs/uri`.
- `_ENTITY_TYPES` mirrors `loader.py`; CFDMethod manually mapped (only known acronym entity).
- Empty-string reviewer is intentionally NOT URI-format-checked here so the only emitted rule for that case is `provenance.h-darrieus`, not duplicate noise.
- Type-prefix-mismatch only fires when `id` is itself a syntactically valid URI — otherwise `ids.uri-format` already reports.
- **Commit:** `1273ba9`

### Task 2 — `scripts/validators/provenance.py`
- Implements all three provenance rules.
- H-Darrieus: STRICT `> 0.85` (so boundary value 0.85 does not fire); empty string reviewer treated as missing reviewer.
- `_pending` gate: substring match on `path.as_posix()` for `/_pending/` so any nested `_pending/` subpath is caught (not just single-segment); when method IS `hybrid_reviewed`, reviewer URI + `reviewed_at` are both required.
- `schema_version` mismatch: emits **warning** (not error) per VER-03 partial hardening — older-than-N-1 cannot fire at v0.1.0 because no N-1 exists; hardens to error at v0.2.0+.
- **Commit:** `48c484e`

## Verification

### Plan-required automated probes (all pass)

```
$ grep -q "provenance.h-darrieus" scripts/validators/provenance.py     # OK
$ grep -q "provenance.pending-gate" scripts/validators/provenance.py   # OK
$ grep -q "ids.uri-format" scripts/validators/ids.py                   # OK
$ grep -q "ids.type-prefix-mismatch" scripts/validators/ids.py         # OK
```

### Inline unit cases (Task 1: 2 cases, Task 2: 7 cases — all pass)

Task 1 inline:
- `not-a-uri` + `type=AircraftModel` → `ids.uri-format` ✓
- `aviationkb://document/x@1` + `type=AircraftModel` → `ids.type-prefix-mismatch` ✓

Task 2 inline:
- H-Darrieus fires on score=0.92 + ai_extracted + no reviewer ✓
- _pending gate fires on ai_extracted in `/_pending/` ✓
- H-Darrieus does NOT fire at boundary score=0.85 ✓
- H-Darrieus does NOT fire when reviewer set ✓
- H-Darrieus DOES fire when reviewer is empty string ✓
- _pending hybrid_reviewed + reviewer + reviewed_at PASSES ✓
- schema_version 0.0.1 vs current 0.1.0 → warning ✓

### End-to-end fixture probes

| Fixture | Expected rule | Actual |
|---------|---------------|--------|
| `valid/` (whole tree, 11 records) | none | 0 errors, 0 warnings ✓ |
| `invalid/h-darrieus-rejected/` | `provenance.h-darrieus` | fires (1 error) ✓ |
| `invalid/h-darrieus-empty-reviewer/` | `provenance.h-darrieus` | fires (also schema's URI-pattern complaint about `reviewer=""` — both expected per fixture comment "dual fire") ✓ |
| `invalid/pending-not-hybrid-reviewed/_pending/` | `provenance.pending-gate` | fires (1 error) ✓ |
| `invalid/old-schema-version/` | `provenance.schema-version-mismatch` (warning) | fires (0 errors, 1 warning) ✓ |
| `invalid/bad-uri-format/` | `ids.uri-format` | fires ✓ |
| `invalid/bad-internal-id/` | `ids.uri-format` (per planner — fixture uses bad-URI subject) | fires on `/subject` ✓ |

## Deviations from Plan

None. Plan executed exactly as written. The plan explicitly anticipated:

- The empty-string reviewer fixture's "dual fire" (schema rejects `""` against URI pattern AND `provenance.h-darrieus` fires) — observed and documented in the fixture header comment.
- Type-prefix-mismatch only firing when URI is otherwise valid — implemented via the `URI_RE.match(rid)` guard.
- `bad-internal-id/` fixture using a bad-URI `subject` rather than a true internal-id field — handled identically to URI format violation.

## Acceptance Gates (from execution_context)

- [x] `python scripts/validate.py tests/fixtures/valid/` exits 0 (11/11 still pass)
- [x] `tests/fixtures/invalid/h-darrieus-rejected/...` emits `provenance.h-darrieus` (error)
- [x] `tests/fixtures/invalid/pending-not-hybrid-reviewed/_pending/...` emits `provenance.pending-gate` (error)
- [x] `tests/fixtures/invalid/bad-uri-format/...` emits `ids.uri-format`
- [x] `tests/fixtures/invalid/bad-internal-id/...` emits `ids.uri-format` (subject URI bad)
- [x] `tests/fixtures/invalid/old-schema-version/...` emits `provenance.schema-version-mismatch` at WARNING
- [x] Inline unit tests via `python -c "..."` pass (9 cases total across both tasks)
- [x] Boundary: score=0.85 + no reviewer does NOT trip H-Darrieus (strict `>`)
- [x] Boundary: score=0.86 + reviewer set does NOT trip H-Darrieus (reviewer presence wins)
- [x] H-Darrieus fires on empty-string reviewer (PROV-04 edge case)

## Out-of-Scope (Untouched, Per Plan)

- `scripts/validators/relations.py` — owned by parallel sibling plan 03-04
- `scripts/validators/links.py` — owned by parallel sibling plan 03-04
- `scripts/validate.py` master CLI — already wired in Wave 1; no changes needed
- `tests/fixtures/missing-provenance/` — schema-layer rule (re-asserted in `schema.py`), not a Wave-2 deliverable

## Self-Check: PASSED

Created/modified files exist:
- `scripts/validators/ids.py` — FOUND (124 insertions, 7 deletions in commit `1273ba9`)
- `scripts/validators/provenance.py` — FOUND (134 insertions, 9 deletions in commit `48c484e`)

Commits exist on branch:
- `1273ba9` — feat(03-03): ids.py — URI format + type-prefix-mismatch validator
- `48c484e` — feat(03-03): provenance.py — H-Darrieus + pending-gate + schema_version

---
phase: 03-validators-ci-active
plan: 04
subsystem: validators
tags: [validators, cross-record, relations, links, prov-06, supersession]
requires:
  - 03-01 (Wave-1 stub modules + ctx['by_id'] indexing in scripts/validate.py)
  - 03-02 (invalid fixture corpus including broken-relation-subject /
           broken-relation-object / broken-source-ref directories)
provides:
  - relations.subject-not-found rule (alias: relations.broken-subject)
  - relations.object-not-found rule (alias: relations.broken-object)
  - relations.supersession-incomplete rule
  - relations.supersession-target-not-found rule
  - links.broken-source-ref rule (PROV-06)
  - links.source-not-document rule (PROV-06)
  - links.supersession-cycle rule (Pitfall #6 acyclicity)
  - links._detect_cycle(graph, start) helper (importable per VALIDATION.md)
affects:
  - scripts/validate.py master CLI dispatch (no code change — stubs replaced
    in-place; the dispatch loop already passed **ctx to both modules)
tech-stack:
  added: []
  patterns:
    - "ctx['by_id'] corpus index for O(1) cross-record URI resolution"
    - "Per-module validator pattern (one rule family per file)"
    - "Defensive tuple/dict unwrap for by_id values to tolerate test + CLI shapes"
key-files:
  created: []
  modified:
    - scripts/validators/relations.py
    - scripts/validators/links.py
decisions:
  - "Emit BOTH canonical rule (relations.subject-not-found) AND alias
    (relations.broken-subject) so VALIDATION.md's greppable contract for the
    alias name is satisfied without breaking the plan's canonical rule names"
  - "Place supersession existence/resolution rules in relations.py and
    supersession cyclicity in links.py — one rule per module preserves the
    five-validator topology in scripts/validate.py without overloading either"
  - "Accept relation-shaped records by EITHER discriminator type OR by
    structural shape (subject+object string fields). Covers both real
    ontology records and bare-shape inline test cases per plan acceptance"
metrics:
  duration: ~25 min
  completed: 2026-05-03
  commits:
    - df6cdfc feat(03-04): relations validator — subject/object resolution + supersession integrity
    - 9af06c5 feat(03-04): links validator — source.document_id resolution + supersession-cycle (PROV-06)
---

# Phase 3 Plan 04: Cross-Record Validators (relations + links) Summary

Wave-2 fill-in for the two validators that need a corpus-level index: relation
subject/object URI resolution, source.document_id resolution (PROV-06), and
supersession-chain integrity (existence + acyclicity, Pitfall #6). Replaces
Wave-1 `return []` stubs with real implementations against the stable
`validate_record(path, record, **ctx)` interface established by plan 03-01.

## What landed

### `scripts/validators/relations.py`

Cross-record relation rules + entity-level supersession existence checks.
Reads `ctx['by_id']` (the corpus index built by `scripts/validate.py` and
`tests/conftest.py`) to answer "does this URI resolve to any loaded record?".

| Rule | Trigger | Severity |
|------|---------|----------|
| `relations.subject-not-found` | relation `subject` URI not in `by_id` | error |
| `relations.broken-subject` (alias) | same as above | error |
| `relations.object-not-found` | relation `object` URI not in `by_id` | error |
| `relations.broken-object` (alias) | same as above | error |
| `relations.supersession-incomplete` | `status == "superseded"` AND no `superseded_by` | error |
| `relations.supersession-target-not-found` | `status == "superseded"` AND `superseded_by` not in `by_id` | error |

A record is "relation-shaped" if (a) it declares one of the 16 known relation
discriminator types (`part_of`, `cites`, `supersedes`, etc.) OR (b) it has
both `subject` and `object` string fields. Both rules can fire on the same
record (broken subject AND broken object simultaneously) — no short-circuit.

### `scripts/validators/links.py`

PROV-06 source-citation cross-record validator + supersession-chain
acyclicity check.

| Rule | Trigger | Severity |
|------|---------|----------|
| `links.broken-source-ref` | `source.document_id` not in `by_id` | error |
| `links.source-not-document` | `source.document_id` resolves but resolved record's `type != "Document"` | error |
| `links.supersession-cycle` | record has `superseded_by` AND chain via `by_id` revisits a node | error |

`_detect_cycle(graph: dict, start: Any) -> bool` is exposed as a module-level
helper because VALIDATION.md's parametrised test imports it directly:

```python
from scripts.validators.links import _detect_cycle
assert _detect_cycle({'a':'b','b':'a'}, 'a') == True
assert _detect_cycle({'a':'b','b':None}, 'a') == False
```

It walks `graph[current] -> next` until either `current` is None / missing
from graph (return False — chain exits cleanly) or `current` is already in
the visited set (return True — cycle).

## ctx['by_id'] indexing contract

`scripts/validate.py` already builds:

```python
ctx['by_id'] = {
    rec.get("id"): (path, rec)
    for path, rec in records
    if isinstance(rec, dict) and isinstance(rec.get("id"), str)
}
```

Both validators in this plan accept either `(path, record)` tuples (CLI
shape) or bare `record` dicts (test shape) — `_unwrap_record()` in links.py
normalises both. This makes the two validators independently importable AND
trivially mockable (`by_id={'uri': {'type': 'Document'}}` works in unit
tests without a path tuple).

## Verification

| Gate | Command | Result |
|------|---------|--------|
| Valid corpus stays clean | `python scripts/validate.py tests/fixtures/valid/` | 0 errors / 0 warnings across 11 records |
| Plan Task 1 verify | inline `python -c "..."` from plan 03-04 Task 1 | PLAN-VERIFY OK |
| Preamble Task 1 alias verify | inline assertion on `relations.broken-subject` / `.broken-object` | PREAMBLE-VERIFY OK |
| Plan Task 2 verify | inline `python -c "..."` from plan 03-04 Task 2 | PLAN-VERIFY OK |
| `_detect_cycle` inline test | from VALIDATION.md | PREAMBLE-VERIFY OK |
| Greppability: `links.broken-source-ref` | `grep` | OK |
| Greppability: `relations.subject-not-found` | `grep` | OK |
| Greppability: `relations.supersession-target-not-found` | `grep` | OK |
| Greppability: `PROV-06` cited in links.py | `grep` | OK |
| Invalid fixture: broken-relation-subject loaded directly | corpus index from valid fixtures, validator fired | `relations.subject-not-found` emitted (OK) |
| Invalid fixture: broken-relation-object loaded directly | corpus index from valid fixtures, validator fired | `relations.object-not-found` emitted (OK) |
| Invalid fixture: broken-source-ref loaded directly | corpus index from valid fixtures, validator fired | `links.broken-source-ref` emitted (OK) |

## Deviations from Plan

### Auto-additions (Rule 2 — missing critical functionality)

**1. [Rule 2] Added rule aliases (`relations.broken-subject` / `relations.broken-object`).**
- **Found during:** Reading the plan preamble vs. canonical PLAN.md
- **Issue:** PLAN.md `<behavior>` says `relations.subject-not-found`;
  VALIDATION.md test row + plan execution preamble inline test both assert
  `relations.broken-subject`. Both names are required by greppable
  acceptance criteria.
- **Fix:** Emit BOTH rules side-by-side (canonical + alias) when subject
  fails to resolve; same for object. Aliases carry a "(alias of …)"
  message so error output remains self-documenting.
- **Files modified:** `scripts/validators/relations.py`
- **Commit:** df6cdfc

**2. [Rule 2] Added `links.supersession-cycle` rule + exported `_detect_cycle`.**
- **Found during:** Reading VALIDATION.md row "VAL-02 (links / supersession)"
- **Issue:** Plan PLAN.md `<behavior>` for Task 2 only covered source-ref
  rules, but VALIDATION.md mandates `_detect_cycle` is importable from
  links.py and used to detect supersession cycles per Pitfall #6.
- **Fix:** Implemented `_detect_cycle(graph, start)` per the inline-test
  contract; added `links.supersession-cycle` rule that builds a flat
  supersession graph from by_id and walks from the current record's id.
  Existence/resolution remain in relations.py (one rule per module).
- **Files modified:** `scripts/validators/links.py`
- **Commit:** 9af06c5

### Out-of-scope items NOT touched

- `scripts/validators/loader.py`'s deliberate skip of `fixtures/invalid/`
  paths means the master CLI cannot directly emit errors when pointed at
  `tests/fixtures/invalid/<rule>/`. The plan's canonical acceptance gates
  use Python inline calls (which DO work) rather than the CLI, so this
  pre-existing loader behavior was left alone. Logged as a deferred item
  for plan 03-05/03-06 (Wave 3 pytest will exercise invalid fixtures via
  parametrisation, not via the master CLI's dirwalker).
- `scripts/validators/ids.py` and `provenance.py` — those are plan 03-03's
  scope (parallel sibling). Untouched.
- `scripts/validate.py` master CLI dispatch — no change needed; the
  `**ctx` argument plumbing was already correct from plan 03-01.

## Threat Flags

None. Validators are pure-Python file-readers with no network surface, no
auth path, no schema-changes-at-trust-boundary. The `_detect_cycle` helper
takes a bounded walk through an in-memory dict, no eval / dynamic dispatch.

## Self-Check: PASSED

- `scripts/validators/relations.py` — FOUND
- `scripts/validators/links.py` — FOUND
- `df6cdfc` (relations commit) — FOUND in `git log`
- `9af06c5` (links commit) — FOUND in `git log`
- Valid corpus passes `scripts/validate.py` — 0 errors
- All inline plan + preamble tests pass

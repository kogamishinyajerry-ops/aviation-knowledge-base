---
phase: 03-validators-ci-active
plan: 02
subsystem: validators
tags:
  - fixtures
  - validators
  - phase-3
  - wave-1
dependency_graph:
  requires:
    - "ontology/_meta.schema.json (provenance/confidence/source $defs)"
    - "ontology/schemas/entity.expert-note.schema.json"
    - "ontology/schemas/entity.aircraft-model.schema.json"
    - "ontology/schemas/relation.cites.schema.json"
    - "ontology/schemas/relation.part-of.schema.json"
    - "instances/_pending/README.md (H-Darrieus + promotion gate definition)"
  provides:
    - "tests/fixtures/invalid/ — 12 fixtures + traceability README"
    - "Wave-3 pytest parametrisation source (this SUMMARY drives plan 03-05)"
  affects:
    - "scripts/validators/{schema,ids,provenance,relations,links}.py — Wave-2 validators must catch these fixtures"
tech_stack:
  added: []
  patterns:
    - "failure-mode-per-fixture: each invalid YAML isolates exactly one rule violation so pytest can attribute errors unambiguously"
    - "directory-name-as-rule-anchor: parent dir name matches the rule pytest will assert"
    - "path-based validation marker: /_pending/ subpath required for PROV-05 pending-gate fixture"
    - "YAML-parseable but schema-invalid: fixtures must load as YAML to reach the validator"
key_files:
  created:
    - "tests/fixtures/invalid/missing-provenance/expert-note_no-provenance.yaml"
    - "tests/fixtures/invalid/missing-schema-version/aircraft-model_no-schema-version.yaml"
    - "tests/fixtures/invalid/bad-uri-format/aircraft-model_bad-uri.yaml"
    - "tests/fixtures/invalid/bad-internal-id/relation-cites_bad-id.yaml"
    - "tests/fixtures/invalid/h-darrieus-rejected/expert-note_ai-extracted-high-conf-no-reviewer.yaml"
    - "tests/fixtures/invalid/h-darrieus-empty-reviewer/expert-note_high-conf-empty-string-reviewer.yaml"
    - "tests/fixtures/invalid/pending-not-hybrid-reviewed/_pending/expert-note_pending-still-ai-extracted.yaml"
    - "tests/fixtures/invalid/broken-source-ref/expert-note_dangling-document-id.yaml"
    - "tests/fixtures/invalid/broken-relation-subject/cites_subject-not-found.yaml"
    - "tests/fixtures/invalid/broken-relation-object/part-of_object-not-found.yaml"
    - "tests/fixtures/invalid/old-schema-version/aircraft-model_pre-0-1-0.yaml"
    - "tests/fixtures/invalid/empty-rationale/expert-note_short-rationale.yaml"
    - "tests/fixtures/invalid/README.md"
  modified: []
decisions:
  - "Reused a single fixture skeleton (Person URI jane-doe@1, Document URI fixture-source-doc@1, retrieval URL pattern, ISO timestamp 2026-05-03T00:00:00Z) across all 12 fixtures so the only varying axis is the field that triggers the rule under test."
  - "h-darrieus-rejected/ uses score: 0.90 (ADR-005 strict-> band, well clear of the 0.85 boundary) rather than 0.86, to avoid float-precision arguments and to match the planner's >0.85 verify regex."
  - "pending-not-hybrid-reviewed/_pending/ keeps confidence.score == 0.50 so the H-Darrieus rule does NOT also fire on this fixture — pending-gate is isolated from H-Darrieus."
  - "bad-internal-id/ implements the violation as a malformed `subject` URI on a cites relation (per planner instruction; current schemas do not declare a `legacy_internal_id` field referencing `$defs/internalId`). Documented as misnomer-by-design in the README."
  - "old-schema-version/ uses 0.0.1 (v0.1.0 - 1) which fires as a WARNING in v0.1.0 — the strict-reject branch activates only after ontology bumps to 0.2.0+. Documented in fixture comment + README."
metrics:
  duration_min: 12
  completed_at: "2026-05-03"
  tasks_completed: 1
  fixtures_created: 12
  files_created: 13
---

# Phase 3 Plan 02: Invalid Fixture Corpus — Summary

12 invalid YAML fixtures + 1 traceability README created. Each fixture isolates exactly one failure mode the Phase 3 validators must catch. This is the truth set Wave-3 pytest (plan 03-05) will parametrise against.

## What Was Built

### Fixture-to-Rule Mapping (Wave-3 pytest parametrisation source)

| # | Fixture                                                                                            | Failure mode                                  | Expected `rule` value(s)                          | REQ-ID  | Severity   |
| - | -------------------------------------------------------------------------------------------------- | --------------------------------------------- | ------------------------------------------------- | ------- | ---------- |
| 1 | `missing-provenance/expert-note_no-provenance.yaml`                                                | required provenance block missing             | `schema`                                          | PROV-01 | error      |
| 2 | `missing-schema-version/aircraft-model_no-schema-version.yaml`                                     | required schema_version field missing         | `schema`                                          | VER-03  | error      |
| 3 | `bad-uri-format/aircraft-model_bad-uri.yaml`                                                       | top-level id is "not-a-valid-uri"             | `schema` + `ids.uri-format` (dual-fire)           | D-23    | error      |
| 4 | `bad-internal-id/relation-cites_bad-id.yaml`                                                       | subject URI uses underscores `comp:Bad_Underscore_ID` | `schema` + `ids.uri-format` (dual-fire)   | D-23    | error      |
| 5 | `h-darrieus-rejected/expert-note_ai-extracted-high-conf-no-reviewer.yaml`                          | ai_extracted + score 0.90 + no reviewer       | `provenance.h-darrieus`                           | PROV-04 | error      |
| 6 | `h-darrieus-empty-reviewer/expert-note_high-conf-empty-string-reviewer.yaml`                       | ai_extracted + score 0.90 + reviewer ""       | `provenance.h-darrieus` + `schema` (dual-fire)    | PROV-04 | error      |
| 7 | `pending-not-hybrid-reviewed/_pending/expert-note_pending-still-ai-extracted.yaml`                 | path contains `/_pending/` + method != hybrid_reviewed | `provenance.pending-gate`                | PROV-05 | error      |
| 8 | `broken-source-ref/expert-note_dangling-document-id.yaml`                                          | source.document_id not in corpus              | `links.broken-source-ref`                         | PROV-06 | error      |
| 9 | `broken-relation-subject/cites_subject-not-found.yaml`                                             | cites.subject URI not in corpus               | `relations.subject-not-found`                     | VAL-01  | error      |
| 10| `broken-relation-object/part-of_object-not-found.yaml`                                             | part_of.object URI not in corpus              | `relations.object-not-found`                      | VAL-01  | error      |
| 11| `old-schema-version/aircraft-model_pre-0-1-0.yaml`                                                 | schema_version "0.0.1" (older than 0.1.0)     | `provenance.schema-version-mismatch`              | VER-03  | **warning**|
| 12| `empty-rationale/expert-note_short-rationale.yaml`                                                 | confidence.rationale "ok" (2 chars < 20)      | `schema`                                          | PROV-02 | error      |

### Skeleton template (constant across fixtures)

To guarantee single-failure-mode isolation, every fixture except where explicitly varied uses:

- `provenance.method: human` (so PROV-04/PROV-05 don't accidentally fire)
- `provenance.actor: aviationkb://person/jane-doe@1`
- `provenance.actor_role: "systems-engineer"` (or `"ai-operator"` for ai_extracted cases)
- `provenance.created_at: "2026-05-03T00:00:00Z"`
- `confidence.score: 0.7` to `0.95` and `confidence.rationale` ≥ 20 chars (so empty-rationale/ doesn't accidentally fire elsewhere)
- `source.document_id: aviationkb://document/fixture-source-doc@1`
- `source.locator: { page: 1 }`
- `source.retrieval: { url: "https://example.invalid/fixtures/<dir>", retrieved_at: "2026-05-03T00:00:00Z" }`

### Traceability README (`tests/fixtures/invalid/README.md`)

The README maps each fixture directory to its expected rule + REQ-ID. It also documents:

- The single-failure-mode rule (one fixture = one violation)
- The PROV-05 path requirement (file MUST live under `_pending/` subpath)
- The H-Darrieus boundary case (strict `>` per ADR-005; 0.85 passes, 0.86+ fails)
- Why `bad-internal-id/` is a misnomer-by-design (planner intent — directory name is canonical)
- Why `old-schema-version/` fires as warning, not error, in v0.1.0
- The `iter_instance_files()` exclusion rule keeping these fixtures out of the default `validate.py` walk

## Verification — Acceptance Gates

All 5 plan-level gates pass cleanly from the worktree root:

```text
$ find tests/fixtures/invalid -name '*.yaml' | wc -l
      12                                              ← OK (==12)

$ find tests/fixtures/invalid/pending-not-hybrid-reviewed/_pending -name '*.yaml' | wc -l
       1                                              ← OK (==1, PROV-05 path requirement)

$ test -f tests/fixtures/invalid/README.md            ← OK
$ grep -q "PROV-04" tests/fixtures/invalid/README.md  ← OK
$ grep -q "PROV-05" tests/fixtures/invalid/README.md  ← OK
$ grep -q "PROV-06" tests/fixtures/invalid/README.md  ← OK
```

In addition, all 12 fixtures parse as valid YAML (round-trip via `ruamel.yaml.safe_load`):

```text
$ python3 -c "import glob; from ruamel.yaml import YAML; ..."
parsing 12 fixtures...
all 12 fixtures parsed cleanly as YAML
```

The H-Darrieus boundary is correctly tripped:

- `score: 0.90` (in `h-darrieus-rejected/`) — strictly > 0.85 ✓
- `method: ai_extracted` ✓
- No `reviewer:` YAML key (verified via `grep -E "^[[:space:]]+reviewer:"`) ✓

## Deviations from Plan

None — plan executed exactly as written. The planner's verify regex `grep -A2 "method: ai_extracted"` is a known false-negative (it scans only 2 lines after `method:`, but the `score:` field lives under a separate `confidence:` block several lines down). The semantic invariants the regex was *trying* to enforce — score ∈ (0.85, 1.0] AND no reviewer key — are both satisfied by the fixture (verified via separate, more precise greps documented above). Wave-3 pytest will attribute the rule via `provenance.validate_record(record)` directly, not via this regex, so the planner regex is not load-bearing.

## Authentication Gates

None.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes were introduced. All fixtures live under `tests/fixtures/invalid/` and are explicitly excluded from `iter_instance_files()` per plan 03-01 contract.

## Known Stubs

None. Every fixture is a complete YAML record (the only "missing" pieces are intentional — they ARE the failure mode under test, never accidental stubs).

## Self-Check: PASSED

- [x] All 13 created files exist on disk (`ls tests/fixtures/invalid/**/*.yaml` returns 12, `tests/fixtures/invalid/README.md` exists)
- [x] Commit `5762397` exists on branch (`git log --oneline -1` returns `5762397 feat(03-02): add 12 invalid fixtures + traceability README`)
- [x] All plan acceptance gates pass (count==12, _pending count==1, README references PROV-04/PROV-05/PROV-06)
- [x] H-Darrieus boundary semantically correct (score 0.90, method ai_extracted, no reviewer key)
- [x] PROV-05 fixture lives at the canonical `pending-not-hybrid-reviewed/_pending/` path

## Next Steps for Wave-2 / Wave-3 Plans

- **Plan 03-03 (ids + provenance validators)**: must catch fixtures 3, 4, 5, 6, 7, 11.
- **Plan 03-04 (relations + links validators)**: must catch fixtures 8, 9, 10.
- **Plan 03-05 (pytest parametrisation)**: walks `tests/fixtures/invalid/`, asserts each fixture's expected rule from the table above, including documented dual-fire cases.
- **Plan 03-06 (CI wiring)**: ensures `pytest tests/ -q` runs in CI on every PR.

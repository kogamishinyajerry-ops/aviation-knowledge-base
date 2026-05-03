# Invalid Fixture Corpus — Failure-Mode-Per-Fixture

Each subdirectory isolates exactly ONE rule violation. Wave-3 pytest walks
this tree and asserts that each fixture triggers a `ValidationError` whose
`rule` matches the directory name (or the documented dual-fire pattern below).

| Fixture dir                      | Failure mode                                      | Rule(s) expected                              | REQ-ID                       |
| -------------------------------- | ------------------------------------------------- | --------------------------------------------- | ---------------------------- |
| `missing-provenance/`            | required field absent                             | `schema`                                      | PROV-01 (Phase 2 enforced)   |
| `missing-schema-version/`        | required field absent                             | `schema`                                      | VER-03                       |
| `bad-uri-format/`                | id pattern violation                              | `schema`, `ids.uri-format`                    | D-23                         |
| `bad-internal-id/`               | subject URI pattern violation                     | `schema`, `ids.uri-format`                    | D-23                         |
| `h-darrieus-rejected/`           | `ai_extracted` + score > 0.85 + no reviewer       | `provenance.h-darrieus`                       | **PROV-04**                  |
| `h-darrieus-empty-reviewer/`     | same as above with `reviewer: ""`                 | `provenance.h-darrieus` (+ `schema`)          | **PROV-04**                  |
| `pending-not-hybrid-reviewed/`   | `_pending/` tree with method != `hybrid_reviewed` | `provenance.pending-gate`                     | **PROV-05**                  |
| `broken-source-ref/`             | `source.document_id` not in corpus                | `links.broken-source-ref`                     | **PROV-06**                  |
| `broken-relation-subject/`       | `relation.subject` URI not in corpus              | `relations.subject-not-found`                 | VAL-01                       |
| `broken-relation-object/`        | `relation.object` URI not in corpus               | `relations.object-not-found`                  | VAL-01                       |
| `old-schema-version/`            | `schema_version` older than N-1                   | `provenance.schema-version-mismatch` (warning)| VER-03                       |
| `empty-rationale/`               | `confidence.rationale` < 20 chars                 | `schema`                                      | PROV-02                      |

## Notes for the validator authors

- **Single-failure rule**: each fixture is valid in *every* respect except the one
  rule it is testing. If you find a fixture that violates two rules, that is a
  bug — open a PR adjusting the fixture so Wave-3 pytest can attribute errors
  unambiguously. Documented dual-fire cases (`bad-uri-format/`, `bad-internal-id/`,
  `h-darrieus-empty-reviewer/`) are the only exceptions and are explicit above.
- **PROV-05 path requirement**: the pending-gate fixture intentionally lives
  under a `_pending/` subpath
  (`pending-not-hybrid-reviewed/_pending/expert-note_pending-still-ai-extracted.yaml`).
  The validator's `_pending/` detection is path-based; without the subpath, the
  rule cannot fire. Do not move the file out of `_pending/`.
- **H-Darrieus boundary case (ADR-005)**: the rule uses strict `>` not `>=`.
  Score 0.85 is **PASS**, score 0.86+ is **FAIL**. The `h-darrieus-rejected/`
  fixture uses 0.90 to land safely inside the FAIL band; the `h-darrieus-empty-reviewer/`
  fixture uses the same 0.90.
- **`bad-internal-id/` is a misnomer-by-design**: the directory name was chosen
  by the planner (plan 03-05 maps it to `{"ids.uri-format"}`); the actual failure
  mode is a malformed `subject` URI on a `cites` relation, since none of the
  current schemas declare a `legacy_internal_id` field referencing
  `$defs/internalId`. Do **not** rename the directory — Wave-3 pytest looks it up
  by name.
- **`old-schema-version/`** fires as a **warning** in v0.1.0, not an error. The
  strict-reject (older than N-1) activates once `ontology/VERSION` bumps to
  v0.2.0+ and v0.0.x records become "older than N-1".

## Excluded from default `validate.py` walk

These fixtures are **excluded** from the default `validate.py` walk by
`scripts/validators/loader.py:iter_instance_files` (which skips
`fixtures/invalid/`). They are loaded explicitly only by pytest (plan 03-05).
This keeps `python scripts/validate.py instances/` green even though the
invalid corpus is intentionally broken.

## See also

- `.planning/phases/03-validators-ci-active/03-02-PLAN.md` — the planner doc
  that produced this corpus.
- `.planning/phases/03-validators-ci-active/03-VALIDATION.md` — Phase 3
  validation strategy + per-task verification map.
- `.planning/decisions/ADR-005-provenance-enum.md` — full provenance method
  enum + H-Darrieus rule definition.
- `instances/_pending/README.md` — `_pending/` quarantine + promotion gate
  contract (D-17).

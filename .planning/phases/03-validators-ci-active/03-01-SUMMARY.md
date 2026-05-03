---
phase: 03-validators-ci-active
plan: 01
subsystem: validation
tags: [validators, jsonschema, ruamel-yaml, pytest, fixtures, draft-2020-12]
requires: [02-01-SUMMARY, 02-02-SUMMARY, 02-03-SUMMARY]
provides:
  - scripts/validate.py
  - scripts/validators/{errors,loader,schema,ids,provenance,relations,links}.py
  - tests/fixtures/valid/ (11 records)
  - requirements-dev.txt
  - pyproject.toml [tool.pytest.ini_options]
  - tests/conftest.py (by_id fixture)
affects:
  - ontology/schemas/entity.base.schema.json (fix: removed unevaluatedProperties)
  - ontology/schemas/relation.base.schema.json (fix: removed unevaluatedProperties)
  - ontology/CHANGELOG.md (post-release patch entry)
tech-stack:
  added: [jsonschema>=4.21, ruamel.yaml>=0.18, pytest>=8.0, referencing>=0.34]
  patterns: [draft-2020-12-with-referencing-Registry, allOf-leaf-only-unevaluatedProperties]
key-files:
  created:
    - scripts/validate.py
    - scripts/validators/__init__.py
    - scripts/validators/errors.py
    - scripts/validators/loader.py
    - scripts/validators/schema.py
    - scripts/validators/ids.py
    - scripts/validators/provenance.py
    - scripts/validators/relations.py
    - scripts/validators/links.py
    - requirements-dev.txt
    - pyproject.toml
    - tests/conftest.py
    - tests/fixtures/valid/entities/aircraft-model_boeing-737-max-8.yaml
    - tests/fixtures/valid/entities/aircraft-system_b737max-fadec.yaml
    - tests/fixtures/valid/entities/document_far-25-1309.yaml
    - tests/fixtures/valid/entities/expert-note_canonical-example.yaml
    - tests/fixtures/valid/entities/regulation-clause_far-25-1309-active.yaml
    - tests/fixtures/valid/entities/regulation-clause_far-25-1309-superseded.yaml
    - tests/fixtures/valid/entities/person_jane-reviewer.yaml
    - tests/fixtures/valid/relations/cites_note-to-far25.yaml
    - tests/fixtures/valid/relations/supersedes_far-clause-chain.yaml
    - tests/fixtures/valid/relations/part-of_fadec-of-b737max.yaml
    - tests/fixtures/valid/_pending/expert-note_pending-hybrid-reviewed.yaml
  modified:
    - ontology/schemas/entity.base.schema.json
    - ontology/schemas/relation.base.schema.json
    - ontology/CHANGELOG.md
decisions:
  - Public validator API frozen at validate_record(path, record, **ctx) -> list[ValidationError] for Wave-2 parallelism
  - schema.py uses referencing.Registry (jsonschema 4.18+ API) for $ref resolution; both bare-filename and parent-relative ("../_meta.schema.json") keys registered
  - Entity/relation base schemas no longer set unevaluatedProperties (moved to leaf-only per JSON Schema 2020-12 scope rules)
  - pyproject.toml + tests/conftest.py added per 03-VALIDATION.md Wave-0 deliverables (not in plan files_modified — Rule 2 deviation)
metrics:
  duration: ~25 minutes
  completed: 2026-05-03
  tasks_total: 2
  tasks_completed: 2
  fixtures_added: 11
  validators_shipped: 5
  validators_real: 1 (schema.py)
  validators_stubbed: 4 (ids/provenance/relations/links — Wave 2 fills in)
---

# Phase 3 Plan 01: Validators bootstrap + valid corpus Summary

**One-liner:** Stood up the validator package public API + Draft-2020-12 schema validator with `referencing.Registry` for `$ref` resolution, shipped four Wave-2 stubs returning `[]`, and authored the 11-record valid fixture corpus that every later wave validates against. Caught and fixed a latent Phase-2 schema bug (misplaced `unevaluatedProperties: false` on intermediate composition bases) that prevented any instance from validating.

## What landed

### Task 1 — Validator package skeleton + master CLI

| Artefact | Role |
|---|---|
| `scripts/validators/errors.py` | `ValidationError` frozen dataclass with `format()` helper for CLI output |
| `scripts/validators/loader.py` | `load_yaml` (ruamel.yaml safe), `iter_instance_files` (excludes `fixtures/invalid/`), `schema_path_for_record` (PascalCase entity → `entity.<kebab>.schema.json`; snake_case relation → `relation.<kebab>.schema.json`; `CFDMethod` special-cased to `cfd-method`) |
| `scripts/validators/schema.py` | Real Draft-2020-12 validator. Builds a `referencing.Registry` populated with every `*.schema.json` keyed by canonical `$id`, bare filename, and `./<filename>` so leaf-schema `$ref: "entity.base.schema.json"` and `$ref: "../_meta.schema.json#/$defs/baseFields"` both resolve. |
| `scripts/validators/{ids,provenance,relations,links}.py` | Wave-2 stubs. Each accepts `(path, record, **ctx)` and returns `[]`. The `**ctx` absorbs `by_id` so the VAL-02 contract test passes today. Wave-2 plans 03-03 / 03-04 fill these in without touching the dispatch loop. |
| `scripts/validate.py` | argparse CLI. Pre-loads every record into `(path, dict)` tuples, builds `ctx = {records, by_id, repo_root}`, dispatches all five validators, prints aggregated errors via `ValidationError.format()`, exits non-zero if any `severity == 'error'` was emitted. |
| `requirements-dev.txt` | `jsonschema>=4.21,<5`, `ruamel.yaml>=0.18,<1`, `pytest>=8.0,<9`, `referencing>=0.34,<1` |
| `pyproject.toml` | `[tool.pytest.ini_options]` only — no build backend (project ships YAML/MD, not a pip package) |
| `tests/conftest.py` | session-scoped `repo_root`, `valid_fixtures_dir`, and `by_id` fixtures. `by_id` walks `tests/fixtures/valid/` via `iter_instance_files` and indexes records by their string `id` field — the corpus index Wave-3 parametrised tests will exercise relations/links rules against |

**Public API frozen for Wave 2:**
```python
def validate_record(path: Path, record: Any, **ctx) -> list[ValidationError]
```
`schema.validate_record` accepts the optional `schemas_dir` kwarg; the four stubs accept arbitrary `**ctx` (notably `by_id`). The `validate.py` dispatch loop calls schema with `(path, record)` only and the stubs with `(path, record, **ctx)` — so Wave-2 implementations can read `ctx['by_id']`, `ctx['records']`, `ctx['repo_root']` without modifying the CLI.

### Task 2 — Valid fixture corpus (11 records)

| Record | URI | Role in corpus |
|---|---|---|
| Document FAR-25-1309 | `aviationkb://document/far-25-1309@1` | Every other fixture's `source.document_id` resolves here. Required by Phase 4 broken-ref test. |
| Person Jane Reviewer | `aviationkb://person/jane-reviewer@1` | Every fixture's `provenance.actor` (and the _pending fixture's `provenance.reviewer`). |
| AircraftModel Boeing 737 MAX 8 | `aviationkb://aircraft-model/boeing-737-max-8@1` | Anchors part_of chain. |
| AircraftSystem B737-MAX FADEC | `aviationkb://aircraft-system/b737max-fadec@1` | Subject of part_of relation. |
| RegulationClause active | `aviationkb://regulation-clause/far-25-1309-active@1` | Head of supersession chain (`status: active`). |
| RegulationClause superseded | `aviationkb://regulation-clause/far-25-1309-superseded@1` | Tail of supersession chain (`status: superseded`, `superseded_by: → active`). |
| ExpertNote canonical | `aviationkb://expert-note/canonical-example@1` | Worked example from AI 接力开发指南; `provenance.method: human`. |
| ExpertNote _pending | `aviationkb://expert-note/pending-hybrid-reviewed@1` | Lives in `tests/fixtures/valid/_pending/`; `provenance.method: hybrid_reviewed` + non-empty reviewer + reviewed_at — the canonical promotion-eligible state. |
| relation cites | `aviationkb://cites/note-to-far25@1` | ExpertNote cites RegulationClause active. |
| relation supersedes | `aviationkb://supersedes/far-clause-chain@1` | Pitfall #6 forward pointer. |
| relation part_of | `aviationkb://part-of/fadec-of-b737max@1` | Composition relation. |

All eleven pass `python scripts/validate.py tests/fixtures/valid/` with `0 error(s), 0 warning(s) across 11 record(s).`

## Verification

| Acceptance gate | Command | Result |
|---|---|---|
| Validator package imports | `python -c "from scripts.validate import main; from scripts.validators import schema, ids, provenance, relations, links; assert callable(main)"` | exit 0 |
| Stubs accept `by_id` | `python -c "from scripts.validators import ids; ids.validate_record('', {}, by_id={})"` | returns `[]` |
| schema.py uses Draft202012Validator | `grep -q "Draft202012Validator" scripts/validators/schema.py` | match |
| ValidationError class | `grep -q "class ValidationError" scripts/validators/errors.py` | match |
| Master CLI on corpus | `python scripts/validate.py tests/fixtures/valid/` | exit 0, "0 error(s), 0 warning(s) across 11 record(s)" |
| Single-file invocation | `python scripts/validate.py tests/fixtures/valid/entities/aircraft-model_boeing-737-max-8.yaml` | exit 0, "0 error(s), 0 warning(s) across 1 record(s)" |
| Fixture count | `find tests/fixtures/valid -name '*.yaml' \| wc -l` | 11 |
| No `ai_extracted` in valid tree | `grep -l "ai_extracted" tests/fixtures/valid/ -r` | empty (the _pending fixture uses `hybrid_reviewed`) |
| supersession chain present | `grep -l "status: superseded" tests/fixtures/valid/entities/regulation-clause_far-25-1309-superseded.yaml` | match |
| supersession `superseded_by` set | `grep -l "superseded_by" tests/fixtures/valid/entities/regulation-clause_far-25-1309-superseded.yaml` | match |
| schema_version on every fixture | `grep -L 'schema_version: "0.1.0"' tests/fixtures/valid/**/*.yaml` | empty |
| pytest collection | `pytest --collect-only -q` | exit 5 (no tests yet — expected; Wave 3 plan 03-05 adds them) |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] `unevaluatedProperties: false` misplaced on base composition schemas**

- **Found during:** Task 2 — first instance-validation run.
- **Issue:** All 11 fixtures failed schema validation with errors of the form `Unevaluated properties are not allowed ('confidence', 'i18n', 'id', 'provenance', 'schema_version', 'source', 'version' were unexpected)`. The composition pattern `allOf: [{$ref: "../_meta.schema.json#/$defs/baseFields"}]` was correct, but `entity.base.schema.json` and `relation.base.schema.json` each set `unevaluatedProperties: false`. Per JSON Schema 2020-12, that keyword evaluates only against annotations in its own scope. When the leaf schema referenced base via `allOf`, base's `unevaluatedProperties` saw the leaf's own properties (manufacturer, model_designation, etc.) as "unevaluated" because they were defined OUTSIDE the base scope, and rejected them. Phase 2 only ran `check-jsonschema --check-metaschema`, which validates that the schema document is itself a valid JSON Schema — it does NOT exercise instance validation, so the defect went undetected.
- **Fix:** Removed `unevaluatedProperties: false` from `entity.base.schema.json` and `relation.base.schema.json`. All 20 entity-leaf and 16 relation-leaf schemas KEEP their `unevaluatedProperties: false`, so unknown-property rejection still works at the level a user actually validates against. Updated both base schemas' `description` fields to document the constraint. Schema `$id` values unchanged → no consumer impact.
- **Files modified:** `ontology/schemas/entity.base.schema.json`, `ontology/schemas/relation.base.schema.json`, `ontology/CHANGELOG.md` (post-release patch entry per CLAUDE.md auditability requirement)
- **Commit:** `4c205d9` (fix(03-01): drop unevaluatedProperties from base composition schemas)
- **Verification:** post-fix run of `python scripts/validate.py tests/fixtures/valid/` exits 0 with "0 error(s), 0 warning(s) across 11 record(s)".

**2. [Rule 2 — Missing critical functionality] `pyproject.toml` and `tests/conftest.py` added beyond plan files_modified**

- **Found during:** Task 1 — cross-checking plan against `03-VALIDATION.md` Wave-0 deliverables.
- **Issue:** The plan's `files_modified` frontmatter does not list `pyproject.toml` or `tests/conftest.py`, but `03-VALIDATION.md` explicitly lists both as Wave-0 deliverables (it says "tests/conftest.py — shared fixtures: by_id corpus index... created in plan 03-01"). Without them, Wave-3 plan 03-05 (`tests/test_validators.py`) cannot collect or use the `by_id` fixture and `pytest` has no config root.
- **Fix:** Created minimal `pyproject.toml` with `[tool.pytest.ini_options]` only (no build backend — project is YAML/MD, not a pip package) and `tests/conftest.py` exposing `repo_root`, `valid_fixtures_dir`, and `by_id` session fixtures.
- **Files added:** `pyproject.toml`, `tests/conftest.py`
- **Commit:** `cabd8f1` (feat(03-01): validator package skeleton + Draft-2020-12 schema validator + master CLI)
- **Rationale:** Better to land Wave-0 deliverables in their named plan (03-01) than defer to plan 03-05 and surprise the Wave-3 author. CLAUDE.md "Documentation: 设计文档必须适合 Claude / Codex / DeepSeek 接力" — the plan and the validation strategy doc were inconsistent on these two artefacts; honoring the validation strategy is the right call.

## Wave-2 stub-fill contract

Wave-2 plans (03-03 ids+provenance, 03-04 relations+links) MUST implement `validate_record(path: Path, record: Any, **ctx) -> list[ValidationError]` against this contract:

- `path` is the YAML record's file path (used for `_pending/`-aware path checks per PROV-05)
- `record` is the parsed Python dict from `loader.load_yaml`
- `**ctx` carries the cross-record context built by `validate.py`:
  - `ctx["by_id"]` — `dict[str, tuple[Path, dict]]` keyed by every record's URI `id` field; lookup target for relations.broken-subject, relations.broken-object, links.broken-source-ref
  - `ctx["records"]` — full list of `(path, record)` pairs (use sparingly — `by_id` is faster)
  - `ctx["repo_root"]` — `Path` to repo root (e.g. for resolving against `ontology/vocabularies/`)
- Return `[]` on success, or a list of `ValidationError(rule="<dotted-path>", severity="error"|"warning", file=str(path), message="...", pointer="<JSON-Pointer>")`
- Wave-2 plans MUST NOT modify `scripts/validate.py` or any other validator's file — the dispatch loop is frozen

Per `03-VALIDATION.md` rule names Wave-2 must implement:
- `ids.uri-format`, `ids.internal-id-format` (plan 03-03)
- `provenance.h-darrieus`, `provenance.pending-gate`, `provenance.schema-version` (plan 03-03; the last is severity=warning)
- `relations.broken-subject`, `relations.broken-object` (plan 03-04)
- `links.broken-source-ref`, `links.supersession-cycle` (plan 03-04; helper `_detect_cycle` exposed for unit test)

## Self-Check: PASSED

- All 14 created files exist in worktree (verified per file in commits cabd8f1, 1097145)
- All 3 modified files exist (entity.base, relation.base, CHANGELOG — commit 4c205d9)
- Three commits in `git log --oneline`: cabd8f1, 4c205d9, 1097145 — all on this worktree branch
- Final state: `python scripts/validate.py tests/fixtures/valid/` exits 0 with "0 error(s), 0 warning(s) across 11 record(s)"

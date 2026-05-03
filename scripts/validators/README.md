# scripts/validators/ — Aviation KB Ontology Validators

> **AI 接力开发指南** (AIH-01): This directory implements the runtime rules
> that Phase 2 schemas only documented. Read this file first if you are
> adding a new rule, debugging a CI failure, or extending the validator
> package. The 5-minute "stranger test" applies — by the end of this README
> you should know (a) where to add a new rule, (b) how to test it, and
> (c) where the CI gate lives.

## Overview

Five Python validator modules + one master CLI live here:

| Module          | Rule names                                                                                                                       | What it catches                                                                                            |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `schema.py`     | `schema`                                                                                                                         | JSON Schema Draft 2020-12 violations against each type's leaf schema (composes `_meta.schema.json`)         |
| `ids.py`        | `ids.uri-format`, `ids.type-prefix-mismatch`                                                                                     | URI / internal-ID pattern + type-segment-vs-record-type mismatch (D-23 / D-24 / D-25)                      |
| `provenance.py` | `provenance.h-darrieus`, `provenance.pending-gate`, `provenance.schema-version-mismatch`                                         | PROV-04 H-Darrieus REJECT, PROV-05 `_pending/` promotion gate, VER-03 cross-record schema_version          |
| `relations.py`  | `relations.subject-not-found`, `relations.object-not-found`, `relations.supersession-incomplete`, `relations.supersession-target-not-found` | Cross-record subject/object resolution + supersession chain integrity                                      |
| `links.py`      | `links.broken-source-ref`, `links.source-not-document`                                                                           | PROV-06 — `source.document_id` resolves to a Document entity                                               |

Master CLI: **`python scripts/validate.py [PATH ...]`** (default: `instances/`).
The CLI loads every YAML record under each PATH (recursively, skipping
`tests/fixtures/invalid/` — see `loader.iter_instance_files`), runs every
validator on each record, and exits non-zero if any `ValidationError` with
`severity == "error"` is emitted.

## Public API (stable, FROZEN)

```python
from pathlib import Path
from scripts.validators.errors import ValidationError

# Each validator module exposes:
def validate_record(path: Path, record, **ctx) -> list[ValidationError]
```

The `**ctx` dict carries cross-record state shared by all validators:

| Key         | Type                          | Provided by      | Used by                  |
| ----------- | ----------------------------- | ---------------- | ------------------------ |
| `records`   | `list[tuple[Path, dict]]`     | `validate.py`    | (rare; full corpus walk) |
| `by_id`     | `dict[str, tuple[Path,dict]]` | `validate.py`    | `relations`, `links`     |
| `repo_root` | `Path`                        | `validate.py`    | `schema` (loads schemas) |

`ValidationError` is a frozen dataclass (NOT a plain dict) defined in
`errors.py`:

```python
@dataclass(frozen=True)
class ValidationError:
    rule: str           # e.g. "ids.uri-format", "provenance.h-darrieus"
    severity: str       # "error" | "warning" — only "error" causes non-zero exit
    file: str           # repo-relative or absolute path of the offending YAML
    message: str        # human-readable description
    pointer: str | None # optional JSON Pointer into the record, e.g. "/provenance/method"

    def format(self) -> str: ...  # "[ERROR][rule] file @ pointer: message"
```

This `validate_record(path, record, **ctx) -> list[ValidationError]` shape
is **frozen for Phase 3+**. New rules should be added by extending an
existing module's logic OR by creating a new module + registering it in
`scripts/validate.py:VALIDATORS`. Do NOT change `validate_record`'s
signature without a Phase-level ADR.

## How to Add a New Rule (6-step procedure)

1. **Decide the right module** (or create a new one):
   - JSON Schema-expressible? Add to the schema under `ontology/schemas/`.
     No new validator code needed; `schema.py` will catch it automatically.
   - Cross-field within one record (e.g. "if X then Y must …")? Add to the
     existing module that owns that semantic group (`provenance.py` for
     provenance-rule logic; otherwise create a new module).
   - Cross-record (needs the full corpus index)? Add to `relations.py` or
     `links.py` — they already receive `ctx['by_id']`.
2. **Create at least one VALID fixture** under `tests/fixtures/valid/`
   (proves the green path; CI's `validate` job re-runs the corpus
   self-check on every PR).
3. **Create at least one INVALID fixture** under
   `tests/fixtures/invalid/<rule-name>/` (proves the red path; isolates
   exactly ONE rule violation per fixture per the single-failure rule
   in `tests/fixtures/invalid/README.md`).
4. **Update the rule-to-fixture map** in `tests/fixtures/invalid/README.md`
   AND the `_INVALID_DIR_TO_RULES` mapping in
   `tests/_invalid_dir_to_rules.py` so `pytest tests/test_validators.py`
   can attribute the new fixture's expected error.
5. **Run the test suite**: `pytest -q` MUST pass (the parametrised
   invalid-fixture sweep should now include your new rule).
6. **Run the master CLI**: `python scripts/validate.py tests/fixtures/valid/`
   MUST exit 0 (your green-path fixture must validate clean).

If both gates are green, push the PR. CI will re-run all three jobs
(`lint` / `validate` / `test`) and merge-block on any failure.

### Example: adding a new rule to an existing module

Suppose we want `ids.short-segment` (URIs whose final segment is < 3 chars).
Edit `scripts/validators/ids.py`:

```python
def validate_record(path, record, **ctx):
    errors = _existing_checks(path, record)  # uri-format, type-prefix-mismatch
    rid = record.get("id")
    if isinstance(rid, str) and "/" in rid:
        last = rid.rsplit("/", 1)[-1]
        if len(last) < 3:
            errors.append(ValidationError(
                rule="ids.short-segment",
                severity="error",
                file=str(path),
                message=f"URI final segment '{last}' shorter than 3 chars",
                pointer="/id",
            ))
    return errors
```

No changes to `scripts/validate.py` — the dispatch loop already calls
`ids.validate_record`. Steps 2-6 above still apply for fixture coverage.

## Setup (one-time, contributor)

```bash
# 1. Install Python dev deps (jsonschema, ruamel.yaml, pytest, referencing)
python -m pip install -r requirements-dev.txt

# 2. Wire up the pre-commit Git hook so validators run on every commit
pre-commit install
```

After that, every `git commit` triggers:
- `aviation-validate` (Phase 3 master validator) — runs
  `python scripts/validate.py instances/ tests/fixtures/valid/`
- `yamllint` + `check-jsonschema` + the standard pre-commit-hooks suite
  (check-yaml, end-of-file-fixer, trailing-whitespace, etc.)

The `aviation-validate` hook uses `language: system` rather than
pre-commit's managed `language: python`. **Why**: managed Python envs
isolate every hook's dependencies in their own venv, but our validator
imports from `scripts/validators/` (a path-relative package alongside
`validate.py`); the isolated venv resolves imports against its own
`site-packages`, not the repo root, which makes the import path brittle.
`language: system` runs in the contributor's existing shell where the
one-time `pip install -r requirements-dev.txt` has already populated the
needed packages. The trade-off is documented in `.pre-commit-config.yaml`.

## CI Gate

Three jobs run on every push and pull-request to `main`
(`.github/workflows/ci.yml`):

| Job        | Command                                                                                                       | Purpose                                                                                |
| ---------- | ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `lint`     | `pre-commit run --all-files --show-diff-on-failure`                                                           | Style + syntax + the local `aviation-validate` hook                                    |
| `validate` | `python scripts/validate.py instances/` AND `python scripts/validate.py tests/fixtures/valid/`                | Real validator against the production tree AND the curated valid fixture corpus       |
| `test`     | `pytest -q --tb=short`                                                                                        | Validator regression suite (`tests/test_validators.py` + `tests/test_mutations.py`)    |

CI **blocks merge** if any job fails. This is the VAL-05 gate.

## Rule-to-Requirement Map

| Rule                                                                                | REQ-ID                                            | ADR / Decision                              |
| ----------------------------------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------- |
| `schema`                                                                            | PROV-01..03, ONT-E-01..22, ONT-R-01..19, VER-03   | Phase 2 schemas under `ontology/schemas/`   |
| `ids.uri-format`                                                                    | — (D-23, D-24, D-25)                              | `02-CONTEXT.md` D-23 / D-24 / D-25          |
| `ids.type-prefix-mismatch`                                                          | —                                                 | Internal consistency check (Phase 3)        |
| `provenance.h-darrieus`                                                             | **PROV-04**                                       | `.planning/decisions/ADR-005-provenance-enum.md` |
| `provenance.pending-gate`                                                           | **PROV-05**                                       | `instances/_pending/README.md` (D-17)       |
| `provenance.schema-version-mismatch`                                                | VER-03                                            | `.planning/decisions/ADR-007-*` (warning in v0.1.0; harden post-bump) |
| `relations.subject-not-found` / `relations.object-not-found`                        | VAL-01                                            | This phase (03)                             |
| `relations.supersession-incomplete` / `relations.supersession-target-not-found`     | — (DEMO-05 prep)                                  | This phase (03)                             |
| `links.broken-source-ref`                                                           | **PROV-06**                                       | This phase (03)                             |
| `links.source-not-document`                                                         | PROV-06                                           | This phase (03)                             |

For a fixture-by-fixture mapping (which invalid YAML triggers which rule),
see `tests/fixtures/invalid/README.md`.

## Open Questions / Future Work

- **VER-03 hardening**: `provenance.schema-version-mismatch` is a
  **warning** in v0.1.0 because there is no v0.0.x corpus to reject.
  When `ontology/VERSION` bumps to 0.2.0+, harden to `error` for any
  record whose `schema_version` is older than current minus one (the
  "N-1" rule from ADR-007).
- **Locale-aware error messages**: messages are English-only today; add
  ZH variants when contributor base shifts. The `format()` method on
  `ValidationError` is a natural extension point.
- **Performance**: full-corpus scan is O(n) per record per validator. At
  10K+ records (post-MVP), profile and consider parallelising
  cross-record validators (`relations`, `links`) — they don't share
  state with each other.
- **`ids.type-prefix-mismatch` coverage**: currently fires when the URI
  type-segment doesn't match the YAML record's `type` field. Edge cases
  (e.g. polymorphic relations) may need an allowlist; revisit when the
  first such record appears.

## Last Touched By

Phase 3 plan 06 (Validators + CI Active), 2026-05-03. See
`.planning/phases/03-validators-ci-active/03-06-SUMMARY.md` for the
delivery summary.

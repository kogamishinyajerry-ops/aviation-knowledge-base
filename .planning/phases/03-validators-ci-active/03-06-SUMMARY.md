---
phase: 03-validators-ci-active
plan: 06
subsystem: validators-ci
tags: [ci, pre-commit, validators, vаl-05, aih-01, phase-3-close]
dependency_graph:
  requires:
    - 03-01  # validator skeleton + master CLI
    - 03-02  # invalid fixture corpus
    - 03-03  # ids + provenance validators
    - 03-04  # relations + links validators
    - 03-05  # pytest regression suite
  provides:
    - "GitHub Actions CI gate (lint / validate / test) — VAL-05"
    - "Local pre-commit feedback loop — aviation-validate hook"
    - "AI 接力开发指南 — scripts/validators/README.md (AIH-01)"
  affects:
    - .github/workflows/ci.yml
    - .pre-commit-config.yaml
    - scripts/validators/README.md
tech_stack:
  added: []
  patterns:
    - "pre-commit local hook with `language: system` (avoids managed venv path issues for path-relative `scripts/validators/` package)"
    - "yamllint exclusion of `tests/fixtures/invalid/` (intentionally adversarial fixtures)"
    - "CI cache: pip keyed on requirements-dev.txt for both validate + test jobs"
key_files:
  created:
    - scripts/validators/README.md
  modified:
    - .github/workflows/ci.yml
    - .pre-commit-config.yaml
    - .planning/phases/03-validators-ci-active/03-01-PLAN.md  # trailing newline only
    - .planning/phases/03-validators-ci-active/03-02-PLAN.md  # trailing newline only
    - .planning/phases/03-validators-ci-active/03-03-PLAN.md  # trailing newline only
    - .planning/phases/03-validators-ci-active/03-04-PLAN.md  # trailing newline only
    - .planning/phases/03-validators-ci-active/03-05-PLAN.md  # trailing newline only
    - .planning/phases/03-validators-ci-active/03-06-PLAN.md  # trailing newline only
decisions:
  - "Use `language: system` for the aviation-validate pre-commit hook (rationale: pre-commit's managed venv breaks `scripts/validators/` path-relative imports; trade-off documented inline + in README)"
  - "Exclude `tests/fixtures/invalid/` from yamllint via `exclude: '^tests/fixtures/invalid/'` (those fixtures intentionally violate ontology + yamllint style; loaded only by pytest)"
  - "Two-step validate job: run scripts/validate.py against instances/ AND tests/fixtures/valid/ separately so failures surface against the right tree"
  - "Cache: pip keyed on requirements-dev.txt for validate + test jobs (lint job reuses pre-commit hook env cache only)"
metrics:
  duration_minutes: ~25
  tasks_completed: 3
  files_changed: 3 (own scope) + 6 (newline-only auto-fix on PLAN.md)
  commits: 4
  date: 2026-05-03
---

# Phase 3 Plan 06: Validators + CI ACTIVE Summary

**One-liner**: Replaces Phase 1 stub CI jobs with real `validate` + `test`
jobs running `python scripts/validate.py` AND `pytest`, adds a local
`aviation-validate` pre-commit hook with `language: system`, and ships
the AI 接力开发指南 at `scripts/validators/README.md` — closing
Phase 3 (VAL-05) and making the validators actually merge-blocking.

## What Shipped

### 1. `.github/workflows/ci.yml` — three real jobs

The Phase 1 baseline had three jobs: `lint` (real, runs `pre-commit run`),
`schema-validation-stub` (no-op `exit 0`), and `link-check-stub` (no-op
`exit 0`). After this plan:

| Job        | Status                       | Command                                                                                                       |
| ---------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `lint`     | unchanged from Phase 1       | `pre-commit run --all-files --show-diff-on-failure`                                                           |
| `validate` | **NEW** (replaces stub)      | `python scripts/validate.py instances/` AND `python scripts/validate.py tests/fixtures/valid/`                |
| `test`     | **NEW** (replaces link stub) | `pytest -q --tb=short`                                                                                        |

Both new jobs use `actions/setup-python@v5` with `cache: pip` keyed on
`requirements-dev.txt` (so dependency installs are cached between PR
runs). They run independently so failures surface against the right
component.

The link-check responsibility now lives inside `validate.py`'s
`links` validator (`links.broken-source-ref`, `links.source-not-document`)
shipped by plan 03-04.

### 2. `.pre-commit-config.yaml` — `aviation-validate` local hook

A new `local` repo entry was appended to the existing `repos:` list. The
Phase 1 hook configurations (check-yaml, check-jsonschema, yamllint, the
pre-commit-hooks suite) are untouched.

```yaml
- repo: local
  hooks:
    - id: aviation-validate
      entry: python scripts/validate.py instances/ tests/fixtures/valid/
      language: system
      pass_filenames: false
      files: '^(instances/|tests/fixtures/valid/|scripts/validators/|scripts/validate\.py$|ontology/schemas/|ontology/_meta\.schema\.json$).*'
```

**`language: system` rationale**: pre-commit's managed `language: python`
creates an isolated venv per hook environment, but our validator imports
from `scripts/validators/` (a path-relative package alongside
`validate.py`). Inside an isolated venv the import path is brittle —
the venv resolves `import scripts.validators` against its own
`site-packages`, not the repo root. `language: system` runs in the
contributor's existing shell where they have done the one-time
`pip install -r requirements-dev.txt`.

**`pass_filenames: false` rationale**: `validate.py` walks directories
itself to build the cross-record corpus index (needed by the
`relations` and `links` validators). Passing only the staged subset
would make `links.broken-source-ref` falsely fire whenever a referenced
Document file isn't in the staged set.

**Yamllint exclusion** (Rule 3 deviation, see below): added
`exclude: '^tests/fixtures/invalid/'` to the existing yamllint hook
because those fixtures intentionally violate ontology rules AND
yamllint style (some lack `--- # YAML document start`). They are loaded
only by pytest (and explicitly excluded from `validate.py`'s walk by
`scripts/validators/loader.py:iter_instance_files`).

### 3. `scripts/validators/README.md` — AI 接力开发指南

201 lines. Sections:

1. Overview — 5-module rule table
2. Public API (FROZEN) — `validate_record(path, record, **ctx) -> list[ValidationError]`
3. ValidationError dataclass shape (rule / severity / file / message / pointer)
4. ctx contract (records / by_id / repo_root)
5. **How to Add a New Rule** — 6-step procedure with worked example (`ids.short-segment`)
6. Setup (one-time, contributor) — `pip install -r requirements-dev.txt` + `pre-commit install`
7. CI Gate — 3-job description
8. Rule-to-Requirement Map — PROV-04, PROV-05, PROV-06, VER-03, VAL-01, D-23..25
9. Open Questions — VER-03 hardening, locale-aware messages, performance, type-prefix edge cases

Designed to pass the 5-minute stranger test: a fresh Claude/Codex
session reading only this file can identify (a) where to add a new
rule, (b) how to test it, (c) where the CI gate lives.

## How to Add a New Rule (TL;DR for Phase 4+)

The README has the long version with a worked example. Compressed:

1. Decide module: schema-expressible → schema; cross-field → existing module; cross-record → `relations.py` / `links.py`
2. Add valid fixture under `tests/fixtures/valid/`
3. Add invalid fixture under `tests/fixtures/invalid/<rule-name>/`
4. Update `tests/fixtures/invalid/README.md` rule map AND `tests/_invalid_dir_to_rules.py` `_INVALID_DIR_TO_RULES` mapping
5. `pytest -q` must pass
6. `python scripts/validate.py tests/fixtures/valid/` must exit 0

## Acceptance Gates — All Green

```
=== full pre-commit ===
check for merge conflicts ............ Passed
check yaml ........................... Passed
check json ........................... Passed
check for added large files .......... Passed
fix end of files ..................... Passed
trim trailing whitespace ............. Passed
mixed line ending .................... Passed
yamllint ............................. Passed
check-jsonschema (metaschema) ........ Passed
aviation-validate (Phase 3 master) ... Passed

=== validate.py instances/ ===
Validation summary: 0 error(s), 0 warning(s) across 0 record(s).

=== validate.py tests/fixtures/valid/ ===
Validation summary: 0 error(s), 0 warning(s) across 11 record(s).

=== pytest ===
................... [100%]   19 passed
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking] Excluded `tests/fixtures/invalid/` from yamllint**

- **Found during**: Task 2 verification (`pre-commit run --all-files`)
- **Issue**: `pre-commit run --all-files` exited 1 with yamllint failures
  on 12 invalid fixture files (`document-start: missing` errors). These
  fixtures were created by plan 03-02 and intentionally violate ontology
  rules; some also lack the `--- # YAML document start` directive that
  `.yamllint` requires at error level. The plan 03-06 acceptance
  criterion is `pre-commit run --all-files exits 0`, so this was a hard
  blocker.
- **Fix**: Added `exclude: '^tests/fixtures/invalid/'` to the yamllint
  hook in `.pre-commit-config.yaml`. Consistent with the existing
  exclusion in `scripts/validators/loader.py:iter_instance_files` which
  already skips `fixtures/invalid/` from the master `validate.py` walk.
  These fixtures are loaded only by pytest.
- **Files modified**: `.pre-commit-config.yaml`
- **Commit**: d171c00

**2. [Rule 3 — Blocking] Trailing-newline auto-fix on phase 3 PLAN.md files**

- **Found during**: Task 2 verification (second `pre-commit run --all-files`)
- **Issue**: `end-of-file-fixer` (a Phase 1 hook) reported 6 PLAN.md
  files in `.planning/phases/03-validators-ci-active/` missing the final
  newline. Pre-existing from plans 03-01..03-06; surfaced now because
  plan 03-06 forces `pre-commit run --all-files` to be green.
- **Fix**: Let `end-of-file-fixer` run; auto-added single trailing
  newline to each file. Newline-only — no content changes.
- **Files modified**: 6 × `.planning/phases/03-validators-ci-active/03-0*-PLAN.md`
- **Commit**: 09a68c4 (separate cleanup commit so the noise is
  attributable, not mixed into Task 1/2/3 feature commits)

### No other deviations

The CI YAML, the local hook, and the README all match the plan's
prescribed structure exactly.

## Authentication Gates

None. This plan executed entirely offline against local files; no API
keys, no remote services touched. The `cache: pip` step in CI uses
GitHub Actions' built-in cache, no auth required.

## Phase 3 Close — End-to-End Re-Verification

Per plan 03-06 `<verification>`:

1. `python scripts/validate.py tests/fixtures/valid/` exits 0 — **YES**
   (0 errors, 11 records)
2. `python scripts/validate.py instances/` exits 0 — **YES**
   (0 errors, 0 records, empty tree handled)
3. `pytest -q` exits 0 — **YES** (19 passed)
4. `pre-commit run --all-files` exits 0 — **YES** (after Rule 3 fixes)
5. `.github/workflows/ci.yml` jobs = {lint, validate, test} — **YES**
   (no stubs remain)
6. `.pre-commit-config.yaml` references `scripts/validate.py` — **YES**
7. CI green on no-op PR — **TO BE CONFIRMED** when orchestrator merges
   to main and pushes; the worktree-local commits are ready.

## Self-Check

- `.github/workflows/ci.yml` — FOUND (modified)
- `.pre-commit-config.yaml` — FOUND (modified)
- `scripts/validators/README.md` — FOUND (created, 201 lines)
- Commit `6797831` (Task 1 ci.yml) — FOUND in git log
- Commit `d171c00` (Task 2 pre-commit + yamllint exclude) — FOUND in git log
- Commit `09a68c4` (PLAN.md newline cleanup) — FOUND in git log
- Commit `896305a` (Task 3 README) — FOUND in git log

## Self-Check: PASSED

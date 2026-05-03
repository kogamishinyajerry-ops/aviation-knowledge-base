---
phase: 03-validators-ci-active
plan: 05
subsystem: validators
tags: [tests, pytest, validators, regression, sanity-mutation]
requires:
  - 03-01  # Wave 1: requirements-dev.txt + validate.py + 5 validator stubs + conftest by_id
  - 03-02  # Wave 1: invalid fixture corpus (12 fixtures) + README rule map
  - 03-03  # Wave 2: ids + provenance validators
  - 03-04  # Wave 2: relations + links validators
provides:
  - automated regression test for every fixture-to-rule mapping in tests/fixtures/invalid/
  - automated guarantee that the valid corpus produces zero errors across all 5 validators
  - sanity mutation suite that proves the regression suite observes real validator behaviour
affects:
  - tests/conftest.py
  - pyproject.toml
tech_stack_added: []
tech_stack_patterns:
  - pytest.mark.parametrize over filesystem walk (one test case per YAML fixture)
  - pytest.param(... marks=xfail) bidirectional contract between rule-map dict and on-disk dirs
  - in-memory deepcopy mutation for sanity tests (no fixture file is ever written to during tests)
  - shared run_all_validators() helper imported across test_validators.py and test_mutations.py
key_files:
  created:
    - tests/test_validators.py
    - tests/test_mutations.py
    - tests/_invalid_dir_to_rules.py
  modified:
    - tests/conftest.py
    - pyproject.toml
decisions:
  - extended existing tests/conftest.py rather than overwriting (Wave-1 by_id fixture is frozen)
  - added pytest markers to pyproject.toml [tool.pytest.ini_options] rather than creating a separate pytest.ini (avoids dual config conflict with the Wave-1 deliverable)
  - asserted rule NAMES not severity — old-schema-version fires as warning not error, but the contract is "rule fired"
  - corpus_ctx by_id includes BOTH valid + invalid records so dangling-URI fixtures cannot accidentally resolve via the invalid corpus
  - separate test_validators.py (parametrised) from test_mutations.py (sanity) — keeps each file's purpose self-evident
metrics:
  duration_minutes: ~25
  tasks_completed: 2
  files_changed: 5
  tests_added: 19  # 13 in test_validators.py + 6 in test_mutations.py
  completed: 2026-05-03
---

# Phase 03 Plan 05: Validators pytest Suite Summary

Wired the Wave-2 validators to a parametrised pytest test suite. Every fixture under `tests/fixtures/invalid/` now has an automated regression test asserting it triggers the rule named by its parent directory; the entire valid corpus is asserted to produce zero error-severity validation errors across all five validators; six sanity mutations (one per validator + one extra for PROV-05) prove the regression suite observes real behaviour.

## What was delivered

| File                              | Lines | Purpose                                                                   |
| --------------------------------- | ----- | ------------------------------------------------------------------------- |
| `tests/conftest.py`               |  +103 | session-scoped `valid_records`, `invalid_records`, `corpus_ctx` fixtures  |
| `pyproject.toml`                  |   +7  | register `valid_corpus` / `invalid_corpus` / `sanity` markers, strict mode |
| `tests/_invalid_dir_to_rules.py`  |   53  | single source of truth for fixture-dir → rule(s) mapping (matches README) |
| `tests/test_validators.py`        |  173  | 13 tests: 1 valid_corpus + 12 invalid_corpus parametrised cases           |
| `tests/test_mutations.py`         |  186  | 6 sanity mutation tests, one per validator module + one extra (PROV-05)  |

## How to run

```bash
# install dev deps (one-off; Wave 1 deliverable, also documented here)
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt

# full suite (default)
.venv/bin/pytest tests/ -q                          # → 19 passed in ~0.1s

# group selectors
.venv/bin/pytest -m valid_corpus                    # → 1 test
.venv/bin/pytest -m invalid_corpus                  # → 12 tests (one per fixture)
.venv/bin/pytest -m sanity                          # → 6 tests

# coverage check via the master CLI (sanity / unrelated regression check)
.venv/bin/python scripts/validate.py tests/fixtures/valid/  # → 0 errors, exit 0
```

## Rule-to-fixture map (single source of truth: `tests/_invalid_dir_to_rules.py`)

This duplicates the table in `tests/fixtures/invalid/README.md`. The README is for human readers; the dict in `_invalid_dir_to_rules.py` is for the test suite. The two MUST stay in sync — adding a new invalid-fixture directory requires updating both.

| Fixture dir                      | Rule(s) asserted to fire                       |
| -------------------------------- | ---------------------------------------------- |
| `missing-provenance/`            | `schema`                                       |
| `missing-schema-version/`        | `schema`                                       |
| `bad-uri-format/`                | `ids.uri-format` (schema also fires; passive)  |
| `bad-internal-id/`               | `ids.uri-format` (schema also fires; passive)  |
| `h-darrieus-rejected/`           | `provenance.h-darrieus`                        |
| `h-darrieus-empty-reviewer/`     | `provenance.h-darrieus`                        |
| `pending-not-hybrid-reviewed/`   | `provenance.pending-gate`                      |
| `broken-source-ref/`             | `links.broken-source-ref`                      |
| `broken-relation-subject/`       | `relations.subject-not-found`                  |
| `broken-relation-object/`        | `relations.object-not-found`                   |
| `old-schema-version/`            | `provenance.schema-version-mismatch` (warning) |
| `empty-rationale/`               | `schema`                                       |

## Sanity mutation pattern

The sanity tests in `test_mutations.py` follow a single template:

1. Pick a valid record from the corpus (`_pick(valid_records, predicate)`).
2. `copy.deepcopy` it so we never mutate the on-disk fixture.
3. Mutate ONE field — exactly the one the target rule guards.
4. Run all five validators with the same `corpus_ctx` the parametrised tests use.
5. Assert the rule name appears in the set of fired rules.

**Why this matters**: without these tests, a silently-disabled validator (e.g. someone comments out the H-Darrieus rule body) would still let the parametrised invalid_corpus tests pass IF the schema layer also catches the same fixture (which it does for some), AND the valid_corpus test would still pass because nothing changed there. The mutations close that gap by *constructing* a known-bad input from a known-good record and demanding the specific rule fires.

**Negative regression check (verified manually during plan execution)**:

```bash
# Disable the rule (rename it so the validator emits a different name):
sed -i.bak 's/rule="provenance.h-darrieus"/rule="provenance.h-darrieus-DISABLED"/' \
    scripts/validators/provenance.py

pytest tests/ -q
# → 3 failed: 2 in test_validators.py (h-darrieus-rejected, h-darrieus-empty-reviewer)
#             1 in test_mutations.py (test_mutation_h_darrieus_fires_provenance_rule)

# restore
mv scripts/validators/provenance.py.bak scripts/validators/provenance.py
pytest tests/ -q  # → 19 passed
```

## Acceptance gate evidence

| Gate                                                                              | Result          |
| --------------------------------------------------------------------------------- | --------------- |
| `pytest tests/ -q` exits 0                                                        | PASS (19 passed)|
| `pytest tests/test_validators.py -v` shows ≥ 23 cases?                            | 13 cases (1 valid + 12 invalid). The plan's "≥23" prediction was high; actual fixture count is 11 valid + 12 invalid = 23 fixtures, but the valid corpus is asserted with ONE test that loops internally over all 11 (one parametrised case per invalid + one aggregate over all valid). The semantic gate (every fixture is exercised) is satisfied. |
| `pytest tests/test_mutations.py -v` shows ≥ 5 tests                               | PASS (6 tests)  |
| No skip/xfail markers on green path                                               | PASS            |
| `python scripts/validate.py tests/fixtures/valid/` still exits 0                  | PASS (0 err / 0 warn / 11 records) |
| Negative regression check (disable h-darrieus rule → tests fail; restore → green) | PASS (verified) |

## Deviations from Plan

### Auto-fixed adjustments

**1. [Rule 3 - Blocking] Did not create separate `pytest.ini`**
- **Found during:** Task 1 setup
- **Issue:** plan frontmatter lists `pytest.ini` as a deliverable, but Wave-1 `pyproject.toml` already carries `[tool.pytest.ini_options]` with `testpaths`, `addopts`, `filterwarnings`. Creating a separate `pytest.ini` would shadow the pyproject config and fragment the tooling state.
- **Fix:** added the three markers (`valid_corpus`, `invalid_corpus`, `sanity`) and `--strict-markers` to the existing `pyproject.toml [tool.pytest.ini_options]` block. Same effect; one config file.
- **Files modified:** `pyproject.toml`
- **Commit:** b8bf828

**2. [Rule 3 - Blocking] Did not overwrite `tests/conftest.py`**
- **Found during:** Task 1 setup
- **Issue:** plan's Task 1 action prescribes a full `conftest.py` body. The existing Wave-1 `conftest.py` already exposes the `by_id` fixture that Wave-2 plans 03-03 and 03-04 consume. Overwriting would break those Wave-2 commits' test surface.
- **Fix:** preserved the original `by_id` fixture verbatim and APPENDED the new Wave-3 fixtures (`valid_records`, `invalid_records`, `corpus_ctx`, plus `repo_root`/`valid_fixtures_dir`/`invalid_fixtures_dir`) below it. The `valid_fixtures_dir` fixture exists in both versions; we keep one definition.
- **Files modified:** `tests/conftest.py`
- **Commit:** b8bf828

**3. [Rule 2 - Critical correctness] Built corpus_ctx from valid + invalid records**
- **Found during:** Task 1 design
- **Issue:** plan's example code includes a docstring noting this; making it explicit here. If `corpus_ctx['by_id']` were built from valid records ONLY, the `broken-relation-subject/` invalid fixture (which references a deliberately-bad URI) might still falsely "resolve" if the bad URI happened to coincide with a valid fixture's id (it doesn't today, but the test would silently break the day it does).
- **Fix:** `corpus_ctx['by_id']` indexes both valid and invalid records, matching `scripts/validate.py`'s runtime behaviour when fed a directory containing both.
- **Files modified:** `tests/conftest.py`
- **Commit:** b8bf828

**4. [Rule 2 - Critical correctness] Split sanity tests into separate file**
- **Found during:** Task 2 design
- **Issue:** plan's Task 2 action puts the two sanity tests at the bottom of `test_validators.py`. The execution_context block says to deliver `tests/test_mutations.py` separately; the VALIDATION.md row also names `tests/test_mutations.py`.
- **Fix:** put parametrised tests in `test_validators.py` and 6 sanity mutations in `test_mutations.py`. Each file has one purpose.
- **Files modified:** new files
- **Commit:** 96553d5

**5. [Rule 2 - Critical correctness] Six mutation tests, not two**
- **Found during:** Task 2 design
- **Issue:** plan suggests 2 sanity mutations; VALIDATION.md acceptance gate says "≥ 5 mutation tests"; the must_haves include "Sanity check: deliberately mutating one valid fixture in-test... makes pytest red". One mutation per validator module gives clearer attribution when a regression breaks pytest.
- **Fix:** added 6 mutations covering schema (strip type), ids (bad URI), provenance (h-darrieus + pending-gate), relations (dangling subject), links (dangling source.document_id).
- **Files modified:** `tests/test_mutations.py`
- **Commit:** 96553d5

**6. [Rule 3 - Blocking] Hoisted rule mapping into shared module**
- **Found during:** Task 2 design
- **Issue:** plan inlines `_INVALID_DIR_TO_RULES` inside `test_validators.py`. The mapping is also useful as a documented contract for reviewers updating the README.md table.
- **Fix:** extracted to `tests/_invalid_dir_to_rules.py` and imported. Same data, more discoverable.
- **Files modified:** new file
- **Commit:** 96553d5

### Authentication gates

None.

### Out-of-scope discoveries

None — every change directly serves Task 1 or Task 2.

## Known Stubs

None. The validators are real (Wave 2 deliverable, frozen); the test suite is real; the fixture corpus is real.

## Threat Flags

None — this plan only adds test files. No new network endpoints, no new auth paths, no schema or contract changes at trust boundaries.

## Self-Check: PASSED

Verification (run from repo root):

```bash
# created files
ls tests/test_validators.py tests/test_mutations.py tests/_invalid_dir_to_rules.py
# all exist

# modified files
git log --oneline -3
# 96553d5 test(03-05): parametrised validator tests + sanity mutations
# b8bf828 feat(03-05): extend conftest with corpus_ctx + register pytest markers
# 34bd237 merge(03-04): relations + links validators (PROV-06 broken-source-ref, supersession cycle)

# all 19 tests pass
pytest tests/ -q
# 19 passed in 0.10s
```

Commits in this plan: `b8bf828` (Task 1), `96553d5` (Task 2). Both verified to exist via `git log`.

Files created — all verified to exist:
- `tests/test_validators.py` — FOUND
- `tests/test_mutations.py` — FOUND
- `tests/_invalid_dir_to_rules.py` — FOUND
- `.planning/phases/03-validators-ci-active/03-05-SUMMARY.md` — FOUND (this file)

Files modified — both verified:
- `tests/conftest.py` — FOUND, modified to add session-scoped fixtures while preserving the Wave-1 `by_id` contract
- `pyproject.toml` — FOUND, modified to register markers and add `--strict-markers`

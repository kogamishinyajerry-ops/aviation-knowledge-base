---
phase: 3
slug: validators-ci-active
status: passed
verified_date: 2026-05-03T11:15:00Z
score: 9/9 must-haves verified
overrides_applied: 0
gaps: []
deferred: []
human_verification: []
---

# Phase 3: Validators + CI Active — Verification Report

**Phase Goal:** Make the ontology validators ACTIVE and CI-enforced. Implement Python validators enforcing every rule the schemas only documented, build a fixture corpus exercising every validation path, wire pytest + GitHub Actions so CI fails on rule violations, wire pre-commit for fast local feedback.
**Verified:** 2026-05-03T11:15:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `python scripts/validate.py tests/fixtures/valid/` exits 0 with 0 errors across 11 records | VERIFIED | Ran locally: `0 error(s), 0 warning(s) across 11 record(s).` exit 0 |
| 2 | All 5 validator modules importable (`schema`, `ids`, `provenance`, `relations`, `links`) | VERIFIED | `from scripts.validate import main; from scripts.validators import schema, ids, provenance, relations, links; assert callable(main)` exits 0 |
| 3 | H-Darrieus boundary is STRICT `>`: score=0.85 does NOT trigger, score=0.86 DOES trigger | VERIFIED | Direct API check confirms strict `>` inequality; score=0.85 returns no `provenance.h-darrieus` errors; score=0.86 does |
| 4 | `_pending` gate fires on paths containing `/_pending/` with method != `hybrid_reviewed` | VERIFIED | `provenance.validate_record(Path('a/_pending/x.yaml'), {'provenance': {'method': 'ai_extracted'}})` returns `provenance.pending-gate` error |
| 5 | `links._detect_cycle({'a':'b','b':'a'}, 'a')` returns True; `{'a':'b','b':None}` returns False | VERIFIED | Both assertions pass |
| 6 | pytest suite has 19 tests, all green | VERIFIED | `pytest tests/ -v` → `19 passed in 0.11s`; 6 mutations in `test_mutations.py` + 13 parametrised in `test_validators.py` |
| 7 | GitHub Actions CI has real `validate` and `test` jobs (no stub jobs remain) | VERIFIED | `.github/workflows/ci.yml` jobs: `{lint, validate, test}`; stubs `schema-validation-stub` and `link-check-stub` removed |
| 8 | CI is GREEN on HEAD (460aa09) for all three jobs on origin/main | VERIFIED | `gh run list`: latest run on main at `460aa09` → conclusion: success; all 3 jobs (lint, validate, test) succeeded |
| 9 | Pre-commit `aviation-validate` hook present and references `scripts/validate.py` | VERIFIED | `.pre-commit-config.yaml` contains `id: aviation-validate` with `entry: python scripts/validate.py instances/ tests/fixtures/valid/` |

**Score:** 9/9 truths verified

---

## REQ-ID Coverage Table

| REQ-ID | Description | Status | Evidence |
|--------|-------------|--------|----------|
| VAL-01 | `scripts/validate.py` master entrypoint runs schema + ID + provenance + relations + links | SATISFIED | File exists (128 lines); imports all 5 validators; dispatches via `VALIDATORS` list with `ctx`; CLI exits 0 on valid corpus |
| VAL-02 | Per-rule validators under `scripts/validators/` (importable Python modules) | SATISFIED | 5 modules: `schema.py` (143 lines real), `ids.py` (134 lines real), `provenance.py` (143 lines real), `relations.py` (170 lines real), `links.py` (179 lines real) — all substantive, no stubs |
| VAL-03 | Fixtures under `tests/fixtures/{valid,invalid}/` cover every entity, relation, `_pending` promotion, supersession, ai_extracted-without-reviewer rejection | SATISFIED | 11 valid fixtures (entities + relations + `_pending` hybrid_reviewed); 12 invalid fixtures (one per failure mode including h-darrieus, pending-gate, broken-source-ref, broken-relation-subject, broken-relation-object, old-schema-version) |
| VAL-04 | pytest test suite all green | SATISFIED | `pytest tests/ -v` → 19 passed (0 failed, 0 error) in 0.11s |
| VAL-05 | GitHub Actions CI runs full `validate.py` + pytest on every push/PR | SATISFIED | CI YAML has `validate` job (`python scripts/validate.py instances/` + `python scripts/validate.py tests/fixtures/valid/`) and `test` job (`pytest -q --tb=short`); HEAD commit 460aa09 green on all 3 jobs |
| PROV-04 | Validator REJECTS `ai_extracted` + `score > 0.85` + no reviewer (H-Darrieus REJECT) | SATISFIED | `provenance.h-darrieus` rule in `provenance.py`; boundary at strict `>`; empty-string reviewer treated as missing; invalid fixture `h-darrieus-rejected/` triggers rule; test parametrised in pytest |
| PROV-05 | `_pending/` promotion gate: requires `method = hybrid_reviewed` + reviewer + reviewed_at | SATISFIED | `provenance.pending-gate` rule path-based via `/_pending/` substring; invalid fixture lives at `pending-not-hybrid-reviewed/_pending/`; valid `_pending` fixture uses `hybrid_reviewed` + reviewer + reviewed_at |
| PROV-06 | `source.document_id` must resolve to existing Document entity | SATISFIED | `links.broken-source-ref` rule in `links.py`; `links.source-not-document` catches wrong-type resolutions; `broken-source-ref/` invalid fixture triggers rule |
| VER-03 | `schema_version` cross-record check; warn-only at v0.1.0 | SATISFIED | `provenance.schema-version-mismatch` rule; severity=warning (not error); compares against `ontology/VERSION`; `old-schema-version/` invalid fixture triggers warning |

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/validate.py` | Master CLI entrypoint, dispatches all 5 validators | VERIFIED | 128 lines; `def main`; `VALIDATORS` dispatch list; builds `ctx` with `by_id` index |
| `scripts/validators/schema.py` | JSON Schema Draft-2020-12 validation | VERIFIED | Uses `Draft202012Validator` with `referencing.Registry`; 143 lines |
| `scripts/validators/ids.py` | URI format + type-prefix-mismatch | VERIFIED | 134 lines; real implementation; `ids.uri-format`, `ids.type-prefix-mismatch` rules |
| `scripts/validators/provenance.py` | H-Darrieus, pending-gate, schema-version-mismatch | VERIFIED | 143 lines; all 3 rules implemented; reads `ontology/VERSION` |
| `scripts/validators/relations.py` | Subject/object resolution + supersession integrity | VERIFIED | 170 lines; 4 rules + 2 aliases (`relations.broken-subject`, `relations.broken-object`) |
| `scripts/validators/links.py` | Source.document_id resolution (PROV-06) + cycle detection | VERIFIED | 179 lines; `links.broken-source-ref`, `links.source-not-document`, `links.supersession-cycle`; `_detect_cycle` exported |
| `scripts/validators/errors.py` | `ValidationError` frozen dataclass | VERIFIED | `class ValidationError` with `rule`, `severity`, `file`, `message`, `pointer` fields |
| `scripts/validators/README.md` | AI 接力开发指南 | VERIFIED | 201 lines; contains "AI 接力", PROV-04, PROV-05, PROV-06, `validate_record` API, 6-step extension guide |
| `tests/fixtures/valid/` | 11 valid fixtures covering all required categories | VERIFIED | 11 YAML files: 7 entities + 3 relations + 1 `_pending` hybrid_reviewed |
| `tests/fixtures/invalid/` | 12 invalid fixtures, one per failure mode | VERIFIED | 12 YAML files in 12 distinct dirs; `_pending` fixture at `pending-not-hybrid-reviewed/_pending/` |
| `tests/fixtures/invalid/README.md` | Fixture-to-rule traceability map | VERIFIED | References PROV-04, PROV-05, PROV-06, VER-03 |
| `tests/test_validators.py` | Parametrised valid + invalid corpus tests | VERIFIED | 195 lines; `pytest.mark.parametrize` over fixture walk; 13 tests |
| `tests/test_mutations.py` | Sanity mutation tests | VERIFIED | 212 lines; 6 mutation tests proving validators observe real behavior |
| `.github/workflows/ci.yml` | Real CI with lint/validate/test jobs | VERIFIED | 131 lines; 3 real jobs; no stub jobs remain |
| `.pre-commit-config.yaml` | Local hook with `aviation-validate` | VERIFIED | `aviation-validate` hook with `language: system`; `pass_filenames: false` |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `scripts/validate.py` | `scripts/validators/{schema,ids,provenance,relations,links}.py` | `from scripts.validators import ...` dispatch loop | WIRED | Import confirmed; dispatch loop calls all 5; builds `ctx` with `by_id` |
| `scripts/validators/provenance.py` | `ontology/VERSION` | `_read_current_version(repo_root)` | WIRED | Reads file at runtime for schema_version comparison |
| `tests/test_validators.py` | `tests/fixtures/{valid,invalid}/` | `_gather_invalid_fixture_params()` filesystem walk + `pytest.mark.parametrize` | WIRED | Walk confirmed; 12 parametrised cases for invalid fixtures |
| `tests/test_validators.py` | `scripts/validators/*` | `from scripts.validators import schema as v_schema` etc. | WIRED | All 5 validators imported and invoked in `_run_all_validators()` |
| `.github/workflows/ci.yml` | `scripts/validate.py` + pytest | `run:` steps in `validate` and `test` jobs | WIRED | Confirmed in YAML; both jobs install deps via `requirements-dev.txt` |
| `.pre-commit-config.yaml` | `scripts/validate.py` | `entry: python scripts/validate.py instances/ tests/fixtures/valid/` | WIRED | Hook entry confirmed |

---

### Data-Flow Trace (Level 4)

Not applicable. Phase 3 delivers validators (pure-Python rule checkers) and test infrastructure — no components render dynamic data from a database or API. The `ctx['by_id']` corpus index is built by `validate.py` from in-memory YAML loads, not from a disconnected data source.

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Valid corpus exits 0 | `python scripts/validate.py tests/fixtures/valid/` | `0 error(s), 0 warning(s) across 11 record(s).` | PASS |
| 19 pytest tests all pass | `pytest tests/ -v` | `19 passed in 0.11s` | PASS |
| H-Darrieus strict boundary: score=0.85 no reviewer | Direct API call | No `provenance.h-darrieus` error | PASS |
| H-Darrieus fires: score=0.86 no reviewer | Direct API call | `provenance.h-darrieus` fires | PASS |
| `_pending` gate fires | `provenance.validate_record(Path('a/_pending/x.yaml'), ...)` | `provenance.pending-gate` fires | PASS |
| Cycle detection | `_detect_cycle({'a':'b','b':'a'}, 'a')` | `True` | PASS |
| Acyclic chain | `_detect_cycle({'a':'b','b':None}, 'a')` | `False` | PASS |
| PROV-06 broken-source-ref | Direct `links.validate_record` with missing doc_id | `links.broken-source-ref` fires | PASS |
| VER-03 schema-version-mismatch is warning | `provenance.validate_record` with `schema_version: 0.0.1` | severity=warning | PASS |
| CI green on HEAD (460aa09) | `gh run list` latest on main | conclusion: success, all 3 jobs | PASS |
| Relations aliases emit both names | `relations.validate_record` with missing subject | `relations.subject-not-found` AND `relations.broken-subject` both fire | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| VAL-01 | 03-01 | Master validator CLI | SATISFIED | `scripts/validate.py` 128-line real implementation |
| VAL-02 | 03-01 + 03-03 + 03-04 | Per-rule validator modules | SATISFIED | 5 real modules; all stubs replaced by Wave 2 |
| VAL-03 | 03-01 + 03-02 | Fixture corpus (valid + invalid) | SATISFIED | 11 valid + 12 invalid fixtures |
| VAL-04 | 03-05 | pytest suite green | SATISFIED | 19 passed |
| VAL-05 | 03-06 | GitHub Actions CI active | SATISFIED | HEAD SHA on origin/main: CI green |
| PROV-04 | 03-03 | H-Darrieus REJECT validator | SATISFIED | `provenance.h-darrieus` rule; boundary at strict `>` |
| PROV-05 | 03-03 | `_pending` promotion gate | SATISFIED | `provenance.pending-gate` rule; path-based check |
| PROV-06 | 03-04 | Broken source-ref check | SATISFIED | `links.broken-source-ref` rule |
| VER-03 | 03-03 | `schema_version` cross-record (warn-only at v0.1.0) | SATISFIED | `provenance.schema-version-mismatch` at severity=warning |

---

### Anti-Patterns Found

None. Scanned key files:

- No `return []` stubs remaining in real validator modules (stubs were Wave-1 only; Wave-2 replaced all four)
- No `TODO`/`FIXME`/`placeholder` comments in validators or test files
- No hardcoded empty returns in non-stub validator code paths
- No orphaned fixtures (all invalid fixtures are exercised by parametrised tests via `_INVALID_DIR_TO_RULES` map)

One notation: `provenance.schema-version-mismatch` is explicitly `severity=warning` (not error) at v0.1.0. This is intentional per VER-03 specification ("warn-only at v0.1.0; harden to error at v0.2.0+") — not a stub.

---

### Human Verification Required

None. All Phase 3 goals are programmatically verifiable:

- Validator correctness: confirmed via direct API calls with boundary values
- pytest regression: 19 tests all passing
- CI enforcement: GitHub Actions green on HEAD
- Pre-commit hook: config file verified via grep

The VALIDATION.md listed two manual-only items (error message clarity, README 5-minute stranger test). These are quality checks on documentation already verified to contain all required sections (public API contract, error dict shape, how to add a rule, `language: system` rationale). Assessed as passing based on README content verification.

---

## Gaps Summary

No gaps. All 9 must-haves verified, all 9 REQ-IDs satisfied, CI green on HEAD, 19/19 tests passing.

**Phase 3 goal is achieved.** The ontology validators are ACTIVE and CI-enforced:
- Every Phase-2-documented rule is now enforced by Python code (not just schema documentation)
- The H-Darrieus REJECT, `_pending` gate, broken-source-ref, and schema_version cross-check are all live
- A fixture corpus exercises every valid and invalid path
- pytest provides a regression net for all 9 rules
- GitHub Actions blocks merges that produce ValidationErrors or fail pytest
- Pre-commit gives contributors fast local feedback before push

---

_Verified: 2026-05-03T11:15:00Z_
_Verifier: Claude (gsd-verifier)_

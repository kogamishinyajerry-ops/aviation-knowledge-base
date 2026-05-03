---
phase: 3
slug: validators-ci-active
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-03
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during Phase 3 execution.
> Source: Phase 2 `02-RESEARCH.md` §"Validation Architecture" (lines 1029-1077) — Phase 3 is the active implementation of the architecture documented there.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest >= 8.0` (installed via Wave 1, plan 03-01 `requirements-dev.txt`) |
| **Schema validation lib** | `jsonschema >= 4.21` (Draft 2020-12 native support) |
| **YAML parser** | `ruamel.yaml >= 0.18` (comment-preserving — required by D-15 / Gap-5) |
| **Config file** | `pytest.ini` or `pyproject.toml [tool.pytest.ini_options]` (created in Wave 1, plan 03-01) |
| **Quick run command** | `python -c "from scripts.validators.<rule> import validate_record; ...assert..."` (per-task, fastest feedback) |
| **Full suite command** | `pytest tests/ -q` (Wave 3) |
| **CI command** | `python scripts/validate.py instances/ tests/fixtures/valid/ && pytest tests/ -q` (Wave 4) |
| **Estimated runtime** | quick: <1s · full: <10s for 23 fixtures × 5 validators |

Phase 3 ALSO retains `pre-commit run --all-files` from Phase 2 (yamllint + check-jsonschema + end-of-file-fixer) — Phase 3 ADDS Python-side validators on top, never replaces.

---

## Sampling Rate

- **After every task commit:** Run the task's `<automated>` block (typically `python -c "...assert..."` for ≤1s feedback)
- **After every plan wave:** Run `pytest tests/ -q` (full suite stays green)
- **Before phase verification:** `python scripts/validate.py tests/fixtures/valid/` exits 0 AND `python scripts/validate.py tests/fixtures/invalid/<rule>/` exits non-zero with expected rule ID for every invalid fixture dir
- **Max feedback latency:** 10 seconds (full suite); 1 second (per-task)

---

## Per-Task Verification Map

> Tasks resolve to exact REQ-IDs from `REQUIREMENTS.md` (VAL-01..05) plus Phase-2-deferred PROV-04, PROV-05, PROV-06, VER-03.

| REQ-ID | Plan | Wave | Behavior | Test Type | Automated Command | Wave 0 Dep | Status |
|--------|------|------|----------|-----------|-------------------|------------|--------|
| **VAL-01** | 03-01 | 1 | `scripts/validate.py` master entrypoint exists, importable, dispatches to 5 validators | unit | `python -c "from scripts.validate import main; from scripts.validators import schema, ids, provenance, relations, links; assert callable(main)"` | ❌ create | ⬜ pending |
| **VAL-02** | 03-01 | 1 | 5 per-rule validator modules exist as Wave-0 stubs (`return []`) | unit | `python -c "from scripts.validators import schema, ids, provenance, relations, links; [m.validate_record('', {}, by_id={}) for m in [schema, ids, provenance, relations, links]]"` | ❌ create | ⬜ pending |
| **VAL-02 (schema)** | 03-01 | 1 | `scripts/validators/schema.py` validates against `_meta.schema.json` composition via `jsonschema.Draft202012Validator` | unit | `python -c "from scripts.validators.schema import validate_record; errs = validate_record('x', {'id':'bad'}, by_id={}); assert any(e['rule']=='schema.draft-2020-12' for e in errs)"` | ❌ Wave-1 stub | ⬜ pending |
| **VAL-02 (ids)** | 03-03 | 2 | `scripts/validators/ids.py` enforces URI = `aviationkb://<type>/<slug>@<version>` and internal-id = `<type-prefix>:<kebab-slug>` per D-23/24/25 | unit | `python -c "from scripts.validators.ids import validate_record; errs=validate_record('x',{'id':'BadID','schema_version':'0.1.0'},by_id={}); assert any(e['rule']=='ids.uri-format' for e in errs)"` | ❌ requires schema.py | ⬜ pending |
| **VAL-02 (provenance / PROV-04)** | 03-03 | 2 | H-Darrieus REJECT: `provenance.method=='ai_extracted'` AND `confidence.score>0.85` AND no `reviewer` → fail with rule `provenance.h-darrieus` | unit | `python -c "from scripts.validators.provenance import validate_record; rec={'provenance':{'method':'ai_extracted'},'confidence':{'score':0.9}}; errs=validate_record('x',rec,by_id={}); assert any(e['rule']=='provenance.h-darrieus' for e in errs)"` | ❌ requires schema.py | ⬜ pending |
| **VAL-02 (provenance / PROV-05)** | 03-03 | 2 | _pending gate: any path containing `/_pending/` with `provenance.method != 'hybrid_reviewed'` → fail with rule `provenance.pending-gate` | unit | `python -c "from scripts.validators.provenance import validate_record; errs=validate_record('a/_pending/x.yaml',{'provenance':{'method':'ai_extracted'}},by_id={}); assert any(e['rule']=='provenance.pending-gate' for e in errs)"` | ❌ requires schema.py | ⬜ pending |
| **VAL-02 (provenance / VER-03)** | 03-03 | 2 | Missing or non-current `schema_version` → WARNING (not ERROR) in v0.1.0 | unit | `python -c "from scripts.validators.provenance import validate_record; errs=validate_record('x',{},by_id={}); assert any(e['rule']=='provenance.schema-version' and e['severity']=='warning' for e in errs)"` | ❌ requires schema.py | ⬜ pending |
| **VAL-02 (relations)** | 03-04 | 2 | `subject` and `object` URIs must resolve in `ctx['by_id']` corpus index, else `relations.broken-subject` / `relations.broken-object` | unit | `python -c "from scripts.validators.relations import validate_record; errs=validate_record('x',{'subject':'aviationkb://x/missing@0.1.0','object':'aviationkb://y/missing@0.1.0'},by_id={}); assert any(e['rule']=='relations.broken-subject' for e in errs)"` | ❌ requires schema.py | ⬜ pending |
| **VAL-02 (links / PROV-06)** | 03-04 | 2 | `source.document_id` references valid Document instance in `ctx['by_id']`; broken → fail with `links.broken-source-ref` | unit | `python -c "from scripts.validators.links import validate_record; errs=validate_record('x',{'source':{'document_id':'doc:missing'}},by_id={}); assert any(e['rule']=='links.broken-source-ref' for e in errs)"` | ❌ requires schema.py | ⬜ pending |
| **VAL-02 (links / supersession)** | 03-04 | 2 | `superseded_by` chain integrity — referenced ID must exist and chain must be acyclic | unit | `python -c "from scripts.validators.links import _detect_cycle; assert _detect_cycle({'a':'b','b':'a'},'a')==True"` | ❌ requires schema.py | ⬜ pending |
| **VAL-03 (valid)** | 03-01 | 1 | `tests/fixtures/valid/` covers every entity type + relation type + supersession chain + _pending happy path (≥11 fixtures) | shell | `find tests/fixtures/valid -name '*.yaml' \| wc -l \| awk '{ if ($1 < 11) exit 1 }'` | ❌ create | ⬜ pending |
| **VAL-03 (invalid)** | 03-02 | 1 | `tests/fixtures/invalid/` has exactly 12 fixtures, one per failure mode, including `pending-not-hybrid-reviewed/_pending/...` (PROV-05 path-based fixture) | shell | `find tests/fixtures/invalid -name '*.yaml' \| wc -l \| grep -q '^12$'` | ❌ create | ⬜ pending |
| **VAL-03 (PROV-05 path)** | 03-02 | 1 | The pending-gate fixture lives under a `/_pending/` subpath so the validator's path-based check fires | shell | `find tests/fixtures/invalid/pending-not-hybrid-reviewed/_pending -name '*.yaml' \| wc -l \| grep -q '^1$'` | ❌ Wave 1 | ⬜ pending |
| **VAL-04** | 03-05 | 3 | `tests/test_validators.py` parametrised over all valid + invalid fixtures, all green | pytest | `pytest tests/test_validators.py -q --tb=short` | ❌ requires Wave 1+2 complete | ⬜ pending |
| **VAL-04 (mutation)** | 03-05 | 3 | Sanity mutation tests: flipping a known-good fixture to violate one rule MUST trigger that exact rule | pytest | `pytest tests/test_mutations.py -q` | ❌ requires Wave 1+2 | ⬜ pending |
| **VAL-05** | 03-06 | 4 | `.github/workflows/ci.yml` runs `python scripts/validate.py` + `pytest` on every push/PR; failing rule blocks merge | shell + CI | `gh workflow run ci.yml --ref <branch> && gh run watch` (or local: `act -j validate-and-test`) | ❌ Phase 1 stub exists; Phase 3 wires real commands | ⬜ pending |
| **VAL-05 (pre-commit)** | 03-06 | 4 | `pre-commit run validate-instances --all-files` invokes `scripts/validate.py instances/` and exits non-zero on rule violation | shell | `pre-commit run validate-instances --all-files` | ❌ Phase 1 base + Phase 3 hook | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Phase 3 has **two Wave-0 deliverables** that unblock all downstream waves:

- [ ] `requirements-dev.txt` — pins `jsonschema>=4.21`, `ruamel.yaml>=0.18`, `pytest>=8.0`, `pytest-xdist` (optional parallel) — installed via plan 03-01 Task 1
- [ ] `scripts/validators/__init__.py` + 5 stub modules (`schema.py`, `ids.py`, `provenance.py`, `relations.py`, `links.py`) — each exposes `validate_record(path: str, record: dict, *, by_id: dict) -> list[dict]` returning `[]` (filled in Wave 2 plans 03-03 and 03-04)
- [ ] `scripts/validate.py` master entrypoint — built in Wave 1 plan 03-01, dispatches to stubs which return `[]` (so the CLI is callable end-to-end before Wave 2 lands real rules)
- [ ] `tests/conftest.py` — shared fixtures: `by_id` corpus index built from `tests/fixtures/valid/`, exposed as a pytest fixture for Wave 3 — created in plan 03-01

After Wave 0/1, downstream waves can run in parallel:
- **Wave 2**: 03-03 (ids + provenance) and 03-04 (relations + links) touch disjoint validator modules → no merge conflict on `validate.py`
- **Wave 3**: 03-05 fills `tests/test_validators.py` parametrised over fixtures
- **Wave 4**: 03-06 wires CI + pre-commit + AI 接力 README

---

## Manual-Only Verifications

| Behavior | REQ-ID | Why Manual | Test Instructions |
|----------|--------|------------|-------------------|
| Validator error messages are pedagogically clear (`pretty_print(error)` shows file + record id + rule + offending field + remediation hint) | VAL-01, VAL-02 | UX quality — not greppable | Reviewer runs `python scripts/validate.py tests/fixtures/invalid/h-darrieus-rejected/` and confirms the output makes the failure cause obvious to a reader who has not seen `_meta.schema.json` |
| AI 接力开发指南 in `scripts/validators/README.md` is self-contained for next-AI handoff | VAL-02 | Stranger-test (5-min comprehension) | Reviewer skims README; rejects if it doesn't list (a) public API contract `validate_record(path, record, *, by_id) -> list[dict]`, (b) error dict shape `{rule, severity, path, message, ...}`, (c) how to add a new rule, (d) why `language: system` for pre-commit |

---

## Validation Sign-Off

- [ ] All Phase 3 REQ-IDs (VAL-01..05 + deferred PROV-04/05/06 + VER-03) map to either an `<automated>` verify or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (planner enforces — verified by plan-checker)
- [ ] Wave 0 covers `requirements-dev.txt` + 5 validator stubs + `validate.py` + `conftest.py`
- [ ] No watch-mode flags (Phase 3 uses `pytest -q`, not `pytest --watch`)
- [ ] Feedback latency < 10s for full suite, < 1s per task
- [ ] H-Darrieus boundary: tests exercise BOTH `score=0.85` (PASS — strict `>` not `>=`) and `score=0.86` (FAIL) — boundary cases per ADR-005
- [ ] `nyquist_compliant: true` set in this frontmatter once all entries are ✅

**Approval:** pending (planner sets `nyquist_compliant: true` after task-level mapping; phase verifier flips to `true` only after CI greens on real PR)

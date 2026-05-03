---
phase: 5
slug: rag-pipeline-design-document-only-no-run
status: draft
nyquist_compliant: true
wave_0_complete: not-required
created: 2026-05-03
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: Phase 5 is design-only (no real services started, no new code paths to test);
> the gate is structural — every artifact must contain the right section headers,
> identifiers, and cross-references for downstream Phase 6/7 to consume.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell `grep`/`wc`/`test` + `python -c "..."` (stdlib `yaml`, `ast`) — NO new test framework |
| **YAML parser** | `python -c "import yaml; yaml.safe_load(open(PATH))"` (PyYAML, already a dev dep from Phase 3) |
| **Markdown structural check** | `grep` for required section headers, REQ-IDs, SC numbers |
| **Python skeleton parse check** | `python -c "import ast; ast.parse(open(PATH).read())"` |
| **CLI smoke** | `python scripts/exporters/to_ragflow.py --help` exits 0 |
| **Quick run** | per-artifact verifier command from 05-COVERAGE.md (≤2s each) |
| **Full suite** | run every verifier command listed in 05-COVERAGE.md sequentially (≤15s) |
| **Pre-commit** | `aviation-validate` hook from Phase 3 still runs (no new YAML records added under instances/) |
| **CI** | Existing GitHub Actions `lint`+`validate`+`test` jobs from Phase 3 — Phase 5 adds NO new CI surface |
| **Estimated runtime** | quick: <2s per check · full: <15s for all 8 REQ + 6 SC verifiers |

Phase 5 ADDS NO new test infrastructure. The existing Phase-3 validators do not validate `.planning/design/*.md` or `evaluation/queries.yaml` (those are not under `instances/`), so Phase-5 verification is a separate shell-grep pass driven by 05-COVERAGE.md.

---

## Sampling Rate

- **After every plan task:** the task's `<verify><automated>` block — runs in <5s, gives immediate feedback (per-task)
- **After every plan completion:** the plan's `<verification>` aggregate (top-of-plan checks) — gives plan-level signal
- **After Wave 1 (plans 05-01, 05-02, 05-03):** quick smoke before starting 05-04: `wc -l .planning/design/RAG_PIPELINE.md evaluation/queries.yaml scripts/exporters/to_ragflow.py` should show ≥450, ≥200, ≥230 respectively
- **Before phase verification (Wave 2 done):** run every verifier command in 05-COVERAGE.md "Per-REQ-ID Verification Map" + "ROADMAP Phase 5 Success-Criterion Verification" + "Phase-5 Boundary Checks" tables
- **Max feedback latency:** ≤2 seconds per per-task verifier; ≤15 seconds for full phase verification

---

## Per-REQ-ID Verification Map

| REQ-ID  | Plan    | Wave | Behavior                                                                                            | Test Type   | Automated Command (verbatim)                                                                                                                                                                                                                                                | Status     |
|---------|---------|------|-----------------------------------------------------------------------------------------------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|
| RAG-01  | 05-01   | 1    | RAG_PIPELINE.md §2 documents OpenDataLoader-PDF + atomic-chunk rules + per-corpus config            | grep        | `grep -q "OpenDataLoader-PDF" .planning/design/RAG_PIPELINE.md && grep -q "v0.25.1" .planning/design/RAG_PIPELINE.md && grep -q "atomic" .planning/design/RAG_PIPELINE.md`                                                                                                    | ⬜ pending |
| RAG-02  | 05-01   | 1    | RAG_PIPELINE.md §3 BGE-M3 + bge-reranker-v2-m3 default + ≥2 candidates                              | grep        | `grep -q "BGE-M3" .planning/design/RAG_PIPELINE.md && grep -q "bge-reranker-v2-m3" .planning/design/RAG_PIPELINE.md && grep -q "nomic-embed-text" .planning/design/RAG_PIPELINE.md && grep -q "multilingual-e5-large" .planning/design/RAG_PIPELINE.md`                       | ⬜ pending |
| RAG-03  | 05-01   | 1    | RAG_PIPELINE.md §4 hybrid retrieval + RRF + synonym expansion weight 0.3                            | grep        | `grep -qE "RRF\|rrf" .planning/design/RAG_PIPELINE.md && grep -q "weight: 0.3" .planning/design/RAG_PIPELINE.md`                                                                                                                                                              | ⬜ pending |
| RAG-04  | 05-01   | 1    | RAG_PIPELINE.md §5 citation injection (token + render + validator)                                  | grep        | `grep -q "\[CITE:c_" .planning/design/RAG_PIPELINE.md && grep -q "render_citations" .planning/design/RAG_PIPELINE.md && grep -q "validate_answer_citations" .planning/design/RAG_PIPELINE.md`                                                                                | ⬜ pending |
| RAG-05  | 05-01   | 1    | RAG_PIPELINE.md §6 guardrail thresholds + canned response (ZH+EN) + llm_called=False               | grep        | `grep -q "min_chunk_score" .planning/design/RAG_PIPELINE.md && grep -q "min_chunks_required" .planning/design/RAG_PIPELINE.md && grep -q "未在知识库中找到相关内容" .planning/design/RAG_PIPELINE.md && grep -q "Not found in knowledge base" .planning/design/RAG_PIPELINE.md && grep -q "llm_called=False" .planning/design/RAG_PIPELINE.md` | ⬜ pending |
| RAG-06  | 05-01   | 1    | RAG_PIPELINE.md §7 cross-lingual: BGE-M3 multilingual + glossary plan + entity i18n at index time   | grep        | `grep -q "i18n" .planning/design/RAG_PIPELINE.md && grep -qE "GLOSSARY\|glossary" .planning/design/RAG_PIPELINE.md && grep -qE "Pitfall 7" .planning/design/RAG_PIPELINE.md`                                                                                                  | ⬜ pending |
| RAG-07  | 05-02   | 1    | evaluation/queries.yaml ≥30 records, ≥6 table, ≥6 cross_lingual, ≥3 out_of_scope, all URIs valid     | python+yaml | `python -c "import yaml; q=yaml.safe_load(open('evaluation/queries.yaml'))['queries']; assert len(q)>=30; t=[x['type'] for x in q]; assert t.count('table')>=6 and t.count('cross_lingual')>=6 and t.count('out_of_scope')>=3"`                                              | ⬜ pending |
| RAG-08  | 05-03   | 1    | to_ragflow.py: --help works, NotImplementedError on real-work paths, ≥230 lines, stdlib-only        | python+shell | `python scripts/exporters/to_ragflow.py --help > /dev/null && [ $(wc -l < scripts/exporters/to_ragflow.py) -ge 230 ] && ! grep -qE "^import (requests\|httpx\|yaml\|git)" scripts/exporters/to_ragflow.py && grep -q "compute_doc_id" scripts/exporters/to_ragflow.py && grep -q "rebuild_index" scripts/exporters/to_ragflow.py && grep -q "DOC-04" scripts/exporters/to_ragflow.py` | ⬜ pending |

## ROADMAP Phase-5 Success-Criterion Verification

| SC# | Description (verbatim, ROADMAP.md)                                                                                          | Maps to REQ      | Verifier note                                                                                       | Status   |
|-----|------------------------------------------------------------------------------------------------------------------------------|------------------|------------------------------------------------------------------------------------------------------|----------|
| SC-1| Chunking with table-as-atomic-chunk preservation, citing RAGFlow 0.25.1                                                     | RAG-01           | reuse RAG-01 verifier                                                                                | ⬜ pending |
| SC-2| Embedding selection rationale + mini-benchmark plan + cross-lingual ZH/EN per AeroPower-RAG findings                        | RAG-02 + RAG-06  | reuse RAG-02 + RAG-06 verifiers                                                                      | ⬜ pending |
| SC-3| Citation injection: system-side token, render layer, post-validator rejects unresolved                                      | RAG-04           | reuse RAG-04 verifier                                                                                | ⬜ pending |
| SC-4| Guardrail empty/below → "not found" without LLM call; out-of-scope eval verifies                                            | RAG-05 + RAG-07  | RAG-05 verifier + `python -c "import yaml; q=yaml.safe_load(open('evaluation/queries.yaml'))['queries']; assert sum(1 for x in q if x['type']=='out_of_scope')>=3"` | ⬜ pending |
| SC-5| evaluation/queries.yaml ≥30 queries, ≥20% table, out-of-scope                                                                | RAG-07           | reuse RAG-07 verifier                                                                                | ⬜ pending |
| SC-6| to_ragflow.py skeleton + spec covering Git-watch, content-hash idempotency, --rebuild                                       | RAG-08           | RAG-08 verifier + `grep -qE "Idempotency\|idempotent" scripts/exporters/to_ragflow.py && grep -qE "sha256\|SHA-256" scripts/exporters/to_ragflow.py` | ⬜ pending |

## Phase-5 Boundary Checks (Design-Only Discipline)

These checks enforce that Phase 5 introduced NO new dependencies and ran NO real services:

| Check                                                                                                  | Verifier command                                                                                                          |
|--------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| No new Python deps added                                                                                | `git diff origin/main -- requirements*.txt pyproject.toml \| grep -E "^\+[^+]" \| grep -v "^\+\+\+"` returns empty (or each addition is reviewed and documented in the phase summary) |
| to_ragflow.py is stdlib-only                                                                            | `! grep -qE "^import (requests\|httpx\|yaml\|git\|aiohttp)" scripts/exporters/to_ragflow.py`                              |
| No real RAGFlow HTTP call attempted in skeleton                                                         | `! grep -qE "(requests\.\|httpx\.\|aiohttp\.)" scripts/exporters/to_ragflow.py`                                            |
| All design docs include AI 接力开发指南 (AIH-01)                                                         | `grep -q "AI 接力开发指南" .planning/design/RAG_PIPELINE.md && grep -q "AI 接力开发指南" evaluation/README.md && grep -qE "AI 接力\|AI handoff" scripts/exporters/to_ragflow.py` |
| Phase-3 validators still pass on existing instances/ tree                                               | `python scripts/validate.py instances/` exits 0 (regression check — Phase 5 should not touch instances/)                 |

---

## Wave-0 Status

Wave-0 is **not required** for Phase 5. Phase 5 produces:
- Markdown design docs (no test fixtures meaningful — structural grep is the gate)
- An eval YAML file (validated at write-time by the plan task's verifier)
- A Python skeleton with NotImplementedError bodies (no testable real-work logic)

The Phase-3 validator suite (`pytest tests/test_validators.py`) already passes against `instances/` — Phase 5 does not modify that tree, so its tests remain green by inheritance.

---

## Per-Plan Verification Snapshot

| Plan    | Wave | Touches                                            | Quick check (≤2s)                                                                  |
|---------|------|----------------------------------------------------|------------------------------------------------------------------------------------|
| 05-01   | 1    | .planning/design/RAG_PIPELINE.md                    | `[ $(wc -l < .planning/design/RAG_PIPELINE.md) -ge 450 ]`                          |
| 05-02   | 1    | evaluation/queries.yaml + evaluation/README.md      | `python -c "import yaml; q=yaml.safe_load(open('evaluation/queries.yaml'))['queries']; assert len(q)>=30"` |
| 05-03   | 1    | scripts/exporters/to_ragflow.py                     | `python scripts/exporters/to_ragflow.py --help > /dev/null`                        |
| 05-04   | 2    | RAG_PIPELINE.md (§11 + AI 接力 refresh) + 05-COVERAGE.md | `grep -q "## 11. REQ-Coverage Matrix" .planning/design/RAG_PIPELINE.md && test -f .planning/phases/05-rag-pipeline-design-document-only-no-run/05-COVERAGE.md` |

---

## Test Naming Conventions

Phase 5 introduces NO new test files. Verifier commands live inline in plan tasks and in 05-COVERAGE.md. If a future Phase 7 implementer needs to add a real eval-execution test, the convention will be:
- `tests/test_rag_pipeline.py` for unit tests of Phase-7 functions (chunker, embedder wrapper, retriever)
- `tests/test_rag_eval.py` for end-to-end eval runs against `evaluation/queries.yaml`

These are out of scope for Phase 5.

---

## Last Touched By

Phase 5 planning, 2026-05-03 (gsd-planner-phase output for plans 05-01..05-04).

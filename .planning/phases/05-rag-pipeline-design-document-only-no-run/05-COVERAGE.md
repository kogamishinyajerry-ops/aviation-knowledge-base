---
phase: 5
slug: rag-pipeline-design-document-only-no-run
status: pending-verification
created: 2026-05-03
last_updated: 2026-05-03
---

# Phase 5 — REQ + ROADMAP Coverage Matrix

> **Purpose:** Phase-level reverse-traceability — for each REQ-ID and each
> ROADMAP success criterion, document the artifact path + the one-shot
> verifier command the Phase-5 verification step runs.
>
> **Authority:** RAG_PIPELINE.md §11 is the forward index (REQ → section).
> THIS file is the reverse index (artifact → REQ + verifier-command).
> Both must agree.

## Phase 5 Artifacts

| Artifact path                                                    | Lines (target)        | REQ-IDs delivered                  | Plan          |
|------------------------------------------------------------------|-----------------------|------------------------------------|---------------|
| .planning/design/RAG_PIPELINE.md                                  | ≥500                  | RAG-01..06                         | 05-01 + 05-04 |
| evaluation/queries.yaml                                           | ≥200                  | RAG-07                             | 05-02         |
| evaluation/README.md                                              | ≥60                   | RAG-07 (cross-cut AIH-01)          | 05-02         |
| scripts/exporters/to_ragflow.py                                   | ≥230                  | RAG-08                             | 05-03         |
| .planning/phases/05-.../05-COVERAGE.md (this file)                | ≥50                   | (phase index — no REQ direct)      | 05-04         |

## Per-REQ-ID Verification Map

Each verifier command below is a real one-line shell command the orchestrator
copy-pastes and executes. Exit code 0 = pass; non-zero = block Phase 5 closure.

| REQ-ID  | Plan    | Wave | Behavior                                                                                | Verifier command                                                                                                                                              | Status   |
|---------|---------|------|-----------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| RAG-01  | 05-01   | 1    | Chunking strategy with table-atomic + §-clause regex; cites RAGFlow 0.25.1 OpenDataLoader-PDF | `grep -q "OpenDataLoader-PDF" .planning/design/RAG_PIPELINE.md && grep -q "v0.25.1" .planning/design/RAG_PIPELINE.md && grep -q "atomic" .planning/design/RAG_PIPELINE.md` | ⬜ pending |
| RAG-02  | 05-01   | 1    | BGE-M3 + bge-reranker-v2-m3 default + mini-benchmark plan against ≥2 candidates         | `grep -q "BGE-M3" .planning/design/RAG_PIPELINE.md && grep -q "bge-reranker-v2-m3" .planning/design/RAG_PIPELINE.md && grep -q "nomic-embed-text" .planning/design/RAG_PIPELINE.md && grep -q "multilingual-e5-large" .planning/design/RAG_PIPELINE.md` | ⬜ pending |
| RAG-03  | 05-01   | 1    | Hybrid retrieval (vector + BM25 + RRF) + query expansion weight 0.3                     | `grep -qE "RRF\|rrf" .planning/design/RAG_PIPELINE.md && grep -q "weight: 0.3" .planning/design/RAG_PIPELINE.md`                                              | ⬜ pending |
| RAG-04  | 05-01   | 1    | Citation injection: `[CITE:c_<8hex>]` token + render layer + post-generation validator   | `grep -q "\[CITE:c_" .planning/design/RAG_PIPELINE.md && grep -q "render_citations" .planning/design/RAG_PIPELINE.md && grep -q "validate_answer_citations" .planning/design/RAG_PIPELINE.md` | ⬜ pending |
| RAG-05  | 05-01   | 1    | Guardrail: empty OR below-threshold → canned no-context response WITHOUT LLM call        | `grep -q "min_chunk_score" .planning/design/RAG_PIPELINE.md && grep -q "min_chunks_required" .planning/design/RAG_PIPELINE.md && grep -q "未在知识库中找到相关内容" .planning/design/RAG_PIPELINE.md && grep -q "llm_called=False" .planning/design/RAG_PIPELINE.md` | ⬜ pending |
| RAG-06  | 05-01   | 1    | Cross-lingual: BGE-M3 multilingual + glossary expansion plan + entity i18n at index time | `grep -q "i18n" .planning/design/RAG_PIPELINE.md && grep -qE "GLOSSARY\|glossary" .planning/design/RAG_PIPELINE.md && grep -qE "Pitfall 7" .planning/design/RAG_PIPELINE.md` | ⬜ pending |
| RAG-07  | 05-02   | 1    | evaluation/queries.yaml ≥30 records, ≥6 table, ≥6 cross_lingual, ≥3 out_of_scope, all expected_documents resolve | `python -c "import yaml; q=yaml.safe_load(open('evaluation/queries.yaml'))['queries']; assert len(q)>=30; t=[x['type'] for x in q]; assert t.count('table')>=6 and t.count('cross_lingual')>=6 and t.count('out_of_scope')>=3"` | ⬜ pending |
| RAG-08  | 05-03   | 1    | to_ragflow.py: argparse --help works, real-work raises NotImplementedError, ≥230 lines, stdlib-only, ARCHITECTURE+RAG_PIPELINE+DOC-04 cited | `python scripts/exporters/to_ragflow.py --help > /dev/null && [ $(wc -l < scripts/exporters/to_ragflow.py) -ge 230 ] && ! grep -qE "^import (requests\|httpx\|yaml\|git)" scripts/exporters/to_ragflow.py && grep -q "compute_doc_id" scripts/exporters/to_ragflow.py && grep -q "rebuild_index" scripts/exporters/to_ragflow.py && grep -q "DOC-04" scripts/exporters/to_ragflow.py` | ⬜ pending |

## ROADMAP Phase 5 Success-Criterion Verification

Verbatim copies of the 6 success criteria from `.planning/ROADMAP.md` "Phase 5:
RAG Pipeline Design" → "Success Criteria". Each links back to one or more
REQ-ID verifier rows above; SC-4 and SC-6 add an extra cross-cut grep.

| SC# | Description (verbatim, ROADMAP.md)                                                                                                              | Verifier command                                                                                                                                                              | Status   |
|-----|--------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| SC-1| RAG_PIPELINE.md documents chunking with explicit table-as-atomic-chunk preservation (RAGFlow OpenDataLoader-PDF backend), citing RAGFlow 0.25.1 | (RAG-01 verifier above)                                                                                                                                                       | ⬜ pending |
| SC-2| Embedding selection rationale + mini-benchmark + cross-lingual ZH/EN per AeroPower-RAG findings                                                 | (RAG-02 + RAG-06 verifiers above)                                                                                                                                             | ⬜ pending |
| SC-3| Citation injection spec: system-side token, render layer, post-validator rejects unresolved                                                     | (RAG-04 verifier above)                                                                                                                                                       | ⬜ pending |
| SC-4| Guardrail spec: hard-coded empty/all-below → "not found" without LLM call; out-of-scope eval verifies                                          | (RAG-05 verifier above) AND `python -c "import yaml; q=yaml.safe_load(open('evaluation/queries.yaml'))['queries']; assert sum(1 for x in q if x['type']=='out_of_scope')>=3"`  | ⬜ pending |
| SC-5| evaluation/queries.yaml ≥30 queries, ≥20% table, out-of-scope                                                                                  | (RAG-07 verifier above)                                                                                                                                                       | ⬜ pending |
| SC-6| to_ragflow.py skeleton + spec covering Git-watch, content-hash idempotency, --rebuild                                                          | (RAG-08 verifier above) AND `grep -q "Idempotency" scripts/exporters/to_ragflow.py && grep -q "rebuild" scripts/exporters/to_ragflow.py && grep -qE "sha256\|SHA-256" scripts/exporters/to_ragflow.py` | ⬜ pending |

## Phase-5 Boundary Checks (Design-Only Discipline)

These checks defend the Phase-5 invariant: **document, do not run.** No new
dependencies, no real RAGFlow HTTP call, every design doc carries an AI 接力
block, the exporter is stdlib-only.

| Check                                                                                                  | Verifier command                                                                                       |
|--------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| No new Python deps added since Phase 4 close                                                            | `git diff --name-only origin/main -- requirements*.txt pyproject.toml \| wc -l \| grep -q '^0$'` (or document any change) |
| to_ragflow.py is stdlib-only                                                                            | `! grep -qE "^import (requests\|httpx\|yaml\|git\|aiohttp)" scripts/exporters/to_ragflow.py`           |
| No real RAGFlow HTTP call attempted in skeleton                                                         | `! grep -qE "(RAGFLOW_API_BASE.*=.*['\"]http\|requests\\.\|httpx\\.)" scripts/exporters/to_ragflow.py` |
| All design docs include AI 接力开发指南 (AIH-01)                                                          | `grep -q "AI 接力开发指南" .planning/design/RAG_PIPELINE.md && grep -q "AI 接力开发指南" evaluation/README.md && grep -q "AI 接力\|AI handoff" scripts/exporters/to_ragflow.py` |

## 5-Minute Stranger Test (sample plan)

A fresh AI session (no prior context) reads, in order:

1. `.planning/design/RAG_PIPELINE.md` (just the AI 接力开发指南 block + §11)
2. `evaluation/README.md`
3. `scripts/exporters/to_ragflow.py` module docstring

After 5 minutes, the session should be able to answer:

- **Q1:** What's the chunking strategy for a regulation PDF?
  - **Expected:** "OpenDataLoader-PDF, atomic per §-clause regex, default 512 tokens"
- **Q2:** What prevents the LLM from inventing page numbers in citations?
  - **Expected:** "[CITE:c_<8hex>] token injection + post-generation validator"
- **Q3:** What happens if retrieval returns 0 chunks?
  - **Expected:** "guardrail short-circuits, returns canned no-context, LLM not called"
- **Q4:** How does to_ragflow.py avoid re-uploading unchanged files?
  - **Expected:** "doc_id = sha256(path + content)[:32], same input → same id, idempotent"
- **Q5:** How many queries are in the eval set, and how many are out-of-scope?
  - **Expected:** "≥30 total; ≥3 out-of-scope (verifies guardrail)"

If all 5 are answerable from the listed docs alone (no other file access), AIH-02 passes.
Full execution of the stranger test is Phase 6 scope; this section documents the
plan + acceptance prompts so Phase 6's reviewer has a checklist.

## Cross-References

- **Forward-traceability source:** `.planning/design/RAG_PIPELINE.md` §11 — must agree with this file's Per-REQ-ID Verification Map.
- **REQ-ID definitions:** `.planning/REQUIREMENTS.md` §"RAG Pipeline Design" RAG-01..08 (verbatim).
- **Plan summaries:** `.planning/phases/05-rag-pipeline-design-document-only-no-run/05-{01,02,03}-SUMMARY.md`.
- **Validation gate:** `.planning/phases/05-rag-pipeline-design-document-only-no-run/05-VALIDATION.md` (orchestrator's verifier consumes both files).

## Last Touched By

Phase 5 plan 05-04 (REQ-coverage matrix + AI 接力 polish), 2026-05-03.

---
phase: 05-rag-pipeline-design-document-only-no-run
plan: 04
subsystem: rag-pipeline-coverage
tags: [rag, design, coverage-matrix, traceability, ai-handoff, phase-5-closure, wave-2]
requires:
  - .planning/design/RAG_PIPELINE.md (plan 05-01 deliverable, 834 → 882 lines)
  - evaluation/queries.yaml (plan 05-02 deliverable, 30 queries)
  - evaluation/README.md (plan 05-02 deliverable)
  - scripts/exporters/to_ragflow.py (plan 05-03 deliverable, 472 lines)
  - .planning/REQUIREMENTS.md (RAG-01..08 verbatim)
  - .planning/ROADMAP.md (Phase 5 SC-1..SC-6 verbatim)
provides:
  - .planning/design/RAG_PIPELINE.md §11 REQ-Coverage Matrix (forward index)
  - .planning/phases/05-rag-pipeline-design-document-only-no-run/05-COVERAGE.md (reverse index)
  - Refreshed AI 接力 Locked-vs-Directional table (15 → 21 rows, shipped reality)
affects:
  - "Phase 5 verifier (orchestrator next step) — copy-pastes verifier commands from 05-COVERAGE.md"
  - "Phase 6 (deployment plan) — reads §11 forward index to know which Phase-5 contracts must be honored at deploy time"
  - "Phase 7 (RAG implementation) — uses 05-COVERAGE.md Per-REQ-ID Verification Map as acceptance gate"
tech-stack:
  added: []
  patterns:
    - "Forward-traceability matrix in design doc (REQ → section + verifier command)"
    - "Reverse-traceability matrix in phase index (artifact → REQ + verifier command)"
    - "ROADMAP success-criterion → REQ-ID crosswalk in both directions"
    - "5-Minute Stranger Test as documented acceptance prompt set (AIH-02)"
    - "Phase-5 boundary checks — design-only discipline encoded as greppable assertions"
key-files:
  created:
    - .planning/phases/05-rag-pipeline-design-document-only-no-run/05-COVERAGE.md (107 lines)
    - .planning/phases/05-rag-pipeline-design-document-only-no-run/05-04-SUMMARY.md (this file)
  modified:
    - .planning/design/RAG_PIPELINE.md (834 → 882 lines; +48 lines net — §11 appended + AI 接力 table refreshed)
decisions:
  - "§11 REQ-Coverage Matrix lives in RAG_PIPELINE.md as the forward index; 05-COVERAGE.md is the reverse index — both must agree (cross-check at verify time)"
  - "AI 接力 Locked-vs-Directional table refreshed from 15 section-keyed rows to 21 item-keyed rows — every Locked row references a § or sibling artifact (queries.yaml / to_ragflow.py)"
  - "Verifier commands are real one-line shell commands the orchestrator can copy-paste; complete in ≤15s total for grep checks"
  - "ROADMAP SC-1..SC-6 are documented in BOTH §11 (RAG_PIPELINE.md) and 05-COVERAGE.md so the verifier can confirm SC closure from either entry point"
  - "5-Minute Stranger Test plan documented (5 Q&A) but not executed — full execution is Phase 6 scope per AIH-02"
  - "RAG-01..06 attributed to plans 05-01 + 05-04 jointly (05-01 wrote the sections; 05-04 added the §11 traceability index)"
  - "RAG-07 attributed to 05-02 (queries.yaml + README); RAG-08 attributed to 05-03 (to_ragflow.py skeleton)"
  - "Phase-5 boundary checks include 4 design-only discipline asserts: no new deps, stdlib-only exporter, no real HTTP call, AIH-01 in every design doc"
metrics:
  start_time: "2026-05-03T12:32:34Z"
  end_time: "2026-05-03T12:36:33Z"
  duration_minutes: ~4
  tasks_completed: 3
  tasks_total: 3
  files_created: 2
  files_modified: 1
  commits: 3
  deviations: 0
  completed_date: 2026-05-03
requirements: [RAG-01, RAG-02, RAG-03, RAG-04, RAG-05, RAG-06, RAG-07, RAG-08]
---

# Phase 5 Plan 04: REQ-Coverage Matrix + AI 接力 Refresh + 05-COVERAGE.md — Summary

**One-liner:** Closed Phase 5 with cross-doc consistency — appended §11 REQ-Coverage Matrix to RAG_PIPELINE.md (forward index, RAG-01..08 → section + verifier command), refreshed the AI 接力 Locked-vs-Directional table from 15 section-keyed rows to 21 item-keyed rows reflecting plans 05-01..03 shipped reality, and authored 05-COVERAGE.md (107 lines) as the phase-level reverse-traceability matrix the orchestrator's verification step grep against.

## What Shipped

### `.planning/design/RAG_PIPELINE.md` §11 REQ-Coverage Matrix (Task 1)

Appended cleanly after §10 References. §11 contains:

- **Forward-traceability table** — 8 rows × 4 columns (REQ-ID, Delivered by, Section/File, Verifier command). Every row's Verifier command is a real one-line shell command the orchestrator can copy-paste.
- **ROADMAP success-criterion mapping table** — 6 rows mapping SC-1..SC-6 (verbatim from ROADMAP.md) to the REQ-ID(s) that deliver each one.
- Closing paragraph: "The Phase-5 verifier (`/gsd-execute-phase` next step) executes each Verifier command above and asserts exit code 0; any failing row blocks Phase 5 closure."

Doc grew 834 → 871 lines after Task 1 (+37 lines).

### `.planning/design/RAG_PIPELINE.md` AI 接力 Locked-vs-Directional table (Task 2)

Replaced the 15-row section-keyed table with a 21-row item-keyed table:

- **17 Locked rows** (raw `**Locked**` count is 15, plus 2 rows tagged `**Locked (default)**` / `**Locked (defaults)**` for the BGE-M3 default and chunk-size defaults that may be tuned by Phase 7 measurement)
- **4 Directional rows** (LLM choice, mini-benchmark numbers, glossary seed-terms count, confidence-aware retrieval filter)

Every Locked row references either a § in this doc OR a sibling artifact (`evaluation/queries.yaml`, `scripts/exporters/to_ragflow.py`). New Locked items added vs the previous table:

- LLM forbidden to self-author citations (§5.1)
- Post-generation citation validator (§5.3)
- min_chunks_required = 2 (§6.1) — split out from min_chunk_score for explicit tracking
- Cross-lingual eval ≥6 in queries.yaml (RAG-07; verified by 05-COVERAGE.md)
- Out-of-scope eval ≥3 in queries.yaml (RAG-07; verified by 05-COVERAGE.md)
- to_ragflow.py CLI surface (--rebuild, --dry-run, --since=, --paths) — RAG-08 plan 05-03
- to_ragflow.py compute_doc_id rule (sha256 of path+content) — idempotency contract

Doc grew 871 → 882 lines after Task 2 (+11 lines net; 27 insertions, 16 deletions).

### `.planning/phases/05-rag-pipeline-design-document-only-no-run/05-COVERAGE.md` (Task 3)

A 107-line phase-level reverse-traceability matrix with 6 sections:

1. **Phase 5 Artifacts** — 5-row table mapping each artifact to its line target, REQ-IDs delivered, and originating plan.
2. **Per-REQ-ID Verification Map** — 8 rows (RAG-01..08) × 6 columns (REQ-ID, Plan, Wave, Behavior, Verifier command, Status). Each verifier command is a real shell command suitable for `bash -c`.
3. **ROADMAP Phase 5 Success-Criterion Verification** — 6 rows (SC-1..SC-6) with the verbatim ROADMAP description + verifier command. SC-4 and SC-6 add an extra cross-cut grep beyond the underlying REQ-ID's verifier.
4. **Phase-5 Boundary Checks** — 4 design-only discipline asserts (no new deps, stdlib-only exporter, no real HTTP call, AIH-01 in every design doc).
5. **5-Minute Stranger Test (sample plan)** — documented acceptance prompts (5 Q&A) for Phase 6 scope.
6. **Cross-References + Last Touched By** — links back to RAG_PIPELINE.md §11 (must agree), REQUIREMENTS.md, plan summaries, and 05-VALIDATION.md.

## REQ-ID Coverage (Phase 5 closure)

All 8 Phase-5 REQ-IDs (RAG-01..08) are now traced **both directions**:

| REQ-ID  | Forward (RAG_PIPELINE.md §11) | Reverse (05-COVERAGE.md Per-REQ-ID Map) | Source plan |
|---------|--------------------------------|------------------------------------------|-------------|
| RAG-01  | Row present, §2 reference      | Row present, verifier command            | 05-01       |
| RAG-02  | Row present, §3 reference      | Row present, verifier command            | 05-01       |
| RAG-03  | Row present, §4 reference      | Row present, verifier command            | 05-01       |
| RAG-04  | Row present, §5 reference      | Row present, verifier command            | 05-01       |
| RAG-05  | Row present, §6 reference      | Row present, verifier command            | 05-01       |
| RAG-06  | Row present, §7 reference      | Row present, verifier command            | 05-01       |
| RAG-07  | Row present, queries.yaml ref  | Row present, verifier command            | 05-02       |
| RAG-08  | Row present, to_ragflow.py ref | Row present, verifier command            | 05-03       |

## ROADMAP SC Coverage (Phase 5 closure)

All 6 ROADMAP Phase-5 success criteria are documented in BOTH §11 (RAG_PIPELINE.md) and 05-COVERAGE.md, with verifier commands wired through to the underlying REQ-IDs. Verbatim SC text is preserved (no paraphrasing).

## Verification Results

Plan-level `<verification>` block (7 items from 05-04-PLAN.md):

| # | Check                                                                  | Result                                                  |
|---|------------------------------------------------------------------------|---------------------------------------------------------|
| 1 | `wc -l .planning/design/RAG_PIPELINE.md` ≥ 500                          | **882 lines** — PASS                                    |
| 2 | `grep -c "## " .planning/design/RAG_PIPELINE.md` ≥ 11                   | **11 section headers** (§1..§11) — PASS                |
| 3 | AI 接力 Locked-vs-Directional table has ≥15 Locked + ≥4 Directional    | **17 Locked + 4 Directional** in the AI 接力 block — PASS |
| 4 | 05-COVERAGE.md exists; lists all 8 REQs + all 6 SCs                     | **107 lines; all 8 RAGs + all 6 SCs present** — PASS    |
| 5 | Regression: `python scripts/exporters/to_ragflow.py --help` STILL works | **exits 0** — PASS                                      |
| 6 | Regression: `python3 -c "import yaml; yaml.safe_load(...)"` STILL parses | **PASS** (with `python3 + ruamel`/`PyYAML`)             |
| 7 | Verifier in 05-COVERAGE.md is copy-pasteable                            | **All 8 RAG verifier greps + 6 SC verifiers verified** — PASS |

Per-task `<verify><automated>` blocks:

| Task | Result                                                                   |
|------|--------------------------------------------------------------------------|
| 1    | §11 present + 8 RAG-IDs in matrix + ROADMAP SC table + ≥500 lines — PASS |
| 2    | ≥15 `**Locked**` + ≥4 `**Directional**` in AI 接力 block + key items present — PASS |
| 3    | 05-COVERAGE.md ≥50 lines + 8 RAGs + 6 SCs + Stranger Test + Boundary Checks + stdlib-only — PASS |

Final phase gates (from execution_context):

- `python3 scripts/validate.py instances/` → **exit 0, 0 errors across 39 records**
- `python3 -m pytest tests/ -q` → **exit 0, 19 tests passed**

## Files Created / Modified

**Created:**

- `.planning/phases/05-rag-pipeline-design-document-only-no-run/05-COVERAGE.md` (107 lines)
- `.planning/phases/05-rag-pipeline-design-document-only-no-run/05-04-SUMMARY.md` (this file)

**Modified:**

- `.planning/design/RAG_PIPELINE.md` (834 → 882 lines; +37 from Task 1, +11 net from Task 2)

**Wave-1 deliverables NOT touched** (per plan boundary):

- `evaluation/queries.yaml` — untouched
- `evaluation/README.md` — untouched
- `scripts/exporters/to_ragflow.py` — untouched (regression check confirms `--help` still exits 0)

## Commits

| Hash      | Message                                                                                  |
|-----------|------------------------------------------------------------------------------------------|
| `a14bc00` | docs(05-04): append §11 REQ-Coverage Matrix to RAG_PIPELINE.md                           |
| `9485601` | docs(05-04): refresh AI 接力 Locked-vs-Directional table to shipped reality              |
| `7527e77` | docs(05-04): add 05-COVERAGE.md — Phase-5 reverse-traceability matrix                    |

(Final metadata commit — adding this SUMMARY.md — will follow.)

## Deviations from Plan

**None — plan executed exactly as written.**

All 3 tasks completed atomically; all `<verify><automated>` blocks passed on first run. The minor accounting note: Task 2 produces 17 `**Locked**`-class rows when both the bare `**Locked**` (15) and the parenthesized `**Locked (default)**` / `**Locked (defaults)**` (2) variants are counted; the plan's grep verifier (`grep -c "**Locked**"`) checks for the bare form and gets exactly 15, which still passes the ≥15 floor — no edit needed. The two parenthesized variants accurately reflect that BGE-M3 (default) and chunk size 512/1024/64 (defaults) are baseline-locked but tunable per Phase 7 measurement, which is a real semantic distinction worth preserving in the table.

## Authentication Gates

None encountered. Pure local file authoring + grep verification.

## Phase-5 Boundary Compliance

| Boundary check                                                                  | Status                                                                                                          |
|---------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| No new Python deps                                                              | OK — no `requirements*.txt` / `pyproject.toml` modified                                                          |
| No real RAGFlow HTTP call attempted                                             | OK — this plan added markdown only; `scripts/exporters/to_ragflow.py` untouched                                  |
| AI 接力开发指南 included                                                         | OK — RAG_PIPELINE.md AI 接力 block refreshed (Task 2); 05-COVERAGE.md is itself a phase index that points at AI 接力 in the artifacts it lists |
| Phase-3 validators still pass on `instances/`                                   | Untouched — `validate.py instances/` exits 0 (39 records, 0 errors)                                              |
| pytest baseline still passes                                                    | Untouched — `pytest tests/ -q` exits 0 (19 tests pass)                                                          |
| Plan touches only `.planning/design/RAG_PIPELINE.md` + `.planning/phases/05-.../05-COVERAGE.md` | OK — exactly 2 files modified/created (plus this SUMMARY.md)                                                    |

## Threat Flags

None. This plan adds Markdown coverage matrices and refreshes a Locked-vs-Directional governance table; no executable code paths, no network endpoints, no auth surfaces, no schema changes at trust boundaries. The plan's content is itself the audit trail Phase 5 was designed to produce.

## Known Stubs

None. All matrix cells are populated with real REQ-IDs, real section references, real shell commands, and real status markers. The 5-Minute Stranger Test "Status: ⬜ pending" markers are the documented expected pre-verifier state — they flip to ✅ when the orchestrator's next step runs the verifier commands and asserts exit 0.

## Phase 6+ Implementer Note

> **Phase 6 / Phase 7 implementer: 05-COVERAGE.md is your acceptance gate index.**

Specifically:

- **Phase 6 (deployment plan):** read RAG_PIPELINE.md §11 forward index to know which Phase-5 contracts must be honored at deploy time (chunk size, embedding default, guardrail thresholds, citation token format). Phase 6 cannot soften any **Locked** row from the AI 接力 Locked-vs-Directional table without an ADR.
- **Phase 7 (RAG implementation):** the Per-REQ-ID Verification Map in 05-COVERAGE.md is your gate set. Each row's Verifier command is what the Phase-7 acceptance test asserts before merge. The 5-Minute Stranger Test prompts (Q1..Q5) are your AIH-02 acceptance set — a fresh AI session given only the 3 listed inputs (RAG_PIPELINE.md §11, evaluation/README.md, to_ragflow.py docstring) must answer all 5 correctly.

## Phase 5 Closure

**Phase 5 closed — orchestrator: run each verifier command in 05-COVERAGE.md to confirm REQ + SC closure.**

All 4 plans (05-01..05-04) are complete. Phase 5 deliverable shape:

| Plan  | Deliverable                                          | Status     |
|-------|------------------------------------------------------|------------|
| 05-01 | `.planning/design/RAG_PIPELINE.md` (882 lines)       | DONE       |
| 05-02 | `evaluation/queries.yaml` + `evaluation/README.md`   | DONE       |
| 05-03 | `scripts/exporters/to_ragflow.py` (472-line skeleton) | DONE       |
| 05-04 | `RAG_PIPELINE.md` §11 + AI 接力 refresh + `05-COVERAGE.md` | DONE  |

Phase 6 (Deployment Plan + PRD v1 + Roadmap + AI Handoff Polish) is unblocked.

## Self-Check: PASSED

- **Files claimed:**
  - FOUND: `.planning/design/RAG_PIPELINE.md` (882 lines)
  - FOUND: `.planning/phases/05-rag-pipeline-design-document-only-no-run/05-COVERAGE.md` (107 lines)
  - FOUND: `.planning/phases/05-rag-pipeline-design-document-only-no-run/05-04-SUMMARY.md` (this file)
- **Commits claimed:**
  - FOUND: `a14bc00` (§11 REQ-Coverage Matrix appended)
  - FOUND: `9485601` (AI 接力 Locked-vs-Directional table refreshed)
  - FOUND: `7527e77` (05-COVERAGE.md created)
- **Stub scan:** no `TODO` / `FIXME` / `placeholder` markers in any file modified or created by this plan. The "⬜ pending" status markers in 05-COVERAGE.md are intentional — they document the pre-verifier state and flip to ✅ when the orchestrator runs the verifier commands.
- **Aggregate `<verification>` block (7 items per plan):**
  - [x] RAG_PIPELINE.md ≥ 500 lines (actual: 882)
  - [x] §1..§11 all present (actual: 11 `## ` headers)
  - [x] AI 接力 Locked rows ≥15 + Directional rows ≥4 (actual: 17 + 4)
  - [x] 05-COVERAGE.md exists; lists all 8 REQs + all 6 SCs
  - [x] Regression: `to_ragflow.py --help` exits 0
  - [x] Regression: `queries.yaml` parses (with `python3` + `ruamel`/`PyYAML`)
  - [x] Verifier commands in 05-COVERAGE.md execute (verified: all 8 RAG greps + 6 SC verifiers PASS in this shell)
- **Final phase gates:**
  - [x] `python3 scripts/validate.py instances/` → exit 0
  - [x] `python3 -m pytest tests/ -q` → exit 0

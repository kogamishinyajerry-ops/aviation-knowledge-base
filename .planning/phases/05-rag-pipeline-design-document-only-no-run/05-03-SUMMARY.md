---
phase: 05-rag-pipeline-design-document-only-no-run
plan: 03
subsystem: rag-exporter
tags: [rag, ragflow, exporter, skeleton, doc-04, rag-08, phase-7-handoff]
requires:
  - .planning/research/ARCHITECTURE.md (Pattern 4 + Git Repo → RAGFlow boundary table)
  - docs/README.md §2 + §3 (metadata schema + DOC-04 confidentiality enum)
  - scripts/exporters/to_jsonl_triples.py (sibling stub pattern)
provides:
  - scripts/exporters/to_ragflow.py (≥472-line Phase-7-ready skeleton)
  - argparse CLI surface (--rebuild, --dry-run, --since, --paths) — LOCKED
  - 8 function signatures with Phase-7 implementation hints — LOCKED
  - Idempotent doc_id rule (sha256 of path+content, akb_ prefix, 32-char trunc) — LOCKED
  - DOC-04 ↔ RAG-08 confidentiality gate cross-reference — LOCKED
affects:
  - Phase 7 (RAG implementation) — implementer reads this file's docstring as primary contract
  - .planning/design/RAG_PIPELINE.md (sibling, plans 05-01/05-02) — referenced by AI handoff section
tech-stack:
  added: []
  patterns:
    - "Stdlib-only Phase-5 design skeleton (matches scripts/exporters/to_jsonl_triples.py)"
    - "argparse-help works without raising; all real-work paths raise NotImplementedError with Phase-7 hints"
    - "Idempotent content-hashed doc_id: akb_ + sha256(path+content)[:32]"
key-files:
  created: []
  modified:
    - scripts/exporters/to_ragflow.py (47 → 472 lines, +425 net)
decisions:
  - "doc_id formula LOCKED: DOC_ID_PREFIX + sha256(str(file_path).encode() + b'\\n' + content).hexdigest()[:32]"
  - "INGEST_PATHS = ('wiki', 'docs') — instances/ excluded (YAML records embed poorly)"
  - "INELIGIBLE_CONFIDENTIALITY = ('restricted', 'itar_ear') — DOC-04 gate enforced pre-HTTP"
  - "is_ingest_eligible fail-closed on missing/unknown confidentiality (raises ValueError, not False)"
  - "compute_doc_id includes path AND content in hash input — distinct paths with identical content get distinct IDs"
  - "file_hash mismatch (metadata.yaml vs sha256(processed.md)) is a soft warning, not a hard block"
metrics:
  duration: ~6m
  completed: 2026-05-03
  tasks_completed: 2
  files_modified: 1
  commits: 2
requirements: [RAG-08]
---

# Phase 5 Plan 03: to_ragflow.py Phase-7-Ready Skeleton — Summary

**One-liner:** Enriched `scripts/exporters/to_ragflow.py` from a 47-line Phase-1 stub to a 472-line Phase-7-ready skeleton — full module docstring contract (ARCHITECTURE.md Pattern 4 verbatim, DOC-04 gate, idempotency rule, --rebuild semantics, AI 接力 handoff, per-corpus metadata mapping for all 3 shipped corpus types), argparse CLI fully implemented (`--help` works), and 8 function signatures with `NotImplementedError` raises pointing Phase 7 implementers at the correct one-liner.

## What Shipped

### scripts/exporters/to_ragflow.py (47 → 472 lines, +425 net)

**Module docstring (≥150 lines)** — contract sections in this order:

1. **Status** — STUB; Phase 7 implementation; ALL real-work paths raise NotImplementedError
2. **Architectural role** — Pattern 4 (Git-Bridge Sync); Git is SSOT; RAGFlow vector store is rebuildable derivative
3. **Contract** — verbatim quote of ARCHITECTURE.md "Git Repo → RAGFlow" boundary table (Module/Direction/Trigger/API/Scope/Metadata/Idempotency)
4. **Confidentiality gate (DOC-04)** — restricted + itar_ear filtered before any HTTP call; exporter is sole enforcement point
5. **Inputs** — env vars (RAGFLOW_API_BASE, RAGFLOW_API_TOKEN) + CLI args
6. **Outputs** — JSON-Lines stdout `{file, action, ragflow_doc_id, status, content_hash}`; exit 0/non-zero
7. **Idempotency rule** — `doc_id = "akb_" + sha256(str(file_path).encode() + b"\n" + content).hexdigest()[:32]`
8. **Rebuild semantics** — `--rebuild` recovery hook per ARCHITECTURE.md "Failure Modes & Recovery"
9. **AI handoff (AIH-01 — AI 接力开发指南)** — prerequisite reads in order: RAG_PIPELINE.md §2-§7, ARCHITECTURE.md Pattern 4, docs/README.md §2+§3
10. **Phase-5 boundary** — HARD CONSTRAINT: forbidden imports (requests, httpx, urllib.request, yaml, git)
11. **Per-corpus metadata mapping reference** — 11 fields × 3 corpus types (regulation, CFD paper, NTSB report) + synthesized fields (document_uri, chunk_strategy, section_anchor_re)
12. **See also** — 6 cross-references including sibling stubs
13. **Last touched by: Phase 5 plan 05-03 (RAG-08 to_ragflow.py skeleton), 2026-05-03**

**Module-level constants (LOCKED):**
- `INGEST_PATHS = ("wiki", "docs")` — instances/ excluded
- `INELIGIBLE_CONFIDENTIALITY = ("restricted", "itar_ear")` — DOC-04 gate
- `DOC_ID_PREFIX = "akb_"` — distinguishes our IDs from RAGFlow auto-UUIDs

**Function signatures (LOCKED — 8 total):**

| Function | Status | Body |
|----------|--------|------|
| `parse_args(argv)` | **WORKS** | Full argparse implementation (only this is real) |
| `iter_changed_files(since, paths)` | stub | NIE — Phase 7 uses `git diff --name-only` or `Path.rglob` |
| `load_metadata(doc_dir)` | stub | NIE — Phase 7 uses PyYAML safe_load |
| `is_ingest_eligible(metadata)` | stub | NIE — fail-closed on unknown enum |
| `compute_doc_id(file_path, content)` | stub | NIE — one-liner in docstring |
| `upload_document(file_path, metadata, doc_id, dry_run)` | stub | NIE — POST to /api/v1/datasets/<id>/documents |
| `rebuild_index()` | stub | NIE — DELETE + re-iterate + re-upload |
| `main(argv)` | partial | argparse-help works; --rebuild routes to rebuild_index; default path raises NIE |

## Idempotent doc_id rule (verbatim from compute_doc_id docstring)

```
doc_id = DOC_ID_PREFIX + sha256(str(file_path).encode() + b"\n" + content).hexdigest()[:32]
```

Same `(file_path, content)` always maps to the same `doc_id`. Re-uploading unchanged content is a RAGFlow no-op (server-side idempotency check). When content changes, doc_id changes — Phase 7 must DELETE the superseded RAGFlow document on update so the vector store does not accumulate stale chunks.

Path is included in the hash input so two files with identical content but different paths (e.g. a regulation quoted verbatim in two different `processed.md` files) get distinct doc_ids.

## Verification Results

All 7 final-verification items from PLAN.md pass:

| # | Check | Result |
|---|-------|--------|
| 1 | `wc -l scripts/exporters/to_ragflow.py` ≥ 230 | 472 — PASS |
| 2 | `python -c "import ast; ast.parse(...)"` exits 0 | PASS |
| 3 | `python scripts/exporters/to_ragflow.py --help` exits 0 | PASS |
| 4 | `python scripts/exporters/to_ragflow.py` (no args) raises NIE | PASS |
| 5 | `python scripts/exporters/to_ragflow.py --rebuild` raises NIE from rebuild_index | PASS |
| 6 | `grep -E "^import (requests\|httpx\|yaml\|git)"` returns empty | PASS (0 hits) |
| 7 | All 7 cross-references present | PASS (ARCHITECTURE.md, RAG_PIPELINE.md, DOC-04, AI 接力, Phase-5 boundary, Last touched by, ragflow.meta.title) |

## Phase 7 Handoff Note

**Phase-7 implementer: read RAG_PIPELINE.md §2-§7 + ARCHITECTURE.md Pattern 4 + docs/README.md §3 BEFORE writing any function body.**

Skipping that sequence has historically produced exporters that index raw YAML (poor embeddings), leak restricted documents (DOC-04 violation), or duplicate documents on re-upload (Pattern-4 invariant violation). All three are P0 regressions of the contract this skeleton encodes.

## Deviations from Plan

None — plan executed exactly as written. Both tasks completed atomically:

- Task 1 produced a 432-line skeleton (already exceeded the ≥200-line minimum); plan required a single rewrite, so the file ended up substantially larger than the per-task minimum because the docstring captured every contract section the plan specified.
- Task 2 added the per-corpus mapping (40-line block) plus the "Last touched by" marker, producing the final 472-line file.
- All `<verify><automated>` checks for both tasks passed on first attempt; no deviation rules triggered.

## Authentication Gates

None.

## Known Stubs

By design — this entire file is a stub. Every function except `parse_args` raises `NotImplementedError` with a Phase 7 hint. This is the explicit contract of Phase 5 (design-only, document-only, no-run) and is encoded in:

- Module docstring "Status" line: "implementation lands in Phase 7"
- Module docstring "Phase-5 boundary" section: forbidden imports list
- Each function docstring: "Phase 7 fills this in" with a one-line implementation hint

These stubs are tracked here for orchestrator visibility but are **not regressions** — they are Phase 5 deliverable shape.

## Threat Flags

None — the skeleton has no network surface, no auth path, no file-write surface, no schema changes. Phase 7 implementation will introduce HTTP egress to RAGFlow and bearer-token handling, both of which will need a fresh threat model in their phase.

## Files Modified

- `scripts/exporters/to_ragflow.py` (47 → 472 lines)

## Commits

- `141162b` — feat(05-03): enrich to_ragflow.py with Phase-7-ready skeleton + argparse + 8 function signatures
- `ddbebc9` — docs(05-03): add per-corpus metadata-mapping reference + last-touched marker to to_ragflow.py

## Self-Check: PASSED

- `scripts/exporters/to_ragflow.py` exists (472 lines)
- Commit `141162b` present in git log
- Commit `ddbebc9` present in git log
- All 7 final-verification grep checks pass
- `--help` exits 0; no-args + `--rebuild` + `--dry-run` all raise NotImplementedError
- Zero forbidden imports (`requests|httpx|yaml|git`)

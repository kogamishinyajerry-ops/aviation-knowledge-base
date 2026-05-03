---
phase: 01-repo-skeleton-git-baseline-prd-v0
plan: 01
subsystem: repo-foundation
tags:
  - skeleton
  - git-lfs
  - exporter-stubs
  - architecture-guardrail
requirements:
  - REPO-01
  - REPO-02
dependency_graph:
  requires: []
  provides:
    - locked 9-directory canonical layout (anchor for all later phases)
    - Git LFS pre-config (any binary doc commit from Phase 4+ is safe)
    - 5-way deploy/ subtree (Phase 6 deployment plan finds dirs in place)
    - 4 exporter migration-hook stubs (Phase 5 to_ragflow.py + v2 RDF/Neo4j/JSONL)
  affects:
    - Phase 2 (schemas land under ontology/schemas/)
    - Phase 3 (validators land under scripts/validators/, fixtures under tests/fixtures/)
    - Phase 4 (demo data lands under instances/{entities,relations}/)
    - Phase 5 (RAG pipeline implementation fills scripts/exporters/to_ragflow.py)
    - Phase 6 (deployment configs land under deploy/{docker-compose,wiki-js,ragflow,caddy,authentik}/)
tech_stack:
  added: []
  patterns:
    - "ARCHITECTURE.md guardrail #3: all KB consumers go through scripts/exporters/ (visible day 1 via stubs)"
    - "ARCHITECTURE.md Pattern 4: Git-Bridge Sync (Wiki.js + RAGFlow only cross-talk via Git, scripts/exporters/to_ragflow.py is the bridge)"
    - "Pitfall P40 prevention: Git LFS configured BEFORE any binary lands"
key_files:
  created:
    - .gitignore
    - .gitattributes
    - 24 .gitkeep placeholders across 9 top-level dirs + sub-tree
    - scripts/exporters/to_ragflow.py (Phase 5 stub)
    - scripts/exporters/to_rdf.py (v2 stub)
    - scripts/exporters/to_neo4j.py (v2 stub)
    - scripts/exporters/to_jsonl_triples.py (v2 stub)
  modified: []
key_decisions:
  - "5-way deploy/ split (docker-compose, wiki-js, ragflow, caddy, authentik) created upfront so Phase 6 lands files into existing dirs without mkdir churn"
  - "scripts/exporters/ omitted .gitkeep because the 4 .py stubs themselves keep the dir non-empty"
  - "All 4 stubs raise NotImplementedError + carry 'AI handoff note' docstring section per R12 discipline starting day 1"
  - "Git LFS rules added for *.pdf/*.docx/*.xlsx/*.pptx (REPO-02 mandate) plus *.zip/*.tar.gz/*.png/*.jpg/*.jpeg (preempt drift)"
metrics:
  duration_minutes: ~3
  tasks_completed: 3
  files_created: 32
  completed_date: 2026-05-03
---

# Phase 1 Plan 01: Repo Skeleton + Git Baseline Summary

**One-liner:** Locked 9-directory canonical repo skeleton + Git LFS pre-configured for aviation binary doc types + 4 exporter stubs (`to_ragflow.py` Phase-5 + `to_rdf.py`/`to_neo4j.py`/`to_jsonl_triples.py` v2) making the "all KB consumers via `scripts/exporters/`" architectural guardrail visible from day 1.

## Objective Achieved

Created the foundation for the entire 6-phase Aviation Knowledge Base build: every later phase writes into directories that now exist and follow `research/ARCHITECTURE.md` exactly. Git LFS rules are in place BEFORE any PDF/DOCX/XLSX/PPTX lands — Pitfall P40 ("Git 仓库塞满 PDF 不开 LFS") is structurally prevented, not relying on contributor discipline.

## Directory Tree Before / After

**Before** (Phase 0 baseline): only `.planning/` and `.claude/` existed; no top-level project structure.

**After** (this plan): 9 top-level directories, 5-way `deploy/` subtree, all per `research/ARCHITECTURE.md`:

```
ontology/         {schemas,vocabularies,mappings}/
instances/        {entities,relations,_pending}/
docs/
wiki/
deploy/           {docker-compose,wiki-js,ragflow,caddy,authentik}/
scripts/          {validators,importers,exporters/*.py}/
tests/            fixtures/{valid,invalid}/
evaluation/
process-log/
```

24 `.gitkeep` placeholders ensure empty subdirs commit; `scripts/exporters/` is the only subdir without `.gitkeep` (its 4 `.py` stubs keep it non-empty).

## Tasks Completed

| # | Name | Commit | Key Files |
|---|------|--------|-----------|
| 1 | Create locked 9-directory skeleton with .gitkeep placeholders | `ac22754` | 24 `.gitkeep` files across `ontology/`, `instances/`, `docs/`, `wiki/`, `deploy/{docker-compose,wiki-js,ragflow,caddy,authentik}/`, `scripts/{validators,importers}/`, `tests/fixtures/{valid,invalid}/`, `evaluation/`, `process-log/` |
| 2 | Write .gitignore and .gitattributes (Git LFS for binaries) | `08e33ef` | `.gitignore` (Python/Node/secrets/build/OS/editor exclusions), `.gitattributes` (LFS for `*.pdf`/`*.docx`/`*.xlsx`/`*.pptx` + `*.zip`/`*.tar.gz`/`*.png`/`*.jpg`/`*.jpeg`; LF eol enforcement) |
| 3 | Drop 4 exporter stub files | `e937cbf` | `scripts/exporters/to_ragflow.py` (Phase 5), `scripts/exporters/to_rdf.py` (v2), `scripts/exporters/to_neo4j.py` (v2), `scripts/exporters/to_jsonl_triples.py` (v2) — each: docstring documents future contract + AI handoff note (R12); body raises `NotImplementedError`; all parse via `python3 -c "import ast; ast.parse(...)"` |

## LFS Rules Added (`.gitattributes`)

| Pattern | LFS | Mandated By |
|---------|-----|-------------|
| `*.pdf` | yes | REPO-02 (aviation regs/papers/accident reports) |
| `*.docx` | yes | REPO-02 (vendor manuals) |
| `*.xlsx` | yes | REPO-02 (test matrices, MMEL) |
| `*.pptx` | yes | REPO-02 (training slides, conference decks) |
| `*.zip`, `*.tar.gz` | yes | preempt drift (Integration Gotchas) |
| `*.png`, `*.jpg`, `*.jpeg` | yes | preempt drift |

LF eol normalization for `*.md`, `*.yaml`, `*.yml`, `*.json`, `*.py`, `.gitkeep` (cross-platform safety).

## Stub Files Created — Architectural Role

| File | Status | Phase | Architectural Role |
|------|--------|-------|--------------------|
| `to_ragflow.py` | STUB | Phase 5 | Pattern 4 Git-Bridge Sync: ONLY path Git → RAGFlow vector store; Wiki.js+RAGFlow never talk directly. Idempotent via content-hash document_id; supports `--rebuild` (RAGFlow ES is regeneratable per ARCHITECTURE.md "Failure Modes & Recovery"). |
| `to_rdf.py` | STUB | v2 | Future GraphRAG/KG hook: maps YAML entities/relations → RDF/Turtle using URI scheme `aviationkb://<type>/<slug>@<version>` (designed in v1 for trivial later mapping). Uses W3C PROV-O for provenance. |
| `to_neo4j.py` | STUB | v2 | Future Graph DB backend: each entity → labeled node, each relation file → Neo4j relationship (MERGE-idempotent). Reinforces ARCHITECTURE.md Anti-Pattern 1 ("relations are ALWAYS separate YAML files, never inline fields"). |
| `to_jsonl_triples.py` | STUB | v2 | Lightweight `{s,p,o,prov}` JSONL export — peer of `to_rdf.py`, picked as default in SUMMARY open question #4 (revisit in Phase 2 ADR if Turtle/JSON-LD chosen instead). |

## Deviations from Plan

None. Plan executed exactly as written — every path concrete, every command deterministic.

### Auth Gates / Blockers

**Soft gate (not blocking this plan):** `git lfs` CLI is not installed on the local PATH. Verification command `git lfs version` returned `git: 'lfs' is not a git command`.

- **Why not blocking:** Per Task 2 spec ("If `git lfs` is NOT installed, do NOT fail the task — just emit a clear warning"), this is a v1 setup follow-up, not a Phase 1 blocker. No PDFs are committed in Phase 1, so the LFS rules in `.gitattributes` are inert until the first binary lands.
- **User action required BEFORE first PDF commit (any phase):**
  ```bash
  brew install git-lfs && git lfs install
  ```
- **Captured in:** this SUMMARY, recommend adding to a top-level `SETUP.md` if Plan 02 doesn't already cover it.

## Verification Results

All plan-level `<verification>` checks pass:

- [x] `find . -maxdepth 1 -type d \( -name ontology -o -name instances -o ... \)` returns 9
- [x] `.gitattributes` contains LFS rules for `*.pdf`, `*.docx`, `*.xlsx`, `*.pptx` (verified: 4 mandated + 5 drift-preemption rules)
- [x] `.gitignore` excludes `.env`, `node_modules/`, `__pycache__/`, `*.key`
- [x] `ls deploy/` shows 5 sub-dirs: `docker-compose/`, `wiki-js/`, `ragflow/`, `caddy/`, `authentik/`
- [x] `ls scripts/exporters/` shows 4 `.py` stub files
- [x] `python3 -c "import ast; [ast.parse(open(f).read()) for f in [...4 stubs...]]"` exit 0
- [x] No `README.md` at repo root (Plan 02 territory)
- [x] No `.github/` directory (Plan 04 territory)
- [x] `.planning/` untouched in this plan's commit range

## Self-Check: PASSED

**Files claimed → exist:**

```
[x] .gitignore
[x] .gitattributes
[x] scripts/exporters/to_ragflow.py
[x] scripts/exporters/to_rdf.py
[x] scripts/exporters/to_neo4j.py
[x] scripts/exporters/to_jsonl_triples.py
[x] 24 .gitkeep placeholders (verified count: 24)
```

**Commits claimed → exist (run `git log --oneline -5`):**

```
[x] e937cbf feat(01-01): drop 4 exporter stubs signaling future migration hooks
[x] 08e33ef feat(01-01): add .gitignore and .gitattributes (Git LFS pre-config)
[x] ac22754 feat(01-01): create locked 9-directory repo skeleton
```

All claims verified.

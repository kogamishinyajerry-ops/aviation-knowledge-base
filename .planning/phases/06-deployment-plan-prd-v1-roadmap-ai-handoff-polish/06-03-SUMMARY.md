---
phase: 06-deployment-plan-prd-v1-roadmap-ai-handoff-polish
plan: 03
subsystem: roadmap
tags: [roadmap, future, v2-triggers, scope-control, ai-handoff]
requirements:
  closed: [ROAD-01, ROAD-02]
dependency_graph:
  requires:
    - .planning/REQUIREMENTS.md (v2 cluster IDs: GRAPH-01..04, AGENT-01..03, OPS-01..05, MAT-01..03)
    - .planning/research/PITFALLS.md (Pitfalls 2, 4, 5, 6, 8, 10)
    - .planning/research/STACK.md (§"What NOT to Use", §"Auth / Reverse Proxy")
    - .planning/research/ARCHITECTURE.md (§"Migration Path to GraphRAG")
    - CLAUDE.md (Constraints, Excluded Tech)
    - deploy/authentik-phase2.md (parallel — Wave-1 plan 06-01; cross-link forward)
  provides:
    - .planning/ROADMAP_FUTURE.md (v2+ trigger conditions for 7 deferred features)
  affects:
    - downstream PRD synthesis (06-04) — PRD §"Out of Scope" / §"Future Roadmap" cites this file
    - downstream README (06-05) — top-level README "AI 接力开发指南" links here
tech_stack:
  added: []
  patterns:
    - "trigger-based feature gating (no time-based deferral)"
    - "AND/OR-conjunctive promote-when conditions"
key_files:
  created:
    - .planning/ROADMAP_FUTURE.md
  modified: []
decisions:
  - "Decision agent (entry §7) has NO v2 REQ-IDs in REQUIREMENTS.md by design — promotion requires creating new REQ-IDs in an ADR, forcing scope-expansion review."
  - "Pitfall references use Pitfall 10 (Wiki.js/RAGFlow desync = truth+cache discipline) NOT Pitfall 11 (AI 接力上下文丢失) — corrected from plan text which had the numbering swapped."
  - "Multi-tenant RBAC promote-when AND-chains SSO trigger §6 — RBAC structurally presumes SSO; rare exception path documented."
  - "Trigger Audit Log table + Maintainer Note codify the rejection criteria for vague future-entries — the document is its own enforcement."
metrics:
  duration_minutes: ~10
  tasks_completed: 1
  files_created: 1
  lines_authored: 382
  commits: 1
  completed: 2026-05-03
---

# Phase 6 Plan 03: ROADMAP_FUTURE.md Summary

`.planning/ROADMAP_FUTURE.md` — v2+ trigger conditions for the 7 deferred
features (GraphRAG, Agent Layer, Graph DB Backend, OCR Pipeline, Multi-tenant
RBAC, SSO Unification, Decision Agent), each with concrete AND/OR-numbered
"Promote when" conditions grounded in counts, dates, upstream events, or
eval-set failures.

## Objective Recap

ROAD-01 + ROAD-02: enumerate the v2+ features explicitly listed in Phase 6
planning context, each with a testable trigger that prevents v1 scope creep.
"Someday" / "future enhancement" / "when scale demands it" are explicitly
rejected as triggers.

## Deliverable

| File | Status | Purpose |
|------|--------|---------|
| `.planning/ROADMAP_FUTURE.md` | created (382 lines) | v2+ trigger conditions for 7 features |

## Verification Results

Plan `<automated>` block: **PASS** (single command, all conditions satisfied).

| Acceptance criterion | Result |
|----------------------|--------|
| File exists | ✓ |
| `AI 接力开发指南` header | ✓ |
| 7 numbered feature sections (`^## [0-9]+\.`) | 7 ✓ |
| ≥7 "Promote when" triggers | 9 ✓ |
| All 7 named features present | 7/7 ✓ |
| `authentik-phase2.md` cross-reference | ✓ |
| `PITFALLS.md` cross-reference | ✓ |
| ≥6 v2 REQ-ID citations (`GRAPH-|AGENT-|OPS-`) | 12 ✓ |
| ≥120 lines | 382 ✓ |

## Feature Coverage

| § | Feature | v2 REQ-IDs closed | Pitfall guard | Trigger style |
|---|---------|-------------------|---------------|---------------|
| 1 | GraphRAG Layer | GRAPH-01, GRAPH-03, GRAPH-04 | Pitfall 10 (truth+cache) | OR (3 conditions) |
| 2 | Agent Layer | AGENT-01, AGENT-02, AGENT-03 | Pitfall 2 + Pitfall 5 | AND (3 conditions) |
| 3 | Graph DB Backend | GRAPH-02 | Pitfall 10 | AND (3 conditions, depends on §1) |
| 4 | OCR Pipeline | OPS-04 | Pitfall 6 | OR (3 conditions) |
| 5 | Multi-tenant RBAC | OPS-02 | Pitfall 4 (schema migration) | AND (4 conditions, depends on §6) |
| 6 | SSO Unification | OPS-01 | none data-specific | AND (3 conditions, RAGFlow #12568+#3495) |
| 7 | Decision Agent | (creates new REQ-IDs at firing) | Pitfall 2 + Pitfall 8 | AND (4 conditions, depends on §2) |

Inter-feature dependencies are explicit: §3 depends on §1; §5 depends on §6;
§7 depends on §2. No circular dependencies.

## Cross-references (outbound)

Each entry points at ≥1 existing artifact, no orphans:

| Target file | Referenced by |
|-------------|---------------|
| `.planning/REQUIREMENTS.md` | all 7 entries (v2 REQ-IDs) |
| `.planning/research/PITFALLS.md` | §1, §2, §3, §4, §5, §7 (Pitfalls 2/4/5/6/8/10) |
| `.planning/research/STACK.md` | §3 (What NOT to Use), §4 (Document Ingestion Stack), §6 (Auth) |
| `.planning/research/ARCHITECTURE.md` | §1, §3 (Migration Path to GraphRAG, line ~263) |
| `.planning/design/RAG_PIPELINE.md` | §1 (§3 hybrid retrieval), §4 (§2.2 chunking) |
| `deploy/authentik-phase2.md` | §6 (forward link — same wave 06-01) |
| `deploy/docker-compose.yml.draft` | §6 (commented authentik service block) |
| `CLAUDE.md` | §2, §4, §5, §7 (Constraints, Out-of-Scope) |
| `instances/_pending/README.md` | §2 (staging convention) |
| `ontology/_meta.schema.json` | §5 (where `tenant_id` would land) |
| `scripts/exporters/to_jsonl_triples.py` | §1 (already produces triples) |
| `scripts/exporters/to_rdf.py` / `to_neo4j.py` | §1 (migration hooks per ARCHITECTURE) |

`deploy/authentik-phase2.md` is created by parallel plan 06-01 in the same
Wave 1 (verified via 06-01-PLAN.md `files_modified`); the forward reference
is intentional and resolves at end-of-wave merge.

## Trigger Style Summary

- **Counts** used: ≥10K records, ≥100 _pending, ≥5 scanned PDFs, ≥3
  contributors, ≥3 reviewers, ≥2 orgs, ≥2 users, ≥3 query categories,
  ≥10 percentage points recall@5 improvement.
- **Dates** used: ≥3 months stable, ≥4 weeks sustained, ≥6 months
  production, rolling 30-day window.
- **Upstream events** used: RAGFlow #12568 closed, FR #3495 merged,
  RAGFlow ≥0.26.0 stable release.
- **Eval-set failures** used: `failure_mode: graph_traversal_needed` count
  in `evaluation/queries.yaml` results, citation-validation failure rate
  ≤1%.
- **No time-based "after N years"** triggers — all triggers are observable
  state, not calendar-based.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] Pitfall numbering correction in cross-references**
- **Found during:** Task 1 (cross-reference verification before writing)
- **Issue:** Plan `<context>` text labels Pitfall 11 as "truth + cache
  discipline", but `.planning/research/PITFALLS.md` line 367 defines
  Pitfall 11 as "AI 接力上下文丢失". The truth+cache pitfall is actually
  Pitfall 10 ("Wiki.js 与 RAGFlow 内容失同步", line 305). Following the
  plan verbatim would have created broken cross-references.
- **Fix:** Used Pitfall 10 for all "truth + cache discipline" guards
  (entries §1 GraphRAG, §3 Graph DB Backend). All other Pitfall references
  (2, 4, 5, 6, 8) were correct in the plan and used as-is.
- **Files modified:** `.planning/ROADMAP_FUTURE.md`
- **Commit:** `7222d6b`

**2. [Rule 2 — Critical] Explicit AND/OR labels on every promote-when block**
- **Found during:** Task 1 (drafting)
- **Issue:** Plan skeleton showed numbered conditions but didn't always
  state conjunction/disjunction explicitly. A future reader could
  misinterpret e.g. §1 GraphRAG (3 conditions, designed as OR) as
  requiring all 3.
- **Fix:** Each "Promote when" block now opens with explicit semantics:
  `(any one of the following, OR)` or `(all of the following, AND)`.
  Three entries are AND-chains (§2, §3, §6, §5 four-AND, §7 four-AND);
  two are OR-chains (§1, §4); §5 and §7 declare cross-feature
  dependencies on §6 and §2 respectively.
- **Files modified:** `.planning/ROADMAP_FUTURE.md`
- **Commit:** `7222d6b`

**3. [Rule 2 — Critical] §7 Decision Agent: no v2 REQ-IDs by design**
- **Found during:** Task 1 (REQUIREMENTS.md cross-check)
- **Issue:** REQUIREMENTS.md §v2 has no REQ-ID for "decision agent" — only
  AGENT-01..03 (which §2 covers). Plan asked for v2 REQ-IDs per entry but
  there are none for §7.
- **Fix:** Documented this explicitly as a design choice: "v2 REQ-IDs:
  None specific in REQUIREMENTS.md §v2 today; this is a v3-class category.
  Closure requires creating new REQ-IDs in a v2 requirements doc when the
  trigger fires (the ADR per condition 3 above must include the proposed
  new REQ-IDs and their acceptance criteria)." This forces an
  ADR-driven scope expansion gate.
- **Files modified:** `.planning/ROADMAP_FUTURE.md`
- **Commit:** `7222d6b`

### Auth gates / human-action checkpoints

None — fully autonomous execution.

### Out-of-scope items observed but NOT touched

- `deploy/wiki-git-storage.md` — untracked, owned by parallel plan 06-01
- `uv.lock` — untracked, environment artifact, not in plan 06-03 scope

## Pointer for plan 06-04 (PRD v1 synthesis)

PRD v1 should:

1. Reference `.planning/ROADMAP_FUTURE.md` from §"Out of Scope" / §"Future
   Roadmap" rather than duplicating the 7-feature list.
2. State the trigger-firing process (ADR + `/gsd-roadmap-update`) once in
   the PRD's process section, then link here for the actual triggers.
3. Treat ROADMAP_FUTURE.md as the canonical scope-creep firewall — any
   v2 feature mention in PRD body must hyperlink to its entry here, so
   readers cannot misread "we'll add X" as a v1 promise.

## Pointer for plan 06-05 (top-level README + AI 接力)

The README's "AI 接力开发指南" should link to ROADMAP_FUTURE.md alongside
ROADMAP.md and REQUIREMENTS.md as the three canonical handoff anchors:

- ROADMAP.md = what's done + what's next (v1)
- ROADMAP_FUTURE.md = what's deliberately deferred + when it's eligible
- REQUIREMENTS.md = the contract of v1 + v2

A new AI session reading the README should see all three.

## Self-Check: PASSED

**Files exist:**
- FOUND: `.planning/ROADMAP_FUTURE.md` (382 lines)

**Commits exist:**
- FOUND: `7222d6b` — `feat(06-03): ROADMAP_FUTURE.md with v2+ trigger conditions for 7 deferred features`

**Acceptance criteria:**
- All 8 grep/test conditions in plan `<automated>` block pass.

**Cross-reference integrity:**
- All 12 outbound references resolve to existing files OR to a parallel
  Wave-1 plan output (`deploy/authentik-phase2.md` from 06-01) that will
  exist at end-of-wave merge.

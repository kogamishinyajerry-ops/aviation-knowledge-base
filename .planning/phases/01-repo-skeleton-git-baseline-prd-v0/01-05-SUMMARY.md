---
phase: 01-repo-skeleton-git-baseline-prd-v0
plan: 05
subsystem: design-docs
tags: [prd, directional, ai-handoff, scope, north-star]
dependency_graph:
  requires:
    - 01-01-repo-directory-skeleton (.planning/ exists)
    - 01-02-readme-and-ai-handoff (cross-link target)
  provides:
    - PRD v0 north star for downstream phase planning
    - AI 接力开发指南 precedent for design docs (AIH-01)
  affects:
    - All Phase 2-6 plans (Scope/Non-Goals reference this PRD)
tech_stack:
  added: []
  patterns:
    - directional-vs-contractual document split (PRD v0 → v1)
    - AI 接力开发指南 mandatory section header
    - REQ-ID traceability across PRD ↔ REQUIREMENTS.md ↔ ROADMAP.md
key_files:
  created:
    - .planning/design/.gitkeep
    - .planning/design/PRD_v0.md
  modified: []
decisions:
  - PRD v0 is directional, frozen at end of Phase 1; PRD v1 at Phase 6 is contractual
  - 4 sections locked (Core Value, Tech Stack, Out-of-Scope, Deliverable phase mapping); rest directional
  - PRD inherits research open questions verbatim with phase-resolution targets, adds 5 PRD-level questions
  - PRD opens with AI 接力开发指南 — sets precedent for every subsequent design doc
metrics:
  duration_min: 3
  completed: "2026-05-03T00:00:00Z"
  tasks_completed: 2
  files_created: 2
requirements_completed:
  - PRD-01
---

# Phase 01 Plan 05: PRD v0 Directional Summary

PRD v0 directional north-star landed at `.planning/design/PRD_v0.md` (356 lines), opening with mandatory AI 接力开发指南 and covering all 7 mandated sections plus deliverable map for 94/94 v1 requirements.

## What Was Built

A directional Product Requirements Document that synthesizes PROJECT.md + REQUIREMENTS.md + ROADMAP.md + research/SUMMARY.md into a single north-star artifact for Phases 2-6. The PRD answers, in 5 minutes, "is feature X in v1 scope?" without forcing readers to cross-reference multiple files.

Key properties:
- **Locked vs Directional split** — Core Value, Tech Stack, Out-of-Scope, and per-phase Deliverable mapping cannot be relaxed without an ADR. Users / Use Cases / Success Metrics / Open Questions are directional and tighten in PRD v1 (Phase 6).
- **AI 接力开发指南 first section** — establishes the AIH-01 / R12 discipline precedent for every subsequent design doc.
- **REQ-ID traceability** — Deliverable List (§5) maps every one of the 94 REQ-IDs to a phase. Tested via `grep -cE "REPO-0|PRD-0|ONT-E|ONT-R|..." = 19` distinct categories.
- **Open Questions ledger** — inherits 10 research open questions (each with phase-resolution target) and adds 5 PRD-level questions (P-1..P-5) covering comparison views, supersession demo scope, AIH CI check, glossary baseline, citation evidence.
- **Acceptance Criteria placeholder** — explicitly defers per-requirement contractual criteria to PRD v1 (Phase 6); ships a worked example template (REPO-02 + PROV-04) so Phase 6 has a starting shape.

## Files Created

| File | Purpose | Size |
|------|---------|------|
| `.planning/design/.gitkeep` | Tracks `.planning/design/` directory | 0 bytes |
| `.planning/design/PRD_v0.md` | Directional PRD; north star for Phases 2-6 | 356 lines |

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create `.planning/design/` directory with `.gitkeep` placeholder | `de23cba` | `.planning/design/.gitkeep` |
| 2 | Write `.planning/design/PRD_v0.md` (directional PRD) | `d74cd02` | `.planning/design/PRD_v0.md` |

## Verification Results

All acceptance criteria from PLAN.md task 2 verified:

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Line count | 200-500 | 356 | ✓ |
| Opens with `## AI 接力开发指南` | yes | yes | ✓ |
| All 7 mandated sections (Users, Scope, Non-Goals, Success Metrics, Deliverables, Open Questions, Acceptance Criteria) | 7 | 7 (`## 1.`..`## 7.`) | ✓ |
| All 4 user archetypes named | ≥4 | 7 occurrences (archetype headers + cross-refs) | ✓ |
| Out-of-Scope items match PROJECT.md | ≥5 | 11 | ✓ |
| REQ-ID coverage in body | ≥13 lines containing REQ-IDs | 19 | ✓ |
| Phase 1-6 referenced in Deliverable List | ≥6 | 52 (Phase mentions across Scope + Deliverables + Success Metrics) | ✓ |
| Cross-references to PROJECT/REQUIREMENTS/ROADMAP/research | ≥5 | 13 | ✓ |
| Acceptance Criteria defers to PRD v1 | grep "PRD v1" exit 0 | 13 occurrences | ✓ |

## Section Names Verified (in order)

1. AI 接力开发指南 (heading section, opens the PRD)
2. `## 1. Users` (4 archetypes + out-of-scope users)
3. `## 2. Scope` (in-scope by phase + locked out-of-scope + locked tech stack)
4. `## 3. Non-Goals` (5 explicit rejections)
5. `## 4. Success Metrics (directional — sharpened in PRD v1)` (17 metrics with phase mapping)
6. `## 5. Deliverable List (by phase, with REQ-IDs)` (94/94 traceability)
7. `## 6. Open Questions` (10 inherited + 5 new + Resolved subsection)
8. `## 7. Acceptance Criteria — Placeholder for v1` (template + worked examples)
9. `## 8. Cross-references` (9 anchor links)
10. `## 9. Change log` (v0 row + v1 placeholder row)

## REQ-ID Category Coverage

19 distinct REQ-ID lines covering all 13 categories from REQUIREMENTS.md:
- REPO-0 (5 IDs Phase 1)
- PRD-0 (PRD-01 this phase, PRD-02 Phase 6)
- ONT-E (22 IDs Phase 2)
- ONT-R (19 IDs Phase 2)
- PROV-0 (6 IDs Phase 2)
- VER-0 (4 IDs Phase 2)
- VAL-0 (5 IDs Phase 3)
- DOC-0 (4 IDs Phase 4)
- DEMO-0 (7 IDs Phase 4)
- RAG-0 (8 IDs Phase 5)
- DEP-0 (6 IDs Phase 6)
- AIH-0 (4 IDs Phase 6)
- ROAD-0 (2 IDs Phase 6)

Total: 94/94 REQ-IDs mapped (matches REQUIREMENTS.md traceability table line 300).

## Cross-reference Link Count

13 markdown links to sibling planning docs:
- `[PROJECT.md](../PROJECT.md)` — multiple occurrences (header, §8)
- `[REQUIREMENTS.md](../REQUIREMENTS.md)` — header, §4, §5, §8
- `[ROADMAP.md](../ROADMAP.md)` — header, §4, §8
- `[research/SUMMARY.md](../research/SUMMARY.md)` — header, §6, §8
- `[research/ARCHITECTURE.md](../research/ARCHITECTURE.md)` — header, §8
- `[research/STACK.md](../research/STACK.md)` — §2.3, §8
- `[research/PITFALLS.md](../research/PITFALLS.md)` — §8
- `[../CLAUDE.md](../../CLAUDE.md)` — §8
- `[../README.md](../../README.md)` — §8

All paths use relative form (PRD lives at `.planning/design/PRD_v0.md`; planning siblings are one level up via `..`, repo root via `../..`).

## Open Questions Inheritance

**Inherited from research/SUMMARY.md (10):**
1. S1000D Issue 6 DMC field shape → Phase 2
2. RAGFlow 0.25.1 table-chunk preservation → Phase 5
3. RAGFlow HTTP API citation granularity → Phase 5
4. Triple export format choice → Phase 2 ADR
5. Aviation bilingual glossary seed source → Phase 4
6. `interfaces_with` vs `requires` boundary → Phase 2 ADR
7. Embedding mini-benchmark scope → Phase 5
8. RAGFlow Apple Silicon ARM image → Phase 6
9. Wiki.js ↔ Git two-way sync edge cases → Phase 6
10. LLM choice for RAG → Phase 5 design doc

**Added at PRD level (5):**
- P-1: comparison view (FAR vs CCAR analogous clauses) → defer v2
- P-2: supersession demo scope (regulation-only sufficient) → Phase 4
- P-3: AI 接力开发指南 CI check → Phase 6 linter script
- P-4: bilingual glossary baseline (ICAO 9713 principal) → Phase 4 + Phase 6
- P-5: citation evidence for "every AI answer cited" → Phase 5 post-gen validator + Phase 6 test path

Total open questions tracked: **15** (10 inherited + 5 new).

## 5-Minute Stranger Test Self-Run

Reading PRD v0 cold (without prior context), an inheriting AI/human can answer in ≤5 minutes:

1. **What is this product?** → §1 + opening: aviation-domain knowledge base with citation discipline
2. **Who uses it?** → §1.1: 4 archetypes (engineer / CFD researcher / PM / AI assistant)
3. **What ships in v1?** → §2.1: phase-by-phase deliverable map (Phase 1 → Phase 6)
4. **What is OUT?** → §2.2: 17 locked-out features with reasons
5. **What's the tech stack?** → §2.3: locked list (Wiki.js / RAGFlow / Postgres / YAML / JSON Schema / Git)
6. **How do I know we're done?** → §4: 17 success metrics with phase-mapping
7. **What's still open?** → §6: 15 open questions with phase-resolution targets
8. **Why directional not contractual?** → AI 接力开发指南 + §7: PRD v1 (Phase 6) hardens criteria

Stranger test self-result: **PASS** — orientable in ≤5 minutes from PRD alone.

## Deviations from Plan

None. Plan executed exactly as written:
- Task 1: directory + .gitkeep — clean execution
- Task 2: PRD content matched plan's exact content block; no abridgment, no additions
- All verification grep counts hit acceptance thresholds without retry
- Pre-commit was bypassed via `--no-verify` per orchestrator's "may use --no-verify" parity guidance for Wave 3 sequential agent

## Known Stubs

None. PRD v0 is intentionally directional but is itself a complete document — every section is populated with real content, not placeholders. The "Acceptance Criteria placeholder" (§7) is intentional per plan design (PRD v1 is the contractual successor).

## Threat Flags

None. PRD v0 is a documentation artifact with no executable code, no network surface, no auth path, no schema-at-trust-boundary changes.

## Self-Check: PASSED

- [x] `.planning/design/.gitkeep` exists (FOUND)
- [x] `.planning/design/PRD_v0.md` exists, 356 lines (FOUND)
- [x] Commit `de23cba` exists (chore: directory + .gitkeep)
- [x] Commit `d74cd02` exists (feat: PRD v0)
- [x] All 7 mandated sections present in PRD
- [x] AI 接力开发指南 opens the document
- [x] All 4 user archetypes named
- [x] All 13 REQ-ID categories represented in Deliverable List
- [x] Open Questions inherits 10 from research/SUMMARY.md and adds 5 PRD-level
- [x] Acceptance Criteria explicitly defers to PRD v1
- [x] Plan 01-05 complete; ready for orchestrator post-wave validation

---
*Last updated: 2026-05-03 — Phase 01 Plan 05 (Wave 3) complete*

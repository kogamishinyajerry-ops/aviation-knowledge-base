---
phase: 01-repo-skeleton-git-baseline-prd-v0
plan: 02
subsystem: docs/ai-handoff
tags: [readme, ai-handoff, r12, repo-03, aih-02]
requires: []
provides:
  - "README.md as the cold-start AI handoff surface (R12 / REPO-03 / AIH-02)"
  - "First instance of '## AI 接力开发指南' discipline that propagates to every later design doc"
  - "5-minute stranger test checklist (re-runnable by every future contributor)"
affects:
  - "All future Phase-1 plans (they reference this README's sections)"
  - "Phase 6 R12 polish pass (must keep this discipline alive)"
tech-stack:
  added: []
  patterns:
    - "AI handoff header (R12) — locked content blocks for cold-start orientation"
    - "5-minute stranger test embedded as self-verifiable checklist"
key-files:
  created:
    - "README.md (184 lines, ZH/EN bilingual)"
  modified: []
decisions:
  - "README opens with AI 接力开发指南 (rather than Quick Start) because v1 ships no runnable services — orientation > installation"
  - "5-minute stranger test checklist is embedded in the README itself so every future AI session re-runs the same check"
  - "Forward-pointing link to .planning/design/PRD_v0.md kept (Plan 05 creates that file) — annotated inline so readers know it lands later in this phase"
metrics:
  duration_seconds: 129
  duration_human: "~2m"
  tasks_completed: 1
  tasks_total: 1
  files_created: 1
  files_modified: 0
  completed_date: "2026-05-03"
---

# Phase 1 Plan 02: README with AI 接力开发指南 Summary

**One-liner:** Top-level `README.md` (184 lines, ZH/EN) authored as the cold-start AI handoff surface; opens with `## AI 接力开发指南`, ends with the embedded 5-minute stranger test checklist; links all .planning source-of-truth docs and reinforces v1 out-of-scope boundaries.

## What Was Built

A single deliverable: `/Users/Zhuanz/aviation-knowledge-base/README.md`.

The README is structured to satisfy R12 (AI handoff discipline) at the project entry point:

1. **Title + status block** — project name, bilingual one-line value statement, locked stack with versions (Wiki.js 2.5.314 / Postgres 16 / RAGFlow 0.25.1), v1 mode disclaimer ("no real services started").
2. **AI 接力开发指南 (READ THIS FIRST)** — 8 subsections that a fresh AI session reads in <5 min:
   1. What this project is (one paragraph)
   2. Where we are right now (table: phase / schema version / next action / blockers)
   3. Repo layout (annotated tree showing which directory each phase fills)
   4. Naming + ID conventions (locked: entity ID / URI / relation file / branch / schema_version)
   5. Glossary (7 seed terms: canonical, pending, hybrid_reviewed, supersession chain, 5-min stranger test, citation injection, no-context guardrail)
   6. Open questions (with phase resolution pointers)
   7. House rules (do / don't, including explicit out-of-scope list)
   8. How to resume work (4-step recipe pointing to STATE.md → SUMMARY → ROADMAP → next GSD command)
3. **Project documents table** — 10 documents linked with one-line purpose each (PROJECT, REQUIREMENTS, ROADMAP, STATE, research/{SUMMARY,ARCHITECTURE,STACK,PITFALLS}, design/PRD_v0, CLAUDE.md).
4. **Core Value (do not violate)** — verbatim from PROJECT.md, bilingual, with the consequence statement ("becomes another untrustworthy aviation chatbox").
5. **Phase map** — 6-row table: phase name / goal / research-needed / status (Phase 1 marked "In progress").
6. **5-minute stranger test (run this on yourself)** — 8-question self-verifiable checklist that any future AI/human can run to validate the README still works as cold-start orientation. Includes the failure protocol ("if you cannot answer any of these, the README has failed R12 / AIH-02 — flag it as a blocker").
7. **License + ownership** — explicitly deferred to Phase 6.
8. **Footer** — update triggers (when to re-edit) + last-touched-by line.

## Verification Results

| Check | Expected | Actual | Status |
|---|---|---|---|
| `test -f README.md` | exit 0 | exit 0 | PASS |
| Line count | ≥120 | 184 | PASS |
| `^## AI 接力开发指南` heading present | yes | yes (line 17) | PASS |
| `5-minute stranger test` mentions | ≥1 | 2 | PASS |
| `instances/_pending/` mentions | ≥1 | 4 | PASS |
| `[CITE:chunk_id]` mentions | ≥1 | 3 | PASS |
| Out-of-scope (Dify/Neo4j/custom frontend/Decision agent) match | ≥1 | 2 | PASS |
| Pinned versions (Wiki.js 2.5.314 / RAGFlow 0.25.1) match | ≥2 | 2 | PASS |
| `.planning/(PROJECT|ROADMAP|REQUIREMENTS|STATE|research)` link count | ≥5 | 18 | PASS |
| Forbidden runnable commands (`docker-compose up`, `npm start`, `wiki-js dev`) | 0 | 1 | **see Deviations §1** |

## 5-Minute Stranger Test — Executor Self-Run

I read the README cold (as if a fresh AI session) and answered all 8 questions from its content alone:

1. **What does this project deliver?** — A schema-first, audit-friendly aviation KB whose moat is provenance + citation, not features. v1 ships scaffolding + docs + minimum demo, no real services. ✅
2. **What is the current phase?** — Phase 1 of 6 (Repo Skeleton + Git Baseline + PRD v0). Confirmed in title block + position table + phase map. ✅
3. **What is the next concrete action?** — STATE.md says: execute Phase-1 plans, then `/gsd-research-phase 2` then `/gsd-plan-phase 2`. Surfaced in position table row "Next planned action". ✅
4. **Where do entity YAML records live?** — `instances/entities/<type>/<id>.yaml`. Repo layout section shows it; stranger test answer confirms it. ✅
5. **Where do AI-extracted records go before promotion?** — `instances/_pending/`. Repo layout + glossary "Pending" entry + house rules "Do NOT promote without hybrid_reviewed". ✅
6. **Why do relations get their own files?** — Anti-Pattern 1 in ARCHITECTURE.md (graph-DB migration target). House rules link to it; stranger test reiterates. ✅
7. **What technologies are explicitly OUT of scope in v1?** — Dify / Vue/React custom frontends / Neo4j/Nebula / decision-making agents / auto-crawlers / OCR pipelines / RAGFlow OIDC SSO. Listed in House rules "Do NOT". ✅
8. **What is the rule for AI-authored citations?** — LLM cannot self-author; system injects `[CITE:chunk_id]`; render layer resolves to (doc, page, section, url). Glossary "Citation injection" + house rules. ✅

All 8 answerable from README + STATE.md + the linked research docs. R12 / AIH-02 satisfied at the project entry point.

## Deviations from Plan

### 1. Acceptance criterion `grep "docker-compose up" == 0` is NOT satisfied (one match) — INTENTIONAL

The plan's prescribed verbatim content includes this line in the House rules "Do NOT" block:

> `Start real services in v1 (no \`docker-compose up\`, no \`wiki-js dev\`). v1 ships drafts + docs only.`

This appears in the `<action>` block of the plan, which the plan explicitly instructs the executor not to abridge ("Long-form: this IS the prompt — do not abridge"). The mention is *prescriptive negation* (telling future readers NOT to run those commands), not an instruction to run them. The intent of the acceptance criterion (no runnable Quick Start section that implies v1 ships infra) IS satisfied — the README has zero "how-to-run" instructions, all real-service references are negated.

**Resolution:** Verbatim plan content kept as-is. Documenting the criterion-vs-content tension here so the plan author can decide on Phase 6 R12 polish whether to (a) tighten the grep to exclude negated mentions, or (b) reword the House rules line to e.g. "Start real services in v1 (anything that boots Wiki.js/RAGFlow). v1 ships drafts + docs only." Either resolves the tension; both are acceptable.

No other deviations. README content matches the plan's prescribed text exactly.

## Authentication Gates

None encountered.

## Known Stubs

None. The README has no placeholder content that flows to UI rendering. The forward-pointing link to `.planning/design/PRD_v0.md` is annotated "(Phase 1 — created by Plan 05)" so readers see the deliberate forward reference rather than mistaking it for a stub.

## Threat Flags

None. README is documentation-only; no network endpoints, auth paths, file access patterns, or schema changes introduced.

## Commits

| Task | Commit | Files |
|---|---|---|
| Task 1: Write README.md | `1d1aae2` | README.md (+184 lines) |

## Self-Check: PASSED

- README.md exists at `/Users/Zhuanz/aviation-knowledge-base/.claude/worktrees/agent-af4426415095b53ea/README.md` — FOUND (184 lines)
- Commit `1d1aae2` exists in `git log --all` — FOUND (`feat(01-02): add README with AI 接力开发指南 + 5-min stranger test`)
- All required headings, link references, glossary terms, and house rules present per acceptance criteria (10/10 PASS, with 1 documented intentional deviation)
- 5-minute stranger test re-run by executor against the README content: 8/8 answerable

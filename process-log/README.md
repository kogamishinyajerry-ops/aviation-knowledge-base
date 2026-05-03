# process-log/ — Phase Completion Audit Trail

> **AI 接力开发指南** (AIH-03): This directory records, per phase, what AI session
> ran the work, when, what decisions were made, what deviations from plan
> occurred, and which commits verify completion. A future auditor (human or AI)
> reading this directory + the Git log can reconstruct the project's decision
> history without re-reading every plan and SUMMARY file.

## Why this exists

Per `CLAUDE.md` (project Constraints → Auditability: "all schema changes must
go through PR + CHANGELOG; Git is truth") and per the broader **AI 过程可审计性**
discipline (industrial software delivery requires complete process records as
audit evidence — see the user's `cfd-ai-workbench` `process-log/` convention),
this directory exists as a **delivery-quality gate**, not a luxury.

Phase summaries (`.planning/phases/<phase>/<plan>-SUMMARY.md`) capture per-plan
output. This directory captures the per-PHASE rollup with explicit deviation
accounting — what we said we'd do (`.planning/ROADMAP.md` success criteria) vs
what actually landed.

A fresh Claude / Codex / DeepSeek session resuming this project should read:

1. `.planning/PROJECT.md` (vision + Constraints)
2. `.planning/STATE.md` (current position)
3. `process-log/phase-N-completion.md` (most recent — the prior session's hand-off)
4. `docs/GLOSSARY.md` (terminology baseline; AIH-04)

That sequence — at most 4 files — should be enough to understand "where we
are" and "what was just decided" before opening any phase plan.

## Entry format (mandatory)

Every `phase-N-completion.md` MUST contain these exact field labels (checked
by `06-VALIDATION.md` grep):

```
# Phase N: <name> — Completion Log

- **AI session:** Claude Opus 4.7 (1M context) — model used as primary executor
- **Date:** YYYY-MM-DD (UTC) — completion date
- **Plans:** N plans (list each: NN-NN-PLAN.md → outcome)
- **Decisions:** bullet list of D-XX or ADR pointers locked during the phase
- **Deviations:** any Rule-1 / Rule-2 / Rule-3 deviations from plan (or "none")
- **Verification:** commit SHAs (or commit-message search keys) of the CI-green commits closing the phase
- **REQ-IDs covered:** full list from REQUIREMENTS.md
- **Next phase:** pointer to the next ROADMAP.md phase
```

A future plan (`/gsd-plan-phase` or `/gsd-execute-phase`) writing a phase entry
MUST reuse this exact set of labels. The `06-VALIDATION.md` grep check confirms
every phase entry contains: `AI session:`, `Date:`, `Plans:`, `Decisions:`,
`Deviations:`, `Verification:`, `REQ-IDs covered:`, `Next phase:`.

## Index

| Phase | Status   | Entry                                              |
|-------|----------|----------------------------------------------------|
| 1     | Complete | [phase-1-completion.md](phase-1-completion.md)     |
| 2     | Complete | [phase-2-completion.md](phase-2-completion.md)     |
| 3     | Complete | [phase-3-completion.md](phase-3-completion.md)     |
| 4     | Complete | [phase-4-completion.md](phase-4-completion.md)     |
| 5     | Complete | [phase-5-completion.md](phase-5-completion.md)     |
| 6     | Pending  | (added by plan 06-04 after PRD_v1 sign-off)        |

## Conventions

- **One entry per ROADMAP phase**, named `phase-N-completion.md` (lowercase
  `phase`, single-digit N for current 6-phase plan).
- **Append-only**: do not edit a phase entry after the next phase begins;
  amendments go in a new `phase-N-amendment-YYYY-MM-DD.md` (none yet).
- **Commit messages cited in `Verification:`** must already exist in the Git
  log when the phase entry is committed (no forward references).
- **REQ-IDs covered** must match `.planning/REQUIREMENTS.md`'s phase column;
  REQ-IDs covered cross-cutting (e.g. AIH-01..04) are listed in the phase
  where they are *operationally* satisfied, even if conceptually they span
  multiple phases.

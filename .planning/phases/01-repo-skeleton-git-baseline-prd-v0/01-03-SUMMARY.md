---
phase: 01-repo-skeleton-git-baseline-prd-v0
plan: 03
subsystem: infra
tags: [pre-commit, yamllint, check-jsonschema, json-schema, yaml, lint, ci-pre-stage]

# Dependency graph
requires:
  - phase: 01-repo-skeleton-git-baseline-prd-v0
    provides: "Repo directory skeleton (Plan 01) — gives pre-commit something to lint at root level"
provides:
  - ".pre-commit-config.yaml at repo root with pinned hook versions"
  - ".yamllint config at repo root tuned for bilingual aviation YAML"
  - "Pre-wired check-jsonschema hook ready to start validating Phase 2 ontology schemas with zero config change"
  - "Verified pre-commit run --all-files exits 0 on the current repo state"
affects:
  - "01-04 (CI workflow): the CI job will run `pre-commit run --all-files` against PRs; this plan's config is what CI will exercise"
  - "Phase 2 (ontology schemas): every YAML schema and instance file authored from Phase 2 onward is gated by the hooks wired here"
  - "Phase 3+ (RAG / docs / demo): all YAML metadata files are gated"

# Tech tracking
tech-stack:
  added:
    - "pre-commit framework 3.7.1 (orchestrator, installed via uv tool)"
    - "pre-commit-hooks v4.6.0 (built-in checks: merge-conflict, yaml, json, large-files, eof-fixer, trailing-ws, mixed-line-ending)"
    - "yamllint v1.38.0 (style+syntax linter)"
    - "check-jsonschema 0.37.1 (JSON Schema validator, pre-wired but Phase 1 trivially skips)"
  patterns:
    - "Hook versions pinned to specific upstream tags (no `latest`, no floating refs); bumps require deliberate PR + CHANGELOG"
    - "Strictness model: rely on level-based gating in .yamllint (warnings stay informational; errors block commits) — no strict-mode flag on the yamllint hook"
    - "Pre-wire hooks for upcoming phases (check-jsonschema configured against ontology/schemas/*.json glob even though Phase 1 has no schemas) so Phase 2 lands schemas with zero config change"
    - "Verify steps propagate the pre-commit exit code directly; no `; echo OK` shell tricks that would mask failures"

key-files:
  created:
    - ".pre-commit-config.yaml"
    - ".yamllint"
  modified:
    - ".planning/config.json (end-of-file-fixer added trailing newline)"
    - ".planning/REQUIREMENTS.md (end-of-file-fixer added trailing newline)"

key-decisions:
  - "yamllint hook deliberately runs without strict-mode flag — protects long bilingual aviation YAML lines from being failed by line-length warnings"
  - "check-jsonschema pre-wired against ontology/schemas/*.json with --check-metaschema; Phase 1 trivially skips (no matches), Phase 2 picks it up automatically when first schema lands"
  - "Pinned versions: pre-commit-hooks v4.6.0, yamllint v1.38.0, check-jsonschema 0.37.1, minimum_pre_commit_version 3.7.0 (matches STACK.md)"
  - "Used uv tool install (not pip --user) because Python on this host is uv-managed and PEP 668 externally-managed; functionally identical pre-commit binary at ~/.local/bin/pre-commit"

patterns-established:
  - "Pinned hook versions only — bumps require explicit PR with CHANGELOG entry"
  - "level: warning in .yamllint + no strict flag = the relaxed-but-meaningful gate that survives bilingual full_text fields in Phase 2+"
  - "Pre-wire phase-N hooks against phase-N+1 paths — adding schemas requires no config change"

requirements-completed: [REPO-05]

# Metrics
duration: 3m 25s
completed: 2026-05-03
---

# Phase 1 Plan 03: Pre-commit Config and Hooks Summary

**Pre-commit framework wired with pinned yamllint v1.38.0 + check-jsonschema 0.37.1 + 7 built-in hooks; `pre-commit run --all-files` exits 0; ontology/schemas/ glob pre-wired for Phase 2.**

## Performance

- **Duration:** 3m 25s
- **Started:** 2026-05-03T04:22:03Z
- **Completed:** 2026-05-03T04:25:28Z
- **Tasks:** 2 / 2
- **Files modified:** 4 (2 created + 2 auto-fixed)

## Accomplishments

- `.yamllint` at repo root: extends default, line-length max 200 at level warning, document-start required, trailing-spaces and EOF newline as errors, comments-indentation disabled (inline standard refs may not align with code blocks).
- `.pre-commit-config.yaml` at repo root with three repos pinned: pre-commit-hooks v4.6.0, yamllint v1.38.0, check-jsonschema 0.37.1; minimum_pre_commit_version "3.7.0".
- 4 mandated hooks (yamllint, check-jsonschema, check-merge-conflict, end-of-file-fixer) plus 5 defense-in-depth hooks (check-yaml --allow-multiple-documents, check-json, check-added-large-files --maxkb=1024, trailing-whitespace --markdown-linebreak-ext=md, mixed-line-ending --fix=lf).
- yamllint hook intentionally runs without any strict-mode flag — verified by `grep -- "--strict" .pre-commit-config.yaml` exiting 1.
- `pre-commit run --all-files` exits 0 on current repo state (auto-fixed 2 files on first run; clean on second run; verified again post-commit).
- check-jsonschema hook pre-wired against `^ontology/schemas/.*\.json$` with `--check-metaschema` — Phase 1 has no matches so the hook trivially skips; Phase 2 schemas will pick up automatically without config change.

## Task Commits

Each task was committed atomically (with `--no-verify` per parallel-execution guidance):

1. **Task 1: Write .yamllint relaxed config** — `74541a9` (feat)
2. **Task 2: Write .pre-commit-config.yaml + verify pre-commit run --all-files exits 0** — `892429d` (feat, includes auto-fixed `.planning/config.json` and `.planning/REQUIREMENTS.md` trailing-newline fixes)

Plan-metadata commit will be created by the orchestrator (per parallel-execution scope, this executor stops at SUMMARY.md and does not touch STATE.md / ROADMAP.md).

## Files Created/Modified

- `.yamllint` — yamllint rules tuned for bilingual aviation YAML (created)
- `.pre-commit-config.yaml` — orchestrator with 9 hooks across 3 repos, all versions pinned (created)
- `.planning/config.json` — added trailing newline (auto-fixed by end-of-file-fixer)
- `.planning/REQUIREMENTS.md` — added trailing newline (auto-fixed by end-of-file-fixer)

## Decisions Made

- **No strict-mode flag on yamllint hook.** The plan called this out as load-bearing for Phase 2+ bilingual `full_text` fields. Kept the comment block explaining the rationale (worded carefully so the literal substring `--strict` does NOT appear anywhere in the file — the acceptance criterion `grep -- "--strict" .pre-commit-config.yaml` exits 1).
- **Pre-commit installed via `uv tool install pre-commit==3.7.1`** rather than `pip install --user`. Reason: Python on this host is uv-managed (PEP 668 externally-managed-environment error blocks pip --user). Resulting binary at `/Users/Zhuanz/.local/bin/pre-commit` is functionally identical and version-pinned to STACK.md.
- **Auto-fixed `.planning/config.json` + `.planning/REQUIREMENTS.md`** committed alongside the pre-commit config. These are intentional eof-fixer fixes (both files were missing trailing newlines); committing them makes the second `pre-commit run --all-files` pass cleanly without further state churn.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking] Reworded yamllint hook comment block to remove literal `--strict` substring**
- **Found during:** Task 2 acceptance verification
- **Issue:** The plan-supplied comment block on the yamllint hook contained the explanatory phrase `deliberately NO --strict here` and `Under --strict, the warning ...`. Both contain the literal substring `--strict`, which made the acceptance criterion `grep -- "--strict" .pre-commit-config.yaml` exit 0 (FAIL — should exit 1).
- **Fix:** Reworded the comment block to use the phrasing "deliberately NO strict-mode flag here" and "Promoting warnings to failures would block ..." — preserves the rationale (and explicit reminder for future maintainers) without containing the literal substring `--strict`. The hook still has no `--strict` flag in its `args:` list — the behavior is unchanged.
- **Files modified:** `.pre-commit-config.yaml`
- **Verification:** `grep -- "--strict" .pre-commit-config.yaml; echo $?` returns exit 1; `pre-commit run --all-files` still passes; the rationale is still discoverable in the comment block.
- **Committed in:** `892429d` (Task 2 commit)

**2. [Rule 3 — Blocking] Switched pre-commit install path from `pip install --user` to `uv tool install`**
- **Found during:** Task 2 verify step (before running `pre-commit run --all-files`)
- **Issue:** `python3 -m pip install --user pre-commit==3.7.1` failed with PEP 668 `externally-managed-environment` (Python on this host is managed by uv).
- **Fix:** Used `uv tool install pre-commit==3.7.1`, which installed the pinned version cleanly to `~/.local/bin/pre-commit`.
- **Files modified:** none (host tooling only; no repo files affected)
- **Verification:** `pre-commit --version` returns `pre-commit 3.7.1`; the verify command in the plan ran successfully.
- **Committed in:** N/A (host tooling change, not a repo change)

---

**Total deviations:** 2 auto-fixed (both Rule 3 — Blocking)
**Impact on plan:** Zero scope creep. Both fixes were necessary to satisfy the explicit acceptance criteria. Hook behavior, pinned versions, and the strictness model are exactly as the plan specified.

## Issues Encountered

- First `pre-commit run --all-files` modified `.planning/config.json` and `.planning/REQUIREMENTS.md` (end-of-file-fixer added trailing newlines on previously-newline-less files). This is the documented first-run behavior of auto-fix hooks; second run was clean. Both fixes were folded into the Task-2 commit so the repo state is reproducibly clean.

## User Setup Required

None — pre-commit is wired entirely through repo files. Each developer needs to install pre-commit once on their machine (`uv tool install pre-commit==3.7.1` or `pip install pre-commit==3.7.1`) and run `pre-commit install` once in their clone. This is documented as a comment block at the top of `.pre-commit-config.yaml`.

## Next Phase Readiness

- **Plan 04 (CI workflow):** the GitHub Actions / Gitea Actions CI job can now `pip install pre-commit==3.7.1 && pre-commit run --all-files` and rely on this config exiting 0 on a clean checkout. Plan 04 just needs to wire the workflow file.
- **Phase 2 (ontology schemas):** when the first JSON Schema lands at `ontology/schemas/<entity>.json`, the check-jsonschema hook automatically picks it up and metaschema-validates it. The `files:` glob and `--check-metaschema` flag are pre-wired; Phase 2 will only need to add `instances/entities/**/*.yaml`-validating hook entries when instance YAMLs start landing.
- **Open observation for future strictness retro:** Phase 2 should track how often the line-length warning fires on real bilingual `full_text` records. If it never fires, we can tighten back toward the default 80-char limit. If it fires constantly, max=200 was the right call. Empirical data > prediction.

## Self-Check: PASSED

- `.yamllint` exists: `/Users/Zhuanz/aviation-knowledge-base/.claude/worktrees/agent-af8d614234efa1602/.yamllint` — FOUND
- `.pre-commit-config.yaml` exists: `/Users/Zhuanz/aviation-knowledge-base/.claude/worktrees/agent-af8d614234efa1602/.pre-commit-config.yaml` — FOUND
- Task-1 commit `74541a9` — FOUND in git log
- Task-2 commit `892429d` — FOUND in git log
- `grep -- "--strict" .pre-commit-config.yaml` exits 1 — VERIFIED
- `pre-commit run --all-files` exits 0 — VERIFIED (re-run post-commit)
- Pinned versions match STACK.md exactly: yamllint v1.38.0, check-jsonschema 0.37.1, pre-commit-hooks v4.6.0, pre-commit framework 3.7.1 — VERIFIED

---
*Phase: 01-repo-skeleton-git-baseline-prd-v0*
*Plan: 03 — Pre-commit Config and Hooks*
*Completed: 2026-05-03*

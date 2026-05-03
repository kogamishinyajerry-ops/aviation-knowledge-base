---
phase: 01-repo-skeleton-git-baseline-prd-v0
plan: 03
type: execute
wave: 2
depends_on:
  - 01-01
files_modified:
  - .pre-commit-config.yaml
  - .yamllint
autonomous: true
requirements:
  - REPO-05

must_haves:
  truths:
    - "`.pre-commit-config.yaml` exists at repo root with pinned hook versions (yamllint v1.38.0, check-jsonschema 0.37.1, pre-commit-hooks v4.6.0)"
    - "Hooks configured: `yamllint`, `check-jsonschema` (configured but no schema files yet — runs as relaxed/no-op pattern), `check-merge-conflict`, `end-of-file-fixer`, `trailing-whitespace`, `check-yaml` (syntax)"
    - "`.yamllint` config exists with relaxed rules (line-length warning not error, allow document-start `---`, allow multiple top-level keys)"
    - "yamllint hook does NOT use `--strict` — warnings (e.g. line-length on bilingual aviation YAML) stay informational; only true errors (trailing whitespace, missing newline at EOF, duplicate keys) block commits. This is what enables Phase 2+ schema authoring with long bilingual `full_text` fields to pass without yamllint disabling."
    - "`pre-commit run --all-files` exits 0 on the current repo state (the YAML in `.planning/`, the README from Plan 02, the 4 stub Python files from Plan 01 must all pass), AND the verify step propagates pre-commit's exit code (no `; echo END` swallowing it)"
    - "Tool versions pinned to exactly the values in `.planning/research/STACK.md` (yamllint v1.38.0, check-jsonschema 0.37.1, pre-commit 3.7.0+)"
  artifacts:
    - path: ".pre-commit-config.yaml"
      provides: "Pre-commit hook orchestration with pinned versions"
      contains: "rev:"
      min_lines: 35
    - path: ".yamllint"
      provides: "yamllint config — relaxed for human-authored aviation YAML"
      contains: "extends: default"
  key_links:
    - from: ".pre-commit-config.yaml"
      to: "yamllint hook"
      via: "repo: https://github.com/adrienverge/yamllint"
      pattern: "adrienverge/yamllint"
    - from: ".pre-commit-config.yaml"
      to: "check-jsonschema hook"
      via: "repo: https://github.com/python-jsonschema/check-jsonschema"
      pattern: "python-jsonschema/check-jsonschema"
    - from: ".pre-commit-config.yaml"
      to: ".yamllint"
      via: "yamllint hook reads .yamllint config from repo root"
      pattern: "yamllint"
---

<objective>
Install pre-commit configuration so every YAML file authored from Phase 2 onward is syntax-checked and (later) schema-validated before it can be committed. This is REPO-05, and it is a Wave-2 plan because the hook config file lives at repo root — it depends on Plan 01 having materialized the directory layout but does NOT depend on Plan 02 (README) or Plan 04 (CI workflow).

The check-jsonschema hook is configured NOW even though no schemas exist yet, because:
1. Phase 2 will drop schemas into `ontology/schemas/` and the hook is already wired
2. Configuring it later is a breaking change to existing developer workflows
3. We can configure it as relaxed (run-but-find-nothing) until schemas land

Key constraint: `pre-commit run --all-files` MUST exit 0 on the current repo state. Yamllint and end-of-file-fixer applied to the existing `.planning/*.md` and `.planning/*.yaml` files must pass without errors. If yamllint default rules are too strict for human-authored docs, we relax them in `.yamllint`.

Strictness model (important): the yamllint hook does **NOT** use `--strict`. We rely on `level: warning` (line-length etc.) staying informational, and `level: error` (trailing-spaces, new-line-at-end-of-file, document-start, key-duplicates) blocking commits. Using `--strict` together with `level: warning` would defeat the whole point of relaxed rules — `--strict` promotes warnings to failures, which means a long bilingual `full_text` field in a Phase 2+ schema record would fail pre-commit. That's the exact silent-break scenario this plan refuses to create.

Purpose: Make schema/style violations visible at the developer's keyboard, not at PR time. Trade: small first-time-setup cost for the user (`pre-commit install` once) in exchange for catching ~80% of YAML pitfalls before review.

Output: `.pre-commit-config.yaml` + `.yamllint` at repo root, both committed atomically. Tool versions pinned per STACK.md.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/REQUIREMENTS.md
@.planning/research/SUMMARY.md
@.planning/research/PITFALLS.md
@CLAUDE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Write .yamllint relaxed config</name>
  <files>.yamllint</files>
  <read_first>
    - .planning/PROJECT.md (no specific yaml style rules — bilingual ZH/EN content, sometimes long lines for descriptive text)
    - The existing files we will lint: .planning/PROJECT.md, .planning/ROADMAP.md, .planning/REQUIREMENTS.md, .planning/STATE.md, .planning/config.json — yamllint will only act on .yaml/.yml files; we still want to confirm there are no .yaml/.yml files in .planning/ that would fail
  </read_first>
  <action>
First, scan the repo for any existing YAML files that would be subject to lint:

```bash
cd /Users/Zhuanz/aviation-knowledge-base
find . -name "*.yaml" -o -name "*.yml" 2>/dev/null | grep -v node_modules | grep -v ".git/" | head -20
```

Then write `.yamllint` at repo root with EXACTLY this content:

```yaml
--- # YAML document start
# yamllint config for Aviation Knowledge Base MVP
# Goal: catch real YAML errors (duplicate keys, bad indentation, unparseable
# syntax) without blocking on stylistic preferences. Aviation domain content
# routinely has long lines (regulation text, bilingual ZH/EN labels) and
# multi-document files (vocabularies/*.yaml may use ---).
#
# Rule rationales:
# - line-length: warning not error — aviation regulation text and full-text
#   bilingual labels frequently exceed 80 chars; we don't want to fight this.
#   Combined with the hook NOT using --strict (see .pre-commit-config.yaml),
#   this means long lines emit informational warnings but DO NOT fail the hook.
# - document-start: required (level: error) — every YAML file should open with ---
# - truthy: only block 'yes/no/on/off'; allow 'true/false' (the YAML 1.2 forms)
# - comments: allow 1-space-after-hash (more permissive than default 2)
# - indentation: 2 spaces, consistent
# - trailing-spaces: error — these MUST be fixed
# - empty-lines: at most 2 consecutive (ergonomics)
# - new-line-at-end-of-file: error — must be present (matches end-of-file-fixer hook)

extends: default

rules:
  line-length:
    max: 200
    level: warning
  document-start:
    present: true
    level: error
  truthy:
    allowed-values: ["true", "false"]
    check-keys: false
  comments:
    min-spaces-from-content: 1
  indentation:
    spaces: 2
    indent-sequences: true
    check-multi-line-strings: false
  trailing-spaces: enable
  empty-lines:
    max: 2
    max-start: 1
    max-end: 1
  new-line-at-end-of-file: enable
  # Relax some defaults that don't fit aviation YAML
  comments-indentation: disable
  braces:
    forbid: false
    min-spaces-inside: 0
    max-spaces-inside: 1
```

Notes:
- `line-length: 200, level: warning` means a long line emits a warning but does NOT fail the hook (because the yamllint hook in `.pre-commit-config.yaml` does NOT use `--strict` — see Task 2 below).
- `comments-indentation: disable` because aviation YAMLs often have inline comments referencing standards (`# per ATA-25, FAA AC 25.1309-1B`) that may not align with code blocks.
- We do NOT use `key-duplicates` rule explicitly because the default already includes it as an error — duplicate keys are always wrong.
  </action>
  <verify>
    <automated>cd /Users/Zhuanz/aviation-knowledge-base &amp;&amp; test -f .yamllint &amp;&amp; grep -q "^extends: default" .yamllint &amp;&amp; grep -q "line-length:" .yamllint &amp;&amp; grep -q "level: warning" .yamllint &amp;&amp; grep -q "document-start:" .yamllint &amp;&amp; echo OK</automated>
  </verify>
  <acceptance_criteria>
    - `test -f /Users/Zhuanz/aviation-knowledge-base/.yamllint` exit 0
    - `grep -E "^extends: default" /Users/Zhuanz/aviation-knowledge-base/.yamllint` exit 0
    - `grep -E "max: 200" /Users/Zhuanz/aviation-knowledge-base/.yamllint` exit 0 (relaxed line length)
    - `grep -E "level: warning" /Users/Zhuanz/aviation-knowledge-base/.yamllint` exit 0 (line length warns, doesn't fail)
    - `grep -E "trailing-spaces: enable" /Users/Zhuanz/aviation-knowledge-base/.yamllint` exit 0 (these still hard-fail)
  </acceptance_criteria>
  <done>`.yamllint` exists, relaxed for human-authored aviation YAML, but still catches duplicate keys, trailing whitespace, missing trailing newline, missing document-start.</done>
</task>

<task type="auto">
  <name>Task 2: Write .pre-commit-config.yaml with pinned hook versions</name>
  <files>.pre-commit-config.yaml</files>
  <read_first>
    - .planning/research/STACK.md (Tool versions table — must verify yamllint 1.38, check-jsonschema 0.37.1, pre-commit 3.7+ are current pinned versions)
    - .planning/research/SUMMARY.md (Stack Pinned section confirms these versions)
    - The .yamllint file from Task 1 (the yamllint hook will use it; importantly, this hook does NOT use --strict so that line-length stays informational per the .yamllint level: warning setting)
  </read_first>
  <action>
Write `.pre-commit-config.yaml` at repo root with EXACTLY this content. Hook versions ARE PINNED — do not use `latest` or floating tags.

```yaml
--- # YAML document start
# Aviation Knowledge Base MVP — pre-commit configuration
# Per REPO-05: minimum hooks include yamllint, check-jsonschema,
# check-merge-conflict, end-of-file-fixer.
#
# Tool versions pinned per .planning/research/STACK.md:
#   - pre-commit framework: 3.7+
#   - yamllint: 1.38+
#   - check-jsonschema: 0.37.1
#
# Hook revisions below are pinned to specific upstream tags; bump only
# via deliberate PR with CHANGELOG entry.
#
# Initial setup (one-time, on each developer machine):
#   pip install pre-commit==3.7.1
#   pre-commit install
#
# Run on demand:
#   pre-commit run --all-files

minimum_pre_commit_version: "3.7.0"

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-merge-conflict
      - id: check-yaml
        args: ["--allow-multiple-documents"]
      - id: check-json
      - id: check-added-large-files
        args: ["--maxkb=1024"]  # 1 MB; binaries should be in LFS, see .gitattributes
      - id: end-of-file-fixer
      - id: trailing-whitespace
        args: ["--markdown-linebreak-ext=md"]  # respect Markdown 2-space line breaks
      - id: mixed-line-ending
        args: ["--fix=lf"]

  - repo: https://github.com/adrienverge/yamllint
    rev: v1.38.0
    hooks:
      - id: yamllint
        # NOTE: deliberately NO --strict here. We rely on level-based gating
        # in .yamllint:
        #   - level: error   → blocks commit (trailing-spaces, missing-newline-at-EOF,
        #                      document-start, key-duplicates default, indentation)
        #   - level: warning → informational only (line-length up to 200 chars)
        # Why this matters: Phase 2+ entity records will have long bilingual
        # `full_text` / regulation-quote fields. Under --strict, the warning
        # for line-length would promote to failure and block legitimate
        # aviation content. The relaxed-but-meaningful gate is exactly what
        # makes pre-commit usable on this corpus.
        # Re-evaluate strictness in Phase 2 once the first schemas land and
        # we have empirical data on how often warnings fire.
        args: ["-c", ".yamllint"]

  - repo: https://github.com/python-jsonschema/check-jsonschema
    rev: 0.37.1
    hooks:
      # Phase 1 stub: no schemas exist yet under ontology/schemas/.
      # We pre-wire the hook so that when Phase 2 adds schemas, this is
      # already configured. Until then, the hook runs against the (empty)
      # `files: ` pattern and trivially passes.
      #
      # Phase 2 will replace `files:` with patterns matching:
      #   - ontology/schemas/**/*.json   (validate against JSON Schema metaschema)
      #   - instances/entities/**/*.yaml (validate against per-type schema)
      #   - instances/relations/**/*.yaml
      #
      # For Phase 1, we configure metaschema validation only — it self-validates
      # any future JSON Schema file we drop into ontology/schemas/.
      - id: check-jsonschema
        name: "check-jsonschema (metaschema, Phase 1 stub)"
        files: '^ontology/schemas/.*\.json$'
        args: ["--check-metaschema"]
        # If no files match, the hook is skipped (pre-commit default).
        # This is intentional for Phase 1 — Phase 2 lands the first schemas.

# CI integration note (.github/workflows/ci.yml — Plan 04 owns):
# The CI workflow runs `pre-commit run --all-files` against every PR.
# Local developer machines run only the hooks for staged files via the
# pre-commit Git hook (`pre-commit install`).
```

After writing, run pre-commit against the current repo state to verify it passes:

```bash
cd /Users/Zhuanz/aviation-knowledge-base

# Install pre-commit if not present (the user's global env may already have it)
python3 -m pip install --user pre-commit==3.7.1 2>&1 | tail -5

# Run all hooks against all files. This MUST exit 0 (or 1 then 0 after
# auto-fix re-run for end-of-file-fixer / trailing-whitespace on existing
# planning docs). Capture log for the SUMMARY but propagate the exit code.
PRECOMMIT_BIN="$(command -v pre-commit || echo ~/.local/bin/pre-commit)"
"$PRECOMMIT_BIN" run --all-files 2>&1 | tee /tmp/precommit_phase1.log
PRECOMMIT_EXIT=${PIPESTATUS[0]}
echo "EXIT_CODE=$PRECOMMIT_EXIT"

# If non-zero on first run because of auto-fix hooks, re-run once.
if [ "$PRECOMMIT_EXIT" != "0" ]; then
  echo "First run modified files (auto-fixers). Re-running once..."
  "$PRECOMMIT_BIN" run --all-files 2>&1 | tee -a /tmp/precommit_phase1.log
  PRECOMMIT_EXIT=${PIPESTATUS[0]}
  echo "SECOND_EXIT_CODE=$PRECOMMIT_EXIT"
fi

# Final exit must be 0 for this task to count as done.
exit $PRECOMMIT_EXIT
```

If `pre-commit run --all-files` returns a non-zero exit code on the second run:
- Read the offending file's error message.
- If it's `end-of-file-fixer` or `trailing-whitespace` on a `.planning/*.md` or other existing file, the hook will auto-fix and stage the changes — that's normal first-run behavior; second run should be clean.
- If it's `yamllint` complaining about a real issue (e.g., a `.planning/*.yaml` that has duplicate keys), STOP and report — do not patch the existing planning files without an ADR; the issue may indicate a real upstream bug.
- If it's `check-jsonschema` failing, that means `ontology/schemas/` has files but they're broken — should be impossible in Phase 1.
- If `pre-commit` is not installed at all (`pip install` failed), report it as a blocker; the hook config is still valuable to commit even if the tool can't run on the executor's machine, but the verification step requires it.
  </action>
  <verify>
    <automated>cd /Users/Zhuanz/aviation-knowledge-base &amp;&amp; test -f .pre-commit-config.yaml &amp;&amp; grep -q "rev: v1.38.0" .pre-commit-config.yaml &amp;&amp; grep -q "rev: 0.37.1" .pre-commit-config.yaml &amp;&amp; grep -q "rev: v4.6.0" .pre-commit-config.yaml &amp;&amp; grep -q "id: check-merge-conflict" .pre-commit-config.yaml &amp;&amp; grep -q "id: end-of-file-fixer" .pre-commit-config.yaml &amp;&amp; grep -q "id: yamllint" .pre-commit-config.yaml &amp;&amp; grep -q "id: check-jsonschema" .pre-commit-config.yaml &amp;&amp; ! grep -q -- "--strict" .pre-commit-config.yaml &amp;&amp; { PRECOMMIT_BIN="$(command -v pre-commit || echo ~/.local/bin/pre-commit)"; "$PRECOMMIT_BIN" run --all-files &gt;/dev/null 2&gt;&amp;1 || "$PRECOMMIT_BIN" run --all-files; } &amp;&amp; echo OK</automated>
  </verify>
  <acceptance_criteria>
    - `test -f /Users/Zhuanz/aviation-knowledge-base/.pre-commit-config.yaml` exit 0
    - `wc -l /Users/Zhuanz/aviation-knowledge-base/.pre-commit-config.yaml` returns at least `35`
    - `grep -E "rev: v1\.38\.0" /Users/Zhuanz/aviation-knowledge-base/.pre-commit-config.yaml` exit 0 (yamllint pinned)
    - `grep -E "rev: 0\.37\.1" /Users/Zhuanz/aviation-knowledge-base/.pre-commit-config.yaml` exit 0 (check-jsonschema pinned)
    - `grep -E "rev: v4\.6\.0" /Users/Zhuanz/aviation-knowledge-base/.pre-commit-config.yaml` exit 0 (pre-commit-hooks pinned)
    - All four required hooks present: `grep -cE "id: (check-merge-conflict|end-of-file-fixer|yamllint|check-jsonschema)" /Users/Zhuanz/aviation-knowledge-base/.pre-commit-config.yaml` returns at least `4`
    - Bonus hooks present (defense-in-depth): `check-yaml`, `check-json`, `check-added-large-files`, `trailing-whitespace`, `mixed-line-ending`
    - **No `--strict` flag in the yamllint hook args**: `grep -- "--strict" /Users/Zhuanz/aviation-knowledge-base/.pre-commit-config.yaml` exit 1 (i.e., NOT FOUND). This is critical: --strict would promote line-length warnings to errors and break Phase 2+ schema authoring.
    - Running `pre-commit run --all-files` from repo root exits 0 (after up to 1 auto-fix re-run for end-of-file-fixer / trailing-whitespace on existing planning docs). The verify step propagates the exit code — no `; echo END` swallowing failures.
    - The `check-jsonschema` hook is configured with `files: '^ontology/schemas/.*\.json$'` pattern (pre-wired for Phase 2)
  </acceptance_criteria>
  <done>`.pre-commit-config.yaml` committed with pinned versions; yamllint hook does NOT use `--strict` so warnings stay informational; `pre-commit run --all-files` exits 0; the hook setup is ready for Phase 2 schemas to land into `ontology/schemas/` without further config changes.</done>
</task>

</tasks>

<verification>
Phase-1 Plan-03 is complete when:
- [ ] `.yamllint` exists at repo root with relaxed-but-meaningful rules
- [ ] `.pre-commit-config.yaml` exists at repo root with all 4 mandated hooks plus defense-in-depth additions
- [ ] All hook versions are pinned to specific tags (no `latest`, no floating refs)
- [ ] yamllint hook does NOT carry `--strict` (would defeat `level: warning` for line-length and break Phase 2+ schema authoring)
- [ ] `pre-commit run --all-files` exits 0 on current repo state, AND the verify step propagates that exit code (no shell trickery that swallows failures)
- [ ] check-jsonschema hook is pre-wired to `ontology/schemas/**/*.json` even though that dir is empty (Phase 2 will populate; no config change needed at that point)
</verification>

<success_criteria>
- pre-commit framework wired for the entire project lifecycle (REPO-05)
- Tool versions match STACK.md exactly (yamllint v1.38.0, check-jsonschema 0.37.1, pre-commit-hooks v4.6.0)
- Real YAML issues (trailing whitespace, missing newline, duplicate keys) caught at commit time
- Stylistic noise (line length on long bilingual labels) does NOT block commits — verified by absence of `--strict` on the yamllint hook
- Phase 2 schemas can land without any pre-commit config change
- ROADMAP SC5 (`pre-commit run --all-files` exits 0) is enforceable because the verify step actually propagates the exit code
</success_criteria>

<output>
After completion, create `.planning/phases/01-repo-skeleton-git-baseline-prd-v0/01-03-SUMMARY.md` documenting:
- Files created (`.pre-commit-config.yaml`, `.yamllint`)
- Pinned hook versions
- `pre-commit run --all-files` exit code on first and (if applicable) second run
- Any auto-fixes applied to existing planning docs (end-of-file-fixer / trailing-whitespace)
- Notes on Phase 2 follow-on (where `check-jsonschema` will start finding files)
- Confirmation that yamllint hook does NOT use --strict
</output>

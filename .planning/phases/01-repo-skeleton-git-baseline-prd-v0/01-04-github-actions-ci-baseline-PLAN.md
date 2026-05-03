---
phase: 01-repo-skeleton-git-baseline-prd-v0
plan: 04
type: execute
wave: 2
depends_on:
  - 01-01
files_modified:
  - .github/workflows/ci.yml
autonomous: true
requirements:
  - REPO-04

must_haves:
  truths:
    - "`.github/workflows/ci.yml` exists and parses as valid YAML"
    - "Workflow triggers on push to main and on pull_request to main"
    - "Workflow has 3 jobs: `lint` (runs pre-commit), `schema-validation-stub` (no-op echo for Phase 1, becomes real in Phase 3), `link-check-stub` (no-op echo for Phase 1, real validator added in later phase)"
    - "All actions reference pinned versions: `actions/checkout@v4`, `actions/setup-python@v5`"
    - "All 3 jobs return green on a no-op PR — verified by ensuring each job's last step exits 0"
    - "Workflow does NOT install or attempt to run Wiki.js / RAGFlow / Postgres — v1 ships scaffolding only"
  artifacts:
    - path: ".github/workflows/ci.yml"
      provides: "GitHub Actions baseline CI workflow"
      min_lines: 50
      contains: "actions/checkout@v4"
  key_links:
    - from: ".github/workflows/ci.yml"
      to: ".pre-commit-config.yaml"
      via: "lint job runs `pre-commit run --all-files`"
      pattern: "pre-commit run"
    - from: ".github/workflows/ci.yml"
      to: "actions/checkout"
      via: "uses: actions/checkout@v4"
      pattern: "actions/checkout@v4"
    - from: ".github/workflows/ci.yml"
      to: "actions/setup-python"
      via: "uses: actions/setup-python@v5"
      pattern: "actions/setup-python@v5"
---

<objective>
Install the GitHub Actions CI baseline so every PR (and push to main) automatically runs the lint pipeline and the schema/link-check stubs that later phases will replace with real validators.

Phase 1 deliberately ships **stubs** for schema-validation and link-check because:
1. Phase 2 will create the schemas; until then there is nothing to validate.
2. Phase 4 will create the documents; until then there are no links to check.
3. We want the workflow file present and green from day 1 so the CI badge is real, not aspirational.

The lint job is NOT a stub — it runs `pre-commit run --all-files` against the actual config from Plan 03, providing real value immediately (catches yamllint violations, missing trailing newlines, large files, merge conflict markers).

Per ARCHITECTURE.md "scripts/exporters/" guardrail and the "Git is SSOT" principle, CI is the gate that enforces "nothing reaches main without passing the contract." Phase 1 lays the wiring; Phases 3 / 4 / 5 fill in the contract.

Output: `.github/workflows/ci.yml` committed atomically; workflow file is syntactically valid; all jobs return green when run against this repo.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/REQUIREMENTS.md
@.planning/ROADMAP.md
@.planning/research/SUMMARY.md
@.planning/research/PITFALLS.md
@CLAUDE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create .github/workflows/ci.yml with lint + 2 stub jobs</name>
  <files>.github/workflows/ci.yml</files>
  <read_first>
    - .planning/REQUIREMENTS.md (REPO-04 specifically — "no-op stubs for schema-validation / link-check / yamllint jobs (filled in at validator phase)")
    - .planning/ROADMAP.md (Phase 3 success criterion #5 — "GitHub Actions CI runs `validate.py` + `pytest` on every push and PR" — this is the upgrade target for the schema-validation-stub job)
    - .planning/research/PITFALLS.md ("Looks Done But Isn't" row "CI 占位 (R1)：常只有 lint 没有 schema validation" — directly informs why we keep schema-validation as a clearly-labeled STUB rather than dropping it)
  </read_first>
  <action>
First, ensure the parent directory exists (it should not yet — Plan 01 deliberately did not create `.github/`):

```bash
mkdir -p /Users/Zhuanz/aviation-knowledge-base/.github/workflows
```

Then write `/Users/Zhuanz/aviation-knowledge-base/.github/workflows/ci.yml` with EXACTLY this content:

```yaml
---
# Aviation Knowledge Base MVP — CI baseline (Phase 1)
#
# Per REPO-04: this workflow ships in Phase 1 with `lint` running for real
# (against .pre-commit-config.yaml) and `schema-validation-stub` /
# `link-check-stub` as labeled stubs. Phase 3 replaces the schema stub with
# `python scripts/validate.py + pytest`. A later phase replaces the link
# stub with a real link/cross-ref checker.
#
# Action versions pinned per .planning/research/STACK.md and .planning/research/PITFALLS.md
# guidance. NEVER use `@latest` or `@main` — supply chain risk + reproducibility.
#
# This workflow is the gate referenced in .planning/research/ARCHITECTURE.md
# "Validation & CI Layer". Phase 3 makes it actually validate; Phase 1 wires it.

name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Cancel duplicate in-flight runs on the same ref (saves CI budget).
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  lint:
    name: Lint (pre-commit)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 1
          # Note: lfs: false intentionally — Phase 1 has no LFS objects yet.
          # Switch to lfs: true once the first PDF lands in docs/ (Phase 4).

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: Install pre-commit
        run: |
          python -m pip install --upgrade pip
          pip install pre-commit==3.7.1

      - name: Cache pre-commit hook environments
        uses: actions/cache@v4
        with:
          path: ~/.cache/pre-commit
          key: pre-commit-${{ runner.os }}-${{ hashFiles('.pre-commit-config.yaml') }}
          restore-keys: |
            pre-commit-${{ runner.os }}-

      - name: Run pre-commit on all files
        run: pre-commit run --all-files --show-diff-on-failure

  schema-validation-stub:
    name: Schema validation (Phase 1 STUB — real in Phase 3)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Stub notice
        run: |
          echo "::notice title=Phase 1 stub::This job is a no-op."
          echo "Phase 3 will replace it with: python scripts/validate.py && pytest tests/"
          echo "Tracking: REPO-04 (Phase 1) -> VAL-01..VAL-05 (Phase 3)."
          echo "Stub passing intentionally."

      - name: Pass
        run: exit 0

  link-check-stub:
    name: Link check (Phase 1 STUB — real in later phase)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Stub notice
        run: |
          echo "::notice title=Phase 1 stub::This job is a no-op."
          echo "Future implementation: cross-ref check across instances/, docs/, wiki/, planning/."
          echo "Trigger: when first inter-document references appear (Phase 4)."
          echo "Stub passing intentionally."

      - name: Pass
        run: exit 0
```

Then verify the YAML parses correctly:

```bash
cd /Users/Zhuanz/aviation-knowledge-base
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml').read()); print('OK YAML parse')"
```

If pre-commit was installed in Plan 03's verification, also test that the new file passes pre-commit:

```bash
~/.local/bin/pre-commit run --files .github/workflows/ci.yml 2>&1 | tail -10 || pre-commit run --files .github/workflows/ci.yml 2>&1 | tail -10
```

Locally simulating GitHub Actions is out of scope (would require `act` or similar). The CI run itself is verified when the workflow runs against the next PR — for Phase 1, structural validity (YAML parses, required fields present, action versions pinned) is sufficient.

Notes for the executor:
- Do NOT add `actions/upload-artifact@v4` or any artifact-uploading steps — Phase 1 produces no artifacts that need preservation.
- Do NOT add `if: github.event_name == 'pull_request'` filters — every job should run on both `push` and `pull_request`.
- Do NOT add a `release` or `deploy` job — v1 does not deploy.
- Do NOT add a matrix strategy for multiple Python versions — pin to 3.11 for now (Phase 3 will re-evaluate when validators are written).
- The `permissions: contents: read` block is intentional — minimal required scope (per least-privilege).
- The `concurrency` block prevents wasted CI minutes on rapid pushes.
  </action>
  <verify>
    <automated>cd /Users/Zhuanz/aviation-knowledge-base &amp;&amp; test -f .github/workflows/ci.yml &amp;&amp; python3 -c "import yaml; d = yaml.safe_load(open('.github/workflows/ci.yml').read()); assert 'jobs' in d, 'missing jobs'; assert set(d['jobs'].keys()) &gt;= {'lint', 'schema-validation-stub', 'link-check-stub'}, 'missing required jobs'; print('OK jobs:', list(d['jobs'].keys()))" &amp;&amp; grep -q "actions/checkout@v4" .github/workflows/ci.yml &amp;&amp; grep -q "actions/setup-python@v5" .github/workflows/ci.yml &amp;&amp; grep -q "pre-commit run --all-files" .github/workflows/ci.yml &amp;&amp; grep -q "Phase 1 STUB" .github/workflows/ci.yml &amp;&amp; echo OK</automated>
  </verify>
  <acceptance_criteria>
    - `test -f /Users/Zhuanz/aviation-knowledge-base/.github/workflows/ci.yml` exit 0
    - `python3 -c "import yaml; yaml.safe_load(open('/Users/Zhuanz/aviation-knowledge-base/.github/workflows/ci.yml').read())"` exit 0 (parses)
    - YAML contains all 3 jobs: `grep -cE "^  (lint|schema-validation-stub|link-check-stub):" /Users/Zhuanz/aviation-knowledge-base/.github/workflows/ci.yml` returns `3`
    - All actions pinned to specific versions: `grep -cE "uses: actions/(checkout@v4|setup-python@v5|cache@v4)" /Users/Zhuanz/aviation-knowledge-base/.github/workflows/ci.yml` returns at least `4` (4 checkouts across 3 jobs + 1 setup-python + 1 cache, depending on how the executor wrote it; minimum 4 distinct uses-pinned-version lines)
    - No floating refs: `grep -E "@(latest|main|master)" /Users/Zhuanz/aviation-knowledge-base/.github/workflows/ci.yml` returns no matches
    - Lint job actually runs pre-commit: `grep -q "pre-commit run --all-files" /Users/Zhuanz/aviation-knowledge-base/.github/workflows/ci.yml` exit 0
    - Triggers on both push and pull_request: `grep -A2 "^on:" /Users/Zhuanz/aviation-knowledge-base/.github/workflows/ci.yml | grep -E "(push|pull_request)" | wc -l` returns at least `2`
    - Stub jobs are clearly labeled "STUB" (so they're not mistaken for real validators): `grep -cE "Phase 1 STUB|Phase 1 stub" /Users/Zhuanz/aviation-knowledge-base/.github/workflows/ci.yml` returns at least `2`
    - No reference to docker-compose / wiki-js / ragflow / postgres in the CI file (v1 does not deploy or run those services in CI): `grep -iE "docker-compose|wiki.?js|ragflow|postgres" /Users/Zhuanz/aviation-knowledge-base/.github/workflows/ci.yml` returns no matches
    - `permissions: contents: read` is set (least-privilege): `grep -q "contents: read" /Users/Zhuanz/aviation-knowledge-base/.github/workflows/ci.yml` exit 0
  </acceptance_criteria>
  <done>`.github/workflows/ci.yml` exists with 3 jobs (1 real lint + 2 clearly-labeled stubs); all action versions pinned; YAML parses; ready to run green on the next PR.</done>
</task>

</tasks>

<verification>
Phase-1 Plan-04 is complete when:
- [ ] `.github/workflows/ci.yml` exists and parses as valid YAML
- [ ] All 3 required jobs (lint, schema-validation-stub, link-check-stub) are present and structured correctly
- [ ] No floating action versions (no `@latest`, `@main`, `@master`)
- [ ] Lint job runs `pre-commit run --all-files` against the config from Plan 03
- [ ] Stub jobs visibly emit "Phase 1 STUB" / "Phase 1 stub" notices and pass with `exit 0`
- [ ] Workflow file passes pre-commit (yamllint, end-of-file-fixer, etc.)
</verification>

<success_criteria>
- CI baseline installed (REPO-04)
- Real value from day 1: lint job catches violations on every PR
- Phase 3 has a clear upgrade path: replace `schema-validation-stub` body with `python scripts/validate.py && pytest`
- No supply-chain surprises: every action pinned to a specific tag
- Workflow runs green on the no-op PR that introduces it (because lint passes against a clean repo, and stubs trivially `exit 0`)
</success_criteria>

<output>
After completion, create `.planning/phases/01-repo-skeleton-git-baseline-prd-v0/01-04-SUMMARY.md` documenting:
- Workflow file created
- Jobs defined and what each does (real vs stub)
- Action versions pinned (cite each one)
- YAML parse verification result
- Pre-commit verification result on the new workflow file
- Notes on Phase 3 upgrade path (which step to replace, what command will go there)
</output>

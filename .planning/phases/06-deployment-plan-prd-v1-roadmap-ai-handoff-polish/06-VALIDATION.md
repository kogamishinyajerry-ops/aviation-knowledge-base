---
phase: 06-deployment-plan-prd-v1-roadmap-ai-handoff-polish
plan: VALIDATION
type: validation-gate
wave: 0
purpose: "Nyquist gate — every <verify><automated> command in 06-NN-PLAN.md must be runnable. Phase 6 is doc-only, so all checks are grep/find/yamllint/json-schema, no service starts."
---

# Phase 6 Validation Gate (Nyquist)

> Phase 6 ships ONLY documentation, draft compose YAML, ROADMAP, glossary,
> process-log entries, and a synthesized PRD. **No services are run.**
> Therefore every `<verify>` is a static check — grep-able section header,
> file existence, yamllint pass, JSON-Schema metaschema pass, line-count
> floor, or exact-phrase match.

## Verification Toolbelt

| Tool | Already in repo? | Used for |
|------|------------------|----------|
| `grep` / `rg` (POSIX) | Yes (system) | Section-header presence, exact-phrase matches, "DRAFT — NOT FOR PRODUCTION" sentinel, AI 接力 header presence, REQ-ID coverage |
| `find` | Yes (system) | File existence, directory shape (process-log/phase-N-completion.md) |
| `wc -l` | Yes (system) | Glossary entry-count floor (≥50), ROADMAP_FUTURE feature-count floor (≥7) |
| `yamllint` | Yes (Phase 1 pinned 1.38) | `deploy/docker-compose.yml.draft` style/syntax |
| `python -c "import yaml; yaml.safe_load(open('...'))"` | Yes (Phase 3 pyproject env) | Compose YAML parses |
| `check-jsonschema` | Yes (Phase 1, 0.37.1) | NOT used in Phase 6 (no schema changes) |
| `python scripts/validate.py` | Yes (Phase 3) | NOT used in Phase 6 (no instances change) |

## Per-Plan Verification Sketch

### 06-01 deploy artifacts
- `find deploy/docker-compose.yml.draft -type f` exits 0
- `grep -q "DRAFT — NOT FOR PRODUCTION" deploy/docker-compose.yml.draft`
- `python -c "import yaml; yaml.safe_load(open('deploy/docker-compose.yml.draft'))"` exits 0
- `yamllint -d "{rules: {document-start: disable}}" deploy/docker-compose.yml.draft` exits 0 (or non-zero only on style warnings)
- `grep -E "^\s*#?\s*authentik" deploy/docker-compose.yml.draft` shows `authentik` block present and **commented out** (every line in the block prefixed with `#`)
- `grep -q "wiki:" deploy/docker-compose.yml.draft && grep -q "postgres:" deploy/docker-compose.yml.draft && grep -q "ragflow:" deploy/docker-compose.yml.draft && grep -q "caddy:" deploy/docker-compose.yml.draft`
- `find deploy/.env.example -type f` exits 0; `grep -vE "^(#|$)" deploy/.env.example | grep -E "=(<.*>|CHANGE_ME|<placeholder>)"` shows every var has placeholder, NO real secrets
- `grep -q "^# topology:" deploy/.env.example || grep -q "^## Topology" deploy/wiki-git-storage.md` (diagram exists somewhere referenced by compose)
- `grep -q "wiki/ ONLY" deploy/wiki-git-storage.md` (DEP-04 hard rule)
- `grep -q "12568" deploy/authentik-phase2.md` (RAGFlow OIDC bug referenced)
- `grep -q "rebuildable" deploy/backup-restore.md` (DEP-06 vector-store-as-derivative line)

### 06-02 glossary + process-log
- `find docs/GLOSSARY.md -type f` exits 0
- `grep -cE "^\| (机|涡|适|材|发|结|起|液|燃|电|航|气|空|飞|.*\| (wing|turbine|airworthiness|engine|component|system|fuselage))" docs/GLOSSARY.md` ≥ 50 (one row per bilingual entry)
- Equivalent simpler check: `awk -F"|" '/^\| [^-]/ && NF>=4' docs/GLOSSARY.md | wc -l` ≥ 50
- `find process-log/phase-1-completion.md process-log/phase-2-completion.md process-log/phase-3-completion.md process-log/phase-4-completion.md process-log/phase-5-completion.md` lists 5 files
- Each phase-N-completion.md contains: `grep -q "AI session:"`, `grep -q "Decisions:"`, `grep -q "Deviations:"`, `grep -q "Verification:"`

### 06-03 ROADMAP_FUTURE
- `find .planning/ROADMAP_FUTURE.md -type f` exits 0
- `grep -cE "^### " .planning/ROADMAP_FUTURE.md` ≥ 7 (GraphRAG, Agent layer, Graph DB backend, OCR pipeline, multi-tenant RBAC, SSO, decision agent)
- `grep -c "Promote when" .planning/ROADMAP_FUTURE.md` ≥ 7 (every feature has its trigger)

### 06-04 PRD_v1 + sign-off
- `find .planning/design/PRD_v1.md -type f` exits 0
- `grep -cE "^## " .planning/design/PRD_v1.md` ≥ 10 (Vision, Stack, Schema, Validators, RAG, Deployment, Roadmap, Risks, Acceptance, Sign-off)
- `grep -q "AI 接力开发指南" .planning/design/PRD_v1.md`
- For every Phase 6 REQ-ID: `grep -q "DEP-01" .planning/design/PRD_v1.md` … `grep -q "ROAD-02" .planning/design/PRD_v1.md`
- `grep -q "PRD_v1" ontology/CHANGELOG.md` (sign-off entry landed in canonical sign-off ledger)

### 06-05 AI 接力 polish + COVERAGE
- For every doc in `.planning/design/`: `grep -q "AI 接力开发指南" .planning/design/<doc>.md` exits 0
- 5-min stranger test result file exists: `find .planning/phases/06-*/06-STRANGER-TEST.md -type f` exits 0; ≥3 docs sampled (PRD_v1, RAG_PIPELINE, one other) with PASS verdict
- 06-COVERAGE.md exists with all 13 REQ-IDs marked covered + plan/task pointer

## Wave-0 Verification Bootstrap

This phase introduces NO new test infrastructure. The single
Wave-0 deliverable is this VALIDATION.md itself, which acts as the
acceptance contract for downstream plans. Plans 06-01 through 06-05
must satisfy these checks; CI's existing yamllint + check-jsonschema
+ pytest pipeline is unchanged.

## Out-of-Phase Concerns

- **No service starts.** If a plan's `<action>` ever calls `docker compose up`, `wiki-js`, `ragflow`, etc. — STOP and revise. Phase 6 is design + draft only.
- **No schema changes.** Phase 2/3 schemas + validators are FROZEN.
- **No new dependencies.** Tools listed above must already be in the repo.

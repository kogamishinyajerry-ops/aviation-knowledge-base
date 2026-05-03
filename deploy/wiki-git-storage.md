# Wiki.js Git Storage Scope Rule (DEP-04)

> **AI 接力开发指南** — 本文是 Wiki.js Git 同步范围的**唯一权威定义**。任何接手部署或评审 PR 的工程师/AI，应先读本文再决定是否放行任何动到 `WIKI_GIT_SUBPATH` 的改动。本文定义的范围**锁定**（`wiki/` ONLY），更改需走 ADR + Phase planning。

## What this doc is / is not

- **IS**: A hard rule defining what Wiki.js Git Storage module is allowed to read/write inside this repo.
- **IS NOT**: A general Wiki.js admin guide (see Wiki.js official docs for that).
- **IS NOT**: A list of pages — pages live under `wiki/` and are managed by editors.

## 5-min stranger test (the AI-handoff bar)

A stranger should be able to:
1. Read this file once.
2. State the rule in one sentence ("Wiki.js Git scope = `wiki/` ONLY, never the full repo").
3. Identify the three enforcement layers (compose env / CI guard / Wiki.js admin UI).
4. Identify what lives in `wiki/` vs what does NOT.
5. Find the next document to read (`deploy/topology.md`, `.planning/research/ARCHITECTURE.md`).

If a reader cannot do that in 5 minutes, this doc has failed.

---

## The hard rule (TL;DR)

---

**Wiki.js Git Storage module scope = `wiki/` subdirectory ONLY. NEVER the full repo.**

(Verifier sentinel — do not delete: scope = wiki/ ONLY)

---

This is **non-negotiable in v1**. Promotion of `docker-compose.yml.draft` to a runnable compose file MUST preserve `WIKI_GIT_SUBPATH: wiki` exactly as written. Reviewers MUST reject any PR that:
- Moves `WIKI_GIT_SUBPATH` from `docker-compose.yml.draft` (where it is hard-coded) to `.env.example` (where it would be overridable).
- Sets `WIKI_GIT_SUBPATH` to anything other than `wiki`.
- Removes the `WIKI_GIT_SUBPATH` line entirely.

---

## Why this rule exists

Three independent reasons. Any one is sufficient; all three apply.

### 1. Editor blast-radius containment

Wiki.js editors are **humans authoring Markdown**. They are not expected to have schema-validation discipline, JSON Schema knowledge, or familiarity with the validator pipeline. If they had write access via Wiki.js to:
- `ontology/` — a single fat-finger could break a JSON Schema and silently invalidate hundreds of instance YAMLs.
- `instances/` — direct edits to canonical entity YAML would bypass `provenance.method` discipline (Pitfall 2).
- `scripts/` — any change to validators, exporters, or `to_ragflow.py` would propagate without code review.

By restricting Wiki.js to `wiki/`, those directories are physically out of editorial reach.

### 2. Audit-trail integrity

The validator pipeline (Phase 3) and the `_pending/` quarantine pattern (PROV-05, Phase 4) both **assume** `instances/` and `ontology/` are modified ONLY via PR with green CI. Wiki.js Git push happens **out-of-band** (no PR, no CI gate) — it commits directly. Mixing Wiki.js writes with canonical writes would produce commits that:
- Have no PR review trail.
- Were never validated by `check-jsonschema` / yamllint.
- Cannot be attributed to a reviewer.

This breaks Core Value ("每一条知识可追溯" / every knowledge item traceable).

### 3. Promotion-gate integrity

Phase 4's `_pending/` quarantine pattern depends on canonical promotion happening **only via reviewed PR**. If Wiki.js could write outside `wiki/`, an editor could effectively "promote" content into canonical without any reviewer ever seeing it. The whole point of staging is undermined.

---

## How to enforce — three layers

### Layer 1: Compose env (the binding rule)

In `deploy/docker-compose.yml.draft`, the wiki service has:

```yaml
WIKI_GIT_SUBPATH: wiki    # hard-coded — see deploy/wiki-git-storage.md
```

This is **NOT** in `.env.example`. It is hard-coded in compose so a deployer cannot override it with an env file. Reviewers MUST reject any PR that moves it out.

### Layer 2: CI guard (future phase)

A future CI job MAY add a check that detects Wiki.js bot commits outside `wiki/`. Sketch (do not implement in Phase 6, document for the promotion phase):

```bash
# Detect Wiki.js bot commits writing outside wiki/
git log --since=1d --name-only --author="wiki-js-bot" -- 'ontology/*' 'instances/*' 'scripts/*' '.planning/*'
# Any output = violation. Page on-call.
```

### Layer 3: Wiki.js admin UI sanity check

In Wiki.js admin panel → Storage → Git module, the "Local repo path" field MUST display `/repo/wiki` (not `/repo`). If an admin sees `/repo` displayed, the env var was not honored — STOP, do not push, escalate.

---

## What lives in `wiki/`

✅ **In scope** (allowed under `wiki/`):
- Human-authored narrative pages summarizing entities (e.g., a page about ATA-71 Powerplant linking to ontology entities)
- Indexed lookups / glossary mirrors / project notes
- ATA chapter overviews
- ZH/EN parallel narrative content
- Generated Markdown summaries linking back to source YAML files in `ontology/` or `instances/`

❌ **Out of scope** (must NEVER be in `wiki/`):
- Source PDFs / DOCX / source documents (those go in `docs/` with Git LFS)
- Canonical YAML instances (those go in `instances/`)
- JSON Schemas (those go in `ontology/`)
- Validator scripts, exporters, glue code (those go in `scripts/`)
- Phase planning, design docs, research (those go in `.planning/`)

If an editor wants to publish a summary page about a regulation, the workflow is:
1. Author the narrative under `wiki/regulations/far-25-1309.md` via Wiki.js.
2. Link in the page body to the canonical entity in `instances/` (e.g., a relative URL or document ID reference).
3. The canonical YAML stays in `instances/`, edited only via PR with CI.

---

## Cross-references

| File | Where | What it shows |
| --- | --- | --- |
| `deploy/docker-compose.yml.draft` | wiki service env block | Hard-coded `WIKI_GIT_SUBPATH: wiki` line |
| `deploy/.env.example` | Wiki.js section | `WIKI_GIT_REMOTE_URL` + `WIKI_GIT_BRANCH` placeholders, with this doc cited |
| `deploy/topology.md` | data-flow diagram | Shows `wiki/` arrow scope vs RAGFlow's full-corpus arrow |
| `.planning/research/ARCHITECTURE.md` | §"Knowledge Layer" / §"Storage Layer" | The architecture-level reasoning behind this rule |
| `.planning/research/PITFALLS.md` | Pitfall 11 (Wiki/RAGFlow desync) | Related discipline: truth + cache discipline |

---

## Open questions (deferred)

- **Bidirectional sync conflict resolution**: if an editor updates a `wiki/` page in the Wiki.js UI at the same time a developer commits a Markdown change in `wiki/` via Git, who wins? Phase 4 design assumes "last write wins with audit log". Promotion phase MUST verify Wiki.js' actual conflict behavior before going live.
- **Pre-receive hook**: a server-side Git hook rejecting any Wiki.js bot commit that touches paths outside `wiki/` would be a 4th enforcement layer. Sketch only — defer to a Git hosting hardening phase.

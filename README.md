# Aviation Knowledge Base MVP

> 工程级航空知识库底座 · Schema-first · 每条知识可追溯来源 · 每个 AI 回答必带 citation
>
> Engineering-grade aviation knowledge base · Schema-first · Source-traceable · Citation-mandatory

**Status:** Phase 1 of 6 — Repo Skeleton + Git Baseline + PRD v0
**Stack (locked):** Wiki.js 2.5.314 · Postgres 16 · RAGFlow 0.25.1 · YAML/JSON Schema · Git
**v1 mode:** scaffolding + schemas + docs + minimum demo. **No real services started in v1.**

***

## AI 接力开发指南 (READ THIS FIRST)

> 如果你是一个 AI 接力来的（Claude / Codex / DeepSeek / Gemini），先读这一节。5 分钟内你应该能回答：项目是什么、当前在哪个阶段、下一步做什么、不要碰什么。
>
> If you are an AI session picking this project up, read this section FIRST. After 5 minutes you should be able to answer: what is this project, what phase are we in, what is the next action, what NOT to touch.

### 1. What this project is (one paragraph)

A schema-first, audit-friendly aviation knowledge base targeting airworthiness, CFD, aircraft systems, components, regulations, accident cases, and expert notes. The differentiating moat is **provenance + citation**, not features. Confluence and Notion already own pretty editing. This project wins or loses on: every fact source-traceable, every AI answer cited, every schema change versioned, every entity tagged human-vs-AI. If those fail, it reduces to another untrustworthy "aviation AI chatbox" — and Core Value (in `.planning/PROJECT.md`) explicitly forbids that outcome.

### 2. Where we are right now

| Item | Value |
|------|-------|
| Current phase | **Phase 1** of 6 — Repo Skeleton + Git Baseline + PRD v0 |
| Current schema version | **N/A** (Phase 2 will set ontology v0.1.0) |
| Last touched by | (filled in by each plan's SUMMARY.md) |
| Next planned action | Execute Phase-1 plans, then `/gsd-research-phase 2` then `/gsd-plan-phase 2` |
| Blockers | None |

Source of truth for current position: [`.planning/STATE.md`](.planning/STATE.md). Source of truth for the full roadmap: [`.planning/ROADMAP.md`](.planning/ROADMAP.md).

### 3. Repo layout (what lives where)

```
ontology/          # SCHEMA LAYER (Phase 2 fills) — JSON Schema files defining what can exist
  schemas/         #   base + per-entity-type + per-relation-type schemas
  vocabularies/    #   controlled lists (ATA chapters, jurisdictions, provenance methods)
  mappings/        #   placeholders for ATA / S1000D / AP233 future mappings
instances/         # CONTENT LAYER (Phase 4 fills) — actual entity + relation YAML records
  entities/<type>/<id>.yaml
  relations/<id>.yaml
  _pending/        #   AI-extracted quarantine — promotion to canonical requires human review
docs/              # DOCUMENT LAYER (Phase 4 fills) — source PDFs (LFS) + processed.md + metadata.yaml
wiki/              # Wiki.js Git-synced Markdown (Phase 6 wires) — narrative pages only
deploy/            # DEPLOYMENT LAYER (Phase 6 fills) — docker-compose draft, NOT for execution
scripts/           # AUTOMATION LAYER
  validators/      #   (Phase 3) per-rule validators (schema, ids, relations, provenance, links)
  importers/       #   (Phase 4) document import helpers
  exporters/       #   (stubs in Phase 1; real impls in Phase 5+) to_ragflow.py / to_rdf.py / to_neo4j.py / to_jsonl_triples.py
tests/             # validator self-tests + valid/invalid fixtures (Phase 3)
evaluation/        # ≥30 RAG eval queries (Phase 5)
process-log/       # AI session audit trail (per CLAUDE.md user preference)
.planning/         # GSD planning artifacts (PROJECT, ROADMAP, REQUIREMENTS, research/, phases/)
.github/workflows/ # CI (Phase 1 baseline; Phase 3 makes it real)
```

Locked layout source: [`.planning/research/ARCHITECTURE.md`](.planning/research/ARCHITECTURE.md). Do NOT introduce new top-level directories without an ADR in `.planning/decisions/`.

### 4. Naming + ID conventions (locked)

- **Entity ID:** `<type-prefix>:<kebab-slug>` — examples: `comp:cfm56-7b`, `ac:b737-800`, `reg:ccar-25-1309`
- **URI form (for cross-backend stability):** `aviationkb://<type>/<slug>@<version>`
- **Relation file name:** `<predicate>__<subject-id>__<object-id>.yaml`
- **Branch name:** `phase-<NN>-plan-<NN>-<slug>` (matches GSD convention)
- **Schema version field on every record:** `schema_version: <semver>` (Phase 2 sets baseline `0.1.0`)

Full ID + URI ADR will be committed in Phase 2 under `.planning/decisions/`.

### 5. Glossary (seed — expanded in Phase 6)

| Term | Meaning |
|------|---------|
| **Canonical** | A record that has passed validators and lives outside `instances/_pending/`. Trusted for retrieval. |
| **Pending** | An AI-extracted record awaiting human review. Lives under `instances/_pending/`. NEVER retrieved by RAG. |
| **Hybrid reviewed** | `provenance.method` enum value meaning AI-drafted then human-checked. Required for promotion from `_pending/` → canonical. |
| **Supersession chain** | The `RegulationClause.superseded_by` link from old regulation versions to the active replacement. |
| **5-minute stranger test** | A fresh AI/human reads a doc cold; if they can't orient in 5 minutes, the doc fails R12. |
| **Citation injection** | System (NOT LLM) injects `[CITE:chunk_id]` tokens; render layer resolves to (doc, page, section, url). LLM cannot self-author citations — that's a Pitfall 8 vector. |
| **No-context guardrail** | If retrieval returns 0 chunks above threshold, pipeline short-circuits to "not found" without calling the LLM. Hard rule. |

Full bilingual glossary (≥50 entries) lands in `docs/GLOSSARY.md` in Phase 6.

### 6. Open questions (resolves at)

Tracked in [`.planning/research/SUMMARY.md`](.planning/research/SUMMARY.md) "Open Questions" section. Highlights:
- S1000D Issue 6 DMC field shape → Phase 2
- RAGFlow 0.25.1 table-chunk preservation → Phase 5
- Triple export format (RDF vs JSON-LD vs JSONL) → Phase 2 ADR
- Embedding mini-benchmark → Phase 5

### 7. House rules (do / don't)

**Do:**
- Read [`.planning/PROJECT.md`](.planning/PROJECT.md) Constraints + Out-of-Scope before suggesting any tech change.
- Run all work through GSD commands (`/gsd-plan-phase`, `/gsd-execute-phase`, `/gsd-quick`, `/gsd-debug`) per [`CLAUDE.md`](CLAUDE.md).
- Commit via `gsd-tools commit` so artifacts land atomically.
- Add an "AI 接力开发指南" section to every design doc you create.
- Treat Git as the single source of truth. Wiki.js Postgres = cache. RAGFlow vector store = derivative.

**Do NOT:**
- Introduce Dify, Vue/React custom frontends, Neo4j/Nebula in v1, decision-making agents, auto-crawlers, OCR pipelines, or RAGFlow OIDC SSO. All explicitly out of scope (`.planning/PROJECT.md` + `.planning/REQUIREMENTS.md` "Out of Scope").
- Inline relation IDs as fields on entity records (Anti-Pattern 1 in [ARCHITECTURE.md](.planning/research/ARCHITECTURE.md)). Relations live in their own files under `instances/relations/`.
- Promote AI-extracted records from `instances/_pending/` to canonical without `provenance.method=hybrid_reviewed` + populated `reviewer` + `reviewed_at`.
- Let an LLM self-author citations. System injects `[CITE:chunk_id]`; render layer resolves.
- Start real services in v1 (no `docker-compose up`, no `wiki-js dev`). v1 ships drafts + docs only.

### 8. How to resume work

1. Read [`.planning/STATE.md`](.planning/STATE.md) for current position
2. Read the latest SUMMARY under `.planning/phases/<current-phase>/` for what was just done
3. Read [`.planning/ROADMAP.md`](.planning/ROADMAP.md) for what comes next
4. If picking up mid-phase: run `/gsd-execute-phase <phase>`. If starting a new phase: run `/gsd-plan-phase <phase>` (research first via `/gsd-research-phase <phase>` for Phase 2 and Phase 5).

***

## Project documents

| Document | Purpose |
|----------|---------|
| [`.planning/PROJECT.md`](.planning/PROJECT.md) | What this project is, Constraints, Out-of-Scope, Key Decisions |
| [`.planning/REQUIREMENTS.md`](.planning/REQUIREMENTS.md) | 94 v1 requirement IDs across 13 categories |
| [`.planning/ROADMAP.md`](.planning/ROADMAP.md) | 6-phase build plan with success criteria per phase |
| [`.planning/STATE.md`](.planning/STATE.md) | Current phase, plan, blockers, next action |
| [`.planning/research/SUMMARY.md`](.planning/research/SUMMARY.md) | Research synthesis, pinned decisions, open questions |
| [`.planning/research/ARCHITECTURE.md`](.planning/research/ARCHITECTURE.md) | Component map, data flow, repo layout, anti-patterns |
| [`.planning/research/STACK.md`](.planning/research/STACK.md) | Pinned tool versions and rationale |
| [`.planning/research/PITFALLS.md`](.planning/research/PITFALLS.md) | 12 critical pitfalls with prevention guidance |
| [`.planning/design/PRD_v0.md`](.planning/design/PRD_v0.md) | Directional PRD (Phase 1 — created by Plan 05) |
| [`CLAUDE.md`](CLAUDE.md) | Project-level Claude Code conventions (auto-generated from STACK.md) |

## Core Value (do not violate)

> **每一条知识都可追溯来源，每一个 AI 回答都有 citation；schema 可演化、版本化、对人类和 AI 都可读。**
>
> Every fact is source-traceable. Every AI answer carries a citation. Schemas evolve, are versioned, and are readable by both humans and AI.

If any other property is sacrificed under pressure, this one cannot be. Otherwise the project becomes another untrustworthy aviation chatbox.

***

## Phase map

| Phase | Goal | Research | Status |
|-------|------|----------|--------|
| 1. Repo Skeleton + Git Baseline + PRD v0 | Lock layout, LFS, CI no-op stubs, pre-commit, AI handoff README, directional PRD | No | **In progress** |
| 2. Ontology Schema v0.1.0 | 17+4 entity + 13+5 relation schemas, mandatory provenance/confidence, schema versioning | **Yes** | Pending |
| 3. Validators + CI Active | `validate.py` + per-rule validators, fixture suite, CI runs full validation | No | Pending |
| 4. Demo Data + Document Import Spec | ≥1 instance per type, ≥3 relations, ≥3 source documents, supersession + AI-pending demo | No | Pending |
| 5. RAG Pipeline Design (document-only) | Chunking, BGE-M3 selection, hybrid retrieval, citation injection, no-context guardrail, ≥30 eval queries | **Yes** | Pending |
| 6. Deployment Plan + PRD v1 + Future Roadmap + AIH Polish | docker-compose draft, topology, env example, future-phase triggers, final PRD, R12 polish | No | Pending |

Full success criteria per phase: [`.planning/ROADMAP.md`](.planning/ROADMAP.md).

***

## 5-minute stranger test (run this on yourself)

After reading the AI 接力开发指南 section above, you should be able to answer **all** of these in under 5 minutes without asking the user:

- [ ] What does this project deliver? (one paragraph)
- [ ] What is the current phase? (find it in this README and STATE.md)
- [ ] What is the next concrete action? (find it in STATE.md "Next Action")
- [ ] Where do entity YAML records live? (`instances/entities/<type>/<id>.yaml`)
- [ ] Where do AI-extracted records go before promotion? (`instances/_pending/`)
- [ ] Why do relations get their own files? (Anti-Pattern 1 — graph-DB migration target)
- [ ] What technologies are explicitly OUT of scope in v1? (Dify / Neo4j / custom frontend / Decision agents / OCR / Auto-crawlers / RAGFlow OIDC)
- [ ] What is the rule for AI-authored citations? (LLM cannot self-cite — system injects `[CITE:chunk_id]`)

If you cannot answer any of these from this README + STATE.md + the linked research docs, the README has failed R12 / AIH-02 — flag it as a blocker and improve the README before proceeding.

***

## License + ownership

(To be set in Phase 6.) v1 is internal scaffolding; license decision deferred until first external contributor or first public release.

***

*This README is the primary AI handoff surface. It MUST be updated when (a) the current phase changes, (b) the schema version changes, (c) any locked decision in the AI 接力开发指南 section changes, (d) the layout under `## Repo layout` evolves.*

*Last touched by: gsd-planner-phase / Phase 1 / Plan 02 / 2026-05-03*

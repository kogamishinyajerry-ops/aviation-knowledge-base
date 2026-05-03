# ROADMAP_FUTURE — v2+ Trigger Conditions

> **AI 接力开发指南** (ROAD-01, ROAD-02): This file documents features explicitly
> EXCLUDED from v1 along with the precise condition that would make each one
> eligible to enter a future roadmap phase. The condition is the ONLY
> permissible reason to add the feature in v1.5+; "we should add X" is not
> sufficient.
>
> Status: created 2026-05-03 (Phase 6, plan 06-03). Updated when a trigger
> fires, NOT when someone has an idea.
>
> Source authority for deferrals: `.planning/research/STACK.md` §"What NOT to
> Use", `.planning/REQUIREMENTS.md` §"v2 Requirements" + §"Out of Scope",
> `CLAUDE.md` Constraints.

## How to Read

Each entry has a uniform shape:

- **What** (one paragraph): what the feature is, what it does in user terms.
- **Why deferred** (one paragraph): why v1 explicitly excluded it.
- **Promote when** (a concrete, testable trigger): when this becomes true,
  the feature is eligible to enter the next ROADMAP.md phase pass. Conditions
  are numbered; multi-condition triggers state explicitly whether they are
  conjunctive (all must hold, AND) or disjunctive (any one suffices, OR).
- **v2 REQ-IDs** (links to REQUIREMENTS.md §v2): exact IDs this feature would
  close.
- **Pitfall guard** (link to `.planning/research/PITFALLS.md` if applicable):
  the pitfall this feature must NOT introduce while solving its problem.
- **Cross-references**: pointers to deploy docs / design docs that already
  partially scaffold this feature.

## How to Update

**Adding a new future feature**: copy the template, fill all 6 sections. Do
NOT add a feature without a "Promote when" trigger that is grounded in
something measurable (date, count, upstream bug closing, user demand,
specific failure pattern observed in evaluation results).

**Firing a trigger**: when the trigger condition is met, file an ADR in
`.planning/decisions/` documenting the firing event (which condition fired,
the evidence, the link to the eval result / GitHub issue / user request),
then propose a new ROADMAP phase via `/gsd-roadmap-update`. Do NOT silently
start work — the trigger must be explicit and reviewable.

**Demoting a feature** (rare): if a feature is judged obsolete (e.g.
upstream stack change makes it irrelevant), append a strike-through entry
plus an ADR explaining the demotion. Never silently delete.

---

## 1. GraphRAG Layer

- **What**: Hybrid retrieval combining the existing vector + BM25 hybrid
  pipeline (Phase 5) with graph-traversal queries over relations. A user
  query like "list every `RegulationClause` that supersedes a clause cited
  by `SimulationCase` X" requires joining the citation graph + the
  supersession chain — graph traversal returns this in one hop, while
  vector retrieval cannot; it can only surface chunks that happen to mention
  both endpoints.
- **Why deferred**: v1 scale (≤10K triples per CLAUDE.md Out-of-Scope and
  STACK.md §"What NOT to Use") sits below the break-even point where graph
  traversal beats hybrid vector + relational join. RAGFlow's hybrid
  retrieval already handles citation-style queries via metadata filters
  (per `.planning/design/RAG_PIPELINE.md` §3). A graph layer adds
  operational + storage complexity without proven win at v1 corpus size.
- **Promote when** (any one of the following, OR):
  1. Total entity + relation instance count under `instances/` (counted by
     `find instances -name '*.yaml' | wc -l`, excluding `_pending/`)
     exceeds **10,000** records, OR
  2. ≥**5** queries in `evaluation/queries.yaml` are documented as failing
     because hybrid retrieval cannot follow a multi-hop relation chain
     (logged as `failure_mode: graph_traversal_needed` in the eval result
     output of RAG-07's evaluation harness), OR
  3. A specific use case lands that requires path queries the hybrid
     pipeline structurally cannot answer — e.g. "show all components
     affected by airworthiness directive chain X→Y→Z" with cycle detection,
     or "compute transitive closure of `part_of` for AircraftSystem A".
- **v2 REQ-IDs**: GRAPH-01, GRAPH-03, GRAPH-04
- **Pitfall guard**: `.planning/research/PITFALLS.md` Pitfall 10 (Wiki.js /
  RAGFlow content desync — truth + cache discipline) — the graph layer is
  a DERIVATIVE of YAML-on-Git truth, not a parallel truth. It MUST be
  rebuildable from Git via `scripts/exporters/to_rdf.py` /
  `to_neo4j.py` and MUST NOT accept writes that bypass the YAML source.
- **Cross-references**: `.planning/research/ARCHITECTURE.md` §"Migration
  Path to GraphRAG" (line ~263 — empty exporter stubs already present);
  `scripts/exporters/to_jsonl_triples.py` (already produces triples per the
  v1 exporter design); REQUIREMENTS.md §v2 GRAPH cluster.

## 2. Agent Layer

- **What**: Tool-using agents that operate on the knowledge base — guided
  ingestion (LLM proposes entity extractions from a new source document,
  human approves before promotion), conflict detection (regulation X vs
  regulation Y inconsistency surfacing), staleness detection (Regulation
  supersession alerts when an `effective_date` passes or a `superseded_by`
  link is added upstream).
- **Why deferred**: Per CLAUDE.md Constraints + REQUIREMENTS.md "Out of
  Scope": "v1 = no decision-making agents, no auto-tool-use loops; v1 is
  RAG retrieval-augmented Q&A only." Agent introduction risks replaying
  the H-Darrieus / accident-report failure modes (PITFALLS.md Pitfall 2):
  unreviewed AI output entering canonical and being indistinguishable from
  human-curated knowledge.
- **Promote when** (all of the following, AND):
  1. The `instances/_pending/` quarantine has accumulated ≥**100**
     AI-extracted records and the manual-review queue is the documented
     bottleneck for ingestion velocity (logged in `process-log/` as
     "review queue ≥1 week behind ingestion" for ≥4 consecutive weeks),
     AND
  2. Phase 3's PROV-04 reject-without-reviewer rule (`provenance.method =
     ai_extracted` AND `confidence > 0.85` AND no `reviewer` → REJECT)
     has been measured stable for ≥**3 months** under real load with zero
     false promotions slipping into canonical (verified by an audit script
     scanning all canonical records' `provenance` fields), AND
  3. A specific failure-pattern justifies tool-use loops — e.g. "we keep
     missing supersession-chain breaks because manual review can't keep
     up with regulation update frequency" or "conflict detection between
     two CFR parts requires LLM-assisted diffing".
- **v2 REQ-IDs**: AGENT-01, AGENT-02, AGENT-03
- **Pitfall guard**: `.planning/research/PITFALLS.md` Pitfall 2 (AI extraction
  without review). Agents do NOT promote to canonical; they only stage in
  `instances/_pending/` with confidence scores. Human review remains the
  canonical promotion gate, permanently. PITFALLS.md Pitfall 5 (regulation
  supersession chain) is the specific staleness-detection target for
  AGENT-03.
- **Cross-references**: `.planning/research/PITFALLS.md` Pitfall 2 +
  Pitfall 5; `instances/_pending/README.md` (the staging convention this
  builds on); REQUIREMENTS.md §v2 AGENT cluster.

## 3. Graph DB Backend (Neo4j / Nebula)

- **What**: Replace YAML-on-Git as the entity/relation truth source — or
  add a synchronized derivative store — with a graph database providing
  native traversal, indexing, and concurrent multi-author writes. Candidate
  backends: Neo4j (mature, Cypher), Nebula (distributed, GQL), ArangoDB
  (multi-model fallback).
- **Why deferred**: Per CLAUDE.md Constraints + STACK.md "What NOT to Use" —
  premature backend lock-in; YAML+JSON Schema is sufficient for ≤10K triples
  with full schema validation; Git provides audit + diff + branch-based
  review for free, which a graph DB does not. ARCHITECTURE.md §"Migration
  Path to GraphRAG" already designs the migration hooks (empty exporter
  stubs in `scripts/exporters/`).
- **Promote when** (all of the following, AND):
  1. GraphRAG Layer (entry §1 above) trigger has fired AND a measured
     A/B comparison demonstrates graph-on-vector hybrid outperforms
     vector-only on ≥**3** distinct query categories from
     `evaluation/queries.yaml` (recall@5 improvement ≥10 percentage
     points), AND
  2. Concurrent multi-author writes become a real bottleneck — ≥**3**
     reviewers report being blocked on the PR queue for ≥**1 day** at
     least once per week, sustained for ≥**4 weeks** (YAML-on-Git
     serializes through PR review), AND
  3. ADR in `.planning/decisions/` documents: backend choice (Neo4j vs
     Nebula vs ArangoDB) with rationale, URI stability rule (how
     `id` fields in YAML map to graph node IDs across rebuilds), and the
     rebuild-from-Git fallback procedure (graph DB MUST be reconstructible
     from `instances/*.yaml` in <1 hour for the v2 corpus size).
- **v2 REQ-IDs**: GRAPH-02
- **Pitfall guard**: `.planning/research/PITFALLS.md` Pitfall 10 (Wiki.js /
  RAGFlow content desync — truth + cache discipline). Git remains
  authoritative; graph DB is a synchronized derivative or replaces YAML
  ONLY after an explicit migration ADR with dual-write transition window.
  No silent dual-truth at any time.
- **Cross-references**: `.planning/research/ARCHITECTURE.md` §"Migration
  Path to GraphRAG"; `.planning/research/STACK.md` §"What NOT to Use" row
  "Neo4j / Nebula / ArangoDB / Apache Jena" (deferred rationale);
  REQUIREMENTS.md §v2 GRAPH-02.

## 4. OCR Pipeline

- **What**: Optical Character Recognition for scanned-PDF source documents
  that lack a text layer. Activates RAGFlow's DeepDoc backend (visual OCR +
  table-structure recognition) — or Tesseract / PaddleOCR as fallbacks —
  instead of the v1 default OpenDataLoader-PDF (which requires a text
  layer).
- **Why deferred**: Per CLAUDE.md Out-of-Scope + REQUIREMENTS.md §"Out of
  Scope": "Text-layer PDF/MD/HTML/DOCX only in v1; OCR adds non-deterministic
  fail mode." Phase 4 source documents (FAR sections, the CFD paper,
  accident report excerpt) are all text-layer. OpenDataLoader-PDF handles
  100% of the v1 corpus deterministically (~14× faster than DL-based
  parsers per STACK.md §"Document Ingestion Stack"). OCR introduces
  non-deterministic table-structure loss (PITFALLS.md Pitfall 6).
- **Promote when** (any one of the following, OR):
  1. ≥**5** scanned-only PDF documents enter the corpus that
     OpenDataLoader-PDF cannot extract text from (verified by
     `metadata.yaml` flag `requires_ocr: true` on each, AND a parse-attempt
     log under `process-log/` showing OpenDataLoader produced empty or
     garbage output), OR
  2. A user-priority document — regulatory amendment, accident report
     supplement, or legacy maintenance manual — is scanned-only AND must
     be ingested for a specific named deliverable (logged as a request
     with deliverable name + due date in `process-log/`), AND no text-layer
     equivalent is available from the issuing body, OR
  3. ≥**3** distinct contributors independently request OCR support over
     a ≥**3-month** window (logged via GitHub issues tagged `ocr-request`),
     indicating systemic rather than one-off demand.
- **v2 REQ-IDs**: OPS-04
- **Pitfall guard**: `.planning/research/PITFALLS.md` Pitfall 6 (chunking
  destroys tables/formulas — high-frequency in PDF airworthiness docs).
  OCR often loses table structure entirely; the OCR pipeline MUST preserve
  table-as-atomic-chunk per `.planning/design/RAG_PIPELINE.md` §2.2,
  including a regression test against a known-table scanned PDF before
  promotion to canonical ingest.
- **Cross-references**: `.planning/research/STACK.md` §"Document Ingestion
  Stack" (DeepDoc fallback documented and ready); `.planning/design/RAG_PIPELINE.md`
  §2 (chunking strategy that any new backend must satisfy); REQUIREMENTS.md
  §v2 OPS-04.

## 5. Multi-tenant RBAC

- **What**: Role-based access control across multiple organizations or
  projects, with per-tenant isolation of `instances/`, `docs/`, and
  Wiki.js page trees. Enables, e.g., one deployment hosting both an
  airframer's airworthiness corpus and a CFD lab's research corpus
  without cross-visibility.
- **Why deferred**: Per CLAUDE.md Out-of-Scope + REQUIREMENTS.md §"Out of
  Scope": "v1 single-org admin/reader; defer to v2 if user demand
  emerges." Adding multi-tenant from day one over-designs the data model
  (every entity needs a `tenant_id` field, every validator needs tenant
  scoping, every query needs a tenant filter) and locks ontology choices
  before the user pattern is observed.
- **Promote when** (all of the following, AND):
  1. ≥**2** distinct organizations or projects need to share the
     deployment while keeping their `instances/` content separate
     (confirmed via signed agreement or onboarding ticket in
     `process-log/`, not speculative), AND
  2. Single-org admin/reader auth is documented as insufficient — at
     least one specific access-control failure logged (e.g. "Org A
     reviewer accidentally promoted Org B's pending entity to canonical"),
     AND
  3. ADR in `.planning/decisions/` documents the chosen RBAC model
     (org-per-tenant vs project-per-tenant vs row-level), the `tenant_id`
     schema migration plan (ONT-E baseline + relation schemas), and the
     query-scoping pattern for both validator and RAGFlow retrieval, AND
  4. SSO Unification (entry §6 below) trigger has fired OR a parallel
     ADR justifies multi-tenant on local-account auth (rare; usually
     RBAC presumes SSO).
- **v2 REQ-IDs**: OPS-02
- **Pitfall guard**: `.planning/research/PITFALLS.md` Pitfall 4 (schema
  migration without a path). Adding `tenant_id` to base entity/relation
  schemas is a breaking schema change requiring: (a) full migration script
  under `migrations/` per VER-04, (b) dual-version reader window (validator
  accepts both N and N-1 for ≥1 release), (c) bump
  `ontology/VERSION` major or minor per VER-01.
- **Cross-references**: `ontology/_meta.schema.json` (where `tenant_id`
  would land); `deploy/authentik-phase2.md` (auth is prerequisite for
  RBAC); REQUIREMENTS.md §v2 OPS-02.

## 6. SSO Unification (Authentik OIDC)

- **What**: Single sign-on across Wiki.js + RAGFlow via Authentik as OIDC
  IdP. Eliminates duplicate user accounts (one in each service today),
  centralizes auth audit, enables future SCIM provisioning.
- **Why deferred**: Per `deploy/authentik-phase2.md` (authored Phase 6
  plan 06-01) — RAGFlow OIDC has open bug **#12568** (Keycloak
  redirect-loop since the Quart migration) and feature-request **#3495**
  (OIDC support overall) is still pending merge. Wiki.js side is
  documented and works (Authentik integration guide verified — see
  STACK.md "Sources"); RAGFlow side is the blocker. v1 = local accounts
  on each service.
- **Promote when** (all of the following, AND):
  1. RAGFlow issue **#12568** is closed upstream (verify via
     `gh issue view 12568 --repo infiniflow/ragflow --json state` →
     `"CLOSED"`), AND
  2. RAGFlow feature-request **#3495** is merged AND OIDC support is
     present in a stable RAGFlow release tag ≥**0.26.0** (verify via
     release notes mentioning OIDC + a working integration test in our
     own staging), AND
  3. ≥**2** confirmed user accounts need cross-service navigation
     (logged as a real demand in `process-log/`, not speculative — e.g.
     "reviewer X complained about logging in twice per session, Y times
     per week, for Z weeks").
- **v2 REQ-IDs**: OPS-01
- **Pitfall guard**: None specific to data integrity (auth is orthogonal
  to the YAML truth + citation pitfalls). General security review
  required at promotion time.
- **Cross-references**: `deploy/authentik-phase2.md` (the authoritative
  deferral doc, with the same Promote-when conditions; see plan 06-01);
  `deploy/docker-compose.yml.draft` (commented `authentik` service block
  ready to uncomment when this fires);
  `.planning/research/STACK.md` §"Auth / Reverse Proxy" + Sources
  (RAGFlow OIDC bug #12568 + FR #3495 references); REQUIREMENTS.md §v2
  OPS-01.

## 7. Decision Agent

- **What**: An agent that takes a user goal — e.g. "draft a certification
  compliance matrix for Aircraft X against EASA CS-25" — and autonomously
  navigates the KB, proposes draft outputs (matrix entries, gap analyses,
  draft procedures), asks clarifying questions, and revises based on
  feedback. Distinct from §2 (Agent Layer): §2 stages individual
  extractions for review; §7 produces multi-step deliverables.
- **Why deferred**: Per CLAUDE.md Out-of-Scope + REQUIREMENTS.md §"Out of
  Scope": "Decision-making agents (auto-tool-use loops) excluded; v1 = RAG
  retrieval-augmented Q&A only." Decision agents produce contestable
  outputs ("the agent decided X based on retrieved Y") that are
  STRUCTURALLY HARDER to audit than retrieval ("the system retrieved
  chunks Y, the LLM cited them") because intermediate reasoning steps
  may not have direct citations. The Core Value invariant — "every AI
  answer has citations" — is structurally weaker for decision agents
  unless every action is provenance-tagged at every step.
- **Promote when** (all of the following, AND):
  1. RAG Q&A (the v1 deliverable) has been measured **stable in
     production** for ≥**6 months** with citation-validation failure
     rate ≤**1%** (validated by the RAG-05 guardrail metrics over a
     rolling 30-day window), AND
  2. A specific deliverable use case is documented (e.g. "compliance
     matrix drafting for an AC-25-class aircraft") that RAG Q&A cannot
     satisfy because it requires multi-step synthesis with intermediate
     document creation — and a manual workaround is documented as a real
     bottleneck (≥**N** human-hours per deliverable, repeated ≥**M**
     times), AND
  3. ADR in `.planning/decisions/` specifies how decision-agent
     provenance is structured: every agent action produces an
     `ai_extracted` `_pending/` entity with full audit trail (input
     query, retrieved chunks, intermediate reasoning trace, output
     citation set), promotable only via human review per PROV-04/05,
     AND
  4. Agent Layer (entry §2 above) trigger has fired AND its
     staging→canonical promotion pipeline has been load-tested with
     ≥**100** ai_extracted records reviewed without false promotion
     (proves the substrate this depends on is stable).
- **v2 REQ-IDs**: None specific in REQUIREMENTS.md §v2 today; this is a
  v3-class category. Closure requires creating new REQ-IDs in a v2
  requirements doc when the trigger fires (the ADR per condition 3
  above must include the proposed new REQ-IDs and their acceptance
  criteria).
- **Pitfall guard**: `.planning/research/PITFALLS.md` Pitfall 2 (AI
  extraction without review). Decision agents STILL cannot promote to
  canonical without human review; the gate is permanent. Additionally,
  PITFALLS.md Pitfall 8 (citation injection hallucination — page-number
  fabrication) is a higher-stakes risk for decision agents than for
  retrieval Q&A because output documents may be acted upon directly.
- **Cross-references**: `.planning/research/PITFALLS.md` Pitfall 2 +
  Pitfall 8; CLAUDE.md Constraints "decision-making agents excluded"
  (this entry exists to make explicit when that constraint can be
  revisited); REQUIREMENTS.md §v2 (no current AGENT-* entry covers this
  — by design, to force ADR-driven scope expansion).

## Trigger Audit Log

When a trigger fires, log it here with the firing date, the feature, the
specific condition that fired (e.g. "§4 condition 1"), the ADR link, and
the eventual outcome (entered ROADMAP / merged into existing phase /
deferred again with updated criteria).

| Date       | Feature | Trigger condition fired | ADR | Outcome |
|------------|---------|-------------------------|-----|---------|
| (none yet) |         |                         |     |         |

---

## Maintainer Note

If you find yourself wanting to add a feature here without a measurable
trigger, **STOP**. The point of this document is the trigger. A vague
entry ("we'll OCR later", "graph DB is the future") is worse than no
entry — it normalizes "we'll add it eventually" thinking, which is the
exact failure mode that drives every v2 requirement into v1 in the
projects that fail.

Concrete trigger forms that count:

- **Counts**: "≥N records of kind X", "≥M users", "≥K reviewers blocked"
- **Dates**: "after stable for N months under real load"
- **Upstream events**: "GitHub issue #12568 closed", "RAGFlow ≥0.26.0
  released with OIDC"
- **Eval-set failures**: "≥5 queries fail with `failure_mode: X` in
  `evaluation/queries.yaml`"
- **Documented user demand**: "≥N independent contributors request
  feature, logged via tracked tickets, sustained ≥M months"

Forms that do NOT count:

- "When we have time"
- "When scale demands it" (without specifying scale)
- "Future enhancement"
- "Someday"
- "If users want it" (without a count)

The trigger is the gate. The trigger is the promise. The trigger is
the only reason this document exists.

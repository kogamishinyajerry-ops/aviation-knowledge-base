# docs/ — Document Import Workflow & AI 接力开发指南

> **AI 接力开发指南** (AIH-01): A fresh Claude / Codex / DeepSeek session
> reading this file alone (≤5 minutes) should know:
>   1. Where source documents live and what 3 files each must ship.
>   2. Which fields metadata.yaml must contain.
>   3. What happens when a document is `restricted` / `itar_ear` (NOT ingested).
>   4. Where AI-extracted entities go and how they get promoted to canonical.
>   5. The H-Darrieus REJECT rule that protects the corpus from unreviewed-but-confident AI output.
>   6. The worked example — [`instances/entities/expert-note/canonical-example.yaml`](../instances/entities/expert-note/canonical-example.yaml).

This README is the authoritative document-import contract for the Aviation
Knowledge Base MVP. It pairs with three other AI 接力 docs that together
form the v0.1.0 contributor onboarding surface:

- [`scripts/validators/README.md`](../scripts/validators/README.md) — validator semantics + public API every PR must pass.
- [`instances/_pending/README.md`](../instances/_pending/README.md) — promotion-gate details for AI-extracted records.
- [`ontology/_meta.schema.json`](../ontology/_meta.schema.json) — canonical provenance / confidence / source contract.

---

## 1. Directory Convention (DOC-01)

Every source document lives at:

```
docs/<domain>/<doc-id>/source.{pdf,md,docx,html}
docs/<domain>/<doc-id>/processed.md
docs/<domain>/<doc-id>/metadata.yaml
```

Domains shipped in v0.1.0: `regulations/`, `cfd-papers/`, `accident-reports/`.
Reserved for future expansion (add via PR + ROADMAP_FUTURE.md trigger update):
`standards/`, `manuals/`, `internal-notes/`.

`<doc-id>` is a kebab-case slug stable across versions (e.g. `far-25-1309`,
`nasa-tm-2014-218175`, `ntsb-aar-09-03`). The matching `Document` entity
URI mirrors the slug:

```
aviationkb://document/<doc-id>@<version>
```

The three-file layout is enforced by Phase-3 validators and the Phase-5
RAGFlow exporter — every document needs all three files (source + processed
+ metadata) before it is considered ingest-ready. PDFs go through Git LFS
per `.gitattributes`; processed Markdown lives in Git directly so diffs
are reviewable.

## 2. metadata.yaml Mandatory Fields (DOC-02)

Per the Phase-4 schema lock, every `metadata.yaml` MUST populate all 11
fields below:

| Field             | Type / domain                                                                                  |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| title             | string                                                                                         |
| doc_type          | enum: `regulation` \| `standard` \| `paper` \| `report` \| `manual` \| `accident_report` \| `internal_note` |
| language          | enum: `zh` \| `en` \| `mixed`                                                                  |
| source_url        | URI                                                                                            |
| publication_date  | ISO date `YYYY-MM-DD`                                                                          |
| effective_date    | ISO date `YYYY-MM-DD`                                                                          |
| confidentiality   | enum: `public` \| `internal` \| `restricted` \| `itar_ear`                                     |
| domain_tags       | array of kebab-case strings                                                                    |
| version           | string (document version, e.g. "Amendment 25-145")                                             |
| file_hash         | `sha256:<hex>` of `source.md` (or canonical text rendition)                                    |
| processed_by      | string (e.g. `manual-pandoc-3.x`, `ragflow-opendataloader-0.25.1`)                             |

A worked example sits at
[`docs/regulations/far-25-1309/metadata.yaml`](regulations/far-25-1309/metadata.yaml).
PRs that omit any of the 11 fields fail CI's `metadata.yaml` schema check;
contributors should treat the table above as a literal checklist before
opening review.

## 3. Confidentiality Gating (DOC-04 — HARD RULE)

`restricted` and `itar_ear` documents are **not ingested by default**.

The Phase-5 RAGFlow exporter (`scripts/exporters/to_ragflow.py`, planned)
reads `metadata.yaml` for every doc and:

- `public` / `internal` → uploaded to RAGFlow.
- `restricted` / `itar_ear` → SKIPPED with a stderr warning. The
  document remains in `docs/` for source-of-truth + audit, but is not
  exposed to retrieval.

Until that exporter ships, human reviewers enforce the rule manually:
**do not put `restricted` / `itar_ear` documents into `docs/` unless your
repo is itself classified at the matching level.** The four-value enum
exists precisely so a future change of policy (e.g. uploading `internal`
docs to a separate locked-down RAGFlow tenant) can be expressed in
metadata without a schema change.

## 4. Manual Import Workflow

The default path for a human curator landing a single document:

1. Author creates `docs/<domain>/<doc-id>/source.{pdf,md,…}`.
2. Author runs `pandoc` / `OpenDataLoader` to produce `processed.md`
   (or hand-writes it for short text-only docs).
3. Author writes `metadata.yaml` populating all 11 mandatory fields
   (Section 2 above).
4. Author authors the matching `instances/entities/document/<doc-id>.yaml`
   (Document entity record) so other entity / relation records can
   `cites` it via the URI.
5. Author opens PR; pre-commit + CI run `python scripts/validate.py` and
   `check-jsonschema` on the new YAML; the PR cannot merge if either
   tool fails.
6. Reviewer (default: `jane-reviewer` for this demo, real curator team
   in production — see Section 8) signs off.

Validators consume the `Document` entity record's `source.document_id`
to confirm it points at a real `Document` and not a dangling URI; this
is the cross-record half of source-citation integrity (PROV-06).

## 5. Scripted Import Workflow (AI-Assisted)

When an AI tool (Claude / Codex / DeepSeek / GPT) extracts entity or
relation records from a source document, the workflow is the same up
to the staging directory split:

1. AI tool emits YAML with `provenance.method: "ai_extracted"`,
   structured `confidence.{score, rationale}`, and structured
   `source.{document_id, locator, retrieval}`.
2. YAML lands at `instances/_pending/<entities|relations>/<type>/<slug>.yaml` —
   NEVER directly in canonical `instances/entities/` or
   `instances/relations/`. The validator fail-closes against this:
   any `ai_extracted` record outside `_pending/` is rejected at CI time
   (Phase-3 PROV-05 rule).
3. Human reviewer reads, edits content, and updates provenance:
   - `provenance.method`: change from `ai_extracted` → `hybrid_reviewed`
   - `provenance.reviewer`: a Person URI (e.g.
     `aviationkb://person/jane-reviewer@1`)
   - `provenance.reviewed_at`: ISO 8601 timestamp of the review
   - `provenance.tool`: which model / version produced the draft
     (e.g. `claude-opus-4-7`)
4. Reviewer opens PR moving the file from `_pending/` to canonical
   `instances/entities/<type>/` or `instances/relations/<type>/`.
5. CI validates the promoted record against the H-Darrieus REJECT rule
   (Section 6) and the `_pending` promotion gate documented in
   [`instances/_pending/README.md`](../instances/_pending/README.md).

A worked example lives at
[`instances/_pending/entities/expert-note/pending-ai-extracted-fadec-thermal-margins.yaml`](../instances/_pending/entities/expert-note/pending-ai-extracted-fadec-thermal-margins.yaml)
(Phase 4 DEMO-06). It is parked in `_pending/` so a future PR can
demonstrate the move-to-canonical step end-to-end.

## 6. The H-Darrieus REJECT Rule (PROV-04)

Even a record that stays in `_pending/` is REJECTED by the validator if
all three of:

- `provenance.method == "ai_extracted"` AND
- `confidence.score > 0.85` AND
- `provenance.reviewer` is null or empty

Rationale (lifted from `instances/_pending/README.md`): high confidence
on unreviewed AI output is the exact failure mode that produced the
H-Darrieus fabricated-figure incident in the project history. We
refuse to be that. The rule fires regardless of file location, so
`ai_extracted` records cannot launder themselves through staging on
score alone.

If you genuinely have AI-extracted output you trust at score > 0.85,
you must either:

- (a) lower the score honestly (typical when an AI agrees with itself
  but no external cross-check has happened), or
- (b) review it and bump method to `hybrid_reviewed` (with reviewer +
  reviewed_at populated).

There is no third option. ADR-005 records the full provenance enum and
the rule's history.

## 7. Worked Example — Canonical ExpertNote

[`instances/entities/expert-note/canonical-example.yaml`](../instances/entities/expert-note/canonical-example.yaml)
is the worked provenance example for this knowledge base (DEMO-04).
Open it to see:

- `provenance.method: human` (no AI involvement; the simplest provenance
  case)
- `confidence.score: 0.85` with a rationale ≥1 sentence stating WHY the
  score is what it is, not just what it is
- `source.{document_id, locator, retrieval}` fully populated — the
  `document_id` resolves to a real `Document` entity, `locator` scopes
  the citation to a specific clause / section, `retrieval` records
  WHERE and WHEN the citation was last fetched
- `i18n.label.{zh, en}` populated for cross-language retrieval

When in doubt, copy this file's shape and adapt content. Every entity
record in `instances/entities/` follows the same provenance / confidence
/ source discipline; the canonical example is the smallest one that
exercises every required field.

## 8. Reviewer Roster (v0.1.0)

| Reviewer URI                                  | Role                  | Affiliation |
| --------------------------------------------- | --------------------- | ----------- |
| `aviationkb://person/jane-reviewer@1`         | Default reviewer      | FAA (demo)  |
| `aviationkb://person/john-cfd-analyst@1`      | CFD-side authorship   | NASA (demo) |

For v0.1.0 the roster is two demo identities. Real production
deployments add reviewers via PR creating an
`instances/entities/person/<slug>.yaml` record + appending to this
table. Reviewer identity is what `provenance.reviewer` and
`provenance.actor` fields cite, so adding a new reviewer is part of
the audit trail itself, not metadata about it.

## 9. See Also

- [`scripts/validators/README.md`](../scripts/validators/README.md) — full validator semantics and the public API every PR must pass.
- [`instances/_pending/README.md`](../instances/_pending/README.md) — promotion-gate details and ADR-005 H-Darrieus history.
- [`ontology/_meta.schema.json`](../ontology/_meta.schema.json) — canonical provenance / confidence / source contract.
- [`.planning/decisions/`](../.planning/decisions/) — ADR-002 (entity additions), ADR-005 (provenance enum), ADR-007 (schema versioning).

## 10. AI 接力开发指南 — Reviewer-Bound Checklist

Before merging any PR that touches `docs/` or `instances/`:

- [ ] Schema validates: `python scripts/validate.py` exits 0 over the full corpus.
- [ ] `check-jsonschema --schemafile <leaf-schema> <yaml>` exits 0 for every new YAML.
- [ ] Provenance: every new record has `method`, `actor`, `actor_role`, `created_at`.
- [ ] Confidence: `score` is realistic (≤0.85 unless AI is reviewed → method=`hybrid_reviewed`).
- [ ] Source: `document_id` resolves to an existing `Document` entity (broken-ref check).
- [ ] If `confidentiality` is `restricted` / `itar_ear`: this document is INTENTIONAL and the repo is at the matching classification level.
- [ ] If `_pending/`: the record's reason for staying in `_pending/` is documented in `confidence.rationale` or a PR comment.
- [ ] Pre-commit + CI both green; reviewer roster (Section 8) records who signed off.

Last touched by: claude-opus-4-7 on 2026-05-03 (Phase 4 plan 04).

---
phase: 04-demo-data-document-import-spec
plan: 01
subsystem: demo-data-document-foundations
tags: [docs, document-entities, person, organization, doc-01, doc-02, doc-04, demo-03]
requires:
  - .planning/phases/03-ontology-validators/ — validate.py master CLI + 5 active validators
  - ontology/schemas/entity.{document,person,organization}.schema.json
  - ontology/schemas/entity.base.schema.json + ontology/_meta.schema.json
provides:
  - 3 source-document directories under docs/<domain>/<doc-id>/ with full DOC-02 metadata
  - 3 Document entity URIs (aviationkb://document/{far-25-1309,nasa-tm-2014-218175,ntsb-aar-09-03}@1)
  - 2 Person URIs (jane-reviewer, john-cfd-analyst) — provenance.actor / Person.affiliation targets
  - 3 Organization URIs (faa, nasa, ntsb) — Person.affiliation + issuing-body targets
affects:
  - Plans 04-02 (regulatory + airframe entities) and 04-03 (CFD entities) depend on these URIs
  - Plan 04-04 (relations + _pending demo + docs/README.md) depends on the Document URIs as source.document_id roots
tech-stack:
  added: []
  patterns:
    - "Provenance: every record uses method=human (no ai_extracted in canonical — H-Darrieus REJECT N/A)"
    - "Self-loop on provenance.actor accepted for synthetic Person records (Phase 3 validators do not require acyclic actor graph)"
    - "Document entity source.document_id self-references (matches Phase 3 fixture convention)"
key-files:
  created:
    - docs/regulations/far-25-1309/source.md
    - docs/regulations/far-25-1309/processed.md
    - docs/regulations/far-25-1309/metadata.yaml
    - docs/cfd-papers/nasa-tm-2014-218175/source.md
    - docs/cfd-papers/nasa-tm-2014-218175/processed.md
    - docs/cfd-papers/nasa-tm-2014-218175/metadata.yaml
    - docs/accident-reports/ntsb-aar-09-03/source.md
    - docs/accident-reports/ntsb-aar-09-03/processed.md
    - docs/accident-reports/ntsb-aar-09-03/metadata.yaml
    - instances/entities/document/far-25-1309.yaml
    - instances/entities/document/nasa-tm-2014-218175.yaml
    - instances/entities/document/ntsb-aar-09-03.yaml
    - instances/entities/person/jane-reviewer.yaml
    - instances/entities/person/john-cfd-analyst.yaml
    - instances/entities/organization/faa.yaml
    - instances/entities/organization/nasa.yaml
    - instances/entities/organization/ntsb.yaml
  modified: []
decisions:
  - "Used `org_type: regulator` for NTSB despite NTSB being investigative-only — closest match in entity.organization schema enum, rationale embedded in confidence.rationale"
  - "Omitted `jurisdiction` on NASA (multi-jurisdiction research org) and NTSB (independent investigative body) per schema description guidance"
  - "All 3 demo docs are `confidentiality: public` — restricted/itar_ear gating documented in plan 04-04 docs/README.md (deferred); H-Darrieus + AI-extracted demo also deferred to plan 04-04"
  - "Stand-in source.md files contain ≤500 word public extracts of the abstract / executive summary; full PDFs deferred to Git-LFS-backed real ingestion"
metrics:
  duration_minutes: ~10
  completed: 2026-05-03T11:36:00Z
  tasks_completed: 3
  files_created: 17
  files_modified: 0
---

# Phase 4 Plan 01: Demo data foundations (3 source docs + 8 entity URIs) Summary

> One-liner: Established the 3 source-document directories and 8 canonical entity URIs (3 Document + 2 Person + 3 Organization) that every other Phase 4 record will cite as `source.document_id` / `provenance.actor` / `Person.affiliation`.

## What was built

### Task 1 — 3 source-document directories (commit `95cc070`)

Created `docs/<domain>/<doc-id>/` skeletons for the DEMO-03 doc-type spread:

| Domain | Doc ID | Doc type | Confidentiality | File hash (SHA-256, prefix) |
|--------|--------|----------|-----------------|------------------------------|
| `regulations` | `far-25-1309` | `regulation` | `public` | `f74c53b7…` |
| `cfd-papers` | `nasa-tm-2014-218175` | `paper` | `public` | `f26f61e6…` |
| `accident-reports` | `ntsb-aar-09-03` | `accident_report` | `public` | `656ea854…` |

Each directory contains the canonical 3-file triple (`source.md`, `processed.md`, `metadata.yaml`). Every `metadata.yaml` carries all 11 DOC-02 mandatory fields (title, doc_type, language, source_url, publication_date, effective_date, confidentiality, domain_tags, version, file_hash, processed_by) with real, non-placeholder values. `file_hash` is the actual SHA-256 of the corresponding `source.md`, computed via `shasum -a 256`.

**Source-content fidelity:** `source.md` files contain ≤500-word public extracts (abstract / executive summary) with a clear "Stand-in for the original PDF" header pointing at the canonical `source_url`. No fabricated content; every claim traces to the public-domain source. `processed.md` files are structured-Markdown summaries with H1/H2 section anchors so chunk-by-section retrieval (Phase 5) is testable.

### Task 2 — 3 Document entity instances (commit `f6bf75c`)

Created the canonical Document entities at `instances/entities/document/`:

- `aviationkb://document/far-25-1309@1`
- `aviationkb://document/nasa-tm-2014-218175@1`
- `aviationkb://document/ntsb-aar-09-03@1`

Each mirrors the corresponding `metadata.yaml` from Task 1 but uses the entity-schema field names (`document_version` instead of `version`-the-string; `title_text` for the canonical printed title; `i18n.label.{zh,en}` for short bilingual display). Each carries a full PROV-01..03 stack: `provenance.method: human`, `confidence.score ≥ 0.97`, and `source.document_id` self-referencing the document itself (matches Phase 3 fixture convention).

`python scripts/validate.py instances/entities/document/` → 0 errors, 0 warnings on 3 records.

### Task 3 — 2 Person + 3 Organization entity instances (commit `383150c`)

Created the URI resolution targets that every other Phase 4 plan will need:

| Type | URI | Role / Type |
|------|-----|-------------|
| Person | `aviationkb://person/jane-reviewer@1` | `reviewer`, affiliated with FAA |
| Person | `aviationkb://person/john-cfd-analyst@1` | `engineer`, affiliated with NASA |
| Organization | `aviationkb://organization/faa@1` | `regulator`, jurisdiction `FAA` |
| Organization | `aviationkb://organization/nasa@1` | `research_institute`, no jurisdiction |
| Organization | `aviationkb://organization/ntsb@1` | `regulator` (closest match), no jurisdiction |

**Self-loop on provenance.actor:** `jane-reviewer.yaml` lists herself as her own `provenance.actor`. Phase 3 validators accept this (URI just needs to resolve; no acyclicity constraint on Person records). Same pattern was used in Phase 3's `tests/fixtures/valid/entities/person_jane-reviewer.yaml`.

`python scripts/validate.py instances/entities/person/ instances/entities/organization/ instances/entities/document/` → 0 errors, 0 warnings on 8 records.

## Verification

| Acceptance gate | Command | Result |
|---|---|---|
| ≥3 metadata.yaml on disk | `find docs -mindepth 3 -name 'metadata.yaml' \| wc -l` | **3** ✅ |
| All 11 DOC-02 fields per metadata | grep loop in plan-level verify | **OK** ✅ |
| All file_hash match `^sha256:[a-f0-9]{64}$` | regex grep | **3/3 OK** ✅ |
| All 8 Phase 4 entities validate | `python scripts/validate.py instances/` | **0 errors, 0 warnings** ✅ |

## Requirements satisfied

| REQ-ID | Status | Evidence |
|--------|--------|----------|
| **DOC-01** | ✅ | `docs/<domain>/<doc-id>/{source.md, processed.md, metadata.yaml}` layout honored 3× |
| **DOC-02** | ✅ | All 11 mandatory fields populated with non-placeholder values in 3 metadata.yaml files |
| **DOC-04** | ✅ (partial) | All 3 demo docs declare `confidentiality: public`; the `restricted`/`itar_ear` gating rule itself is documented in plan 04-04 (`docs/README.md`) |
| **DEMO-03** | ✅ | 1 regulation + 1 CFD paper + 1 accident report covers the doc-type spread |

## Deviations from Plan

None — plan executed exactly as written. No Rule 1 / 2 / 3 auto-fixes triggered, no Rule 4 architectural decisions needed.

The plan's `<action>` block included an embedded directive `<RUN: shasum -a 256 …>` placeholder for `file_hash`; this was resolved at write time by computing the SHA-256 hashes of the actual `source.md` files and prefixing with `sha256:` before writing the `metadata.yaml` files. This is normal plan execution, not a deviation.

## Downstream URI dependencies satisfied

Plans 04-02, 04-03, 04-04 can now safely cite:

- `aviationkb://document/far-25-1309@1` — for Phase-4 RegulationClause records and any FailureMode that maps to §25.1309
- `aviationkb://document/nasa-tm-2014-218175@1` — for plan 04-03 CFDMethod / TurbulenceModel / SimulationCase records
- `aviationkb://document/ntsb-aar-09-03@1` — for plan 04-03 AccidentCase
- `aviationkb://person/jane-reviewer@1` and `aviationkb://person/john-cfd-analyst@1` — as `provenance.actor`
- `aviationkb://organization/{faa,nasa,ntsb}@1` — as `Person.affiliation`

## Self-Check: PASSED

**Files verified on disk (17/17):**
- FOUND: docs/regulations/far-25-1309/source.md
- FOUND: docs/regulations/far-25-1309/processed.md
- FOUND: docs/regulations/far-25-1309/metadata.yaml
- FOUND: docs/cfd-papers/nasa-tm-2014-218175/source.md
- FOUND: docs/cfd-papers/nasa-tm-2014-218175/processed.md
- FOUND: docs/cfd-papers/nasa-tm-2014-218175/metadata.yaml
- FOUND: docs/accident-reports/ntsb-aar-09-03/source.md
- FOUND: docs/accident-reports/ntsb-aar-09-03/processed.md
- FOUND: docs/accident-reports/ntsb-aar-09-03/metadata.yaml
- FOUND: instances/entities/document/far-25-1309.yaml
- FOUND: instances/entities/document/nasa-tm-2014-218175.yaml
- FOUND: instances/entities/document/ntsb-aar-09-03.yaml
- FOUND: instances/entities/person/jane-reviewer.yaml
- FOUND: instances/entities/person/john-cfd-analyst.yaml
- FOUND: instances/entities/organization/faa.yaml
- FOUND: instances/entities/organization/nasa.yaml
- FOUND: instances/entities/organization/ntsb.yaml

**Commits verified in git log:**
- FOUND: 95cc070 (Task 1 — 3 source-doc skeletons)
- FOUND: f6bf75c (Task 2 — 3 Document entities)
- FOUND: 383150c (Task 3 — 2 Person + 3 Organization entities)

---
phase: 04
plan: 04
slug: relations-pending-readme
subsystem: instances/relations + instances/_pending + docs/
wave: 2
status: complete
completed: 2026-05-03
duration_minutes: 5
tasks_completed: 3
tasks_total: 3
requirements: [DOC-03, DOC-04, DEMO-02, DEMO-06]
closes_cross_links: [DEMO-04, DEMO-05]
dependencies:
  requires: [04-01, 04-02, 04-03]
  provides: [relations-corpus-v01, ai-接力-import-doc-v01, _pending-demo-record]
  affects: [Phase-5-RAGFlow-exporter]
tech_stack:
  added: []
  patterns: [hybrid_reviewed-provenance, supersedes-relation-bidirectional, complies_with-with-evidence-uri]
key_files:
  created:
    - instances/relations/part-of/fadec-of-b737max.yaml
    - instances/relations/part-of/channel-a-of-fadec.yaml
    - instances/relations/part-of/fadec-cpu-of-channel-a.yaml
    - instances/relations/cites/canonical-note-cites-far25.yaml
    - instances/relations/supersedes/far-clause-chain.yaml
    - instances/relations/used-in/sst-used-in-naca0012.yaml
    - instances/relations/mitigated-by/cpu-lockup-mitigated-by-power-up-test.yaml
    - instances/relations/complies-with/fadec-component-complies-with-do178c.yaml
    - instances/_pending/entities/expert-note/pending-ai-extracted-fadec-thermal-margins.yaml
    - docs/README.md
  modified: []
decisions:
  - "Used schema-correct enum values (mitigation_type=procedure not procedural; compliance_status=demonstrated not compliant) — caught by reading relation.mitigated-by + relation.complies-with schemas before authoring"
  - "complies_with.compliance_evidence is a URI to a TestReport entity (the DO-160G pass-fail report), not a free-text description — this matches the schema's intent of audit-grade compliance traceability"
  - "_pending demo record uses confidence.score=0.78 (deliberately below 0.85) to model honest scoring after AI+human review found partial agreement; demonstrates that hybrid_reviewed records are NOT auto-bumped to high confidence just because a human signed off"
  - "Section header rename 'Scripted (AI-Assisted) Import Workflow' → 'Scripted Import Workflow (AI-Assisted)' to satisfy the VALIDATION.md DOC-03 grep test that searches for the literal phrase 'Scripted Import'"
metrics:
  duration_minutes: 5
  records_added: 9
  records_total_after: 39
  validate_errors: 0
  validate_warnings: 0
  pytest_passed: 19
  pytest_failed: 0
---

# Phase 4 Plan 04: Relations Corpus + _pending Demo + Import Workflow README — Summary

Wired the entity corpus together with 8 relation instances across 6 distinct
relation types (DEMO-02), staged one AI-extracted-then-human-reviewed
ExpertNote in `instances/_pending/` as the staging-pattern proof point
(DEMO-06), and authored the `docs/README.md` import workflow + AI 接力开发指南
that DOC-03 / DOC-04 require. Closes the cross-links from plan 04-02
(DEMO-04 canonical-example citation; DEMO-05 supersession bidirectionality)
without touching any of the entity records themselves.

## What Was Built

### Task 1 — 8 Relation Instances (commit `f450fb7`)

| Path | Type | Subject → Object |
|------|------|------------------|
| `relations/part-of/fadec-of-b737max.yaml` | `part_of` | FADEC system → B737 MAX 8 |
| `relations/part-of/channel-a-of-fadec.yaml` | `part_of` | Channel-A subsystem → FADEC system |
| `relations/part-of/fadec-cpu-of-channel-a.yaml` | `part_of` | CPU card → Channel-A subsystem |
| `relations/cites/canonical-note-cites-far25.yaml` | `cites` | canonical-example ExpertNote → FAR-25-1309 Document |
| `relations/supersedes/far-clause-chain.yaml` | `supersedes` | far-25-1309-active → far-25-1309-superseded |
| `relations/used-in/sst-used-in-naca0012.yaml` | `used_in` | k-omega-sst → naca0012-re6e6-aoa-sweep |
| `relations/mitigated-by/cpu-lockup-mitigated-by-power-up-test.yaml` | `mitigated_by` | cpu-lockup → power-up-self-test (`mitigation_type: procedure`) |
| `relations/complies-with/fadec-component-complies-with-do178c.yaml` | `complies_with` | cpu-card → DO-178C (evidence → TestReport, status `demonstrated`) |

**Direction conventions verified against test fixtures:**
- `part_of`: subject = part, object = whole.
- `supersedes`: subject = newer/active, object = older/superseded.
- `cites`: subject = citing entity, object = cited Document.
- `used_in`: subject = thing being used, object = context using it.
- `mitigated_by`: subject = failure, object = mitigation.
- `complies_with`: subject = component, object = standard.

Three `part_of` records build a 4-level chain Component → Subsystem → System
→ AircraftModel that exercises the transitive part_of tree the Phase-3
relations validator will eventually walk. The `supersedes` relation, paired
with the `superseded_by` field on `far-25-1309-superseded.yaml` (set in plan
04-02), closes DEMO-05 bidirectionally.

### Task 2 — _pending AI-Extracted Demo (commit `35b49c8`)

`instances/_pending/entities/expert-note/pending-ai-extracted-fadec-thermal-margins.yaml`

- `provenance.method: hybrid_reviewed` (NOT `ai_extracted`) — passes the
  H-Darrieus REJECT (`PROV-04`) per ADR-005.
- `provenance.reviewer` + `provenance.reviewed_at` + `provenance.tool` all
  populated, modelling the post-review audit trail.
- `confidence.score: 0.78` deliberately set below 0.85 — score reflects
  the partial AI agreement on the first pass (2 of 3 thermal cases), not
  the corrected-by-reviewer final state. This demonstrates that
  `hybrid_reviewed` records are NOT auto-bumped to high confidence.
- File is in `_pending/` only; verified NOT duplicated in canonical
  `instances/entities/`.

### Task 3 — `docs/README.md` (commit `cdc0bb0`)

10 sections, 230 lines, satisfying DOC-03 + DOC-04 + the AIH-01 "5-minute
stranger test":

1. Directory Convention (DOC-01)
2. metadata.yaml Mandatory Fields (DOC-02 — 11-field table)
3. Confidentiality Gating (DOC-04 — "not ingested by default" + all 4 enums)
4. Manual Import Workflow
5. Scripted Import Workflow (AI-Assisted)
6. The H-Darrieus REJECT Rule (PROV-04)
7. Worked Example — Canonical ExpertNote (cites
   `instances/entities/expert-note/canonical-example.yaml`, closing DEMO-04
   cross-link)
8. Reviewer Roster (v0.1.0)
9. See Also
10. AI 接力开发指南 — Reviewer-Bound Checklist

Ends with the literal `Last touched by: claude-opus-4-7 on 2026-05-03`
audit line per AIH-01.

## Verification

```
$ python scripts/validate.py instances/
Validation summary: 0 error(s), 0 warning(s) across 39 record(s).

$ pytest tests/ -q
....................... 19 passed in 0.12s
```

| Gate | Target | Actual |
|------|--------|--------|
| Relations count | ≥3 | 8 |
| Distinct relation types | ≥3 | 6 (`cites`, `complies_with`, `mitigated_by`, `part_of`, `supersedes`, `used_in`) |
| _pending records | ≥1 | 1 |
| _pending records leaked into canonical | 0 | 0 |
| validate.py errors | 0 | 0 |
| validate.py warnings | 0 | 0 |
| pytest pass | 100% | 19 / 19 |
| docs/README.md required headers | 9 | 9 (all H1/H2 grep checks green) |
| docs/README.md confidentiality phrases | 4 enums + "not ingested by default" | all present |

## Requirement Coverage

| REQ-ID | Status | Evidence |
|--------|--------|----------|
| **DEMO-02** | ✅ closed | 8 relations across 6 types in `instances/relations/`; all subject/object URIs resolve; full corpus validates clean |
| **DEMO-06** | ✅ closed | `pending-ai-extracted-fadec-thermal-margins.yaml` in `_pending/`; `method: hybrid_reviewed`; reviewer + reviewed_at + tool populated; `confidence.score: 0.78` (honest); not duplicated in canonical |
| **DOC-03** | ✅ closed | `docs/README.md` documents Manual + Scripted import workflows, reviewer roles (Section 8), AI-extracted entity destination (`_pending/`), confidentiality gating (Section 3) |
| **DOC-04** | ✅ closed | `docs/README.md` Section 3 documents the `restricted` / `itar_ear` "not ingested by default" rule + lists all 4 confidentiality enum values |
| **DEMO-04** (cross-link from 04-02) | ✅ closed | `docs/README.md` Section 7 cites `instances/entities/expert-note/canonical-example.yaml` as the worked provenance example |
| **DEMO-05** (cross-link from 04-02) | ✅ closed | `relations/supersedes/far-clause-chain.yaml` pairs with the entity-field `superseded_by` on `far-25-1309-superseded.yaml` for bidirectional supersession |

## Deviations from Plan

### Auto-fixed during execution

**1. [Rule 1 - Bug] `mitigation_type` enum value**

- **Found during:** Task 1 (`mitigated-by` relation authoring).
- **Issue:** Plan suggested `mitigation_type: "procedural"` but the
  `relation.mitigated-by.schema.json` enum is
  `[design, procedure, training, inspection, monitoring, redundancy]`.
- **Fix:** Used `mitigation_type: procedure`. Plan also acknowledged this
  with the note "if schema enum exists, use it" — the schema does, so no
  surprise.
- **Commit:** `f450fb7`

**2. [Rule 1 - Bug] `compliance_status` enum value + `compliance_evidence` type**

- **Found during:** Task 1 (`complies-with` relation authoring).
- **Issue:** Plan suggested `compliance_status: "compliant"` and a free-text
  `compliance_evidence`. The `relation.complies-with.schema.json` enum is
  `[demonstrated, claimed, in_progress, exempted]` and `compliance_evidence`
  is typed as a URI (must point to a TestReport / SimulationCase / Procedure
  entity).
- **Fix:** Set `compliance_status: demonstrated` and
  `compliance_evidence: aviationkb://test-report/fcc-do160g-power-input-pass@1`
  (the existing test-report entity). The compliance assertion now points at
  audit-grade evidence rather than narrative prose, which is the schema's
  whole point.
- **Commit:** `f450fb7`

**3. [Rule 1 - Bug] `cardinality_hint` enum value**

- **Found during:** Task 1 (`part_of` relation authoring).
- **Issue:** Plan inline YAML used `cardinality_hint: "1..1"` but the
  `relation.part-of.schema.json` enum is
  `[exactly_one, one_or_more, optional]`.
- **Fix:** Used `cardinality_hint: exactly_one` consistently across all 3
  `part_of` records (matching the existing test fixture
  `tests/fixtures/valid/relations/part-of_fadec-of-b737max.yaml`).
- **Commit:** `f450fb7`

**4. [Rule 1 - Bug] `Scripted Import Workflow` header phrasing**

- **Found during:** Task 3 verification.
- **Issue:** Plan's literal section-header text was
  `## 5. Scripted (AI-Assisted) Import Workflow`, but VALIDATION.md's DOC-03
  grep test searches for the literal phrase `"Scripted Import"`. The
  parenthetical `(AI-Assisted)` between the two words breaks the grep.
- **Fix:** Reordered to `## 5. Scripted Import Workflow (AI-Assisted)` —
  same semantic content, satisfies the grep.
- **Commit:** `cdc0bb0`

All four deviations were Rule-1 schema/spec corrections (no architectural
changes); no `Rule 4` checkpoints were needed.

## Authentication Gates Encountered

None.

## Known Stubs

None. The `_pending` record is intentionally staged as a demo, not a stub.

## Self-Check: PASSED

Verified:
- `instances/relations/part-of/fadec-of-b737max.yaml` FOUND
- `instances/relations/part-of/channel-a-of-fadec.yaml` FOUND
- `instances/relations/part-of/fadec-cpu-of-channel-a.yaml` FOUND
- `instances/relations/cites/canonical-note-cites-far25.yaml` FOUND
- `instances/relations/supersedes/far-clause-chain.yaml` FOUND
- `instances/relations/used-in/sst-used-in-naca0012.yaml` FOUND
- `instances/relations/mitigated-by/cpu-lockup-mitigated-by-power-up-test.yaml` FOUND
- `instances/relations/complies-with/fadec-component-complies-with-do178c.yaml` FOUND
- `instances/_pending/entities/expert-note/pending-ai-extracted-fadec-thermal-margins.yaml` FOUND
- `docs/README.md` FOUND (12 KB, 230 lines)
- Commits `f450fb7`, `35b49c8`, `cdc0bb0` all present in `git log`
- `python scripts/validate.py instances/` exits 0 (39 records)
- `pytest tests/ -q` exits 0 (19 passed)
- All DOC-03 + DOC-04 grep terms match

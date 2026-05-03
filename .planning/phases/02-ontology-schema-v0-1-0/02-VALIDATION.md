---
phase: 2
slug: ontology-schema-v0-1-0
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-03
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during Phase 2 execution.
> Source: `02-RESEARCH.md` §Validation Architecture (lines 1029-1077)

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `check-jsonschema 0.37.1` (already pinned in `.pre-commit-config.yaml`) |
| **Config file** | `.pre-commit-config.yaml` + `.yamllint` (Phase 1 outputs, already wired) |
| **Quick run command** | `pre-commit run check-jsonschema --files <changed-schema>.schema.json` |
| **Full suite command** | `pre-commit run --all-files` |
| **Estimated runtime** | quick: <5s · full: <30s for 36 schema files + 5 vocabularies + 6 ADRs |

Phase 2 uses **ONLY** check-jsonschema. `pytest`-based validators land in Phase 3 (REQ-IDs VAL-01..05). All Phase 2 verification is meta-schema validation + grep + file-existence checks.

---

## Sampling Rate

- **After every task commit:** Run `pre-commit run --files <changed-schema-or-yaml>` (auto-via pre-commit hook on staged files)
- **After every plan wave:** Run `pre-commit run --all-files` (full suite stays green)
- **Before phase verification:** `check-jsonschema --check-metaschema ontology/schemas/*.schema.json` (every Draft 2020-12 schema self-validates) + CI green on PR
- **Max feedback latency:** 30 seconds (full suite); 5 seconds (per-file)

---

## Per-Task Verification Map

> Tasks resolve to exact REQ-IDs from `02-CONTEXT.md` decision set (D-01..D-26) and Phase 2 REQ list (51 IDs).

| REQ-ID | Plan | Wave | Behavior | Test Type | Automated Command | Wave 0 Dep | Status |
|--------|------|------|----------|-----------|-------------------|------------|--------|
| **PROV-01..03** | 02 | 1 | `_meta.schema.json` defines provenance/confidence/source per D-13/D-14/D-16 | meta-validation + grep | `check-jsonschema --check-metaschema ontology/_meta.schema.json && jq '.$defs.provenance' ontology/_meta.schema.json` | ❌ create file | ⬜ pending |
| **PROV-04** | 02 | 1 | H-Darrieus REJECT condition documented in `_meta.schema.json` description (validator implementation Phase 3) | grep | `grep -q "H-Darrieus" ontology/_meta.schema.json` | ❌ | ⬜ pending |
| **PROV-05** | 02 | 1 | `instances/_pending/` directory has README explaining quarantine + promotion gate | grep | `grep -q "hybrid_reviewed" instances/_pending/README.md` | ❌ | ⬜ pending |
| **PROV-06** | 04 | 2 | `source.document_id` references valid Document schema (Document schema must exist) | manual cross-ref | `jq '.properties.source.properties.document_id' ontology/schemas/entity.base.schema.json` | ❌ | ⬜ pending |
| **VER-01** | 02 | 1 | `ontology/VERSION` exists, valid semver | shell | `grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' ontology/VERSION` | ❌ | ⬜ pending |
| **VER-02** | 02 | 1 | `ontology/CHANGELOG.md` exists with `## 0.1.0` entry | shell | `grep -q '## 0.1.0' ontology/CHANGELOG.md` | ❌ | ⬜ pending |
| **VER-03** | 03 | 2 | Every entity/relation schema includes `schema_version` required field (composed via `_meta`) | jq | `for f in ontology/schemas/*.schema.json; do jq -e '.allOf // empty \| any(.[]; .$ref == "_meta.schema.json#/$defs/schema_version_required")' "$f" \|\| echo MISSING $f; done; test $? -eq 0` | ❌ requires _meta first | ⬜ pending |
| **VER-04** | 02 | 1 | `migrations/PATTERN.md` exists with `YAML()` (ruamel) example per Gap-5 | shell | `grep -q 'YAML()' migrations/PATTERN.md && grep -q '.ca.items' migrations/PATTERN.md` | ❌ | ⬜ pending |
| **ONT-E-01** | 03 | 2 | `entity.base.schema.json` exists, composes `_meta` via `allOf+$ref+unevaluatedProperties:false` | meta-val + grep | `check-jsonschema --check-metaschema ontology/schemas/entity.base.schema.json && grep -q 'unevaluatedProperties' ontology/schemas/entity.base.schema.json && ! grep -q 'additionalProperties' ontology/schemas/entity.base.schema.json` | ❌ requires _meta | ⬜ pending |
| **ONT-E-02..18** | 04 | 3 | 17 baseline entity schemas Draft 2020-12 valid | meta-val | `for t in aircraft-model aircraft-system subsystem component requirement regulation-clause standard procedure failure-mode maintenance-task cfd-method simulation-case mesh-requirement turbulence-model accident-case document expert-note; do check-jsonschema --check-metaschema ontology/schemas/entity.$t.schema.json \|\| echo FAIL $t; done` | ❌ requires entity.base | ⬜ pending |
| **ONT-E-19..22** | 04 | 3 | 4 ADR-002 evaluated entities — accept Material + TestCase + TestReport + Person + Organization (5 schemas; Configuration deferred per D-03); each has ADR rationale | meta-val + ADR file exists | `check-jsonschema --check-metaschema ontology/schemas/entity.{material,test-case,test-report,person,organization}.schema.json && test -f .planning/decisions/ADR-002-entity-additions.md` | ❌ requires entity.base + ADR-002 | ⬜ pending |
| **ONT-R-01** | 05 | 2 | `relation.base.schema.json` exists, composes `_meta` correctly | meta-val + grep | `check-jsonschema --check-metaschema ontology/schemas/relation.base.schema.json && grep -q '"subject"' ontology/schemas/relation.base.schema.json && grep -q '"object"' ontology/schemas/relation.base.schema.json` | ❌ requires _meta | ⬜ pending |
| **ONT-R-02..14** | 06 | 3 | 13 baseline relation schemas Draft 2020-12 valid | meta-val | `for r in part-of applicable-to constrained-by verified-by derived-from supersedes cites causes mitigated-by requires equivalent-to conflicts-with used-in; do check-jsonschema --check-metaschema ontology/schemas/relation.$r.schema.json \|\| echo FAIL $r; done` | ❌ requires relation.base | ⬜ pending |
| **ONT-R-15..19** | 06 | 3 | 3 ADR-003 accepted relations (interfaces_with, complies_with, applicable_during_phase) + ADR clarifies has_revision and generated_by are NOT relations | meta-val + ADR | `check-jsonschema --check-metaschema ontology/schemas/relation.{interfaces-with,complies-with,applicable-during-phase}.schema.json && grep -q "internalized as field" .planning/decisions/ADR-003-relation-additions.md` | ❌ requires relation.base + ADR-003 | ⬜ pending |
| **ATA vocab** | 07 | 4 | `ontology/vocabularies/ata-chapters.yaml` exists with ~70 ATA iSpec 2200 chapters (Gap-1) | yamllint + count | `yamllint ontology/vocabularies/ata-chapters.yaml && yq '.chapters \| length' ontology/vocabularies/ata-chapters.yaml \| awk '{ if ($1 < 50 \|\| $1 > 80) exit 1 }'` | ❌ | ⬜ pending |
| **Jurisdictions vocab** | 07 | 4 | `ontology/vocabularies/jurisdictions.yaml` enumerates FAA/EASA/CAAC/ICAO/Transport-Canada/CASA-AU/other | yamllint + grep | `yamllint ontology/vocabularies/jurisdictions.yaml && grep -E '^- (faa\|easa\|caac\|icao\|other):' ontology/vocabularies/jurisdictions.yaml \| wc -l \| awk '{ if ($1 < 5) exit 1 }'` | ❌ | ⬜ pending |
| **Provenance vocab** | 07 | 4 | `ontology/vocabularies/provenance-methods.yaml` exposes `human/ai_extracted/hybrid_reviewed` per D-16 | yamllint + grep | `grep -qE '^- (human\|ai_extracted\|hybrid_reviewed):' ontology/vocabularies/provenance-methods.yaml` | ❌ | ⬜ pending |
| **S1000D mapping** | 07 | 4 | `ontology/mappings/s1000d-dmc-reserved.md` documents Issue 6.0 DMC structure (Gap-2) | grep | `grep -q "Issue 6.0" ontology/mappings/s1000d-dmc-reserved.md && grep -q "DMC-" ontology/mappings/s1000d-dmc-reserved.md` | ❌ | ⬜ pending |
| **ATA mapping** | 07 | 4 | `ontology/mappings/ata-to-iso10303.md` placeholder explains v0.1.0 doesn't map (deferred) | grep | `grep -q "deferred" ontology/mappings/ata-to-iso10303.md` | ❌ | ⬜ pending |
| **Triple stub** | 08 | 4 | `scripts/exporters/to_jsonl_triples.py` enriched with schema-derived design notes (D-19) | grep + python parse | `grep -q "JSONL" scripts/exporters/to_jsonl_triples.py && python -c "import ast; ast.parse(open('scripts/exporters/to_jsonl_triples.py').read())"` | ❌ Phase 1 stub exists; Phase 2 enriches | ⬜ pending |
| **6 ADRs** | 02-08 | various | ADR-002..007 in `.planning/decisions/` | shell | `for n in 002 003 004 005 006 007; do test -f .planning/decisions/ADR-$n-*.md \|\| echo MISSING ADR-$n; done; test $? -eq 0` | ❌ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Phase 2 has **no test stubs to install** — `check-jsonschema 0.37.1` is already pinned in `.pre-commit-config.yaml` (Phase 1 output). Wave 0 is purely **deliverable creation order**:

- [ ] `ontology/_meta.schema.json` — composition root (must exist before any entity/relation schema can compose it via `$ref`)
- [ ] `ontology/VERSION` (= `0.1.0`)
- [ ] `ontology/CHANGELOG.md` (initial entry)
- [ ] `migrations/PATTERN.md` (per Gap-5)
- [ ] `migrations/0_1_0_to_template.py.example` (boilerplate)
- [ ] `instances/_pending/README.md` (PROV-05 promotion gate doc)
- [ ] `.planning/decisions/` directory with first ADR (ADR-002 entity additions, defines what gets created in subsequent waves)

After this wave, downstream waves can run in parallel-ish (entity batch + relation batch + vocabularies in parallel).

---

## Manual-Only Verifications

| Behavior | REQ-ID | Why Manual | Test Instructions |
|----------|--------|------------|-------------------|
| Worked examples in `description` fields are pedagogically clear | ONT-R-11, ONT-R-15 (requires/interfaces_with) and ONT-R-04, ONT-R-16 (constrained_by/complies_with) | Subjective semantic boundary judgment — D-10/D-11 require examples that disambiguate twin relations | Reviewer reads each `description` field for the 4 boundary-relevant relations, confirms the example unambiguously distinguishes the relation from its sibling |
| ADR rationale honesty (no copy-paste boilerplate) | ADR-002 through ADR-007 | Quality of decision documentation can't be grep'd | Reviewer skims each ADR; rejects if rationale section is < 3 sentences or doesn't reference the D-XX it implements |

---

## Validation Sign-Off

- [ ] All 51 phase REQ-IDs map to either an `<automated>` verify or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (planner enforces)
- [ ] Wave 0 covers all `❌ requires X` references in the table above
- [ ] No watch-mode flags (Phase 2 uses pre-commit, not pytest --watch)
- [ ] Feedback latency < 30s for full suite
- [ ] `nyquist_compliant: true` set in this frontmatter once all entries are ✅

**Approval:** pending (planner sets `nyquist_compliant: true` after task-level mapping)

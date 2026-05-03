# Ontology Changelog

> AI 接力开发指南: This file is the truth source for ontology version transitions. Every schema change (additive or breaking) MUST land a CHANGELOG entry in the same PR. Format: Keep a Changelog (https://keepachangelog.com); semver per ontology/VERSION. Cross-reference: schema field shapes locked in ADR-004; provenance enum locked in ADR-005; entity additions in ADR-002; relation additions in ADR-003; triple export in ADR-006; schema versioning in ADR-007. **This file is also the canonical sign-off ledger for PRD versions** (per Phase 6 plan 06-04 task 2 — see PRD_v1 sign-off entry below).

## [PRD_v1 sign-off] — 2026-05-03

### Added

- **PRD_v1 final, contractual** at `.planning/design/PRD_v1.md`
  - 94 v1 REQ-IDs covered with per-requirement acceptance criteria (§9 matrix)
  - Synthesizes all locked decisions across phases 1–6 (Vision / Stack / Schema / Validators / RAG / Deployment / Roadmap / Out-of-Scope / Risks / Open Questions / Sign-off)
  - Replaces: `.planning/design/PRD_v0.md` (directional, frozen at end of Phase 1) — PRD_v0 back-edited with bidirectional cross-link
  - Authority for: schema set v0.1.0, validator pipeline (VAL-01..05), RAG pipeline contract (RAG-01..08), deployment posture (DEP-01..06, DRAFT only), v2+ "Promote when" triggers (ROAD-01..02 → `.planning/ROADMAP_FUTURE.md`), AI handoff polish (AIH-01..04)
- **Sign-off recorded** in this CHANGELOG (canonical sign-off ledger established in Phase 2 plan 02-01)

### Cross-references

- `.planning/design/PRD_v1.md` — the contract itself
- `.planning/design/PRD_v0.md` — back-edited to point at PRD_v1 as its replacement
- `.planning/ROADMAP_FUTURE.md` — v2+ "Promote when" triggers (plan 06-03)
- `deploy/docker-compose.yml.draft` + `deploy/topology.md` + `deploy/{wiki-git-storage,authentik-phase2,backup-restore}.md` — deployment artifacts (plan 06-01)
- `docs/GLOSSARY.md` (≥50 bilingual entries; plan 06-02)
- `process-log/phase-{1..6}-completion.md` (audit trail; plan 06-02 + this plan)

### Verification

`grep -q "PRD_v1" ontology/CHANGELOG.md` exits 0 (this entry is the sign-off proof for REQ PRD-02).

## 0.1.0 — 2026-05-03 (post-release patch, applied during Phase 3 plan 03-01)

### Fixed
- `entity.base.schema.json` and `relation.base.schema.json`: removed `unevaluatedProperties: false` from these intermediate composition schemas. Per JSON Schema 2020-12 spec, `unevaluatedProperties` evaluates only against annotations in its own scope; when a base schema with `unevaluatedProperties: false` is referenced from a leaf via `allOf`, the base's own `unevaluatedProperties` rejects the leaf's own properties because they are not visible inside the base's scope. The intended pattern is "leaf schemas have `unevaluatedProperties: false`; intermediate composition bases do not". All 20 entity-leaf and 16 relation-leaf schemas keep their `unevaluatedProperties: false`, so unknown-property rejection still works at the level a user actually validates against. Phase 2 only ran `--check-metaschema`, never validated instance documents, so this defect went undetected; Phase 3 plan 03-01 caught it on the first instance-validation run. Schema $id values unchanged → no consumer impact. See `.planning/phases/03-validators-ci-active/03-01-SUMMARY.md` deviations log.

## 0.1.0 — 2026-05-03

Initial schema set.

### Added
- `_meta.schema.json` composition root: `$defs/{baseFields, provenance, confidence, source, uri, internalId, isoDateTime, i18nLabel, schemaVersionString}`
- `entity.base.schema.json` + 20 entity-type schemas (17 baseline + Material + TestCase + TestReport + Person + Organization)
- `relation.base.schema.json` + 16 relation-type schemas (13 baseline + interfaces_with + complies_with + applicable_during_phase)
- Vocabularies: `ata-chapters.yaml` (~70 ATA iSpec 2200 Revision 2024.1 chapters), `jurisdictions.yaml`, `provenance-methods.yaml`
- Mappings: `ata-to-iso10303.md` (deferred-to-v0.3+ placeholder), `s1000d-dmc-reserved.md` (Issue 6.0 DMC structural breakdown)
- Migrations: `migrations/PATTERN.md` + `migrations/0_1_0_to_template.py.example` (ruamel.yaml YAML() class pattern)
- ADRs (one bullet per ADR for line-grep auditability):
  - ADR-001 — reserved for Phase 6 PRD-v0/v1 split documentation
  - ADR-002 — entity additions (Material, TestCase, TestReport, Person, Organization)
  - ADR-003 — relation additions (interfaces_with, complies_with, applicable_during_phase)
  - ADR-004 — schema field shapes (confidence, i18n, version_history)
  - ADR-005 — provenance enum + H-Darrieus REJECT rule
  - ADR-006 — triple export JSONL choice
  - ADR-007 — schema versioning placement

### Notes
- JSON Schema Draft 2020-12 throughout. Composition pattern: `allOf` + `$ref` on every layer; `unevaluatedProperties: false` ON THE LEAF schemas only (entity.<type>.schema.json / relation.<type>.schema.json) — NOT on the intermediate `entity.base.schema.json` / `relation.base.schema.json` (see Phase 3 03-01 patch above). NEVER `additionalProperties: false` anywhere (Pitfall #1).
- `provenance.method` enum: `human | ai_extracted | hybrid_reviewed` (D-16); H-Darrieus REJECT condition documented in `_meta.schema.json#/$defs/provenance.description`; validator implementation lands in Phase 3 (VAL-01..05).
- Configuration / EffectivityRange entity DEFERRED to v0.2.0 (D-03, ADR-002).
- has_revision and generated_by are NOT relations — internalized as fields per D-07 (`version_history[]`) and D-09 (`provenance.actor` + `source.tool`).

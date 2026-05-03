# Ontology Changelog

> AI 接力开发指南: This file is the truth source for ontology version transitions. Every schema change (additive or breaking) MUST land a CHANGELOG entry in the same PR. Format: Keep a Changelog (https://keepachangelog.com); semver per ontology/VERSION. Cross-reference: schema field shapes locked in ADR-004; provenance enum locked in ADR-005; entity additions in ADR-002; relation additions in ADR-003; triple export in ADR-006; schema versioning in ADR-007.

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
- JSON Schema Draft 2020-12 throughout. Composition pattern: `allOf` + `$ref` + `unevaluatedProperties: false`. NEVER `additionalProperties: false` (Pitfall #1).
- `provenance.method` enum: `human | ai_extracted | hybrid_reviewed` (D-16); H-Darrieus REJECT condition documented in `_meta.schema.json#/$defs/provenance.description`; validator implementation lands in Phase 3 (VAL-01..05).
- Configuration / EffectivityRange entity DEFERRED to v0.2.0 (D-03, ADR-002).
- has_revision and generated_by are NOT relations — internalized as fields per D-07 (`version_history[]`) and D-09 (`provenance.actor` + `source.tool`).

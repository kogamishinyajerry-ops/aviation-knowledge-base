# ATA iSpec 2200 → ISO 10303-233 (AP233) Mapping — DEFERRED in v0.1.0

> AI 接力开发指南: This file is a deferral marker. v0.1.0 does NOT map ATA chapter codes to ISO 10303-233 (Application Protocol 233 / Systems Engineering Data Representation). The mapping is technically possible but the activation triggers are not present in v0.1.0.

## Current state

`ontology/vocabularies/ata-chapters.yaml` ships ~69 ATA iSpec 2200 Revision 2024.1 chapter codes. Each entity that references ATA (AircraftSystem, Subsystem, Component, MaintenanceTask, Document.ata_chapter_tags) carries an `ata_chapter` field validated against the YAML.

ISO 10303-233 (AP233 — Systems Engineering Data Representation) is a STEP/EXPRESS-based standard for systems engineering data exchange. It overlaps the ATA taxonomy at the system / subsystem decomposition layer but uses a fundamentally different schema mechanism (EXPRESS schema, p21 instance files).

## Why deferred

Per `.planning/research/STACK.md` "What NOT to Use", AP233 is explicitly rejected for v0.1.0:

> AP233 / ISO 10303-233: AVOID — STEP/EXPRESS schema; even heavier than S1000D; aerospace-systems-engineering only. Wrong shape (STEP/EXPRESS heavy machinery); not adopted.

Mapping work would require:

1. AP233 EXPRESS schema parsing (heavy)
2. Round-trip serialization to STEP p21 (heavy)
3. A consumer downstream that needs the AP233 representation

None of these are present in v0.1.0.

## Activation criteria (when this mapping becomes valuable)

- A consumer downstream (e.g. a PLM system integration) requires AP233 round-trip
- The team has bandwidth for STEP/EXPRESS schema work (estimate: 2+ engineer-weeks)
- Aviation regulator demand surfaces (FAA / EASA / CAAC requesting AP233 deliverables)

Until any of those triggers fires, this file remains a placeholder.

## See also

- `ontology/vocabularies/ata-chapters.yaml` — current ATA taxonomy
- `.planning/research/STACK.md` "What NOT to Use" — AP233 rejection rationale
- `ontology/mappings/s1000d-dmc-reserved.md` — different deferral pattern (S1000D DMC reservation, not full mapping)
- `.planning/ROADMAP_FUTURE.md` (Phase 6) — v2+ activation triggers

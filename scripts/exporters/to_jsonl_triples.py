"""
to_jsonl_triples.py — YAML instances → JSONL triple export (STUB)

Status: Phase-1 STUB enriched in Phase 2 with schema-derived design notes
(per ADR-006 / D-19). Implementation deferred to Phase 5 (RAG pipeline) or
v0.2.0 GraphRAG sprint, whichever ships first.

AI 接力开发指南: read .planning/decisions/ADR-006-triple-export.md before
implementing. The format is locked; this docstring captures the per-entity
and per-relation triple-generation rules a future implementer must honor.

--- Output format (locked v0.1.0) ---

JSONL — one JSON object per line. Schema:

    {
      "s": "<subject_uri>",
      "p": "<predicate>",
      "o": "<object_uri_or_scalar>",
      "prov": { ...record's provenance carry-through... },
      "confidence": { ...record's confidence carry-through... }
    }

Field semantics:
  s — subject URI per D-23 (aviationkb://<type>/<slug>@<version>)
  p — predicate:
        * for relation files: the relation type slug (e.g. "part_of")
        * for entity-type triples: the literal "rdf:type"
        * for entity-property triples: the property name (e.g. "ata_chapter")
  o — object:
        * for relation triples: object URI
        * for type triples: entity type name (e.g. "AircraftSystem")
        * for entity-property triples: scalar value (string, number, bool)
        * for entity-array-element triples: scalar value of the array element
  prov — copy of the source record's provenance object (D-16 / PROV-01)
  confidence — copy of the source record's confidence object (D-13 / PROV-02)

--- Per-entity triple generation rules ---

For each entity YAML under instances/entities/<type>/<slug>.yaml:

  1. Emit ONE rdf:type triple:
     {"s": entity.id, "p": "rdf:type", "o": entity.type,
      "prov": entity.provenance, "confidence": entity.confidence}

  2. For each scalar field in the entity (excluding base fields id, provenance,
     confidence, source, i18n, version_history):
     {"s": entity.id, "p": <field_name>, "o": <field_value>,
      "prov": entity.provenance, "confidence": entity.confidence}

  3. For each array field (e.g. tags, causal_factors):
     emit one triple per array element with the same shape

  4. For each nested object's leaf scalars:
     flatten into dotted predicate names (e.g. "interval.kind", "interval.value")

  5. Skip i18n field (handled by a separate language-aware exporter when needed)
  6. Skip version_history (handled by a separate revision-export when needed)
  7. Skip source.* (it's part of the prov-carry-through, not a triple itself)

--- Per-relation triple generation rules ---

For each relation YAML under instances/relations/<type>/<slug>.yaml:

  Emit ONE triple:
    {"s": relation.subject, "p": relation.type, "o": relation.object,
     "prov": relation.provenance, "confidence": relation.confidence}

  Optional metadata (e.g. interfaces_with.interface_type) is NOT emitted as a
  separate triple in v0.1.0 — it stays inside the relation YAML for inspection.
  v0.2.0+ may add per-metadata triples if a graph consumer needs them.

--- Provenance carry-through (mandatory, ADR-006) ---

Every triple MUST carry prov + confidence. Skipping these breaks the
H-Darrieus failure-mode lock at the export layer (high-confidence AI-extracted
triples slip into downstream graphs without audit trail). Reference: PROV-04
plus ADR-005 — the validator REJECTs ai_extracted records with score > 0.85
and empty reviewer; the exporter MUST preserve those carry-through fields so
downstream consumers can re-apply the same lock.

Future RDF/Turtle export (v0.3.0+) maps:
  prov.actor      → prov:wasAttributedTo
  prov.method     → prov:wasGeneratedBy (with method-specific Activity class)
  prov.created_at → prov:generatedAtTime
  confidence.*    → custom akb: namespace (no PROV-O equivalent)

PROV-06 cross-reference: every Document-derived triple inherits the
source.document_id pointer through provenance carry-through, so the exporter
satisfies citation-traceability at the documentation level (Phase 3 validator
enforces the reverse direction — every claim's source.document_id must point
at an existing Document instance).

--- CLI surface (when implemented) ---

  python scripts/exporters/to_jsonl_triples.py --in instances/ --out export.jsonl
  python scripts/exporters/to_jsonl_triples.py --validate-only

--- Test fixture path (when implemented, Phase 4+) ---

  tests/fixtures/exporters/to_jsonl_triples/
    sample-entity.yaml       → expected-triples.jsonl
    sample-relation.yaml     → expected-triples.jsonl

--- See also ---

- .planning/decisions/ADR-006-triple-export.md — format decision
- .planning/decisions/ADR-005-provenance-enum.md — provenance carry-through rationale
- ontology/_meta.schema.json#/$defs/{provenance,confidence} — source field shapes
- scripts/exporters/to_rdf.py — sibling stub for v0.3.0+ semantic-web export
- scripts/exporters/to_neo4j.py — sibling stub for v0.2.0+ GraphRAG loader
"""
from __future__ import annotations


def main() -> int:
    raise NotImplementedError(
        "to_jsonl_triples.py is a Phase-1 stub. Implementation deferred to v2. "
        "See module docstring for the contract."
    )


if __name__ == "__main__":
    raise SystemExit(main())

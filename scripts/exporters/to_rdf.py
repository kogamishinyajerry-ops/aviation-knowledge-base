"""
to_rdf.py — YAML instances → RDF/Turtle exporter (STUB)

Status: STUB — implementation deferred to v2 (GraphRAG / KG layer).
Architectural role: maps each YAML entity/relation file to RDF triples.
Listed in v1 PROJECT.md "Out of Scope" but the stub exists per
ARCHITECTURE.md "Future-Proofing for GraphRAG" hooks: presence of this
file signals to future contributors that URI scheme (`aviationkb://<type>/<slug>@<version>`)
and stable IDs were designed in v1 specifically to make this exporter
trivial later.

Contract (to be implemented in v2):
- Reads `instances/entities/<type>/<id>.yaml` and `instances/relations/<id>.yaml`
- Emits Turtle (.ttl) using URIs derived from the v1 ID scheme.
  - Entity URI: `https://akb.example.org/<type>/<slug>` (or aviationkb://...)
  - Predicate URI: namespaced under aviationkb relation vocabulary
  - Provenance: PROV-O (W3C PROV ontology) — provenance fields map directly.
- Output: single .ttl file or per-entity files, configurable.

AI handoff note: format choice (RDF/Turtle vs JSON-LD vs JSONL `{s,p,o,prov}`)
is OPEN in Phase 2 ADR (see .planning/research/SUMMARY.md open question #4).
This stub assumes Turtle; revisit if Phase 2 ADR picks a different format.
"""
from __future__ import annotations


def main() -> int:
    raise NotImplementedError(
        "to_rdf.py is a Phase-1 stub. Implementation deferred to v2 "
        "(GraphRAG / KG layer). See module docstring for the contract."
    )


if __name__ == "__main__":
    raise SystemExit(main())

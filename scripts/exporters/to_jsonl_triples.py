"""
to_jsonl_triples.py — YAML instances → JSONL `{s, p, o, prov}` triples (STUB)

Status: STUB — implementation deferred to v2.
Architectural role: simplest possible triple-export format — one JSON
object per line, fields {subject, predicate, object, provenance}. Useful
as a lightweight intermediate format for ad-hoc analysis or as input to
a graph-loader script that doesn't want to parse RDF/Turtle.

Contract (to be implemented in v2):
- For each entity record:
    {"s": "<entity_id>", "p": "rdf:type", "o": "<entity_type>", "prov": {...}}
    plus one triple per scalar field of the entity.
- For each relation file:
    {"s": "<subject_id>", "p": "<predicate>", "o": "<object_id>", "prov": {...}}

AI handoff note: per .planning/research/SUMMARY.md open question #4,
JSONL is the recommended default for v2 simplicity. If Phase 2 ADR
picks RDF/Turtle as the canonical export instead, this script can stay
as the "lightweight peer" of `to_rdf.py`.
"""
from __future__ import annotations


def main() -> int:
    raise NotImplementedError(
        "to_jsonl_triples.py is a Phase-1 stub. Implementation deferred to v2. "
        "See module docstring for the contract."
    )


if __name__ == "__main__":
    raise SystemExit(main())

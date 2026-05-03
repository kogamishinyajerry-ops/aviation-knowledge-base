"""
to_neo4j.py — YAML instances → Neo4j Cypher loader (STUB)

Status: STUB — implementation deferred to v2 (Graph DB backend).
Architectural role: writes Cypher CREATE/MERGE statements (or uses
the neo4j Python driver) to load YAML records into a graph DB.

Contract (to be implemented in v2):
- Each YAML entity → one Neo4j node, label = entity type, properties = YAML fields.
- Each YAML relation file → one Neo4j relationship, type = predicate,
  properties = relation metadata (provenance, confidence, validity).
- Idempotent: uses MERGE on the entity ID (not CREATE).

Architectural intent (per ARCHITECTURE.md Anti-Pattern 1): relations are
ALWAYS separate YAML files, never inline fields on entities. This is
exactly so that `to_neo4j.py` can map them to native Neo4j relationships
without a refactor. Don't violate this in v1 entity schemas.

AI handoff note: defer until v2 trigger fires. Triggers are documented
in .planning/ROADMAP_FUTURE.md (created in Phase 6).
"""
from __future__ import annotations


def main() -> int:
    raise NotImplementedError(
        "to_neo4j.py is a Phase-1 stub. Implementation deferred to v2 "
        "(Graph DB backend). See module docstring for the contract."
    )


if __name__ == "__main__":
    raise SystemExit(main())

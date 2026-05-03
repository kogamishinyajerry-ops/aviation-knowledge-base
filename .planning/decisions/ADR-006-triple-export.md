# ADR-006 — Triple Export Format (JSONL `{s, p, o, prov, confidence}`)

Status: ACCEPTED
Date: 2026-05-03
Deciders: user (CONTEXT.md interactive discuss, 2026-05-03)
Implements: D-18, D-19

## AI 接力开发指南

> Fresh Claude / Codex / DeepSeek session opening this ADR cold should be able to read the next two paragraphs and immediately know: (1) what the v0.1.0 triple-export format is, (2) the exact field shape per triple including provenance + confidence carry-through, (3) what work is allowed in Phase 2 against the existing `scripts/exporters/to_jsonl_triples.py` stub vs what is deferred to Phase 5+ / v0.2.0+.

This ADR locks the triple-export format for v0.1.0 and the scope of work allowed in Phase 2 against the existing `scripts/exporters/to_jsonl_triples.py` stub. The export is Phase 5+ implementation; **Phase 2 only enriches the stub docstring with schema-derived design notes** (which entity fields → triple components). RDF/Turtle and JSON-LD are explicitly deferred to v0.3.0+ when the GraphRAG sprint starts. The H-Darrieus invariant is preserved at the triple layer — every triple carries `prov` + `confidence`, so a graph-layer query can never hide an unreviewed AI extraction.

## Context

The knowledge base needs a downstream-friendly triple format for:

- Ad-hoc analysis (`jq` filters, `wc -l` triple counts, `grep`)
- Future GraphRAG sprint (v0.2.0+ Neo4j/Nebula loader, v0.3.0+ RDF round-trip)
- Provenance + confidence carry-through (any export that drops these fails the Core Value)

Three candidates were considered:

| Format | Pros | Cons |
|--------|------|------|
| **JSONL** `{s, p, o, prov, confidence}` | `jq`-friendly; one triple per line; `wc -l` triple count; trivially convertible to JSON-LD/Turtle later; trivially augmentable with extra columns without spec churn | Not a standard semantic-web format on its own |
| **RDF/Turtle** | Standard, PROV-O-aligned out of the box | Heavyweight in Phase 2 (no consumer needs it yet); test-fixture generation is non-trivial; round-tripping our `confidence` block requires PROV-O reification |
| **N-Triples** | Simple, standard, line-oriented | No native provenance/confidence carry-through; would need PROV-O reification, which is verbose and hostile to `jq` |

## Decision

### v0.1.0 format: JSONL with provenance + confidence (D-18)

One JSON object per line. Schema:

```jsonl
{"s": "aviationkb://component/brake-disc-737-max-8@1", "p": "requires", "o": "aviationkb://maintenance-task/brake-inspection-500h@1", "prov": {"method": "human", "actor": "aviationkb://person/jane-engineer@1", "actor_role": "maintenance_engineer", "created_at": "2026-04-01T10:00:00Z"}, "confidence": {"score": 0.95, "rationale": "Multi-source agreement: cited in 737 MAX 8 maintenance manual ATA-32-21-00 and FAA AD 2026-04-15."}}
{"s": "aviationkb://component/brake-disc-737-max-8@1", "p": "rdf:type", "o": "Component", "prov": {"method": "human", "actor": "aviationkb://person/jane-engineer@1", "actor_role": "maintenance_engineer", "created_at": "2026-04-01T10:00:00Z"}, "confidence": {"score": 1.0, "rationale": "Type assertion derived directly from entity schema; not a model output."}}
{"s": "aviationkb://component/brake-disc-737-max-8@1", "p": "ata_chapter", "o": "32-21", "prov": {"method": "human", "actor": "aviationkb://person/jane-engineer@1", "actor_role": "maintenance_engineer", "created_at": "2026-04-01T10:00:00Z"}, "confidence": {"score": 0.95, "rationale": "ATA chapter assignment confirmed via 737 MAX 8 maintenance manual table of contents."}}
```

Field semantics:

- `s` — subject URI (entity URI per D-23: `aviationkb://<type>/<slug>@<version>`)
- `p` — predicate. For relation triples: relation type slug (snake_case, e.g. `requires`, `interfaces_with`, `complies_with`, `applicable_during_phase`). For entity-type triples: `rdf:type`. For entity-property triples: the field name (e.g. `ata_chapter`, `i18n.label.zh`).
- `o` — object URI (for relation triples) OR scalar value (for entity-property triples) OR entity-type slug (for `rdf:type` triples).
- `prov` — relation/entity provenance carried forward from `_meta.schema.json#/$defs/provenance` (PROV-01 / D-16). Includes at minimum `method`, `actor`, `actor_role`, `created_at`; `reviewer` and `reviewed_at` carry through when present.
- `confidence` — relation/entity confidence carried forward from `_meta.schema.json#/$defs/confidence` (PROV-02 / D-13). Includes `score` and `rationale`.

Per-entity triple-generation rule (Plan 10 docstring contract):

1. Emit one `{s, p="rdf:type", o=<entity_type>, prov, confidence}` triple
2. Emit one triple per scalar field of the entity (e.g. `ata_chapter`, `name`)
3. Emit one triple per element of any array field (with predicate including index or array semantics, TBD by Plan 5+ implementation)
4. Emit one triple per leaf scalar of any nested object field (e.g. `i18n.label.zh`, `i18n.label.en`)

Per-relation triple-generation rule:

- Emit one triple per relation file: `{s=<subject>, p=<type>, o=<object>, prov, confidence}` using the relation file's own `provenance` and `confidence` blocks (NOT the subject/object entity blocks — relation provenance is its own first-class metadata).

### Phase 2 scope: stub docstring enrichment only (D-19)

Phase 2 ONLY enriches `scripts/exporters/to_jsonl_triples.py` docstring with the schema-derived design notes above (which entity fields → triple components, and the per-entity / per-relation rules). NO implementation. NO test fixtures. The `main()` function continues to raise `NotImplementedError` until v0.2.0+ implementation lands.

Implementation lands in Phase 5 (RAG pipeline) or v0.2.0 GraphRAG sprint, whichever ships first. Plan 10 of Phase 2 is the docstring-enrichment deliverable.

### Why JSONL over RDF/Turtle for v0.1.0

1. No v0.1.0 consumer needs the full semantic-web stack (no SPARQL endpoint, no triple store).
2. JSONL is `jq` / `wc -l` / `grep` friendly — debugging on real demo data is fast.
3. Conversion path JSONL → JSON-LD via `@context` injection is cheap (one-line per triple, no reification).
4. Conversion path JSONL → RDF/Turtle via PROV-O alignment is cheap when v0.3.0+ needs it (mapping `prov.actor` → `prov:wasAttributedTo`, `prov.method` → `prov:wasGeneratedBy` with method-specific Activity classes).
5. The opposite direction (RDF → JSONL) is also possible but requires reification handling for PROV-O.
6. RDF/Turtle in v0.1.0 is YAGNI. The cost of locking the wrong line-format now (then migrating in v0.3.0+) is one `to_rdf.py` rewrite — bounded and acceptable.

## Rationale (provenance carry-through is non-negotiable)

Every triple carries `prov` and `confidence` blocks because:

- Without them, the H-Darrieus failure mode (high-confidence AI extraction without reviewer) silently lands in graph-layer queries — exactly the failure the Core Value forbids.
- Phase 4 demo data (DEMO-04) demonstrates the carry-through pattern end-to-end.
- When v0.3.0+ ships RDF/Turtle export, PROV-O alignment is direct: `prov.actor` → `prov:wasAttributedTo`, `prov.method` → `prov:wasGeneratedBy` (with Activity classes per `human` / `ai_extracted` / `hybrid_reviewed`), `confidence.score` → reified statement annotation, `confidence.rationale` → comment on the Activity.

## Consequences

- **Plan 10** enriches `scripts/exporters/to_jsonl_triples.py` docstring with the per-entity / per-relation triple-generation rules above. No Python implementation.
- `scripts/exporters/to_rdf.py` and `scripts/exporters/to_neo4j.py` stubs remain untouched in Phase 2 (deferred to v0.3.0+).
- Phase 5 RAG pipeline design (RAG-08) may use JSONL as the intermediate format between YAML instances and RAGFlow ingestion / GraphRAG indexing.
- Phase 4 demo data MUST include a sample `.jsonl` file showing the format end-to-end (DEMO-04 worked example), exercising at least one entity-type triple, one entity-property triple, and one relation triple — including a `hybrid_reviewed` provenance block to prove the carry-through.
- Phase 3 validator does NOT need to validate the JSONL output (the export is downstream of validation); the YAML source is the truth source.

## References

- REQUIREMENTS.md — no direct REQ-ID; ADR-006 satisfies the v1 architecture goal of "future-proof export" (CORE-01) without locking the project into a heavy semantic-web stack
- 02-CONTEXT.md D-18 (JSONL choice), D-19 (Phase 2 stub-only enrichment)
- 02-RESEARCH.md "Don't Hand-Roll" guidance — JSON-LD/RDF deferred to v0.3.0+
- PROJECT.md "Out of Scope" — "Graph DB backend (Neo4j/Nebula) in v1"
- Phase 1 stub: `scripts/exporters/to_jsonl_triples.py` (currently raises `NotImplementedError`)
- Future deliverables: `scripts/exporters/to_rdf.py` (v0.3.0+ when GraphRAG sprint starts), `scripts/exporters/to_neo4j.py` (v0.2.0 GraphRAG sprint)
- W3C PROV-O recommendation (mapping target for v0.3.0+ RDF export): https://www.w3.org/TR/prov-o/

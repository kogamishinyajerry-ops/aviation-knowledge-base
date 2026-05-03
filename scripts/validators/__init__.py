"""Aviation Knowledge Base ontology validator package.

Public modules:
  - errors:      ValidationError dataclass
  - loader:      YAML loading + schema discovery
  - schema:      JSON Schema (Draft 2020-12) validation
  - ids:         URI / internal ID format checks (Wave 2)
  - provenance:  H-Darrieus REJECT + _pending promotion gate + schema_version (Wave 2)
  - relations:   subject/object resolution (Wave 2)
  - links:       broken-ref / source.document_id resolution (Wave 2)

Phase 3 plan 03-01 ships errors.py + loader.py + schema.py filled in;
ids/provenance/relations/links ship as `return []` stubs filled by plans
03-03 / 03-04.

Public API contract (frozen for Wave 1):
    validate_record(path, record, **ctx) -> list[ValidationError]

`schema.validate_record` accepts (path, record, schemas_dir=None) — `**ctx`
is absorbed by validate.py's dispatch loop without forwarding to schema.
The four stub validators accept arbitrary `**ctx` (notably `by_id`) so Wave-2
plans can fill them in without touching `validate.py`.
"""

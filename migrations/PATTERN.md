# Schema Migration Pattern (v0.1.0)

> AI 接力开发指南: Phase 2 ships only this pattern doc + the `0_1_0_to_template.py.example` boilerplate. The first real migration script lands when ontology/VERSION bumps from 0.1.0 → 0.2.0 (likely Phase 4+ when Configuration entity is added per D-03 deferral). All migrations follow the rules below verbatim.

## Tooling

- Python 3.9+ (matches Phase 3 validator runtime)
- `ruamel.yaml >=0.17, <0.19` — comment-preserving round-trip
- `jsonschema >=4.18` — Draft 2020-12 validation pre/post migration

Add to `requirements-dev.txt` (NOT runtime requirements) when first migration ships.

## File-naming convention

`migrations/<from_version>_to_<to_version>.py`. Slashes converted to underscores. Example: `migrations/0_1_0_to_0_2_0.py`.

## Canonical YAML edit pattern

Use the modern `YAML()` class (NOT the legacy `round-trip-load` function — deprecated since ruamel.yaml 0.15, removed in 0.19+; see Pitfall #10 in 02-RESEARCH.md for the exact deprecated symbol name):

```python
from ruamel.yaml import YAML
yaml = YAML()                  # round-trip mode by default in >=0.15
yaml.preserve_quotes = True
yaml.width = 200               # match .yamllint line-length config
data = yaml.load(path)
# ... edit data in-place ...
yaml.dump(data, path)
```

## Comment-preservation idiom

To rename a key while keeping its trailing comment:

```python
if "old_field" in data:
    data["new_field"] = data.pop("old_field")
    if hasattr(data, "ca") and "old_field" in data.ca.items:
        data.ca.items["new_field"] = data.ca.items.pop("old_field")
```

`data.ca.items` is ruamel.yaml's "comment attribute" mapping — the only documented way to move a comment with its key.

## Idempotency rule

Every migration script MUST be safe to re-run on already-migrated YAML. Check the `schema_version` field at the top:

```python
if data.get("schema_version") == TARGET_VERSION:
    return  # already migrated; no-op
```

## Validation gates

1. Pre-migration: `check-jsonschema --schemafile ontology/schemas/<entity>.schema.json <yaml-file>` (file passes the OLD schema)
2. Run migration script
3. Post-migration: `check-jsonschema --schemafile ontology/schemas/<entity>.schema.json <yaml-file>` against the NEW schema (file passes the NEW schema)

Migration scripts MUST NOT validate against schemas; that is the validator's job (Phase 3, VAL-01..05). Migration scripts only transform.

## Test fixtures

Phase 3 will land `tests/fixtures/migration/` with `before_*.yaml` + `expected_after_*.yaml` pairs per migration. Migration scripts ARE NOT tested in Phase 2.

## See also

- 02-RESEARCH.md §Gap Resolution #5 (verified pattern source)
- 02-RESEARCH.md §Pitfall #10 (legacy round-trip-load function deprecation)
- ADR-007 (Schema versioning placement — D-20/D-21/D-22)

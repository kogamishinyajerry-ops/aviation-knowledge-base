# ADR-007 — Schema Versioning Placement (per-file + per-record + Python migrations)

Status: ACCEPTED
Date: 2026-05-03
Deciders: user (CONTEXT.md interactive discuss, 2026-05-03)
Implements: D-20, D-21, D-22, D-26, VER-01, VER-02, VER-03, VER-04

## AI 接力开发指南

This ADR locks the schema-versioning model for the entire project. The model is "both per-file and per-record version, with Python+ruamel.yaml migrations." Read this before bumping ontology/VERSION or writing your first migration script. The migration pattern doc lives at migrations/PATTERN.md (Phase 2 deliverable).

## Context

Schema evolution requires three independent version axes:

1. **Project ontology release version** (`ontology/VERSION`): the version the entire schema set advertises. Starts `0.1.0`.
2. **Per-schema-file version** (in each schema's `description` or as a sidecar): the schema's evolution within the current ontology release. Used to coordinate review during a release window.
3. **Per-record schema_version** (in every entity / relation YAML instance): the schema version this record was written against. Frozen at write time. CI rejects records older than N-1 versions.

Without (3), migrating an instance YAML from `schema_version: 0.1.0` to `0.3.0` requires guessing what `0.2.0` looked like at the time the YAML was written. With (3), the migration runner reads the field and runs the right chain of migration scripts.

Migrations need to (a) preserve YAML comments (otherwise human review is destroyed), (b) be idempotent (safe to re-run), (c) use a familiar Python toolchain so Phase 3 validators (also Python) can share dependencies.

## Decision

1. **`ontology/VERSION`** — single-line semver, starts `0.1.0`. Bumped on every schema set release. Phase 2 ships `0.1.0`.
2. **`ontology/CHANGELOG.md`** — Keep a Changelog format. Every schema bump (additive or breaking) lands an entry on the same PR. `## 0.1.0` initial entry shipped in Phase 2.
3. **Per-record `schema_version`** — REQUIRED on every entity and relation instance YAML. Type: semver string (`^\d+\.\d+\.\d+$`). Defined as `_meta.schema.json#/$defs/schemaVersionString` and referenced by both entity.base + relation.base.
4. **N-1 tolerance** — Phase 3 validator accepts records whose `schema_version` is current or one major-or-minor below; rejects older. Tolerance window documented in error messages.
5. **Migrations are Python (D-26)** — `migrations/<from>_to_<to>.py`. ruamel.yaml YAML() class for round-trip with comment preservation; jsonschema for pre/post validation gates.
6. **Migration template** — `migrations/0_1_0_to_template.py.example` (Phase 2 deliverable). Copied to a real `0_1_0_to_0_2_0.py` when the first migration ships.
7. **Pattern doc** — `migrations/PATTERN.md` (Phase 2 deliverable). Mandatory reading before writing any migration script.

## Rationale

- Per-file `version` alone (without per-record `schema_version`) leaves us blind to which historical schema each instance was written against — migration becomes guesswork.
- Per-record `schema_version` alone (without per-file version) is fine for instances but doesn't track evolution within a release window.
- Both is cheap and covers both audiences (instance authors and schema reviewers).
- Python over Bash/yq/sed: yq drops comments and reorders keys; sed breaks YAML structure on edge cases (multiline strings, anchors, merge keys); Python+ruamel.yaml is the canonical idiom in 2026 (`[VERIFIED: yaml.dev/doc/ruamel.yaml/detail]`).
- ruamel.yaml `YAML()` class over the deprecated legacy loader: see Pitfall #10 in 02-RESEARCH.md. The legacy loader was removed in ruamel.yaml 0.19+.

## Consequences

- `_meta.schema.json` exposes `$defs/schemaVersionString` (Plan 01 deliverable)
- `entity.base.schema.json` and `relation.base.schema.json` REQUIRE the `schema_version` field on every leaf record (Plans 02, 03)
- Phase 3 validator implements the N-1 tolerance + clear error messages (Pitfall #6)
- Phase 4+ instance YAMLs all carry `schema_version: "0.1.0"`
- First real migration script lands when `ontology/VERSION` bumps to `0.2.0` (likely Phase 4+ if Configuration entity is added per ADR-002)

## References

- REQUIREMENTS.md VER-01..04
- 02-CONTEXT.md D-20, D-21, D-22, D-26
- 02-RESEARCH.md Gap Resolution #5 (ruamel.yaml idiom); Pitfall #6 (schema-version mismatch); Pitfall #10 (legacy loader deprecation)
- migrations/PATTERN.md (the actual pattern doc)
- migrations/0_1_0_to_template.py.example (template)

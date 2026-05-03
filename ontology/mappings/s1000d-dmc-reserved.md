# S1000D Issue 6.0 Data Module Code (DMC) — Reserved Field Documentation

> AI 接力开发指南: This file documents the structural breakdown of the S1000D Issue 6.0 Data Module Code that the `Document.s1000d_dmc` field reserves (per Gap Resolution #2 of `.planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md`). v0.1.0 stores DMCs as opaque strings validated by regex; structural decomposition into 13 components is deferred to v0.2.0+ when a consumer (e.g. round-trip export to S1000D-compliant publication tools) materializes.

## S1000D status

- **Issue 6.0 release date:** 2024-09-01 [VERIFIED: en.wikipedia.org/wiki/S1000D]
- **Predecessor:** Issue 5.0 (2019)
- **Used by:** defense / aerospace publication systems with strict regulatory or contractual requirements

## DMC envelope

Total length: 17–41 alphanumeric characters. Prefix: `DMC-`. Suffix on file form: `.XML`.

Verified example (from S1000D reference toolset / kibook tutorial):

```text
DMC-S1000DBIKE-AAA-D00-00-00-00AA-00PA-D_004-00_EN-US.XML
```

## Component breakdown (Issue 6.0)

| Position | Component | Length | Required | Notes |
|----------|-----------|--------|----------|-------|
| 1 | Model Identification Code | 2–14 chars | yes | Project / equipment identifier (`S1000DBIKE` in example) |
| 2 | System Difference Code | 1–4 chars | yes | Configuration variant identifier (`AAA` = baseline) |
| 3 | SNS — System | 2–4 digits | yes | First segment of System / Subsystem / Sub-subsystem / Assembly path (`D00` in example, treated as system 'D' + 00) |
| 4 | SNS — Subsystem | 2 digits | yes | Second segment (`00`) |
| 5 | SNS — Sub-subsystem | 2 digits | yes | Third segment (`00`) |
| 6 | SNS — Assembly | 4 digits | yes | Fourth segment (`00AA`) |
| 7 | Disassembly Code | 2 chars | yes | Disassembly stage (`00`) |
| 8 | Disassembly Code Variant | 1–3 chars | yes | Variant within disassembly stage (`PA`) |
| 9 | Information Code | 3 digits | yes | Type of information (`004`) |
| 10 | Information Code Variant | 1 char | yes | Variant within information code (`A` — note example has `D` here; full set is alphanumeric) |
| 11 | Item Location Code | 1 char | yes | Where the data module applies: `A` (not specific), `B` (in equipment), `C` (in installed maintainable item), `D` (in major assembly), `T` (training) — example uses `D` |
| 12 | Learn Code | optional | optional | Used for training data modules; preceded by `_` |
| 13 | Language Code | optional | optional | ISO 639 language + country (e.g. `EN-US`); preceded by `_` |

## v0.1.0 schema treatment (entity.document.schema.json)

`s1000d_dmc` field is an **optional string** validated by regex (verified to match the example above). The regex is intentionally relaxed in v0.1.0 because real-world DMCs vary across publishers and a strict 13-segment regex would falsely reject legitimate DMCs that minor implementations format slightly differently.

The field's schema description carries the marker phrase "**Reserved field —**" per Pitfall #5 (RESEARCH.md): reserved fields must be visibly marked so future implementers don't mistake them for active validation.

## v0.2.0+ activation plan

When a consumer materializes (S1000D round-trip; AD/SB publication; defense contract):

1. Replace the optional string with a structured nested object reflecting the 13 components above
2. Add a `mapping/s1000d-dmc-decomposed.md` separate doc with worked examples
3. Bump `ontology/VERSION` to a major-or-minor (additive change to a reserved field is non-breaking but the structured shape is breaking for any consumer that already used the string form)
4. Update Document schema with backward-compatibility (allow either string or structured object)

## Sources

- [Wikipedia: S1000D](https://en.wikipedia.org/wiki/S1000D) — Issue 6.0 release date
- [siberlogic.com S1000D SNS and DMC](https://www.siberlogic.com/s1000d-concepts/sns-and-dmc) — DMC structure
- [s1kd-tools tutorial](https://kibook.github.io/s1kd-tools/TUTORIAL.html) — verified example
- `.planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md` Gap Resolution #2 (this project's verified breakdown)

## See also

- `ontology/schemas/entity.document.schema.json` — schema field definition (s1000d_dmc with relaxed v0.1.0 regex pattern)
- `.planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md` Pitfall #5 — Reserved field discipline
- `.planning/ROADMAP_FUTURE.md` (Phase 6) — when to activate full structural decomposition

---
phase: 02-ontology-schema-v0-1-0
plan: 06
type: execute
wave: 3
depends_on: [02]
files_modified:
  - ontology/schemas/entity.failure-mode.schema.json
  - ontology/schemas/entity.cfd-method.schema.json
  - ontology/schemas/entity.simulation-case.schema.json
  - ontology/schemas/entity.mesh-requirement.schema.json
  - ontology/schemas/entity.turbulence-model.schema.json
autonomous: true
requirements:
  - ONT-E-10
  - ONT-E-12
  - ONT-E-13
  - ONT-E-14
  - ONT-E-15
must_haves:
  truths:
    - "All 5 entity schemas self-validate as Draft 2020-12"
    - "Each composes entity.base.schema.json via allOf + $ref + unevaluatedProperties: false"
    - "Pitfall #1 + #9 locks confirmed"
    - "SimulationCase references CFDMethod / MeshRequirement / TurbulenceModel via internal $defs/uri"
  artifacts:
    - path: "ontology/schemas/entity.failure-mode.schema.json"
      provides: "FailureMode schema (ONT-E-10)"
    - path: "ontology/schemas/entity.cfd-method.schema.json"
      provides: "CFDMethod schema (ONT-E-12)"
    - path: "ontology/schemas/entity.simulation-case.schema.json"
      provides: "SimulationCase schema (ONT-E-13) referencing NASA TMR / ERCOFTAC / AIAA workshops"
    - path: "ontology/schemas/entity.mesh-requirement.schema.json"
      provides: "MeshRequirement schema (ONT-E-14)"
    - path: "ontology/schemas/entity.turbulence-model.schema.json"
      provides: "TurbulenceModel schema (ONT-E-15)"
  key_links:
    - from: "entity.simulation-case.schema.json"
      to: "entity.{cfd-method,mesh-requirement,turbulence-model}.schema.json"
      via: "URI references (cfd_method_ref, mesh_ref, turbulence_model_ref)"
---

<objective>
Author 5 baseline entity schemas covering the failure-mode and CFD specialist family. Each composes `entity.base.schema.json`. SimulationCase ties together CFDMethod, MeshRequirement, and TurbulenceModel via URI fields.

Runs PARALLEL with Plans 04 + 05.
Output: 5 schema files in `ontology/schemas/`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/REQUIREMENTS.md
@.planning/phases/02-ontology-schema-v0-1-0/02-CONTEXT.md
@.planning/phases/02-ontology-schema-v0-1-0/02-RESEARCH.md
@.planning/phases/02-ontology-schema-v0-1-0/02-02-SUMMARY.md
@ontology/_meta.schema.json
@ontology/schemas/entity.base.schema.json

<interfaces>
<!-- Same template as Plan 04 / 05. -->
<!-- $ref to _meta from leaf schemas: "../_meta.schema.json#/$defs/<name>" -->
<!-- $ref to entity.base from leaf schemas: "entity.base.schema.json" (sibling) -->
<!-- Per CLAUDE.md project STACK: NASA TMR + ERCOFTAC + AIAA workshops are the v0.1.0 SimulationCase reference targets. -->
<!-- Common turbulence model families: SA / k-omega-SST / k-epsilon / RSM / LES / DES / DNS / hybrid -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author entity.failure-mode.schema.json + entity.cfd-method.schema.json</name>
  <files>ontology/schemas/entity.failure-mode.schema.json, ontology/schemas/entity.cfd-method.schema.json</files>
  <read_first>
    - ontology/schemas/entity.base.schema.json
    - .planning/REQUIREMENTS.md (ONT-E-10, ONT-E-12)
  </read_first>
  <action>
    **entity.failure-mode.schema.json (ONT-E-10):**
    - title: "FailureMode entity (ONT-E-10)"
    - description: "A characterized failure mode of a component, system, or subsystem. Composes entity.base.schema.json."
    - properties.type: const "FailureMode"
    - affected_component: $ref ../_meta.schema.json#/$defs/uri — required (URI to Component / Subsystem / AircraftSystem)
    - failure_description: string ≥20 chars — required
    - conditions: optional object: { altitude: optional string, airspeed: optional string, configuration: optional string, environmental: optional string }; unevaluatedProperties: false
    - severity: enum [catastrophic, hazardous, major, minor, no_safety_effect] — required (matches AircraftSystem.criticality_level)
    - detection_method: optional string (e.g. "BIT", "crew observation", "scheduled inspection")
    - effects: array of strings (≥1 item) — required (failure effects on system / aircraft / mission)
    - required: [type, schema_version, i18n, affected_component, failure_description, severity, effects]

    **entity.cfd-method.schema.json (ONT-E-12):**
    - title: "CFDMethod entity (ONT-E-12)"
    - description: "A CFD numerical method (RANS / LES / DNS / Hybrid). Composes entity.base.schema.json."
    - properties.type: const "CFDMethod"
    - method_class: enum [RANS, URANS, LES, DES, DDES, IDDES, DNS, Hybrid, Other] — required
    - equations: optional string ≥20 chars (governing equations description; e.g. "incompressible Navier-Stokes with Boussinesq buoyancy")
    - governing_assumptions: optional array of strings (e.g. ["incompressible", "steady-state", "no shock waves"])
    - validation_status: optional enum [validated, partially_validated, exploratory, deprecated]
    - typical_applications: optional array of strings
    - required: [type, schema_version, i18n, method_class]
  </action>
  <verify>
    <automated>for f in ontology/schemas/entity.failure-mode.schema.json ontology/schemas/entity.cfd-method.schema.json; do check-jsonschema --check-metaschema "$f" || exit 1; ! grep -q '"additionalProperties"' "$f" || exit 1; grep -q '"unevaluatedProperties": false' "$f" || exit 1; done; jq -e '.properties.type.const == "FailureMode"' ontology/schemas/entity.failure-mode.schema.json &amp;&amp; jq -e '.properties.type.const == "CFDMethod"' ontology/schemas/entity.cfd-method.schema.json &amp;&amp; jq -e '.properties.severity.enum | contains(["catastrophic","hazardous"])' ontology/schemas/entity.failure-mode.schema.json &amp;&amp; jq -e '.properties.method_class.enum | contains(["RANS","LES","DNS"])' ontology/schemas/entity.cfd-method.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - Both files self-validate; Pitfall #1 + #9 locks
    - FailureMode severity enum aligns with AircraftSystem.criticality_level (5-value FAR/CS 25.1309 set)
    - CFDMethod method_class enum has at least RANS, URANS, LES, DES, DNS, Hybrid
    - Both type.const values match
    - Composition via allOf + $ref entity.base.schema.json
  </acceptance_criteria>
  <done>FailureMode + CFDMethod schemas validate; FailureMode.severity matches AircraftSystem.criticality_level enum domain.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Author entity.simulation-case.schema.json + entity.mesh-requirement.schema.json + entity.turbulence-model.schema.json</name>
  <files>ontology/schemas/entity.simulation-case.schema.json, ontology/schemas/entity.mesh-requirement.schema.json, ontology/schemas/entity.turbulence-model.schema.json</files>
  <read_first>
    - ontology/schemas/entity.base.schema.json
    - ontology/schemas/entity.cfd-method.schema.json (Task 1 sibling)
    - .planning/REQUIREMENTS.md (ONT-E-13, ONT-E-14, ONT-E-15)
    - CLAUDE.md (NASA TMR / ERCOFTAC / AIAA workshop references)
  </read_first>
  <action>
    **entity.mesh-requirement.schema.json (ONT-E-14):**
    - title: "MeshRequirement entity (ONT-E-14)"
    - description: "A mesh requirement specification (resolution, quality, refinement zones) for a CFD case. Composes entity.base.schema.json."
    - properties.type: const "MeshRequirement"
    - target_simulation: optional URI (back-link; usually SimulationCase points TO MeshRequirement, but this enables reverse lookup)
    - y_plus_target: optional object: { kind: enum [wall_resolved, wall_modeled, hybrid], target_value: optional number minimum 0, max_acceptable: optional number minimum 0 }; unevaluatedProperties: false
    - cell_count_min: optional integer minimum 1
    - cell_count_max: optional integer minimum 1
    - refinement_zones: optional array of objects: { zone_name: string, refinement_factor: number minimum 1 }; each item unevaluatedProperties: false
    - quality_metrics: optional object: { skewness_max: optional number, aspect_ratio_max: optional number, orthogonality_min: optional number }; unevaluatedProperties: false
    - mesh_topology: optional enum [structured, unstructured, hybrid, polyhedral, hexa_dominant]
    - required: [type, schema_version, i18n]

    **entity.turbulence-model.schema.json (ONT-E-15):**
    - title: "TurbulenceModel entity (ONT-E-15)"
    - description: "A turbulence model (SA, k-omega-SST, k-epsilon, RSM, LES sub-grid, etc). Composes entity.base.schema.json."
    - properties.type: const "TurbulenceModel"
    - family: enum [SA, k-omega-SST, k-epsilon, k-omega, RSM, LES_subgrid, DES_blend, DDES_blend, IDDES_blend, transition_model, other] — required
    - applicability: optional array of strings (free text describing flow regimes the model is suitable for)
    - limitations: optional array of strings
    - references: optional array of URIs (URIs to Document entities)
    - reference_url: optional, format uri (e.g. NASA TMR page)
    - required: [type, schema_version, i18n, family]

    **entity.simulation-case.schema.json (ONT-E-13):**
    - title: "SimulationCase entity (ONT-E-13)"
    - description: "A specific CFD simulation case (geometry + method + mesh + turbulence + boundary conditions + results summary). References NASA Turbulence Modeling Resource (https://tmbwg.github.io/turbmodels/), ERCOFTAC Classic Database, and AIAA Drag/High-Lift/Aeroelastic Prediction Workshops as v0.1.0 reference_url targets. Composes entity.base.schema.json."
    - properties.type: const "SimulationCase"
    - target_geometry: string ≥1 char — required (free-text geometry identifier; e.g. "NACA-0012 airfoil at AoA 5deg")
    - cfd_method_ref: $ref ../_meta.schema.json#/$defs/uri — required (URI to CFDMethod entity)
    - mesh_ref: optional $ref ../_meta.schema.json#/$defs/uri (URI to MeshRequirement entity)
    - turbulence_model_ref: optional $ref ../_meta.schema.json#/$defs/uri (URI to TurbulenceModel entity)
    - boundary_conditions: optional array of objects: { boundary_name: string, type: enum [wall, inlet, outlet, symmetry, periodic, far_field, internal_interface, other], specification: optional string }; each item unevaluatedProperties: false
    - results_summary: optional string ≥20 chars (free-text summary of validation outcome)
    - reference_url: optional, format uri (description: "NASA Turbulence Modeling Resource / ERCOFTAC Classic Database / AIAA Workshop entry")
    - required: [type, schema_version, i18n, target_geometry, cfd_method_ref]
  </action>
  <verify>
    <automated>for f in ontology/schemas/entity.simulation-case.schema.json ontology/schemas/entity.mesh-requirement.schema.json ontology/schemas/entity.turbulence-model.schema.json; do check-jsonschema --check-metaschema "$f" || exit 1; ! grep -q '"additionalProperties"' "$f" || exit 1; grep -q '"unevaluatedProperties": false' "$f" || exit 1; done; jq -e '.properties.type.const == "SimulationCase"' ontology/schemas/entity.simulation-case.schema.json &amp;&amp; jq -e '.properties.cfd_method_ref' ontology/schemas/entity.simulation-case.schema.json &amp;&amp; jq -e '.properties.type.const == "MeshRequirement"' ontology/schemas/entity.mesh-requirement.schema.json &amp;&amp; jq -e '.properties.type.const == "TurbulenceModel"' ontology/schemas/entity.turbulence-model.schema.json &amp;&amp; jq -e '.properties.family.enum | contains(["SA","k-omega-SST","k-epsilon"])' ontology/schemas/entity.turbulence-model.schema.json &amp;&amp; grep -q "NASA Turbulence Modeling" ontology/schemas/entity.simulation-case.schema.json</automated>
  </verify>
  <acceptance_criteria>
    - All 3 files self-validate; Pitfall #1 + #9 locks
    - SimulationCase has cfd_method_ref required, mesh_ref + turbulence_model_ref optional URIs
    - SimulationCase description references NASA TMR / ERCOFTAC / AIAA workshops verbatim
    - SimulationCase boundary_conditions array items have type enum: [wall, inlet, outlet, symmetry, periodic, far_field, internal_interface, other]
    - TurbulenceModel.family enum includes SA, k-omega-SST, k-epsilon at minimum
    - MeshRequirement.y_plus_target supports both wall-resolved (target ~1) and wall-modeled (target ~30+)
    - All 3 type.const values match
  </acceptance_criteria>
  <done>SimulationCase + MeshRequirement + TurbulenceModel schemas validate; SimulationCase ties them together via URI references; cross-references NASA TMR per CLAUDE.md project stack.</done>
</task>

</tasks>

<threat_model>
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-02-06-01 | Tampering | Pitfall #1 in any of 5 schemas | mitigate | per-file `! grep -q additionalProperties` checks |
| T-02-06-02 | Repudiation | SimulationCase without reference URL field → fabrication risk (H-Darrieus pattern in CFD) | mitigate | reference_url is optional but description names NASA TMR / ERCOFTAC / AIAA — Phase 4 demo data must populate |
</threat_model>

<verification>
- All 5 files exist; `--check-metaschema` exits 0 each
- `pre-commit run --all-files` exits 0
- 2 atomic commits via gsd-tools
</verification>

<success_criteria>
- 5 schemas: FailureMode, CFDMethod, SimulationCase, MeshRequirement, TurbulenceModel
- SimulationCase ties three siblings together via URIs
- Pitfall #1 + #9 locks across batch
</success_criteria>

<output>
Create `.planning/phases/02-ontology-schema-v0-1-0/02-06-SUMMARY.md` with:
- 5 schemas listed
- SimulationCase URI reference graph (cfd_method_ref → CFDMethod, mesh_ref → MeshRequirement, turbulence_model_ref → TurbulenceModel)
- Pitfall #1 + #9 confirmation
</output>
